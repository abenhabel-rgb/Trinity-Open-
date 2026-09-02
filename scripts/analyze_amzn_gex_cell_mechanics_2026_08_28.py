#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review/extracted/j1_vs_open')
CELL_DELTAS = BASE / 'cell_deltas.csv'
SEQ_SCORES = BASE / 'structure_summary/sequential_persistence_model/snapshot_sequential_scores.csv'
OUT = BASE / 'structure_summary/amzn_gex_cell_mechanics'

TICKER = 'AMZN'
METRIC = 'GEX'


def fnum(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except Exception:
        return None


def truthy(v) -> bool:
    return str(v).strip().lower() in {'1','true','yes','y'}


def pct_distance(strike: float, spot: float | None) -> float | None:
    if spot in (None, 0):
        return None
    return (strike / spot - 1.0) * 100.0


def weighted_center(rows, value_key: str) -> float | None:
    num = den = 0.0
    for r in rows:
        v = fnum(r.get(value_key))
        k = fnum(r.get('strike'))
        if v is None or k is None:
            continue
        w = abs(v)
        num += w * k
        den += w
    return num / den if den else None


def concentration(rows, value_key: str, n: int) -> float | None:
    vals = sorted((abs(fnum(r.get(value_key)) or 0.0) for r in rows), reverse=True)
    total = sum(vals)
    return sum(vals[:n]) / total if total else None


def net_ratio(rows, value_key: str) -> float | None:
    vals = [fnum(r.get(value_key)) for r in rows]
    vals = [v for v in vals if v is not None]
    den = sum(abs(v) for v in vals)
    return sum(vals) / den if den else None


def near_spot_share(rows, value_key: str, spot: float | None, band_pct: float) -> float | None:
    if spot in (None, 0):
        return None
    den = 0.0
    num = 0.0
    for r in rows:
        v = fnum(r.get(value_key))
        k = fnum(r.get('strike'))
        if v is None or k is None:
            continue
        a = abs(v)
        den += a
        if abs(k / spot - 1.0) * 100.0 <= band_pct:
            num += a
    return num / den if den else None


def dominant(rows, value_key: str, mode: str):
    valid = []
    for r in rows:
        v = fnum(r.get(value_key))
        if v is None:
            continue
        if mode == 'positive' and v <= 0:
            continue
        if mode == 'negative' and v >= 0:
            continue
        valid.append((r, v))
    if not valid:
        return None
    if mode == 'absolute':
        r, v = max(valid, key=lambda x: abs(x[1]))
    elif mode == 'positive':
        r, v = max(valid, key=lambda x: x[1])
    else:
        r, v = min(valid, key=lambda x: x[1])
    return {
        'expiration': r['expiration'],
        'strike': fnum(r['strike']),
        'value': v,
    }


def rank_map(rows, value_key: str):
    ranked = []
    for r in rows:
        v = fnum(r.get(value_key))
        if v is None:
            continue
        ranked.append(((r['expiration'], float(r['strike'])), abs(v)))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return {key: i + 1 for i, (key, _) in enumerate(ranked)}


def main() -> int:
    if not CELL_DELTAS.exists():
        raise SystemExit(f'missing {CELL_DELTAS}')
    if not SEQ_SCORES.exists():
        raise SystemExit(f'missing {SEQ_SCORES}; run model_heatseeker_sequential_persistence_2026_08_28.py first')
    OUT.mkdir(parents=True, exist_ok=True)

    with SEQ_SCORES.open(encoding='utf-8') as f:
        seq = [r for r in csv.DictReader(f) if r.get('ticker') == TICKER and r.get('metric') == METRIC]
    seq.sort(key=lambda r: r['j_timestamp'])
    selected = [r for r in seq if truthy(r.get('top_decile_anomaly'))]
    if not selected:
        raise SystemExit('no AMZN GEX top-decile sequential observations found')
    selected_ts = [r['j_timestamp'] for r in selected]
    selected_set = set(selected_ts)

    with CELL_DELTAS.open(encoding='utf-8') as f:
        cells = [
            r for r in csv.DictReader(f)
            if r.get('ticker') == TICKER and r.get('metric') == METRIC and r.get('j_timestamp') in selected_set
        ]
    if not cells:
        raise SystemExit('no AMZN GEX cell deltas found for selected timestamps')

    by_ts = defaultdict(list)
    for r in cells:
        by_ts[r['j_timestamp']].append(r)

    # Strict persistent universe: exact expiration/strike cells present in every selected observation.
    keysets = []
    for ts in selected_ts:
        keysets.append({(r['expiration'], float(r['strike'])) for r in by_ts.get(ts, [])})
    persistent_keys = set.intersection(*keysets) if keysets else set()
    if not persistent_keys:
        raise SystemExit('no exact cells persist across all selected observations')

    persistent_by_ts = {}
    for ts in selected_ts:
        persistent_by_ts[ts] = [
            r for r in by_ts[ts]
            if (r['expiration'], float(r['strike'])) in persistent_keys
        ]

    # Baseline J-1 values are fixed by cell key; use first selected observation to define them.
    first_rows = persistent_by_ts[selected_ts[0]]
    base_by_key = {
        (r['expiration'], float(r['strike'])): fnum(r['j1_value'])
        for r in first_rows
    }
    base_rows = [
        {
            'expiration': exp,
            'strike': strike,
            'j1_value': value,
        }
        for (exp, strike), value in sorted(base_by_key.items())
    ]
    base_rank = rank_map(base_rows, 'j1_value')
    base_abs_node = dominant(base_rows, 'j1_value', 'absolute')
    base_pos_node = dominant(base_rows, 'j1_value', 'positive')
    base_neg_node = dominant(base_rows, 'j1_value', 'negative')
    base_center = weighted_center(base_rows, 'j1_value')

    seq_by_ts = {r['j_timestamp']: r for r in selected}
    snapshot_rows = []
    node_trajectory = []
    prior_abs = None

    for ts in selected_ts:
        rows = persistent_by_ts[ts]
        spot = fnum(rows[0].get('j_spot')) if rows else None
        cur_abs = dominant(rows, 'j_value', 'absolute')
        cur_pos = dominant(rows, 'j_value', 'positive')
        cur_neg = dominant(rows, 'j_value', 'negative')
        cur_center = weighted_center(rows, 'j_value')
        cur_rank = rank_map(rows, 'j_value')

        j1_vals = [fnum(r.get('j1_value')) or 0.0 for r in rows]
        j_vals = [fnum(r.get('j_value')) or 0.0 for r in rows]
        l1_num = sum(abs(c - b) for b, c in zip(j1_vals, j_vals))
        l1_den = sum(abs(b) for b in j1_vals)
        rel_l1 = l1_num / l1_den if l1_den else None
        flips = sum(1 for b, c in zip(j1_vals, j_vals) if b * c < 0)

        expiration_abs = defaultdict(float)
        expiration_net = defaultdict(float)
        for r in rows:
            v = fnum(r.get('j_value')) or 0.0
            expiration_abs[r['expiration']] += abs(v)
            expiration_net[r['expiration']] += v
        total_abs = sum(expiration_abs.values())
        top_exp = max(expiration_abs, key=expiration_abs.get) if expiration_abs else ''

        # Rank-gain diagnostics: large negative delta means a cell became more dominant.
        gains = []
        for key in persistent_keys:
            if key not in base_rank or key not in cur_rank:
                continue
            gains.append({
                'expiration': key[0],
                'strike': key[1],
                'j1_abs_rank': base_rank[key],
                'current_abs_rank': cur_rank[key],
                'rank_gain': base_rank[key] - cur_rank[key],
            })
        gains.sort(key=lambda x: x['rank_gain'], reverse=True)

        seq_meta = seq_by_ts[ts]
        row = {
            'j_timestamp': ts,
            'spot': spot,
            'sequential_residual_score': fnum(seq_meta.get('residual_shuffle_score')),
            'cross_section_percentile': fnum(seq_meta.get('cross_section_percentile')),
            'persistent_cells': len(rows),
            'persistent_relative_l1_change': rel_l1,
            'sign_flips_vs_j1': flips,
            'sign_flip_ratio_vs_j1': flips / len(rows) if rows else None,
            'abs_weighted_center_strike': cur_center,
            'center_shift_from_j1': (cur_center - base_center) if cur_center is not None and base_center is not None else None,
            'top1_abs_concentration': concentration(rows, 'j_value', 1),
            'top3_abs_concentration': concentration(rows, 'j_value', 3),
            'top5_abs_concentration': concentration(rows, 'j_value', 5),
            'net_to_abs_ratio': net_ratio(rows, 'j_value'),
            'abs_share_within_2pct_spot': near_spot_share(rows, 'j_value', spot, 2.0),
            'abs_share_within_5pct_spot': near_spot_share(rows, 'j_value', spot, 5.0),
            'dominant_abs_expiration': cur_abs['expiration'] if cur_abs else '',
            'dominant_abs_strike': cur_abs['strike'] if cur_abs else None,
            'dominant_abs_value': cur_abs['value'] if cur_abs else None,
            'dominant_abs_distance_pct_spot': pct_distance(cur_abs['strike'], spot) if cur_abs else None,
            'dominant_positive_expiration': cur_pos['expiration'] if cur_pos else '',
            'dominant_positive_strike': cur_pos['strike'] if cur_pos else None,
            'dominant_positive_value': cur_pos['value'] if cur_pos else None,
            'dominant_negative_expiration': cur_neg['expiration'] if cur_neg else '',
            'dominant_negative_strike': cur_neg['strike'] if cur_neg else None,
            'dominant_negative_value': cur_neg['value'] if cur_neg else None,
            'top_expiration_by_abs': top_exp,
            'top_expiration_abs_share': expiration_abs[top_exp] / total_abs if top_exp and total_abs else None,
            'top_rank_gain_expiration': gains[0]['expiration'] if gains else '',
            'top_rank_gain_strike': gains[0]['strike'] if gains else None,
            'top_rank_gain': gains[0]['rank_gain'] if gains else None,
        }
        snapshot_rows.append(row)

        node_trajectory.append({
            'j_timestamp': ts,
            'spot': spot,
            'candidate_type': 'dominant_abs_common_cell',
            'expiration': cur_abs['expiration'] if cur_abs else '',
            'strike': cur_abs['strike'] if cur_abs else None,
            'value': cur_abs['value'] if cur_abs else None,
            'distance_pct_spot': pct_distance(cur_abs['strike'], spot) if cur_abs else None,
            'strike_change_from_prior': (cur_abs['strike'] - prior_abs['strike']) if cur_abs and prior_abs else None,
            'same_cell_as_prior': bool(cur_abs and prior_abs and cur_abs['strike'] == prior_abs['strike'] and cur_abs['expiration'] == prior_abs['expiration']),
            'label_policy': 'OpenClaw heuristic; not confirmed Skylit King/node label',
        })
        prior_abs = cur_abs

    # Cell trajectories across all 11 selected observations.
    by_key_values = defaultdict(list)
    for ts in selected_ts:
        for r in persistent_by_ts[ts]:
            key = (r['expiration'], float(r['strike']))
            by_key_values[key].append((ts, fnum(r.get('j_value')) or 0.0, fnum(r.get('j1_value')) or 0.0))

    top5_counts = Counter()
    for ts in selected_ts:
        ranked = sorted(
            persistent_by_ts[ts],
            key=lambda r: abs(fnum(r.get('j_value')) or 0.0),
            reverse=True,
        )[:5]
        for r in ranked:
            top5_counts[(r['expiration'], float(r['strike']))] += 1

    cell_summary = []
    for key, vals in sorted(by_key_values.items()):
        cur = [v for _, v, _ in vals]
        base = vals[0][2]
        abs_cur = [abs(v) for v in cur]
        sign_flips = sum(1 for v in cur if base * v < 0)
        cell_summary.append({
            'expiration': key[0],
            'strike': key[1],
            'j1_value': base,
            'mean_j_value': statistics.mean(cur),
            'median_j_value': statistics.median(cur),
            'mean_abs_j_value': statistics.mean(abs_cur),
            'max_abs_j_value': max(abs_cur),
            'min_abs_j_value': min(abs_cur),
            'stdev_j_value': statistics.pstdev(cur) if len(cur) > 1 else 0.0,
            'top5_appearances': top5_counts[key],
            'sign_flip_observations_vs_j1': sign_flips,
            'mean_abs_change_vs_j1': statistics.mean(abs(v - base) for v in cur),
        })
    cell_summary.sort(key=lambda r: (r['top5_appearances'], r['mean_abs_j_value']), reverse=True)

    # Stable node candidates are exact cells repeatedly in the top five by |GEX|.
    stable_nodes = cell_summary[:20]

    snap_csv = OUT / 'amzn_gex_persistent_snapshot_metrics.csv'
    with snap_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(snapshot_rows[0].keys()))
        w.writeheader(); w.writerows(snapshot_rows)

    traj_csv = OUT / 'amzn_gex_dominant_node_trajectory.csv'
    with traj_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(node_trajectory[0].keys()))
        w.writeheader(); w.writerows(node_trajectory)

    cell_csv = OUT / 'amzn_gex_persistent_cell_summary.csv'
    with cell_csv.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(cell_summary[0].keys()))
        w.writeheader(); w.writerows(cell_summary)

    # Minimal self-contained HTML review.
    html = []
    html.append('<!doctype html><meta charset="utf-8"><title>AMZN GEX cell mechanics</title>')
    html.append('<style>body{font-family:system-ui;background:#111;color:#eee;margin:28px}table{border-collapse:collapse;width:100%;margin:18px 0}th,td{border:1px solid #444;padding:6px;text-align:right}th:first-child,td:first-child{text-align:left}h1,h2{margin-top:28px}.note{color:#bbb}</style>')
    html.append('<h1>OpenClaw — AMZN GEX persistent shuffle mechanics — 2026-08-28</h1>')
    html.append('<p class="note">Observed-only. Exact expiration/strike cells present in all selected top-decile observations. “Node/King” language below is heuristic only and is not a confirmed Skylit label.</p>')
    html.append(f'<p><b>Selected observations:</b> {len(selected_ts)} &nbsp; <b>Persistent exact cells:</b> {len(persistent_keys)}</p>')
    html.append('<h2>Dominant |GEX| cell trajectory</h2><table><tr><th>Time</th><th>Spot</th><th>Expiration</th><th>Strike</th><th>Value</th><th>Dist. % spot</th><th>Δ strike</th><th>Same as prior</th></tr>')
    for r in node_trajectory:
        html.append('<tr>' + ''.join(f'<td>{r.get(k,"")}</td>' for k in ['j_timestamp','spot','expiration','strike','value','distance_pct_spot','strike_change_from_prior','same_cell_as_prior']) + '</tr>')
    html.append('</table>')
    html.append('<h2>Snapshot structure on persistent cell universe</h2><table><tr><th>Time</th><th>Spot</th><th>Residual score</th><th>Rel L1</th><th>Flips</th><th>Center strike</th><th>Center shift</th><th>Top3 share</th><th>±2% spot share</th><th>Net/abs</th></tr>')
    for r in snapshot_rows:
        keys=['j_timestamp','spot','sequential_residual_score','persistent_relative_l1_change','sign_flip_ratio_vs_j1','abs_weighted_center_strike','center_shift_from_j1','top3_abs_concentration','abs_share_within_2pct_spot','net_to_abs_ratio']
        html.append('<tr>' + ''.join(f'<td>{r.get(k,"")}</td>' for k in keys) + '</tr>')
    html.append('</table>')
    html.append('<h2>Stable / repeatedly dominant exact cells</h2><table><tr><th>Expiration</th><th>Strike</th><th>J-1</th><th>Mean J</th><th>Mean |J|</th><th>Max |J|</th><th>Top-5 appearances</th><th>Sign-flip obs.</th></tr>')
    for r in stable_nodes:
        keys=['expiration','strike','j1_value','mean_j_value','mean_abs_j_value','max_abs_j_value','top5_appearances','sign_flip_observations_vs_j1']
        html.append('<tr>' + ''.join(f'<td>{r.get(k,"")}</td>' for k in keys) + '</tr>')
    html.append('</table>')
    index = OUT / 'index.html'
    index.write_text('\n'.join(html), encoding='utf-8')

    dom_counter = Counter((r['expiration'], r['strike']) for r in node_trajectory if r['strike'] is not None)
    most_common_dom = dom_counter.most_common(5)

    summary = {
        'ticker': TICKER,
        'metric': METRIC,
        'selected_top_decile_observations': len(selected_ts),
        'selected_timestamps': selected_ts,
        'persistent_exact_cells': len(persistent_keys),
        'j1_baseline': {
            'dominant_abs_candidate': base_abs_node,
            'dominant_positive_candidate': base_pos_node,
            'dominant_negative_candidate': base_neg_node,
            'abs_weighted_center_strike': base_center,
        },
        'dominant_abs_candidate_frequency': [
            {'expiration': exp, 'strike': strike, 'observations': count, 'fraction': count / len(selected_ts)}
            for (exp, strike), count in most_common_dom
        ],
        'first_snapshot': snapshot_rows[0],
        'last_snapshot': snapshot_rows[-1],
        'top_stable_cells': stable_nodes[:10],
        'interpretation_guardrail': 'All King/node language is OpenClaw heuristic. Analysis is limited to exact cells observed in all selected snapshots; no missing cells are filled.',
        'outputs': {
            'snapshot_metrics_csv': str(snap_csv),
            'dominant_node_trajectory_csv': str(traj_csv),
            'persistent_cell_summary_csv': str(cell_csv),
            'html_review': str(index),
        },
    }
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
