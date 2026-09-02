#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review/extracted/j1_vs_open/structure_summary')
SNAP_JSON = ROOT / 'snapshot_structure.json'
OUT = ROOT / 'sequential_persistence_model'

MIN_TRAIN_PAIRS = 8
TOP_DECILE = 0.90


def fnum(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except Exception:
        return None


def dt(v: str) -> datetime:
    return datetime.fromisoformat(v)


def weighted_linear_fit(points):
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
    center = weighted_median(values, weights)
    deviations = [abs(v - center) for v in values]
    mad = weighted_median(deviations, weights)
    scale = 1.4826 * mad
    if scale <= 1e-12:
        sw = sum(weights) or 1.0
        scale = math.sqrt(sum(w * (v - center) ** 2 for v, w in zip(values, weights)) / sw)
    if scale <= 1e-12:
        scale = 1.0
    return center, scale


def empirical_percentile(value, population):
    vals = [v for v in population if v is not None and math.isfinite(v)]
    if not vals:
        return None
    below = sum(v < value for v in vals)
    equal = sum(v == value for v in vals)
    return (below + 0.5 * equal) / len(vals)


def longest_run(flags):
    best = cur = 0
    for flag in flags:
        if flag:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def latest_cross_section(rows, metric, timestamp, exclude_pair):
    latest = {}
    for r in rows:
        if r['metric'] != metric:
            continue
        if r['_dt'] > timestamp:
            continue
        pair = (r['ticker'], r['metric'])
        if pair == exclude_pair:
            continue
        prev = latest.get(pair)
        if prev is None or r['_dt'] > prev['_dt']:
            latest[pair] = r
    return list(latest.values())


def score_target(target, all_rows):
    train = latest_cross_section(
        all_rows,
        target['metric'],
        target['_dt'],
        (target['ticker'], target['metric']),
    )
    if len(train) < MIN_TRAIN_PAIRS:
        return None

    points = []
    for r in train:
        x = math.log1p(abs(r['spot_change_pct']))
        y = math.log1p(r['relative_l1_change'])
        w = math.sqrt(max(1, r['common_cells']))
        points.append((x, y, w))

    a, b = weighted_linear_fit(points)

    residuals = []
    weights = []
    train_payload = []
    for r in train:
        x = math.log1p(abs(r['spot_change_pct']))
        y = math.log1p(r['relative_l1_change'])
        pred = a + b * x
        resid = y - pred
        w = math.sqrt(max(1, r['common_cells']))
        residuals.append(resid)
        weights.append(w)
        train_payload.append((r, resid))

    center, scale = robust_location_scale(residuals, weights)
    median_cells = statistics.median(r['common_cells'] for r in train)

    tx = math.log1p(abs(target['spot_change_pct']))
    ty = math.log1p(target['relative_l1_change'])
    pred_log = a + b * tx
    expected = max(0.0, math.expm1(pred_log))
    residual = ty - pred_log
    z = (residual - center) / scale
    reliability = math.sqrt(target['common_cells'] / (target['common_cells'] + median_cells)) if median_cells > 0 else 1.0
    score = z * reliability

    training_scores = []
    for r, resid in train_payload:
        rz = (resid - center) / scale
        rr = math.sqrt(r['common_cells'] / (r['common_cells'] + median_cells)) if median_cells > 0 else 1.0
        training_scores.append(rz * rr)

    pct = empirical_percentile(score, training_scores)
    return {
        'expected_relative_l1_change': expected,
        'observed_to_expected_ratio': (target['relative_l1_change'] / expected) if expected > 0 else None,
        'residual_log': residual,
        'residual_robust_z': z,
        'coverage_reliability': reliability,
        'residual_shuffle_score': score,
        'cross_section_percentile': pct,
        'top_decile_anomaly': bool(pct is not None and pct >= TOP_DECILE),
        'training_pairs': len(train),
        'model_intercept_log': a,
        'model_slope_log_abs_spot': b,
        'training_residual_center': center,
        'training_residual_scale': scale,
        'training_median_common_cells': median_cells,
    }


def main() -> int:
    if not SNAP_JSON.exists():
        raise SystemExit(f'missing {SNAP_JSON}; run summarize_heatseeker_structure_2026_08_28.py first')
    OUT.mkdir(parents=True, exist_ok=True)

    raw = json.loads(SNAP_JSON.read_text(encoding='utf-8'))
    rows = []
    for r in raw:
        rel = fnum(r.get('relative_l1_change'))
        spot = fnum(r.get('spot_change_pct'))
        common = fnum(r.get('common_cells'))
        ts = r.get('j_timestamp')
        if rel is None or spot is None or common is None or common <= 0 or not ts:
            continue
        rows.append({
            'ticker': r['ticker'],
            'metric': r['metric'],
            'j1_timestamp': r['j1_timestamp'],
            'j_timestamp': ts,
            '_dt': dt(ts),
            'relative_l1_change': rel,
            'spot_change_pct': spot,
            'abs_spot_change_pct': abs(spot),
            'common_cells': int(common),
            'sign_flip_ratio': fnum(r.get('sign_flip_ratio')),
            'j1_spot': fnum(r.get('j1_spot')),
            'j_spot': fnum(r.get('j_spot')),
        })

    rows.sort(key=lambda r: r['_dt'])
    scored = []
    unscored = 0
    for i, r in enumerate(rows, 1):
        result = score_target(r, rows)
        if result is None:
            unscored += 1
            continue
        out = {k: v for k, v in r.items() if k != '_dt'}
        out.update(result)
        scored.append(out)

    seq_csv = OUT / 'snapshot_sequential_scores.csv'
    seq_fields = [
        'ticker','metric','j1_timestamp','j_timestamp','relative_l1_change',
        'expected_relative_l1_change','observed_to_expected_ratio','spot_change_pct',
        'abs_spot_change_pct','common_cells','sign_flip_ratio','residual_log',
        'residual_robust_z','coverage_reliability','residual_shuffle_score',
        'cross_section_percentile','top_decile_anomaly','training_pairs',
        'model_intercept_log','model_slope_log_abs_spot','training_residual_center',
        'training_residual_scale','training_median_common_cells','j1_spot','j_spot'
    ]
    with seq_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=seq_fields)
        w.writeheader()
        for r in scored:
            w.writerow({k: r.get(k) for k in seq_fields})

    by_pair = defaultdict(list)
    for r in scored:
        by_pair[(r['ticker'], r['metric'])].append(r)

    persistence = []
    for (ticker, metric), seq in sorted(by_pair.items()):
        seq.sort(key=lambda r: r['j_timestamp'])
        scores = [r['residual_shuffle_score'] for r in seq]
        percentiles = [r['cross_section_percentile'] for r in seq]
        positives = [s > 0 for s in scores]
        top_flags = [bool(r['top_decile_anomaly']) for r in seq]

        first_top = next((r for r in seq if r['top_decile_anomaly']), None)
        max_score_row = max(seq, key=lambda r: r['residual_shuffle_score'])
        max_spot_row = max(seq, key=lambda r: abs(r['spot_change_pct']))

        lead_minutes = None
        if first_top:
            lead_minutes = (dt(max_spot_row['j_timestamp']) - dt(first_top['j_timestamp'])).total_seconds() / 60.0

        persistence.append({
            'ticker': ticker,
            'metric': metric,
            'scored_snapshots': len(seq),
            'first_scored_timestamp': seq[0]['j_timestamp'],
            'last_scored_timestamp': seq[-1]['j_timestamp'],
            'mean_residual_shuffle_score': sum(scores) / len(scores),
            'median_residual_shuffle_score': statistics.median(scores),
            'max_residual_shuffle_score': max_score_row['residual_shuffle_score'],
            'max_residual_timestamp': max_score_row['j_timestamp'],
            'max_cross_section_percentile': max(percentiles),
            'positive_observations': sum(positives),
            'positive_fraction': sum(positives) / len(positives),
            'longest_positive_run': longest_run(positives),
            'cumulative_positive_score': sum(max(0.0, s) for s in scores),
            'top_decile_observations': sum(top_flags),
            'top_decile_fraction': sum(top_flags) / len(top_flags),
            'longest_top_decile_run': longest_run(top_flags),
            'first_top_decile_timestamp': first_top['j_timestamp'] if first_top else '',
            'first_top_decile_spot_change_pct': first_top['spot_change_pct'] if first_top else '',
            'peak_abs_spot_timestamp': max_spot_row['j_timestamp'],
            'peak_abs_spot_change_pct': max_spot_row['spot_change_pct'],
            'lead_minutes_first_top_decile_to_peak_abs_spot': lead_minutes if lead_minutes is not None else '',
            'first_top_decile_before_peak_abs_spot': (lead_minutes > 0) if lead_minutes is not None else '',
            'data_policy': 'causal_cross_section_observed_only',
        })

    # Ranking emphasizes repeated anomaly rather than a single maximum.
    ranked = sorted(
        persistence,
        key=lambda r: (
            r['longest_top_decile_run'],
            r['top_decile_observations'],
            r['cumulative_positive_score'],
            r['max_residual_shuffle_score'],
        ),
        reverse=True,
    )
    for i, r in enumerate(ranked, 1):
        r['persistence_rank'] = i

    p_csv = OUT / 'ticker_metric_persistence.csv'
    p_fields = ['persistence_rank'] + [k for k in ranked[0].keys() if k != 'persistence_rank'] if ranked else ['persistence_rank']
    with p_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=p_fields)
        w.writeheader()
        for r in ranked:
            w.writerow({k: r.get(k) for k in p_fields})

    (OUT / 'ticker_metric_persistence.json').write_text(json.dumps(ranked, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    top20 = ranked[:20]
    summary = {
        'input_snapshot_rows': len(rows),
        'scored_snapshot_rows': len(scored),
        'unscored_early_rows_insufficient_cross_section': unscored,
        'ticker_metric_pairs': len(ranked),
        'method': {
            'causal_ordering': 'for each target snapshot, training uses only other ticker×metric latest observations with timestamp <= target timestamp',
            'separate_models': ['GEX', 'VEX'],
            'target': 'relative L1 change versus J-1 at each observed snapshot',
            'predictor': 'absolute contemporaneous spot change versus J-1',
            'transform': 'log1p predictor and target',
            'fit_weight': 'sqrt(common_cells)',
            'minimum_cross_section_pairs': MIN_TRAIN_PAIRS,
            'anomaly_percentile': 'empirical percentile versus contemporaneous training residual scores',
            'top_decile_definition': TOP_DECILE,
            'threshold_free_persistence': ['positive_fraction','longest_positive_run','cumulative_positive_score'],
            'high_anomaly_persistence': ['top_decile_observations','longest_top_decile_run'],
            'lead_lag': 'first top-decile residual timestamp compared with timestamp of maximum absolute observed spot change in the window',
        },
        'top20_persistence': [
            {
                'rank': r['persistence_rank'],
                'ticker': r['ticker'],
                'metric': r['metric'],
                'scored_snapshots': r['scored_snapshots'],
                'top_decile_observations': r['top_decile_observations'],
                'longest_top_decile_run': r['longest_top_decile_run'],
                'positive_fraction': r['positive_fraction'],
                'cumulative_positive_score': r['cumulative_positive_score'],
                'first_top_decile_timestamp': r['first_top_decile_timestamp'],
                'first_top_decile_spot_change_pct': r['first_top_decile_spot_change_pct'],
                'peak_abs_spot_timestamp': r['peak_abs_spot_timestamp'],
                'peak_abs_spot_change_pct': r['peak_abs_spot_change_pct'],
                'lead_minutes_first_top_decile_to_peak_abs_spot': r['lead_minutes_first_top_decile_to_peak_abs_spot'],
            }
            for r in top20
        ],
        'important_note': 'This is an OpenClaw research diagnostic, not a confirmed Skylit/Heatseeker metric. No future observations of the target ticker are used to score an earlier snapshot, and missing matrix cells are not imputed.',
        'outputs': {
            'snapshot_scores_csv': str(seq_csv),
            'persistence_csv': str(p_csv),
            'persistence_json': str(OUT / 'ticker_metric_persistence.json'),
        },
    }
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
