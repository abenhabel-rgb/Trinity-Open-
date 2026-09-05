#!/usr/bin/env python3
"""MU 2026-04-06 — frozen-protocol second-layer replication diagnostic.

New HeatSeeker card supplied after the 2026-04-28 residual protocol was fixed.

Card facts transcribed from screenshot:
- MU
- published 2026-04-06 20:58 Paris = 14:58 ET
- displayed spot 380.25
- target expiration 2026-04-17 (fully visible column containing displayed King)
- displayed King: strike 420, +3790.3K
- fully legible target-expiry strikes: 352.5..432.5

Method preserved from the 2026-04-28 second-layer diagnostic:
- target magnitude: |HeatSeeker GEX|
- primary static control: prior-close ThetaData EOD gamma * settled OI
- primary subset: ex-King
- seven fixed second-layer candidates
- partial Spearman
- 10,000 deterministic permutations
- Benjamini-Hochberg FDR across the seven candidate tests
- secondary joint control: gamma*OI + total OI

This run does not reconstruct intraday gamma and does not modify H1-H5.

Important status:
The second-layer statistical protocol is frozen from the prior card, but the
expiration-selection rule ("use the fully visible expiry containing the displayed
King") was not preregistered before this screenshot was seen. Therefore this card
is a replication diagnostic, not a new confirmatory gate.
"""

from __future__ import annotations

import json
import math
import random
import statistics
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASE = "http://127.0.0.1:25503/v3"
SYMBOL = "MU"
DATE = "20260406"
EXPIRATION = "20260417"
SPOT = 380.25
START = "09:30:00"
END = "14:58:00"
# 2026-04-03 was a US market holiday; use the last prior trading session.
GAMMA_DATE = "20260402"
KING = 420.0

FLOW_FILE = Path("mu_20260406_20260417_145800_volland_like_frozen_v1.json")
STATIC_FILE = Path("mu_20260406_20260417_static_oi_gamma.json")
IV_FILE = Path("mu_20260406_1453_1458_intraday_iv_raw.json")
OUT_FILE = Path("mu_20260406_second_layer_replication.json")

N_PERM = 10_000
# Keep the same deterministic seed as the already-fixed 2026-04-28 residual test.
SEED = 20260428

TARGET = "abs_heatseeker_gex_k"
PRIMARY_CONTROL = "gamma_oi_total"
SECONDARY_CONTROLS = ["gamma_oi_total", "total_oi"]
CANDIDATES = [
    "raw_contract_volume",
    "trade_count",
    "abs_signed_premium_notional",
    "mean_observed_iv",
    "abs_call_minus_put_iv",
    "mean_dollar_spread",
    "mean_relative_spread",
]

# 2026-04-17 GEX column, K units exactly as displayed.
# Only fully legible rows are used.
HS_GEX_K = {
    432.5: -8.5,
    430.0: 36.6,
    427.5: 20.3,
    425.0: -154.6,
    422.5: -3.8,
    420.0: 3790.3,
    417.5: 6.9,
    415.0: 2735.4,
    412.5: 76.3,
    410.0: -287.1,
    407.5: -2.0,
    405.0: 61.7,
    402.5: -47.6,
    400.0: -258.7,
    397.5: -22.5,
    395.0: 311.0,
    392.5: -20.1,
    390.0: -1235.1,
    387.5: -34.7,
    385.0: -26.3,
    382.5: -84.2,
    380.0: -330.8,
    377.5: 77.5,
    375.0: -42.6,
    372.5: -235.3,
    370.0: -262.8,
    367.5: 21.2,
    365.0: 7.5,
    362.5: 226.6,
    360.0: -61.0,
    357.5: -9.7,
    355.0: 40.9,
    352.5: 9.1,
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


def latest_iv_by_side(payload: object) -> dict[tuple[float, str], dict[str, float]]:
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


def finite_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(float(v))


def rankdata(xs: list[float]) -> list[float]:
    pairs = sorted(enumerate(xs), key=lambda z: z[1])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(pairs):
        j = i + 1
        while j < len(pairs) and pairs[j][1] == pairs[i][1]:
            j += 1
        avg = (i + 1 + j) / 2.0
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


def spearman(x: list[float], y: list[float]) -> float:
    return pearson(rankdata(x), rankdata(y))


def residualize_one(y: list[float], z: list[float]) -> list[float]:
    mz, my = statistics.mean(z), statistics.mean(y)
    den = sum((v - mz) ** 2 for v in z)
    beta = 0.0 if den == 0 else sum((a-mz)*(b-my) for a, b in zip(z, y)) / den
    alpha = my - beta * mz
    return [b - (alpha + beta*a) for a, b in zip(z, y)]


def solve_linear(a: list[list[float]], b: list[float]) -> list[float] | None:
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            return None
        m[col], m[pivot] = m[pivot], m[col]
        div = m[col][col]
        m[col] = [v / div for v in m[col]]
        for r in range(n):
            if r == col:
                continue
            f = m[r][col]
            if f == 0:
                continue
            m[r] = [rv - f*cv for rv, cv in zip(m[r], m[col])]
    return [m[i][-1] for i in range(n)]


def residualize_many(y: list[float], controls: list[list[float]]) -> list[float] | None:
    n = len(y)
    p = 1 + len(controls)
    xrows = [[1.0] + [controls[j][i] for j in range(len(controls))] for i in range(n)]
    xtx = [[0.0]*p for _ in range(p)]
    xty = [0.0]*p
    for row, yy in zip(xrows, y):
        for i in range(p):
            xty[i] += row[i] * yy
            for j in range(p):
                xtx[i][j] += row[i] * row[j]
    beta = solve_linear(xtx, xty)
    if beta is None:
        return None
    return [yy - sum(bb*xx for bb, xx in zip(beta, row)) for row, yy in zip(xrows, y)]


def partial_spearman_one(x: list[float], y: list[float], z: list[float]) -> float:
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    return pearson(residualize_one(rx, rz), residualize_one(ry, rz))


def partial_spearman_many(x: list[float], y: list[float], zs: list[list[float]]) -> float:
    rx, ry = rankdata(x), rankdata(y)
    rzs = [rankdata(z) for z in zs]
    ex = residualize_many(rx, rzs)
    ey = residualize_many(ry, rzs)
    if ex is None or ey is None:
        return float("nan")
    return pearson(ex, ey)


def perm_p_primary(x: list[float], y: list[float], z: list[float], observed: float, rng: random.Random) -> float:
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    ey = residualize_one(ry, rz)
    ge = 0
    for _ in range(N_PERM):
        px = rx[:]
        rng.shuffle(px)
        ex = residualize_one(px, rz)
        rp = pearson(ex, ey)
        if math.isfinite(rp) and abs(rp) >= abs(observed) - 1e-15:
            ge += 1
    return (ge + 1) / (N_PERM + 1)


def bh_qvalues(pairs: list[tuple[str, float]]) -> dict[str, float]:
    m = len(pairs)
    ordered = sorted(pairs, key=lambda z: z[1])
    qtmp = [0.0] * m
    prev = 1.0
    for i in range(m - 1, -1, -1):
        rank = i + 1
        q = min(prev, ordered[i][1] * m / rank, 1.0)
        qtmp[i] = q
        prev = q
    return {ordered[i][0]: qtmp[i] for i in range(m)}


def collect(rows: list[dict[str, Any]], candidate: str, controls: list[str]) -> tuple[list[float], list[float], list[list[float]]]:
    good = []
    needed = [candidate, TARGET] + controls
    for r in rows:
        if all(finite_num(r.get(k)) for k in needed):
            good.append(r)
    x = [float(r[candidate]) for r in good]
    y = [float(r[TARGET]) for r in good]
    zs = [[float(r[c]) for r in good] for c in controls]
    return x, y, zs


def corr(rows: list[dict[str, Any]], xkey: str, ykey: str) -> tuple[int, float]:
    pairs = []
    for r in rows:
        x, y = r.get(xkey), r.get(ykey)
        if finite_num(x) and finite_num(y):
            pairs.append((float(x), float(y)))
    if len(pairs) < 3:
        return len(pairs), float("nan")
    return len(pairs), spearman([a for a, _ in pairs], [b for _, b in pairs])


def sign_agreement(rows: list[dict[str, Any]], xkey: str, ykey: str) -> tuple[int, int, float]:
    good = total = 0
    for r in rows:
        x, y = r.get(xkey), r.get(ykey)
        if not finite_num(x) or not finite_num(y):
            continue
        x = float(x); y = float(y)
        if x == 0 or y == 0:
            continue
        total += 1
        good += int((x > 0) == (y > 0))
    return good, total, (good / total if total else float("nan"))


def evaluate_second_layer(rows: list[dict[str, Any]], label: str) -> dict[str, Any]:
    out: dict[str, Any] = {"label": label, "n_rows": len(rows), "candidates": {}}
    rng = random.Random(SEED + (0 if label == "EX_KING_PRIMARY" else 1000))
    pvals: list[tuple[str, float]] = []

    for c in CANDIDATES:
        x, y, zs = collect(rows, c, [PRIMARY_CONTROL])
        if len(x) < 8:
            out["candidates"][c] = {"n": len(x), "status": "INSUFFICIENT"}
            continue
        raw = spearman(x, y)
        primary = partial_spearman_one(x, y, zs[0])
        p = perm_p_primary(x, y, zs[0], primary, rng)

        x2, y2, zs2 = collect(rows, c, SECONDARY_CONTROLS)
        joint = partial_spearman_many(x2, y2, zs2) if len(x2) >= 8 else float("nan")

        out["candidates"][c] = {
            "n": len(x),
            "raw_spearman": raw,
            "partial_spearman_given_gammaoi": primary,
            "permutation_p_two_sided": p,
            "joint_control_n": len(x2),
            "partial_spearman_given_gammaoi_and_totaloi": joint,
        }
        pvals.append((c, p))

    qs = bh_qvalues(pvals)
    for c, q in qs.items():
        out["candidates"][c]["bh_fdr_q"] = q

    ranked = [
        (c, d) for c, d in out["candidates"].items()
        if "partial_spearman_given_gammaoi" in d
    ]
    ranked.sort(key=lambda z: abs(z[1]["partial_spearman_given_gammaoi"]), reverse=True)
    out["ranking_by_abs_primary_partial_rho"] = [c for c, _ in ranked]
    return out


def print_second_layer(ev: dict[str, Any]) -> None:
    print(f"\n=== {ev['label']} ===")
    print("candidate                       n   raw_rho   partial|gammaOI   perm_p    BH_q    partial|gammaOI+OI")
    for c in ev.get("ranking_by_abs_primary_partial_rho", []):
        d = ev["candidates"][c]
        print(
            f"{c:30s} {d['n']:2d}  {d['raw_spearman']:+.3f}       "
            f"{d['partial_spearman_given_gammaoi']:+.3f}          "
            f"{d['permutation_p_two_sided']:.4f}   {d['bh_fdr_q']:.4f}        "
            f"{d['partial_spearman_given_gammaoi_and_totaloi']:+.3f}"
        )


def main() -> int:
    print("MU 2026-04-06 — FROZEN-PROTOCOL SECOND-LAYER REPLICATION DIAGNOSTIC")
    print(f"Card: 14:58 ET, spot={SPOT}, expiry={EXPIRATION}, displayed King={KING}")
    print(f"Fully legible transcribed strikes: {len(HS_GEX_K)}")
    print("H1-H5 unchanged. No intraday gamma reconstruction.")

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

    run([
        sys.executable, "collect_mu_static_structure.py",
        "--symbol", SYMBOL,
        "--expiration", EXPIRATION,
        "--oi-date", DATE,
        "--gamma-date", GAMMA_DATE,
        "--output", str(STATIC_FILE),
    ])

    iv_payload = get_json("/option/history/greeks/implied_volatility", {
        "symbol": SYMBOL,
        "expiration": EXPIRATION,
        "date": DATE,
        "strike": "*",
        "right": "both",
        "start_time": "14:53:00",
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
            for k in (
                "trade_count", "classified_contracts", "unknown_contracts",
                "signed_contract_flow", "signed_premium_notional",
                "raw_contract_volume", "unknown_fraction",
            ):
                if k in f:
                    r[k] = f[k]
            if "signed_premium_notional" in r:
                r["abs_signed_premium_notional"] = abs(float(r["signed_premium_notional"]))

        if strike in smap:
            s = smap[strike]
            for k in (
                "call_oi", "put_oi", "total_oi", "call_gamma_oi", "put_gamma_oi",
                "gamma_oi_total", "cp_gamma_imbalance",
            ):
                if k in s:
                    r[k] = s[k]

        valid_ivs = []
        rel_spreads = []
        dollar_spreads = []
        for side in ("call", "put"):
            d = ivmap.get((strike, side))
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

        if valid_ivs:
            r["mean_observed_iv"] = statistics.mean(valid_ivs)
        if "call_iv" in r and "put_iv" in r:
            r["call_minus_put_iv"] = r["call_iv"] - r["put_iv"]
            r["abs_call_minus_put_iv"] = abs(r["call_minus_put_iv"])
        if dollar_spreads:
            r["mean_dollar_spread"] = statistics.mean(dollar_spreads)
        if rel_spreads:
            r["mean_relative_spread"] = statistics.mean(rel_spreads)

        rows.append(r)

    ex_king = [r for r in rows if not r["is_king"]]

    core = {}
    for label, rr in (("all", rows), ("ex_king", ex_king)):
        core[label] = {}
        for feature in ("total_oi", "gamma_oi_total", "raw_contract_volume", "trade_count"):
            n, rho = corr(rr, feature, TARGET)
            core[label][feature] = {"n": n, "spearman_vs_abs_gex": rho}
        n, rho = corr(rr, "cp_gamma_imbalance", "heatseeker_gex_k")
        good, total, sign = sign_agreement(rr, "cp_gamma_imbalance", "heatseeker_gex_k")
        core[label]["cp_gamma_direction"] = {
            "n": n, "spearman": rho, "sign_good": good, "sign_n": total, "sign_agreement": sign
        }
        n, rho = corr(rr, "signed_contract_flow", "heatseeker_gex_k")
        good, total, sign = sign_agreement(rr, "signed_contract_flow", "heatseeker_gex_k")
        core[label]["flow_direction"] = {
            "n": n, "spearman": rho, "sign_good": good, "sign_n": total, "sign_agreement": sign
        }

    primary = evaluate_second_layer(ex_king, "EX_KING_PRIMARY")
    secondary = evaluate_second_layer(rows, "ALL_STRIKES_SECONDARY")

    result = {
        "status": "REPLICATION_DIAGNOSTIC_NOT_CONFIRMATORY",
        "symbol": SYMBOL,
        "date": DATE,
        "publication_paris": "2026-04-06 20:58",
        "publication_outer_bound_et": END,
        "spot_displayed": SPOT,
        "expiration": EXPIRATION,
        "heatseeker_source": {
            "metric": "GEX",
            "units_transcribed": "K as displayed",
            "fully_legible_strike_range": [352.5, 432.5],
            "n_transcribed": len(HS_GEX_K),
            "king_strike": KING,
            "king_gex_k": HS_GEX_K[KING],
            "exact_snapshot_time_known": False,
        },
        "data_controls": {
            "flow_method": "volland_like_frozen_v1.py unchanged",
            "flow_window_et": [START, END],
            "oi_date": DATE,
            "prior_close_gamma_date": GAMMA_DATE,
            "intraday_iv_window_et": ["14:53:00", END],
            "intraday_gamma_reconstructed": False,
            "dealer_sign_from_call_put": False,
        },
        "frozen_second_layer_protocol": {
            "target": TARGET,
            "primary_subset": "ex-King",
            "primary_control": PRIMARY_CONTROL,
            "secondary_joint_controls": SECONDARY_CONTROLS,
            "candidates": CANDIDATES,
            "permutations": N_PERM,
            "seed": SEED,
            "multiple_testing": "Benjamini-Hochberg FDR across seven candidate tests",
        },
        "static_core": core,
        "second_layer_primary_ex_king": primary,
        "second_layer_all_strikes_secondary": secondary,
        "rows": rows,
        "limitations": [
            "second-layer statistics are frozen from 2026-04-28",
            "expiration-selection rule was not preregistered before this card; therefore not confirmatory",
            "publication time is an outer bound, not proven HeatSeeker snapshot time",
            "prior-close gamma is observed EOD gamma and can be stale intraday",
            "signed flow is a quote-edge classifier, not observed dealer inventory",
            "call-minus-put gamma*OI is structural contrast only, not dealer positioning",
            "no H1-H5 gate is changed or rescued",
        ],
    }
    OUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("\n=== STATIC CORE REPLICATION ===")
    for label in ("all", "ex_king"):
        c = core[label]
        print(f"\n{label.upper()}")
        for f in ("total_oi", "gamma_oi_total", "raw_contract_volume", "trade_count"):
            x = c[f]
            print(f"{f:24s} n={x['n']:2d} rho(|GEX|)={x['spearman_vs_abs_gex']:+.3f}")
        x = c["cp_gamma_direction"]
        print(f"cp_gamma direction       n={x['n']:2d} rho={x['spearman']:+.3f} sign={x['sign_agreement']:.3f} ({x['sign_good']}/{x['sign_n']})")
        x = c["flow_direction"]
        print(f"frozen flow direction    n={x['n']:2d} rho={x['spearman']:+.3f} sign={x['sign_agreement']:.3f} ({x['sign_good']}/{x['sign_n']})")

    print_second_layer(primary)
    print_second_layer(secondary)

    print("\nINTERPRETATION RULE (UNCHANGED)")
    print("A second-layer candidate needs non-trivial partial rho after gammaOI control AND low BH-FDR q.")
    print("A strong raw rho that collapses after control is shared static/liquidity structure, not an independent layer.")
    print("\nSTATUS: REPLICATION_DIAGNOSTIC_NOT_CONFIRMATORY")
    print("Reason: statistics were frozen, but expiry-selection rule was not preregistered before this screenshot.")
    print(f"saved: {OUT_FILE.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
