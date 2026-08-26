> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# VWAP

> The volume-weighted average price, with up to three deviation bands, anchored to the session, week, month, quarter or year.

VWAP marks **the average price every share actually traded at** since the anchor started — each bar's price weighted by the volume that went through it. It is the level institutional desks measure their own fills against, which is what makes it a reference rather than a signal: price above it means buyers have paid up relative to the session's own average, price below it means they haven't.

This is the classic price VWAP, and it is **not** the GEX VWAP that sits beside it in the Add menu. That one weights the option board by exposure. This one weights price by traded volume. Same word, different instrument.

## Adding the indicator

Open the chart settings panel and use the **Add** button in the Indicators section. Each instance gets its own settings cog and can be removed the same way, and you can run more than one at different anchors.

## Settings

| Setting     | Options                                           | What it controls                                                                                                                                        |
| ----------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Anchor      | **Session** (default), Week, Month, Quarter, Year | When the running sum resets. Session restarts each trading day; the wider anchors carry the average across the whole period.                            |
| Source      | **hlc3** (default), Close                         | The price each bar contributes. `hlc3` is the average of the high, low and close — the classic choice, and steadier than the close alone on a wide bar. |
| Bands       | Up to three pairs, off by default                 | Each pair draws above and below the centre line, with its own colour and a soft fill.                                                                   |
| Band basis  | **Standard deviation** (default), Percent         | Volume-weighted σ, or a fixed percent offset from the line.                                                                                             |
| Multipliers | 1, 2, 3 by default                                | How far each pair sits from the centre, in σ or in percent.                                                                                             |

## Reading notes

* **Sessions stay connected across an anchor reset.** At the boundary the line jumps rather than breaking — the same way TradingView draws it. A vertical step is the reset, not a gap in the data.
* **The forming bar's value is provisional.** It folds whatever volume has printed so far in that bar, so it firms up as the bar closes. It never invents a value it cannot compute.
* **SPXW has no traded volume of its own** — the index itself doesn't trade. Its VWAP pairs SPXW's prices with **ES futures** volume, the instrument that actually trades the index, rather than an ETF stand-in. On 4h and daily anchors that weighting deliberately uses the full futures session rather than regular hours only, since a bar that wide already spans well past the cash close.
* **Replay is fully supported.** Scrub back to any day and the VWAP builds bar by bar with the tape, including its bands.
