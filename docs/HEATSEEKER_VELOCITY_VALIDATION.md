# Heatseeker velocity validation protocol

## Objective

Determine which observable formula reproduces Heatseeker velocity fields such as `delta1Min` and `percent1Min` without claiming access to the private server-side implementation.

## Evidence classes

### Confirmed directly

Only values actually present in captured frontend/network payloads:

- timestamps;
- Greek (`GEX`, `VEX`, etc.);
- strike;
- expiration;
- current node value;
- reported `delta*` fields;
- reported `percent*` fields;
- event type such as `velocity_update` when present.

### Reconstructed

A formula is considered reconstructed only if it reproduces the reported values on observed data within frozen tolerances. The validator currently tests:

- `(current - previous) / previous * 100`;
- `(current - previous) / abs(previous) * 100`;
- `(abs(current) - abs(previous)) / abs(previous) * 100`;
- `(current - previous) / current * 100`;
- `(current - previous) / abs(current) * 100`.

For the historical reference, it separately tests:

- last snapshot at or before the exact horizon;
- nearest snapshot to the exact horizon;
- first snapshot at or after the exact horizon.

The default timing tolerance is 15 seconds and must not be widened after inspecting an outcome without recording that change.

### Not confirmed

The following remain unproven until the observed corpus uniquely identifies them:

- the exact private backend formula;
- the exact server snapshot-selection rule;
- treatment of missing historical nodes;
- treatment of previous value = 0;
- treatment of current value = 0;
- treatment of sign changes;
- any smoothing, clipping, rounding or cache behavior performed server-side.

## Implicit denominator test

Whenever both a reported delta and non-zero reported percentage exist, the validator reconstructs:

`implicit_denominator = 100 * reported_delta / reported_percent`

It then compares that quantity with:

- the signed historical value;
- the absolute historical value.

This test is useful because a sign-flip observation can distinguish formulas that are otherwise identical on positive values.

## Node identity

Historical state is keyed strictly by:

`Greek + strike + expiration`

No substitution across strikes, expirations or Greeks is permitted.

## Edge cases

Rows are explicitly labelled as:

- `regular`;
- `sign_flip`;
- `zero_reference`;
- `zero_to_zero`;
- `current_zero`;
- `current_null`;
- `new_node_or_no_reference`;
- `no_reference_for_horizon`.

They are retained in the evidence table rather than silently discarded.

## Capture

The validator is transport-agnostic. It can preserve JSON payloads supplied on stdin:

```bash
python scripts/validate_heatseeker_velocity.py capture \
  --output data/heatseeker_velocity_raw.jsonl
```

Each input JSON line is wrapped with a local UTC `received_at` timestamp and appended to the JSONL file. Raw captures belong under `data/`, which the repository policy treats as local-only data.

## Analysis

```bash
python scripts/validate_heatseeker_velocity.py analyze \
  data/heatseeker_velocity_raw.jsonl \
  --out-dir reports/heatseeker_velocity
```

Outputs:

- `REPORT.md`;
- `velocity_evidence.csv`;
- `velocity_formula_ranking.csv`;
- `velocity_denominator_audit.csv`;
- `velocity_edge_cases.csv`.

A candidate should not be called the formula merely because it wins on a small sample. Prefer observations containing negative values, sign flips, zero transitions and irregular snapshot timing because these cases distinguish otherwise-equivalent candidates.
