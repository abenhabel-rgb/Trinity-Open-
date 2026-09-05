#!/usr/bin/env python3
"""MU 2026-04-28 09:50 ET — observed-variable GEX exploratory test.

Purpose
-------
Use a new MU HeatSeeker GEX card to compare ONLY observed market variables or
previously frozen transparent transforms:
- settled OI,
- prior-close ThetaData EOD gamma * OI,
- raw trade volume,
- trade count,
- frozen-v1 quote-edge signed flow / signed premium,
- observed intraday implied volatility,
- observed bid/ask spread.

This script is EXPLORATORY. It does not modify or rescue H1-H5 and it does not
reconstruct intraday gamma. Publication time (09:50 ET) is only an outer bound
for the unknown exact HeatSeeker snapshot time.

HeatSeeker source transcribed from the user-provided screenshot:
MU, published 2026-04-28 15:50 Paris = 09:50 ET, spot 515.46,
expiration column 2026-05-01. Only fully legible strikes 475.0..557.5 are used.
King in this visible column: strike 500.0, GEX -1908.7K.
"""

from __future__ import annotations

import json
import math
import statistics
import subprocess
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

BASE = "http://127.0.0.1:25503/v3"
SYMBOL = "MU"
DATE = "20260428"
EXPIRATION = "20260501"
SPOT = 515.46
START = "09:30:00"
END = "09:50:00"
GAMMA_DATE = "20260427"
KING = 500.0

FLOW_FILE = Path("mu_20260428_20260501_095000_volland_like_frozen_v1.json")
STATIC_FILE = Path("mu_20260428_20260501_static_oi_gamma.json")
IV_FILE = Path("mu_20260428_0945_0950_intraday_iv_raw.json")
OUT_FILE = Path("mu_20260428_gex_observed_exploratory.json")

# HeatSeeker GEX, K units exactly as displayed in the fully legible 2026-05-01 column.
HS_GEX_K = {
    557.5: -7.6,
    555.0: -14.5,
    552.5: -28.6,
    550.0: 865.1,
    547.5: -2.0,
    545.0: 36.7,
    542.5: -7.0,
    540.0: 268.9,
    537.5: 6.2,
    535.0: 30.8,
    532.5: 21.3,
    530.0: 146.3,
    527.5: 75.1,
    525.0: -615.7,
    522.5: 5.1,
    520.0: 54.8,
    517.5: 43.8,
    515.0: 321.5,
    512.5: 4.2,
    510.0: -768.7,
    507.5: 3.7,
    505.0: 329.6,
    502.5: 24.6,
    500.0: -1908.7,
    497.5: -8.6,
    495.0: -73.3,
    492.5: 30.5,
    490.0: -349.7,
    487.5: 26.1,
    485.0: 84.8,
    482.5: 77.5,
    480.0: -1117.0,
    477.5: -47.7,
    475.0: -245.3,
}


def run(cmd: list[str]) -> None:
    print("\n$ " + " ".join(cmd))
    p = subprocess.run(cmd)
    if p.returncode != 0:
        raise RuntimeError(f"command failed with exit code {p.returncode}: {' '.join(cmd)}")


def get_json(path: str, params: dict[str, Any]) -> object:
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    print("\nThetaData IV request:")
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


def rankdata(xs: list[float]) -> list[float]:
    pairs = sorted(enumerate(xs), key=lambda z: z[1])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(pairs):
        j = i + 1
        while j < len(pairs) and pairs[j][1] == pairs[i][1]:
            j += 1
        avg = (i + 1 + j) / 2.0  # 1-based average rank
        for k in range(i, j):
            ranks[pairs[k][0]] = avg
        i = j
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 3:
        return float("nan")
    mx, my = statistics.mean(xs), statistics.mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    if den == 0:
        return float("nan")
    return sum(x*y for x, y in zip(dx, dy)) / den


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(rankdata(xs), rankdata(ys))


def residualize(y: list[float], z: list[float]) -> list[float]:
    # OLS y ~ 1 + z, standard-library implementation.
    mz, my = statistics.mean(z), statistics.mean(y)
    den = sum((v - mz) ** 2 for v in z)
    beta = 0.0 if den == 0 else sum((a-mz)*(b-my) for a, b in zip(z, y)) / den
    alpha = my - beta * mz
    return [b - (alpha + beta*a) for a, b in zip(z, y)]


def partial_spearman(x: list[float], y: list[float], z: list[float]) -> float:
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    return pearson(residualize(rx, rz), residualize(ry, rz))


def corr(rows: list[dict[str, Any]], xkey: str, ykey: str) -> tuple[int, float]:
    pairs = []
    for r in rows:
        x, y = r.get(xkey), r.get(ykey)
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) and math.isfinite(float(x)) and math.isfinite(float(y)):
            pairs.append((float(x), float(y)))
    if len(pairs) < 3:
        return len(pairs), float("nan")
    return len(pairs), spearman([p[0] for p in pairs], [p[1] for p in pairs])


def sign_agreement(rows: list[dict[str, Any]], xkey: str, ykey: str) -> tuple[int, int, float]:
    good = total = 0
    for r in rows:
        x, y = r.get(xkey), r.get(ykey)
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            continue
        if x == 0 or y == 0:
            continue
        total += 1
        good += int((x > 0) == (y > 0))
    return good, total, (good / total if total else float("nan"))


def latest_iv_by_side(payload: object) -> dict[tuple[float, str], dict[str, float]]:
    # Rows are minute observations. Keep the lexicographically latest ISO timestamp
    # per strike/right in the 09:45-09:50 query window.
    best: dict[tuple[float, str], tuple[str, dict[str, float]]] = {}
    for r in explode(payload):
        try:
            strike = float(pick(r, "contract.strike", "strike"))
            right = right_norm(pick(r, "contract.right", "right"))
            ts = str(pick(r, "timestamp"))
            iv = float(pick(r, "implied_vol"))
            bid = float(pick(r, "bid"))
            ask = float(pick(r, "ask"))
            mid = float(pick(r, "midpoint"))
            iv_error = float(pick(r, "iv_error"))
            under = float(pick(r, "underlying_price"))
        except Exception:
            continue
        if right not in ("call", "put"):
            continue
        d = {
            "iv": iv,
            "bid": bid,
            "ask": ask,
            "midpoint": mid,
            "iv_error": iv_error,
            "underlying_price": under,
        }
        key = (strike, right)
        if key not in best or ts > best[key][0]:
            best[key] = (ts, d)
    return {k: v[1] for k, v in best.items()}


def main() -> int:
    print("MU 2026-04-28 GEX — OBSERVED-VARIABLE EXPLORATORY TEST")
    print("No intraday gamma reconstruction. No H1-H5 gate is changed.")
    print(f"HeatSeeker publication outer bound: {END} ET; spot={SPOT}; expiration={EXPIRATION}")
    print(f"Visible HeatSeeker strikes transcribed: {len(HS_GEX_K)}; King={KING}")

    # 1) Frozen signed-flow collector, unchanged.
    run([
        sys.executable, "volland_like_frozen_v1.py",
        "--symbol", SYMBOL,
        "--date", DATE,
        "--expiration", EXPIRATION,
        "--start-time", START,
        "--end-time", END,
        "--spot", str(SPOT),
        "--output", str(FLOW_FILE),
    ])

    # 2) Static settled OI + observed prior-close ThetaData EOD gamma.
    run([
        sys.executable, "collect_mu_static_structure.py",
        "--symbol", SYMBOL,
        "--expiration", EXPIRATION,
        "--oi-date", DATE,
        "--gamma-date", GAMMA_DATE,
        "--output", str(STATIC_FILE),
    ])

    # 3) Observed intraday IV / bid / ask only; no gamma reconstruction.
    iv_payload = get_json("/option/history/greeks/implied_volatility", {
        "symbol": SYMBOL,
        "expiration": EXPIRATION,
        "date": DATE,
        "strike": "*",
        "right": "both",
        "start_time": "09:45:00",
        "end_time": END,
        "interval": "1m",
        "version": "latest",
        "format": "json",
    })
    IV_FILE.write_text(json.dumps(iv_payload, indent=2), encoding="utf-8")

    flow = json.loads(FLOW_FILE.read_text(encoding="utf-8"))
    static = json.loads(STATIC_FILE.read_text(encoding="utf-8"))
    fmap = {float(r["strike"]): r for r in flow.get("rows", [])}
    smap = {float(r["strike"]): r for r in static.get("rows", [])}
    ivmap = latest_iv_by_side(iv_payload)

    rows: list[dict[str, Any]] = []
    for strike, gex in sorted(HS_GEX_K.items()):
        r: dict[str, Any] = {
            "strike": strike,
            "heatseeker_gex_k": gex,
            "abs_heatseeker_gex_k": abs(gex),
            "is_king": strike == KING,
        }
        if strike in fmap:
            f = fmap[strike]
            for k in ("trade_count", "classified_contracts", "unknown_contracts", "signed_contract_flow",
                      "signed_premium_notional", "raw_contract_volume", "unknown_fraction"):
                if k in f:
                    r[k] = f[k]
            if "signed_premium_notional" in r:
                r["abs_signed_premium_notional"] = abs(float(r["signed_premium_notional"]))
        if strike in smap:
            s = smap[strike]
            for k in ("call_oi", "put_oi", "total_oi", "call_gamma_oi", "put_gamma_oi",
                      "gamma_oi_total", "cp_gamma_imbalance"):
                if k in s:
                    r[k] = s[k]
        sides = {side: ivmap.get((strike, side)) for side in ("call", "put")}
        valid_ivs = []
        rel_spreads = []
        dollar_spreads = []
        for side, d in sides.items():
            if not d:
                continue
            iv = d["iv"]
            if iv > 0 and math.isfinite(iv):
                r[f"{side}_iv"] = iv
                r[f"{side}_iv_error"] = d["iv_error"]
                valid_ivs.append(iv)
            bid, ask, mid = d["bid"], d["ask"], d["midpoint"]
            if ask >= bid and math.isfinite(ask) and math.isfinite(bid):
                spread = ask - bid
                dollar_spreads.append(spread)
                if mid > 0:
                    rel_spreads.append(spread / mid)
            if d["underlying_price"] > 0:
                r[f"{side}_underlying_price"] = d["underlying_price"]
        if valid_ivs:
            r["mean_observed_iv"] = statistics.mean(valid_ivs)
            r["valid_iv_sides"] = len(valid_ivs)
        if "call_iv" in r and "put_iv" in r:
            r["call_minus_put_iv"] = r["call_iv"] - r["put_iv"]
            r["abs_call_minus_put_iv"] = abs(r["call_minus_put_iv"])
        if dollar_spreads:
            r["mean_dollar_spread"] = statistics.mean(dollar_spreads)
        if rel_spreads:
            r["mean_relative_spread"] = statistics.mean(rel_spreads)
        rows.append(r)

    all_rows = rows
    ex_king = [r for r in rows if not r["is_king"]]

    direction_features = [
        "signed_contract_flow",
        "signed_premium_notional",
        "cp_gamma_imbalance",
        "call_minus_put_iv",
    ]
    magnitude_features = [
        "total_oi",
        "gamma_oi_total",
        "raw_contract_volume",
        "trade_count",
        "abs_signed_premium_notional",
        "mean_observed_iv",
        "abs_call_minus_put_iv",
        "mean_dollar_spread",
        "mean_relative_spread",
    ]

    def evaluate(label: str, rr: list[dict[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {"n_heatseeker": len(rr), "direction": {}, "magnitude": {}}
        for f in direction_features:
            n, rho = corr(rr, f, "heatseeker_gex_k")
            good, total, sign = sign_agreement(rr, f, "heatseeker_gex_k")
            out["direction"][f] = {"n": n, "spearman": rho, "sign_good": good, "sign_n": total, "sign_agreement": sign}
        for f in magnitude_features:
            n, rho = corr(rr, f, "abs_heatseeker_gex_k")
            out["magnitude"][f] = {"n": n, "spearman": rho}

        # Incremental descriptive tests. No gates, no confirmatory status.
        triples = []
        for r in rr:
            if all(isinstance(r.get(k), (int, float)) and math.isfinite(float(r[k]))
                   for k in ("signed_contract_flow", "heatseeker_gex_k", "cp_gamma_imbalance")):
                triples.append(r)
        if len(triples) >= 5:
            out["partial_direction_flow_given_static_cp"] = {
                "n": len(triples),
                "partial_spearman": partial_spearman(
                    [float(r["signed_contract_flow"]) for r in triples],
                    [float(r["heatseeker_gex_k"]) for r in triples],
                    [float(r["cp_gamma_imbalance"]) for r in triples],
                ),
            }

        triples = []
        for r in rr:
            if all(isinstance(r.get(k), (int, float)) and math.isfinite(float(r[k]))
                   for k in ("raw_contract_volume", "abs_heatseeker_gex_k", "gamma_oi_total")):
                triples.append(r)
        if len(triples) >= 5:
            out["partial_magnitude_volume_given_static_gammaoi"] = {
                "n": len(triples),
                "partial_spearman": partial_spearman(
                    [float(r["raw_contract_volume"]) for r in triples],
                    [float(r["abs_heatseeker_gex_k"]) for r in triples],
                    [float(r["gamma_oi_total"]) for r in triples],
                ),
            }
        return out

    eval_all = evaluate("all", all_rows)
    eval_ex = evaluate("ex_king", ex_king)

    result = {
        "status": "EXPLORATORY_ONLY",
        "symbol": SYMBOL,
        "date": DATE,
        "publication_outer_bound_et": END,
        "publication_paris": "2026-04-28 15:50",
        "spot_displayed": SPOT,
        "expiration": EXPIRATION,
        "heatseeker_source": {
            "metric": "GEX",
            "units_transcribed": "K as displayed",
            "visible_strike_range": [475.0, 557.5],
            "king_strike": KING,
            "king_gex_k": HS_GEX_K[KING],
            "exact_snapshot_time_known": False,
        },
        "data_controls": {
            "flow_method": "volland_like_frozen_v1.py unchanged",
            "flow_window_et": [START, END],
            "oi_date": DATE,
            "prior_close_gamma_date": GAMMA_DATE,
            "intraday_iv_window_et": ["09:45:00", END],
            "intraday_gamma_reconstructed": False,
            "dealer_sign_from_call_put": False,
        },
        "flow_summary": flow.get("summary", {}),
        "static_source_counts": static.get("source_counts", {}),
        "evaluations": {"all": eval_all, "ex_king": eval_ex},
        "rows": rows,
        "limitations": [
            "exploratory test; no H1-H5 gate is modified",
            "publication time is an outer bound, not proven HeatSeeker snapshot time",
            "prior-close gamma is observed but may be stale intraday",
            "signed flow is a transparent quote-edge classifier, not observed dealer inventory",
            "call-minus-put gamma*OI is structural contrast only, not dealer positioning",
            "IV and spreads are observed directly; no intraday gamma is reconstructed",
        ],
    }
    OUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    def show(label: str, ev: dict[str, Any]) -> None:
        print(f"\n=== {label} ===")
        print("DIRECTION vs signed HeatSeeker GEX (Spearman; sign agreement)")
        for f in direction_features:
            x = ev["direction"][f]
            print(f"{f:30s} n={x['n']:2d} rho={x['spearman']:+.3f} sign={x['sign_agreement']:.3f} ({x['sign_good']}/{x['sign_n']})")
        if "partial_direction_flow_given_static_cp" in ev:
            x = ev["partial_direction_flow_given_static_cp"]
            print(f"partial flow | static cp       n={x['n']:2d} rho={x['partial_spearman']:+.3f}")

        print("MAGNITUDE vs |HeatSeeker GEX| (Spearman)")
        for f in magnitude_features:
            x = ev["magnitude"][f]
            print(f"{f:30s} n={x['n']:2d} rho={x['spearman']:+.3f}")
        if "partial_magnitude_volume_given_static_gammaoi" in ev:
            x = ev["partial_magnitude_volume_given_static_gammaoi"]
            print(f"partial volume | gammaOI      n={x['n']:2d} rho={x['partial_spearman']:+.3f}")

    print("\nMU 2026-04-28 GEX OBSERVED-VARIABLE RESULTS")
    show("ALL VISIBLE STRIKES", eval_all)
    show("EX-KING 500", eval_ex)
    print("\nSTATUS: EXPLORATORY_ONLY — H1-H5 unchanged")
    print(f"saved: {OUT_FILE.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
