# H8 — cross-ticker static gamma×OI core protocol (frozen)

Status: **FROZEN FOR THE NEXT UNSEEN ELIGIBLE NON-MU SINGLE-NAME CARD**.

Chronology: the NBIS 2026-09-02 card was shown before H8 was explicitly recorded. It is therefore usable only as a replication diagnostic, not as the confirmatory H8 decision card.

## Purpose

Test whether the static-core relationship already observed on MU generalizes across single-name equities: HeatSeeker GEX magnitude should be associated with prior-close ThetaData EOD gamma multiplied by settled open interest.

## Eligibility

- Single-name US equity ticker other than MU.
- HeatSeeker GEX card not previously analyzed in OpenClaw.
- Publication after 09:30 ET.
- Spot visible.
- Expiration headers visible.
- A starred GEX King visible in a fully readable expiration column.
- At least 20 fully legible strikes in that same expiration column after excluding the King.

## Deterministic expiration-selection rule

Use the expiration column containing the starred GEX King. If the expiration header is unreadable or truncated, the card is ineligible. Do not substitute another expiration.

## Strike-selection rule

Use the largest contiguous block of fully legible displayed strikes in the selected expiration column. Do not interpolate or repair unreadable values. Primary analysis excludes the King.

## Data inputs

- HeatSeeker GEX: direct screenshot transcription.
- Settled OI: ThetaData observed data on the card date.
- Gamma: ThetaData observed prior-close EOD gamma from the most recent prior US trading session.
- Static variable: `gamma_oi_total = call_gamma*call_OI + put_gamma*put_OI`.
- Baseline: `total_oi = call_OI + put_OI`.
- No reconstructed intraday gamma.
- No dealer sign inferred from call/put type.
- No coefficient is transferred from MU to another ticker.

## Primary target

`|HeatSeeker GEX|` on ex-King strikes.

## Primary statistic

Spearman correlation:

`rho(gamma_oi_total, |HeatSeeker GEX|)`

## Frozen H8 gates

H8 PASS requires all of the following on the next eligible unseen non-MU card:

1. at least 20 usable ex-King strikes;
2. Spearman(`gamma_oi_total`, `|GEX|`) >= +0.60;
3. two-sided permutation p-value < 0.05 using 10,000 deterministic permutations;
4. robustness: after King exclusion, remove the single largest remaining `|GEX|` node and require Spearman(`gamma_oi_total`, `|GEX|`) >= +0.50.

These are the same static-core thresholds already frozen for MU H7; H8 introduces no new tuning.

`total_oi` is a secondary baseline only. H8 does not require gamma×OI to beat total OI on every card.

## Interpretation

PASS would support cross-ticker generalization of a static OI/gamma core in HeatSeeker GEX magnitude. It would not identify the proprietary formula, dealer positioning, sign convention, or intraday adjustment layer.

FAIL would mean the MU static-core relationship does not meet the same frozen standard on the next unseen non-MU card.

H1-H7 remain unchanged.
