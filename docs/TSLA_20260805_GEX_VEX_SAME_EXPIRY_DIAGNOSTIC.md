# TSLA 2026-08-05 — same-expiry GEX/VEX diagnostic

Status: **DIAGNOSTIC ONLY**. This is not H9/H10 material because the publication time supplied by the user was 18:54 Paris = 12:54 ET.

Source: paired HeatSeeker screenshots from the same publication snapshot, one GEX and one VEX. Spot was approximately 324.26–324.31. The same expiration columns are visible on both panels.

We transcribed the common strike block 287.5–372.5 in 2.5-point increments (35 strikes) for expirations 2026-08-05, 2026-08-07, and 2026-08-10.

## Results

### Expiration 2026-08-05
- Spearman(|GEX|, |VEX|) = **+0.986835**
- Spearman(GEX, VEX) = **+0.047619**
- Spearman(GEX × sign(K−S), VEX) = **+0.995798**
- transformed-sign agreement = **35/35** strikes

### Expiration 2026-08-07
- Spearman(|GEX|, |VEX|) = **+0.884594**
- Spearman(GEX, VEX) = **+0.009244**
- Spearman(GEX × sign(K−S), VEX) = **+0.956303**
- transformed-sign agreement = **35/35** strikes

### Expiration 2026-08-10
- Spearman(|GEX|, |VEX|) = **+0.902304**
- Spearman(GEX × sign(K−S), VEX) = **+0.960852**
- transformed-sign agreement = **35/35** strikes

## Direct observation

For every transcribed strike across all three expirations, VEX has the same sign as GEX for strikes above spot and the opposite sign for strikes below spot. Equivalently in this sample:

`sign(VEX) = sign(GEX) × sign(K − S)`

The raw signed GEX–VEX correlation is near zero because the sign flip occurs across spot, while the side-adjusted signed rank correlation is extremely high.

## Interpretation

This is strong evidence that the displayed GEX and VEX share a common strike-level position/intensity structure in this snapshot and differ by a Greek/moneyness transformation. It is consistent with the known Black-Scholes relationship in which vanna changes sign around the forward/spot region while gamma does not.

This does **not** identify Skylit's proprietary netting weights, dealer position, or full HeatSeeker formula. The exact sign boundary in theory is tied to d2/forward rather than necessarily the raw spot, so replication on additional cards is required.

The finding is materially stronger than a generic correlation: the sign rule replicated 35/35 on three separate expirations in the same snapshot.
