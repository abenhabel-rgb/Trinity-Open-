#!/usr/bin/env python3
"""Post-hoc timestamp-sensitivity diagnostic for the failed MU 2026-06-24 H5 card.

This script does NOT modify H5, its frozen classifier, or its frozen gates.
It reports the complete cumulative-window path; no best timestamp is promoted to
confirmatory evidence. Publication time 11:04 ET is an outer bound only.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

STATIC = Path("mu_20260624_static_oi_gamma.json")
KING = 1000.0
WINDOWS = ["09:45:00", "10:00:00", "10:15:00", "10:30:00", "10:45:00", "11:00:00", "11:04:00"]

HS_GEX = {
    955.0: -25.7, 960.0: 25.0, 965.0: -32.8, 970.0: -82.7, 975.0: 23.6,
    980.0: -47.1, 985.0: 3.1, 990.0: -102.4, 995.0: -6.3, 1000.0: -2469.1,
    1005.0: 29.0, 1010.0: 24.6, 1015.0: 21.1, 1020.0: 42.6, 1025.0: 29.0,
    1030.0: -19.4, 1035.0: 24.8, 1040.0: -111.9, 1045.0: 19.2,
    1050.0: 1082.4, 1055.0: -746.7,
}


def mean(xs): return sum(xs) / len(xs)

def pearson(xs, ys):
    mx, my = mean(xs), mean(ys)
    dx = [x-mx for x in xs]; dy = [y-my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return float("nan") if den == 0 else sum(x*y for x, y in zip(dx, dy)) / den

def ranks(v):
    p = sorted(enumerate(v), key=lambda z: z[1]); out = [0.0]*len(v); i = 0
    while i < len(p):
        j = i + 1
        while j < len(p) and p[j][1] == p[i][1]: j += 1
        r = (i + 1 + j) / 2.0
        for k in range(i, j): out[p[k][0]] = r
        i = j
    return out

def spearman(xs, ys): return pearson(ranks(xs), ranks(ys))

def partial_spearman(x, y, z):
    rxy = spearman(x, y); rxz = spearman(x, z); ryz = spearman(y, z)
    den = math.sqrt(max(0.0, (1-rxz*rxz)*(1-ryz*ryz)))
    return float("nan") if den == 0 else (rxy-rxz*ryz)/den

def sign_agreement(xs, ys):
    good = n = 0
    for x, y in zip(xs, ys):
        if x == 0 or y == 0: continue
        n += 1; good += int((x > 0) == (y > 0))
    return good/n if n else float("nan")


def main():
    if not STATIC.exists():
        raise SystemExit(f"Missing {STATIC}")
    static = json.loads(STATIC.read_text())
    sb = {float(r["strike"]): r for r in static["rows"]}

    print("MU 2026-06-24 — POST-HOC TIMESTAMP SENSITIVITY")
    print("H5 confirmatory result remains FAIL regardless of this diagnostic.")
    print("All windows start 09:30 ET; only cumulative end time varies.")
    print("No best window may be relabeled confirmatory.\n")
    print("end_ET   n  Spearman(flow,GEX)  partial(flow,GEX|cp)  sign_agreement")

    vals = []
    for end in WINDOWS:
        safe = end.replace(":", "")
        path = Path(f"mu_20260624_20260626_{safe}_volland_like_frozen_v1.json")
        if not path.exists():
            print(f"{end}   MISSING {path}")
            continue
        flow = json.loads(path.read_text())
        fb = {float(r["strike"]): r for r in flow["rows"]}
        common = [k for k in sorted(HS_GEX) if k != KING and k in fb and k in sb]
        if len(common) < 12:
            print(f"{end}   NOT EVALUABLE n={len(common)}")
            continue
        f = [float(fb[k]["signed_contract_flow"]) for k in common]
        g = [HS_GEX[k] for k in common]
        cp = [float(sb[k]["cp_gamma_imbalance"]) for k in common]
        rf = spearman(f, g)
        pf = partial_spearman(f, g, cp)
        sa = sign_agreement(f, g)
        vals.append((end, rf, pf, sa))
        print(f"{end}  {len(common):2d}       {rf:+.3f}                 {pf:+.3f}              {sa:.3f}")

    if vals:
        rfs = [v[1] for v in vals]; pfs = [v[2] for v in vals]; sas = [v[3] for v in vals]
        print("\nRANGE ONLY — descriptive, post-hoc")
        print(f"Spearman(flow,GEX):       {min(rfs):+.3f} .. {max(rfs):+.3f}")
        print(f"partial(flow,GEX|cp):     {min(pfs):+.3f} .. {max(pfs):+.3f}")
        print(f"sign agreement:           {min(sas):.3f} .. {max(sas):.3f}")
        print("\nInterpretation: a strong time path would indicate timestamp sensitivity worth testing prospectively on a future card with a pre-specified end-time rule. It does not overturn the H5 FAIL.")


if __name__ == "__main__": main()
