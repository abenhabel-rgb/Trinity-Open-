#!/usr/bin/env python3
"""MU 2026-03-18 — H6 premium second-layer confirmatory test.

This script implements the already-frozen protocol in
`docs/MU_H6_PREMIUM_SECOND_LAYER_FROZEN.md` on the next eligible unseen MU card.

Card facts transcribed from the user-provided screenshot:
- symbol: MU
- published: 2026-03-18 18:16 Paris = 13:16 ET
  (France still CET; US already EDT, so 5-hour difference)
- displayed spot: 464.82
- starred GEX King: strike 500, +3103.2K
- deterministic expiration rule => use 2026-03-20, the column containing that King
- largest contiguous fully legible block in that column: 392.5 .. 522.5

Primary H6 target and candidate:
- target: |HeatSeeker GEX|
- candidate: abs_signed_premium_notional from unchanged volland_like_frozen_v1.py
- primary control: prior-close ThetaData EOD gamma * settled OI (`gamma_oi_total`)
- robustness controls: gamma_oi_total + total_oi
- primary subset: ex-King
- 10,000 two-sided deterministic permutations

No intraday gamma is reconstructed. No dealer sign is inferred from call/put type.
H1-H5 are unchanged. This script does not retune H6.
"""

from __future__ import annotations

import json
import math
import random
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

SYMBOL = "MU"
DATE = "20260318"
EXPIRATION = "20260320"
SPOT = 464.82
START = "09:30:00"
END = "13:16:00"
GAMMA_DATE = "20260317"
KING = 500.0
N_PERM = 10_000
SEED = 20260318

FLOW_FILE = Path("mu_20260318_20260320_131600_volland_like_frozen_v1.json")
STATIC_FILE = Path("mu_20260318_20260320_static_oi_gamma.json")
OUT_FILE = Path("mu_20260318_h6_confirmatory.json")

# 2026-03-20 HeatSeeker GEX column, K units exactly as displayed.
# Largest contiguous block judged fully legible in the screenshot.
HS_GEX_K = {
    522.5: -3.2,
    520.0: -111.4,
    517.5: -57.2,
    515.0: -32.6,
    512.5: -33.3,
    510.0: 133.5,
    507.5: 12.0,
    505.0: 38.7,
    502.5: 217.8,
    500.0: 3103.2,
    497.5: -115.4,
    495.0: 72.0,
    492.5: -8.0,
    490.0: 163.7,
    487.5: -4.1,
    485.0: 664.1,
    482.5: 413.0,
    480.0: 263.0,
    477.5: 19.7,
    475.0: -476.7,
    472.5: 40.0,
    470.0: 563.9,
    467.5: 187.7,
    465.0: 427.3,
    462.5: 134.1,
    460.0: 1152.5,
    457.5: 609.5,
    455.0: 166.9,
    452.5: -93.5,
    450.0: 461.4,
    447.5: 149.5,
    445.0: -352.8,
    442.5: -825.2,
    440.0: -369.6,
    437.5: 106.1,
    435.0: -30.5,
    432.5: 134.7,
    430.0: 1929.5,
    427.5: 69.0,
    425.0: -961.7,
    422.5: 41.7,
    420.0: 201.7,
    417.5: 135.5,
    415.0: 56.1,
    412.5: 711.5,
    410.0: 921.2,
    407.5: 1.5,
    405.0: 220.4,
    402.5: 540.9,
    400.0: 709.3,
    397.5: 97.9,
    395.0: -92.1,
    392.5: 1.9,
}


def run(cmd: list[str]) -> None:
    print("\n$ " + " ".join(cmd))
    p = subprocess.run(cmd)
    if p.returncode != 0:
        raise RuntimeError(f"command failed with exit code {p.returncode}: {' '.join(cmd)}")


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


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(rankdata(xs), rankdata(ys))


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
    xtx = [[0.0] * p for _ in range(p)]
    xty = [0.0] * p
    for row, yy in zip(xrows, y):
        for i in range(p):
            xty[i] += row[i] * yy
            for j in range(p):
                xtx[i][j] += row[i] * row[j]
    beta = solve_linear(xtx, xty)
    if beta is None:
        return None
    return [yy - sum(bb*xx for bb, xx in zip(beta, row)) for row, yy in zip(xrows, y)]


def partial_one(x: list[float], y: list[float], z: list[float]) -> float:
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    return pearson(residualize_one(rx, rz), residualize_one(ry, rz))


def partial_many(x: list[float], y: list[float], zs: list[list[float]]) -> float:
    rx, ry = rankdata(x), rankdata(y)
    rzs = [rankdata(z) for z in zs]
    ex = residualize_many(rx, rzs)
    ey = residualize_many(ry, rzs)
    if ex is None or ey is None:
        return float("nan")
    return pearson(ex, ey)


def permutation_p(x: list[float], y: list[float], z: list[float], observed: float) -> float:
    rng = random.Random(SEED)
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


def main() -> int:
    print("MU 2026-03-18 — H6 CONFIRMATORY TEST")
    print("Frozen protocol: docs/MU_H6_PREMIUM_SECOND_LAYER_FROZEN.md")
    print(f"publication outer bound={END} ET spot={SPOT} expiration={EXPIRATION} King={KING}")
    print(f"transcribed fully-legible strikes={len(HS_GEX_K)}")

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

    flow = json.loads(FLOW_FILE.read_text(encoding="utf-8"))
    static = json.loads(STATIC_FILE.read_text(encoding="utf-8"))
    fmap = {float(r["strike"]): r for r in flow.get("rows", [])}
    smap = {float(r["strike"]): r for r in static.get("rows", [])}

    rows: list[dict[str, float]] = []
    for strike, gex in sorted(HS_GEX_K.items()):
        f = fmap.get(strike)
        s = smap.get(strike)
        if not f or not s:
            continue
        premium = f.get("signed_premium_notional")
        gammaoi = s.get("gamma_oi_total")
        oi = s.get("total_oi")
        if not all(finite_num(v) for v in (premium, gammaoi, oi)):
            continue
        rows.append({
            "strike": strike,
            "abs_gex": abs(float(gex)),
            "abs_signed_premium": abs(float(premium)),
            "gamma_oi_total": float(gammaoi),
            "total_oi": float(oi),
            "raw_contract_volume": float(f.get("raw_contract_volume", 0.0)),
            "trade_count": float(f.get("trade_count", 0.0)),
            "is_king": 1.0 if strike == KING else 0.0,
        })

    ex = [r for r in rows if r["strike"] != KING]
    x = [r["abs_signed_premium"] for r in ex]
    y = [r["abs_gex"] for r in ex]
    z = [r["gamma_oi_total"] for r in ex]
    oi = [r["total_oi"] for r in ex]

    if len(ex) < 3:
        print("NOT EVALUABLE: fewer than 3 usable ex-King rows")
        return 2

    raw = spearman(x, y)
    part = partial_one(x, y, z)
    pval = permutation_p(x, y, z, part)
    joint = partial_many(x, y, [z, oi])

    static_oi_rho = spearman(oi, y)
    static_gammaoi_rho = spearman(z, y)
    vol_rho = spearman([r["raw_contract_volume"] for r in ex], y)
    trades_rho = spearman([r["trade_count"] for r in ex], y)

    gates = {
        "n_ge_20": len(ex) >= 20,
        "raw_spearman_gt_0": raw > 0,
        "partial_gammaoi_ge_0_35": part >= 0.35,
        "permutation_p_lt_0_05": pval < 0.05,
        "joint_partial_ge_0_35": joint >= 0.35,
    }
    passed = all(gates.values())

    result = {
        "status": "PASS" if passed else "FAIL",
        "protocol": "MU_H6_PREMIUM_SECOND_LAYER_FROZEN",
        "symbol": SYMBOL,
        "date": DATE,
        "publication_paris": "2026-03-18 18:16",
        "publication_outer_bound_et": END,
        "spot": SPOT,
        "expiration": EXPIRATION,
        "king": KING,
        "transcribed_strike_range": [392.5, 522.5],
        "transcribed_count": len(HS_GEX_K),
        "usable_ex_king_n": len(ex),
        "primary": {
            "raw_spearman_abs_premium_vs_abs_gex": raw,
            "partial_spearman_given_gammaoi": part,
            "permutation_p_two_sided_10000": pval,
            "partial_spearman_given_gammaoi_and_totaloi": joint,
        },
        "frozen_gates": gates,
        "secondary_diagnostics": {
            "spearman_total_oi_vs_abs_gex": static_oi_rho,
            "spearman_gammaoi_vs_abs_gex": static_gammaoi_rho,
            "spearman_raw_volume_vs_abs_gex": vol_rho,
            "spearman_trade_count_vs_abs_gex": trades_rho,
        },
        "flow_summary": flow.get("summary", {}),
        "static_source_counts": static.get("source_counts", {}),
        "limitations": [
            "publication time is an outer bound, not a proven HeatSeeker snapshot time",
            "abs_signed_premium_notional is from frozen quote-edge classification, not observed dealer inventory",
            "gamma_oi_total uses observed prior-close EOD gamma and settled OI",
            "PASS would support a second layer on this card only; it would not identify HeatSeeker's proprietary formula",
            "H1-H5 are unchanged",
        ],
    }
    OUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("\n=== H6 PRIMARY EX-KING ===")
    print(f"n usable ex-King: {len(ex)}")
    print(f"raw Spearman(abs signed premium, |GEX|): {raw:+.3f}")
    print(f"partial Spearman | gammaOI:              {part:+.3f}")
    print(f"permutation p (two-sided, 10k):          {pval:.5f}")
    print(f"partial Spearman | gammaOI + totalOI:    {joint:+.3f}")

    print("\n=== SECONDARY STATIC CORE ===")
    print(f"total OI vs |GEX|:       {static_oi_rho:+.3f}")
    print(f"gammaOI total vs |GEX|:  {static_gammaoi_rho:+.3f}")
    print(f"raw volume vs |GEX|:     {vol_rho:+.3f}")
    print(f"trade count vs |GEX|:    {trades_rho:+.3f}")

    print("\n=== FROZEN H6 GATES ===")
    print(f"1 n>=20:                         {'PASS' if gates['n_ge_20'] else 'FAIL'} ({len(ex)})")
    print(f"2 raw rho > 0:                   {'PASS' if gates['raw_spearman_gt_0'] else 'FAIL'} ({raw:+.3f})")
    print(f"3 partial|gammaOI >= +0.35:      {'PASS' if gates['partial_gammaoi_ge_0_35'] else 'FAIL'} ({part:+.3f})")
    print(f"4 permutation p < 0.05:          {'PASS' if gates['permutation_p_lt_0_05'] else 'FAIL'} ({pval:.5f})")
    print(f"5 partial|gammaOI+OI >= +0.35:   {'PASS' if gates['joint_partial_ge_0_35'] else 'FAIL'} ({joint:+.3f})")
    print(f"OVERALL H6: {'PASS' if passed else 'FAIL'}")
    print(f"saved: {OUT_FILE.resolve()}")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
