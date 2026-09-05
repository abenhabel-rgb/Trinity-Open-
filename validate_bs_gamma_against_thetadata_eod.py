#!/usr/bin/env python3
"""Validate a local Black-Scholes gamma reconstruction against observed ThetaData EOD gamma.

Purpose
-------
Before any reconstructed intraday gamma is allowed into OpenClaw, verify that the
local formula reproduces ThetaData's own EOD gamma on a date where ThetaData returns
both gamma and implied volatility.

This is NOT a HeatSeeker fit. No HeatSeeker values are read.

Controls
--------
- ThetaData is explicitly requested with rate_value=0 and annual_dividend=0, so the
  local reconstruction has no unobserved rate/dividend proxy.
- version=latest is used on both sides.
- time-to-expiry is computed from ThetaData's underlying_timestamp to 16:00 ET on
  expiration day, with ThetaData's documented 1-hour minimum.
- IV unit semantics are tested only to identify API units (raw vs percent /100).

Predeclared validation gate
---------------------------
PASS only if:
- >= 20 usable contract rows,
- median absolute relative gamma error <= 2%, and
- 90th percentile absolute relative gamma error <= 5%.

A FAIL means reconstructed intraday gamma remains prohibited.
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
DATE = "20260623"
EXPIRATION = "20260626"
OUT = Path("mu_20260623_bs_gamma_validation.json")


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
        if name.lower() in f and f[name.lower()] is not None:
            return f[name.lower()]
    raise KeyError(" / ".join(names))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def parse_ts(s: str) -> datetime:
    # ThetaData v3 historical rows are ET-local timestamps without an offset.
    return datetime.fromisoformat(s)


def t_years(ts: datetime) -> float:
    exp_date = datetime.strptime(EXPIRATION, "%Y%m%d")
    expiry = exp_date.replace(hour=16, minute=0, second=0, microsecond=0)
    seconds = max((expiry - ts).total_seconds(), 3600.0)  # documented 1h floor
    return seconds / (365.0 * 24.0 * 3600.0)


def bs_gamma(s: float, k: float, sigma: float, t: float) -> float:
    # Requested comparison environment: r=0, q=0.
    if s <= 0 or k <= 0 or sigma <= 0 or t <= 0:
        return float("nan")
    root_t = math.sqrt(t)
    d1 = (math.log(s / k) + 0.5 * sigma * sigma * t) / (sigma * root_t)
    return norm_pdf(d1) / (s * sigma * root_t)


def quantile(xs: list[float], q: float) -> float:
    if not xs:
        return float("nan")
    ys = sorted(xs)
    pos = (len(ys) - 1) * q
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi:
        return ys[lo]
    w = pos - lo
    return ys[lo] * (1 - w) + ys[hi] * w


def main() -> int:
    payload = get("/option/history/greeks/eod", {
        "symbol": SYMBOL,
        "start_date": DATE,
        "end_date": DATE,
        "expiration": EXPIRATION,
        "strike": "*",
        "right": "both",
        "annual_dividend": 0,
        "rate_value": 0,
        "version": "latest",
        "underlyer_use_nbbo": "false",
        "format": "json",
    })
    rows = explode(payload)
    print(f"raw EOD rows: {len(rows)}")

    base = []
    for r in rows:
        try:
            k = float(pick(r, "contract.strike", "strike"))
            right = str(pick(r, "contract.right", "right"))
            provider_gamma = float(pick(r, "gamma"))
            iv = float(pick(r, "implied_vol"))
            s = float(pick(r, "underlying_price"))
            ts = parse_ts(str(pick(r, "underlying_timestamp")))
        except Exception:
            continue
        if provider_gamma <= 0 or iv <= 0 or s <= 0:
            continue
        t = t_years(ts)
        base.append((k, right, provider_gamma, iv, s, ts, t))

    if len(base) < 20:
        print(f"FAIL: only {len(base)} usable rows (<20)")
        return 2

    # Unit-semantics check only; this does not use HeatSeeker or optimize model parameters.
    candidates = {"raw": 1.0, "percent_div_100": 0.01}
    candidate_medians: dict[str, float] = {}
    for name, scale in candidates.items():
        errs = []
        for k, right, pg, iv, s, ts, t in base:
            g = bs_gamma(s, k, iv * scale, t)
            if math.isfinite(g) and pg != 0:
                errs.append(abs(g - pg) / abs(pg))
        candidate_medians[name] = statistics.median(errs) if errs else float("inf")

    iv_semantics = min(candidate_medians, key=candidate_medians.get)
    iv_scale = candidates[iv_semantics]

    out_rows = []
    rel_errors = []
    for k, right, pg, iv, s, ts, t in base:
        g = bs_gamma(s, k, iv * iv_scale, t)
        if not math.isfinite(g) or pg == 0:
            continue
        re = abs(g - pg) / abs(pg)
        rel_errors.append(re)
        out_rows.append({
            "strike": k,
            "right": right,
            "provider_gamma": pg,
            "reconstructed_gamma": g,
            "implied_vol_raw": iv,
            "iv_scale": iv_scale,
            "underlying_price": s,
            "underlying_timestamp": ts.isoformat(timespec="milliseconds"),
            "tte_years": t,
            "abs_relative_error": re,
        })

    med = statistics.median(rel_errors)
    p90 = quantile(rel_errors, 0.90)
    mx = max(rel_errors)
    passed = len(rel_errors) >= 20 and med <= 0.02 and p90 <= 0.05

    result = {
        "status": "PASS" if passed else "FAIL",
        "purpose": "validate local BS gamma reconstruction against ThetaData EOD before any intraday use",
        "symbol": SYMBOL,
        "date": DATE,
        "expiration": EXPIRATION,
        "theta_request_controls": {
            "rate_value": 0,
            "annual_dividend": 0,
            "version": "latest",
            "underlyer_use_nbbo": False,
        },
        "iv_semantics_test": candidate_medians,
        "selected_iv_semantics": iv_semantics,
        "selected_iv_scale": iv_scale,
        "gate": {
            "min_rows": 20,
            "median_abs_relative_error_max": 0.02,
            "p90_abs_relative_error_max": 0.05,
        },
        "summary": {
            "usable_rows": len(rel_errors),
            "median_abs_relative_error": med,
            "p90_abs_relative_error": p90,
            "max_abs_relative_error": mx,
        },
        "rows": out_rows,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("THETADATA EOD -> LOCAL BLACK-SCHOLES GAMMA VALIDATION")
    print(f"usable rows: {len(rel_errors)}")
    print(f"IV semantics selected: {iv_semantics} (scale={iv_scale})")
    print(f"candidate median errors: {candidate_medians}")
    print(f"median absolute relative error: {med:.6f}")
    print(f"p90 absolute relative error:    {p90:.6f}")
    print(f"max absolute relative error:    {mx:.6f}")
    print("GATE: median<=0.02, p90<=0.05, n>=20")
    print(f"OVERALL: {'PASS' if passed else 'FAIL'}")
    print(f"saved: {OUT.resolve()}")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
