#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

SOURCE = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/heatseeker_source_manifest.csv')
OUTDIR = Path('/Volumes/OPENCLAW/OpenClaw_Metadata')
EXCLUDE_BASENAMES = {'heatseeker-trinity.webp', 'heatseeker-swing.webp'}


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f'missing source manifest: {SOURCE}')

    with SOURCE.open(encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))

    session_rows = [
        r for r in rows
        if r.get('basename') not in EXCLUDE_BASENAMES and r.get('path_date')
    ]

    for r in session_rows:
        r['session_date'] = r.get('path_date', '')
        r['session_time_naive'] = ''
        ts = r.get('filename_timestamp_naive', '')
        if ts and 'T' in ts:
            r['session_time_naive'] = ts.split('T', 1)[1]
        r['time_status'] = 'explicit_filename_time' if r['session_time_naive'] else 'unresolved'
        r['timezone_status'] = 'unresolved'

    session_rows.sort(
        key=lambda r: (
            r['session_date'],
            r['session_time_naive'] or '99:99:99',
            r.get('basename', ''),
            r.get('sha256', ''),
        )
    )

    fields = [
        'session_date', 'session_time_naive', 'time_status', 'timezone_status',
        'basename', 'sha256', 'source_path', 'bytes', 'mtime_utc',
        'filename_timestamp_naive', 'path_date', 'data_policy'
    ]

    csv_path = OUTDIR / 'heatseeker_chronology.csv'
    jsonl_path = OUTDIR / 'heatseeker_chronology.jsonl'
    summary_path = OUTDIR / 'heatseeker_chronology_summary.json'

    with csv_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in session_rows:
            writer.writerow({k: row.get(k, '') for k in fields})

    with jsonl_path.open('w', encoding='utf-8') as handle:
        for row in session_rows:
            handle.write(json.dumps({k: row.get(k, '') for k in fields}, ensure_ascii=False, separators=(',', ':')) + '\n')

    by_date = Counter(r['session_date'] for r in session_rows)
    summary = {
        'session_images': len(session_rows),
        'dates': len(by_date),
        'with_explicit_filename_time': sum(r['time_status'] == 'explicit_filename_time' for r in session_rows),
        'with_unresolved_time': sum(r['time_status'] == 'unresolved' for r in session_rows),
        'timezone_resolved': 0,
        'images_per_date': dict(sorted(by_date.items())),
        'output_csv': str(csv_path),
        'output_jsonl': str(jsonl_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
