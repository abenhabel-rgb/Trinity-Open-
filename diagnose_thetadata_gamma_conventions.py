#!/usr/bin/env python3
"""Diagnose why local Black-Scholes gamma differs from ThetaData EOD gamma.

This is a provider-convention diagnostic only. It does NOT read HeatSeeker data and
it does NOT change any frozen OpenClaw gate/model.

The earlier validator used underlying_timestamp for time-to-expiry. ThetaData's
current documentation says that for <7 DTE with version=latest, real TTE is based on
the option/quote timestamp (1-hour floor). This script tests that hypothesis and
several alternatives against ThetaData's own reported gamma, d1, IV, S and timestamps.

It also derives an implied TTE directly from ThetaData gamma+d1:
    gamma = phi(d1) / (S * sigma * sqrt(T))    [q=0]
so
    T = (phi(d1) / (S * sigma * gamma))^2
This is useful because it isolates the time convention without fitting HeatSeeker.
"""

from __future__ import annotations

import json
import math
import statistics
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

BASE = "http://127.0.0.1:25503/v3"
SYMBOL = "MU"
DATE = "20260623"
EXPIRATION = "20260626"
OUT = Path("mu_20260623_gamma_convention_diagnostic.json")
SECONDS_YEAR = 365.0 * 24.0 * 3600.0
MIN_T = 3600.0 / SECONDS_YEAR


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


def expiry_dt() -> datetime:
    d = datetime.strptime(EXPIRATION, "%Y%m%d")
    return d.replace(hour=16, minute=0, second=0, microsecond=0)


def floor_t(seconds: float) -> float:
    return max(seconds / SECONDS_YEAR, MIN_T)


def t_option_timestamp(r: dict[str, Any]) -> float:
    return floor_t((expiry_dt() - r["timestamp"]).total_seconds())


def t_underlying_timestamp(r: dict[str, Any]) -> float:
    return floor_t((expiry_dt() - r["underlying_timestamp"]).total_seconds())


def t_fixed_close(r: dict[str, Any]) -> float:
    v = r["timestamp"].replace(hour=16, minute=0, second=0, microsecond=0)
    return floor_t((expiry_dt() - v).total_seconds())


def t_full_calendar_days(r: dict[str, Any]) -> float:
    d0 = r["timestamp"].date()
    de = expiry_dt().date()
    return max((de - d0).days / 365.0, MIN_T)


def bs_d1(s: float, k: float, sigma: float, t: float) -> float:
    # Request explicitly sets r=0 and annual dividend=0.
    return (math.log(s / k) + 0.5 * sigma * sigma * t) / (sigma * math.sqrt(t))


def bs_gamma_from_d1(s: float, sigma: float, t: float, d1: float) -> float:
    return norm_pdf(d1) / (s * sigma * math.sqrt(t))


def bs_gamma(s: float, k: float, sigma: float, t: float) -> float:
    return bs_gamma_from_d1(s, sigma, t, bs_d1(s, k, sigma, t))


def quantile(xs: list[float], q: float) -> float:
    if not xs:
        return float("nan")
    ys = sorted(xs)
    pos = (len(ys) - 1) * q
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi:
        return ys[lo]
    w = pos - lo
    return ys[lo] * (1.0 - w) + ys[hi] * w


def summarize_errors(errs: list[float]) -> dict[str, float | int]:
    if not errs:
        return {"n": 0, "median": float("nan"), "p90": float("nan"), "max": float("nan")}
    return {
        "n": len(errs),
        "median": statistics.median(errs),
        "p90": quantile(errs, 0.90),
        "max": max(errs),
    }


def relerr(a: float, b: float) -> float:
    return abs(a - b) / abs(b) if b != 0 else float("nan")


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
    raw = explode(payload)
    print(f"raw EOD rows: {len(raw)}")

    rows: list[dict[str, Any]] = []
    skipped = defaultdict(int)
    for x in raw:
        try:
            r = {
                "strike": float(pick(x, "contract.strike", "strike")),
                "right": str(pick(x, "contract.right", "right")),
                "gamma": float(pick(x, "gamma")),
                "d1": float(pick(x, "d1")),
                "iv": float(pick(x, "implied_vol")),
                "iv_error": float(pick(x, "iv_error")),
                "s": float(pick(x, "underlying_price")),
                "timestamp": parse_ts(pick(x, "timestamp")),
                "underlying_timestamp": parse_ts(pick(x, "underlying_timestamp")),
            }
        except Exception:
            skipped["parse"] += 1
            continue
        if r["gamma"] <= 0 or r["iv"] <= 0 or r["s"] <= 0 or not math.isfinite(r["d1"]):
            skipped["nonpositive_or_nonfinite"] += 1
            continue
        rows.append(r)

    print(f"usable provider rows: {len(rows)}")
    print(f"skipped: {dict(skipped)}")
    if len(rows) < 20:
        print("NOT EVALUABLE: <20 usable rows")
        return 2

    candidates: dict[str, Callable[[dict[str, Any]], float]] = {
        "option_timestamp_to_1600": t_option_timestamp,
        "underlying_timestamp_to_1600": t_underlying_timestamp,
        "fixed_1600_on_valuation_day": t_fixed_close,
        "full_calendar_days": t_full_calendar_days,
    }

    candidate_results: dict[str, Any] = {}
    for name, tfun in candidates.items():
        errs_full: list[float] = []
        errs_provider_d1: list[float] = []
        d1_abs: list[float] = []
        for r in rows:
            t = tfun(r)
            g = bs_gamma(r["s"], r["strike"], r["iv"], t)
            gd1 = bs_gamma_from_d1(r["s"], r["iv"], t, r["d1"])
            if math.isfinite(g):
                errs_full.append(relerr(g, r["gamma"]))
            if math.isfinite(gd1):
                errs_provider_d1.append(relerr(gd1, r["gamma"]))
            try:
                d1_abs.append(abs(bs_d1(r["s"], r["strike"], r["iv"], t) - r["d1"]))
            except Exception:
                pass
        candidate_results[name] = {
            "gamma_full_formula": summarize_errors(errs_full),
            "gamma_using_provider_d1": summarize_errors(errs_provider_d1),
            "d1_abs_error": {
                "n": len(d1_abs),
                "median": statistics.median(d1_abs) if d1_abs else float("nan"),
                "p90": quantile(d1_abs, 0.90),
            },
        }

    # Infer ThetaData T directly from provider gamma+d1 under q=0.
    inferred_hours: list[float] = []
    ratio_by_candidate: dict[str, list[float]] = {k: [] for k in candidates}
    for r in rows:
        denom = r["s"] * r["iv"] * r["gamma"]
        if denom <= 0:
            continue
        t_inf = (norm_pdf(r["d1"]) / denom) ** 2
        if not math.isfinite(t_inf) or t_inf <= 0:
            continue
        inferred_hours.append(t_inf * SECONDS_YEAR / 3600.0)
        for name, tfun in candidates.items():
            tc = tfun(r)
            if tc > 0:
                ratio_by_candidate[name].append(t_inf / tc)

    inferred_summary = {
        "n": len(inferred_hours),
        "median_hours": statistics.median(inferred_hours),
        "p10_hours": quantile(inferred_hours, 0.10),
        "p90_hours": quantile(inferred_hours, 0.90),
        "median_T_ratio_to_candidates": {
            name: statistics.median(vals) if vals else float("nan")
            for name, vals in ratio_by_candidate.items()
        },
    }

    # Determine whether tails are dominated by poor IV fits or stale timestamps.
    subset_results: dict[str, Any] = {}
    subsets = {
        "iv_error_le_0.01": lambda r: abs(r["iv_error"]) <= 0.01,
        "iv_error_le_0.05": lambda r: abs(r["iv_error"]) <= 0.05,
        "moneyness_0.8_to_1.2": lambda r: 0.8 <= r["strike"] / r["s"] <= 1.2,
        "timestamp_gap_le_60s": lambda r: abs((r["timestamp"] - r["underlying_timestamp"]).total_seconds()) <= 60,
    }
    for sname, pred in subsets.items():
        rr = [r for r in rows if pred(r)]
        errs = []
        for r in rr:
            g = bs_gamma(r["s"], r["strike"], r["iv"], t_option_timestamp(r))
            if math.isfinite(g):
                errs.append(relerr(g, r["gamma"]))
        subset_results[sname] = summarize_errors(errs)

    ranked = sorted(
        candidate_results,
        key=lambda k: candidate_results[k]["gamma_full_formula"]["median"],
    )
    best = ranked[0]

    result = {
        "purpose": "ThetaData EOD gamma convention diagnostic; no HeatSeeker fit",
        "symbol": SYMBOL,
        "date": DATE,
        "expiration": EXPIRATION,
        "request_controls": {
            "rate_value": 0,
            "annual_dividend": 0,
            "version": "latest",
            "underlyer_use_nbbo": False,
        },
        "candidate_results": candidate_results,
        "inferred_tte_from_provider_gamma_d1": inferred_summary,
        "subset_results_using_option_timestamp": subset_results,
        "best_candidate_by_median_full_gamma_error": best,
        "note": "Diagnostic only. Frozen validators/gates are unchanged.",
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("\nTHETADATA GAMMA CONVENTION DIAGNOSTIC")
    print("No HeatSeeker values are used. No frozen model/gate is changed.")
    for name in ranked:
        x = candidate_results[name]
        gf = x["gamma_full_formula"]
        gd = x["gamma_using_provider_d1"]
        de = x["d1_abs_error"]
        print(f"\n{name}")
        print(f"  full gamma:       n={gf['n']} median={gf['median']:.6f} p90={gf['p90']:.6f}")
        print(f"  provider-d1 gamma:n={gd['n']} median={gd['median']:.6f} p90={gd['p90']:.6f}")
        print(f"  |local d1-provider d1| median={de['median']:.6f} p90={de['p90']:.6f}")

    print("\nTTE INFERRED DIRECTLY FROM PROVIDER gamma+d1")
    print(f"n={inferred_summary['n']} median_hours={inferred_summary['median_hours']:.3f} "
          f"p10={inferred_summary['p10_hours']:.3f} p90={inferred_summary['p90_hours']:.3f}")
    for name, ratio in inferred_summary["median_T_ratio_to_candidates"].items():
        print(f"  median inferred_T / {name} = {ratio:.6f}")

    print("\nOPTION-TIMESTAMP FORMULA — ROBUSTNESS SUBSETS")
    for name, s in subset_results.items():
        print(f"  {name}: n={s['n']} median={s['median']:.6f} p90={s['p90']:.6f}")

    print(f"\nBEST TIME CANDIDATE BY MEDIAN FULL-GAMMA ERROR: {best}")
    print(f"saved: {OUT.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
