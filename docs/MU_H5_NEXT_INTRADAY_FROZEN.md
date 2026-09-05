# MU H5 — next unseen intraday card, frozen before observation

Status: preregistered prospective discrimination test.

## Objective

Test whether same-day frozen-v1 signed dealer-flow adds directional HeatSeeker GEX information beyond a pre-existing static OI/gamma structure on the next unseen MU intraday card.

## Frozen inputs

Dynamic candidate:
- OpenClaw `volland_like_frozen_v1`
- edge fraction 0.10
- near ask -> dealer sell -> sign -1
- near bid -> dealer buy -> sign +1
- inside/locked spread -> UNKNOWN
- no call/put dealer-sign assumption
- no DAG transform

Static structure:
- OI available before the card timestamp
- gamma observed from the latest temporally valid prior-close EOD Greek snapshot
- `cp_gamma_imbalance = call_gamma*call_OI - put_gamma*put_OI`
- this is a structural contrast only, never labeled dealer position

Target:
- exact MU HeatSeeker GEX column matching the expiration under test
- publication time is only an outer bound unless an internal snapshot time is visible

## Primary analysis

Evaluate both all common strikes and ex-King.

Primary ex-King metrics:
1. Spearman(flow, GEX)
2. sign agreement(flow, GEX)
3. partial Spearman(flow, GEX | cp_gamma_imbalance)
4. permutation p-value for the partial-flow association
5. Spearman(cp_gamma_imbalance, GEX)
6. partial Spearman(cp_gamma_imbalance, GEX | flow)

## Frozen H5 gates

The next unseen intraday card passes H5 only if all ex-King conditions hold:
- sign agreement(flow, GEX) >= 0.65
- Spearman(flow, GEX) >= 0.35
- partial Spearman(flow, GEX | cp_gamma_imbalance) >= 0.35
- permutation p(partial flow) < 0.05

The static contrast is not required to fail. H5 asks whether flow retains incremental information after conditioning on it.

## Secondary diagnostics

Report but do not gate on:
- Spearman(total OI, |GEX|)
- Spearman(gammaOI_total, |GEX|)
- King-included metrics
- VEX comparisons

## Falsification rule

If the partial-flow association collapses below +0.35 or its permutation p-value is >= 0.05, do not claim an incremental dynamic flow component on that card.

No parameter, strike window, sign convention, time window, static formula, or threshold may be changed after the next card is seen.

Passing H5 would support replication of an incremental intraday flow component. It would still not identify HeatSeeker's proprietary formula or establish dealer inventory.
