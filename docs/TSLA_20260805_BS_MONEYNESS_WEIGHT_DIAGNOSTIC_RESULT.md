# TSLA 2026-08-05 — Black-Scholes moneyness weight diagnostic

Status: **DIAGNOSTIC_ONLY**

Observed HeatSeeker snapshot: TSLA, 2026-08-05, 12:54 ET, spot 324.26.

Tested transform:

`W_BS = -sqrt(T) * d2`

and fitted no-intercept model per expiry:

`VEX ~= alpha_expiry * GEX * W_BS`

using ThetaData observed historical strike-level IV, call/put IV averaged, with r=q=0 for this short-dated diagnostic.

## Results

| Expiry | n | T (years) | median IV | BS Spearman | BS Pearson | BS R2 | sign | alpha_BS | sign(K-S) R2 | log(K/S) R2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-08-05 | 35 | 0.000354 | 0.9046 | 0.9790 | 0.9979 | 0.9958 | 35/35 | 330.396278 | 0.5901 | 0.9848 |
| 2026-08-07 | 35 | 0.005833 | 0.5445 | 0.9983 | 0.9992 | 0.9983 | 35/35 | 323.565027 | 0.6110 | 0.9951 |
| 2026-08-10 | 35 | 0.014053 | 0.4325 | 0.9927 | 0.9966 | 0.9932 | 35/35 | 340.451934 | 0.4460 | 0.9894 |

Spot was 324.26. Therefore alpha_BS / spot is approximately 1.0189, 0.9979, and 1.0499 across the three expiries.

## Interpretation

The BS moneyness transform explains the observed VEX magnitudes extremely well on this TSLA snapshot. It materially outperforms the pure sign(K-S) baseline in linear fit and slightly improves R2 over the much stronger log(K/S) baseline.

The fitted scale alpha_BS being close to spot is notable because the Black-Scholes identity for standard vanna and gamma is:

`Vanna / Gamma = -S * sqrt(T) * d2`.

Since the tested predictor omitted the leading S and used only `-sqrt(T)*d2`, an alpha near spot is exactly what this identity predicts if Skylit's displayed GEX and VEX share a common exposure/scaling kernel up to remaining convention differences.

However this remains diagnostic rather than formula identification. The simple log-moneyness baseline is already extremely strong, the IV proxy averages call/put IV at each strike, r and q are set to zero, and proprietary aggregation/scaling conventions remain unknown. Independent replication on another ticker/snapshot is required before treating the BS transform as identified.
