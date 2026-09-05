# MU H6 — premium second-layer confirmatory protocol (frozen)

Status: **FROZEN BEFORE NEXT CARD**.

Purpose: test whether absolute signed premium notional adds independent information about HeatSeeker GEX magnitude after controlling the static OI/gamma structure.

This protocol is motivated by the 2026-04-06 replication diagnostic, where `abs_signed_premium_notional` remained materially associated with `|GEX|` after gamma*OI control, while the earlier 2026-04-28 card did not show that effect. H6 therefore tests a possible regime-dependent second layer on a new unseen MU card.

## Eligibility

- Symbol: MU.
- New HeatSeeker GEX card not previously analyzed in OpenClaw.
- Publication after 09:30 ET.
- Spot visible.
- Expiration headers visible.
- A starred HeatSeeker GEX King is visible and belongs to a fully readable expiration column.
- At least 20 fully legible strikes in that same expiration column, excluding the King.

## Deterministic expiration-selection rule

Use the expiration column that contains the displayed starred GEX King.

If the King column header is unreadable or the column is truncated so that the expiration cannot be identified exactly, the card is **ineligible**. Do not substitute another expiration.

## Strike-selection rule

Use the largest contiguous block of fully legible strikes in the selected expiration column. Do not interpolate unreadable values. Primary analysis excludes the King strike.

## Data inputs

- HeatSeeker GEX values: directly transcribed from the eligible screenshot.
- Settled OI: ThetaData observed data.
- Static control: prior-close ThetaData EOD gamma × settled OI, aggregated as `gamma_oi_total`.
- Candidate second-layer variable: `abs_signed_premium_notional` from the unchanged `volland_like_frozen_v1.py` quote-edge classifier.
- Flow window: 09:30 ET to the publication time, which is treated only as an outer bound for the unknown exact HeatSeeker snapshot time.
- No reconstructed intraday gamma.
- No dealer sign inferred from call/put type.

## Primary target and statistic

Primary target: `|HeatSeeker GEX|`.

Primary statistic: partial Spearman correlation

`rho(abs_signed_premium_notional, |GEX| | gamma_oi_total)`

on ex-King strikes only.

## Frozen H6 gates

H6 PASS requires all of the following on the next eligible unseen MU card:

1. at least 20 ex-King usable strikes;
2. raw Spearman(`abs_signed_premium_notional`, `|GEX|`) > 0;
3. partial Spearman given `gamma_oi_total` >= +0.35;
4. two-sided permutation p-value < 0.05 using 10,000 permutations;
5. robustness partial Spearman controlling both `gamma_oi_total` and `total_oi` >= +0.35.

No multiple-testing correction is required because H6 has one preregistered candidate variable.

## Secondary diagnostics

May be printed but cannot decide H6:
- total OI vs |GEX|;
- gamma_oi_total vs |GEX|;
- raw contract volume;
- trade count;
- observed IV and spreads;
- signed-flow direction.

These diagnostics must not be used to replace the H6 candidate after the card is seen.

## Interpretation

PASS would support the existence of a premium/activity second layer above the static OI/gamma structure on the tested card. It would not identify the proprietary HeatSeeker formula and would not prove a universal second layer across regimes.

FAIL would mean the premium second-layer hypothesis does not replicate on the next eligible card. The earlier 2026-04-06 signal must then remain exploratory/regime-specific.

H1-H5 remain unchanged. H6 cannot rescue any prior frozen failure.
