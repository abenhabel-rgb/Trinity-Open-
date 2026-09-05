# AMD 2025-11-10/11 — delta static-core diagnostic result

Status: **DIAGNOSTIC_ONLY_SMALL_N**.

## Scope

Two AMD morning HeatSeeker cards were compared on the common 2025-11-21 expiration using the common fully legible strike window. The shared King was strike 260. Primary delta analysis excluded the King.

The usable intersection was only 12 strikes including the King, therefore 11 ex-King strikes. This is below confirmatory sample size and cannot decide a frozen hypothesis.

## Cross-sectional static fit

Card A:
- total OI vs |GEX| Spearman: +0.882
- gamma×OI vs |GEX| Spearman: +0.900

Card B:
- total OI vs |GEX| Spearman: +0.855
- gamma×OI vs |GEX| Spearman: +0.809

Interpretation: the static core remains very strong on each card, but gamma weighting does not consistently beat raw OI cross-sectionally.

## Delta discrimination

Across the 11 common ex-King strikes:
- ΔOI vs Δ|GEX|: rho = -0.464, p = 0.1520
- Δ(gamma×OI) vs Δ|GEX|: rho = +0.064, p = 0.8632
- partial Δ(gamma×OI) | ΔOI: rho = +0.207, p = 0.5621
- partial ΔOI | Δ(gamma×OI): rho = -0.495, p = 0.1442

## Interpretation

This pair does **not** provide evidence that gamma weighting explains day-to-day HeatSeeker magnitude changes beyond raw OI. The positive incremental gamma signal is small and non-significant. Raw OI is not significant either; if anything, its delta association is larger in magnitude but negative on this small sample.

The correct conclusion is therefore not that OI beats gamma, but that this small-N pair **fails to discriminate** between the two mechanisms.

The strong cross-sectional static fit remains intact. No proprietary formula, sign convention, dealer positioning, or intraday layer is identified.

## Next step

Use a new unseen pair of same-ticker morning cards with the same readable expiration and at least 20 common ex-King strikes. Freeze the delta-discrimination protocol before seeing that pair.
