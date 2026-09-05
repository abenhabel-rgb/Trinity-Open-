# MU 2026-09-04 H4 — incremental flow vs static OI/gamma

Status: development discrimination result. This does not identify the proprietary HeatSeeker formula.

## Question

Does same-day conservative signed dealer-flow retain cross-sectional information about signed HeatSeeker GEX after controlling for the pre-existing call-minus-put gamma*OI structural contrast?

The flow estimator remains frozen v1: quote-edge 0.10, near ask -> dealer sell, near bid -> dealer buy, inside spread UNKNOWN, no dealer sign from call/put, no DAG transform.

## Results

All common strikes, n=20:
- Spearman(flow, GEX): +0.364
- Spearman(cp_gamma_imbalance, GEX): +0.044
- flow-minus-static rank delta: +0.320
- partial Spearman(flow, GEX | cp): +0.362
- partial Spearman(cp, GEX | flow): +0.012
- permutation p(partial flow): 0.13049
- sign agreement flow/GEX: 0.750
- sign agreement cp/GEX: 0.500
- Spearman(total OI, |GEX|): +0.570
- Spearman(gammaOI_total, |GEX|): +0.305

Ex-King 1000, n=19:
- Spearman(flow, GEX): +0.591
- Spearman(cp_gamma_imbalance, GEX): -0.116
- flow-minus-static rank delta: +0.707
- partial Spearman(flow, GEX | cp): +0.651
- partial Spearman(cp, GEX | flow): -0.355
- permutation p(partial flow): 0.00380
- sign agreement flow/GEX: 0.789
- sign agreement cp/GEX: 0.474
- Spearman(total OI, |GEX|): +0.498
- Spearman(gammaOI_total, |GEX|): +0.189

## Interpretation

On this intraday card, the signed-flow association does not collapse after conditioning on the static call-minus-put gamma*OI contrast. Ex-King, the partial rank association is strong (+0.651) and survives the permutation test (p=0.00380). The static call-minus-put contrast is weak to negative on this card and does not explain away the flow result.

This supports a two-component research hypothesis:
1. a pre-existing OI/gamma structure can matter before the session, as observed on the 2026-08-19 premarket card;
2. same-day signed option flow can add distinct directional information intraday.

The magnitude branch is not stable across cards: on this 2026-09-04 card raw OI correlates with |GEX| more strongly than gamma*OI total. Therefore no universal magnitude formula is claimed.

## Limits

- One intraday discrimination card is insufficient for a general claim.
- Partial Spearman here conditions only on the tested cp gamma*OI structural contrast, not on every possible static exposure variable.
- The proprietary HeatSeeker formula remains unidentified.
- The quote-edge classifier is an OpenClaw estimator, not Volland's proprietary classifier.
