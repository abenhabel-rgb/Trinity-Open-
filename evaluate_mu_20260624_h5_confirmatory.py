#!/usr/bin/env python3
"""H5 confirmatory replication on MU card published 2026-06-24 17:04 Paris = 11:04 ET.

Method and gates were frozen before this card was supplied.
Publication time is used as an outer bound; exact HeatSeeker snapshot time is not proven.

Primary question: does same-day signed dealer flow retain directional information on
HeatSeeker GEX after conditioning on the static call-minus-put gamma*OI contrast?

Frozen gates (ex-King):
- sign agreement flow/GEX >= 0.65
- Spearman(flow,GEX) >= 0.35
- partial Spearman(flow,GEX | cp_gamma_imbalance) >= 0.35
- permutation p(partial flow) < 0.05

No dealer sign is inferred from call/put type. The static cp variable is a structural
call-minus-put contrast only.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

FLOW = Path("mu_20260624_20260626_110400_volland_like_frozen_v1.json")
STATIC = Path("mu_20260624_static_oi_gamma.json")
KING = 1000.0

# User-provided HeatSeeker GEX screenshot, published 2026-06-24 17:04 Paris.
# Expiration column: 2026-06-26. Units: K as displayed.
# Contiguous legible grid 955..1055, chosen by screenshot visibility, not outcome.
HS_GEX = {
    955.0: -25.7,
    960.0: 25.0,
    965.0: -32.8,
    970.0: -82.7,
    975.0: 23.6,
    980.0: -47.1,
    985.0: 3.1,
    990.0: -102.4,
    995.0: -6.3,
    1000.0: -2469.1,
    1005.0: 29.0,
    1010.0: 24.6,
    1015.0: 21.1,
    1020.0: 42.6,
    1025.0: 29.0,
    1030.0: -19.4,
    1035.0: 24.8,
    1040.0: -111.9,
    1045.0: 19.2,
    1050.0: 1082.4,
    1055.0: -746.7,
}


def mean(xs):
    return sum(xs) / len(xs)


def pearson(xs, ys):
    mx, my = mean(xs), mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return float("nan") if den == 0 else sum(x*y for x, y in zip(dx, dy)) / den


def ranks(v):
    p = sorted(enumerate(v), key=lambda z: z[1])
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


def partial_spearman(x, y, z):
    rxy = spearman(x, y)
    rxz = spearman(x, z)
    ryz = spearman(y, z)
    den = math.sqrt(max(0.0, (1-rxz*rxz) * (1-ryz*ryz)))
    return float("nan") if den == 0 else (rxy-rxz*ryz) / den


def sign_agreement(xs, ys):
    good = n = 0
    for x, y in zip(xs, ys):
        if x == 0 or y == 0:
            continue
        n += 1
        good += int((x > 0) == (y > 0))
    return (good / n if n else float("nan"), good, n)


def perm_partial_p(flow, gex, cp, observed, n=20000, seed=24062026):
    rng = random.Random(seed)
    f = list(flow)
    extreme = 1
    for _ in range(n):
        rng.shuffle(f)
        v = partial_spearman(f, gex, cp)
        if abs(v) >= abs(observed):
            extreme += 1
    return extreme / (n + 1)


def report(label, strikes, flow_by, static_by):
    f = [float(flow_by[k]["signed_contract_flow"]) for k in strikes]
    g = [HS_GEX[k] for k in strikes]
    cp = [float(static_by[k]["cp_gamma_imbalance"]) for k in strikes]
    oi = [float(static_by[k]["total_oi"]) for k in strikes]
    goi = [float(static_by[k]["gamma_oi_total"]) for k in strikes]

    rf = spearman(f, g)
    rcp = spearman(cp, g)
    pflow = partial_spearman(f, g, cp)
    pcp = partial_spearman(cp, g, f)
    pperm = perm_partial_p(f, g, cp, pflow)
    sa, good, nsign = sign_agreement(f, g)

    print(f"\n=== {label} | n={len(strikes)} ===")
    print("SIGNED TARGET GEX")
    print(f"Spearman(flow,GEX)                  {rf:+.3f}")
    print(f"Spearman(cp_gamma_imbalance,GEX)    {rcp:+.3f}")
    print(f"delta flow-minus-static             {rf-rcp:+.3f}")
    print(f"partial Spearman(flow,GEX | cp)     {pflow:+.3f}")
    print(f"partial Spearman(cp,GEX | flow)     {pcp:+.3f}")
    print(f"permutation p(partial flow)         {pperm:.5f}")
    print(f"sign agreement flow/GEX             {sa:.3f} ({good}/{nsign})")
    print(f"sign agreement cp/GEX               {sign_agreement(cp,g)[0]:.3f}")
    print("MAGNITUDE DIAGNOSTIC — NOT A GATE")
    print(f"Spearman(total_OI,|GEX|)            {spearman(oi,list(map(abs,g))):+.3f}")
    print(f"Spearman(gammaOI_total,|GEX|)       {spearman(goi,list(map(abs,g))):+.3f}")
    return rf, pflow, pperm, sa


def main():
    if not FLOW.exists():
        raise SystemExit(f"Missing {FLOW}. Run volland_like_frozen_v1.py first.")
    if not STATIC.exists():
        raise SystemExit(f"Missing {STATIC}. Run collect_mu_static_structure.py first.")

    flow = json.loads(FLOW.read_text())
    static = json.loads(STATIC.read_text())
    fb = {float(r["strike"]): r for r in flow["rows"]}
    sb = {float(r["strike"]): r for r in static["rows"]}

    common = [k for k in sorted(HS_GEX) if k in fb and k in sb]
    if len(common) < 12:
        raise SystemExit(f"NOT EVALUABLE: only {len(common)} common strikes")
    ex = [k for k in common if k != KING]

    print("MU 2026-06-24 H5 — CONFIRMATORY FLOW INCREMENTAL TO STATIC OI/GAMMA")
    print("Card publication: 17:04 Paris = 11:04 ET; publication time is an outer bound.")
    print("Expiration: 2026-06-26. GEX King on tested grid: strike 1000 = -2469.1K.")
    print("Method and gates were frozen before this card was supplied.")
    print("Static cp variable is structural call-minus-put gamma*OI, NOT dealer positioning.")

    report("ALL COMMON STRIKES", common, fb, sb)
    rf, pf, pp, sa = report("EX-KING 1000 PRIMARY", ex, fb, sb)

    gates = {
        "sign": sa >= 0.65,
        "spearman": rf >= 0.35,
        "partial": pf >= 0.35,
        "p": pp < 0.05,
    }
    print("\n=== FROZEN H5 GATE DECISION — EX-KING ===")
    print(f"sign agreement >= 0.65:                 {'PASS' if gates['sign'] else 'FAIL'} ({sa:.3f})")
    print(f"Spearman(flow,GEX) >= 0.35:              {'PASS' if gates['spearman'] else 'FAIL'} ({rf:+.3f})")
    print(f"partial Spearman(flow,GEX | cp) >= 0.35: {'PASS' if gates['partial'] else 'FAIL'} ({pf:+.3f})")
    print(f"permutation p(partial flow) < 0.05:      {'PASS' if gates['p'] else 'FAIL'} ({pp:.5f})")
    print(f"OVERALL: {'PASS' if all(gates.values()) else 'FAIL'}")

    print("\nINTERPRETATION RULE")
    print("PASS supports replication of an incremental same-day signed-flow component beyond the static OI/gamma contrast.")
    print("FAIL weakens that incremental-flow hypothesis. Neither outcome identifies the proprietary HeatSeeker formula.")
    print("Because exact snapshot time is unproven, publication-bounded results must be labeled as such.")


if __name__ == "__main__":
    main()
