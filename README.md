# Trinity / OpenClaw

Trinity is the research core of the OpenClaw quantitative options project.

The objective is to reproduce and statistically validate deterministic market-structure signals from options gamma, flow and price interaction, with strict replay and out-of-sample testing.

## Research principles

- deterministic rules before optimization
- derive, do not read outcomes from labels
- compare every hypothesis against an explicit baseline
- measure lift, not raw hit rate alone
- freeze hypotheses before new holdout sessions
- keep replay and live logic aligned
- use Eastern Time (ET) as the market-time standard

## Initial scope

- QQQ
- SPY
- SPXW 0DTE
- later: single names

## Core research components

- gamma / node map reconstruction
- King Node, Gatekeeper and route logic
- price-to-node contact events
- opening regime classification
- FlowSeeker-style flow primitives
- replay and out-of-sample validation
- deterministic setup scoring

## Repository structure

```text
src/trinity/       Python package
research/          frozen hypotheses and research checkpoints
docs/              architecture and conventions
tests/             automated tests
data/               local-only raw/derived market data (gitignored)
```

## Current checkpoint

The frozen H2 mean-reversion hypothesis was rejected out of sample due to sign reversal. H3 (`FIXED_KING_ESCAPE`) is the next frozen hypothesis to test on fresh holdout sessions. See `research/CHECKPOINT_2026-08-17.md`.

## Safety / data policy

Raw OPRA/ThetaData files, credentials, API keys, `.env` files, local databases and large replay artifacts must never be committed to GitHub.
