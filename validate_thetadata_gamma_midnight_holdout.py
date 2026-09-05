#!/usr/bin/env python3
"""Held-out validation of ThetaData gamma time-to-expiry convention.

Why this exists
---------------
The 2026-06-23 development diagnostic inferred a median TTE around 80.7 hours for
MU options expiring 2026-06-26, whereas a same-day 16:00 expiry clock gives about
72 hours. That pattern is consistent with an expiry clock near midnight AFTER the
expiration date (2026-06-27 00:00 ET).

This script freezes that hypothesis BEFORE looking at a different EOD date and tests
it on 2026-06-22. It does not read HeatSeeker and does not alter any H1-H5 gate.

Primary held-out convention
---------------------------
T = max((next_midnight_after_expiration - underlying_timestamp), 1 hour) / year

Reference baseline
------------------
Same formula but expiration at 16:00 ET on expiration date.

Validation gate (unchanged from the earlier gamma validator)
-------------------------------------------------------------
PASS only if, on the held-out date:
- >= 20 usable rows
- median absolute relative gamma error <= 2%
- p90 absolute relative gamma error <= 5%

If this fails, reconstructed intraday gamma remains prohibited.
"""

from __future__ import annotations

import json
import math
import statistics
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

BASE = "http://127.0.0.1:25503/v3"
SYMBOL = "MU"
DEVELOPMENT_DATE = "20260623"
HOLDOUT_DATE = "20260622"
EXPIRATION = "20260626"
OUT = Path("mu_20260622_gamma_midnight_holdout.json")
SECONDS_YEAR = 365.0 * 24.0 * 3600.0
MIN_SECONDS = 3600.0


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
                if isinstance(event, dict):
                    row = dict(event)
                    row["contract"] = dict(contract)
                    out.append(row)
        else:
            out.append(dict(item))
    return out


def flat(obj: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            full = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, dict):
                out.update(flat(v, full))
            else:
                out[full.lower()] = v
                out.setdefault(str(k).lower(), v)
    return out


def pick(row: dict[str, Any], *names: str) -> Any:
    f = flat(row)
    for name in names:
        key = name.lower()
        if key in f and f[key] is not None:
            return f[key]
    raise KeyError(" / ".join(names))


def parse_ts(v: Any) -> datetime:
    return datetime.fromisoformat(str(v))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def expiry_1600() -> datetime:
    d = datetime.strptime(EXPIRATION, "%Y%m%d")
    return d.replace(hour=16, minute=0, second=0, microsecond=0)


def expiry_next_midnight() -> datetime:
    d = datetime.strptime(EXPIRATION, "%Y%m%d")
    return (d + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


def t_years(ts: datetime, expiry: datetime) -> float:
    sec = max((expiry - ts).total_seconds(), MIN_SECONDS)
    return sec / SECONDS_YEAR


def bs_d1(s: float, k: float, sigma: float, t: float) -> float:
    return (math.log(s / k) + 0.5 * sigma * sigma * t) / (sigma * math.sqrt(t))


def bs_gamma(s: float, k: float, sigma: float, t: float) -> float:
    d1 = bs_d1(s, k, sigma, t)
    return norm_pdf(d1) / (s * sigma * math.sqrt(t))


def quantile(xs: list[float], q: float) -> float:
    ys = sorted(xs)
    if not ys:
        return float("nan")
    pos = (len(ys) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ys[lo]
    w = pos - lo
    return ys[lo] * (1.0 - w) + ys[hi] * w


def relerr(a: float, b: float) -> float:
    return abs(a - b) / abs(b) if b != 0 else float("nan")


def load_date(date: str) -> list[dict[str, Any]]:
    payload = get("/option/history/greeks/eod", {
        "symbol": SYMBOL,
        "start_date": date,
        "end_date": date,
        "expiration": EXPIRATION,
        "strike": "*",
        "right": "both",
        "annual_dividend": 0,
        "rate_value": 0,
        "version": "latest",
        "underlyer_use_nbbo": "false",
        "format": "json",
    })
    raw = explode(payload)
    rows: list[dict[str, Any]] = []
    for x in raw:
        try:
            r = {
                "strike": float(pick(x, "contract.strike", "strike")),
                "right": str(pick(x, "contract.right", "right")),
                "gamma": float(pick(x, "gamma")),
                "d1": float(pick(x, "d1")),
                "iv": float(pick(x, "implied_vol")),
                "s": float(pick(x, "underlying_price")),
                "underlying_timestamp": parse_ts(pick(x, "underlying_timestamp")),
            }
        except Exception:
            continue
        if r["gamma"] <= 0 or r["iv"] <= 0 or r["s"] <= 0 or not math.isfinite(r["d1"]):
            continue
        rows.append(r)
    print(f"{date}: usable rows={len(rows)}")
    return rows


def summarize(rows: list[dict[str, Any]], expiry: datetime) -> dict[str, Any]:
    errs: list[float] = []
    d1_errs: list[float] = []
    ratios_inferred_t: list[float] = []
    out_rows: list[dict[str, Any]] = []

    for r in rows:
        t = t_years(r["underlying_timestamp"], expiry)
        try:
            g = bs_gamma(r["s"], r["strike"], r["iv"], t)
            d1_local = bs_d1(r["s"], r["strike"], r["iv"], t)
        except Exception:
            continue
        if not math.isfinite(g) or g <= 0:
            continue
        e = relerr(g, r["gamma"])
        if math.isfinite(e):
            errs.append(e)
        d1e = abs(d1_local - r["d1"])
        if math.isfinite(d1e):
            d1_errs.append(d1e)

        denom = r["s"] * r["iv"] * r["gamma"]
        if denom > 0:
            t_inf = (norm_pdf(r["d1"]) / denom) ** 2
            if math.isfinite(t_inf) and t > 0:
                ratios_inferred_t.append(t_inf / t)

        out_rows.append({
            "strike": r["strike"],
            "right": r["right"],
            "provider_gamma": r["gamma"],
            "local_gamma": g,
            "abs_relative_error": e,
            "provider_d1": r["d1"],
            "local_d1": d1_local,
            "underlying_timestamp": r["underlying_timestamp"].isoformat(timespec="milliseconds"),
            "tte_hours": t * SECONDS_YEAR / 3600.0,
        })

    return {
        "n": len(errs),
        "median_abs_relative_error": statistics.median(errs) if errs else float("nan"),
        "p90_abs_relative_error": quantile(errs, 0.90),
        "median_abs_d1_error": statistics.median(d1_errs) if d1_errs else float("nan"),
        "p90_abs_d1_error": quantile(d1_errs, 0.90),
        "median_inferred_T_over_candidate_T": statistics.median(ratios_inferred_t) if ratios_inferred_t else float("nan"),
        "rows": out_rows,
    }


def short(x: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in x.items() if k != "rows"}


def main() -> int:
    print("THETADATA GAMMA MIDNIGHT-CONVENTION HOLDOUT")
    print("No HeatSeeker values are used. No frozen OpenClaw gate/model is changed.")
    print("Development date only confirms the already-observed clue; holdout date decides validation.")

    dev = load_date(DEVELOPMENT_DATE)
    hold = load_date(HOLDOUT_DATE)
    if len(hold) < 20:
        print("NOT EVALUABLE: holdout has <20 usable rows")
        return 2

    e16 = expiry_1600()
    emid = expiry_next_midnight()

    dev_16 = summarize(dev, e16)
    dev_mid = summarize(dev, emid)
    hold_16 = summarize(hold, e16)
    hold_mid = summarize(hold, emid)

    print("\nDEVELOPMENT 2026-06-23 — DESCRIPTIVE ONLY")
    print(f"16:00 baseline: median={dev_16['median_abs_relative_error']:.6f} p90={dev_16['p90_abs_relative_error']:.6f} T_ratio={dev_16['median_inferred_T_over_candidate_T']:.6f}")
    print(f"next-midnight:  median={dev_mid['median_abs_relative_error']:.6f} p90={dev_mid['p90_abs_relative_error']:.6f} T_ratio={dev_mid['median_inferred_T_over_candidate_T']:.6f}")

    print("\nHOLDOUT 2026-06-22 — PRIMARY VALIDATION")
    print(f"16:00 baseline: median={hold_16['median_abs_relative_error']:.6f} p90={hold_16['p90_abs_relative_error']:.6f} n={hold_16['n']}")
    print(f"next-midnight:  median={hold_mid['median_abs_relative_error']:.6f} p90={hold_mid['p90_abs_relative_error']:.6f} n={hold_mid['n']}")
    print(f"next-midnight d1 error: median={hold_mid['median_abs_d1_error']:.6f} p90={hold_mid['p90_abs_d1_error']:.6f}")
    print(f"next-midnight inferred_T/candidate_T median={hold_mid['median_inferred_T_over_candidate_T']:.6f}")

    passed = (
        hold_mid["n"] >= 20
        and hold_mid["median_abs_relative_error"] <= 0.02
        and hold_mid["p90_abs_relative_error"] <= 0.05
    )

    print("\nUNCHANGED VALIDATION GATE")
    print(f"n >= 20:                         {'PASS' if hold_mid['n'] >= 20 else 'FAIL'} ({hold_mid['n']})")
    print(f"median relative error <= 2%:    {'PASS' if hold_mid['median_abs_relative_error'] <= 0.02 else 'FAIL'} ({hold_mid['median_abs_relative_error']:.6f})")
    print(f"p90 relative error <= 5%:       {'PASS' if hold_mid['p90_abs_relative_error'] <= 0.05 else 'FAIL'} ({hold_mid['p90_abs_relative_error']:.6f})")
    print(f"OVERALL: {'PASS' if passed else 'FAIL'}")

    result = {
        "purpose": "held-out validation of next-midnight-after-expiration TTE convention",
        "symbol": SYMBOL,
        "expiration": EXPIRATION,
        "development_date": DEVELOPMENT_DATE,
        "holdout_date": HOLDOUT_DATE,
        "controls": {
            "rate_value": 0,
            "annual_dividend": 0,
            "version": "latest",
            "underlyer_use_nbbo": False,
            "timestamp_source": "underlying_timestamp",
            "primary_expiry_clock": "00:00 ET on calendar day after expiration",
            "minimum_tte_hours": 1,
        },
        "development": {
            "expiry_1600": short(dev_16),
            "expiry_next_midnight": short(dev_mid),
        },
        "holdout": {
            "expiry_1600": short(hold_16),
            "expiry_next_midnight": short(hold_mid),
        },
        "gate": {
            "min_rows": 20,
            "median_abs_relative_error_max": 0.02,
            "p90_abs_relative_error_max": 0.05,
        },
        "status": "PASS" if passed else "FAIL",
        "note": "A PASS validates only this ThetaData reconstruction convention; it does not validate any HeatSeeker hypothesis.",
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"saved: {OUT.resolve()}")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
