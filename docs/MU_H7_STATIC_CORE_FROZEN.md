# MU H7 — static gamma×OI core confirmatory protocol (frozen)

Status: **FROZEN FOR THE NEXT UNSEEN ELIGIBLE MU CARD**.

Important chronology note: the 2026-05-20 card was shown before this protocol was explicitly recorded as frozen. It may be used only as a replication diagnostic, not as the confirmatory H7 decision card.

## Purpose

Test whether HeatSeeker GEX magnitude is primarily explained by a pre-existing static options structure measured as prior-close ThetaData EOD gamma multiplied by settled open interest.

## Eligibility

- Symbol: MU.
- New HeatSeeker GEX card not previously analyzed in OpenClaw.
- Publication after 09:30 ET.
- Spot visible.
- Expiration headers visible.
- A starred HeatSeeker GEX King is visible in a fully readable expiration column.
- At least 20 fully legible strikes in that same expiration column after excluding the King.

## Deterministic expiration-selection rule

Use the expiration column containing the starred GEX King.

If that expiration header is unreadable or truncated, the card is ineligible. Do not substitute another expiration.

## Strike-selection rule

Use the largest contiguous block of fully legible displayed strikes in the selected expiration column. Do not interpolate or repair unreadable values. Primary analysis excludes the King strike.

## Data inputs

- HeatSeeker GEX: directly transcribed from the screenshot.
- Settled OI: ThetaData observed data on the card date.
- Gamma: ThetaData observed prior-close EOD gamma from the most recent prior US trading session.
- Static variable: `gamma_oi_total = call_gamma*call_OI + put_gamma*put_OI`.
- Baseline: `total_oi = call_OI + put_OI`.
- No reconstructed intraday gamma.
- No dealer sign inferred from call/put type.

## Primary target

`|HeatSeeker GEX|` on ex-King strikes.

## Primary statistic

Spearman correlation:

`rho(gamma_oi_total, |HeatSeeker GEX|)`

## Frozen H7 gates

H7 PASS requires all of the following on the next eligible unseen card:

1. at least 20 usable ex-King strikes;
2. Spearman(`gamma_oi_total`, `|GEX|`) >= +0.60;
3. two-sided permutation p-value < 0.05 using 10,000 deterministic permutations;
4. robustness: remove the single largest remaining `|GEX|` node after King exclusion, then Spearman(`gamma_oi_total`, `|GEX|`) >= +0.50.

`total_oi` is a secondary baseline only. H7 does not require gamma×OI to beat total OI on every card.

## Secondary diagnostics

May be printed but cannot decide H7:
- total OI vs |GEX|;
- raw volume / trade count if already available;
- direction contrasts;
- all-strikes including King;
- alternative expirations.

No secondary diagnostic may replace the primary statistic after the card is seen.

## Interpretation

PASS would support the existence of a robust static OI/gamma core in HeatSeeker GEX magnitude. It would not identify the proprietary HeatSeeker formula, sign convention, dealer inventory, or any intraday adjustment layer.

FAIL would mean the static-core hypothesis does not meet the frozen replication standard on the next unseen eligible card.

H1-H6 remain unchanged.
