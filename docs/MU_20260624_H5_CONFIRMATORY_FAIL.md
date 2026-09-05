# MU 2026-06-24 H5 — confirmatory result

Status: **FAIL**. This failure is retained. Frozen H5 gates are not changed.

## Target

- Symbol: MU
- HeatSeeker card publication: 2026-06-24 17:04 Paris = 11:04 ET
- Exact HeatSeeker snapshot time: **unknown**; publication time is only an outer bound
- Expiration column tested: 2026-06-26
- Tested GEX King: strike 1000, -2469.1K
- Primary grid: contiguous visible strikes 955..1055; ex-King n=20

## Frozen method

- `volland_like_frozen_v1.py`
- trade/quote edge fraction = 0.10
- near ask -> customer buy -> dealer sell sign -1
- near bid -> customer sell -> dealer buy sign +1
- inside-spread -> UNKNOWN
- no dealer sign inferred from call/put
- no DAG transform
- static control = call-minus-put gamma*OI **structural contrast only**, not dealer positioning

## Ex-King primary result

- Spearman(flow, GEX): **-0.167**
- Spearman(static cp gamma*OI contrast, GEX): **+0.113**
- partial Spearman(flow, GEX | static cp): **-0.166**
- permutation p(partial flow): **0.49328**
- sign agreement flow/GEX: **0.450 (9/20)**
- magnitude diagnostic: Spearman(total OI, |GEX|) = **+0.397**
- magnitude diagnostic: Spearman(gamma*OI total, |GEX|) = **+0.395**

## Frozen H5 gates

- sign agreement >= 0.65: **FAIL** (0.450)
- Spearman(flow,GEX) >= 0.35: **FAIL** (-0.167)
- partial Spearman(flow,GEX | cp) >= 0.35: **FAIL** (-0.166)
- permutation p(partial flow) < 0.05: **FAIL** (0.49328)

**OVERALL: FAIL**

## Interpretation

This confirmatory card weakens the hypothesis that the frozen same-day signed-flow estimator provides a universal incremental directional component in HeatSeeker GEX.

The earlier positive H1/H4 results must therefore not be generalized across dates without a regime or timestamp explanation that is specified and validated independently.

The exact HeatSeeker snapshot time is not known. A post-hoc cumulative end-time sweep may be used only as a **timestamp-sensitivity diagnostic**. It cannot rescue H5 and must not be used to retune the frozen method or select a favorable timestamp as confirmatory evidence.
