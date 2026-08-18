# Trinity Architecture

Trinity is organized so the same deterministic logic can be used for replay and live evaluation.

## Layers

1. **Data adapters** — normalize underlying, options, OI and flow inputs.
2. **Market state** — reconstruct gamma structures and time-aligned market state.
3. **Primitives** — King Node, Gatekeeper, node freshness/contact, route and flow metrics.
4. **Hypotheses** — frozen deterministic event definitions and directional predictions.
5. **Validation** — baselines, lift, holdout accounting and falsification.
6. **Runtime** — replay first; live execution later using the same primitives.

## Time convention

All market-event timestamps and replay windows use **US Eastern Time (ET)** unless explicitly documented otherwise.

## Research-to-production rule

A signal is not promoted into live logic merely because it looks plausible or has a high in-sample hit rate. It must survive a pre-registered out-of-sample test against an explicit baseline.

## Planned modules

```text
src/trinity/
  data/          adapters and normalized schemas
  gamma/         GEX/node calculations
  flow/          options-flow primitives
  market/        market state and regime
  hypotheses/    frozen deterministic hypotheses
  validation/    baseline/lift/OOS evaluation
  runtime/       replay/live orchestration
```

These directories describe the intended architecture. Implementations should only be added when their exact behavior has been specified and tested.
