#!/usr/bin/env python3
from __future__ import annotations

import csv, json, math, statistics
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review/extracted/j1_vs_open')
CELL_DELTAS = BASE / 'cell_deltas.csv'
SEQ_SCORES = BASE / 'structure_summary/sequential_persistence_model/snapshot_sequential_scores.csv'
OUT = BASE / 'structure_summary/mrvl_meta_shuffle_signature'
TARGETS = [('MRVL','GEX'),('MRVL','VEX'),('META','GEX'),('META','VEX')]


def fnum(v):
    try:
        x=float(v); return x if math.isfinite(x) else None
    except Exception: return None

def truthy(v): return str(v).strip().lower() in {'1','true','yes','y'}
def pctdist(k,s): return None if s in (None,0) else (k/s-1.0)*100.0

def center(rows,key):
    num=den=0.0
    for r in rows:
        v=fnum(r.get(key)); k=fnum(r.get('strike'))
        if v is None or k is None: continue
        w=abs(v); num+=w*k; den+=w
    return num/den if den else None

def dominant(rows,key):
    valid=[(r,fnum(r.get(key))) for r in rows if fnum(r.get(key)) is not None]
    if not valid: return None
    r,v=max(valid,key=lambda x:abs(x[1]))
    return {'expiration':r['expiration'],'strike':float(r['strike']),'value':v}

def share_side(rows,key,spot,side):
    if spot in (None,0): return None
    den=num=0.0
    for r in rows:
        v=fnum(r.get(key)); k=fnum(r.get('strike'))
        if v is None or k is None: continue
        a=abs(v); den+=a
        if (side=='above' and k>spot) or (side=='below' and k<spot): num+=a
    return num/den if den else None

def top_share(rows,key,n=3):
    vals=sorted([abs(fnum(r.get(key)) or 0.0) for r in rows],reverse=True)
    return sum(vals[:n])/sum(vals) if sum(vals) else None

def longest_run(flags):
    best=cur=0
    for x in flags:
        cur=cur+1 if x else 0; best=max(best,cur)
    return best

def analyze(ticker,metric,seq_all,cells_all):
    seq=sorted([r for r in seq_all if r.get('ticker')==ticker and r.get('metric')==metric],key=lambda r:r['j_timestamp'])
    selected=[r for r in seq if truthy(r.get('top_decile_anomaly'))]
    if not selected:
        return {'ticker':ticker,'metric':metric,'status':'no_top_decile_observations'}
    ts=[r['j_timestamp'] for r in selected]; tsset=set(ts)
    cells=[r for r in cells_all if r.get('ticker')==ticker and r.get('metric')==metric and r.get('j_timestamp') in tsset]
    by=defaultdict(list)
    for r in cells: by[r['j_timestamp']].append(r)
    keysets=[{(r['expiration'],float(r['strike'])) for r in by[t]} for t in ts if by[t]]
    if len(keysets)!=len(ts):
        return {'ticker':ticker,'metric':metric,'status':'missing_snapshot_cells'}
    common=set.intersection(*keysets) if keysets else set()
    if not common:
        return {'ticker':ticker,'metric':metric,'status':'no_persistent_exact_cells'}
    pdata={t:[r for r in by[t] if (r['expiration'],float(r['strike'])) in common] for t in ts}
    first=pdata[ts[0]]
    base_center=center(first,'j1_value')
    base_above=share_side(first,'j1_value',fnum(first[0].get('j1_spot')),'above')
    base_below=share_side(first,'j1_value',fnum(first[0].get('j1_spot')),'below')
    rows=[]; doms=[]; prior=None
    for t in ts:
        rr=pdata[t]; spot=fnum(rr[0].get('j_spot')); c=center(rr,'j_value'); d=dominant(rr,'j_value')
        above=share_side(rr,'j_value',spot,'above'); below=share_side(rr,'j_value',spot,'below')
        flips=sum(1 for r in rr if (fnum(r.get('j1_value')) or 0)*(fnum(r.get('j_value')) or 0)<0)
        rows.append({
            'ticker':ticker,'metric':metric,'timestamp':t,'spot':spot,
            'center_strike':c,'center_shift_from_j1':None if c is None or base_center is None else c-base_center,
            'above_spot_abs_share':above,'below_spot_abs_share':below,
            'above_share_change_vs_j1':None if above is None or base_above is None else above-base_above,
            'below_share_change_vs_j1':None if below is None or base_below is None else below-base_below,
            'top3_abs_share':top_share(rr,'j_value',3),
            'sign_flip_ratio':flips/len(rr) if rr else None,
            'dominant_expiration':d['expiration'] if d else '',
            'dominant_strike':d['strike'] if d else None,
            'dominant_value':d['value'] if d else None,
            'dominant_distance_pct_spot':pctdist(d['strike'],spot) if d else None,
            'handoff_from_prior':bool(prior and d and (d['strike']!=prior['strike'] or d['expiration']!=prior['expiration'])),
            'residual_shuffle_score':fnum(next(x for x in selected if x['j_timestamp']==t).get('residual_shuffle_score')),
        })
        if d: doms.append((d['expiration'],d['strike']))
        prior=d
    domfreq=Counter(doms)
    center_shifts=[r['center_shift_from_j1'] for r in rows if r['center_shift_from_j1'] is not None]
    above_changes=[r['above_share_change_vs_j1'] for r in rows if r['above_share_change_vs_j1'] is not None]
    below_changes=[r['below_share_change_vs_j1'] for r in rows if r['below_share_change_vs_j1'] is not None]
    handoffs=[r['handoff_from_prior'] for r in rows[1:]]
    positive_center=[x>0 for x in center_shifts]
    reinforce_above=[x>0 for x in above_changes]
    weaken_below=[x<0 for x in below_changes]
    signature_hits=[]
    for r in rows:
        sig=(r['center_shift_from_j1'] is not None and r['center_shift_from_j1']>0 and
             r['above_share_change_vs_j1'] is not None and r['above_share_change_vs_j1']>0 and
             r['below_share_change_vs_j1'] is not None and r['below_share_change_vs_j1']<0)
        signature_hits.append(sig)
    return {
        'ticker':ticker,'metric':metric,'status':'ok','selected_top_decile_observations':len(ts),
        'persistent_exact_cells':len(common),'first_timestamp':ts[0],'last_timestamp':ts[-1],
        'mean_center_shift_from_j1':statistics.mean(center_shifts) if center_shifts else None,
        'positive_center_shift_fraction':sum(positive_center)/len(positive_center) if positive_center else None,
        'mean_above_share_change_vs_j1':statistics.mean(above_changes) if above_changes else None,
        'reinforce_above_fraction':sum(reinforce_above)/len(reinforce_above) if reinforce_above else None,
        'mean_below_share_change_vs_j1':statistics.mean(below_changes) if below_changes else None,
        'weaken_below_fraction':sum(weaken_below)/len(weaken_below) if weaken_below else None,
        'signature_hit_fraction':sum(signature_hits)/len(signature_hits),
        'longest_signature_run':longest_run(signature_hits),
        'handoff_count':sum(handoffs),'handoff_fraction':sum(handoffs)/len(handoffs) if handoffs else 0.0,
        'dominant_candidate_frequency':[{'expiration':e,'strike':k,'observations':n,'fraction':n/len(ts)} for (e,k),n in domfreq.most_common(5)],
        'snapshots':rows,
    }

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with SEQ_SCORES.open(encoding='utf-8') as f: seq=list(csv.DictReader(f))
    with CELL_DELTAS.open(encoding='utf-8') as f: cells=list(csv.DictReader(f))
    results=[analyze(t,m,seq,cells) for t,m in TARGETS]
    flat=[]
    for r in results:
        if r.get('status')!='ok':
            flat.append({'ticker':r['ticker'],'metric':r['metric'],'status':r['status']}); continue
        flat.append({k:v for k,v in r.items() if k not in {'snapshots','dominant_candidate_frequency'}})
    fields=sorted({k for r in flat for k in r.keys()})
    with (OUT/'comparison_summary.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(flat)
    for r in results:
        if r.get('status')!='ok': continue
        name=f"{r['ticker'].lower()}_{r['metric'].lower()}_snapshots.csv"
        with (OUT/name).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(r['snapshots'][0].keys())); w.writeheader(); w.writerows(r['snapshots'])
    (OUT/'comparison_summary.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    html=['<!doctype html><meta charset="utf-8"><title>MRVL META shuffle signature</title>',
          '<style>body{font-family:system-ui;background:#111;color:#eee;margin:28px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #444;padding:7px;text-align:right}th:first-child,td:first-child{text-align:left}.note{color:#bbb}</style>',
          '<h1>OpenClaw — MRVL / META shuffle signature — 2026-08-28</h1>',
          '<p class="note">Same frozen diagnostics as AMZN. Observed-only; exact persistent cells; no imputation. Node/King wording is heuristic, not confirmed Skylit terminology.</p>',
          '<table><tr><th>Ticker</th><th>Metric</th><th>Top-decile obs.</th><th>Persistent cells</th><th>Mean center shift</th><th>Above-share Δ</th><th>Below-share Δ</th><th>Signature fraction</th><th>Longest run</th><th>Handoffs</th></tr>']
    for r in results:
        if r.get('status')!='ok':
            html.append(f"<tr><td>{r['ticker']}</td><td>{r['metric']}</td><td colspan='8'>{r['status']}</td></tr>"); continue
        vals=[r['ticker'],r['metric'],r['selected_top_decile_observations'],r['persistent_exact_cells'],r['mean_center_shift_from_j1'],r['mean_above_share_change_vs_j1'],r['mean_below_share_change_vs_j1'],r['signature_hit_fraction'],r['longest_signature_run'],r['handoff_count']]
        html.append('<tr>'+''.join(f'<td>{v}</td>' for v in vals)+'</tr>')
    html.append('</table>')
    for r in results:
        if r.get('status')!='ok': continue
        html.append(f"<h2>{r['ticker']} {r['metric']}</h2><p>Dominant candidates: {json.dumps(r['dominant_candidate_frequency'],ensure_ascii=False)}</p>")
        html.append('<table><tr><th>Time</th><th>Spot</th><th>Center shift</th><th>Above Δ</th><th>Below Δ</th><th>Top3</th><th>Dom strike</th><th>Handoff</th><th>Residual</th></tr>')
        for x in r['snapshots']:
            ks=['timestamp','spot','center_shift_from_j1','above_share_change_vs_j1','below_share_change_vs_j1','top3_abs_share','dominant_strike','handoff_from_prior','residual_shuffle_score']
            html.append('<tr>'+''.join(f'<td>{x.get(k,"")}</td>' for k in ks)+'</tr>')
        html.append('</table>')
    (OUT/'index.html').write_text('\n'.join(html),encoding='utf-8')
    print(json.dumps({'outputs':{'summary_csv':str(OUT/'comparison_summary.csv'),'summary_json':str(OUT/'comparison_summary.json'),'html':str(OUT/'index.html')},'results':flat},indent=2,ensure_ascii=False))

if __name__=='__main__': main()
