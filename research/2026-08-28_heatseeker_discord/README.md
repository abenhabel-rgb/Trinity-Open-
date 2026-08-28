# Discord / HeatSeeker — OOS research memo — 2026-08-28

## Scope

This memo records the 2026-08-28 Discord/HeatSeeker capture and the first reconstruction tests performed on the captured heatmaps. Raw Discord/Skylit images are intentionally **not** committed here because the repository is public and the images may contain proprietary third-party content.

## Capture status

- Target window: **15:30–16:00 Paris / 09:30–10:00 New York**.
- Effective continuous Discord/HeatSeeker coverage: **15:30:00–15:55:59 Paris**.
- Effective duration: **25 min 59 s**.
- Status: **OOS PARTIAL** (last ~4 minutes missing).
- Files in the original capture window: **1,031**.
- Unique contents by SHA-256 in the original capture window: **850**.
- ZIP subsequently analyzed after strict truncation to 15:55:59: **847 unique heatmaps**.
- 26/26 minutes between 15:30 and 15:55 represented.
- 232 distinct collection timestamps.
- Mean images per collection timestamp: ~3.65.
- Maximum images in one collection burst: 10.

Important distinction: file/collection timestamps are not treated as market timestamps. The timestamp printed inside a heatmap should be preferred when aligning market events, because Discord delivery latency is variable.

## What is directly observed in the heatmaps

The Discord feed is multiplexed across symbols and metrics rather than being a single evolving image. The same collection burst can contain, for example, GEX and VEX for the same symbol and additional symbols.

The heatmaps visibly encode:

- symbol;
- metric (for example GEX or VEX);
- spot price;
- internal market timestamp;
- strikes;
- expirations;
- signed cell values.

This means the images are potentially convertible into a structured time series of the form:

```text
timestamp, symbol, metric, spot, expiration, strike, value
```

No proxy reconstruction is considered evidence. Only directly observed heatmap values or separately validated reconstructions are admissible.

## MU replay — partial OOS sequence

The analyzed ZIP did not contain a complete MU series from 09:30 ET. The first usable synchronized MU GEX/VEX pair appears at **09:39:30 ET** and the last at **09:54:56 ET**.

Observed synchronized MU snapshots:

| Time ET | Spot | GEX | VEX |
|---|---:|---|---|
| 09:39:30 | 925.16 | yes | yes |
| 09:41:08 | 930.52 | yes | yes |
| 09:42:28 | 928.56 | yes | yes |
| 09:42:42 | 929.27 | yes | yes |
| 09:43:22 | 927.23 | yes | yes |
| 09:43:45 | 926.68 | yes | yes |
| 09:47:42 | 930.21 | yes | yes |
| 09:48:17 | 932.31 | yes | yes |
| 09:48:22 | 932.25 | yes | yes |
| 09:49:08 | 933.55 | yes | yes |
| 09:49:40 | 933.74 | yes | yes |
| 09:49:50 | 931.99 | yes | yes |
| 09:54:42 | 930.41 | yes | yes |
| 09:54:56 | 929.92 | yes | yes |

Observed spot change over this partial sequence: **925.16 → 929.92 (+4.76, ~+0.51%)**, with an observed maximum of **933.74 at 09:49:40 ET**.

### MU key 0DTE GEX observations

At approximately 09:39:30 ET:

- 950: +1.992M
- 940: +1.479M
- 917.5: +1.197M
- 930: +1.004M
- 925: -1.895M
- 900: +1.876M

At approximately 09:54:56 ET:

- 950: +2.975M
- 940: +1.352M
- 900: +1.677M
- 925: -2.183M
- 917.5: +0.998M
- 930: +1.486M

The 950 positive node remained prominent and strengthened, while the 925 negative node remained large and became more negative in magnitude.

### MU VEX observation

At approximately 09:39:30 ET, visible 0DTE VEX concentrations included approximately:

- 950: +51.9M
- 940: +21.2M
- 955: +18.2M
- 960: +10.8M
- 925: -51.3M
- 900: -54.8M

This is recorded as direct structural evidence only; it is not interpreted as a validated predictive rule.

## Candidate ratio test

A simple candidate metric was tested without using reconstructed Greeks:

```text
R = dominant positive 0DTE GEX / abs(dominant negative 0DTE GEX)
```

### MU

| Time ET | Spot | Positive node | Negative node | R |
|---|---:|---:|---:|---:|
| 09:39:30 | 925.16 | 1.992M | -1.895M | 1.05 |
| 09:41:08 | 930.52 | 2.042M | -2.005M | 1.02 |
| 09:42:28 | 928.56 | 1.973M | -1.938M | 1.02 |
| 09:42:42 | 929.27 | 2.006M | -1.937M | 1.04 |
| 09:43:22 | 927.23 | 2.116M | -1.979M | 1.07 |
| 09:43:45 | 926.68 | 2.021M | -2.064M | 0.98 |
| 09:47:42 | 930.21 | 2.511M | -2.197M | 1.14 |
| 09:48:17 | 932.31 | 2.687M | -2.179M | 1.23 |
| 09:48:22 | 932.25 | 2.708M | -2.182M | 1.24 |
| 09:49:08 | 933.55 | 2.837M | -2.209M | 1.28 |
| 09:49:40 | 933.74 | 2.942M | -2.061M | 1.43 |

The transition between 09:43:45 and 09:47:42 was initially considered a possible ARMED-like candidate, because the 950 positive node strengthened relative to the 925 negative node while price moved higher.

However, there is a ~4 minute gap in the MU snapshots at the critical transition, so the exact lead/lag relationship is not established.

## Cross-symbol controls

The same simple ratio idea was checked on additional symbols without redefining the rule to rescue MU.

### AMZN

Observed examples:

| Time ET | Spot | + dominant | - dominant | R |
|---|---:|---:|---:|---:|
| 09:38:11 | 258.70 | +27.351M | -3.191M | 8.57 |
| 09:43:33 | 258.79 | +28.036M | -0.833M | 33.67 |
| 09:53:28 | 259.57 | +36.015M | -0.779M | 46.24 |

AMZN moved **258.70 → 259.57 (~+0.34%)** while R increased sharply. This is compatible with the candidate but does not establish predictive lead because only three AMZN snapshots were available in this comparison.

### AAPL

Observed examples:

| Time ET | Spot | + dominant | - dominant | R |
|---|---:|---:|---:|---:|
| 09:38:16 | 317.21 | +17.123M | -6.445M | 2.66 |
| 09:48:10 | 315.97 | +24.338M | -1.200M | 20.28 |

AAPL therefore produced a strong contradiction to the directional interpretation: R increased by roughly 7.6x while spot declined **317.21 → 315.97 (~-0.39%)**.

### RIVN / META

Preliminary checks did not show the same MU-style transition. These controls are retained as exploratory observations only and should be re-extracted systematically before quantitative use.

## Current verdict

### OBSERVED

- Discord HeatSeeker provides multiple symbols and multiple metrics in bursts.
- GEX and VEX can be available for the same symbol and timestamp.
- Heatmaps contain signed numerical matrices, spot and internal timestamps.
- MU displayed strong persistent structural polarity around 925 negative and 940/950 positive during the observed sequence.

### TESTED / FALSIFIED

- **The simple ratio R alone is rejected as a general directional ARMED signal.**
- AAPL is the key counterexample: an extreme increase in R occurred while spot declined.

### NOT VALIDATED

- ARMED from HeatSeeker alone.
- FIRE from HeatSeeker alone.
- Direction from dominant GEX polarity alone.
- Any fixed threshold such as R > 1.10 or R > 1.15.
- Predictive lead of the MU transition.

No threshold should be introduced after observing these outcomes merely to rescue the hypothesis.

## Working architecture hypothesis

The current research direction is:

```text
HeatSeeker = structure / geometry
FlowSeeker = order-flow pressure / confirmation
Possible ARMED/FIRE = confluence, not GEX ratio alone
```

This is a hypothesis, not a validated model.

## FlowSeeker filters to investigate

Publicly visible/documented and previously observed candidate fields include:

- premium minimum;
- Calls vs Puts;
- Side: Bid / Mid / Ask and potentially above-ask / below-bid variants;
- Sweeps Only;
- Flow Score;
- Days to Expiry;
- 0DTE / OTM / ITM toggles where exposed;
- volume above OI;
- single-leg only;
- equity type (stocks / ETFs / indices);
- sector / industry;
- OI Growth where available in scanner views;
- symbol / watchlist;
- date and time constraints.

The next useful test is to align FlowSeeker observations with HeatSeeker for the same symbol and internal timestamp and determine whether MU/AMZN have order-flow confirmation that AAPL lacks.

## Infrastructure notes

- Discord/HeatSeeker silent collection on the Mac succeeded for the partial OOS window.
- Skylit/Safari automated capture did **not** succeed in the same test: the scripts logged an ARMED/waiting state but no subsequent DEBUT/start event was confirmed.
- The prior Skylit script used macOS `screencapture`, therefore it would have produced frontend PNGs rather than backend JSON/HAR even if it had started successfully.
- Future capture should start just before the market window rather than sleeping for many hours, and should use a dedicated network collector if JSON/HAR is required.
- A VPS plus an independent options data source such as ThetaData is being considered for systematic replay and validation.

## Research discipline

1. Separate **OBSERVED**, **TESTED**, **BLOCKED**, **TO TEST**, and **HYPOTHESIS**.
2. Do not use proxy calculations as evidence for Skylit internals.
3. Do not tune thresholds after opening OOS outcomes.
4. Prefer internal heatmap timestamps over local file timestamps.
5. Keep raw third-party screenshots outside this public repository unless rights/publication status are explicitly resolved.
6. Validate frontend conformity separately from backend behavioral equivalence.
7. A reconstructed backend is credible only when frozen rules reproduce unseen Skylit outputs on OOS snapshots.
