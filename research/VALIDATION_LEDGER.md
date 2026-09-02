# OpenClaw Validation Ledger

## Burned cases

### META — 2026-08-28 — Direction Engine

**Status:** BURNED

**Scope:** Direction Engine validation only.

**Reason:** The post-confirmation price path and intraday volume behavior were already inspected before the Direction Engine rules were frozen. The session was also used to discuss candidate directional rules such as pivot rejection, breakout/breakdown confirmation, volume confirmation, and a provisional SELL interpretation.

**Allowed use:**
- framework development;
- debugging;
- code verification;
- illustrative / in-sample replay.

**Prohibited use:**
- out-of-sample validation;
- hit-rate or lift statistics for Direction Engine;
- evidence that a subsequently frozen BUY/SELL rule predicted the META 2026-08-28 move.

**Rule:** A future Direction Engine version may be demonstrated on this date, but the result must always be labeled `BURNED / DEVELOPMENT ONLY` and excluded from validation statistics.
