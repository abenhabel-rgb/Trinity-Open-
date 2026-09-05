#!/usr/bin/env python3
"""Exploratory AMD 2026-04-27 GEX↔VEX strike-alignment diagnostic.

Important: the screenshots do NOT show overlapping expirations.
GEX uses 2026-05-01; VEX uses later expirations 2026-05-29, 2026-06-05,
and 2026-06-18. Therefore this script tests only whether strike concentration
persists across Greeks/maturities. It does NOT test a same-contract GEX↔VEX mapping.

Three visually obstructed rows are excluded a priori from the clean sample:
355.0, 342.5, 310.0.
"""

import numpy as np
from scipy.stats import spearmanr, rankdata, pearsonr

SEED = 20260427
N_PERM = 10_000

# Values manually transcribed from the supplied HeatSeeker screenshots, in K.
# Clean common strike range 295..375; uncertain/obstructed rows are omitted.
rows = [
    # strike, GEX_2026-05-01, VEX_2026-05-29, VEX_2026-06-05, VEX_2026-06-18
    (375.0,    0.0,       0.0,       0.0,        0.0),
    (372.5, -115.9,       0.0,       0.0,        0.0),
    (370.0,  359.8,   -2363.9,    -378.7,     2212.3),
    (367.5,  -84.4,       0.0,       0.0,        0.0),
    (365.0,  -79.8,    -247.0,     -18.7,        0.0),
    (362.5,  103.8,       0.0,       0.0,        0.0),
    (360.0,  280.7,    -574.5,    -238.2,   -15820.2),
    (357.5, -123.1,       0.0,       0.0,        0.0),
    (352.5,  -14.6,       0.0,       0.0,        0.0),
    (350.0, 2558.2,    -957.9,      42.6,    70477.3),
    (347.5,    0.4,       0.0,       0.0,        0.0),
    (345.0, -475.7,    -352.8,      51.7,        0.0),
    (340.0,  426.7,   -3252.5,      11.8,    -9160.8),
    (337.5,  173.3,       0.0,       0.0,        0.0),
    (335.0,  -72.4,      31.7,     -19.6,        0.0),
    (332.5,  305.0,       0.0,       0.0,        0.0),
    (330.0, -733.9,      37.4,     -20.4,    -1752.4),
    (327.5, -117.5,       0.0,       0.0,        0.0),
    (325.0,-1081.4,    1397.9,      43.1,        0.0),
    (322.5,   54.1,       0.0,       0.0,        0.0),
    (320.0, -901.3,     125.6,      39.7,     3011.4),
    (317.5, -137.3,       0.0,       0.0,        0.0),
    (315.0,   63.1,     699.1,     -13.0,        0.0),
    (312.5,   19.9,       0.0,       0.0,        0.0),
    (307.5, -305.6,       0.0,       0.0,        0.0),
    (305.0,-1294.9,     -22.9,     204.0,        0.0),
    (302.5, -497.0,       0.0,       0.0,        0.0),
    (300.0,  633.7,   -4481.0,     610.3,   -41271.6),
    (297.5, -160.6,       0.0,       0.0,        0.0),
    (295.0, -413.6,     218.7,     111.9,        0.0),
]

a = np.asarray(rows, dtype=float)
strike = a[:, 0]
gex = a[:, 1]
v529 = a[:, 2]
v605 = a[:, 3]
v618 = a[:, 4]

gex_abs = np.abs(gex)
vmax_abs = np.max(np.abs(np.column_stack([v529, v605, v618])), axis=1)


def perm_p(x, y, seed=SEED, n=N_PERM):
    rng = np.random.default_rng(seed)
    obs = spearmanr(x, y).statistic
    exceed = 0
    for _ in range(n):
        yp = rng.permutation(y)
        r = spearmanr(x, yp).statistic
        if abs(r) >= abs(obs) - 1e-15:
            exceed += 1
    return obs, (exceed + 1) / (n + 1)


def partial_spearman_binary_control(x, y, z):
    # Spearman = Pearson on ranks; residualize both rank vectors on intercept + z.
    rx = rankdata(x)
    ry = rankdata(y)
    X = np.column_stack([np.ones(len(z)), z])
    bx = np.linalg.lstsq(X, rx, rcond=None)[0]
    by = np.linalg.lstsq(X, ry, rcond=None)[0]
    ex = rx - X @ bx
    ey = ry - X @ by
    return pearsonr(ex, ey)

rho_all, p_all = perm_p(gex_abs, vmax_abs)

ex_king = strike != 350.0
rho_ex, p_ex = perm_p(gex_abs[ex_king], vmax_abs[ex_king], seed=SEED + 1)

# Control for the strong 5-dollar vs 2.5-dollar strike-grid pattern.
major_grid = np.array([(s % 5.0) == 0.0 for s in strike], dtype=float)
partial_grid_r, partial_grid_p = partial_spearman_binary_control(
    gex_abs, vmax_abs, major_grid
)

# Restrict to strikes where VEX is nonzero in at least one visible VEX maturity.
nonzero = vmax_abs > 0
rho_nonzero, p_nonzero = spearmanr(gex_abs[nonzero], vmax_abs[nonzero])

print("AMD 2026-04-27 — GEX↔VEX STRIKE-ALIGNMENT DIAGNOSTIC")
print("status: DIAGNOSTIC_ONLY")
print("publication: 2026-04-27 17:28 Paris = 11:28 ET")
print("GEX expiry tested: 2026-05-01")
print("VEX expiries summarized by max |VEX|: 2026-05-29, 2026-06-05, 2026-06-18")
print("WARNING: no overlapping GEX/VEX expiration in screenshots")
print(f"clean common strikes: {len(strike)}")
print("excluded as visually obstructed: 355.0, 342.5, 310.0")
print(f"GEX King: strike 350.0, +2558.2K")
print(f"VEX King: strike 350.0, +70477.3K (2026-06-18)")
print(f"|GEX| vs max|VEX| Spearman: {rho_all:+.3f}; perm p={p_all:.5f}")
print(f"ex-GEX-King Spearman: {rho_ex:+.3f}; perm p={p_ex:.5f}")
print(f"partial Spearman controlling 5-dollar grid: {partial_grid_r:+.3f}; approx p={partial_grid_p:.5f}")
print(f"VEX-nonzero-only n={nonzero.sum()} Spearman: {rho_nonzero:+.3f}; p={p_nonzero:.5f}")
print("INTERPRETATION: broad strike concentration aligns, but much of the signal is tied")
print("to coarse strike-grid concentration; among VEX-active strikes alone the association")
print("is not statistically resolved. This does not identify a GEX↔VEX formula.")
