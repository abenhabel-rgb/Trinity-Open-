#!/usr/bin/env python3
"""MU 2026-05-20 — H7 static-core replication diagnostic.

The H7 rules are now frozen in docs/MU_H7_STATIC_CORE_FROZEN.md for the NEXT unseen
eligible MU card. This 2026-05-20 card was already visible before the explicit freeze,
so this run is diagnostic only and cannot decide H7.

Card facts transcribed from the user-provided screenshot:
- published 2026-05-20 20:35 Paris = 14:35 ET
- displayed spot 727.40
- starred GEX King: strike 700, -1558.0K
- deterministic King-column expiration: 2026-05-22
- largest fully legible displayed block used here: 630.0 .. 835.0
- 66 displayed strikes, 65 ex-King

No reconstructed intraday gamma. No dealer sign inferred from call/put.
"""
from __future__ import annotations

import json, math, random, statistics, subprocess, sys
from pathlib import Path

SYMBOL="MU"; DATE="20260520"; EXPIRATION="20260522"; GAMMA_DATE="20260519"; KING=700.0
N_PERM=10_000; SEED=20260520
STATIC_FILE=Path("mu_20260520_20260522_static_oi_gamma.json")
OUT_FILE=Path("mu_20260520_h7_replication_diagnostic.json")

HS_GEX_K={
835.0:-38.4,830.0:-55.2,825.0:80.8,820.0:-16.8,815.0:113.8,810.0:95.4,805.0:310.2,
800.0:-567.9,795.0:-44.4,790.0:-232.3,785.0:-0.2,780.0:-529.4,775.0:30.0,770.0:553.3,
765.0:63.1,760.0:356.0,755.0:184.7,750.0:607.6,747.5:-4.1,745.0:64.3,742.5:56.7,
740.0:165.7,737.5:2.8,735.0:-676.3,732.5:101.4,730.0:-604.4,727.5:52.0,725.0:424.2,
722.5:144.0,720.0:433.6,717.5:24.2,715.0:273.8,712.5:109.4,710.0:273.6,707.5:86.4,
705.0:75.1,702.5:-8.1,700.0:-1558.0,697.5:105.5,695.0:74.3,692.5:-40.8,690.0:-334.4,
687.5:206.1,685.0:33.2,682.5:8.9,680.0:-552.9,677.5:32.0,675.0:-6.4,672.5:-13.5,
670.0:-81.6,667.5:5.7,665.0:57.8,662.5:76.4,660.0:156.3,657.5:-6.4,655.0:-19.9,
652.5:-8.9,650.0:795.7,647.5:-37.9,645.0:-184.1,642.5:182.9,640.0:80.2,637.5:-12.3,
635.0:2.4,632.5:-47.2,630.0:-776.7}

def rankdata(xs):
    pairs=sorted(enumerate(xs),key=lambda z:z[1]); r=[0.0]*len(xs); i=0
    while i<len(pairs):
        j=i+1
        while j<len(pairs) and pairs[j][1]==pairs[i][1]: j+=1
        a=(i+1+j)/2.0
        for k in range(i,j): r[pairs[k][0]]=a
        i=j
    return r

def pearson(x,y):
    mx,my=statistics.mean(x),statistics.mean(y); dx=[v-mx for v in x]; dy=[v-my for v in y]
    den=math.sqrt(sum(v*v for v in dx)*sum(v*v for v in dy))
    return float('nan') if den==0 else sum(a*b for a,b in zip(dx,dy))/den

def spearman(x,y): return pearson(rankdata(x),rankdata(y))

def perm_p(x,y,obs):
    rng=random.Random(SEED); rx=rankdata(x); ry=rankdata(y); ge=0
    for _ in range(N_PERM):
        px=rx[:]; rng.shuffle(px); rp=pearson(px,ry)
        if abs(rp)>=abs(obs)-1e-15: ge+=1
    return (ge+1)/(N_PERM+1)

def main():
    subprocess.run([sys.executable,"collect_mu_static_structure.py","--symbol",SYMBOL,"--expiration",EXPIRATION,
                    "--oi-date",DATE,"--gamma-date",GAMMA_DATE,"--output",str(STATIC_FILE)],check=True)
    data=json.loads(STATIC_FILE.read_text()); smap={float(r['strike']):r for r in data.get('rows',[])}
    rows=[]
    for k,g in HS_GEX_K.items():
        s=smap.get(k)
        if not s: continue
        rows.append({'strike':k,'gex_k':g,'abs_gex_k':abs(g),'gamma_oi_total':s['gamma_oi_total'],'total_oi':s['total_oi']})
    ex=[r for r in rows if r['strike']!=KING]
    x=[float(r['gamma_oi_total']) for r in ex]; y=[float(r['abs_gex_k']) for r in ex]
    rho=spearman(x,y); p=perm_p(x,y,rho)
    rho_oi=spearman([float(r['total_oi']) for r in ex],y)
    largest=max(ex,key=lambda r:r['abs_gex_k'])
    robust=[r for r in ex if r['strike']!=largest['strike']]
    rho_rob=spearman([float(r['gamma_oi_total']) for r in robust],[float(r['abs_gex_k']) for r in robust])
    gates={'n_ge_20':len(ex)>=20,'rho_ge_060':rho>=0.60,'perm_p_lt_005':p<0.05,'robust_rho_ge_050':rho_rob>=0.50}
    result={'status':'REPLICATION_DIAGNOSTIC_NOT_CONFIRMATORY','symbol':SYMBOL,'date':DATE,'expiration':EXPIRATION,
            'spot_displayed':727.40,'publication_paris':'2026-05-20 20:35','publication_et':'2026-05-20 14:35',
            'king':{'strike':KING,'gex_k':HS_GEX_K[KING]},'n_usable_all':len(rows),'n_usable_ex_king':len(ex),
            'primary':{'spearman_gammaoi_abs_gex':rho,'permutation_p_two_sided':p,'spearman_totaloi_abs_gex':rho_oi},
            'robustness':{'removed_largest_remaining_abs_gex_strike':largest['strike'],'removed_abs_gex_k':largest['abs_gex_k'],
                          'spearman_gammaoi_abs_gex_after_removal':rho_rob,'n':len(robust)},
            'proposed_h7_gates_applied_diagnostically':gates,'rows':rows,
            'note':'Cannot decide H7 because explicit freeze occurred after this card was already seen.'}
    OUT_FILE.write_text(json.dumps(result,indent=2))
    print("MU 2026-05-20 — H7 STATIC-CORE REPLICATION DIAGNOSTIC")
    print(f"usable all={len(rows)} ex-King={len(ex)}")
    print(f"gammaOI vs |GEX| Spearman: {rho:+.3f}")
    print(f"permutation p (two-sided, 10k): {p:.5f}")
    print(f"total OI vs |GEX| Spearman: {rho_oi:+.3f}")
    print(f"largest remaining |GEX| removed: strike {largest['strike']:.1f}, |GEX|={largest['abs_gex_k']:.1f}K")
    print(f"robust gammaOI vs |GEX| Spearman: {rho_rob:+.3f}")
    print("\nPROPOSED H7 GATES APPLIED DIAGNOSTICALLY")
    for k,v in gates.items(): print(f"{k}: {'PASS' if v else 'FAIL'}")
    print("STATUS: REPLICATION_DIAGNOSTIC_NOT_CONFIRMATORY")
    print(f"saved: {OUT_FILE.resolve()}")
    return 0
if __name__=='__main__': raise SystemExit(main())
