#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

DATE = '2026-08-24'
OBSERVED = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/heatseeker_observed_2026-08-24/heatseeker_observed.jsonl')
OUTDIR = OBSERVED.parent

# Negative-only classification. These rules can reject an image as an obvious
# broker/trade/account screen. They NEVER confirm an image as Heatseeker.
STRONG_RULES = {
    'trade_closed_summary': re.compile(r'\bclosed on\b', re.I),
    'cost_at_open': re.compile(r'\bcost at open\b', re.I),
    'sell_to_close': re.compile(r'\bsell to close\b', re.I),
    'buy_to_open': re.compile(r'\bbuy to open\b', re.I),
    'filled_at': re.compile(r'\bfilled at\b', re.I),
    'contract_trade_summary': re.compile(r'\b(?:contract|contracts)\b.*\b(?:avg|cost|filled|open|close)\b', re.I),
    'option_exercise': re.compile(r'\bexercise\b', re.I),
}

MEDIUM_RULES = {
    'index_options': re.compile(r'\bindex options\b', re.I),
    'history_screen': re.compile(r'\bhistory\b', re.I),
    'open_market_columns': re.compile(r'\bopen mkt\b', re.I),
    'filters_columns': re.compile(r'\bfilters\b.*\bcolumns\b|\bcolumns\b.*\bfilters\b', re.I),
    'overview_screen': re.compile(r'\boverview\b', re.I),
    'view_spx': re.compile(r'\bview spx\b', re.I),
}


def load_rows() -> list[dict]:
    if not OBSERVED.exists():
        raise SystemExit(f'missing observed OCR file: {OBSERVED}')
    rows=[]
    for line in OBSERVED.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        obj=json.loads(line)
        if obj.get('session_date') == DATE:
            rows.append(obj)
    return rows


def classify(row: dict) -> dict:
    text='\n'.join(str(x) for x in row.get('raw_text', []) if str(x).strip())
    strong=[name for name,rx in STRONG_RULES.items() if rx.search(text)]
    medium=[name for name,rx in MEDIUM_RULES.items() if rx.search(text)]

    if strong:
        state='non_heatseeker_obvious'
        confidence='high'
        reasons=strong+medium
    elif len(medium) >= 2:
        state='non_heatseeker_obvious'
        confidence='medium'
        reasons=medium
    else:
        state='review_required'
        confidence='unresolved'
        reasons=medium

    return {
        'session_date': row.get('session_date',''),
        'basename': row.get('basename',''),
        'sha256': row.get('sha256',''),
        'source_path': row.get('source_path',''),
        'classification': state,
        'classification_confidence': confidence,
        'negative_evidence': reasons,
        'filename_time_naive': row.get('filename_time_naive',''),
        'visible_time_candidates': row.get('visible_time_candidates',[]),
        'ticker_candidates': row.get('ticker_candidates',[]),
        'data_policy': 'observed_only',
        'note': 'negative-only classifier; review_required does not mean Heatseeker confirmed',
    }


def main() -> int:
    rows=load_rows()
    classified=[classify(r) for r in rows]
    classified.sort(key=lambda r:r['basename'])

    jsonl=OUTDIR/'candidate_classification.jsonl'
    with jsonl.open('w',encoding='utf-8') as f:
        for r in classified:
            f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')

    csvp=OUTDIR/'candidate_classification.csv'
    fields=['session_date','basename','sha256','classification','classification_confidence',
            'negative_evidence','filename_time_naive','visible_time_candidates','ticker_candidates',
            'source_path','data_policy','note']
    with csvp.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in classified:
            out={k:r.get(k,'') for k in fields}
            for k in ['negative_evidence','visible_time_candidates','ticker_candidates']:
                out[k]=json.dumps(out[k],ensure_ascii=False)
            w.writerow(out)

    rejected=[r for r in classified if r['classification']=='non_heatseeker_obvious']
    review=[r for r in classified if r['classification']=='review_required']
    summary={
        'date': DATE,
        'candidates_examined': len(classified),
        'non_heatseeker_obvious': len(rejected),
        'review_required': len(review),
        'heatseeker_confirmed_automatically': 0,
        'rejected_files': [
            {'basename':r['basename'],'confidence':r['classification_confidence'],'reasons':r['negative_evidence']}
            for r in rejected
        ],
        'review_files':[r['basename'] for r in review],
        'output_csv':str(csvp),
        'output_jsonl':str(jsonl),
    }
    (OUTDIR/'candidate_classification_summary.json').write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
