#!/usr/bin/env python3
"""Confirmatory evaluation for the second independent MU HeatSeeker card.

Card supplied after MU_FLOW_H1_FROZEN_V1 was frozen.
Publication: 2026-09-03 23:23 Paris = 17:23 ET.
No internal HeatSeeker snapshot time is visible, so publication time is used only
as the pre-registered outer bound. Primary target is GEX for expiration 2026-09-04.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

FLOW_FILE = Path("mu_20260903_20260904_172300_volland_like_frozen_v1.json")
KING = 1000.0

HS_GEX = {
    955.0:-763.4, 960.0:606.6, 965.0:-753.2, 970.0:-1973.4,
    975.0:-251.5, 980.0:-1416.1, 985.0:358.8, 990.0:-596.3,
    995.0:-1878.8, 1000.0:8879.6, 1005.0:129.2, 1010.0:75.9,
    1015.0:-13.4, 1020.0:189.1, 1025.0:19.9, 1030.0:-72.3,
    1035.0:9.7, 1040.0:9.4, 1045.0:-0.4, 1050.0:233.6,
}

# Secondary diagnostic only.
HS_VEX = {
    955.0:3807.2, 960.0:1675.0, 965.0:-7744.3, 970.0:-36835.9,
    975.0:-6621.7, 980.0:-48681.6, 985.0:14787.3, 990.0:-28729.0,
    995.0:-103786.6, 1000.0:549802.9, 1005.0:8774.6, 1010.0:5403.0,
    1015.0:-1094.9, 1020.0:16046.7, 1025.0:1804.2, 1030.0:-6835.7,
    1035.0:956.2, 1040.0:1031.0, 1045.0:-68.2, 1050.0:25881.0,
}

GATES = {
    "sign_agreement": 0.65,
    "spearman_flow_gex": 0.35,
    "directional_lift_vs_volume": 0.20,
}


def mean(xs):
    return sum(xs) / len(xs)


def pearson(xs, ys):
    mx, my = mean(xs), mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return float("nan") if den == 0 else sum(x*y for x,y in zip(dx,dy)) / den


def ranks(values):
    pairs = sorted(enumerate(values), key=lambda p: p[1])
    out = [0.0] * len(values)
    i = 0
    while i < len(pairs):
        j = i + 1
        while j < len(pairs) and pairs[j][1] == pairs[i][1]:
            j += 1
        rank = (i + 1 + j) / 2.0
        for k in range(i,j):
            out[pairs[k][0]] = rank
        i = j
    return out


def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))


def sign_agreement(xs, ys):
    pairs = [(x,y) for x,y in zip(xs,ys) if x != 0 and y != 0]
    return sum((x > 0) == (y > 0) for x,y in pairs) / len(pairs)


def binom_two_sided(k, n):
    # Exact two-sided binomial test under p=0.5 using probability ordering.
    probs = [math.comb(n,i) / (2**n) for i in range(n+1)]
    pk = probs[k]
    return min(1.0, sum(p for p in probs if p <= pk + 1e-15))


def permutation_pvalue(xs, ys, observed, n_perm=100000, seed=20260903):
    rng = random.Random(seed)
    perm = list(ys)
    extreme = 0
    for _ in range(n_perm):
        rng.shuffle(perm)
        r = spearman(xs, perm)
        if abs(r) >= abs(observed) - 1e-15:
            extreme += 1
    return (extreme + 1) / (n_perm + 1)


def report(label, strikes, by_strike, target):
    flow = [float(by_strike[k]["signed_contract_flow"]) for k in strikes]
    volume = [float(by_strike[k]["raw_contract_volume"]) for k in strikes]
    y = [float(target[k]) for k in strikes]

    rho_flow = spearman(flow, y)
    rho_volume = spearman(volume, y)
    lift = rho_flow - rho_volume
    agree = sign_agreement(flow, y)
    pear = pearson(flow, y)

    nonzero = [(f,t) for f,t in zip(flow,y) if f != 0 and t != 0]
    k = sum((f > 0) == (t > 0) for f,t in nonzero)
    n = len(nonzero)
    p_sign = binom_two_sided(k,n)
    p_rho = permutation_pvalue(flow,y,rho_flow)

    print(f"\n=== {label} | n={len(strikes)} ===")
    print(f"Pearson(flow,GEX)          {pear:+.3f}")
    print(f"Spearman(flow,GEX)         {rho_flow:+.3f}")
    print(f"Sign agreement             {agree:.3f} ({k}/{n}), exact p={p_sign:.5f}")
    print(f"Spearman(volume,GEX)       {rho_volume:+.3f}")
    print(f"Directional lift           {lift:+.3f}")
    print(f"Permutation p(Spearman)    {p_rho:.5f}")

    return {
        "rho_flow": rho_flow,
        "rho_volume": rho_volume,
        "lift": lift,
        "sign": agree,
        "p_sign": p_sign,
        "p_rho": p_rho,
    }


def main():
    if not FLOW_FILE.exists():
        raise SystemExit(f"Missing {FLOW_FILE}. Run volland_like_frozen_v1.py for 2026-09-03 first.")

    data = json.loads(FLOW_FILE.read_text())
    print("OPENCLAW MU SECOND-CARD CONFIRMATORY TEST")
    print("method:", data.get("method"))
    print("window_et:", data.get("window_et"))
    print("summary:", json.dumps(data.get("summary",{}), indent=2))
    print("publication note: 23:23 Paris = 17:23 ET; no internal snapshot time visible")

    by_strike = {float(r["strike"]): r for r in data["rows"]}
    common = [k for k in sorted(HS_GEX) if k in by_strike]
    ex_king = [k for k in common if k != KING]

    print(f"\ncommon strikes={len(common)}; ex-King={len(ex_king)}; King={KING:.1f}")
    print("strike   flow    volume    HS_GEX")
    for k in common:
        print(f"{k:6.1f} {by_strike[k]['signed_contract_flow']:7d} {by_strike[k]['raw_contract_volume']:9d} {HS_GEX[k]:9.1f}")

    all_res = report("ALL COMMON STRIKES", common, by_strike, HS_GEX)
    ex_res = report("EX-KING 1000 PRIMARY", ex_king, by_strike, HS_GEX)

    print("\n=== FROZEN GATE DECISION (EX-KING) ===")
    gate1 = ex_res["sign"] >= GATES["sign_agreement"]
    gate2 = ex_res["rho_flow"] >= GATES["spearman_flow_gex"]
    gate3 = ex_res["lift"] >= GATES["directional_lift_vs_volume"]
    print(f"sign agreement >= {GATES['sign_agreement']:.2f}: {'PASS' if gate1 else 'FAIL'} ({ex_res['sign']:.3f})")
    print(f"Spearman(flow,GEX) >= {GATES['spearman_flow_gex']:.2f}: {'PASS' if gate2 else 'FAIL'} ({ex_res['rho_flow']:+.3f})")
    print(f"directional lift >= {GATES['directional_lift_vs_volume']:+.2f}: {'PASS' if gate3 else 'FAIL'} ({ex_res['lift']:+.3f})")
    print("OVERALL:", "PASS" if (gate1 and gate2 and gate3) else "FAIL")

    # Secondary VEX diagnostic, not part of the gate.
    flow_ex = [float(by_strike[k]["signed_contract_flow"]) for k in ex_king]
    vex_ex = [HS_VEX[k] for k in ex_king]
    print("\nSECONDARY VEX DIAGNOSTIC (NOT A GATE)")
    print(f"Spearman(flow,VEX) ex-King = {spearman(flow_ex,vex_ex):+.3f}")
    print(f"Sign agreement flow/VEX    = {sign_agreement(flow_ex,vex_ex):.3f}")

    print("\nINTERPRETATION")
    print("This card was supplied after the method and thresholds were frozen.")
    print("Passing supports the narrow directional-flow hypothesis only; failing rejects confirmation on this card.")
    print("Neither outcome identifies HeatSeeker's proprietary formula.")


if __name__ == "__main__":
    main()
