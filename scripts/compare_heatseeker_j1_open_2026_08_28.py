#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, time
from pathlib import Path

ROOT = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review/extracted')
IMAGES = ROOT / 'heatseeker_images.csv'
CELLS = ROOT / 'heatseeker_cells.csv'
OUT = ROOT / 'j1_vs_open'

J1_DATE = '2026-08-27'
J_DATE = '2026-08-28'
OPEN_START = time(9, 30, 0)
OPEN_END = time(10, 0, 0)


def dt(s: str) -> datetime | None:
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def main() -> int:
    if not IMAGES.exists() or not CELLS.exists():
        raise SystemExit('run extract_discord_heatseeker_2026_08_28.py first')
    OUT.mkdir(parents=True, exist_ok=True)

    with IMAGES.open(encoding='utf-8') as f:
        images=list(csv.DictReader(f))
    with CELLS.open(encoding='utf-8') as f:
        cells=list(csv.DictReader(f))

    img_by_sha={r['sha256']:r for r in images}
    grouped=defaultdict(list)
    for r in images:
        t=dt(r.get('internal_timestamp_naive',''))
        if not t or not r.get('ticker') or not r.get('metric'):
            continue
        grouped[(r['ticker'],r['metric'])].append((t,r))

    cell_by_sha=defaultdict(list)
    for c in cells:
        cell_by_sha[c['sha256']].append(c)

    comparisons=[]
    ticker_summaries=[]

    for key, seq in sorted(grouped.items()):
        ticker,metric=key
        seq.sort(key=lambda x:x[0])
        j1=[(t,r) for t,r in seq if t.date().isoformat()==J1_DATE]
        op=[(t,r) for t,r in seq if t.date().isoformat()==J_DATE and OPEN_START <= t.time() <= OPEN_END]
        if not j1 or not op:
            continue
        base_t,base=max(j1,key=lambda x:x[0])
        base_cells={(c['expiration'],float(c['strike'])):c for c in cell_by_sha[base['sha256']]}
        ticker_rows=0
        for cur_t,cur in op:
            cur_cells={(c['expiration'],float(c['strike'])):c for c in cell_by_sha[cur['sha256']]}
            common=sorted(set(base_cells)&set(cur_cells))
            for k in common:
                b=base_cells[k]; c=cur_cells[k]
                try:
                    bv=float(b['value']); cv=float(c['value'])
                except Exception:
                    continue
                comparisons.append({
                    'ticker':ticker,'metric':metric,
                    'j1_timestamp':base_t.isoformat(),
                    'j_timestamp':cur_t.isoformat(),
                    'j1_sha256':base['sha256'],'j_sha256':cur['sha256'],
                    'j1_spot':base.get('spot',''),'j_spot':cur.get('spot',''),
                    'expiration':k[0],'strike':k[1],
                    'j1_value':bv,'j_value':cv,'delta_value':cv-bv,
                    'data_policy':'observed_only'
                })
                ticker_rows += 1
        ticker_summaries.append({
            'ticker':ticker,'metric':metric,
            'j1_snapshot':base_t.isoformat(),
            'j1_cell_count':len(base_cells),
            'open_snapshots':len(op),
            'comparison_rows':ticker_rows,
        })

    comp_csv=OUT/'cell_deltas.csv'
    if comparisons:
        with comp_csv.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(comparisons[0])); w.writeheader(); w.writerows(comparisons)
    else:
        comp_csv.write_text('ticker,metric\n',encoding='utf-8')

    sum_csv=OUT/'ticker_summary.csv'
    if ticker_summaries:
        with sum_csv.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(ticker_summaries[0])); w.writeheader(); w.writerows(ticker_summaries)
    else:
        sum_csv.write_text('ticker,metric\n',encoding='utf-8')

    summary={
        'ticker_metric_pairs_compared':len(ticker_summaries),
        'cell_delta_rows':len(comparisons),
        'j1_rule':'latest observed internal timestamp on 2026-08-27',
        'j_open_window':'2026-08-28 09:30:00 through 10:00:00 internal timestamp',
        'out_cell_deltas':str(comp_csv),
        'out_ticker_summary':str(sum_csv),
        'note':'No missing matrix values are interpolated; only exact common expiration/strike cells are compared.'
    }
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
