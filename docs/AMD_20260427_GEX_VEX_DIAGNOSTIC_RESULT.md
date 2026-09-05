# AMD 2026-04-27 — exploratory GEX↔VEX strike-alignment diagnostic

Status: **DIAGNOSTIC ONLY**. This does not modify or decide H9/H10.

## Source

Same AMD HeatSeeker publication, 2026-04-27 17:28 Paris = 11:28 ET.

- GEX screenshot: spot ~333.20; visible tested expiry 2026-05-01; GEX King strike 350 = +2,558.2K.
- VEX screenshot: spot ~333.49; visible later expiries 2026-05-29, 2026-06-05, 2026-06-18; VEX King strike 350 = +70,477.3K on 2026-06-18.

Critical limitation: the supplied screenshots do **not** contain an overlapping expiration between GEX and VEX. Therefore this cannot test a same-contract GEX↔VEX formula. It only tests whether strike concentration persists across Greek and maturity.

## Deterministic clean sample

Common readable strike range 295–375. Excluded rows 355.0, 342.5 and 310.0 because the screenshot annotation/overlay prevents clean transcription of at least one required cell. Final n = 30.

For VEX, define per-strike `max|VEX|` as the maximum absolute displayed VEX across 2026-05-29, 2026-06-05 and 2026-06-18.

## Results

- `|GEX_2026-05-01|` vs `max|VEX|`: Spearman **+0.613**, deterministic 10k two-sided permutation **p = 0.00090**.
- Excluding the GEX King strike 350: Spearman **+0.567**, deterministic 10k permutation **p = 0.00180**.
- Partial Spearman controlling a 5-dollar-vs-2.5-dollar strike-grid indicator: **+0.521**, approximate p = **0.00313**.
- Restricting only to strikes where VEX is nonzero in at least one displayed maturity: n = 14, Spearman **+0.323**, p = **0.260**.

## Interpretation

There is a real broad alignment of strike concentration across the supplied GEX and later-maturity VEX panels, and it is not entirely explained by the shared 5-dollar strike grid. The identical dominant strike 350 is consistent with that structural overlap.

However, when the comparison is restricted to VEX-active strikes only, the association is weak and statistically unresolved in this small sample. Much of the all-strike correlation is therefore related to which strikes carry any material exposure at all, rather than a demonstrated proportional mapping between GEX and VEX magnitudes.

Conclusion: **support for a common strike-structure component; no evidence here for a direct GEX↔VEX transformation or proprietary formula.** A proper same-expiry GEX/VEX test requires screenshots with at least one identical expiration visible on both panels.

Reproduction script: `diagnose_amd_20260427_gex_vex_strike_alignment.py`.
