#!/usr/bin/env python3
"""AMD 2026-08-04 — static-core diagnostic on HeatSeeker GEX.

Card facts transcribed from user screenshot:
- symbol AMD
- published 2026-08-04 21:31 Paris = 15:31 ET
- displayed spot 526.91
- GEX starred King: strike 550.0, +1184.7K
- deterministic expiry column containing King: 2026-08-05
- largest contiguous fully legible block used: 475.0 .. 565.0

Purpose:
Replicate the already-supported static-core relationship on AMD by comparing
|HeatSeeker GEX| with observed ThetaData total OI and prior-close EOD gamma*OI.
This is diagnostic only. It does not decide H8 or H9 and does not retune any gate.

No intraday gamma reconstruction. No dealer-position sign inference.
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

SYMBOL = "AMD"
DATE = "20260804"
EXPIRATION = "20260805"
GAMMA_DATE = "20260803"
KING = 550.0
N_PERM = 10_000
SEED = 20260804

STATIC_FILE = Path("amd_20260804_20260805_static_oi_gamma.json")
OUT_FILE = Path("amd_20260804_static_core_diagnostic.json")

# 2026-08-05 GEX column, K units exactly as displayed.
HS_GEX_K = {
    565.0: 118.1,
    562.5: -2.0,
    560.0: 29.2,
    557.5: 126.8,
    555.0: 32.0,
    552.5: -60.4,
    550.0: 1184.7,
    547.5: 67.7,
    545.0: 104.1,
    542.5: 1.2,
    540.0: 23.7,
    537.5: 10.6,
    535.0: 13.9,
    532.5: 28.3,
    530.0: 1051.4,
    527.5: 416.8,
    525.0: 966.7,
    522.5: 1.4,
    520.0: 346.9,
    517.5: -250.8,
    515.0: 290.4,
    512.5: 530.0,
    510.0: 504.8,
    507.5: -509.6,
    505.0: 54.0,
    502.5: 1.5,
    500.0: 611.1,
    497.5: 83.7,
    495.0: 69.3,
    492.5: 9.4,
    490.0: -13.6,
    487.5: 4.6,
    485.0: 338.0,
    482.5: 297.2,
    480.0: 390.3,
    477.5: -10.4,
    475.0: 40.7,
}


def run(cmd: list[str]) -> None:
    print("\n$ " + " ".join(cmd))
    p = subprocess.run(cmd)
    if p.returncode != 0:
        raise RuntimeError(f"command failed with exit code {p.returncode}: {' '.join(cmd)}")


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
    mx, my = statistics.mean(xs), statistics.mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    if den == 0:
        return float("nan")
    return sum(x*y for x, y in zip(dx, dy)) / den


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(rankdata(xs), rankdata(ys))


def perm_p(xs: list[float], ys: list[float], observed: float) -> float:
    rng = random.Random(SEED)
    rx, ry = rankdata(xs), rankdata(ys)
    ge = 0
    for _ in range(N_PERM):
        px = rx[:]
        rng.shuffle(px)
        r = pearson(px, ry)
        if math.isfinite(r) and abs(r) >= abs(observed) - 1e-15:
            ge += 1
    return (ge + 1) / (N_PERM + 1)


def finite(v: Any) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(float(v))


def main() -> int:
    run([
        sys.executable, "collect_mu_static_structure.py",
        "--symbol", SYMBOL,
        "--expiration", EXPIRATION,
        "--oi-date", DATE,
        "--gamma-date", GAMMA_DATE,
        "--output", str(STATIC_FILE),
    ])

    static = json.loads(STATIC_FILE.read_text(encoding="utf-8"))
    smap = {float(r["strike"]): r for r in static.get("rows", [])}

    rows = []
    for strike, gex in sorted(HS_GEX_K.items()):
        s = smap.get(strike)
        if not s:
            continue
        gammaoi = s.get("gamma_oi_total")
        totaloi = s.get("total_oi")
        if not finite(gammaoi) or not finite(totaloi):
            continue
        rows.append({
            "strike": strike,
            "gex_k": gex,
            "abs_gex_k": abs(gex),
            "gamma_oi_total": float(gammaoi),
            "total_oi": float(totaloi),
            "is_king": strike == KING,
        })

    ex = [r for r in rows if not r["is_king"]]
    xg = [r["gamma_oi_total"] for r in ex]
    xo = [r["total_oi"] for r in ex]
    y = [r["abs_gex_k"] for r in ex]

    gamma_rho = spearman(xg, y) if len(ex) >= 3 else float("nan")
    oi_rho = spearman(xo, y) if len(ex) >= 3 else float("nan")
    p = perm_p(xg, y, gamma_rho) if len(ex) >= 3 else float("nan")

    robust_rows = ex[:]
    removed = None
    robust_rho = float("nan")
    if robust_rows:
        removed = max(robust_rows, key=lambda r: r["abs_gex_k"])
        robust_rows = [r for r in robust_rows if r is not removed]
        if len(robust_rows) >= 3:
            robust_rho = spearman(
                [r["gamma_oi_total"] for r in robust_rows],
                [r["abs_gex_k"] for r in robust_rows],
            )

    result = {
        "status": "DIAGNOSTIC_ONLY",
        "symbol": SYMBOL,
        "date": DATE,
        "publication_paris": "2026-08-04 21:31",
        "publication_et": "15:31",
        "spot": 526.91,
        "expiration": EXPIRATION,
        "king": {"strike": KING, "gex_k": HS_GEX_K[KING]},
        "visible_range": [475.0, 565.0],
        "usable_all": len(rows),
        "usable_ex_king": len(ex),
        "gammaoi_spearman_ex_king": gamma_rho,
        "total_oi_spearman_ex_king": oi_rho,
        "permutation_p_two_sided_10k": p,
        "robust_removed": removed,
        "robust_gammaoi_spearman": robust_rho,
        "rows": rows,
        "limitations": [
            "diagnostic only; H8 already decided and H9 requires paired 09:30 cards",
            "no proprietary HeatSeeker formula is identified",
            "no dealer-position sign is inferred",
        ],
    }
    OUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("AMD 2026-08-04 — STATIC-CORE DIAGNOSTIC")
    print(f"usable all={len(rows)} ex-King={len(ex)}")
    print(f"gammaOI vs |GEX| Spearman: {gamma_rho:+.3f}")
    print(f"total OI vs |GEX| Spearman: {oi_rho:+.3f}")
    print(f"permutation p gammaOI (two-sided, 10k): {p:.5f}")
    if removed:
        print(f"largest remaining |GEX| removed: strike {removed['strike']:.1f}, |GEX|={removed['abs_gex_k']:.1f}K")
    print(f"robust gammaOI vs |GEX| Spearman: {robust_rho:+.3f}")
    print("STATUS: DIAGNOSTIC_ONLY")
    print(f"saved: {OUT_FILE.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
