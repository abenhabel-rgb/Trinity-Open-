#!/usr/bin/env python3
"""Exploratory H4: does same-day signed dealer flow add information beyond static OI/gamma structure?

Target card: MU 2026-09-04, publication outer bound 12:27 ET, expiration 2026-09-04.
This is retrospective exploratory discrimination only. No confirmatory gate is declared here.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

FLOW = Path("mu_20260904_1227_volland_like.json")
STATIC = Path("mu_20260904_static_oi_gamma.json")
KING = 1000.0

HS_GEX = {
    955.0:-142.6, 960.0:319.8, 965.0:-193.0, 970.0:1607.2, 975.0:122.9,
    980.0:-1458.3, 985.0:4.5, 990.0:-2479.7, 995.0:-4046.6,
    1000.0:35984.6, 1005.0:2484.8, 1010.0:-1579.6, 1015.0:-609.6,
    1020.0:1743.0, 1025.0:2046.9, 1030.0:-1231.0, 1035.0:-151.4,
    1040.0:-123.6, 1045.0:72.6, 1050.0:601.7,
}


def mean(xs): return sum(xs)/len(xs)
def pearson(xs,ys):
    mx,my=mean(xs),mean(ys)
    dx=[x-mx for x in xs]; dy=[y-my for y in ys]
    den=math.sqrt(sum(x*x for x in dx)*sum(y*y for y in dy))
    return float('nan') if den==0 else sum(x*y for x,y in zip(dx,dy))/den

def ranks(v):
    p=sorted(enumerate(v), key=lambda z:z[1]); out=[0.0]*len(v); i=0
    while i<len(p):
        j=i+1
        while j<len(p) and p[j][1]==p[i][1]: j+=1
        r=(i+1+j)/2.0
        for k in range(i,j): out[p[k][0]]=r
        i=j
    return out

def spearman(xs,ys): return pearson(ranks(xs),ranks(ys))
def partial_spearman(x,y,z):
    rxy=spearman(x,y); rxz=spearman(x,z); ryz=spearman(y,z)
    den=math.sqrt(max(0.0,(1-rxz*rxz)*(1-ryz*ryz)))
    return float('nan') if den==0 else (rxy-rxz*ryz)/den

def sign_agreement(xs,ys):
    good=n=0
    for x,y in zip(xs,ys):
        if x==0 or y==0: continue
        n+=1; good += int((x>0)==(y>0))
    return good/n if n else float('nan')
def perm_partial_p(flow,gex,cp,obs,n=20000,seed=9042026):
    rng=random.Random(seed); f=list(flow); e=1
    for _ in range(n):
        rng.shuffle(f)
        v=partial_spearman(f,gex,cp)
        if abs(v)>=abs(obs): e+=1
    return e/(n+1)


def report(label,strikes,flow_by,static_by):
    f=[float(flow_by[k]['signed_contract_flow']) for k in strikes]
    g=[HS_GEX[k] for k in strikes]
    cp=[float(static_by[k]['cp_gamma_imbalance']) for k in strikes]
    goi=[float(static_by[k]['gamma_oi_total']) for k in strikes]
    oi=[float(static_by[k]['total_oi']) for k in strikes]

    rf=spearman(f,g)
    rcp=spearman(cp,g)
    pflow=partial_spearman(f,g,cp)
    pcp=partial_spearman(cp,g,f)
    pperm=perm_partial_p(f,g,cp,pflow)

    print(f"\n=== {label} | n={len(strikes)} ===")
    print("SIGNED TARGET GEX")
    print(f"Spearman(flow,GEX)                  {rf:+.3f}")
    print(f"Spearman(cp_gamma_imbalance,GEX)    {rcp:+.3f}")
    print(f"delta flow-minus-static             {rf-rcp:+.3f}")
    print(f"partial Spearman(flow,GEX | cp)     {pflow:+.3f}")
    print(f"partial Spearman(cp,GEX | flow)     {pcp:+.3f}")
    print(f"permutation p(partial flow)         {pperm:.5f}")
    print(f"sign agreement flow/GEX             {sign_agreement(f,g):.3f}")
    print(f"sign agreement cp/GEX               {sign_agreement(cp,g):.3f}")

    print("MAGNITUDE TARGET |GEX|")
    print(f"Spearman(total_OI,|GEX|)            {spearman(oi,list(map(abs,g))):+.3f}")
    print(f"Spearman(gammaOI_total,|GEX|)       {spearman(goi,list(map(abs,g))):+.3f}")
    return pflow,pperm


def main():
    if not FLOW.exists():
        raise SystemExit(f"Missing {FLOW}")
    if not STATIC.exists():
        raise SystemExit(f"Missing {STATIC}. Run collect_mu_static_structure.py first.")
    flow=json.loads(FLOW.read_text())
    static=json.loads(STATIC.read_text())
    fb={float(r['strike']):r for r in flow['rows']}
    sb={float(r['strike']):r for r in static['rows']}
    common=[k for k in sorted(HS_GEX) if k in fb and k in sb]
    if len(common)<8:
        raise SystemExit(f"NOT EVALUABLE: only {len(common)} common strikes")
    ex=[k for k in common if k!=KING]

    print("MU 2026-09-04 H4 — FLOW INCREMENTAL TO STATIC OI/GAMMA")
    print("Status: retrospective exploratory discrimination; not confirmatory.")
    print("Static sign variable = call-minus-put gamma*OI structural contrast, NOT dealer positioning.")
    report("ALL COMMON STRIKES",common,fb,sb)
    report("EX-KING 1000 PRIMARY",ex,fb,sb)
    print("\nINTERPRETATION")
    print("If partial flow correlation remains material after conditioning on static cp gamma*OI contrast, same-day flow contains incremental cross-sectional information on this card.")
    print("If it collapses toward zero, the earlier flow result may mainly proxy the pre-existing OI/gamma structure.")


if __name__=='__main__': main()
