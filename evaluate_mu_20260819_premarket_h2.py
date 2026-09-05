#!/usr/bin/env python3
"""Exploratory H2: prior-session signed flow vs MU premarket HeatSeeker GEX.

H2 was frozen before inspecting ThetaData 2026-08-18 results.
This is development evidence only, not confirmatory.

IMPORTANT: the target values below are the actual 2026-08-19 GEX screenshot
published 2026-08-19 13:25 Paris (07:25 ET). An earlier revision mistakenly
contained values from a different MU card; results from that revision are invalid.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

FLOW_FILE = Path("mu_20260818_20260819_160000_volland_like_frozen_v1.json")
KING = 950.0

# Direct transcription from the user-provided MU GEX screenshot.
# Target column: expiration 2026-08-19. Units: K as displayed by HeatSeeker.
# Only clearly readable strikes are included.
HS_GEX = {
    935.0: 552.0,
    940.0: -317.1,
    942.5: 0.0,
    945.0: -298.0,
    950.0: -2170.2,
    955.0: 324.9,
    960.0: 1559.3,
    962.5: 0.0,
    965.0: 635.0,
    970.0: 67.5,
    975.0: 435.3,
    980.0: 1352.2,
    985.0: 116.1,
    990.0: -626.2,
    995.0: 370.0,
    1000.0: 189.2,
    1005.0: 7.1,
    1010.0: 48.9,
    1015.0: 41.8,
    1020.0: -74.2,
}


def mean(xs):
    return sum(xs) / len(xs)


def pearson(xs, ys):
    mx, my = mean(xs), mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return float("nan") if den == 0 else sum(x*y for x, y in zip(dx,dy)) / den


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
    return good / n if n else float("nan"), good, n


def permutation_p(xs, ys, observed, nperm=20000, seed=20260819):
    rng = random.Random(seed)
    y = list(ys)
    extreme = 1
    for _ in range(nperm):
        rng.shuffle(y)
        if abs(spearman(xs, y)) >= abs(observed):
            extreme += 1
    return extreme / (nperm + 1)


def report(label, strikes, by_strike):
    flow = [float(by_strike[k]["signed_contract_flow"]) for k in strikes]
    volume = [float(by_strike[k].get("raw_contract_volume", by_strike[k]["classified_contracts"] + by_strike[k]["unknown_contracts"])) for k in strikes]
    trades = [float(by_strike[k]["trade_count"]) for k in strikes]
    gex = [HS_GEX[k] for k in strikes]

    r_flow = spearman(flow, gex)
    r_vol = spearman(volume, gex)
    r_trades = spearman(trades, gex)
    agree, good, n = sign_agreement(flow, gex)
    lift = r_flow - r_vol
    pperm = permutation_p(flow, gex, r_flow)

    print(f"\n=== {label} | n={len(strikes)} ===")
    print(f"Pearson(flow,GEX)        {pearson(flow,gex):+.3f}")
    print(f"Spearman(flow,GEX)       {r_flow:+.3f}")
    print(f"Sign agreement           {agree:.3f} ({good}/{n})")
    print(f"Spearman(volume,GEX)     {r_vol:+.3f}")
    print(f"Spearman(tradecount,GEX) {r_trades:+.3f}")
    print(f"Directional lift         {lift:+.3f}")
    print(f"Permutation p(Spearman)  {pperm:.5f}")
    return r_flow, agree, lift


def main():
    if not FLOW_FILE.exists():
        raise SystemExit(f"Missing {FLOW_FILE}. Run the frozen collector first.")

    data = json.loads(FLOW_FILE.read_text())
    by_strike = {float(r["strike"]): r for r in data["rows"]}
    common = [k for k in sorted(HS_GEX) if k in by_strike]
    ex_king = [k for k in common if k != KING]

    print("MU 2026-08-19 PREMARKET H2 — PRIOR SESSION CARRY — CORRECTED TARGET")
    print("Target card publication: 07:25 ET, before regular-session open.")
    print("Candidate source: 2026-08-18 09:30-16:00 ET signed flow, expiration 2026-08-19.")
    print("King on actual GEX screenshot: strike 950, value -2170.2K.")
    print("Status: exploratory development; not confirmatory.")

    report("ALL COMMON STRIKES", common, by_strike)
    r, s, l = report("EX-KING 950 PRIMARY", ex_king, by_strike)

    print("\nREFERENCE THRESHOLDS (same numbers as frozen H1, descriptive only)")
    print(f"sign agreement >= 0.65: {'PASS' if s >= 0.65 else 'FAIL'} ({s:.3f})")
    print(f"Spearman(flow,GEX) >= 0.35: {'PASS' if r >= 0.35 else 'FAIL'} ({r:+.3f})")
    print(f"directional lift >= +0.20: {'PASS' if l >= 0.20 else 'FAIL'} ({l:+.3f})")
    print("\nINTERPRETATION")
    print("A pass supports exploring prior-session carry; a fail weakens that simple explanation.")
    print("Do not compare these results with the invalid earlier run that used the wrong target card.")


if __name__ == "__main__":
    main()
