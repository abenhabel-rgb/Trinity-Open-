#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import os
import shutil
from pathlib import Path

ROOT = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/heatseeker_observed_2026-08-24')
CLASSIFICATION = ROOT / 'candidate_classification.csv'
REVIEW = ROOT / 'visual_review'


def main() -> int:
    if not CLASSIFICATION.exists():
        raise SystemExit(f'missing classification file: {CLASSIFICATION}')

    with CLASSIFICATION.open(encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r.get('classification') == 'review_required']

    if REVIEW.exists():
        shutil.rmtree(REVIEW)
    REVIEW.mkdir(parents=True, exist_ok=True)

    cards=[]
    for i,row in enumerate(rows,1):
        src=Path(row['source_path'])
        ext=src.suffix.lower() or '.img'
        local_name=f'{i:02d}{ext}'
        local=REVIEW/local_name
        try:
            os.symlink(src, local)
        except OSError:
            shutil.copy2(src, local)

        cards.append({
            'n':i,
            'image':local_name,
            'basename':row.get('basename',''),
            'filename_time':row.get('filename_time_naive',''),
            'visible_time':row.get('visible_time_candidates',''),
            'tickers':row.get('ticker_candidates',''),
            'sha256':row.get('sha256',''),
        })

    css='''
    body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#111;color:#eee;margin:24px}
    h1{font-size:26px}.note{color:#bbb;margin-bottom:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:22px}
    .card{background:#1b1b1b;border:1px solid #444;border-radius:10px;padding:12px}.card img{width:100%;height:auto;max-height:520px;object-fit:contain;background:#000;border-radius:6px}
    .meta{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;line-height:1.5;margin-top:10px;word-break:break-word}.n{font-size:20px;font-weight:700}.muted{color:#aaa}
    '''
    parts=[f'<!doctype html><html><head><meta charset="utf-8"><title>OpenClaw Heatseeker Review 2026-08-24</title><style>{css}</style></head><body>',
           '<h1>OpenClaw — Heatseeker visual review — 2026-08-24</h1>',
           '<div class="note">Only images that survived the negative-only filter are shown. Presence here does not confirm Heatseeker.</div>',
           '<div class="grid">']
    for c in cards:
        parts.append('<div class="card">')
        parts.append(f'<div class="n">#{c["n"]:02d}</div>')
        parts.append(f'<img src="{html.escape(c["image"])}" loading="lazy">')
        parts.append('<div class="meta">')
        parts.append(f'<div><b>file</b>: {html.escape(c["basename"])}</div>')
        parts.append(f'<div><b>filename time</b>: {html.escape(c["filename_time"] or "—")}</div>')
        parts.append(f'<div><b>visible time candidates</b>: {html.escape(c["visible_time"] or "—")}</div>')
        parts.append(f'<div><b>ticker candidates</b>: {html.escape(c["tickers"] or "—")}</div>')
        parts.append(f'<div class="muted"><b>sha256</b>: {html.escape(c["sha256"])}</div>')
        parts.append('</div></div>')
    parts.append('</div></body></html>')

    index=REVIEW/'index.html'
    index.write_text('\n'.join(parts), encoding='utf-8')
    (REVIEW/'review_manifest.json').write_text(json.dumps(cards,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'review_images':len(cards),'index':str(index)},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
