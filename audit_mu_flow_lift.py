#!/usr/bin/env python3
"""Audit whether signed dealer-flow adds structure beyond raw option volume.

Uses the frozen MU 2026-09-04 HeatSeeker transcription and the already-produced
Volland-like flow JSON. This is a diagnostic lift test, not proof of a proprietary
formula and not a predictive backtest.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

FLOW_FILE = Path("mu_20260904_1227_volland_like.json")
KING = 1000.0

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
    return float("nan") if den == 0 else sum(x*y for x, y in zip(dx, dy)) / den


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
    n = good = 0
    for x, y in zip(xs, ys):
        if x == 0 or y == 0:
            continue
        n += 1
        good += ((x > 0) == (y > 0))
    return good / n if n else float("nan")


def corr(xs, ys):
    return pearson(xs, ys), spearman(xs, ys)


def fmt(x):
    return "nan" if math.isnan(x) else f"{x:+.3f}"


def analyze(label, strikes, by_strike):
    flow = [float(by_strike[k]["signed_contract_flow"]) for k in strikes]
    volume = [float(by_strike[k]["classified_contracts"] + by_strike[k]["unknown_contracts"]) for k in strikes]
    trades = [float(by_strike[k]["trade_count"]) for k in strikes]
    premium = [float(by_strike[k]["signed_premium_notional"]) for k in strikes]
    gex = [HS_GEX[k] for k in strikes]
    vex = [HS_VEX[k] for k in strikes]

    print(f"\n=== {label} | n={len(strikes)} ===")
    print(f"signed flow vs GEX:       pearson={fmt(pearson(flow,gex))} spearman={fmt(spearman(flow,gex))} sign={sign_agreement(flow,gex):.3f}")
    print(f"signed flow vs VEX:       pearson={fmt(pearson(flow,vex))} spearman={fmt(spearman(flow,vex))} sign={sign_agreement(flow,vex):.3f}")

    for target_name, target in (("|GEX|", list(map(abs, gex))), ("|VEX|", list(map(abs, vex)))):
        aflow = list(map(abs, flow))
        avol = volume
        atrades = trades
        apremium = list(map(abs, premium))
        p_f, s_f = corr(aflow, target)
        p_v, s_v = corr(avol, target)
        p_t, s_t = corr(atrades, target)
        p_p, s_p = corr(apremium, target)
        print(f"\nMagnitude target {target_name}")
        print(f"  |signed flow|:           pearson={fmt(p_f)} spearman={fmt(s_f)}")
        print(f"  raw contract volume:     pearson={fmt(p_v)} spearman={fmt(s_v)}")
        print(f"  raw trade count:         pearson={fmt(p_t)} spearman={fmt(s_t)}")
        print(f"  |signed premium|:        pearson={fmt(p_p)} spearman={fmt(s_p)}")
        print(f"  LIFT flow-volume:        pearson={fmt(p_f-p_v)} spearman={fmt(s_f-s_v)}")
        print(f"  LIFT flow-tradecount:    pearson={fmt(p_f-p_t)} spearman={fmt(s_f-s_t)}")


def leave_one_out(strikes, by_strike, target_map):
    rows = []
    for omitted in strikes:
        ss = [k for k in strikes if k != omitted]
        flow = [abs(float(by_strike[k]["signed_contract_flow"])) for k in ss]
        volume = [float(by_strike[k]["classified_contracts"] + by_strike[k]["unknown_contracts"]) for k in ss]
        target = [abs(target_map[k]) for k in ss]
        sf = spearman(flow, target)
        sv = spearman(volume, target)
        rows.append((omitted, sf, sv, sf-sv))
    return rows


def summarize_loo(name, rows):
    lifts = [x[3] for x in rows]
    flows = [x[1] for x in rows]
    vols = [x[2] for x in rows]
    worst = min(rows, key=lambda x: x[3])
    best = max(rows, key=lambda x: x[3])
    print(f"\nLEAVE-ONE-OUT {name} (Spearman magnitude)")
    print(f"  |flow| range:   {min(flows):+.3f} .. {max(flows):+.3f}")
    print(f"  volume range:   {min(vols):+.3f} .. {max(vols):+.3f}")
    print(f"  lift range:     {min(lifts):+.3f} .. {max(lifts):+.3f}")
    print(f"  worst lift when omitting strike {worst[0]:.1f}: {worst[3]:+.3f}")
    print(f"  best  lift when omitting strike {best[0]:.1f}: {best[3]:+.3f}")


def main():
    data = json.loads(FLOW_FILE.read_text())
    by_strike = {float(r["strike"]): r for r in data["rows"]}
    strikes = [k for k in sorted(HS_GEX) if k in by_strike]
    ex_king = [k for k in strikes if k != KING]

    print("OPENCLAW MU FLOW LIFT AUDIT")
    print("Candidate: conservative quote-edge signed dealer flow")
    print("Baseline: raw contract volume by strike (classified + unknown)")
    print("Secondary baseline: raw trade count")
    print("No parameter tuning is performed in this script.")

    analyze("ALL COMMON STRIKES", strikes, by_strike)
    analyze("EX-KING 1000", ex_king, by_strike)

    summarize_loo("|GEX|", leave_one_out(strikes, by_strike, HS_GEX))
    summarize_loo("|VEX|", leave_one_out(strikes, by_strike, HS_VEX))

    print("\nDECISION RULE")
    print("Positive lift means |signed dealer flow| ranks HeatSeeker magnitude better than raw volume on this card.")
    print("This is an in-sample mechanical diagnostic only. The method must remain frozen for the next independent MU card.")


if __name__ == "__main__":
    main()
