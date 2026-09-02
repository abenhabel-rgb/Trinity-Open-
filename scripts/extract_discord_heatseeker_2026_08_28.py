#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

# Allow execution directly from a fresh git checkout without installing the
# package first. Resolve the repository path from this script itself rather
# than assuming /tmp/Trinity-Open-.
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trinity.heatseeker_matrix_parser import parse_capture_filename_time, parse_ocr_result, seconds_between_naive

ROOT = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review')
MANIFEST = ROOT / 'manifest.jsonl'
CACHE = ROOT / 'ocr_cache'
OUT = ROOT / 'extracted'
SWIFT = REPO_ROOT / 'scripts' / 'heatseeker_ocr.swift'


def run_ocr(image: str, cache_path: Path) -> dict:
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding='utf-8'))
    proc = subprocess.run(['swift', str(SWIFT), image], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f'OCR failed for {image}')
    payload = json.loads(proc.stdout)
    cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    return payload


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit(f'missing manifest: {MANIFEST}')
    rows = [json.loads(line) for line in MANIFEST.read_text(encoding='utf-8').splitlines() if line.strip()]
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    image_rows=[]
    cell_rows=[]
    status_counts={}

    total=len(rows)
    for i,row in enumerate(rows,1):
        sha=row['sha256']
        cache=CACHE/f'{sha}.json'
        try:
            ocr=run_ocr(row['source_path'], cache)
            parsed=parse_ocr_result(ocr)
            error=''
        except Exception as exc:
            parsed={'parse_status':'error','footer':None,'expirations':[],'strikes':[],'cells':[],
                    'quality':{'expiration_count':0,'strike_count':0,'cell_count':0,'possible_cells':0,'cell_fill_ratio':0.0,'mean_cell_confidence':0.0},
                    'ocr_line_count':0,'data_policy':'observed_only'}
            error=str(exc)

        footer=parsed.get('footer') or {}
        capture_local=parse_capture_filename_time(row['basename'])
        internal=footer.get('internal_timestamp','')
        offset=seconds_between_naive(capture_local, internal)
        q=parsed['quality']
        img={
            'sha256':sha,
            'basename':row['basename'],
            'source_path':row['source_path'],
            'capture_filename_timestamp_naive':capture_local,
            'ticker':footer.get('ticker',''),
            'metric':footer.get('metric',''),
            'internal_timestamp_naive':internal,
            'spot':footer.get('spot',''),
            'capture_minus_internal_seconds': '' if offset is None else int(offset),
            'parse_status':parsed['parse_status'],
            'expiration_count':q.get('expiration_count',0),
            'strike_count':q.get('strike_count',0),
            'cell_count':q.get('cell_count',0),
            'possible_cells':q.get('possible_cells',0),
            'cell_fill_ratio':q.get('cell_fill_ratio',0.0),
            'mean_cell_confidence':q.get('mean_cell_confidence',0.0),
            'ocr_line_count':parsed.get('ocr_line_count',0),
            'error':error,
            'data_policy':'observed_only',
        }
        image_rows.append(img)
        status_counts[img['parse_status']]=status_counts.get(img['parse_status'],0)+1

        for cell in parsed.get('cells',[]):
            cell_rows.append({
                'sha256':sha,
                'basename':row['basename'],
                'ticker':img['ticker'],
                'metric':img['metric'],
                'internal_timestamp_naive':img['internal_timestamp_naive'],
                'spot':img['spot'],
                'expiration':cell['expiration'],
                'strike':cell['strike'],
                'value':cell['value'],
                'raw_text':cell['raw_text'],
                'ocr_confidence':cell['confidence'],
                'data_policy':'observed_only',
            })

        if i == 1 or i % 25 == 0 or i == total:
            print(f'[OpenClaw] {i}/{total} {row["basename"]} -> {img["parse_status"]} cells={img["cell_count"]}', flush=True)

    img_csv=OUT/'heatseeker_images.csv'
    fields=list(image_rows[0].keys()) if image_rows else []
    with img_csv.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(image_rows)

    cell_csv=OUT/'heatseeker_cells.csv'
    cfields=list(cell_rows[0].keys()) if cell_rows else ['sha256']
    with cell_csv.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cfields); w.writeheader(); w.writerows(cell_rows)

    parsed_offsets=[r['capture_minus_internal_seconds'] for r in image_rows if isinstance(r['capture_minus_internal_seconds'],int)]
    summary={
        'images_total':len(image_rows),
        'status_counts':status_counts,
        'cells_total':len(cell_rows),
        'footer_parsed':sum(bool(r['ticker'] and r['metric'] and r['internal_timestamp_naive']) for r in image_rows),
        'matrix_parsed':sum(r['parse_status']=='parsed_matrix' for r in image_rows),
        'offset_observations':len(parsed_offsets),
        'offset_seconds_median': sorted(parsed_offsets)[len(parsed_offsets)//2] if parsed_offsets else None,
        'output_images_csv':str(img_csv),
        'output_cells_csv':str(cell_csv),
        'ocr_cache':str(CACHE),
    }
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
