#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review/extracted/j1_vs_open')
DELTAS = ROOT / 'cell_deltas.csv'
OUT = ROOT / 'structure_summary'


def fnum(x: str) -> float | None:
    try:
        return float(x)
    except Exception:
        return None


def snapshot_stats(rows: list[dict]) -> dict:
    valid=[]
    for r in rows:
        b=fnum(r.get('j1_value',''))
        c=fnum(r.get('j_value',''))
        d=fnum(r.get('delta_value',''))
        if b is None or c is None or d is None:
            continue
        valid.append((r,b,c,d))

    n=len(valid)
    abs_base=sum(abs(b) for _,b,_,_ in valid)
    abs_cur=sum(abs(c) for _,_,c,_ in valid)
    abs_delta=sum(abs(d) for *_,d in valid)
    signed_base=sum(b for _,b,_,_ in valid)
    signed_cur=sum(c for _,_,c,_ in valid)
    signed_delta=sum(d for *_,d in valid)
    flips=sum(1 for _,b,c,_ in valid if b*c < 0)
    zero_to_nonzero=sum(1 for _,b,c,_ in valid if b == 0 and c != 0)
    nonzero_to_zero=sum(1 for _,b,c,_ in valid if b != 0 and c == 0)

    largest=sorted(valid,key=lambda x:abs(x[3]),reverse=True)[:10]
    top_cells=[{
        'expiration':r['expiration'],
        'strike':float(r['strike']),
        'j1_value':b,
        'j_value':c,
        'delta_value':d,
    } for r,b,c,d in largest]

    j1_spot=fnum(rows[0].get('j1_spot','')) if rows else None
    j_spot=fnum(rows[0].get('j_spot','')) if rows else None
    spot_pct=((j_spot/j1_spot)-1.0)*100.0 if j1_spot not in (None,0) and j_spot is not None else None

    return {
        'common_cells':n,
        'sum_abs_j1_common':abs_base,
        'sum_abs_j_common':abs_cur,
        'sum_abs_delta':abs_delta,
        'relative_l1_change':(abs_delta/abs_base) if abs_base else None,
        'signed_sum_j1_common':signed_base,
        'signed_sum_j_common':signed_cur,
        'signed_sum_delta':signed_delta,
        'sign_flips':flips,
        'sign_flip_ratio':(flips/n) if n else None,
        'zero_to_nonzero':zero_to_nonzero,
        'nonzero_to_zero':nonzero_to_zero,
        'j1_spot':j1_spot,
        'j_spot':j_spot,
        'spot_change_pct':spot_pct,
        'top_abs_delta_cells':top_cells,
    }


def main() -> int:
    if not DELTAS.exists():
        raise SystemExit(f'missing {DELTAS}; run compare_heatseeker_j1_open_2026_08_28.py first')
    OUT.mkdir(parents=True, exist_ok=True)

    with DELTAS.open(encoding='utf-8') as f:
        rows=list(csv.DictReader(f))

    by_snapshot=defaultdict(list)
    for r in rows:
        key=(r['ticker'],r['metric'],r['j1_timestamp'],r['j_timestamp'])
        by_snapshot[key].append(r)

    snap_rows=[]
    snap_json=[]
    for key,group in sorted(by_snapshot.items()):
        ticker,metric,j1_ts,j_ts=key
        s=snapshot_stats(group)
        flat={
            'ticker':ticker,'metric':metric,'j1_timestamp':j1_ts,'j_timestamp':j_ts,
            **{k:v for k,v in s.items() if k != 'top_abs_delta_cells'},
        }
        snap_rows.append(flat)
        snap_json.append({**flat,'top_abs_delta_cells':s['top_abs_delta_cells']})

    snap_csv=OUT/'snapshot_structure.csv'
    fields=list(snap_rows[0].keys()) if snap_rows else ['ticker','metric']
    with snap_csv.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(snap_rows)
    (OUT/'snapshot_structure.json').write_text(json.dumps(snap_json,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

    by_pair=defaultdict(list)
    for r in snap_rows:
        by_pair[(r['ticker'],r['metric'])].append(r)

    pair_rows=[]
    for (ticker,metric),seq in sorted(by_pair.items()):
        seq.sort(key=lambda r:r['j_timestamp'])
        last=seq[-1]
        max_rel=max((r for r in seq if r['relative_l1_change'] is not None), key=lambda r:r['relative_l1_change'], default=None)
        max_flip=max((r for r in seq if r['sign_flip_ratio'] is not None), key=lambda r:r['sign_flip_ratio'], default=None)
        pair_rows.append({
            'ticker':ticker,
            'metric':metric,
            'j1_snapshot':last['j1_timestamp'],
            'open_snapshots_compared':len(seq),
            'last_open_snapshot':last['j_timestamp'],
            'last_common_cells':last['common_cells'],
            'last_relative_l1_change':last['relative_l1_change'],
            'last_sign_flip_ratio':last['sign_flip_ratio'],
            'last_signed_sum_delta':last['signed_sum_delta'],
            'last_spot_change_pct':last['spot_change_pct'],
            'max_relative_l1_change':max_rel['relative_l1_change'] if max_rel else None,
            'max_relative_l1_timestamp':max_rel['j_timestamp'] if max_rel else '',
            'max_sign_flip_ratio':max_flip['sign_flip_ratio'] if max_flip else None,
            'max_sign_flip_timestamp':max_flip['j_timestamp'] if max_flip else '',
            'data_policy':'observed_only_common_cells',
        })

    # Ranking is based on a dimensionless statistic. We intentionally do not
    # rank different tickers by raw dollar GEX/VEX deltas because scales differ.
    ranked=sorted(
        [r for r in pair_rows if r['max_relative_l1_change'] is not None],
        key=lambda r:r['max_relative_l1_change'],reverse=True
    )
    for rank,r in enumerate(ranked,1):
        r['relative_change_rank']=rank
    for r in pair_rows:
        r.setdefault('relative_change_rank','')

    pair_csv=OUT/'ticker_metric_structure.csv'
    pfields=list(pair_rows[0].keys()) if pair_rows else ['ticker','metric']
    with pair_csv.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=pfields); w.writeheader(); w.writerows(pair_rows)

    top=ranked[:25]
    top_csv=OUT/'top25_relative_structure_change.csv'
    with top_csv.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=pfields); w.writeheader(); w.writerows(top)

    summary={
        'cell_delta_rows':len(rows),
        'snapshot_comparisons':len(snap_rows),
        'ticker_metric_pairs':len(pair_rows),
        'ranking_metric':'max relative L1 change = sum(|J-J1|) / sum(|J1|) over exact common cells',
        'raw_cross_ticker_ranking_used':False,
        'outputs':{
            'snapshot_csv':str(snap_csv),
            'snapshot_json':str(OUT/'snapshot_structure.json'),
            'pair_csv':str(pair_csv),
            'top25_csv':str(top_csv),
        },
        'top10_relative_change':[
            {
                'rank':r['relative_change_rank'],
                'ticker':r['ticker'],
                'metric':r['metric'],
                'max_relative_l1_change':r['max_relative_l1_change'],
                'timestamp':r['max_relative_l1_timestamp'],
                'last_spot_change_pct':r['last_spot_change_pct'],
            }
            for r in top[:10]
        ],
        'note':'All summaries use only exact expiration/strike cells present in both J-1 and J snapshots. No missing values are filled or interpolated.'
    }
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
