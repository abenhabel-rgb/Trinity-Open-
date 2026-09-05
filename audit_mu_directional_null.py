#!/usr/bin/env python3
"""Directional-null audit for MU 2026-09-04 HeatSeeker vs frozen dealer-flow v1.

Purpose:
- test whether ex-King sign agreement can arise from the observed sign balance alone;
- test ex-King Spearman(flow, HS_GEX) against strike-label permutation;
- report leave-one-out stability;
- avoid confusing directional association with magnitude lift.

This remains in-sample mechanical evidence only.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

FLOW_FILE = Path("mu_20260904_1227_volland_like.json")
KING = 1000.0
N_PERM = 200_000
SEED = 20260905

HS_GEX = {
    955.0:-142.6, 960.0:319.8, 965.0:-193.0, 970.0:1607.2, 975.0:122.9,
    980.0:-1458.3, 985.0:4.5, 990.0:-2479.7, 995.0:-4046.6,
    1000.0:35984.6, 1005.0:2484.8, 1010.0:-1579.6, 1015.0:-609.6,
    1020.0:1743.0, 1025.0:2046.9, 1030.0:-1231.0, 1035.0:-151.4,
    1040.0:-123.6, 1045.0:72.6, 1050.0:601.7,
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
        for k in range(i, j):
            out[pairs[k][0]] = rank
        i = j
    return out


def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))


def sign_agreement(xs, ys):
    pairs = [(x,y) for x,y in zip(xs,ys) if x != 0 and y != 0]
    return sum((x > 0) == (y > 0) for x,y in pairs) / len(pairs)


def exact_sign_null_p(pred, target):
    """One-sided exact p, preserving numbers of positive predicted/target signs."""
    pred_pos = sum(x > 0 for x in pred)
    target_pos = sum(y > 0 for y in target)
    n = len(pred)
    observed_matches = sum((x > 0) == (y > 0) for x,y in zip(pred,target))

    lo = max(0, pred_pos + target_pos - n)
    hi = min(pred_pos, target_pos)
    denom = math.comb(n, target_pos)
    p = 0.0
    rows = []
    for overlap in range(lo, hi + 1):
        prob = math.comb(pred_pos, overlap) * math.comb(n - pred_pos, target_pos - overlap) / denom
        pred_neg = n - pred_pos
        target_pos_in_pred_neg = target_pos - overlap
        negneg = pred_neg - target_pos_in_pred_neg
        matches = overlap + negneg
        rows.append((overlap, matches, prob))
        if matches >= observed_matches:
            p += prob
    return observed_matches, pred_pos, target_pos, p


def permutation_spearman_p(xs, ys, n_perm=N_PERM, seed=SEED):
    obs = spearman(xs, ys)
    rng = random.Random(seed)
    y = list(ys)
    ge = 0
    for _ in range(n_perm):
        rng.shuffle(y)
        if spearman(xs, y) >= obs - 1e-15:
            ge += 1
    return obs, (ge + 1) / (n_perm + 1)


def main():
    data = json.loads(FLOW_FILE.read_text())
    by_strike = {float(r["strike"]): r for r in data["rows"]}
    strikes = [k for k in sorted(HS_GEX) if k in by_strike and k != KING]
    flow = [float(by_strike[k]["signed_contract_flow"]) for k in strikes]
    gex = [float(HS_GEX[k]) for k in strikes]

    print("OPENCLAW MU DIRECTIONAL NULL AUDIT")
    print(f"card=MU 2026-09-04 expiration=2026-09-04 ex_king={KING:.1f}")
    print(f"n={len(strikes)} frozen_method=quote_edge_signed_flow_v1")
    print("NOTE: this tests directional association only; prior magnitude audit favored raw volume/trade count.\n")

    acc = sign_agreement(flow, gex)
    matches, pred_pos, target_pos, p_sign = exact_sign_null_p(flow, gex)
    best_constant = max(target_pos, len(gex)-target_pos) / len(gex)

    print("SIGN TEST")
    print(f"observed_matches={matches}/{len(gex)} agreement={acc:.3f}")
    print(f"predicted_positive={pred_pos} target_positive={target_pos}")
    print(f"best_constant_sign_baseline={best_constant:.3f}")
    print(f"exact_one_sided_p_preserving_sign_counts={p_sign:.6f}")

    obs_s, p_s = permutation_spearman_p(flow, gex)
    print("\nRANK TEST")
    print(f"observed_spearman={obs_s:.3f}")
    print(f"permutation_n={N_PERM} seed={SEED}")
    print(f"one_sided_permutation_p={p_s:.6f}")

    loo = []
    for omit in strikes:
        sub = [k for k in strikes if k != omit]
        xf = [float(by_strike[k]["signed_contract_flow"]) for k in sub]
        yg = [float(HS_GEX[k]) for k in sub]
        loo.append((omit, sign_agreement(xf, yg), spearman(xf, yg)))

    print("\nLEAVE-ONE-OUT STABILITY")
    min_acc = min(loo, key=lambda x: x[1])
    max_acc = max(loo, key=lambda x: x[1])
    min_sp = min(loo, key=lambda x: x[2])
    max_sp = max(loo, key=lambda x: x[2])
    print(f"sign_agreement_range={min_acc[1]:.3f}..{max_acc[1]:.3f} (worst omit={min_acc[0]:.1f}, best omit={max_acc[0]:.1f})")
    print(f"spearman_range={min_sp[2]:.3f}..{max_sp[2]:.3f} (worst omit={min_sp[0]:.1f}, best omit={max_sp[0]:.1f})")

    print("\nSTATUS")
    gate_sign = acc >= 0.65
    gate_rank = obs_s >= 0.35
    print(f"development_gate_sign>=0.65: {'PASS' if gate_sign else 'FAIL'}")
    print(f"development_gate_spearman>=0.35: {'PASS' if gate_rank else 'FAIL'}")
    print("magnitude_lift_vs_volume: FAIL on this card (from prior audit)")
    print("VERDICT: retain a narrow directional-flow hypothesis only. Do not claim a magnitude model or proprietary HeatSeeker reconstruction.")
    print("NEXT: run frozen v1 unchanged on an independent MU card before any parameter tuning.")


if __name__ == "__main__":
    main()
