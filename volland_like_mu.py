#!/usr/bin/env python3
"""OpenClaw: simple Volland-like dealer-flow test for MU 2026-09-04.

Research estimator only. It does NOT reproduce Volland's proprietary model.
It uses ThetaData trade+quote history and a conservative quote-edge rule:
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
from collections import defaultdict
from pathlib import Path

BASE = "http://127.0.0.1:25503/v3"
SYMBOL = "MU"
DATE = "20260904"
EXPIRATION = "20260904"
START = "09:30:00"
END = "12:27:00"
SPOT = 1002.66
EDGE = 0.10
OUT = Path("mu_20260904_1227_volland_like.json")


def get_json(path: str, params: dict) -> object:
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    print("[1/4] ThetaData request")
    print(url)
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def rows_from_payload(payload: object) -> list[dict]:
    if isinstance(payload, list):
        if not payload:
            return []
        if isinstance(payload[0], dict):
            return payload

    if not isinstance(payload, dict):
        raise RuntimeError(f"Unexpected ThetaData JSON type: {type(payload).__name__}")

    data = None
    for key in ("response", "data", "results"):
        if isinstance(payload.get(key), list):
            data = payload[key]
            break
    if data is None:
        raise RuntimeError("ThetaData JSON has no response/data/results list")
    if not data:
        return []
    if isinstance(data[0], dict):
        return data

    # ThetaData can return rows as arrays plus a format/header description.
    header = payload.get("header", {})
    fmt = None
    if isinstance(header, dict):
        for key in ("format", "columns", "fields"):
            if isinstance(header.get(key), list):
                fmt = header[key]
                break
    if fmt is None and isinstance(payload.get("format"), list):
        fmt = payload["format"]
    if fmt is None:
        raise RuntimeError("ThetaData returned array rows but no column format was found")

    names = []
    for item in fmt:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict):
            names.append(str(item.get("name") or item.get("field") or item.get("column")))
        else:
            names.append(str(item))
    return [dict(zip(names, row)) for row in data]


def pick(row: dict, *names: str):
    lower = {str(k).lower(): v for k, v in row.items()}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    raise KeyError(" / ".join(names))


def f(row: dict, *names: str) -> float:
    return float(pick(row, *names))


def i(row: dict, *names: str) -> int:
    return int(float(pick(row, *names)))


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

    print(f"[2/4] rows received: {len(rows)}")
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

    for row in rows:
        try:
            strike = f(row, "strike")
            size = i(row, "size", "trade_size", "trade_size_contracts")
            price = f(row, "price", "trade_price")
            bid = f(row, "bid", "bid_price")
            ask = f(row, "ask", "ask_price")
        except Exception:
            bad_rows += 1
            continue

        if size <= 0 or ask < bid:
            bad_rows += 1
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
            # customer buys -> dealer sells
            sign = -1
        elif loc <= EDGE:
            # customer sells -> dealer buys
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
            "source_rows": len(rows),
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
