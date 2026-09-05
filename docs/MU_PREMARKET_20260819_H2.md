# MU 2026-08-19 premarket card — falsification note and exploratory H2

## Observed timing

User-reported publication time: 2026-08-19 13:25 Europe/Paris = 07:25 America/New_York.

The card therefore predates the 09:30 ET regular-session open.

Observed card state:
- symbol: MU
- card date / nearest expiration shown: 2026-08-19
- displayed spot: about 942.37 (VEX view) / 942.81 (GEX view)
- GEX King: strike 1000, +8,879.6K on the 2026-08-19 expiration
- VEX King: strike 1000, +549,802.9K on the 2026-08-19 expiration

## Consequence for frozen H1

Frozen H1 uses same-day signed dealer flow from 09:30 ET to publication time as an outer-bound collection window.

That protocol cannot be applied to a card published at 07:25 ET because there is no same-day regular-session trade window yet.

This is falsification pressure against any strong interpretation that the premarket HeatSeeker map is generated from same-day option prints.

Do not alter frozen H1 to force-fit this card.

## Exploratory H2 — prior-session carry

Before inspecting ThetaData results for 2026-08-18, freeze the following exploratory test:

- target: HeatSeeker GEX 2026-08-19 expiration by strike from the premarket 2026-08-19 card
- candidate: conservative signed dealer flow from the previous regular session, 2026-08-18 09:30:00–16:00:00 ET, for options expiring 2026-08-19
- classifier: exactly frozen_v1 edge=0.10 quote-edge logic
- no call/put dealer-sign assumption
- no DAG transform in the primary test
- baseline: raw contract volume by strike
- secondary baseline: raw trade count
- metrics: Spearman(flow,GEX), sign agreement, Spearman(volume,GEX), directional lift = Spearman(flow,GEX)-Spearman(volume,GEX)
- report all-common and ex-King 1000

This H2 is exploratory development because it was motivated by seeing the premarket card. It is not confirmatory even if it passes.

If H2 looks promising, it must be frozen and tested on another untouched premarket MU card before any confirmation claim.
