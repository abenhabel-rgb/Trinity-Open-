> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# TPO (Market Profile)

> A letter-per-bar Market Profile with Point of Control, Value Area, single prints, an Initial Balance, and persisting naked levels.

TPO builds the classic **Market Profile**: for every bar, a letter is stamped onto each price row that bar traded through. Rows visited often grow wide; rows the market passed through once stay a single character. What the profile measures is **time at price**, not volume — which is what separates it from Volume Profile sitting beside it in the Add menu. A price can hold size in one print, or hold the market for an hour; those are different facts, and this is the one that shows the second.

The shape is the point. A balanced session builds a bell around a middle it keeps returning to; a trend session builds a thin, elongated profile that barely revisits anything.

## Adding the indicator

Open the chart settings panel and use the **Add** button in the Indicators section. One TPO instance can be active per chart.

## What it draws

| Element         | What it is                                                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Letters         | One per bar per row touched. Each period gets the next letter, so the alphabet reads as the session's clock.                                |
| POC             | The Point of Control — the row with the most letters, in yellow.                                                                            |
| Value Area      | The band around the POC holding the bulk of the session's time, its letters picked out and the area shaded.                                 |
| Single prints   | Rows touched exactly once — the thin patches a market usually revisits.                                                                     |
| Initial Balance | The range of the session's opening window.                                                                                                  |
| Naked levels    | POC, Value Area and single-print levels from earlier sessions that price has **not** traded back through since. They persist until it does. |

## Settings

| Setting                            | Options                                            | What it controls                                                                                                                          |
| ---------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Type                               | **Regular** (default), Fixed Range, Fixed Interval | Recalculate every N periods, profile one explicit window, or profile a recurring daily time window.                                       |
| Period / Unit                      | **1 day** (default)                                | How often Regular starts a fresh profile — in minutes, days, weeks or months.                                                             |
| Range start                        | Blank by default                                   | Where a Fixed Range profile begins. Blank means the most recent session.                                                                  |
| Interval start / end               | 13:00–17:00 ET                                     | The recurring window Fixed Interval profiles each day.                                                                                    |
| Row size                           | **Auto** (default), Custom                         | Auto sizes rows from the instrument's own recent range, aiming for a readable profile on any symbol. Custom sets the row height in ticks. |
| Prev Sessions / Ranges / Black Box | On, on, off                                        | How much of the completed sessions to the left stays drawn.                                                                               |
| SP Lines, FR Marker, Tick Levels   |                                                    | The single-print lines, the Fixed Range start marker, and per-row gridlines.                                                              |
| Hide distance %                    | **5**                                              | Naked levels further than this from the last price are hidden, so only the ones in play are drawn.                                        |
| Text, Font, Colours                |                                                    | Letter size and family, and a colour per element.                                                                                         |

## Reading notes

* **Auto row size targets a row count, not a tick count.** A fixed tick height that reads well on a penny-tick equity collapses a quarter-tick futures profile into three rows; sizing from the instrument's own range keeps the profile legible on both.
* **POC and single prints appear from the fifth period.** Before that there is not enough of a profile for either to mean anything, so the letters draw alone.
* **On daily and higher charts the profile is a composite**: one bar is one period, so a blank Range start profiles the last twenty bars — roughly a month on a daily chart — one letter per day.
* **A completed session's naked levels appear once the next session opens**, since a level only counts as untouched after the session that made it has ended.
* **Replay is supported**, including historically correct naked levels at any point in the day.
