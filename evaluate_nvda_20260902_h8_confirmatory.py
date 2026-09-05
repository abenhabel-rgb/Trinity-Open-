#!/usr/bin/env python3
"""NVDA 2026-09-02 — H8 cross-ticker static-core CONFIRMATORY test.

This script implements the already-frozen protocol in
`docs/H8_CROSS_TICKER_STATIC_CORE_FROZEN.md` on the next eligible unseen
non-MU single-name card.

Card facts transcribed from the user-provided screenshot used for H8:
- symbol: NVDA
- published: 2026-09-02 17:56 Paris = 11:56 ET
- displayed spot: 227.29
- starred GEX King: strike 235.0, -27,669.3K
- deterministic expiry rule => use 2026-09-04, the column containing the King
- largest contiguous fully legible block used: 213.0 .. 270.0

A second screenshot supplied in the same user message shows a different spot
(217.94) and a different starred King/expiry. It is therefore not merged with
this card and contributes no H8 values.

Primary H8 test:
- target: |HeatSeeker GEX|
- predictor: prior-close ThetaData EOD gamma * settled OI (`gamma_oi_total`)
- primary subset: ex-King
- 10,000 two-sided deterministic permutations
- robustness: remove the single largest remaining |GEX| node after King exclusion

No intraday gamma reconstruction. No dealer-position sign inference. H1-H7 unchanged.
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

SYMBOL = "NVDA"
DATE = "20260902"
EXPIRATION = "20260904"
GAMMA_DATE = "20260901"
KING = 235.0
N_PERM = 10_000
SEED = 20260902

STATIC_FILE = Path("nvda_20260902_20260904_static_oi_gamma.json")
OUT_FILE = Path("nvda_20260902_h8_confirmatory.json")

# HeatSeeker GEX, K units exactly as displayed in the fully legible
# 2026-09-04 column of the selected screenshot.
HS_GEX_K = {
    270.0: -3.2,
    265.0: -0.1,
    262.5: -1.2,
    260.0: -13.6,
    257.5: -28.9,
    255.0: -9.2,
    252.5: -33.9,
    250.0: 283.3,
    247.5: 76.9,
    245.0: -1911.6,
    242.5: 2388.9,
    240.0: 20314.3,
    237.5: 13369.3,
    235.0: -27669.3,
    232.5: 20451.3,
    230.0: 21288.1,
    228.0: 0.0,
    227.5: -11841.1,
    227.0: 0.0,
    226.0: 0.0,
    225.0: 8711.2,
    224.0: 0.0,
    223.0: 0.0,
    222.5: 12512.5,
    222.0: 0.0,
    221.0: 0.0,
    220.0: 12828.2,
    219.0: 0.0,
    218.0: 0.0,
    217.5: 753.2,
    217.0: 0.0,
    216.0: 0.0,
    215.0: 3425.5,
    214.0: 0.0,
    213.0: 0.0,
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
    print("NVDA 2026-09-02 — H8 CROSS-TICKER STATIC-CORE CONFIRMATORY TEST")
    print("Frozen H8 protocol; no retuning; second inconsistent screenshot excluded.")

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
    x = [r["gamma_oi_total"] for r in ex]
    y = [r["abs_gex_k"] for r in ex]
    oi = [r["total_oi"] for r in ex]

    rho = spearman(x, y) if len(ex) >= 3 else float("nan")
    p = perm_p(x, y, rho) if len(ex) >= 3 else float("nan")
    oi_rho = spearman(oi, y) if len(ex) >= 3 else float("nan")

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

    gates = {
        "n_ge_20": len(ex) >= 20,
        "rho_ge_060": finite(rho) and rho >= 0.60,
        "perm_p_lt_005": finite(p) and p < 0.05,
        "robust_rho_ge_050": finite(robust_rho) and robust_rho >= 0.50,
    }
    overall = all(gates.values())

    result = {
        "status": "H8_CONFIRMATORY_PASS" if overall else "H8_CONFIRMATORY_FAIL",
        "protocol": "docs/H8_CROSS_TICKER_STATIC_CORE_FROZEN.md",
        "symbol": SYMBOL,
        "date": DATE,
        "publication_paris": "2026-09-02 17:56",
        "publication_et": "11:56",
        "spot": 227.29,
        "expiration": EXPIRATION,
        "gamma_date": GAMMA_DATE,
        "king": {"strike": KING, "gex_k": HS_GEX_K[KING]},
        "visible_range": [213.0, 270.0],
        "transcribed_strikes": len(HS_GEX_K),
        "usable_all": len(rows),
        "usable_ex_king": len(ex),
        "gammaoi_spearman_ex_king": rho,
        "permutation_p_two_sided_10k": p,
        "total_oi_spearman_ex_king": oi_rho,
        "robust_removed": removed,
        "robust_gammaoi_spearman": robust_rho,
        "frozen_h8_gates": gates,
        "overall_h8_pass": overall,
        "rows": rows,
        "source_control": {
            "selected_screenshot_spot": 227.29,
            "excluded_second_screenshot_spot": 217.94,
            "reason_second_screenshot_excluded": "different spot and different starred King/expiration; not merged",
        },
        "limitations": [
            "publication time is metadata supplied by user; exact HeatSeeker snapshot timestamp may differ",
            "H8 tests association of static gamma*OI with |GEX|, not the proprietary formula",
            "total OI remains a secondary baseline",
            "no dealer-position sign is inferred",
            "no intraday gamma is reconstructed",
        ],
    }
    OUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("\n=== H8 PRIMARY EX-KING ===")
    print(f"usable all={len(rows)} ex-King={len(ex)}")
    print(f"gammaOI vs |GEX| Spearman: {rho:+.3f}")
    print(f"permutation p (two-sided, 10k): {p:.5f}")
    print(f"total OI vs |GEX| Spearman: {oi_rho:+.3f}")
    if removed:
        print(f"largest remaining |GEX| removed: strike {removed['strike']:.1f}, |GEX|={removed['abs_gex_k']:.1f}K")
    print(f"robust gammaOI vs |GEX| Spearman: {robust_rho:+.3f}")

    print("\n=== FROZEN H8 GATES ===")
    for k, v in gates.items():
        print(f"{k}: {'PASS' if v else 'FAIL'}")
    print(f"OVERALL H8: {'PASS' if overall else 'FAIL'}")
    print(f"saved: {OUT_FILE.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
