# NVDA 2026-09-02 — H8 confirmatory result

Status: **H8 PASS**.

This result applies the already-frozen protocol in `docs/H8_CROSS_TICKER_STATIC_CORE_FROZEN.md` to the next eligible unseen non-MU single-name HeatSeeker GEX card.

## Card used

- Symbol: NVDA
- Card date: 2026-09-02
- Publication: 17:56 Paris = 11:56 ET
- Displayed spot: 227.29
- Expiration selected by the frozen King-column rule: 2026-09-04
- Starred GEX King: strike 235.0, -27,669.3K
- Second screenshot supplied in the same message had a different spot/King state and was excluded rather than merged.

## Primary ex-King result

- usable all strikes after ThetaData matching: 22
- usable ex-King strikes: 21
- Spearman(`gamma_oi_total`, `|GEX|`): **+0.792**
- two-sided permutation p, 10,000 draws: **0.00010**
- total OI vs `|GEX|` Spearman (secondary baseline): **+0.781**
- largest remaining `|GEX|` node removed for robustness: strike 230.0, |GEX| = 21,288.1K
- robust Spearman(`gamma_oi_total`, `|GEX|`) after that removal: **+0.821**

## Frozen H8 gates

1. n >= 20: **PASS** (21)
2. Spearman >= +0.60: **PASS** (+0.792)
3. permutation p < 0.05: **PASS** (0.00010)
4. robust Spearman >= +0.50: **PASS** (+0.821)

**OVERALL H8: PASS**

## Interpretation

This is confirmatory evidence that the static OI/gamma core observed on MU generalizes to at least one independent non-MU single-name equity under the same frozen thresholds. It supports a cross-ticker association between HeatSeeker GEX magnitude and prior-close ThetaData gamma multiplied by settled OI.

It does **not** identify the proprietary HeatSeeker formula, prove a dealer-position sign convention, prove gamma weighting is necessary relative to raw OI on every ticker, or establish an intraday adjustment layer.

The raw OI baseline remained strong on this NVDA card (rho +0.781), so the exact incremental contribution of gamma weighting remains an identification question.

H1-H7 remain unchanged.