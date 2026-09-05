#!/usr/bin/env python3
"""OpenClaw: simple Volland-like dealer-flow test for MU 2026-09-04.

Research estimator only. It does NOT reproduce Volland's proprietary model.
It uses ThetaData v3 option trade_quote and a conservative quote-edge rule:
- execution near ask => customer buy => dealer sell
- execution near bid => customer sell => dealer buy
- otherwise => UNKNOWN

No call/put sign assumption is used.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

BASE = "http://127.0.0.1:25503/v3"
SYMBOL = "MU"
DATE = "20260904"
EXPIRATION = "20260904"
START = "09:30:00"
END = "12:27:00"
SPOT = 1002.66
EDGE = 0.10
OUT = Path("mu_20260904_1227_volland_like.json")


def get_json(path: str, params: dict[str, Any]) -> object:
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    print("[1/4] ThetaData request")
    print(url)
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def explode_contract_data(items: list[Any]) -> list[dict[str, Any]]:
    """ThetaData v3 often returns [{contract:{...}, data:[{trade...}, ...]}, ...]."""
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

            header = payload.get("header", {})
            fmt = None
            if isinstance(header, dict):
                for fmt_key in ("format", "columns", "fields"):
                    if isinstance(header.get(fmt_key), list):
                        fmt = header[fmt_key]
                        break
            if fmt is None and isinstance(payload.get("format"), list):
                fmt = payload["format"]
            if fmt is None:
                raise RuntimeError("ThetaData returned array rows but no column format was found")

            names: list[str] = []
            for item in fmt:
                if isinstance(item, str):
                    names.append(item)
                elif isinstance(item, dict):
                    names.append(str(item.get("name") or item.get("field") or item.get("column")))
                else:
                    names.append(str(item))
            return [dict(zip(names, row)) for row in data]

    raise RuntimeError("ThetaData JSON has no response/data/results list")


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
    strike = num(row, "contract.strike", "strike")
    size = integer(row, "size")
    price = num(row, "price")
    bid = num(row, "bid")
    ask = num(row, "ask")
    return strike, size, price, bid, ask


def main() -> int:
    try:
        payload = get_json(
            "/option/history/trade_quote",
            {
                "symbol": SYMBOL,
                "date": DATE,
                "expiration": EXPIRATION,
                "strike": "*",
                "right": "both",
                "start_time": START,
                "end_time": END,
                "exclusive": "true",
                "format": "json",
            },
        )
        rows = rows_from_payload(payload)
    except Exception as exc:
        print(f"ERROR ThetaData: {exc}", file=sys.stderr)
        print("If this says connection refused, Theta Terminal is not running.", file=sys.stderr)
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

    total_contracts = 0
    classified_contracts = 0
    unknown_contracts = 0
    bad_rows = 0
    failures: Counter[str] = Counter()
    first_bad: tuple[dict[str, Any], str] | None = None

    for row in rows:
        try:
            strike, size, price, bid, ask = parse_market_row(row)
        except Exception as exc:
            bad_rows += 1
            failures[f"parse:{type(exc).__name__}:{exc}"] += 1
            if first_bad is None:
                first_bad = (row, repr(exc))
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
            b["unknown_contracts"] += size
            unknown_contracts += size
            continue

        loc = (price - bid) / spread
        if loc >= 1.0 - EDGE:
            sign = -1
        elif loc <= EDGE:
            sign = 1
        else:
            sign = 0

        if sign == 0:
            b["unknown_contracts"] += size
            unknown_contracts += size
        else:
            b["classified_contracts"] += size
            classified_contracts += size
            b["signed_contract_flow"] += sign * size
            b["signed_premium_notional"] += sign * size * price * 100.0

    if bad_rows == len(rows):
        print("ERROR: ThetaData returned trade rows, but none could be parsed.", file=sys.stderr)
        if first_bad is not None:
            row, err = first_bad
            print(f"FIRST PARSE ERROR: {err}", file=sys.stderr)
            print("FIRST ROW KEYS:", sorted(flatten(row).keys()), file=sys.stderr)
            print("FIRST ROW SAMPLE:", json.dumps(row, indent=2)[:4000], file=sys.stderr)
        print("FAILURE COUNTS:", dict(failures.most_common(5)), file=sys.stderr)
        return 4

    out_rows = []
    for strike in sorted(buckets):
        b = buckets[strike]
        denom = b["classified_contracts"] + b["unknown_contracts"]
        out_rows.append({
            "strike": strike,
            **b,
            "unknown_fraction": (b["unknown_contracts"] / denom) if denom else 0.0,
            "above_spot": strike > SPOT,
        })

    result = {
        "method": "openclaw_volland_like_signed_flow_v1",
        "status": "transparent_research_estimator_not_volland_proprietary_formula",
        "symbol": SYMBOL,
        "date": DATE,
        "expiration": EXPIRATION,
        "window_et": [START, END],
        "heatseeker_publication_outer_bound_note": "12:27 ET is publication-time outer bound, not proven snapshot time",
        "spot_reference": SPOT,
        "classification": {
            "edge_fraction": EDGE,
            "near_ask": "customer_buy_dealer_sell",
            "near_bid": "customer_sell_dealer_buy",
            "inside_spread": "UNKNOWN",
            "call_put_sign_assumption": False,
        },
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
            "this Standard-compatible pass does not compute GEX/VEX Greeks",
        ],
    }

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("[3/4] aggregation complete")
    print(json.dumps(result["summary"], indent=2))
    print(f"[4/4] saved: {OUT.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
