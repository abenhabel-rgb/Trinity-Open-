# MU 2026-08-19 premarket H3 — result

Status: exploratory development result. Not confirmatory evidence of the proprietary HeatSeeker formula.

## Target

- Symbol: MU
- HeatSeeker publication: 2026-08-19 07:25 ET
- Expiration column: 2026-08-19
- GEX King: strike 950, -2170.2K
- Same-day regular-session flow was not available at publication.

## Inputs

Temporally valid structure available before publication:
- OI message dated 2026-08-19, representing prior-session OI.
- EOD gamma from 2026-08-18 close.
- No dealer sign inferred from call/put type.

## Results

All common strikes, n=18:
- Spearman(total OI, |GEX|): +0.534
- Spearman(gamma*OI total, |GEX|): +0.659
- gamma-weighting lift: +0.126
- permutation p for gamma*OI magnitude: 0.00370
- Spearman(call-minus-put gamma*OI contrast, signed GEX): +0.346
- sign agreement of structural contrast vs GEX: 0.667 (12/18)
- permutation p for structural contrast: 0.15869

Ex-King 950, n=17:
- Spearman(total OI, |GEX|): +0.480
- Spearman(gamma*OI total, |GEX|): +0.625
- gamma-weighting lift: +0.145
- permutation p for gamma*OI magnitude: 0.00710
- Spearman(call-minus-put gamma*OI contrast, signed GEX): +0.517
- sign agreement of structural contrast vs GEX: 0.706 (12/17)
- permutation p for structural contrast: 0.03570

## Preregistered exploratory gates

All four ex-King gates passed:
- gamma*OI magnitude Spearman >= 0.50: PASS (+0.625)
- gamma-weighting lift vs raw OI >= +0.10: PASS (+0.145)
- call-minus-put gamma*OI contrast Spearman >= 0.35: PASS (+0.517)
- structural contrast sign agreement >= 0.65: PASS (0.706)

## Interpretation

This card supports a pre-existing OI/gamma structure as a serious HeatSeeker GEX candidate. The magnitude result is stronger than raw OI alone. The call-minus-put gamma*OI contrast also tracks signed GEX on this card, but it is a structural contrast only and must not be labeled dealer positioning.

This result does not identify HeatSeeker's proprietary formula and does not establish causality. The next discrimination test should ask whether same-day signed dealer flow adds information beyond the static OI/gamma structure on intraday cards.
