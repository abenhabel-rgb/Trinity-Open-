#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path

DATE = '2026-08-24'
CHRONOLOGY = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/heatseeker_chronology.csv')
OUTDIR = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/heatseeker_observed_2026-08-24')
SWIFT = Path(__file__).with_name('heatseeker_ocr.swift')

TIME_RE = re.compile(r'\b(?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?\b')
PRICE_RE = re.compile(r'\b\d{2,5}(?:\.\d{1,4})?\b')
TICKER_RE = re.compile(r'\$?\b[A-Z]{1,6}\b')

LABELS = {
    'king': re.compile(r'\bking\b', re.I),
    'gatekeeper': re.compile(r'\bgate\s*keeper\b|\bgatekeeper\b', re.I),
    'pika': re.compile(r'\bpika\b', re.I),
    'barney': re.compile(r'\bbarney\b', re.I),
    'gex': re.compile(r'\bgex\b|gamma', re.I),
    'vex': re.compile(r'\bvex\b|vanna', re.I),
    'volume_spike': re.compile(r'volume\s*spike|vol(?:ume)?\s*spike', re.I),
}

STOPWORDS = {
    'AM','PM','USD','CALL','PUT','GEX','VEX','SPOT','KING','GATEKEEPER','GATE','HEATSEEKER',
    'OPEN','CLOSE','HIGH','LOW','VOL','VOLUME','GAMMA','VANNA','DELTA','THETA','IV','OI'
}


def run_ocr(path: str) -> dict:
    proc = subprocess.run(['swift', str(SWIFT), path], capture_output=True, text=True)
    if proc.returncode != 0:
        return {'image_path': path, 'lines': [], 'error': proc.stderr.strip()}
    return json.loads(proc.stdout)


def dedupe(items):
    out=[]; seen=set()
    for x in items:
        if x not in seen:
            seen.add(x); out.append(x)
    return out


def extract(ocr: dict, row: dict) -> dict:
    lines = ocr.get('lines', [])
    texts = [str(x.get('text','')).strip() for x in lines if str(x.get('text','')).strip()]
    joined = '\n'.join(texts)

    times = dedupe(TIME_RE.findall(joined))
    labels = [name for name, rx in LABELS.items() if rx.search(joined)]

    ticker_candidates=[]
    for text in texts[:12]:
        for token in TICKER_RE.findall(text):
            token=token.lstrip('$').upper()
            if token not in STOPWORDS and not token.isdigit():
                ticker_candidates.append(token)
    ticker_candidates=dedupe(ticker_candidates)

    numeric_candidates=[]
    for text in texts:
        numeric_candidates.extend(PRICE_RE.findall(text))
    numeric_candidates=dedupe(numeric_candidates)

    explicit_filename_time = row.get('session_time_naive','')
    status = 'ocr_text_detected' if texts else 'unresolved'

    return {
        'session_date': row.get('session_date',''),
        'basename': row.get('basename',''),
        'sha256': row.get('sha256',''),
        'source_path': row.get('source_path',''),
        'filename_time_naive': explicit_filename_time,
        'timezone_status': 'unresolved',
        'ocr_status': status,
        'ocr_line_count': len(texts),
        'visible_time_candidates': times,
        'ticker_candidates': ticker_candidates,
        'heatseeker_labels_observed': labels,
        'numeric_candidates': numeric_candidates,
        'raw_text': texts,
        'data_policy': 'observed_only',
        'review_required': True,
        'ocr_error': ocr.get('error',''),
    }


def main() -> int:
    if not CHRONOLOGY.exists():
        raise SystemExit(f'missing chronology: {CHRONOLOGY}')
    if not SWIFT.exists():
        raise SystemExit(f'missing OCR helper: {SWIFT}')

    with CHRONOLOGY.open(encoding='utf-8') as f:
        rows=[r for r in csv.DictReader(f) if r.get('session_date') == DATE]

    OUTDIR.mkdir(parents=True, exist_ok=True)
    results=[]
    for i,row in enumerate(rows,1):
        print(f'[OpenClaw] OCR {i}/{len(rows)} {row["basename"]}', flush=True)
        ocr=run_ocr(row['source_path'])
        result=extract(ocr,row)
        results.append(result)
        (OUTDIR/f'{i:02d}_{Path(row["basename"]).stem}.json').write_text(
            json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

    jsonl=OUTDIR/'heatseeker_observed.jsonl'
    with jsonl.open('w',encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False, separators=(',',':'))+'\n')

    review=OUTDIR/'review_queue.csv'
    fields=['session_date','basename','sha256','filename_time_naive','ocr_status','ocr_line_count',
            'visible_time_candidates','ticker_candidates','heatseeker_labels_observed','source_path']
    with review.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in results:
            row={k:r.get(k,'') for k in fields}
            for k in ['visible_time_candidates','ticker_candidates','heatseeker_labels_observed']:
                row[k]=json.dumps(row[k],ensure_ascii=False)
            w.writerow(row)

    summary={
        'images': len(results),
        'ocr_text_detected': sum(r['ocr_status']=='ocr_text_detected' for r in results),
        'with_visible_time_candidate': sum(bool(r['visible_time_candidates']) for r in results),
        'with_ticker_candidate': sum(bool(r['ticker_candidates']) for r in results),
        'with_heatseeker_label': sum(bool(r['heatseeker_labels_observed']) for r in results),
        'review_required': len(results),
        'output_dir': str(OUTDIR),
    }
    (OUTDIR/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
