# AAPL 2026-07-31 — Black-Scholes moneyness third-ticker diagnostic

Status: **DIAGNOSTIC ONLY**.

Snapshot: AAPL 2026-07-31 09:43 ET. GEX spot 300.50; VEX panel spot 300.62. Same-expiry GEX/VEX values tested on 29 common strikes for expiries 2026-07-31, 2026-08-03, 2026-08-05 using observed ThetaData strike-level IV at 09:43 ET and the factor `W_BS=-sqrt(T)*d2` with the same method used for TSLA/NVDA.

Results:

- 2026-07-31: BS Spearman +0.9847, Pearson +0.9906, R2 +0.9802, sign 28/29, fitted alpha 280.281740, alpha/spot 0.932718. Baselines: sign(K-S) R2 +0.3536; log(K/S) R2 +0.8195.
- 2026-08-03: BS Spearman +0.8197, Pearson +0.7610, R2 +0.5443, sign 28/29, fitted alpha 182.051501, alpha/spot 0.605829. Baselines: sign(K-S) R2 +0.1994; log(K/S) R2 +0.5138.
- 2026-08-05: BS Spearman +0.9611, Pearson +0.9872, R2 +0.9742, sign 29/29, fitted alpha 257.686705, alpha/spot 0.857526. Baselines: sign(K-S) R2 +0.4189; log(K/S) R2 +0.9568.

Interpretation:

The BS moneyness weighting continues to outperform the coarse sign(K-S) baseline and generally outperforms log(K/S), especially on the nearest and 2026-08-05 expiries. The sign transformation is highly stable (85/87 total sign matches).

However, the stronger cross-ticker claim `alpha/spot ≈ 1` does **not** replicate cleanly on AAPL: ratios are 0.933, 0.606, and 0.858. The 2026-08-03 expiry is materially weaker in both fit and scaling. Therefore AAPL supports a shared moneyness-weighted GEX→VEX structure but falsifies a universal exact unit-scale identity across all expiries/tickers under the current implementation.

No proprietary Skylit formula or dealer-positioning convention is identified by this diagnostic.
