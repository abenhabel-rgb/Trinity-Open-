# MU dealer-flow H1 — confirmatory result on 2026-09-03

Status: **CONFIRMATORY PASS on one independent post-freeze MU card**.

This document records the result only. It does not alter the frozen estimator, thresholds, strike rules, or sign convention defined in `docs/MU_FLOW_H1_FROZEN_V1.md`.

## Card provenance

- Symbol: MU
- HeatSeeker publication date/time supplied by user: 2026-09-03 23:23 Europe/Paris = 17:23 ET
- Publication time is treated only as the collection outer bound; no internal HeatSeeker snapshot timestamp was visible.
- Spot shown on card: 954.46
- Expiration column tested: 2026-09-04
- GEX King on card: strike 1000, +8,879.6K
- The card was supplied after the method and gates had already been frozen.

## Frozen method used

- ThetaData option `trade_quote`
- Window: 09:30:00 ET to 17:23:00 ET outer bound
- Quote-edge fraction: 0.10
- Near ask => customer buy => dealer sell => signed flow -1
- Near bid => customer sell => dealer buy => signed flow +1
- Inside spread / zero spread => UNKNOWN
- No dealer sign inferred from call/put type
- No DAG sign flip in the primary hypothesis
- Primary candidate: signed contract flow by strike
- Primary baseline: raw contract volume by strike

## Confirmatory result

### All 20 common strikes

- Pearson(flow, GEX): +0.953
- Spearman(flow, GEX): +0.660
- Sign agreement: 0.850 = 17/20
- Exact sign-test p-value: 0.00258
- Spearman(volume, GEX): -0.138
- Directional lift vs volume: +0.798
- Permutation p-value for Spearman: 0.00226

### Ex-King 1000 — preregistered primary view

- n = 19
- Pearson(flow, GEX): +0.634
- Spearman(flow, GEX): +0.604
- Sign agreement: 0.842 = 16/19
- Exact sign-test p-value: 0.00443
- Spearman(volume, GEX): -0.328
- Directional lift vs volume: +0.932
- Permutation p-value for Spearman: 0.00714

## Frozen gate decision

The frozen ex-King gates were:

- sign agreement >= 0.65
- Spearman(flow, GEX) >= 0.35
- directional lift vs raw volume >= +0.20

Observed:

- sign agreement = 0.842 => PASS
- Spearman(flow, GEX) = +0.604 => PASS
- directional lift = +0.932 => PASS

**OVERALL: PASS**

## Secondary VEX diagnostic

Not a preregistered gate:

- Spearman(flow, VEX), ex-King: +0.565
- Sign agreement flow/VEX: 0.789

This is recorded as secondary evidence only.

## Interpretation

The result supports the narrow hypothesis that HeatSeeker GEX by strike contains directional/rank information associated with the frozen conservative dealer-flow estimate.

It does **not** establish:

- the proprietary HeatSeeker formula;
- the proprietary Volland classifier;
- total dealer inventory;
- predictive trading value;
- that signed flow determines node magnitude.

The prior development card showed that raw volume can explain HeatSeeker node magnitude better than |signed flow|. Therefore the supported claim remains narrow: **raw activity may explain node intensity while signed dealer-flow may add directional information**.

## Next stage

Do not retune the frozen v1 method. Collect additional untouched MU cards first. After at least several further independent cards, evaluate pooled and per-card distributions of:

1. ex-King Spearman(flow, GEX)
2. ex-King sign agreement
3. directional lift vs raw volume
4. failure rate across cards
5. sensitivity to publication-time outer-bound uncertainty

A second ticker should be tested only after the MU behavior is characterized without changing the estimator.