#!/usr/bin/env python3
"""Generic frozen-v1 Volland-like dealer-flow collector for OpenClaw.

This preserves the MU H1 v1 method: edge_fraction=0.10, quote-edge sign only,
inside-spread UNKNOWN, no call/put sign assumption, no DAG transform.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

BASE = "http://127.0.0.1:25503/v3"
EDGE = 0.10


def get_json(path: str, params: dict[str, Any]) -> object:
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    print("[1/4] ThetaData request")
    print(url)
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def explode_contract_data(items: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        contract = item.get("contract")
        data = item.get("data")
        if isinstance(contract, dict) and isinstance(data, list):
            for event in data:
                if not isinstance(event, dict):
                    continue
                row = dict(event)
                row["contract"] = dict(contract)
                out.append(row)
        else:
            out.append(dict(item))
    return out


def rows_from_payload(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return explode_contract_data(payload)
    if not isinstance(payload, dict):
        raise RuntimeError(f"Unexpected ThetaData JSON type: {type(payload).__name__}")
    for key in ("response", "data", "results"):
        data = payload.get(key)
        if isinstance(data, list):
            if not data:
                return []
            if isinstance(data[0], dict):
                return explode_contract_data(data)
    raise RuntimeError("ThetaData JSON has no usable response/data/results list")


def flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_s = str(key)
            full = f"{prefix}.{key_s}" if prefix else key_s
            if isinstance(value, dict):
                out.update(flatten(value, full))
            else:
                out[full.lower()] = value
                out.setdefault(key_s.lower(), value)
    return out


def pick(row: dict[str, Any], *names: str) -> Any:
    flat = flatten(row)
    for name in names:
        key = name.lower()
        if key in flat and flat[key] is not None:
            return flat[key]
    for name in names:
        suffix = "." + name.lower()
        matches = [v for k, v in flat.items() if k.endswith(suffix) and v is not None]
        if len(matches) == 1:
            return matches[0]
    raise KeyError(" / ".join(names))


def num(row: dict[str, Any], *names: str) -> float:
    value = pick(row, *names)
    if isinstance(value, str):
        value = value.replace(",", "").replace("$", "").strip()
    return float(value)


def integer(row: dict[str, Any], *names: str) -> int:
    return int(num(row, *names))


def parse_market_row(row: dict[str, Any]) -> tuple[float, int, float, float, float]:
    return (
        num(row, "contract.strike", "strike"),
        integer(row, "size"),
        num(row, "price"),
        num(row, "bid"),
        num(row, "ask"),
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", required=True)
    p.add_argument("--date", required=True, help="YYYYMMDD")
    p.add_argument("--expiration", required=True, help="YYYYMMDD")
    p.add_argument("--end-time", required=True, help="HH:MM:SS ET")
    p.add_argument("--spot", required=True, type=float)
    p.add_argument("--start-time", default="09:30:00")
    p.add_argument("--output", default=None)
    return p.parse_args()


def main() -> int:
    a = parse_args()
    symbol = a.symbol.upper()
    out = Path(a.output or f"{symbol.lower()}_{a.date}_{a.expiration}_{a.end_time.replace(':','')}_volland_like_frozen_v1.json")

    try:
        payload = get_json(
            "/option/history/trade_quote",
            {
                "symbol": symbol,
                "date": a.date,
                "expiration": a.expiration,
                "strike": "*",
                "right": "both",
                "start_time": a.start_time,
                "end_time": a.end_time,
                "exclusive": "true",
                "format": "json",
            },
        )
        rows = rows_from_payload(payload)
    except Exception as exc:
        print(f"ERROR ThetaData: {exc}", file=sys.stderr)
        return 2

    print(f"[2/4] trade rows received: {len(rows)}")
    if not rows:
        print("ERROR: no trade_quote rows returned", file=sys.stderr)
        return 3

    buckets = defaultdict(lambda: {
        "trade_count": 0,
        "classified_contracts": 0,
        "unknown_contracts": 0,
        "signed_contract_flow": 0,
        "signed_premium_notional": 0.0,
    })
    total_contracts = classified_contracts = unknown_contracts = bad_rows = 0
    failures: Counter[str] = Counter()

    for row in rows:
        try:
            strike, size, price, bid, ask = parse_market_row(row)
        except Exception as exc:
            bad_rows += 1
            failures[f"parse:{type(exc).__name__}:{exc}"] += 1
            continue
        if size <= 0:
            bad_rows += 1
            failures["invalid_size"] += 1
            continue
        if ask < bid:
            bad_rows += 1
            failures["crossed_quote"] += 1
            continue

        b = buckets[strike]
        b["trade_count"] += 1
        total_contracts += size
        spread = ask - bid
        if spread <= 0:
            sign = 0
        else:
            loc = (price - bid) / spread
            sign = -1 if loc >= 1.0 - EDGE else (1 if loc <= EDGE else 0)

        if sign == 0:
            b["unknown_contracts"] += size
            unknown_contracts += size
        else:
            b["classified_contracts"] += size
            classified_contracts += size
            b["signed_contract_flow"] += sign * size
            b["signed_premium_notional"] += sign * size * price * 100.0

    if not buckets:
        print("ERROR: no usable rows after parsing", file=sys.stderr)
        print(dict(failures.most_common(5)), file=sys.stderr)
        return 4

    out_rows = []
    for strike in sorted(buckets):
        b = buckets[strike]
        denom = b["classified_contracts"] + b["unknown_contracts"]
        out_rows.append({
            "strike": strike,
            **b,
            "raw_contract_volume": denom,
            "unknown_fraction": (b["unknown_contracts"] / denom) if denom else 0.0,
            "above_spot": strike > a.spot,
        })

    result = {
        "method": "openclaw_volland_like_signed_flow_frozen_v1",
        "frozen_parameters": {
            "edge_fraction": EDGE,
            "near_ask": "customer_buy_dealer_sell_sign_-1",
            "near_bid": "customer_sell_dealer_buy_sign_+1",
            "inside_spread": "UNKNOWN",
            "call_put_sign_assumption": False,
            "dag_primary_transform": False,
        },
        "symbol": symbol,
        "date": a.date,
        "expiration": a.expiration,
        "window_et": [a.start_time, a.end_time],
        "spot_reference": a.spot,
        "summary": {
            "source_trade_rows": len(rows),
            "bad_rows": bad_rows,
            "total_contracts": total_contracts,
            "classified_contracts": classified_contracts,
            "unknown_contracts": unknown_contracts,
            "unknown_fraction": (unknown_contracts / total_contracts) if total_contracts else 0.0,
        },
        "rows": out_rows,
        "limitations": [
            "intraday signed flow is not total dealer inventory",
            "opening dealer inventory is unknown",
            "no proprietary Volland classifier is reproduced",
            "publication time is an outer bound unless card snapshot time is proven",
        ],
    }
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("[3/4] aggregation complete")
    print(json.dumps(result["summary"], indent=2))
    print(f"[4/4] saved: {out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
