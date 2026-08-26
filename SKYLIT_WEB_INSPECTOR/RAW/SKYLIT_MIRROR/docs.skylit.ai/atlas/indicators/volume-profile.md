> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Volume Profile

> A price-by-price histogram of where volume actually traded, with the Point of Control and a shaded Value Area.

Volume Profile turns the chart on its side: instead of volume per bar, it shows **volume per price** — a histogram anchored to the right edge, one row per price band, over whatever lookback you set. Where the rows are long, the market spent size; where they are short, it passed through. Those thin patches are the levels price tends to travel back across quickly.

Two levels are marked on it. The **Point of Control** is the single busiest price in the window. The **Value Area** is the band around it holding the chosen share of the window's volume — 68% by default — with its upper and lower bounds badged on the price axis as VAH and VAL.

## Adding the indicator

Open the chart settings panel and use the **Add** button in the Indicators section. The profile draws behind the candles so it never hides price action.

## Settings

| Setting                 | Options                                  | What it controls                                                                                                                |
| ----------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Lookback                | **Fixed depth** (default), Visible range | Profile a set number of bars back, or whatever is currently on screen — the visible-range mode rebuilds as you scroll and zoom. |
| Depth                   | **200** bars (default)                   | How far back fixed mode reaches. Disabled under visible range, which takes its window from the viewport.                        |
| Levels                  | The row count                            | How finely the price axis is divided. More rows resolve more structure; fewer read more cleanly.                                |
| Volume                  | **Total** (default), Buy, Sell           | Which side to profile.                                                                                                          |
| Value Area              | **68%** (default)                        | The share of window volume the area must hold.                                                                                  |
| Width                   | A share of the pane                      | How far the longest row reaches across the chart.                                                                               |
| Show POC / VA / VAH-VAL | On by default                            | The level lines and their axis badges.                                                                                          |

## Reading notes

* **Buy and Sell profiles are real, not estimated.** Because the tape carries true trade sides, profiling one side alone shows where that side actually transacted — something a profile built from bar direction cannot offer.
* **A bar's volume is spread across the rows its range covers**, in proportion to how much of the bar sits in each. A bar that closes in one row lands wholly in that row.
* **Ties resolve downward for the Point of Control** and upward when the Value Area expands, matching the reference implementation traders will have used elsewhere.
* **A sparse profile's Value Area can stop short of the target percentage.** When the rows on both sides of the area hold no volume at all, it stops there rather than reaching across a gap to manufacture the number.
* **Replay is supported**: the profile fills in level by level as the day unfolds.
