# H10 — near-open gamma incremental over raw OI, paired-card protocol (frozen)

Status: **FROZEN BEFORE NEXT ELIGIBLE PAIR**.

## Purpose

Provide a separate near-open paired-card test for cases where HeatSeeker cards are not published exactly at 09:30 ET, while preserving H9 unchanged.

H10 tests the same substantive question as H9: whether gamma weighting contributes incremental information beyond raw open interest in explaining day-to-day changes in HeatSeeker GEX magnitude.

H9 remains frozen at exactly 09:30 ET and is not modified or rescued by H10.

## Eligibility

- Same US single-name ticker on both cards.
- Two consecutive US trading days.
- Each card publication time must be between **09:25 ET and 09:35 ET inclusive**.
- The absolute difference between the two publication times must be **10 minutes or less**.
- The same expiration column must be fully readable on both cards.
- The same starred GEX King strike must be present in that expiration on both cards. If the King changes, the pair is ineligible.
- At least **20 common fully legible ex-King strikes** in the selected expiration.
- Spot visible on both cards.
- The prior EOD snapshot date/time shown on each card must be readable so ThetaData OI and EOD gamma can be aligned to the corresponding static snapshot.
- The pair must be unseen by OpenClaw before H10 is frozen. Pairs already inspected before this file was created are diagnostic only.

## Deterministic strike rule

Use the intersection of the fully legible strikes in the selected expiration on both cards. Exclude the shared King from the primary analysis. Do not interpolate, repair, or substitute unreadable values.

## Variables

For each common strike K:

- target change: `Δ|GEX|(K) = |GEX_B(K)| - |GEX_A(K)|`
- raw-OI change: `ΔOI(K) = OI_B(K) - OI_A(K)`
- gamma-weighted change: `ΔgammaOI(K) = gammaOI_B(K) - gammaOI_A(K)`

where

`gammaOI = call_gamma*call_OI + put_gamma*put_OI`

using ThetaData observed EOD gamma and settled OI aligned to each card's displayed prior-EOD snapshot.

No reconstructed intraday gamma. No dealer-position sign inference from call/put type.

## Primary statistic

Partial Spearman correlation:

`rho(ΔgammaOI, Δ|GEX| | ΔOI)`

Primary significance is evaluated with 10,000 deterministic two-sided permutations of the candidate ranks relative to fixed target/control.

## Frozen H10 PASS gates

H10 PASS requires all of the following on the next eligible unseen pair:

1. at least 20 common usable ex-King strikes;
2. raw Spearman(`ΔgammaOI`, `Δ|GEX|`) > 0;
3. partial Spearman(`ΔgammaOI`, `Δ|GEX|` | `ΔOI`) >= +0.30;
4. two-sided permutation p < 0.05 with 10,000 deterministic permutations;
5. gamma incremental advantage: partial rho(`ΔgammaOI` | `ΔOI`) must exceed partial rho(`ΔOI` | `ΔgammaOI`) by at least +0.15.

These statistical thresholds are copied unchanged from H9. H10 changes only the timing eligibility window.

## Robustness

Secondary only: remove the single largest absolute `Δ|GEX|` observation and recompute both partial correlations. This cannot rescue a failed primary H10.

Also report the exact publication times and their difference in minutes. No post-hoc time adjustment is allowed.

## Interpretation

PASS would support gamma weighting as an incremental dynamic component beyond raw OI under a near-open publication regime.

FAIL would mean the next eligible near-open paired sample does not show a reproducible gamma increment over OI.

A PASS would not identify the proprietary HeatSeeker formula, dealer positioning, sign convention, or any intraday adjustment layer.

## Chronology controls

- H9 remains unchanged and still requires exactly 09:30 ET.
- TSLA cards already shown before this H10 freeze are **not confirmatory H10 material** and may be used only diagnostically.
- H1-H9 remain unchanged.
