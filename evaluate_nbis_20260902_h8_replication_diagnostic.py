#!/usr/bin/env python3
"""NBIS 2026-09-02 — H8 cross-ticker static-core replication diagnostic.

The NBIS card was shown before H8 was explicitly frozen, so this run is
DIAGNOSTIC ONLY. It applies the same static-core gates already frozen for MU H7
and now copied unchanged into H8.

Card facts transcribed from screenshot:
- symbol NBIS
- published 2026-09-02 20:57 Paris = 14:57 ET
- spot 204.53
- starred GEX King: strike 200, +750.0K
- deterministic expiry column containing King: 2026-09-18
- largest contiguous fully legible block used: 162.5 .. 252.5

No intraday gamma reconstruction. No dealer sign inference.
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

SYMBOL = "NBIS"
DATE = "20260902"
EXPIRATION = "20260918"
GAMMA_DATE = "20260901"
KING = 200.0
N_PERM = 10_000
SEED = 20260902

STATIC_FILE = Path("nbis_20260902_20260918_static_oi_gamma.json")
OUT_FILE = Path("nbis_20260902_h8_replication_diagnostic.json")

HS_GEX_K = {
    252.5: 0.0,
    250.0: 108.3,
    247.5: 0.0,
    245.0: -7.5,
    242.5: -1.2,
    240.0: -431.3,
    237.5: -7.7,
    235.0: -5.9,
    232.5: -0.4,
    230.0: 279.9,
    227.5: 4.6,
    225.0: -46.4,
    222.5: 2.4,
    220.0: -83.2,
    217.5: -17.1,
    215.0: 64.0,
    212.5: 9.1,
    210.0: -51.8,
    207.5: 1.0,
    205.0: -54.5,
    202.5: 3.6,
    200.0: 750.0,
    197.5: -5.2,
    195.0: 228.9,
    192.5: -2.9,
    190.0: 130.7,
    187.5: 0.0,
    185.0: 177.4,
    182.5: 0.0,
    180.0: 134.8,
    177.5: 0.0,
    175.0: 41.3,
    172.5: 0.0,
    170.0: 268.5,
    167.5: 0.0,
    165.0: -89.3,
    162.5: 0.0,
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

    result = {
        "status": "REPLICATION_DIAGNOSTIC_NOT_CONFIRMATORY",
        "symbol": SYMBOL,
        "date": DATE,
        "publication_paris": "2026-09-02 20:57",
        "publication_et": "14:57",
        "spot": 204.53,
        "expiration": EXPIRATION,
        "king": {"strike": KING, "gex_k": HS_GEX_K[KING]},
        "visible_range": [162.5, 252.5],
        "usable_all": len(rows),
        "usable_ex_king": len(ex),
        "gammaoi_spearman_ex_king": rho,
        "permutation_p_two_sided_10k": p,
        "total_oi_spearman_ex_king": oi_rho,
        "robust_removed": removed,
        "robust_gammaoi_spearman": robust_rho,
        "h8_gates_applied_diagnostically": gates,
        "rows": rows,
        "limitations": [
            "NBIS screenshot was seen before H8 was explicitly frozen",
            "diagnostic only; cannot decide H8 confirmatory status",
            "no proprietary HeatSeeker formula is identified",
            "no dealer-position sign is inferred",
        ],
    }
    OUT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("NBIS 2026-09-02 — H8 CROSS-TICKER STATIC-CORE REPLICATION DIAGNOSTIC")
    print(f"usable all={len(rows)} ex-King={len(ex)}")
    print(f"gammaOI vs |GEX| Spearman: {rho:+.3f}")
    print(f"permutation p (two-sided, 10k): {p:.5f}")
    print(f"total OI vs |GEX| Spearman: {oi_rho:+.3f}")
    if removed:
        print(f"largest remaining |GEX| removed: strike {removed['strike']:.1f}, |GEX|={removed['abs_gex_k']:.1f}K")
    print(f"robust gammaOI vs |GEX| Spearman: {robust_rho:+.3f}")
    print("\nH8 GATES APPLIED DIAGNOSTICALLY")
    for k, v in gates.items():
        print(f"{k}: {'PASS' if v else 'FAIL'}")
    print("STATUS: REPLICATION_DIAGNOSTIC_NOT_CONFIRMATORY")
    print(f"saved: {OUT_FILE.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
