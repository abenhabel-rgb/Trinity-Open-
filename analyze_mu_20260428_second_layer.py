#!/usr/bin/env python3
"""MU 2026-04-28 — second-layer residual diagnostic for HeatSeeker GEX magnitude.

Question
--------
After controlling the strong static structure (prior-close gamma*OI), do directly
observed intraday variables still explain residual |HeatSeeker GEX| across strikes?

Primary analysis
----------------
- EX-KING strikes only (King 500 excluded).
- Target: |HeatSeeker GEX|.
- Primary control: gamma_oi_total (observed prior-close ThetaData gamma * settled OI).
- Candidate second-layer variables are fixed before this run:
    raw_contract_volume, trade_count, abs_signed_premium_notional,
    mean_observed_iv, abs_call_minus_put_iv,
    mean_dollar_spread, mean_relative_spread.
- Statistic: partial Spearman rho(candidate, |GEX| | gamma_oi_total).
- 10,000 deterministic permutation draws per candidate.
- Benjamini-Hochberg FDR q-values across the seven primary candidate tests.

Secondary robustness
--------------------
Jointly control both gamma_oi_total and total_oi using rank-space OLS residuals.
This is descriptive because total OI and gamma*OI are strongly related.

This is EXPLORATORY_ONLY. It does not change H1-H5, does not reconstruct intraday
gamma, and cannot rescue a frozen failure.
"""

from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

INFILE = Path("mu_20260428_gex_observed_exploratory.json")
OUTFILE = Path("mu_20260428_second_layer_residual.json")
KING = 500.0
N_PERM = 10_000
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


def residualize_one(y: list[float], z: list[float]) -> list[float]:
    mz, my = statistics.mean(z), statistics.mean(y)
    den = sum((v - mz) ** 2 for v in z)
    beta = 0.0 if den == 0 else sum((a-mz)*(b-my) for a, b in zip(z, y)) / den
    alpha = my - beta * mz
    return [b - (alpha + beta*a) for a, b in zip(z, y)]


def solve_linear(a: list[list[float]], b: list[float]) -> list[float] | None:
    # Small Gaussian elimination with partial pivoting.
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
    # y ~ intercept + controls, all already rank-transformed.
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


def spearman(x: list[float], y: list[float]) -> float:
    return pearson(rankdata(x), rankdata(y))


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
    # Permute candidate ranks relative to fixed target/control; recompute partial rho.
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


def evaluate_subset(rows: list[dict[str, Any]], label: str) -> dict[str, Any]:
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


def print_eval(ev: dict[str, Any]) -> None:
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
    if not INFILE.exists():
        print(f"ERROR: missing {INFILE}. Run explore_mu_20260428_gex_observed.py first.")
        return 2
    data = json.loads(INFILE.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    if not isinstance(rows, list):
        print("ERROR: rows missing from exploratory input JSON")
        return 3

    ex_king = [r for r in rows if float(r.get("strike", float("nan"))) != KING]
    all_rows = rows

    primary = evaluate_subset(ex_king, "EX_KING_PRIMARY")
    secondary = evaluate_subset(all_rows, "ALL_STRIKES_SECONDARY")

    result = {
        "status": "EXPLORATORY_ONLY",
        "purpose": "test residual second-layer variables after static gamma*OI control",
        "source_file": str(INFILE),
        "target": TARGET,
        "king_excluded_primary": KING,
        "primary_control": PRIMARY_CONTROL,
        "secondary_joint_controls": SECONDARY_CONTROLS,
        "candidates_fixed_before_run": CANDIDATES,
        "permutations": N_PERM,
        "multiple_testing": "Benjamini-Hochberg FDR across seven primary candidate variables",
        "primary_ex_king": primary,
        "secondary_all_strikes": secondary,
        "limitations": [
            "exploratory only; same card was previously inspected for raw correlations",
            "partial correlation does not identify a proprietary HeatSeeker formula",
            "gamma*OI uses observed prior-close EOD gamma and settled OI; it can be stale intraday",
            "spread/liquidity/activity can be consequences of common strike concentration rather than explicit model inputs",
            "no H1-H5 gate is changed or rescued",
        ],
    }
    OUTFILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("MU 2026-04-28 — SECOND-LAYER RESIDUAL DIAGNOSTIC")
    print("Primary target: |HeatSeeker GEX|; primary control: gamma_oi_total; King 500 excluded")
    print("No intraday gamma reconstruction. H1-H5 unchanged.")
    print_eval(primary)
    print_eval(secondary)
    print("\nINTERPRETATION RULE FOR THIS EXPLORATORY RUN")
    print("Look for variables with non-trivial partial rho after gammaOI control AND low BH-FDR q.")
    print("A strong raw rho that collapses after control is treated as shared static/liquidity structure, not a second layer.")
    print("STATUS: EXPLORATORY_ONLY")
    print(f"saved: {OUTFILE.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
