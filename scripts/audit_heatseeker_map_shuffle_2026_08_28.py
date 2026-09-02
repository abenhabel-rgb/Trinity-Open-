#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review/extracted/j1_vs_open/structure_summary')
PAIR = ROOT / 'ticker_metric_structure.csv'
SNAP_JSON = ROOT / 'snapshot_structure.json'
OUT = ROOT / 'map_shuffle_audit'


def fnum(v):
    try:
        return float(v)
    except Exception:
        return None


def classify(relative_change: float | None, spot_change_pct: float | None) -> str:
    if relative_change is None or spot_change_pct is None:
        return 'insufficient'
    a = abs(spot_change_pct)
    # OpenClaw diagnostic labels only. They are not Skylit categories.
    if relative_change >= 0.70 and a <= 0.50:
        return 'structure_dominant_candidate'
    if relative_change >= 0.70 and a >= 2.00:
        return 'spot_coupled_candidate'
    if relative_change >= 0.70:
        return 'mixed_candidate'
    return 'lower_shuffle'


def main() -> int:
    if not PAIR.exists() or not SNAP_JSON.exists():
        raise SystemExit('run summarize_heatseeker_structure_2026_08_28.py first')
    OUT.mkdir(parents=True, exist_ok=True)

    with PAIR.open(encoding='utf-8') as f:
        pairs = list(csv.DictReader(f))
    snapshots = json.loads(SNAP_JSON.read_text(encoding='utf-8'))

    ranked = [r for r in pairs if str(r.get('relative_change_rank','')).strip()]
    ranked.sort(key=lambda r: int(r['relative_change_rank']))
    selected = ranked[:10]

    by_key_time = {(r['ticker'], r['metric'], r['j_timestamp']): r for r in snapshots}
    audit=[]
    for p in selected:
        rel = fnum(p.get('max_relative_l1_change'))
        spot = fnum(p.get('last_spot_change_pct'))
        peak_ts = p.get('max_relative_l1_timestamp','')
        snap = by_key_time.get((p['ticker'], p['metric'], peak_ts), {})
        audit.append({
            'rank': int(p['relative_change_rank']),
            'ticker': p['ticker'],
            'metric': p['metric'],
            'peak_timestamp': peak_ts,
            'max_relative_l1_change': rel,
            'spot_change_pct': spot,
            'openclaw_driver_label': classify(rel, spot),
            'common_cells_at_peak': snap.get('common_cells'),
            'sign_flip_ratio_at_peak': snap.get('sign_flip_ratio'),
            'signed_sum_delta_at_peak': snap.get('signed_sum_delta'),
            'j1_spot': snap.get('j1_spot'),
            'j_spot': snap.get('j_spot'),
            'top_abs_delta_cells': snap.get('top_abs_delta_cells', []),
            'data_policy': 'observed_only_common_cells',
        })

    out_json = OUT / 'top10_map_shuffle_audit.json'
    out_json.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    out_csv = OUT / 'top10_map_shuffle_audit.csv'
    fields = ['rank','ticker','metric','peak_timestamp','max_relative_l1_change','spot_change_pct',
              'openclaw_driver_label','common_cells_at_peak','sign_flip_ratio_at_peak',
              'signed_sum_delta_at_peak','j1_spot','j_spot','data_policy']
    with out_csv.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in audit:
            w.writerow({k:r.get(k) for k in fields})

    summary = {
        'pairs_audited': len(audit),
        'labels': {
            'structure_dominant_candidate': sum(r['openclaw_driver_label']=='structure_dominant_candidate' for r in audit),
            'mixed_candidate': sum(r['openclaw_driver_label']=='mixed_candidate' for r in audit),
            'spot_coupled_candidate': sum(r['openclaw_driver_label']=='spot_coupled_candidate' for r in audit),
            'lower_shuffle': sum(r['openclaw_driver_label']=='lower_shuffle' for r in audit),
        },
        'important_note': 'Labels are OpenClaw diagnostics, not confirmed Skylit/Heatseeker metrics.',
        'top10': [{k:r[k] for k in ['rank','ticker','metric','peak_timestamp','max_relative_l1_change','spot_change_pct','openclaw_driver_label','common_cells_at_peak','sign_flip_ratio_at_peak']} for r in audit],
        'output_json': str(out_json),
        'output_csv': str(out_csv),
    }
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
