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
from typing import Any

BASE = "http://127.0.0.1:25503/v3"
SYMBOL = "MU"
EXP = "20260819"
OI_DATE = "20260819"
GREEKS_DATE = "20260818"
OUT = Path("mu_20260819_premarket_oi_gamma_h3.json")


def get(path: str, params: dict[str, Any]) -> object:
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    print(url)
    with urllib.request.urlopen(url, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def top_objects(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for k in ("response", "data", "results"):
            v = payload.get(k)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
    raise RuntimeError("Unexpected ThetaData JSON schema")


def explode_contract_data(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten ThetaData v3 [{contract:{...}, data:[...]}, ...] responses."""
    out: list[dict[str, Any]] = []
    for item in items:
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


def rows(payload: object) -> list[dict[str, Any]]:
    return explode_contract_data(top_objects(payload))


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
    f = flatten(row)
    for name in names:
        key = name.lower()
        if key in f and f[key] is not None:
            return f[key]
    for name in names:
        suffix = "." + name.lower()
        matches = [v for k, v in f.items() if k.endswith(suffix) and v is not None]
        if len(matches) == 1:
            return matches[0]
    raise KeyError(" / ".join(names))


def number(row: dict[str, Any], *names: str) -> float:
    value = pick(row, *names)
    if isinstance(value, str):
        value = value.replace(",", "").replace("$", "").strip()
    return float(value)


def right_norm(v: Any) -> str:
    s = str(v).lower()
    if s in ("c", "call"):
        return "call"
    if s in ("p", "put"):
        return "put"
    return s


def contract_key(row: dict[str, Any]) -> tuple[float, str]:
    strike = number(row, "contract.strike", "strike")
    right = right_norm(pick(row, "contract.right", "right"))
    return strike, right


def main() -> None:
    oi_payload = get("/option/history/open_interest", {
        "symbol": SYMBOL, "expiration": EXP, "date": OI_DATE,
        "strike": "*", "right": "both", "format": "json",
    })
    greek_payload = get("/option/history/greeks/eod", {
        "symbol": SYMBOL, "expiration": EXP,
        "start_date": GREEKS_DATE, "end_date": GREEKS_DATE,
        "strike": "*", "right": "both", "format": "json",
        "version": "latest",
    })

    oi_top = top_objects(oi_payload)
    greek_top = top_objects(greek_payload)
    oi = explode_contract_data(oi_top)
    greeks = explode_contract_data(greek_top)

    print(f"OI contract blocks: {len(oi_top)}")
    print(f"OI event rows: {len(oi)}")
    print(f"EOD Greek contract blocks: {len(greek_top)}")
    print(f"EOD Greek event rows: {len(greeks)}")

    oi_map: dict[tuple[float, str], int] = {}
    oi_bad = 0
    first_oi_error = None
    for r in oi:
        try:
            key = contract_key(r)
            oi_map[key] = int(number(r, "open_interest", "oi"))
        except Exception as exc:
            oi_bad += 1
            if first_oi_error is None:
                first_oi_error = (repr(exc), sorted(flatten(r).keys()))

    gamma_map: dict[tuple[float, str], float] = {}
    greek_bad = 0
    first_greek_error = None
    for r in greeks:
        try:
            key = contract_key(r)
            gamma_map[key] = number(r, "gamma")
        except Exception as exc:
            greek_bad += 1
            if first_greek_error is None:
                first_greek_error = (repr(exc), sorted(flatten(r).keys()))

    print(f"parsed OI contract-sides: {len(oi_map)} (bad rows={oi_bad})")
    print(f"parsed gamma contract-sides: {len(gamma_map)} (bad rows={greek_bad})")

    if not oi_map:
        print("ERROR: OI rows were returned but no OI contract-side could be parsed.")
        if first_oi_error:
            print("FIRST OI PARSE ERROR:", first_oi_error[0])
            print("FIRST OI KEYS:", first_oi_error[1])
        raise SystemExit(2)
    if not gamma_map:
        print("ERROR: Greek rows were returned but no gamma contract-side could be parsed.")
        if first_greek_error:
            print("FIRST GREEK PARSE ERROR:", first_greek_error[0])
            print("FIRST GREEK KEYS:", first_greek_error[1])
        raise SystemExit(3)

    all_strikes = sorted({k[0] for k in oi_map} | {k[0] for k in gamma_map})
    agg: dict[float, dict[str, float]] = defaultdict(dict)
    missing_pairs: list[dict[str, Any]] = []

    for strike in all_strikes:
        for right in ("call", "put"):
            key = (strike, right)
            if key not in oi_map or key not in gamma_map:
                missing_pairs.append({
                    "strike": strike,
                    "right": right,
                    "has_oi": key in oi_map,
                    "has_gamma": key in gamma_map,
                })
                continue
            agg[strike][f"{right}_oi"] = oi_map[key]
            agg[strike][f"{right}_gamma"] = gamma_map[key]

    out_rows = []
    for strike in sorted(agg):
        d = agg[strike]
        required = ("call_oi", "put_oi", "call_gamma", "put_gamma")
        if not all(k in d for k in required):
            continue
        cgoi = d["call_oi"] * d["call_gamma"]
        pgoi = d["put_oi"] * d["put_gamma"]
        out_rows.append({
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
        "source_counts": {
            "oi_contract_blocks": len(oi_top),
            "oi_event_rows": len(oi),
            "greeks_contract_blocks": len(greek_top),
            "greeks_event_rows": len(greeks),
            "parsed_oi_contract_sides": len(oi_map),
            "parsed_gamma_contract_sides": len(gamma_map),
            "oi_bad_rows": oi_bad,
            "greek_bad_rows": greek_bad,
            "missing_contract_side_pairs": len(missing_pairs),
        },
        "missing_pairs": missing_pairs,
        "rows": out_rows,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"usable strikes: {len(out_rows)}")
    print(f"saved: {OUT.resolve()}")

    if not out_rows:
        print("ERROR: no complete call+put OI/gamma strike pairs; H3 cannot be evaluated.")
        print("This is a data-join failure, not evidence for or against H3.")
        raise SystemExit(4)


if __name__ == "__main__":
    main()
