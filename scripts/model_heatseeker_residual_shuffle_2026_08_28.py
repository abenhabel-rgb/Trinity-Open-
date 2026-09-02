#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review/extracted/j1_vs_open/structure_summary')
SNAP_JSON = ROOT / 'snapshot_structure.json'
OUT = ROOT / 'residual_shuffle_model'


def fnum(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except Exception:
        return None


def weighted_linear_fit(points):
    """Fit y = a + b*x using positive weights.

    Returns (a, b). Falls back to a weighted mean if x has no variance.
    """
    pts = [(x, y, w) for x, y, w in points if w > 0 and math.isfinite(x) and math.isfinite(y)]
    if not pts:
        return 0.0, 0.0
    sw = sum(w for _, _, w in pts)
    mx = sum(w * x for x, _, w in pts) / sw
    my = sum(w * y for _, y, w in pts) / sw
    sxx = sum(w * (x - mx) ** 2 for x, _, w in pts)
    sxy = sum(w * (x - mx) * (y - my) for x, y, w in pts)
    if sxx <= 1e-15:
        return my, 0.0
    b = sxy / sxx
    a = my - b * mx
    return a, b


def weighted_median(values, weights):
    pairs = sorted((v, w) for v, w in zip(values, weights) if w > 0 and math.isfinite(v))
    if not pairs:
        return 0.0
    total = sum(w for _, w in pairs)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= total / 2.0:
            return v
    return pairs[-1][0]


def robust_location_scale(values, weights):
    med = weighted_median(values, weights)
    deviations = [abs(v - med) for v in values]
    mad = weighted_median(deviations, weights)
    scale = 1.4826 * mad
    if scale <= 1e-12:
        sw = sum(weights) or 1.0
        rms = math.sqrt(sum(w * (v - med) ** 2 for v, w in zip(values, weights)) / sw)
        scale = rms if rms > 1e-12 else 1.0
    return med, scale


def choose_peak_rows(snapshots):
    by_pair = defaultdict(list)
    for r in snapshots:
        rel = fnum(r.get('relative_l1_change'))
        spot = fnum(r.get('spot_change_pct'))
        common = fnum(r.get('common_cells'))
        if rel is None or spot is None or common is None or common <= 0:
            continue
        by_pair[(r['ticker'], r['metric'])].append(r)

    peaks = []
    for (ticker, metric), rows in sorted(by_pair.items()):
        peak = max(rows, key=lambda r: fnum(r.get('relative_l1_change')) or -1.0)
        peaks.append({
            'ticker': ticker,
            'metric': metric,
            'peak_timestamp': peak['j_timestamp'],
            'j1_timestamp': peak['j1_timestamp'],
            'relative_l1_change': fnum(peak.get('relative_l1_change')),
            'spot_change_pct': fnum(peak.get('spot_change_pct')),
            'abs_spot_change_pct': abs(fnum(peak.get('spot_change_pct')) or 0.0),
            'common_cells': int(float(peak.get('common_cells') or 0)),
            'sign_flip_ratio': fnum(peak.get('sign_flip_ratio')),
            'signed_sum_delta': fnum(peak.get('signed_sum_delta')),
            'j1_spot': fnum(peak.get('j1_spot')),
            'j_spot': fnum(peak.get('j_spot')),
            'top_abs_delta_cells': peak.get('top_abs_delta_cells', []),
        })
    return peaks


def main() -> int:
    if not SNAP_JSON.exists():
        raise SystemExit(f'missing {SNAP_JSON}; run summarize_heatseeker_structure_2026_08_28.py first')
    OUT.mkdir(parents=True, exist_ok=True)

    snapshots = json.loads(SNAP_JSON.read_text(encoding='utf-8'))
    peaks = choose_peak_rows(snapshots)
    if not peaks:
        raise SystemExit('no valid ticker/metric peak rows')

    # Model separately by metric so GEX and VEX can have different intercepts
    # and spot-sensitivity slopes. Predictor/response are log1p transformed.
    # Each point is predicted leave-one-pair-out to reduce self-influence.
    groups = defaultdict(list)
    for p in peaks:
        p['x_log_abs_spot'] = math.log1p(p['abs_spot_change_pct'])
        p['y_log_structure'] = math.log1p(p['relative_l1_change'])
        p['fit_weight'] = math.sqrt(max(1, p['common_cells']))
        groups[p['metric']].append(p)

    model_info = {}
    for metric, rows in groups.items():
        full_fit = weighted_linear_fit([(r['x_log_abs_spot'], r['y_log_structure'], r['fit_weight']) for r in rows])
        model_info[metric] = {
            'n_pairs': len(rows),
            'intercept_log': full_fit[0],
            'slope_log_abs_spot': full_fit[1],
            'model': 'log1p(relative_L1) = a + b*log1p(abs(spot_change_pct))',
            'fit_weight': 'sqrt(common_cells)',
            'prediction': 'leave-one-pair-out',
        }

        for target in rows:
            train = [r for r in rows if r is not target]
            a, b = weighted_linear_fit([(r['x_log_abs_spot'], r['y_log_structure'], r['fit_weight']) for r in train])
            pred_log = a + b * target['x_log_abs_spot']
            target['expected_relative_l1_change'] = max(0.0, math.expm1(pred_log))
            target['residual_log'] = target['y_log_structure'] - pred_log
            target['loo_intercept_log'] = a
            target['loo_slope_log_abs_spot'] = b

    # Standardize residuals robustly within GEX/VEX, then apply smooth reliability
    # shrinkage based on the data-derived median cell coverage. No hard exclusions.
    for metric, rows in groups.items():
        vals = [r['residual_log'] for r in rows]
        ws = [r['fit_weight'] for r in rows]
        center, scale = robust_location_scale(vals, ws)
        median_cells = statistics.median(r['common_cells'] for r in rows)
        model_info[metric]['residual_center'] = center
        model_info[metric]['residual_robust_scale'] = scale
        model_info[metric]['median_common_cells'] = median_cells

        for r in rows:
            z = (r['residual_log'] - center) / scale
            reliability = math.sqrt(r['common_cells'] / (r['common_cells'] + median_cells)) if median_cells > 0 else 1.0
            r['residual_robust_z'] = z
            r['coverage_reliability'] = reliability
            r['residual_shuffle_score'] = z * reliability
            exp_rel = r['expected_relative_l1_change']
            r['observed_to_expected_ratio'] = (r['relative_l1_change'] / exp_rel) if exp_rel and exp_rel > 0 else None

    ranked = sorted(peaks, key=lambda r: r['residual_shuffle_score'], reverse=True)
    for i, r in enumerate(ranked, 1):
        r['residual_shuffle_rank'] = i

    csv_fields = [
        'residual_shuffle_rank','ticker','metric','peak_timestamp','j1_timestamp',
        'relative_l1_change','expected_relative_l1_change','observed_to_expected_ratio',
        'spot_change_pct','abs_spot_change_pct','common_cells','sign_flip_ratio',
        'residual_log','residual_robust_z','coverage_reliability','residual_shuffle_score',
        'j1_spot','j_spot','fit_weight','loo_intercept_log','loo_slope_log_abs_spot'
    ]
    out_csv = OUT / 'ticker_metric_residual_shuffle.csv'
    with out_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        for r in ranked:
            w.writerow({k: r.get(k) for k in csv_fields})

    out_json = OUT / 'ticker_metric_residual_shuffle.json'
    out_json.write_text(json.dumps(ranked, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    top20_csv = OUT / 'top20_residual_shuffle.csv'
    with top20_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        for r in ranked[:20]:
            w.writerow({k: r.get(k) for k in csv_fields})

    summary = {
        'ticker_metric_pairs_modeled': len(peaks),
        'method': {
            'target': 'peak observed relative L1 map change for each ticker×metric pair',
            'predictor': 'absolute spot change at the same peak timestamp',
            'transformation': 'log1p on both structure change and absolute spot change',
            'separate_models': ['GEX', 'VEX'],
            'prediction_scheme': 'leave-one-pair-out weighted linear regression',
            'fit_weight': 'sqrt(common_cells)',
            'residual_standardization': 'weighted median / MAD within metric',
            'coverage_adjustment': 'smooth sqrt(n/(n+median_n)); no hard cell-count threshold',
            'ranking': 'residual_shuffle_score = robust residual z × coverage reliability',
        },
        'models': model_info,
        'top15_residual_shuffle': [
            {
                'rank': r['residual_shuffle_rank'],
                'ticker': r['ticker'],
                'metric': r['metric'],
                'peak_timestamp': r['peak_timestamp'],
                'relative_l1_change': r['relative_l1_change'],
                'expected_relative_l1_change': r['expected_relative_l1_change'],
                'observed_to_expected_ratio': r['observed_to_expected_ratio'],
                'spot_change_pct': r['spot_change_pct'],
                'common_cells': r['common_cells'],
                'residual_robust_z': r['residual_robust_z'],
                'coverage_reliability': r['coverage_reliability'],
                'residual_shuffle_score': r['residual_shuffle_score'],
            }
            for r in ranked[:15]
        ],
        'important_note': 'This is an OpenClaw residual diagnostic, not a confirmed Skylit/Heatseeker metric. It uses observed common cells only; no missing values are imputed.',
        'outputs': {
            'csv': str(out_csv),
            'json': str(out_json),
            'top20_csv': str(top20_csv),
        },
    }
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
