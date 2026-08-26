> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Flowseeker

> Real-time and historical options-flow analytics for the Skylit platform.

Flowseeker is Skylit's options-flow workspace. It brings live and historical options activity into focused views for reviewing individual prints, contract-level activity, ranked flow boards, dark-pool prints, and saved contracts.

The product is organized around a simple idea: different flow questions need different surfaces. Live Feed is built for print-level review. Flow Scanner is built for contract-level aggregation. Contract Lookup and Contract Drilldown are built for focused research. Flow Tracker stores flow and contracts users want to revisit.

Use Flowseeker inside the Skylit app for live review, or connect to the same data programmatically through the **API Reference** and [MCP Server](/mcp/overview). Developer access uses the same Skylit API key and credit model across REST and MCP.

<Note>
  This page covers product guidance for Flowseeker: what the main surfaces are, how the primary controls work, and what users should understand before configuring filters or interpreting flow. The Flowseeker Academy module inside Skylit Terminal covers deeper applied walkthroughs and examples.
</Note>

<CardGroup cols={2}>
  <Card title="Launch Flowseeker" icon="activity" href="https://app.skylit.ai">
    Live feed, flow scanner, dark feed, compass, and contract research in the Skylit app.
  </Card>

  <Card title="Use it over MCP" icon="plug" href="/mcp/overview">
    Query Flowseeker from Claude or Cursor in natural language.
  </Card>

  <Card title="Pair with Heatseeker" icon="flame" href="/introduction">
    Combine flow with real-time dealer-positioning heatmaps.
  </Card>
</CardGroup>

| Surface            | What it shows                                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Live Feed          | Individual options-flow prints with contract, pricing, side, premium, volume, open interest, and related context. |
| Dark Feed          | Dark-pool equity prints with price, size, notional value, and sector.                                             |
| Flow Scanner       | Aggregated contract activity across volume, premium, open interest, price movement, and side composition.         |
| Flow Compass       | Ranked discovery boards that surface contracts matching specific flow categories.                                 |
| Contract Lookup    | Ticker and contract search with top-volume, top-premium, open-interest, and unusual-activity lists.               |
| Contract Drilldown | Detailed charts and tables for a selected contract.                                                               |
| Flow Tracker       | Saved flow prints and saved contracts.                                                                            |
| Settings           | API keys, Discord sharing, and Flowseeker configuration.                                                          |

***

# Live Feed

Live Feed is the primary print-level view in Flowseeker. Each row represents options activity with timing, contract details, execution context, premium, volume, open interest, implied volatility, and related market data.

<img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/flowseeker-live-feed.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=a5dd3405ffd82f037b5f33ad1482d8c8" alt="Flowseeker Live Feed" width="1280" height="720" data-path="images/flowseeker-live-feed.png" />

Users can review Live Feed in live mode or historical mode. Live mode updates as new prints appear. Historical mode lets users revisit flow from a selected trade date or date range.

***

## Top controls

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-16.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=798bd556957bb1ea2ed1c3b24814a233" alt="Image" width="1280" height="720" data-path="images/image-16.png" />
</Frame>

| Control           | Purpose                                                   |
| ----------------- | --------------------------------------------------------- |
| Feed tabs         | Switch between saved Live Feed layouts.                   |
| Ticker search     | Narrow the view by ticker.                                |
| Live / Historical | Switch between real-time flow and historical flow review. |
| Results           | Control how many rows are shown.                          |
| Sort By           | Choose the active sort field.                             |
| Filters           | Open the filter drawer.                                   |
| Columns           | Choose which columns appear in the table.                 |
| Share             | Share the current view where sharing is available.        |

***

## Summary metrics

| Metric                | Meaning                                                         |
| --------------------- | --------------------------------------------------------------- |
| Directional sentiment | A broad bullish or bearish readout for the active flow context. |
| Net premium           | Net premium represented by the active view.                     |
| FIR                   | Flow imbalance ratio or related flow-imbalance readout.         |
| Calls / Puts          | Call-side and put-side volume and premium totals.               |
| P/C                   | Put/call ratio for the active view.                             |
| RVOL                  | Relative volume for the active view.                            |

## Live Feed columns

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-14.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=e4394e026719ea364cda272411cf3f41" alt="Image" width="1280" height="720" data-path="images/image-14.png" />
</Frame>

| Column              | Meaning                                                                          |
| ------------------- | -------------------------------------------------------------------------------- |
| Date / Time         | When the print occurred.                                                         |
| Ticker              | Underlying symbol.                                                               |
| Strike              | Contract strike price.                                                           |
| C/P                 | Call or put.                                                                     |
| OTM                 | How far the contract is out of the money or in the money, shown as a percentage. |
| Exp / DTE           | Expiration date and days to expiration.                                          |
| Fill / Spread       | Reported fill price and bid/ask spread around the print.                         |
| Side                | Where the print occurred relative to bid, mid, ask, below bid, or above ask.     |
| Flow Score          | Directional score assigned to the print.                                         |
| Size / Prem         | Number of contracts and premium represented by the print.                        |
| Vol / OI / Delta OI | Contract volume, open interest, and open-interest change when available.         |
| Spot / IV / V/OI    | Underlying price, implied volatility, and volume relative to open interest.      |
| Strategy / Earnings | Detected strategy label and earnings timing when available.                      |

<Note>
  Side describes where activity occurred relative to the market. It should not be read as perfect proof of buyer or seller intent.
</Note>

***

## Filters and Columns

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-19.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=3373596050d04e4bae32d424bf84d16c" alt="Image" width="1280" height="720" data-path="images/image-19.png" />

  Filters control the flow universe shown in the current view. Filter choices can be saved to the active tab, which makes it possible to keep multiple Live Feed layouts for different review contexts.
</Frame>

***

## Filter groups

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-18.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=413465a1a597b52e798cefc29cbd756d" alt="Image" width="1280" height="720" data-path="images/image-18.png" />
</Frame>

| Filter                        | What it controls                                                         |
| ----------------------------- | ------------------------------------------------------------------------ |
| Ticker                        | Includes or narrows by underlying symbol.                                |
| Type                          | Shows all options, calls only, or puts only.                             |
| Flow Score                    | Filters by positive, negative, or absolute score ranges.                 |
| Side                          | Filters bid, mid, ask, below-bid, or above-ask activity.                 |
| Equity Type                   | Includes or excludes stocks, ETFs, and indices.                          |
| Trade Date / Expiry Date      | Controls trade date and contract expiration scope.                       |
| DTE                           | Filters by minimum and maximum days to expiration.                       |
| Premium, OI, Volume, Size     | Filters by transaction and contract activity levels.                     |
| Vol/OI                        | Filters by volume relative to open interest.                             |
| % OTM                         | Filters by moneyness.                                                    |
| Stock, strike, contract price | Filters by underlying price, strike price, or contract price.            |
| Earnings / IV                 | Filters by earnings timing, implied volatility, or IV expansion metrics. |
| Sector / Industry             | Narrows flow by company classification.                                  |

***

## Special toggles

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-20.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=c90864529aec9190fbcdf8b3effcf769" alt="Image" width="1908" height="925" data-path="images/image-20.png" />
</Frame>

| Toggle           | What it does                                         |
| ---------------- | ---------------------------------------------------- |
| Volume > OI      | Shows contracts where volume exceeds open interest.  |
| Size > OI        | Shows prints where print size exceeds open interest. |
| Exclude Deep ITM | Removes deep in-the-money contracts from the view.   |
| OTM Only         | Shows out-of-the-money contracts only.               |
| Multi-Leg Only   | Shows detected multi-leg flow only.                  |
| Single-Leg Only  | Shows single-leg prints only.                        |
| Sweeps Only      | Shows sweep activity only.                           |

***

# Dark Feed

Dark Feed shows dark-pool equity prints. These are off-exchange equity transactions, separate from options-flow prints. The view includes ticker search, live mode, result count, filters, columns, and sharing controls.

## Filters

<Frame caption="Open Filters from the top-right controls.">
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-22.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=38b0fab6710678707e0fbc570ae0ba1a" alt="Image" width="1635" height="925" data-path="images/image-22.png" />

  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-23.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=ee62fe8699590a50b259966b401e7348" alt="Image" width="1635" height="925" data-path="images/image-23.png" />
</Frame>

| Column      | Meaning                    |
| ----------- | -------------------------- |
| Date / Time | When the print occurred.   |
| Ticker      | Equity symbol.             |
| Price       | Print price.               |
| Size        | Number of shares.          |
| Notional    | Dollar value of the print. |
| Sector      | Sector classification.     |

<Note>
  Dark-pool prints do not include options-side context and should not be treated as bullish or bearish by default.
</Note>

***

## Flow Scanner

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-24.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=b240537d51d962b02808c8cddd1caf28" alt="Image" width="1280" height="720" data-path="images/image-24.png" />
</Frame>

Flow Scanner is the contract-level view in Flowseeker. It summarizes what is happening in a contract instead of showing every individual print.

<Frame caption="Filters and Columns can be adjusted at the top right.">
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-25.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=66a7913fbe6efae5549442138478330a" alt="Image" width="1280" height="720" data-path="images/image-25.png" />

  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-26.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=ad3b6b20e80473f4f867300df1b7c769" alt="Image" width="1635" height="925" data-path="images/image-26.png" />

  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-27.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=bd01a6c067f23216856c4cbfd814c641" alt="Image" width="3286" height="1920" data-path="images/image-27.png" />
</Frame>

The scanner is useful when users want to review contracts with notable volume, premium, open-interest changes, price movement, or bid/ask-side composition.

| Column                | Meaning                                             |
| --------------------- | --------------------------------------------------- |
| Contract              | Strike, call/put, and expiration.                   |
| DTE / Spot / %OTM     | Expiration timing, underlying price, and moneyness. |
| Avg / Last            | Average and most recent contract price.             |
| Chg% / Day%           | Contract price movement.                            |
| Vol / OI              | Contract volume and open interest.                  |
| Delta OI / Delta OI % | Open-interest change and percentage change.         |
| Prem / IV             | Accumulated premium and implied volatility.         |
| %Tot                  | Contract share of total relevant activity.          |
| Bull/Bear             | Contract-level bullish or bearish composition.      |
| Chain Bull/Bear       | Broader chain-level composition.                    |
| Contract Ratio        | Bid/ask or side-ratio context.                      |

***

## Flow Compass

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-28.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=c23ef992d33d3501a58139acd7c3d184" alt="Image" width="3286" height="1898" data-path="images/image-28.png" />
</Frame>

Flow Compass is a ranked discovery surface. It organizes contracts into boards that highlight different types of flow behavior. Each card summarizes the contract, volume multiple, expiration, DTE, volume, premium, moneyness, and ask-side percentage.

| Card field        | Meaning                                                            |
| ----------------- | ------------------------------------------------------------------ |
| Rank              | Position within the board.                                         |
| Ticker / Contract | Underlying symbol plus strike and call/put.                        |
| Multiple          | Volume or activity multiple used by the board.                     |
| Expiration / DTE  | Contract expiration and days to expiration.                        |
| Volume / Premium  | Contract activity and dollar value.                                |
| OTM / Ask %       | Moneyness and percentage of activity occurring at or near the ask. |

***

## Contract Lookup

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-29.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=f3c8d1651cad84578521ab14ca45aaf9" alt="Image" width="3286" height="1898" data-path="images/image-29.png" />
</Frame>

Contract Lookup allows users to search for a ticker or a specific options contract. A ticker-only search opens a ticker overview. A contract-style search can open a more specific contract path.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-30.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=454603650fd99b3b9f67ddd2ab002c15" alt="Image" width="3286" height="1746" data-path="images/image-30.png" />
</Frame>

Supported search patterns include ticker-only input, such as `TSLA`, and contract-style input such as `TSLA 6/20 135 C`.

| Section             | What it shows                                             |
| ------------------- | --------------------------------------------------------- |
| Spot and daily move | Current underlying price and percentage move.             |
| Calls / Puts / Net  | Call-side, put-side, and net premium context.             |
| P/C                 | Put/call ratio.                                           |
| Bullish / Bearish   | Broad composition for the lookup context.                 |
| Top Volume Today    | Contracts with the highest volume.                        |
| Top Premium Today   | Contracts with the highest premium.                       |
| Top Open Interest   | Contracts with the highest open interest.                 |
| Unusual Vol/OI      | Contracts where volume is high relative to open interest. |

***

## Contract Drilldown

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-31.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=e70eee8e60338491f60cf2b13a61522e" alt="Image" width="2864" height="1726" data-path="images/image-31.png" />
</Frame>

Contract Drilldown is the detailed view for a single options contract. It combines contract identity, selectable contract controls, contract-flow charts, premium charts, and flow-history tables.

<Frame caption="Select a flow bar to review the prints behind that flow.">
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-32.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=5b56c0e64240f10867be047a11563311" alt="Image" width="2864" height="1726" data-path="images/image-32.png" />
</Frame>

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-33.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=41c9f961e2723b75ad3fff305d7e62b4" alt="Image" width="1438" height="834" data-path="images/image-33.png" />
</Frame>

### Contract flow

| Metric          | Meaning                                         |
| --------------- | ----------------------------------------------- |
| Vol / OI        | Contract volume and open interest.              |
| Avg / Prem      | Average contract price and total premium.       |
| OTM / Vol/OI    | Moneyness and volume relative to open interest. |
| Multi           | Multi-leg percentage where available.           |
| Contract Ratio  | Bid/ask-side composition for the contract.      |
| Bid / Mid / Ask | Distribution of volume by execution area.       |

### Net premium

| Metric                       | Meaning                                                               |
| ---------------------------- | --------------------------------------------------------------------- |
| Vol / Prem / Net             | Total volume, total premium, and net premium.                         |
| NCP / NPP                    | Net call premium and net put premium.                                 |
| Net Sentiment                | Bullish/bearish premium composition.                                  |
| Call Bought / Call Sold      | Call-side premium composition.                                        |
| Put Bought / Put Sold        | Put-side premium composition.                                         |
| Flow Orders / Vol-OI History | Lower tables for print-level orders and historical contract activity. |

***

## Flow Tracker

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-34.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=a027a3b602701059866c0b4dd7527d9b" alt="Image" width="1280" height="720" data-path="images/image-34.png" />
</Frame>

Flow Tracker stores flow and contracts that a user has saved for later review. It has two modes: Tracked Flow and Tracked Contracts.

<Frame caption="Select the flow bar in tracked contracts to review the percentage change from the saved entry.">
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-36.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=a3d26bc416ac0c6b203de20c432341f1" alt="Image" width="1425" height="846" data-path="images/image-36.png" />
</Frame>

<Frame caption="Use the bookmark icon inside Contract Drilldown to track a contract.">
  <img src="https://mintcdn.com/skylit-490c28ef/QU4Pk6SK-6-klbCr/images/image-37.png?fit=max&auto=format&n=QU4Pk6SK-6-klbCr&q=85&s=9dadb9769a5312392d2ebb8e54626ee6" alt="Image" width="1717" height="888" data-path="images/image-37.png" />
</Frame>

| Mode              | What it stores                                                                |
| ----------------- | ----------------------------------------------------------------------------- |
| Tracked Flow      | Individual flow prints saved from Flowseeker, preserving print-level context. |
| Tracked Contracts | Contracts saved from Contract Drilldown or other Flowseeker surfaces.         |

| Tracked Contracts column | Meaning                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------- |
| Saved                    | Date the contract was saved.                                                       |
| Ticker                   | Underlying symbol.                                                                 |
| Strike / C/P             | Strike price and call/put.                                                         |
| Exp / DTE                | Expiration date and days to expiration.                                            |
| Mid / Spot               | Current or most recent contract midpoint and underlying spot price when available. |

***

## Flowseeker in Atlas

Flowseeker data can appear inside Atlas so users can review options-flow context directly on a chart. In Atlas, flow bars represent premium rather than raw contract volume. Calls and puts are displayed separately, and tooltips can show net flow context.

| Atlas flow setting | What it controls                                |
| ------------------ | ----------------------------------------------- |
| Single Leg Only    | Shows single-leg flow only.                     |
| Sweep Only         | Shows sweep activity only.                      |
| OTM Only           | Shows out-of-the-money contracts only.          |
| Ask Side Only      | Shows ask-side activity only.                   |
| DTE Min / Max      | Limits flow by days to expiration.              |
| Min Flow Score     | Sets the minimum Flow Score shown on the chart. |

***

## Data caveats

<Warning>
  Flowseeker provides structured market context. It should be used to review flow behavior, not as a standalone signal generator.
</Warning>

* Side is based on where activity occurs relative to bid, mid, and ask. It is not perfect proof of intent.
* A large print does not automatically mean a new directional position was opened.
* Multi-leg detection can group related prints, but not every strategy can be known with perfect certainty.
* Volume greater than open interest can be useful context, but it is not a complete thesis by itself.
* Open interest updates are not always instant and can change after the trade date.
* Dark-pool prints do not include options-side context and should not be documented as bullish or bearish by default.

***

## Field glossary

| Term                  | Definition                                                               |
| --------------------- | ------------------------------------------------------------------------ |
| Ask-side              | Activity occurring at or near the ask.                                   |
| Bid-side              | Activity occurring at or near the bid.                                   |
| Mid                   | Activity occurring near the midpoint between bid and ask.                |
| Below Bid / Above Ask | Activity reported outside the visible bid/ask range.                     |
| Premium               | Dollar value represented by options activity.                            |
| Volume                | Number of contracts traded.                                              |
| Open Interest         | Number of outstanding contracts.                                         |
| Delta OI              | Change in open interest when available.                                  |
| Vol/OI                | Volume divided by open interest.                                         |
| OTM                   | Out of the money.                                                        |
| DTE                   | Days to expiration.                                                      |
| Sweep                 | Activity that appears to execute across multiple venues or price levels. |
| Multi-leg             | Activity detected as part of a multi-leg strategy.                       |
| Contract Ratio        | Bid/ask-side composition for the contract.                               |
| NCP / NPP             | Net call premium and net put premium.                                    |

## Continue learning

For deeper applied education, use the Flowseeker Academy module inside Skylit Terminal. Academy is where Skylit teaches practical application, while public Docs remain focused on product guidance, settings, and best practices.
