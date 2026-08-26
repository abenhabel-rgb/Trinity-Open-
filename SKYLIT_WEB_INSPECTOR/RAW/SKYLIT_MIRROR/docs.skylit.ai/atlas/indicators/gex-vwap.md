> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# GEX VWAP

> The exposure-weighted average strike of the option board, drawn on the Atlas chart as a centre line with an optional band and envelope.

GEX VWAP draws the **centre of gravity of dealer positioning** directly on the price chart. Every minute, Atlas takes the option board behind the heatmap and computes the exposure-weighted average strike — each strike weighted by the size of its exposure. The result is a line that tracks where the board's weight sits, updated minute by minute through the session.

Despite the name, this is **not a volume VWAP**. No traded share volume is involved: the weights are exposure magnitudes from the same data that powers Heatseeker and the Orbs. Price VWAP answers "where has volume traded" — GEX VWAP answers "where is the positioning centred."

## Adding the indicator

Open the chart settings panel and use the **Add** button in the Indicators section. GEX VWAP appears in the list alongside the moving averages and the other Skylit studies. Each instance gets its own settings cog and can be removed the same way.

## The lines

| Line                | What it is                                                            |
| ------------------- | --------------------------------------------------------------------- |
| Centre              | The exposure-weighted average strike across the selected board.       |
| Upper               | The same average, re-run over only the strikes **above** the centre.  |
| Lower               | The same average, re-run over only the strikes **below** the centre.  |
| Envelope (optional) | Two levels marking how far the band has reached over a chosen window. |

The upper and lower lines split the board at the **centre line itself**, not at the current price — so together they show where the weight sits on each side of the board's own midpoint. A minute where no board data exists renders as a gap rather than a stale value.

## Settings

| Setting     | Options                                       | What it controls                                                                                                                                                                                                                                                                                   |
| ----------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Expirations | **Front only** (default), 1W, 1M, 3M, 6M, All | Which expirations of the board feed the average. Front only uses the current expiration — the same board the Orbs draw by default. Wider windows fold in further-dated exposure.                                                                                                                   |
| Nodes       | **All** (default), P50, P40, P30, P25, P20    | Which strikes feed the lines. All folds every strike on the board. A P-value folds only the strikes whose exposure is at least that percent of the King Node — the same percent-of-king vocabulary as the GEX Nodes dropdown — so the lines track the drawn orb cluster instead of the full board. |
| Band        | Band + centre, Centre only                    | Show the upper/lower lines around the centre, or the centre line alone.                                                                                                                                                                                                                            |
| Envelope    | Off (default), Opening window, Session        | Draws two levels at the extremes the band has reached. **Opening window** measures the first N minutes after the 09:30 ET open (default 15, configurable 8–60) and freezes once the window closes. **Session** runs from the open and only widens through the day.                                 |

On SPXW, an additional **Trinity combine** option folds SPY and QQQ exposure into a unified SPX-priced board. It is SPXW-only because the combined board is priced in SPX terms.

## Reading notes

* The lines are computed fresh each minute from that minute's board — they are not smoothed and carry no memory, so a sudden repositioning of the board moves them immediately.
* The centre is not a price target or a signal. It marks where positioning is centred so you can see, at a glance, whether the weight sits above or below the market and how that gap evolves through the session.
* The Opening-window envelope needs at least 8 minutes of board data inside its window; a session that opens without enough data draws no envelope rather than a misleading one.
