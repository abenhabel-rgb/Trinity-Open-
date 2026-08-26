> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Tool Catalog

> Every Skylit MCP tool, grouped by purpose, with its credit cost.

<div className="skylit-soon">
  <span><strong>Limited beta</strong> — the Skylit API is in limited beta. Create and manage keys in the Developer tab of the <a href="https://app.skylit.ai">Skylit app</a>.</span>
</div>

The server exposes **40 tools**. Each call costs the same credits as the
equivalent REST endpoint; the cost is shown per tool below and your remaining
balance is returned in each result's `meta`.

Every tool wraps a Skylit REST endpoint **1:1** — same auth, same credit cost,
same JSON. The **Endpoint** column gives the underlying path; for the full
request parameters and response schema of any endpoint, see the
[API Reference](/api-reference/introduction). For example, `flow_feed` is the
[`GET /v1/flow/{ticker}`](/api-reference/flow/raw-flow-feed-for-a-ticker-flow-score-+-flowbonus-per-trade)
operation. The `heat_*` tools map to the Heatseeker heatmap endpoints
(`api.skylit.ai`); everything else maps to Flowseeker (`flow-api.skylit.ai`).

<Info>
  Tools that take a single option contract expect an **OPRA symbol** in URL-safe
  form: `{ticker}__{YYMMDD}{C|P}{strike×1000, 8 digits}` — e.g.
  `AAPL__260117C00250000`. Discover tickers with `flow_search` and expirations with
  `expirations` first.
</Info>

## Discovery

Find valid symbols and the active universe before calling analytics tools.

| Tool                      | Returns                                                            | Endpoint                                  | Credits |
| ------------------------- | ------------------------------------------------------------------ | ----------------------------------------- | ------: |
| `flow_search`             | Search underlyings by ticker fragment                              | `GET /v1/underlying/search`               |       1 |
| `list_active_underlyings` | Every underlying that traded options on a date, ranked by premium  | `GET /v1/underlying`                      |       1 |
| `expirations`             | Available expiration dates for an underlying, with contract counts | `GET /v1/underlying/{ticker}/expirations` |       1 |

## Scores & trades

Scored options flow for a ticker or a single trade.

| Tool              | Returns                                                               | Endpoint                          | Credits |
| ----------------- | --------------------------------------------------------------------- | --------------------------------- | ------: |
| `flow_feed`       | Recent scored trades (Flow Score, FlowBonus) + VWF/SDF/FIR aggregates | `GET /v1/flow/{ticker}`           |       1 |
| `trade_score`     | Full scoring + context for one trade id (from a `flow_feed` row)      | `GET /v1/score/{trade_id}`        |       1 |
| `aggregate_score` | Composite + VWF/SDF/FIR across one or more trailing timeframes        | `GET /v1/aggregate/{ticker}`      |       3 |
| `flow_aggregate`  | Server-side rollup over an arbitrary `[start_time, end_time]` window  | `GET /v1/flow/{ticker}/aggregate` |       3 |

## Sweeps & momentum

| Tool            | Returns                                                                 | Endpoint                         | Credits |
| --------------- | ----------------------------------------------------------------------- | -------------------------------- | ------: |
| `sweeps`        | Aggregated multi-exchange sweeps with venues, premium, moneyness, score | `GET /v1/sweeps/{ticker}`        |       3 |
| `flow_momentum` | Live 5m/30m/1h flow vs trailing baseline, with z-scores + trend label   | `GET /v1/flow/{ticker}/momentum` |       3 |
| `flow_baseline` | Trailing per-time-of-day baseline `flow_momentum` compares against      | `GET /v1/flow/{ticker}/baseline` |       3 |

## Strike & tide concentration

| Tool           | Returns                                                              | Endpoint                                | Credits |
| -------------- | -------------------------------------------------------------------- | --------------------------------------- | ------: |
| `flow_strikes` | Top-N strikes by net/total premium with bull/bear split + OI context | `GET /v1/flow/{ticker}/strikes`         |       3 |
| `flow_tide`    | Bucketed bullish vs bearish premium with cumulative net premium      | `GET /v1/flow/{ticker}/tide`            |       3 |
| `by_strike`    | Strike-level distribution of a day's flow, optionally by DTE band    | `GET /v1/underlying/{ticker}/by-strike` |       3 |

## Screeners

Single-day and weekly top lists, plus unusual-activity scanners.

| Tool                     | Returns                                                                 | Endpoint                          | Credits |
| ------------------------ | ----------------------------------------------------------------------- | --------------------------------- | ------: |
| `top_underlyings_daily`  | Top underlyings by single-day flow (call/put split, net premium, ratio) | `GET /v1/underlying/top/daily`    |       1 |
| `top_underlyings_weekly` | Same, over the trailing week                                            | `GET /v1/underlying/top/weekly`   |       1 |
| `top_contracts_daily`    | Single-day top-contract screener (premium / volume / OI / sweeps)       | `GET /v1/contract/top/daily`      |       1 |
| `top_contracts_weekly`   | Same, over the trailing week                                            | `GET /v1/contract/top/weekly`     |       1 |
| `unusual_volume`         | Contracts with anomalous volume vs an `avg_period` baseline (RVOL)      | `GET /v1/contract/unusual-volume` |       3 |
| `unusual_oi`             | Contracts with significant open-interest changes (opening vs closing)   | `GET /v1/contract/unusual-oi`     |       3 |

## Bull/bear & pressure ratios

| Tool                 | Returns                                                                | Endpoint                              | Credits |
| -------------------- | ---------------------------------------------------------------------- | ------------------------------------- | ------: |
| `chain_bull_bear`    | Chain-level bull/bear/neutral % with call- and put-only breakdowns     | `GET /v1/chain-bull-bear/{ticker}`    |       3 |
| `contract_bull_bear` | Bull/bear/neutral % for a single OPRA contract                         | `GET /v1/contract-bull-bear/{symbol}` |       1 |
| `chain_ratio`        | Chain-level ask/bid/mid + aggression ratios with a bias interpretation | `GET /v1/chain-ratio/{ticker}`        |       1 |
| `contract_ratio`     | Same bid/ask/mid pressure for a single OPRA contract                   | `GET /v1/contract-ratio/{symbol}`     |       1 |

## Stats, Vol/OI & moneyness

| Tool               | Returns                                                                  | Endpoint                            | Credits |
| ------------------ | ------------------------------------------------------------------------ | ----------------------------------- | ------: |
| `underlying_stats` | Daily aggregate stats for an underlying (premium, volume, net, OI)       | `GET /v1/underlying/{ticker}/stats` |       1 |
| `contract_stats`   | Daily aggregate stats for a contract (volume, OI, premium, IV)           | `GET /v1/contract/{symbol}/stats`   |       1 |
| `vol_oi`           | Vol/OI accumulation analysis; distinguishes new positioning from closing | `GET /v1/vol-oi/{ticker}`           |       1 |
| `moneyness`        | Premium/sentiment split across deep\_itm…deep\_otm + detected patterns   | `GET /v1/moneyness/{ticker}`        |       1 |

## Chains, charts & RVOL

| Tool               | Returns                                                                  | Endpoint                            | Credits |
| ------------------ | ------------------------------------------------------------------------ | ----------------------------------- | ------: |
| `option_chain`     | Full chain at an expiration (per-strike call/put volume, OI, premium)    | `GET /v1/underlying/{ticker}/chain` |       3 |
| `underlying_chart` | Intraday OHLC-style bars for an underlying                               | `GET /v1/underlying/{ticker}/chart` |       3 |
| `contract_chart`   | Intraday OHLC-style bars for a single contract                           | `GET /v1/contract/{symbol}/chart`   |       3 |
| `underlying_rvol`  | Relative-volume bars for an underlying (`format=summary` for stats only) | `GET /v1/underlying/{ticker}/rvol`  |       1 |
| `contract_rvol`    | Relative-volume bars for a single contract                               | `GET /v1/contract/{symbol}/rvol`    |       1 |

## Market-wide & sector

| Tool              | Returns                                                       | Endpoint                       | Credits |
| ----------------- | ------------------------------------------------------------- | ------------------------------ | ------: |
| `market_overview` | Market-wide flow for the day + top tickers by premium         | `GET /v1/market/overview`      |       3 |
| `market_tide`     | Bucketed net call/put premium time series with an SPY overlay | `GET /v1/market/tide`          |       3 |
| `market_breadth`  | SPY/QQQ/IWM sentiment, advance/decline, per-sector rotation   | `GET /v1/flow/market-breadth`  |       3 |
| `sector_flow`     | Sector/industry flow aggregation with top-contributor tickers | `GET /v1/flow/sector/{sector}` |       3 |

## Dark pool

Off-exchange (TRF) prints. No side / BBO / greeks — these are raw block prints.

| Tool                   | Returns                                                                                                                              | Endpoint                                | Credits |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------- | ------: |
| `dark_pool_trades`     | Paginated off-exchange prints (filters: tickers / date range / notional / venue / sector); `$1M+` by default, span capped at 31 days | `GET /v1/dark-pool/trades`              |       5 |
| `dark_pool_top_prints` | Top-N largest prints for a ticker over a trailing window, ordered by notional                                                        | `GET /v1/dark-pool/top-prints/{ticker}` |       3 |

## Heatseeker — gamma/vanna heatmaps

| Tool                      | Returns                                                               | Endpoint             | Credits |
| ------------------------- | --------------------------------------------------------------------- | -------------------- | ------: |
| `heat_heatmap`            | Current per-strike gamma/vanna heatmap + live velocity (multi-symbol) | `GET /v1/heatmap`    |       1 |
| `heat_historical_heatmap` | Replay the heatmap at a past instant (up to 365 days back)            | `GET /v1/historical` |       5 |

<Note>
  `heat_heatmap` accepts comma-separated `symbols` (e.g. `SPY,SPX,QQQ`) for a single
  cross-asset call — handy for finding gamma/vanna walls across correlated names at once.
</Note>
