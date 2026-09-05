#!/usr/bin/env python3
"""Evaluate MU 2026-08-19 premarket H3 using observed OI and prior-close gamma.

Primary question: does gamma-weighted OI explain HeatSeeker GEX magnitude better
than raw OI? Secondary exploratory question: does call-minus-put gamma-OI balance
track signed HeatSeeker GEX? The latter is NOT interpreted as dealer positioning.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

DATA = Path("mu_20260819_premarket_oi_gamma_h3.json")
KING = 950.0

HS_GEX = {
    935.0: 552.0, 940.0: -317.1, 942.5: 0.0, 945.0: -298.0,
    950.0: -2170.2, 955.0: 324.9, 960.0: 1559.3, 962.5: 0.0,
    965.0: 635.0, 970.0: 67.5, 975.0: 435.3, 980.0: 1352.2,
    985.0: 116.1, 990.0: -626.2, 995.0: 370.0, 1000.0: 189.2,
    1005.0: 7.1, 1010.0: 48.9, 1015.0: 41.8, 1020.0: -74.2,
}


def mean(xs):
    return sum(xs) / len(xs)


def pearson(xs, ys):
    if len(xs) < 2 or len(ys) < 2 or len(xs) != len(ys):
        return float("nan")
    mx, my = mean(xs), mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return float("nan") if den == 0 else sum(x*y for x,y in zip(dx,dy)) / den


def ranks(v):
    p = sorted(enumerate(v), key=lambda z:z[1])
    out = [0.0] * len(v)
    i = 0
    while i < len(p):
        j = i + 1
        while j < len(p) and p[j][1] == p[i][1]:
            j += 1
        r = (i + 1 + j) / 2.0
        for k in range(i, j):
            out[p[k][0]] = r
        i = j
    return out


def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))


def sign_agreement(xs, ys):
    good = n = 0
    for x, y in zip(xs, ys):
        if x == 0 or y == 0:
            continue
        n += 1
        good += int((x > 0) == (y > 0))
    return (good/n if n else float("nan"), good, n)


def perm_p(xs, ys, obs, n=20000, seed=8192026):
    if len(xs) < 2 or math.isnan(obs):
        return float("nan")
    rng = random.Random(seed)
    y = list(ys)
    e = 1
    for _ in range(n):
        rng.shuffle(y)
        trial = spearman(xs, y)
        if not math.isnan(trial) and abs(trial) >= abs(obs):
            e += 1
    return e / (n + 1)


def report(label, strikes, by):
    if len(strikes) < 2:
        print(f"\n=== {label} | n={len(strikes)} ===")
        print("INSUFFICIENT DATA: fewer than 2 common strikes.")
        return None

    g = [HS_GEX[k] for k in strikes]
    mag = list(map(abs, g))
    oi = [float(by[k]['total_oi']) for k in strikes]
    goi = [float(by[k]['gamma_oi_total']) for k in strikes]
    cp = [float(by[k]['cp_gamma_imbalance']) for k in strikes]

    r_oi = spearman(oi, mag)
    r_goi = spearman(goi, mag)
    lift = r_goi - r_oi
    r_cp = spearman(cp, g)
    sa, good, n = sign_agreement(cp, g)

    print(f"\n=== {label} | n={len(strikes)} ===")
    print("MAGNITUDE TARGET |GEX|")
    print(f"Spearman(total_OI,|GEX|)         {r_oi:+.3f}")
    print(f"Spearman(gammaOI_total,|GEX|)    {r_goi:+.3f}")
    print(f"gamma-weighting lift             {lift:+.3f}")
    print(f"Permutation p(gammaOI magnitude) {perm_p(goi,mag,r_goi):.5f}")
    print("STRUCTURAL CALL-PUT CONTRAST — NOT DEALER POSITION")
    print(f"Spearman(cp_gamma_imbalance,GEX) {r_cp:+.3f}")
    print(f"Sign agreement                   {sa:.3f} ({good}/{n})")
    print(f"Permutation p(cp imbalance)      {perm_p(cp,g,r_cp,seed=8192027):.5f}")
    return r_oi, r_goi, lift, r_cp, sa


def main():
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}. Run collect_mu_20260819_oi_gamma_h3.py first.")

    d = json.loads(DATA.read_text())
    by = {float(r['strike']): r for r in d.get('rows', [])}
    common = [k for k in sorted(HS_GEX) if k in by]
    ex = [k for k in common if k != KING]

    print("MU 2026-08-19 PREMARKET H3 — OI + PRIOR-CLOSE GAMMA")
    print("Target publication 07:25 ET; King GEX strike 950 = -2170.2K.")
    print("No dealer sign is inferred from call/put type.")
    print("Source counts:", d.get("source_counts", {}))

    if len(common) < 2:
        print("\nH3 STATUS: NOT EVALUABLE")
        print("Reason: fewer than 2 HeatSeeker strikes have complete call+put OI/gamma joins.")
        print("This is a collection/join failure, not a failed market hypothesis.")
        raise SystemExit(2)

    report("ALL COMMON STRIKES", common, by)
    result = report("EX-KING 950 PRIMARY", ex, by)
    if result is None:
        print("\nH3 STATUS: NOT EVALUABLE EX-KING")
        raise SystemExit(3)

    a, b, l, c, s = result

    print("\nPREREGISTERED EXPLORATORY GATES")
    print(f"gammaOI magnitude Spearman >= 0.50: {'PASS' if b>=0.50 else 'FAIL'} ({b:+.3f})")
    print(f"gamma-weighting lift vs raw OI >= +0.10: {'PASS' if l>=0.10 else 'FAIL'} ({l:+.3f})")
    print(f"cp imbalance Spearman >= 0.35: {'PASS' if c>=0.35 else 'FAIL'} ({c:+.3f})")
    print(f"cp imbalance sign agreement >= 0.65: {'PASS' if s>=0.65 else 'FAIL'} ({s:.3f})")
    print("\nINTERPRETATION")
    print("Magnitude gates test OI/gamma structure. CP imbalance is a structural contrast only and must not be called dealer positioning.")


if __name__ == '__main__':
    main()
