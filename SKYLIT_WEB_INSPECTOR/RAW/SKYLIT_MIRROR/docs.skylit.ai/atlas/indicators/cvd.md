> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Cumulative Volume Delta

> The running buy-minus-sell volume since the anchor started, drawn as delta candles in its own pane, computed from true trade sides.

CVD draws **the running total of buying minus selling volume** since the anchor started, as candles in their own pane. It answers a question price alone cannot: whether a move is being carried by real aggressive flow or drifting on thin participation. Price making a new high while CVD does not is the classic divergence traders watch for.

Unlike TradingView's CVD, which has to **estimate** each bar's split from whether it closed up or down, ours reads the **true side of every trade** off the tape. The delta you read is the delta that actually traded.

## Adding the indicator

Open the chart settings panel and use the **Add** button in the Indicators section. CVD gets its own pane below the chart, with its own price axis.

## Settings

| Setting   | Options                                           | What it controls                                                |
| --------- | ------------------------------------------------- | --------------------------------------------------------------- |
| Anchor    | **Session** (default), Week, Month, Quarter, Year | When the running total resets to zero.                          |
| MA        | **On** (default), Off                             | A moving average over the delta, drawn in front of the candles. |
| MA type   | **SMA** (default), EMA                            | How that average is computed.                                   |
| MA period | **20** (default)                                  | Its lookback in bars.                                           |

## Reading the pane

| Element    | What it is                                                                                                                                        |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Candles    | Each bar's delta, opening where the previous one closed — so the body is that bar's own contribution and the line of closes is the running total. |
| Zero line  | A dashed level at zero, so a sign flip is obvious at a glance.                                                                                    |
| Axis badge | The current running delta, on the pane's own price axis.                                                                                          |

## Reading notes

* **Every period opens at zero**, and within a period each candle opens exactly where the last one closed. There are no hidden jumps.
* **A bar with no data emits no candle at all.** Absence stays visible rather than being drawn as a fake flat stretch.
* **CVD and the Volume pane can never disagree** about the same bar — both read the identical reconciled buy/sell figures, so a delta here always matches the net of the stack there.
* **The forming candle's wicks hold their extremes** through the sub-second updates that build them, rather than retracting as both sides grow. On intervals above one minute an intra-minute extreme can still settle back once that minute closes: sided volume is minute-granular, and the pane will not claim more precision than the data has.
* **SPXW reads ES futures flow**, for the same reason VWAP does — the index has no trades of its own.
* **Replay is fully supported**; the delta builds minute by minute as you play the day back.
