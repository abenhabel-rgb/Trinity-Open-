#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path

SOURCE = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/heatseeker_chronology.csv')
OUTDIR = Path('/Volumes/OPENCLAW/OpenClaw_Metadata')

MDLS_KEYS = [
    'kMDItemContentCreationDate',
    'kMDItemFSCreationDate',
    'kMDItemFSContentChangeDate',
]


def parse_mdls_value(text: str) -> str:
    text = text.strip()
    if text == '(null)' or not text:
        return ''
    return text


def parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S %z')
    except ValueError:
        return None


def mdls(path: str) -> dict[str, str]:
    cmd = ['mdls']
    for key in MDLS_KEYS:
        cmd += ['-name', key]
    cmd.append(path)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {'mdls_error': proc.stderr.strip() or f'exit_{proc.returncode}'}

    out: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if ' = ' not in line:
            continue
        key, value = line.split(' = ', 1)
        out[key.strip()] = parse_mdls_value(value)
    return out


def classify(content: datetime | None, fscreate: datetime | None) -> tuple[str, float | None]:
    if content is None or fscreate is None:
        return 'insufficient_metadata', None
    delta = (fscreate - content).total_seconds()
    # Same-second/minute metadata strongly suggests one import/copy event.
    if abs(delta) <= 300:
        return 'probable_import_metadata', delta
    # Content date materially predates file-system creation: candidate original metadata.
    if delta > 300:
        return 'candidate_original_metadata', delta
    # Content date later than fs creation is internally inconsistent for our purpose.
    return 'metadata_inconsistent', delta


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f'missing chronology: {SOURCE}')

    with SOURCE.open(encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))

    audited = []
    for row in rows:
        meta = mdls(row['source_path'])
        content_raw = meta.get('kMDItemContentCreationDate', '')
        fscreate_raw = meta.get('kMDItemFSCreationDate', '')
        fschange_raw = meta.get('kMDItemFSContentChangeDate', '')
        content_dt = parse_dt(content_raw)
        fscreate_dt = parse_dt(fscreate_raw)
        classification, delta_seconds = classify(content_dt, fscreate_dt)

        audited.append({
            'session_date': row.get('session_date', ''),
            'basename': row.get('basename', ''),
            'sha256': row.get('sha256', ''),
            'source_path': row.get('source_path', ''),
            'filename_timestamp_naive': row.get('filename_timestamp_naive', ''),
            'content_creation_date_raw': content_raw,
            'fs_creation_date_raw': fscreate_raw,
            'fs_content_change_date_raw': fschange_raw,
            'content_vs_fscreate_seconds': '' if delta_seconds is None else int(delta_seconds),
            'metadata_classification': classification,
            'timezone_status': 'unresolved',
            'data_policy': 'observed_only',
            'mdls_error': meta.get('mdls_error', ''),
        })

    audited.sort(key=lambda r: (r['session_date'], r['basename'], r['sha256']))

    csv_path = OUTDIR / 'heatseeker_metadata_audit.csv'
    jsonl_path = OUTDIR / 'heatseeker_metadata_audit.jsonl'
    summary_path = OUTDIR / 'heatseeker_metadata_audit_summary.json'

    fields = list(audited[0].keys()) if audited else ['session_date']
    with csv_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(audited)

    with jsonl_path.open('w', encoding='utf-8') as handle:
        for row in audited:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')

    counts: dict[str, int] = {}
    for row in audited:
        counts[row['metadata_classification']] = counts.get(row['metadata_classification'], 0) + 1

    candidates = [r for r in audited if r['metadata_classification'] == 'candidate_original_metadata']
    summary = {
        'images_audited': len(audited),
        'classifications': counts,
        'candidate_original_metadata': len(candidates),
        'candidate_files': [
            {
                'session_date': r['session_date'],
                'basename': r['basename'],
                'content_creation_date_raw': r['content_creation_date_raw'],
                'fs_creation_date_raw': r['fs_creation_date_raw'],
            }
            for r in candidates
        ],
        'output_csv': str(csv_path),
        'output_jsonl': str(jsonl_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
