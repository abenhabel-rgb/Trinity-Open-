# MU 2026-06-24 H5 timestamp sensitivity — result

Status: post-hoc diagnostic only. It does not overturn the frozen H5 confirmatory FAIL.

Target card:
- MU
- Publication outer bound: 2026-06-24 11:04 ET
- Expiration: 2026-06-26
- H5 primary King excluded: strike 1000

Method:
- Same frozen_v1 quote-edge signed-flow classifier for every window.
- Same 09:30 ET start.
- Only the cumulative end time changes.
- No window selection is confirmatory.

Results, ex-King:

| End ET | Spearman(flow,GEX) | partial(flow,GEX\|cp) | sign agreement |
|---|---:|---:|---:|
| 09:45 | -0.002 | +0.059 | 0.421 |
| 10:00 | -0.293 | -0.299 | 0.400 |
| 10:15 | -0.100 | -0.039 | 0.500 |
| 10:30 | -0.404 | -0.390 | 0.350 |
| 10:45 | -0.191 | -0.188 | 0.400 |
| 11:00 | -0.152 | -0.152 | 0.450 |
| 11:04 | -0.167 | -0.166 | 0.450 |

Range only, descriptive:
- Spearman(flow,GEX): -0.404 .. -0.002
- partial(flow,GEX|cp): -0.390 .. +0.059
- sign agreement: 0.350 .. 0.500

Interpretation:
- No tested cumulative window approaches the frozen H5 gates.
- The H5 failure is not plausibly explained by choosing 11:04 ET instead of an earlier tested publication-bounded end time.
- Timestamp sensitivity is therefore not a rescue explanation for this card.
- The general incremental same-day signed-flow hypothesis remains weakened.

Next discrimination:
- Prior-close gamma is temporally valid but can be stale on an intraday card.
- Before using any reconstructed intraday gamma, validate reconstruction against ThetaData-observed Greeks under the documented ThetaData Black-Scholes convention.
