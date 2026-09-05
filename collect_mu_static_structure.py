#!/usr/bin/env python3
"""Collect temporally valid static MU option structure: OI + prior-close gamma.

Generic research collector for OpenClaw H4 discrimination tests.
No dealer sign is inferred from call/put type.
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

BASE = "http://127.0.0.1:25503/v3"


def get(path: str, params: dict[str, Any]) -> object:
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    print(url)
    with urllib.request.urlopen(url, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


def explode(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        for key in ("response", "data", "results"):
            if isinstance(payload.get(key), list):
                payload = payload[key]
                break
    if not isinstance(payload, list):
        raise RuntimeError("Unexpected ThetaData JSON schema")

    out: list[dict[str, Any]] = []
    for item in payload:
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


def flat(obj: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            full = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(value, dict):
                out.update(flat(value, full))
            else:
                out[full.lower()] = value
                out.setdefault(str(key).lower(), value)
    return out


def pick(row: dict[str, Any], *names: str) -> Any:
    f = flat(row)
    for name in names:
        if name.lower() in f and f[name.lower()] is not None:
            return f[name.lower()]
    raise KeyError(" / ".join(names))


def right_norm(v: Any) -> str:
    s = str(v).strip().lower()
    if s in ("c", "call"):
        return "call"
    if s in ("p", "put"):
        return "put"
    return s


def args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="MU")
    p.add_argument("--expiration", required=True, help="YYYYMMDD")
    p.add_argument("--oi-date", required=True, help="YYYYMMDD; OI observation date")
    p.add_argument("--gamma-date", required=True, help="YYYYMMDD; prior-close EOD Greeks date")
    p.add_argument("--output", required=True)
    return p.parse_args()


def main() -> int:
    a = args()
    symbol = a.symbol.upper()

    oi_rows = explode(get("/option/history/open_interest", {
        "symbol": symbol,
        "expiration": a.expiration,
        "date": a.oi_date,
        "strike": "*",
        "right": "both",
        "format": "json",
    }))
    greek_rows = explode(get("/option/history/greeks/eod", {
        "symbol": symbol,
        "expiration": a.expiration,
        "start_date": a.gamma_date,
        "end_date": a.gamma_date,
        "strike": "*",
        "right": "both",
        "format": "json",
        "version": "latest",
    }))

    oi_map: dict[tuple[float, str], int] = {}
    for r in oi_rows:
        try:
            strike = float(pick(r, "contract.strike", "strike"))
            right = right_norm(pick(r, "contract.right", "right"))
            oi = int(float(pick(r, "open_interest")))
            oi_map[(strike, right)] = oi
        except Exception:
            continue

    gamma_map: dict[tuple[float, str], float] = {}
    for r in greek_rows:
        try:
            strike = float(pick(r, "contract.strike", "strike"))
            right = right_norm(pick(r, "contract.right", "right"))
            gamma = float(pick(r, "gamma"))
            gamma_map[(strike, right)] = gamma
        except Exception:
            continue

    print(f"parsed OI contract-sides: {len(oi_map)}")
    print(f"parsed gamma contract-sides: {len(gamma_map)}")

    strikes = sorted({k[0] for k in oi_map} & {k[0] for k in gamma_map})
    rows = []
    missing_pairs = 0
    for strike in strikes:
        d: dict[str, Any] = {}
        for right in ("call", "put"):
            key = (strike, right)
            if key not in oi_map or key not in gamma_map:
                missing_pairs += 1
                continue
            d[f"{right}_oi"] = oi_map[key]
            d[f"{right}_gamma"] = gamma_map[key]
        needed = ("call_oi", "put_oi", "call_gamma", "put_gamma")
        if not all(k in d for k in needed):
            continue
        c = d["call_oi"] * d["call_gamma"]
        p = d["put_oi"] * d["put_gamma"]
        rows.append({
            "strike": strike,
            **d,
            "total_oi": d["call_oi"] + d["put_oi"],
            "call_gamma_oi": c,
            "put_gamma_oi": p,
            "gamma_oi_total": c + p,
            "cp_gamma_imbalance": c - p,
        })

    result = {
        "symbol": symbol,
        "expiration": a.expiration,
        "oi_date": a.oi_date,
        "gamma_date": a.gamma_date,
        "dealer_sign_from_call_put": False,
        "cp_gamma_imbalance_semantics": "call-minus-put structural contrast only; NOT dealer positioning",
        "source_counts": {
            "oi_events": len(oi_rows),
            "greek_events": len(greek_rows),
            "parsed_oi_contract_sides": len(oi_map),
            "parsed_gamma_contract_sides": len(gamma_map),
            "missing_pairs": missing_pairs,
        },
        "rows": rows,
    }
    Path(a.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"usable strikes: {len(rows)}")
    print(f"saved: {Path(a.output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
