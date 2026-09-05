# MU 2026-03-18 H6 — confirmatory result

Status: **FAIL**. Frozen H6 gates are unchanged.

## Target

- Symbol: MU
- HeatSeeker publication: 2026-03-18 18:16 Paris = 13:16 ET
- Displayed spot: 464.82
- Selected expiration by frozen rule: 2026-03-20
- Displayed starred King: strike 500, +3103.2K
- Primary subset: largest contiguous fully legible block, ex-King
- Usable ex-King strikes: 52

## Frozen H6 candidate

`abs_signed_premium_notional` from unchanged `volland_like_frozen_v1.py`.

Primary target: `|HeatSeeker GEX|`.

Primary control: `gamma_oi_total` = observed prior-close ThetaData EOD gamma × settled OI.

Robustness controls: `gamma_oi_total + total_oi`.

## Primary result

- raw Spearman(abs signed premium, |GEX|): **+0.484**
- partial Spearman given gammaOI: **+0.017**
- two-sided permutation p (10,000): **0.90871**
- partial Spearman given gammaOI + totalOI: **+0.019**

## Secondary static-core diagnostics

- total OI vs |GEX|: **+0.774**
- gammaOI total vs |GEX|: **+0.814**
- raw volume vs |GEX|: **+0.565**
- trade count vs |GEX|: **+0.598**

## Frozen H6 gates

1. n >= 20: **PASS** (52)
2. raw rho > 0: **PASS** (+0.484)
3. partial rho | gammaOI >= +0.35: **FAIL** (+0.017)
4. permutation p < 0.05: **FAIL** (0.90871)
5. partial rho | gammaOI + totalOI >= +0.35: **FAIL** (+0.019)

**OVERALL H6: FAIL**

## Interpretation

The premium magnitude has a positive raw association with |HeatSeeker GEX|, but that association is almost completely absorbed by the static gamma*OI structure. On this preregistered confirmatory card, absolute signed premium notional does not provide an independent second layer above the static OI/gamma core.

The earlier 2026-04-06 residual premium signal therefore remains exploratory/regime-specific and is not replicated by H6.

The static core remains strong on this card, especially gammaOI total (rho +0.814), but this H6 test was not designed to confirm the static core itself.

H1-H5 are unchanged. H6 is closed as a confirmatory FAIL and must not be retuned on this card.
