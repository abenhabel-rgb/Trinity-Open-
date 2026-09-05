# NVDA 2026-04-10 — GEX/VEX moneyness diagnostic

Status: **DIAGNOSTIC ONLY**.

## Source

Two HeatSeeker screenshots for NVDA, published 2026-04-10 at 14:59 Paris = 08:59 ET. Both panels show spot 184.03. GEX and VEX share the visible expiration columns 2026-04-10, 2026-04-13, and 2026-04-15.

The deterministic analysis block is the fully legible common strike range 175 through 200 (27 displayed rows). Eleven rows per expiration have non-zero GEX/VEX values; zero rows are retained separately in the all-row diagnostic but do not drive the non-zero-only result.

Transformation tested:

`T(K) = GEX(K) * sign(K - spot)`

This is a descriptive moneyness transform only. It is not asserted to be the proprietary VEX formula, a dealer-position convention, or a full theoretical vanna formula.

## Results

### 2026-04-10 expiration

- non-zero common strikes: 11
- all 27 rows: Spearman `|GEX|` vs `|VEX|` = +0.989
- all 27 rows: signed GEX vs VEX = +0.208
- all 27 rows: transformed GEX vs VEX = +0.998
- non-zero only: `|GEX|` vs `|VEX|` = +0.873
- non-zero only: signed GEX vs VEX = +0.091
- non-zero only: transformed GEX vs VEX = **+0.973**
- deterministic 10k two-sided permutation p for transformed non-zero ranks = **0.00020**
- transformed sign agreement = **11/11**

### 2026-04-13 expiration

- non-zero common strikes: 11
- all 27 rows: Spearman `|GEX|` vs `|VEX|` = +0.995
- all 27 rows: signed GEX vs VEX = +0.250
- all 27 rows: transformed GEX vs VEX = **+1.000**
- non-zero only: `|GEX|` vs `|VEX|` = +0.945
- non-zero only: signed GEX vs VEX = +0.291
- non-zero only: transformed GEX vs VEX = **+1.000**
- deterministic 10k two-sided permutation p for transformed non-zero ranks = **0.00010**
- transformed sign agreement = **11/11**

### 2026-04-15 expiration

- non-zero common strikes: 11
- all 27 rows: Spearman `|GEX|` vs `|VEX|` = +0.963
- all 27 rows: signed GEX vs VEX = +0.179
- all 27 rows: transformed GEX vs VEX = +0.994
- non-zero only: `|GEX|` vs `|VEX|` = +0.564
- non-zero only: signed GEX vs VEX = -0.109
- non-zero only: transformed GEX vs VEX = **+0.927**
- deterministic 10k two-sided permutation p for transformed non-zero ranks = **0.00020**
- transformed sign agreement = **11/11**

Across the three expirations, transformed sign agreement is **33/33 non-zero observations**.

## Additional diagnostic

The scale factor `VEX / T(K)` is not constant. Its rank relation with absolute moneyness `|K - spot|` is:

- 2026-04-10: +0.755
- 2026-04-13: +0.973
- 2026-04-15: +0.973

This is consistent with a strong shared strike skeleton plus an additional moneyness-dependent magnitude transform. It argues against a simple constant rescaling of GEX into VEX.

## Interpretation

This is an independent cross-ticker replication of the TSLA observation: raw signed GEX has weak rank agreement with VEX, while flipping the GEX sign around spot produces near-perfect rank and sign agreement on the visible non-zero strikes.

The evidence supports a shared structural basis between displayed GEX and VEX plus a moneyness-dependent transformation. It does **not** identify Skylit's private formula, prove dealer-position conventions, or establish that `sign(K-spot)` is itself the theoretical vanna sign rule in all regimes.
