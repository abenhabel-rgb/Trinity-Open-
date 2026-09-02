#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, time
from pathlib import Path

BASE = Path('/Volumes/OPENCLAW/OpenClaw_Metadata/discord_heatseeker_2026-08-28_review/extracted/j1_vs_open')
CELL_DELTAS = BASE / 'cell_deltas.csv'
OUT = BASE / 'structure_summary/causal_shuffle_vector'

# Frozen OpenClaw research thresholds. These are not Skylit/Heatseeker metrics.
CENTER_SHIFT_PCT_THRESHOLD = 0.50      # center migration >= 0.50% of spot
ALIGNED_TRANSFER_THRESHOLD = 0.10      # >= 10 percentage points of |exposure| shifted with center direction
WATCH_RUN = 2                          # two consecutive primitive hits
ARMED_RUN = 3                          # three consecutive primitive hits
START = time(9, 30, 0)
END = time(10, 0, 0)


def fnum(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except Exception:
        return None


def parse_ts(s: str) -> datetime:
    return datetime.fromisoformat(s)


def in_window(ts: str) -> bool:
    t = parse_ts(ts).time()
    return START <= t <= END


def weighted_center(rows, value_key: str):
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


def abs_share_above(rows, value_key: str, boundary: float | None):
    if boundary is None:
        return None
    num = den = 0.0
    for r in rows:
        v = fnum(r.get(value_key))
        k = fnum(r.get('strike'))
        if v is None or k is None:
            continue
        a = abs(v)
        den += a
        if k > boundary:
            num += a
    return num / den if den else None


def dominant_abs(rows, value_key: str):
    valid = []
    for r in rows:
        v = fnum(r.get(value_key))
        k = fnum(r.get('strike'))
        exp = r.get('expiration')
        if v is None or k is None or not exp:
            continue
        valid.append((abs(v), exp, k, v))
    if not valid:
        return None
    _, exp, k, v = max(valid)
    return {'expiration': exp, 'strike': k, 'value': v}


def sign(x: float | None) -> int:
    if x is None or x == 0:
        return 0
    return 1 if x > 0 else -1


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def component_strength(abs_value: float | None, threshold: float) -> float:
    if abs_value is None or threshold <= 0:
        return 0.0
    return clamp01(abs_value / threshold)


def pair_key(r):
    return r.get('ticker', ''), r.get('metric', '')


def main() -> int:
    if not CELL_DELTAS.exists():
        raise SystemExit(f'missing {CELL_DELTAS}')
    OUT.mkdir(parents=True, exist_ok=True)

    with CELL_DELTAS.open(encoding='utf-8') as f:
        raw = list(csv.DictReader(f))

    # Current-session rows only. No future spot outcome or top-decile labels are loaded.
    raw = [r for r in raw if r.get('j_timestamp') and in_window(r['j_timestamp'])]

    by_pair_ts = defaultdict(lambda: defaultdict(list))
    for r in raw:
        t, m = pair_key(r)
        if not t or not m:
            continue
        # A row is eligible only if its exact J-1 and J values are observed.
        if fnum(r.get('j1_value')) is None or fnum(r.get('j_value')) is None:
            continue
        if fnum(r.get('strike')) is None or not r.get('expiration'):
            continue
        by_pair_ts[(t, m)][r['j_timestamp']].append(r)

    all_rows = []
    summaries = []

    for (ticker, metric), tsmap in sorted(by_pair_ts.items()):
        timestamps = sorted(tsmap)
        prior_dom = None
        primitive_run = 0
        handoff_seen_in_run = False
        first_primitive = first_watch = first_armed = first_confirmed = None
        state_counts = Counter()

        for ts in timestamps:
            rows = tsmap[ts]
            if not rows:
                continue
            spot = fnum(rows[0].get('j_spot'))
            if spot in (None, 0):
                continue

            # IMPORTANT: J-1 and J centers are computed on exactly the current snapshot's
            # common cells. This avoids using future snapshots to define a persistent universe.
            j1_center = weighted_center(rows, 'j1_value')
            j_center = weighted_center(rows, 'j_value')
            center_shift = None if j1_center is None or j_center is None else j_center - j1_center
            center_shift_pct = None if center_shift is None else center_shift / spot * 100.0

            # Fixed-boundary transfer: use CURRENT spot as the same strike boundary for
            # both J-1 and J values. Thus the component is not mechanically created by
            # a changing spot boundary.
            j1_above_fixed = abs_share_above(rows, 'j1_value', spot)
            j_above_fixed = abs_share_above(rows, 'j_value', spot)
            above_transfer_fixed = None
            if j1_above_fixed is not None and j_above_fixed is not None:
                above_transfer_fixed = j_above_fixed - j1_above_fixed

            direction = sign(center_shift_pct)
            aligned_transfer = None if above_transfer_fixed is None else direction * above_transfer_fixed

            center_hit = center_shift_pct is not None and abs(center_shift_pct) >= CENTER_SHIFT_PCT_THRESHOLD
            transfer_hit = aligned_transfer is not None and aligned_transfer >= ALIGNED_TRANSFER_THRESHOLD
            primitive_hit = bool(center_hit and transfer_hit)

            dom = dominant_abs(rows, 'j_value')
            handoff = bool(
                prior_dom and dom and
                (dom['expiration'] != prior_dom['expiration'] or dom['strike'] != prior_dom['strike'])
            )
            handoff_distance_pct = None
            if handoff and prior_dom and dom:
                handoff_distance_pct = abs(dom['strike'] - prior_dom['strike']) / spot * 100.0

            if primitive_hit:
                primitive_run += 1
                if handoff:
                    handoff_seen_in_run = True
            else:
                primitive_run = 0
                handoff_seen_in_run = False

            if primitive_hit and first_primitive is None:
                first_primitive = ts

            # Four-component causal vector, each component in [0,1].
            c1_center = component_strength(abs(center_shift_pct) if center_shift_pct is not None else None,
                                           CENTER_SHIFT_PCT_THRESHOLD)
            c2_transfer = component_strength(aligned_transfer if aligned_transfer is not None else None,
                                             ALIGNED_TRANSFER_THRESHOLD)
            c3_persistence = clamp01(primitive_run / ARMED_RUN)
            # Handoff is a state-change component, not required for WATCH/ARMED.
            c4_handoff = 1.0 if handoff_seen_in_run else 0.0
            vector_score = (c1_center + c2_transfer + c3_persistence + c4_handoff) / 4.0

            if primitive_run >= ARMED_RUN and handoff_seen_in_run:
                state = 'CONFIRMED_SHUFFLE'
                if first_confirmed is None:
                    first_confirmed = ts
            elif primitive_run >= ARMED_RUN:
                state = 'ARMED'
                if first_armed is None:
                    first_armed = ts
            elif primitive_run >= WATCH_RUN:
                state = 'WATCH'
                if first_watch is None:
                    first_watch = ts
            elif primitive_hit:
                state = 'OBSERVE'
            else:
                state = 'NONE'

            # If confirmation occurs directly on the third hit, that timestamp is also
            # the first time the system would have been ARMED absent the handoff.
            if primitive_run >= ARMED_RUN and first_armed is None:
                first_armed = ts
            if primitive_run >= WATCH_RUN and first_watch is None:
                first_watch = ts

            state_counts[state] += 1
            all_rows.append({
                'ticker': ticker,
                'metric': metric,
                'timestamp': ts,
                'spot': spot,
                'common_cells_current_snapshot': len(rows),
                'j1_center_same_cells': j1_center,
                'j_center_same_cells': j_center,
                'center_shift': center_shift,
                'center_shift_pct_spot': center_shift_pct,
                'j1_above_abs_share_fixed_current_spot': j1_above_fixed,
                'j_above_abs_share_fixed_current_spot': j_above_fixed,
                'above_transfer_fixed': above_transfer_fixed,
                'center_direction': direction,
                'aligned_transfer': aligned_transfer,
                'center_hit': center_hit,
                'transfer_hit': transfer_hit,
                'primitive_hit': primitive_hit,
                'primitive_run': primitive_run,
                'dominant_expiration': dom['expiration'] if dom else '',
                'dominant_strike': dom['strike'] if dom else None,
                'dominant_value': dom['value'] if dom else None,
                'handoff_now': handoff,
                'handoff_seen_in_run': handoff_seen_in_run,
                'handoff_distance_pct_spot': handoff_distance_pct,
                'c1_center': c1_center,
                'c2_transfer': c2_transfer,
                'c3_persistence': c3_persistence,
                'c4_handoff': c4_handoff,
                'shuffle_vector_score': vector_score,
                'state': state,
                'causal_guardrail': 'J-1 + current/past snapshots only; no future spot, no future cell-universe intersection',
            })
            prior_dom = dom

        pair_rows = [r for r in all_rows if r['ticker'] == ticker and r['metric'] == metric]
        if not pair_rows:
            continue
        summaries.append({
            'ticker': ticker,
            'metric': metric,
            'snapshots_0930_1000': len(pair_rows),
            'first_snapshot': pair_rows[0]['timestamp'],
            'last_snapshot': pair_rows[-1]['timestamp'],
            'first_primitive': first_primitive or '',
            'first_watch': first_watch or '',
            'first_armed': first_armed or '',
            'first_confirmed_shuffle': first_confirmed or '',
            'max_primitive_run': max(r['primitive_run'] for r in pair_rows),
            'handoffs_total': sum(1 for r in pair_rows if r['handoff_now']),
            'max_shuffle_vector_score': max(r['shuffle_vector_score'] for r in pair_rows),
            'final_state': pair_rows[-1]['state'],
            'state_counts': dict(state_counts),
        })

    rows_csv = OUT / 'causal_shuffle_vector_snapshots.csv'
    if all_rows:
        with rows_csv.open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            w.writeheader(); w.writerows(all_rows)

    summary_csv = OUT / 'causal_shuffle_vector_summary.csv'
    if summaries:
        fields = [k for k in summaries[0].keys() if k != 'state_counts']
        with summary_csv.open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in summaries:
                w.writerow({k: r[k] for k in fields})

    summary_json = OUT / 'causal_shuffle_vector_summary.json'
    summary_json.write_text(json.dumps({
        'policy': {
            'window': '09:30:00-10:00:00 internal timestamp',
            'center_shift_pct_threshold': CENTER_SHIFT_PCT_THRESHOLD,
            'aligned_transfer_threshold': ALIGNED_TRANSFER_THRESHOLD,
            'watch_run': WATCH_RUN,
            'armed_run': ARMED_RUN,
            'confirmed_rule': 'ARMED plus at least one dominant-cell handoff during the current primitive run',
            'transfer_definition': 'change in absolute-exposure share above CURRENT spot, applying the same current-spot boundary to J-1 and J values',
            'future_leakage': 'prohibited',
            'label_status': 'OpenClaw research diagnostic; not confirmed Skylit/Heatseeker metric',
        },
        'summaries': summaries,
    }, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    # Focused human-readable console output.
    focus = [r for r in summaries if r['ticker'] in {'MRVL','AMZN','META'}]
    print(json.dumps({
        'frozen_policy': {
            'center_shift_pct_threshold': CENTER_SHIFT_PCT_THRESHOLD,
            'aligned_transfer_threshold': ALIGNED_TRANSFER_THRESHOLD,
            'WATCH': f'{WATCH_RUN} consecutive primitive hits',
            'ARMED': f'{ARMED_RUN} consecutive primitive hits',
            'CONFIRMED_SHUFFLE': 'ARMED + handoff observed in current run',
            'causal': True,
        },
        'focus': focus,
        'outputs': {
            'snapshots_csv': str(rows_csv),
            'summary_csv': str(summary_csv),
            'summary_json': str(summary_json),
        },
    }, indent=2, ensure_ascii=False))

    # HTML audit trail.
    html = [
        '<!doctype html><meta charset="utf-8"><title>OpenClaw causal Shuffle Vector</title>',
        '<style>body{font-family:system-ui;background:#111;color:#eee;margin:28px}table{border-collapse:collapse;width:100%;margin:18px 0}th,td{border:1px solid #444;padding:6px;text-align:right}th:first-child,td:first-child{text-align:left}.note{color:#bbb}.confirmed{font-weight:700}</style>',
        '<h1>OpenClaw — causal 4-component Shuffle Vector — 2026-08-28</h1>',
        '<p class="note">Strict replay: J−1 + current/past snapshots only. No future spot outcome, no future snapshot-defined persistent universe, no imputation. This is an OpenClaw research diagnostic, not a confirmed Skylit metric.</p>',
        f'<p>Frozen thresholds: |center shift| ≥ {CENTER_SHIFT_PCT_THRESHOLD}% of spot; aligned cross-spot transfer ≥ {ALIGNED_TRANSFER_THRESHOLD:.0%}; WATCH={WATCH_RUN} hits; ARMED={ARMED_RUN} hits; CONFIRMED=ARMED + handoff.</p>',
        '<h2>Detection summary</h2><table><tr><th>Ticker</th><th>Metric</th><th>Snapshots</th><th>Primitive</th><th>WATCH</th><th>ARMED</th><th>CONFIRMED</th><th>Max run</th><th>Handoffs</th><th>Max vector</th></tr>'
    ]
    for r in sorted(summaries, key=lambda x: (x['ticker'], x['metric'])):
        vals = [r['ticker'],r['metric'],r['snapshots_0930_1000'],r['first_primitive'],r['first_watch'],r['first_armed'],r['first_confirmed_shuffle'],r['max_primitive_run'],r['handoffs_total'],round(r['max_shuffle_vector_score'],4)]
        html.append('<tr>' + ''.join(f'<td>{v}</td>' for v in vals) + '</tr>')
    html.append('</table>')

    for ticker, metric in [('MRVL','VEX'),('MRVL','GEX'),('META','VEX'),('META','GEX'),('AMZN','GEX')]:
        rr = [r for r in all_rows if r['ticker']==ticker and r['metric']==metric]
        if not rr:
            continue
        html.append(f'<h2>{ticker} {metric}</h2><table><tr><th>Time</th><th>Spot</th><th>Center %</th><th>Aligned transfer</th><th>Run</th><th>Dom strike</th><th>Handoff</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>Vector</th><th>State</th></tr>')
        for r in rr:
            keys=['timestamp','spot','center_shift_pct_spot','aligned_transfer','primitive_run','dominant_strike','handoff_now','c1_center','c2_transfer','c3_persistence','c4_handoff','shuffle_vector_score','state']
            html.append('<tr>' + ''.join(f'<td>{r.get(k,"")}</td>' for k in keys) + '</tr>')
        html.append('</table>')
    html.append('</body>')
    (OUT / 'index.html').write_text('\n'.join(html), encoding='utf-8')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
