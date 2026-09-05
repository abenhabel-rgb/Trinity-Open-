# MU HeatSeeker dealer-flow hypothesis — frozen v1

Status: development freeze after the first MU card (2026-09-04), before any second independent MU card is evaluated.

## Scope

Test whether HeatSeeker GEX by strike contains directional information related to a conservative dealer-flow estimate derived from ThetaData trade+quote data.

This does **not** claim to reproduce Volland's proprietary classifier and does **not** identify HeatSeeker's proprietary formula.

## Frozen estimator

- Symbol: MU for the next confirmatory card.
- Expiration: compare the same expiration column visible on the HeatSeeker card.
- Collection window: 09:30:00 ET to the card publication time used only as an outer bound unless an internal snapshot timestamp is visible.
- Trade classification edge fraction: 0.10.
- Near ask: customer buy -> dealer sell -> sign -1.
- Near bid: customer sell -> dealer buy -> sign +1.
- Inside spread: UNKNOWN.
- Locked/zero spread: UNKNOWN.
- Never assign dealer direction from call/put type.
- No DAG sign flip in the primary hypothesis.
- Do not tune edge fraction, time window, strike selection, or sign convention after seeing the next card.

## Primary observable

`signed_contract_flow` by strike.

## Baselines

Primary baseline: raw contract volume by strike = classified_contracts + unknown_contracts.

Secondary baseline: raw trade count by strike.

Signed premium is retained as a diagnostic only, not the primary candidate.

## Primary confirmatory metrics

Evaluate both all common strikes and ex-King.

1. Spearman(signed_contract_flow, HeatSeeker GEX)
2. Sign agreement(signed_contract_flow, HeatSeeker GEX)
3. Spearman(raw contract volume, HeatSeeker GEX)
4. Directional lift = Spearman(flow, GEX) - Spearman(raw volume, GEX)

Magnitude diagnostics:

- Spearman(|flow|, |GEX|)
- Spearman(raw volume, |GEX|)
- magnitude lift = |flow| rank correlation minus raw-volume rank correlation

The first development card already indicates that raw volume may explain magnitude better than |signed flow|. Therefore the confirmatory question is specifically whether signed dealer-flow adds **directional/rank information**, not whether it explains node magnitude.

## Frozen next-card gates

These gates are preregistered only for the next independent MU card and are not retroactive claims about the first card.

Ex-King primary gate:

- sign agreement >= 0.65
- Spearman(flow, GEX) >= 0.35
- directional lift versus raw-volume signed-target Spearman >= +0.20

If any of these fail, H1 is not confirmed on that card.

No magnitude-lift gate is imposed because the first development card showed raw activity can dominate node magnitude.

## Interpretation

Passing one independent card is confirmatory evidence, not formula identification. A broader claim requires additional untouched cards and/or another ticker.

All failures, missing data, ambiguous timestamps, and parsing losses must be reported explicitly.
