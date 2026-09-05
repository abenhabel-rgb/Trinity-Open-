# MU intraday gamma reconstruction — BLOCKED under Standard

Status: **BLOCKED / NOT VALIDATED**.

No frozen HeatSeeker model, gate, H1-H5 result, or raw data is modified by this note.

## What was tested

A local Black-Scholes gamma reconstruction was compared against ThetaData-observed EOD gamma for MU, with `rate_value=0`, `annual_dividend=0`, and `version=latest`.

Original validation gate (unchanged):
- at least 20 usable rows;
- median absolute relative gamma error <= 2%;
- p90 absolute relative gamma error <= 5%.

Observed on 2026-06-23, expiration 2026-06-26:
- usable rows: 458;
- median relative error: 5.3965%;
- p90 relative error: 41.0490%;
- result: **FAIL**.

## Time-convention diagnostics

Several time-to-expiry conventions were tested without HeatSeeker values.

On 2026-06-23, fixed 16:00 / full-calendar-day timing reproduced ThetaData `d1` almost exactly, while the full gamma still missed materially. This shows that the principal residual mismatch is not explained by `d1` timing alone.

A next-midnight hypothesis was then tested on an independent holdout date, 2026-06-22:
- 16:00 baseline median error: 5.6822%; p90: 40.2453%;
- next-midnight median error: 8.3283%; p90: 57.5470%;
- unchanged gate: **FAIL**.

Therefore the next-midnight convention is rejected as a rescue explanation.

## Provider-semantics limitation

ThetaData documents that its EOD Greeks endpoint is based on dedicated end-of-day reports generated after the close using closing option and underlying prices, while its intraday implied-volatility endpoint uses timestamped quote/underlying observations. Therefore EOD Greeks are not a clean one-for-one validator of an intraday gamma reconstruction.

The intraday second-order Greeks endpoint that would expose observed gamma directly is Pro-only. Under Standard, the project does not currently have an observed intraday gamma target against which to validate the reconstruction.

## Decision

Until an observed intraday gamma benchmark is available, local reconstructed intraday gamma must NOT be promoted to observed market data and must NOT be used in confirmatory HeatSeeker tests.

Allowed uses:
- ThetaData EOD gamma as observed provider data for static / pre-market structure tests;
- intraday implied-volatility fields as observed IV data;
- a local intraday gamma reconstruction only as an explicitly labeled exploratory hypothesis, never as observed gamma and never inside a frozen confirmatory gate.

## Consequence for current MU work

- H3 pre-market OI/gamma results remain valid because they use observed EOD gamma.
- H5 confirmatory FAIL remains valid and is not rescued by gamma reconstruction.
- The post-hoc H5 timestamp sweep remains descriptive only.
- Further parameter tuning against EOD gamma is stopped to avoid overfitting endpoint-specific EOD semantics.
