#!/usr/bin/env python3
"""Compare MU 2026-09-04 Volland-like flow against observed HeatSeeker GEX/VEX.

The HeatSeeker values below are transcribed from the user-provided 2026-09-04
MU screenshots for expiration 2026-09-04. This is mechanical comparison only;
it does not identify HeatSeeker's proprietary formula.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

FLOW_FILE = Path("mu_20260904_1227_volland_like.json")
SPOT = 1002.66

HS_GEX = {
    955.0:-142.6, 960.0:319.8, 965.0:-193.0, 970.0:1607.2, 975.0:122.9,
    980.0:-1458.3, 985.0:4.5, 990.0:-2479.7, 995.0:-4046.6,
    1000.0:35984.6, 1005.0:2484.8, 1010.0:-1579.6, 1015.0:-609.6,
    1020.0:1743.0, 1025.0:2046.9, 1030.0:-1231.0, 1035.0:-151.4,
    1040.0:-123.6, 1045.0:72.6, 1050.0:601.7,
}

HS_VEX = {
    955.0:4836.7, 960.0:-16048.0, 965.0:7410.3, 970.0:-65598.8,
    975.0:-3596.3, 980.0:49118.2, 985.0:-1700.0, 990.0:45553.7,
    995.0:42329.9, 1000.0:-145189.6, 1005.0:9080.5,
    1010.0:-17401.2, 1015.0:-10710.5, 1020.0:40363.9,
    1025.0:59672.4, 1030.0:-41936.0, 1035.0:-5630.6,
    1040.0:-4927.8, 1045.0:3182.6, 1050.0:25971.9,
}


def mean(xs):
    return sum(xs) / len(xs)


def pearson(xs, ys):
    mx, my = mean(xs), mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return float('nan') if den == 0 else sum(x*y for x, y in zip(dx,dy)) / den


def ranks(values):
    # Average ranks for ties.
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
    good = 0
    n = 0
    for x,y in zip(xs,ys):
        if x == 0 or y == 0:
            continue
        n += 1
        good += (x > 0) == (y > 0)
    return good / n if n else float('nan')


def metric(name, xs, ys):
    print(f"{name:26s} pearson={pearson(xs,ys): .3f} spearman={spearman(xs,ys): .3f} sign={sign_agreement(xs,ys):.3f}")


def main():
    data = json.loads(FLOW_FILE.read_text())
    by_strike = {float(r['strike']): r for r in data['rows']}
    strikes = [k for k in sorted(HS_GEX) if k in by_strike]

    flow = [float(by_strike[k]['signed_contract_flow']) for k in strikes]
    premium = [float(by_strike[k]['signed_premium_notional']) for k in strikes]
    dag_flow = [(-x if k > SPOT else x) for k,x in zip(strikes,flow)]
    dag_premium = [(-x if k > SPOT else x) for k,x in zip(strikes,premium)]
    gex = [HS_GEX[k] for k in strikes]
    vex = [HS_VEX[k] for k in strikes]

    print(f"COMMON STRIKES: {len(strikes)}\n")
    print("strike    flow        premium      HS_GEX(K)      HS_VEX(K)")
    for k,f,p,g,v in zip(strikes,flow,premium,gex,vex):
        print(f"{k:6.1f} {f:8.0f} {p:13.0f} {g:13.1f} {v:14.1f}")

    print("\nSIGNED COMPARISONS")
    metric("flow vs GEX", flow, gex)
    metric("flow vs VEX", flow, vex)
    metric("premium vs GEX", premium, gex)
    metric("premium vs VEX", premium, vex)
    metric("DAG flow vs GEX", dag_flow, gex)
    metric("DAG flow vs VEX", dag_flow, vex)
    metric("DAG premium vs GEX", dag_premium, gex)
    metric("DAG premium vs VEX", dag_premium, vex)

    print("\nMAGNITUDE COMPARISONS")
    metric("|flow| vs |GEX|", list(map(abs,flow)), list(map(abs,gex)))
    metric("|flow| vs |VEX|", list(map(abs,flow)), list(map(abs,vex)))
    metric("|premium| vs |GEX|", list(map(abs,premium)), list(map(abs,gex)))
    metric("|premium| vs |VEX|", list(map(abs,premium)), list(map(abs,vex)))

    print("\nINTERPRETATION RULE")
    print("Correlation here is mechanical evidence only. It does not establish the proprietary HeatSeeker formula or predictive lift.")


if __name__ == "__main__":
    main()
