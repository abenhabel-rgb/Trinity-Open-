#!/usr/bin/env python3
"""Diagnostic only: NVDA 2026-04-10 same-snapshot GEX/VEX moneyness transform.

Source: two Skylit HeatSeeker screenshots published 2026-04-10 14:59 Paris
(08:59 ET), spot 184.03 on both panels. We use only the fully legible
common block K=175..200 and expirations 2026-04-10, 2026-04-13, 2026-04-15.

This does NOT identify the proprietary formula or dealer positioning.
"""

import numpy as np
from scipy.stats import spearmanr

SPOT = 184.03
SEED = 20260410
N_PERM = 10_000
STRIKES = np.array([
    200,197.5,195,194,193,192.5,192,191,190,189,188,187.5,187,186,
    185,184,183,182.5,182,181,180,179,178,177.5,177,176,175
], dtype=float)

GEX = {
    "2026-04-10": np.array([-22.6,115.4,1425.6,0,0,860.0,0,0,20292.7,0,0,10096.3,0,0,24814.4,0,0,68835.1,0,0,1168.7,0,0,8946.1,0,0,6655.0]),
    "2026-04-13": np.array([-68.2,6.9,234.5,0,0,-33.8,0,0,3439.6,0,0,-1579.0,0,0,-6271.1,0,0,-2358.7,0,0,-84.7,0,0,-606.3,0,0,262.8]),
    "2026-04-15": np.array([44.5,61.0,96.0,0,0,-100.2,0,0,-391.5,0,0,-211.9,0,0,-231.0,0,0,-590.4,0,0,-536.2,0,0,-50.1,0,0,256.3]),
}
VEX = {
    "2026-04-10": np.array([-272.9,2711.5,32527.2,0,0,18888.3,0,0,374573.0,0,0,121377.0,0,0,89584.3,0,0,-306918.4,0,0,-12724.7,0,0,-127357.4,0,0,-112342.0]),
    "2026-04-13": np.array([-3103.6,301.7,9166.3,0,0,-1131.3,0,0,86351.4,0,0,-23879.5,0,0,-27253.9,0,0,13594.3,0,0,1022.9,0,0,13436.1,0,0,-7042.4]),
    "2026-04-15": np.array([2256.1,2845.5,3783.1,0,0,-3230.5,0,0,-9085.9,0,0,-2864.1,0,0,-923.8,0,0,2960.5,0,0,7055.0,0,0,1023.0,0,0,-7664.5]),
}


def perm_p(x, y, n=N_PERM, seed=SEED):
    obs = spearmanr(x, y).statistic
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n):
        yp = rng.permutation(y)
        r = spearmanr(x, yp).statistic
        if abs(r) >= abs(obs) - 1e-12:
            hits += 1
    return obs, (hits + 1) / (n + 1)


print("NVDA 2026-04-10 — GEX/VEX MONEYNESS DIAGNOSTIC")
print(f"spot={SPOT:.2f}; common visible rows={len(STRIKES)}")
for i, exp in enumerate(GEX):
    g = GEX[exp]
    v = VEX[exp]
    t = g * np.sign(STRIKES - SPOT)
    nz = (g != 0) & (v != 0)

    rho_abs_all = spearmanr(np.abs(g), np.abs(v)).statistic
    rho_signed_all = spearmanr(g, v).statistic
    rho_transform_all = spearmanr(t, v).statistic

    rho_abs_nz = spearmanr(np.abs(g[nz]), np.abs(v[nz])).statistic
    rho_signed_nz = spearmanr(g[nz], v[nz]).statistic
    rho_transform_nz, p_transform = perm_p(t[nz], v[nz], seed=SEED+i)

    signs = np.sign(t[nz]) == np.sign(v[nz])
    ratio = v[nz] / t[nz]
    rho_scale_moneyness = spearmanr(np.abs(STRIKES[nz] - SPOT), ratio).statistic

    print(f"\n{exp}")
    print(f"  nonzero common n={nz.sum()}")
    print(f"  all rows: |GEX|~|VEX| rho={rho_abs_all:+.3f}; GEX~VEX={rho_signed_all:+.3f}; transformed={rho_transform_all:+.3f}")
    print(f"  nonzero:  |GEX|~|VEX| rho={rho_abs_nz:+.3f}; GEX~VEX={rho_signed_nz:+.3f}; transformed={rho_transform_nz:+.3f}; perm p={p_transform:.5f}")
    print(f"  transformed sign agreement={signs.sum()}/{len(signs)}")
    print(f"  rho(|K-spot|, VEX/transformed-GEX)={rho_scale_moneyness:+.3f}")

print("\nSTATUS: DIAGNOSTIC_ONLY")
