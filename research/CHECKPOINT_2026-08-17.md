# Trinity Research Checkpoint — 2026-08-17

## H2 — FIXED_KING_MEAN_REVERSION

Status: **REJECTED**

Frozen rule was falsified out of sample in its tested form.

### In-sample

- N = 18
- hit rate = 72.2%
- baseline = 48.7%
- lift = +23.5 percentage points
- mean lift = +8.67 bp

### Out-of-sample cumulative

Holdouts: 2026-08-06, 2026-07-29, 2026-07-30; 2026-08-07 contained no event.

- N = 9
- hit rate = 22.2%
- baseline = 50.0%
- lift = -27.8 percentage points
- mean lift = -14.67 bp

Interpretation: **sign reversal OOS**. Do not rescue or retune H2 using these holdouts.

---

## H3 — FIXED_KING_ESCAPE

Status: **FROZEN / READY FOR FRESH HOLDOUTS**

Pre-registered before examining new holdout outcomes.

### Frozen definition

- `King_t = King_{t-5}`
- `Zone_{t-5} = ATM`
- `Zone_t ∈ {ABOVE, BELOW}`
- ATM band remains fixed at ±20 bp
- single horizon: +5 minutes
- prediction direction is opposite H2: **escape away from the fixed King**
- baseline: fixed King already outside ATM, without a new ATM → outside transition

No post-hoc filter should be added after examining holdout results.

## Research discipline

1. freeze rules before new data
2. preserve holdout integrity
3. report N, hit rate, baseline and lift
4. inspect mean move / mean lift in basis points
5. reject hypotheses that reverse sign OOS
6. never convert a failed hypothesis into a success by adding filters learned from its holdouts
