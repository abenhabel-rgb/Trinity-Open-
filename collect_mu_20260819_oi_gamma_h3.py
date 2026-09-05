#!/usr/bin/env python3
"""Collect temporally valid OI + prior-close gamma for MU premarket H3.

Target card: MU published 2026-08-19 07:25 ET, expiration 2026-08-19.
Inputs are provider observations available before publication:
- OI message dated 2026-08-19 (reflects end of 2026-08-18 session)
- ThetaData EOD Greeks generated from 2026-08-18 close, including gamma

No dealer sign is inferred from call/put type.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE = "http://127.0.0.1:25503/v3"
SYMBOL = "MU"
EXP = "20260819"
OI_DATE = "20260819"
GREEKS_DATE = "20260818"
OUT = Path("mu_20260819_premarket_oi_gamma_h3.json")


def get(path, params):
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    print(url)
    with urllib.request.urlopen(url, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def objects(payload):
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for k in ("response", "data", "results"):
            v = payload.get(k)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
    raise RuntimeError("Unexpected ThetaData JSON schema")


def right_norm(v):
    s = str(v).lower()
    if s in ("c", "call"):
        return "call"
    if s in ("p", "put"):
        return "put"
    return s


def main():
    oi = objects(get("/option/history/open_interest", {
        "symbol": SYMBOL, "expiration": EXP, "date": OI_DATE,
        "strike": "*", "right": "both", "format": "json",
    }))
    greeks = objects(get("/option/history/greeks/eod", {
        "symbol": SYMBOL, "expiration": EXP,
        "start_date": GREEKS_DATE, "end_date": GREEKS_DATE,
        "strike": "*", "right": "both", "format": "json",
        "version": "latest",
    }))

    print(f"OI rows: {len(oi)}")
    print(f"EOD Greek rows: {len(greeks)}")

    oi_map = {}
    for r in oi:
        try:
            key = (float(r["strike"]), right_norm(r["right"]))
            oi_map[key] = int(r["open_interest"])
        except Exception:
            continue

    gamma_map = {}
    for r in greeks:
        try:
            key = (float(r["strike"]), right_norm(r["right"]))
            gamma_map[key] = float(r["gamma"])
        except Exception:
            continue

    strikes = sorted({k[0] for k in oi_map} & {k[0] for k in gamma_map})
    agg = defaultdict(dict)
    missing_pairs = 0
    for strike in strikes:
        for right in ("call", "put"):
            key = (strike, right)
            if key not in oi_map or key not in gamma_map:
                missing_pairs += 1
                continue
            agg[strike][f"{right}_oi"] = oi_map[key]
            agg[strike][f"{right}_gamma"] = gamma_map[key]

    rows = []
    for strike in sorted(agg):
        d = agg[strike]
        if not all(k in d for k in ("call_oi", "put_oi", "call_gamma", "put_gamma")):
            continue
        cgoi = d["call_oi"] * d["call_gamma"]
        pgoi = d["put_oi"] * d["put_gamma"]
        rows.append({
            "strike": strike,
            **d,
            "total_oi": d["call_oi"] + d["put_oi"],
            "call_gamma_oi": cgoi,
            "put_gamma_oi": pgoi,
            "gamma_oi_total": cgoi + pgoi,
            "cp_gamma_imbalance": cgoi - pgoi,
        })

    result = {
        "symbol": SYMBOL,
        "target_publication_et": "2026-08-19 07:25:00",
        "expiration": EXP,
        "oi_date": OI_DATE,
        "oi_semantics": "ThetaData/OPRA OI reported around 06:30 ET and represents end of previous trading day",
        "gamma_source_date": GREEKS_DATE,
        "gamma_semantics": "ThetaData EOD gamma from prior close",
        "dealer_sign_from_call_put": False,
        "cp_gamma_imbalance_semantics": "call-minus-put structural contrast only; NOT dealer positioning",
        "source_counts": {"oi_rows": len(oi), "greeks_rows": len(greeks), "missing_pairs": missing_pairs},
        "rows": rows,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"usable strikes: {len(rows)}")
    print(f"saved: {OUT.resolve()}")


if __name__ == "__main__":
    main()
