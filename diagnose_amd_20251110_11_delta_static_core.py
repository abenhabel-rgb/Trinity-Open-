#!/usr/bin/env python3
"""AMD 2025-11-10 -> 2025-11-11 HeatSeeker delta diagnostic.

Purpose
-------
Use the two user-provided AMD morning screenshots as a small within-ticker
before/after diagnostic to ask whether changes in prior-close gamma*OI track
changes in HeatSeeker |GEX| better than changes in raw OI.

This is DIAGNOSTIC ONLY:
- only 12 fully legible common strikes are available in the King expiry,
  11 after King exclusion;
- no confirmatory gate is defined;
- no proprietary HeatSeeker formula is identified;
- no intraday gamma is reconstructed;
- no dealer-position sign is inferred.

Card alignment from the screenshots
-----------------------------------
Card A: 2025-11-10 09:30, displayed snapshot 2025-11-07 15:59:57 EST,
        spot 233.42, expiry 2025-11-21, King 260 = -3194.4K.
Card B: 2025-11-11 09:30, displayed snapshot 2025-11-10 15:59:56 EST,
        spot 244.04, expiry 2025-11-21, King 260 = -13469.5K.

ThetaData static inputs are aligned to the displayed snapshot dates:
- 2025-11-07 for Card A
- 2025-11-10 for Card B

Primary descriptive quantities
------------------------------
For ex-King common strikes:
1) cross-sectional Spearman on each date:
   total OI vs |GEX|, gamma*OI vs |GEX|
2) delta Spearman:
   delta total OI vs delta |GEX|
   delta gamma*OI vs delta |GEX|
3) partial rank correlations:
   delta gamma*OI vs delta |GEX| controlling delta OI
   delta OI vs delta |GEX| controlling delta gamma*OI

The sample is small, so all p-values are descriptive only.
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
EXPIRATION = "20251121"
SNAP_A = "20251107"
SNAP_B = "20251110"
KING = 260.0
N_PERM = 10_000
SEED = 20251111

STATIC_A = Path("amd_20251107_20251121_static_oi_gamma.json")
STATIC_B = Path("amd_20251110_20251121_static_oi_gamma.json")
OUT = Path("amd_20251110_11_delta_static_core_diagnostic.json")

# K units exactly as displayed in the 2025-11-21 column.
# Only the fully legible intersection of the two screenshots is used.
GEX_A = {
    262.5: 11.4,
    260.0: -3194.4,
    257.5: -26.0,
    255.0: 94.2,
    252.5: -32.1,
    250.0: 838.3,
    247.5: 54.6,
    245.0: -161.4,
    242.5: -105.7,
    240.0: 233.3,
    237.5: 90.5,
    235.0: -341.2,
}

GEX_B = {
    262.5: 15.0,
    260.0: -13469.5,
    257.5: -4.3,
    255.0: 92.0,
    252.5: -42.2,
    250.0: 939.9,
    247.5: 36.8,
    245.0: -111.0,
    242.5: -66.4,
    240.0: 140.8,
    237.5: 106.6,
    235.0: -240.3,
}


def run(cmd: list[str]) -> None:
    print("\n$ " + " ".join(cmd))
    p = subprocess.run(cmd)
    if p.returncode != 0:
        raise RuntimeError(f"command failed with exit code {p.returncode}: {' '.join(cmd)}")


def finite(v: Any) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(float(v))


def rankdata(xs: list[float]) -> list[float]:
    pairs = sorted(enumerate(xs), key=lambda z: z[1])
    out = [0.0] * len(xs)
    i = 0
    while i < len(pairs):
        j = i + 1
        while j < len(pairs) and pairs[j][1] == pairs[i][1]:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            out[pairs[k][0]] = avg
        i = j
    return out


def pearson(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 3:
        return float("nan")
    mx, my = statistics.mean(x), statistics.mean(y)
    dx = [v - mx for v in x]
    dy = [v - my for v in y]
    den = math.sqrt(sum(v*v for v in dx) * sum(v*v for v in dy))
    if den == 0:
        return float("nan")
    return sum(a*b for a, b in zip(dx, dy)) / den


def spearman(x: list[float], y: list[float]) -> float:
    return pearson(rankdata(x), rankdata(y))


def residualize(y: list[float], z: list[float]) -> list[float]:
    mz, my = statistics.mean(z), statistics.mean(y)
    den = sum((v - mz) ** 2 for v in z)
    beta = 0.0 if den == 0 else sum((a-mz)*(b-my) for a, b in zip(z, y)) / den
    alpha = my - beta*mz
    return [b - (alpha + beta*a) for a, b in zip(z, y)]


def partial_spearman(x: list[float], y: list[float], z: list[float]) -> float:
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    return pearson(residualize(rx, rz), residualize(ry, rz))


def permutation_p(x: list[float], y: list[float], observed: float, seed: int) -> float:
    rng = random.Random(seed)
    rx, ry = rankdata(x), rankdata(y)
    ge = 0
    for _ in range(N_PERM):
        px = rx[:]
        rng.shuffle(px)
        r = pearson(px, ry)
        if math.isfinite(r) and abs(r) >= abs(observed) - 1e-15:
            ge += 1
    return (ge + 1) / (N_PERM + 1)


def partial_perm_p(x: list[float], y: list[float], z: list[float], observed: float, seed: int) -> float:
    rng = random.Random(seed)
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    ey = residualize(ry, rz)
    ge = 0
    for _ in range(N_PERM):
        px = rx[:]
        rng.shuffle(px)
        ex = residualize(px, rz)
        r = pearson(ex, ey)
        if math.isfinite(r) and abs(r) >= abs(observed) - 1e-15:
            ge += 1
    return (ge + 1) / (N_PERM + 1)


def main() -> int:
    print("AMD 2025-11-10 -> 2025-11-11 DELTA STATIC-CORE DIAGNOSTIC")
    print("Common expiry: 2025-11-21; King 260 excluded from primary delta analysis.")
    print("Small-n diagnostic only; no H1-H8 gate is changed.")

    for snap, out in [(SNAP_A, STATIC_A), (SNAP_B, STATIC_B)]:
        run([
            sys.executable, "collect_mu_static_structure.py",
            "--symbol", SYMBOL,
            "--expiration", EXPIRATION,
            "--oi-date", snap,
            "--gamma-date", snap,
            "--output", str(out),
        ])

    a = json.loads(STATIC_A.read_text(encoding="utf-8"))
    b = json.loads(STATIC_B.read_text(encoding="utf-8"))
    amap = {float(r["strike"]): r for r in a.get("rows", [])}
    bmap = {float(r["strike"]): r for r in b.get("rows", [])}

    rows = []
    for strike in sorted(set(GEX_A) & set(GEX_B)):
        sa, sb = amap.get(strike), bmap.get(strike)
        if not sa or not sb:
            continue
        needed = [
            sa.get("total_oi"), sa.get("gamma_oi_total"),
            sb.get("total_oi"), sb.get("gamma_oi_total"),
        ]
        if not all(finite(v) for v in needed):
            continue
        ga, gb = GEX_A[strike], GEX_B[strike]
        row = {
            "strike": strike,
            "is_king": strike == KING,
            "gex_a_k": ga,
            "gex_b_k": gb,
            "abs_gex_a_k": abs(ga),
            "abs_gex_b_k": abs(gb),
            "delta_abs_gex_k": abs(gb) - abs(ga),
            "delta_signed_gex_k": gb - ga,
            "oi_a": float(sa["total_oi"]),
            "oi_b": float(sb["total_oi"]),
            "delta_oi": float(sb["total_oi"]) - float(sa["total_oi"]),
            "gammaoi_a": float(sa["gamma_oi_total"]),
            "gammaoi_b": float(sb["gamma_oi_total"]),
            "delta_gammaoi": float(sb["gamma_oi_total"]) - float(sa["gamma_oi_total"]),
        }
        rows.append(row)

    ex = [r for r in rows if not r["is_king"]]

    def vec(key: str) -> list[float]:
        return [float(r[key]) for r in ex]

    # Cross-sectional static fit on each date.
    oi_a_rho = spearman(vec("oi_a"), vec("abs_gex_a_k"))
    goi_a_rho = spearman(vec("gammaoi_a"), vec("abs_gex_a_k"))
    oi_b_rho = spearman(vec("oi_b"), vec("abs_gex_b_k"))
    goi_b_rho = spearman(vec("gammaoi_b"), vec("abs_gex_b_k"))

    # Within-strike changes.
    d_oi = vec("delta_oi")
    d_goi = vec("delta_gammaoi")
    d_gex = vec("delta_abs_gex_k")
    d_oi_rho = spearman(d_oi, d_gex)
    d_goi_rho = spearman(d_goi, d_gex)
    d_oi_p = permutation_p(d_oi, d_gex, d_oi_rho, SEED + 1)
    d_goi_p = permutation_p(d_goi, d_gex, d_goi_rho, SEED + 2)

    goi_given_oi = partial_spearman(d_goi, d_gex, d_oi)
    oi_given_goi = partial_spearman(d_oi, d_gex, d_goi)
    goi_given_oi_p = partial_perm_p(d_goi, d_gex, d_oi, goi_given_oi, SEED + 3)
    oi_given_goi_p = partial_perm_p(d_oi, d_gex, d_goi, oi_given_goi, SEED + 4)

    result = {
        "status": "DIAGNOSTIC_ONLY_SMALL_N",
        "symbol": SYMBOL,
        "expiration": EXPIRATION,
        "card_a": {
            "date": "2025-11-10",
            "time": "09:30:00",
            "displayed_snapshot": "2025-11-07 15:59:57 EST",
            "spot": 233.42,
            "king": {"strike": 260.0, "gex_k": -3194.4},
        },
        "card_b": {
            "date": "2025-11-11",
            "time": "09:30:00",
            "displayed_snapshot": "2025-11-10 15:59:56 EST",
            "spot": 244.04,
            "king": {"strike": 260.0, "gex_k": -13469.5},
        },
        "usable_common": len(rows),
        "usable_ex_king": len(ex),
        "cross_section": {
            "a_totaloi_vs_absgex": oi_a_rho,
            "a_gammaoi_vs_absgex": goi_a_rho,
            "b_totaloi_vs_absgex": oi_b_rho,
            "b_gammaoi_vs_absgex": goi_b_rho,
        },
        "delta": {
            "delta_oi_vs_delta_absgex": {"rho": d_oi_rho, "perm_p": d_oi_p},
            "delta_gammaoi_vs_delta_absgex": {"rho": d_goi_rho, "perm_p": d_goi_p},
            "partial_delta_gammaoi_given_delta_oi": {"rho": goi_given_oi, "perm_p": goi_given_oi_p},
            "partial_delta_oi_given_delta_gammaoi": {"rho": oi_given_goi, "perm_p": oi_given_goi_p},
        },
        "rows": rows,
        "limitations": [
            "Only 11 ex-King common strikes are fully legible; inferential power is low.",
            "ThetaData static inputs are aligned to displayed snapshot dates, not to an unobserved proprietary HeatSeeker calculation timestamp.",
            "Historical OI is daily settled data; exact vendor timing conventions may differ.",
            "This diagnostic does not identify a proprietary formula and does not alter H1-H8.",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"usable common={len(rows)} ex-King={len(ex)}")
    print("\n=== CROSS-SECTIONAL STATIC FIT ===")
    print(f"Card A totalOI vs |GEX|:  {oi_a_rho:+.3f}")
    print(f"Card A gammaOI vs |GEX|:  {goi_a_rho:+.3f}")
    print(f"Card B totalOI vs |GEX|:  {oi_b_rho:+.3f}")
    print(f"Card B gammaOI vs |GEX|:  {goi_b_rho:+.3f}")

    print("\n=== DELTA DISCRIMINATION: OI vs gammaOI ===")
    print(f"delta OI      vs delta |GEX|: rho={d_oi_rho:+.3f} p={d_oi_p:.4f}")
    print(f"delta gammaOI vs delta |GEX|: rho={d_goi_rho:+.3f} p={d_goi_p:.4f}")
    print(f"partial delta gammaOI | delta OI: rho={goi_given_oi:+.3f} p={goi_given_oi_p:.4f}")
    print(f"partial delta OI | delta gammaOI: rho={oi_given_goi:+.3f} p={oi_given_goi_p:.4f}")

    print("\nINTERPRETATION")
    print("If gammaOI retains materially larger positive delta association after controlling delta OI, gamma weighting is favored.")
    print("If both collapse or OI remains as strong, this pair does not distinguish gamma weighting from raw OI.")
    print("STATUS: DIAGNOSTIC_ONLY_SMALL_N")
    print(f"saved: {OUT.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
