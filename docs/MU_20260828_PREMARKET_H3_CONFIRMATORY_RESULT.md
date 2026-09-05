# MU 2026-08-28 premarket H3 — confirmatory replication result

Status: confirmatory replication of the frozen premarket H3 structure test. This does not identify HeatSeeker's proprietary formula and does not establish dealer positioning.

## Target

- Symbol: MU
- HeatSeeker publication: 2026-08-28 09:23 ET (15:23 Paris)
- Expiration column: 2026-08-28
- GEX King: strike 950, +1779.1K
- Same-day regular-session flow was not available at publication.

## Frozen structure

The test reuses the pre-existing H3 setup and thresholds from the earlier MU 2026-08-19 premarket experiment:
- magnitude target: |HeatSeeker GEX|
- baseline: total OI
- candidate: call gamma*OI + put gamma*OI
- signed structural contrast: call gamma*OI - put gamma*OI
- no dealer sign inferred from call/put type
- King excluded in the primary gate evaluation

## Results

All common strikes, n=19:
- Spearman(total OI, |GEX|): +0.442
- Spearman(gamma*OI total, |GEX|): +0.763
- gamma-weighting lift: +0.321
- permutation p for gamma*OI magnitude: 0.00040
- Spearman(call-minus-put gamma*OI contrast, signed GEX): +0.674
- sign agreement of structural contrast vs GEX: 0.737 (14/19)
- permutation p for structural contrast: 0.00205

Ex-King 950, n=18:
- Spearman(total OI, |GEX|): +0.348
- Spearman(gamma*OI total, |GEX|): +0.721
- gamma-weighting lift: +0.374
- permutation p for gamma*OI magnitude: 0.00155
- Spearman(call-minus-put gamma*OI contrast, signed GEX): +0.616
- sign agreement of structural contrast vs GEX: 0.722 (13/18)
- permutation p for structural contrast: 0.00790

## Frozen replication gates — ex-King

All four gates passed without retuning:
- gamma*OI magnitude Spearman >= 0.50: PASS (+0.721)
- gamma-weighting lift vs raw OI >= +0.10: PASS (+0.374)
- call-minus-put gamma*OI contrast Spearman >= 0.35: PASS (+0.616)
- structural contrast sign agreement >= 0.65: PASS (0.722)
- OVERALL: PASS

## Interpretation

This is a successful replication of the pre-existing OI/gamma structure hypothesis on a second MU premarket card after the H3 thresholds were already frozen.

The magnitude evidence is materially stronger for gamma-weighted OI than for raw OI on this card. The call-minus-put gamma*OI contrast also tracks signed HeatSeeker GEX, but remains a structural contrast only and must not be labeled dealer positioning.

This replication strengthens the claim that HeatSeeker's premarket GEX structure is compatible with information already present in prior-close OI/gamma structure. It does not imply that the exact HeatSeeker formula is gamma*OI, nor that same-day intraday dealer flow is irrelevant. H5 remains reserved for a true post-09:30 ET intraday card and must not be retuned using this premarket result.
