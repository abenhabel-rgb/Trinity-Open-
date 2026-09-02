#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import os
import re
from collections import Counter
from pathlib import Path

SOURCE = Path('/Volumes/OPENCLAW/OpenClaw_Archives/2026-08-28/30_DATA_CAPTURES/DISCORD_HEATSEEKER_SILENT_2026-08-28/heatmaps')
OUT = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review')
EXTS = {'.png', '.jpg', '.jpeg', '.webp'}
TIME_RE = re.compile(r'2026-08-28[_-](\d{2})-(\d{2})-(\d{2})')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def parse_time(name: str) -> str:
    m = TIME_RE.search(name)
    if not m:
        return ''
    return ':'.join(m.groups())


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f'missing source folder: {SOURCE}')

    files = sorted(p for p in SOURCE.iterdir() if p.is_file() and p.suffix.lower() in EXTS)
    rows = []
    seen = set()
    dupes = 0

    for p in files:
        digest = sha256(p)
        if digest in seen:
            dupes += 1
            continue
        seen.add(digest)
        rows.append({
            'basename': p.name,
            'source_path': str(p),
            'sha256': digest,
            'bytes': p.stat().st_size,
            'filename_time_naive': parse_time(p.name),
            'timezone_status': 'unresolved',
            'data_policy': 'observed_only',
        })

    rows.sort(key=lambda r: (r['filename_time_naive'] or '99:99:99', r['basename']))
    OUT.mkdir(parents=True, exist_ok=True)

    manifest = OUT / 'manifest.jsonl'
    with manifest.open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n')

    css = '''
    body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#111;color:#eee;margin:24px}
    h1{font-size:26px}.note{color:#bbb;margin-bottom:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:20px}
    .card{background:#1b1b1b;border:1px solid #444;border-radius:10px;padding:12px}.card img{width:100%;height:auto;max-height:620px;object-fit:contain;background:#000;border-radius:6px}
    .meta{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;line-height:1.45;margin-top:9px;word-break:break-word}.n{font-size:20px;font-weight:700}.muted{color:#999}
    '''
    parts = [
        '<!doctype html><html><head><meta charset="utf-8"><title>Discord Heatseeker 2026-08-28</title>',
        f'<style>{css}</style></head><body>',
        '<h1>OpenClaw — Discord Heatseeker — 2026-08-28</h1>',
        '<div class="note">Exact archive folder only. Deduplicated by SHA-256. Filename times are preserved as observed and are not assumed to be ET.</div>',
        '<div class="grid">',
    ]
    for i, r in enumerate(rows, 1):
        uri = Path(r['source_path']).as_uri()
        parts += [
            '<div class="card">',
            f'<div class="n">#{i:03d} — {html.escape(r["filename_time_naive"] or "TIME UNKNOWN")}</div>',
            f'<img src="{html.escape(uri)}" loading="lazy">',
            '<div class="meta">',
            f'<div><b>file</b>: {html.escape(r["basename"])}</div>',
            f'<div><b>sha256</b>: <span class="muted">{html.escape(r["sha256"])}</span></div>',
            '</div></div>'
        ]
    parts.append('</div></body></html>')
    index = OUT / 'index.html'
    index.write_text('\n'.join(parts), encoding='utf-8')

    time_counts = Counter(r['filename_time_naive'] for r in rows if r['filename_time_naive'])
    summary = {
        'source_folder': str(SOURCE),
        'files_found': len(files),
        'unique_sha': len(rows),
        'duplicate_files': dupes,
        'with_filename_time': sum(bool(r['filename_time_naive']) for r in rows),
        'distinct_filename_times': len(time_counts),
        'first_time': min(time_counts) if time_counts else '',
        'last_time': max(time_counts) if time_counts else '',
        'index': str(index),
        'manifest': str(manifest),
    }
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
