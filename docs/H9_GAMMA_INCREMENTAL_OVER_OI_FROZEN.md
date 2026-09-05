# H9 — gamma incremental over raw OI, paired-card protocol (frozen)

Status: **FROZEN BEFORE NEXT ELIGIBLE PAIR**.

## Purpose

Determine whether gamma weighting contributes incremental information beyond raw open interest in explaining day-to-day changes in HeatSeeker GEX magnitude.

H8 established a cross-ticker static-core relationship, but gamma×OI and raw OI are strongly correlated cross-sectionally. H9 therefore uses a paired-card delta design to discriminate between them.

## Eligibility

- Same US single-name ticker on both cards.
- Two consecutive trading-day morning HeatSeeker GEX cards.
- Both cards must show 09:30 ET.
- The same expiration column must be fully readable on both cards.
- The same starred GEX King strike should be present in that expiration on both cards; if King changes, the pair is ineligible for H9.
- At least 20 common fully legible ex-King strikes in the selected expiration.
- The prior EOD snapshot date/time shown on each card must be readable so ThetaData OI and EOD gamma can be aligned to the corresponding static snapshot.

## Deterministic strike rule

Use the intersection of the fully legible strikes in the selected expiration on both cards. Exclude the shared King from the primary analysis. Do not interpolate or repair unreadable values.

## Variables

For each common strike K:

- target change: Δ|GEX|(K) = |GEX_B(K)| - |GEX_A(K)|
- raw-OI change: ΔOI(K) = OI_B(K) - OI_A(K)
- gamma-weighted change: ΔgammaOI(K) = gammaOI_B(K) - gammaOI_A(K)

where `gammaOI = call_gamma*call_OI + put_gamma*put_OI`, using ThetaData observed EOD gamma and settled OI aligned to each card's displayed prior-EOD snapshot.

No reconstructed intraday gamma. No dealer-position sign inference.

## Primary statistic

Partial Spearman correlation:

`rho(ΔgammaOI, Δ|GEX| | ΔOI)`

Primary two-sided significance is evaluated with 10,000 deterministic permutations of the candidate ranks relative to fixed target/control.

## Frozen H9 PASS gates

H9 PASS requires all of the following on the next eligible unseen pair:

1. at least 20 common usable ex-King strikes;
2. raw Spearman(ΔgammaOI, Δ|GEX|) > 0;
3. partial Spearman(ΔgammaOI, Δ|GEX| | ΔOI) >= +0.30;
4. two-sided permutation p < 0.05 with 10,000 deterministic permutations;
5. gamma incremental advantage: partial rho(ΔgammaOI | ΔOI) must exceed partial rho(ΔOI | ΔgammaOI) by at least +0.15.

## Robustness

Secondary only: remove the single largest absolute Δ|GEX| observation and recompute both partial correlations. This cannot rescue a failed primary H9.

## Interpretation

PASS would support gamma weighting as an incremental dynamic component beyond raw OI in the static core.

FAIL would mean the next eligible paired sample does not show a reproducible gamma increment over OI. It would not invalidate H8's broader result that the HeatSeeker magnitude structure is strongly associated with OI/gamma structure.

The 2025-11-10/11 AMD pair was seen before H9 was frozen and had only 11 ex-King observations, so it remains diagnostic only and cannot decide H9.

H1-H8 remain unchanged.
