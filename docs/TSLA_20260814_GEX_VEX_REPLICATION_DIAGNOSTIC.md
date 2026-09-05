# TSLA 2026-08-14 — GEX/VEX replication diagnostic

Source: paired HeatSeeker screenshots published 2026-08-14 at 13:31 Paris (07:31 ET). GEX spot 341.69; VEX spot 341.87, so the panels are quasi-simultaneous rather than the exact same underlying tick.

Status: DIAGNOSTIC ONLY. Not H9/H10.

Common fully legible strikes: 37, from 302.5 to 392.5.

For each visible shared expiration, compare GEX and VEX on identical strike rows. Define transformed GEX as `GEX * sign(K - spot)` using spot 341.78 (midpoint of the two displayed spots).

Results:

| Expiration | Spearman |GEX| vs |VEX| | Spearman raw signed GEX vs VEX | Spearman transformed GEX vs VEX | Sign agreement transformed/VEX |
|---|---:|---:|---:|---:|
| 2026-08-14 | +0.865 | +0.023 | +0.930 | 36/37 |
| 2026-08-17 | +0.868 | +0.091 | +0.961 | 37/37 |
| 2026-08-19 | +0.887 | -0.081 | +0.966 | 36/37 |

Across the three expirations, 109/111 strike-expiration observations match the moneyness sign rule. The two mismatches are strike 327.5 on 2026-08-14 and strike 302.5 on 2026-08-19 (the latter has GEX only +0.1K).

Interpretation: this independently replicates, on another TSLA date, a very strong common strike structure between GEX and VEX and a sign relation consistent with a moneyness-dependent transformation. It does not identify Skylit's proprietary formula or a dealer sign convention. Same ticker means this is temporal replication, not cross-ticker replication.
