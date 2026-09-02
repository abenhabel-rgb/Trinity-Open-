#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review')
MANIFEST = ROOT / 'manifest.jsonl'
OUT = ROOT / 'sample_24'
SAMPLE_N = 24


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit(f'missing manifest: {MANIFEST}')

    rows = [json.loads(line) for line in MANIFEST.read_text(encoding='utf-8').splitlines() if line.strip()]
    if not rows:
        raise SystemExit('manifest is empty')

    if len(rows) <= SAMPLE_N:
        sample = rows
    else:
        idxs = sorted({round(i * (len(rows)-1) / (SAMPLE_N-1)) for i in range(SAMPLE_N)})
        sample = [rows[i] for i in idxs]

    OUT.mkdir(parents=True, exist_ok=True)

    css = '''
    body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#111;color:#eee;margin:24px}
    h1{font-size:26px}.note{color:#bbb;margin-bottom:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:20px}
    .card{background:#1b1b1b;border:1px solid #444;border-radius:10px;padding:12px}.card img{width:100%;height:auto;max-height:620px;object-fit:contain;background:#000;border-radius:6px}
    .meta{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;line-height:1.45;margin-top:9px;word-break:break-word}.n{font-size:20px;font-weight:700}.muted{color:#999}
    '''
    parts = [
        '<!doctype html><html><head><meta charset="utf-8"><title>Discord Heatseeker 2026-08-28 — 24 sample</title>',
        f'<style>{css}</style></head><body>',
        '<h1>OpenClaw — Discord Heatseeker 2026-08-28 — 24-point sample</h1>',
        '<div class="note">Evenly sampled from the 1,292 unique SHA images across the observed filename-time range. Times are preserved as observed; timezone unresolved.</div>',
        '<div class="grid">'
    ]

    for i, r in enumerate(sample, 1):
        uri = Path(r['source_path']).as_uri()
        parts += [
            '<div class="card">',
            f'<div class="n">#{i:02d} — {html.escape(r.get("filename_time_naive") or "TIME UNKNOWN")}</div>',
            f'<img src="{html.escape(uri)}" loading="lazy">',
            '<div class="meta">',
            f'<div><b>file</b>: {html.escape(r.get("basename", ""))}</div>',
            f'<div><b>sha256</b>: <span class="muted">{html.escape(r.get("sha256", ""))}</span></div>',
            '</div></div>'
        ]

    parts.append('</div></body></html>')
    index = OUT / 'index.html'
    index.write_text('\n'.join(parts), encoding='utf-8')

    sample_manifest = OUT / 'sample_manifest.json'
    sample_manifest.write_text(json.dumps(sample, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    summary = {
        'population_unique_sha': len(rows),
        'sample_images': len(sample),
        'first_sample_time': sample[0].get('filename_time_naive',''),
        'last_sample_time': sample[-1].get('filename_time_naive',''),
        'index': str(index),
        'sample_manifest': str(sample_manifest),
    }
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
