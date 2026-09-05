#!/usr/bin/env python3
"""Confirmatory replication of MU premarket static OI/gamma H3 on 2026-08-28.

Important:
- The H3 structure and thresholds were defined on the earlier 2026-08-19 premarket card.
- This 2026-08-28 card was supplied later, so no thresholds are tuned here.
- Publication 2026-08-28 15:23 Paris = 09:23 ET, before regular-session open.
- Same-day regular-session dealer flow therefore cannot generate this premarket snapshot.
- No dealer sign is inferred from call/put type.

Target: HeatSeeker GEX, expiration 2026-08-28.
Use exactly the same 20-strike grid as the earlier H3 test: 935..1020 including 942.5/962.5.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

DATA = Path("mu_20260828_static_oi_gamma.json")
KING = 950.0

# User-provided HeatSeeker GEX screenshot, published 2026-08-28 15:23 Paris (09:23 ET).
# Expiration column: 2026-08-28. Units: K as displayed.
# Fixed 20-strike grid copied from the prior H3 protocol; no strike selection by result.
HS_GEX = {
    935.0: 222.6,
    940.0: 1269.4,
    942.5: -351.6,
    945.0: 71.5,
    950.0: 1779.1,
    955.0: 670.2,
    960.0: 226.7,
    962.5: 0.0,
    965.0: -86.2,
    970.0: -190.1,
    975.0: 363.7,
    980.0: 59.7,
    985.0: 26.8,
    990.0: 46.7,
    995.0: 97.6,
    1000.0: 1072.0,
    1005.0: 7.2,
    1010.0: 60.4,
    1015.0: -9.3,
    1020.0: -45.4,
}

# Frozen from the earlier H3 exploratory protocol; not tuned on this card.
GATE_MAG_SPEARMAN = 0.50
GATE_MAG_LIFT = 0.10
GATE_CP_SPEARMAN = 0.35
GATE_CP_SIGN = 0.65


def mean(xs):
    return sum(xs) / len(xs)


def pearson(xs, ys):
    mx, my = mean(xs), mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return float("nan") if den == 0 else sum(x*y for x, y in zip(dx, dy)) / den


def ranks(values):
    pairs = sorted(enumerate(values), key=lambda p: p[1])
    out = [0.0] * len(values)
    i = 0
    while i < len(pairs):
        j = i + 1
        while j < len(pairs) and pairs[j][1] == pairs[i][1]:
            j += 1
        r = (i + 1 + j) / 2.0
        for k in range(i, j):
            out[pairs[k][0]] = r
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
    return (good / n if n else float("nan"), good, n)


def perm_p(xs, ys, obs, n=20000, seed=20260828):
    rng = random.Random(seed)
    y = list(ys)
    extreme = 1
    for _ in range(n):
        rng.shuffle(y)
        if abs(spearman(xs, y)) >= abs(obs):
            extreme += 1
    return extreme / (n + 1)


def report(label, strikes, by):
    gex = [HS_GEX[k] for k in strikes]
    mag = [abs(x) for x in gex]
    oi = [float(by[k]["total_oi"]) for k in strikes]
    goi = [float(by[k]["gamma_oi_total"]) for k in strikes]
    cp = [float(by[k]["cp_gamma_imbalance"]) for k in strikes]

    r_oi = spearman(oi, mag)
    r_goi = spearman(goi, mag)
    lift = r_goi - r_oi
    r_cp = spearman(cp, gex)
    sa, good, n = sign_agreement(cp, gex)

    print(f"\n=== {label} | n={len(strikes)} ===")
    print("MAGNITUDE TARGET |GEX|")
    print(f"Spearman(total_OI,|GEX|)          {r_oi:+.3f}")
    print(f"Spearman(gammaOI_total,|GEX|)     {r_goi:+.3f}")
    print(f"gamma-weighting lift              {lift:+.3f}")
    print(f"Permutation p(gammaOI magnitude)  {perm_p(goi, mag, r_goi):.5f}")
    print("STRUCTURAL CALL-PUT CONTRAST — NOT DEALER POSITION")
    print(f"Spearman(cp_gamma_imbalance,GEX)  {r_cp:+.3f}")
    print(f"Sign agreement                    {sa:.3f} ({good}/{n})")
    print(f"Permutation p(cp imbalance)       {perm_p(cp, gex, r_cp, seed=282026):.5f}")
    return r_oi, r_goi, lift, r_cp, sa


def main():
    if not DATA.exists():
        raise SystemExit(f"Missing {DATA}. Run collect_mu_static_structure.py first.")

    d = json.loads(DATA.read_text())
    by = {float(r["strike"]): r for r in d.get("rows", [])}
    common = [k for k in sorted(HS_GEX) if k in by]
    ex = [k for k in common if k != KING]

    print("MU 2026-08-28 PREMARKET H3 CONFIRMATORY REPLICATION")
    print("Publication: 09:23 ET, before regular-session open.")
    print("Target: HeatSeeker GEX expiration 2026-08-28; King strike 950 = +1779.1K.")
    print("Static source: OI dated 2026-08-28 + prior-close gamma 2026-08-27.")
    print("Same 20-strike grid and same four H3 gates as the earlier 2026-08-19 test.")
    print("No dealer sign is inferred from call/put type.")

    if len(common) < 12:
        raise SystemExit(f"NOT EVALUABLE: only {len(common)} common strikes; expected broad overlap.")

    report("ALL COMMON STRIKES", common, by)
    _, r_goi, lift, r_cp, sa = report("EX-KING 950 PRIMARY", ex, by)

    p1 = r_goi >= GATE_MAG_SPEARMAN
    p2 = lift >= GATE_MAG_LIFT
    p3 = r_cp >= GATE_CP_SPEARMAN
    p4 = sa >= GATE_CP_SIGN

    print("\nFROZEN H3 REPLICATION GATES — EX-KING")
    print(f"gammaOI magnitude Spearman >= {GATE_MAG_SPEARMAN:.2f}: {'PASS' if p1 else 'FAIL'} ({r_goi:+.3f})")
    print(f"gamma-weighting lift vs raw OI >= +{GATE_MAG_LIFT:.2f}: {'PASS' if p2 else 'FAIL'} ({lift:+.3f})")
    print(f"cp imbalance Spearman >= {GATE_CP_SPEARMAN:.2f}: {'PASS' if p3 else 'FAIL'} ({r_cp:+.3f})")
    print(f"cp imbalance sign agreement >= {GATE_CP_SIGN:.2f}: {'PASS' if p4 else 'FAIL'} ({sa:.3f})")
    print(f"OVERALL: {'PASS' if all((p1,p2,p3,p4)) else 'FAIL'}")

    print("\nINTERPRETATION RULE")
    print("PASS supports replication of the pre-existing OI/gamma structure hypothesis on a second premarket card.")
    print("FAIL weakens that hypothesis. Either result must be logged; thresholds must not be retuned on this card.")
    print("The call-minus-put contrast is structural only and must not be labeled dealer positioning.")


if __name__ == "__main__":
    main()
