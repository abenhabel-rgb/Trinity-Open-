> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Example Prompts

> Natural-language questions an agent can answer, and the tools behind them.

<div className="skylit-soon">
  <span><strong>Limited beta</strong> — the Skylit API is in limited beta. Create and manage keys in the Developer tab of the <a href="https://app.skylit.ai">Skylit app</a>.</span>
</div>

Once the [server is connected](/mcp/quickstart), just ask in plain
English — the agent picks the tools. The examples below show the typical tool
path so you know what each question costs and where the answer comes from.

## Unusual activity

> Were there any unusual bullish sweeps on TSLA today?

`flow_search` (confirm ticker) → `sweeps` and/or `unusual_volume`, filtered to
calls. The agent summarizes premium, venues, and Flow Score.

> Which tickers had the most unusual options volume this week, excluding the indices?

`unusual_volume` with `exclude_tickers=SPY,QQQ,IWM` — or `top_contracts_weekly`
for a premium-ranked list.

## Directional read on a name

> Is the flow on NVDA bullish or bearish right now, and how strong?

`aggregate_score` (Composite + VWF/SDF/FIR across timeframes), often paired with
`flow_momentum` for a "vs baseline" read and `chain_bull_bear` to separate call
buying from put selling.

> Show me where the premium is concentrated by strike on SPY this afternoon.

`flow_strikes` (or `by_strike`) over the session window.

## Positioning & accumulation

> Is the OTM call activity on AMD new positioning or closing flow?

`vol_oi` (accumulation score + new-position estimate) and `unusual_oi`
(opening vs closing direction).

> What does the AAPL chain look like for the Jan 17 expiration?

`expirations` (find the date) → `option_chain` for that expiration.

## Market-wide

> What's the overall market tone today — risk-on or risk-off?

`market_breadth` for the one-line read, `market_overview` and `market_tide` for
the supporting detail.

> Which sector is seeing the strongest call flow?

`market_breadth` (per-sector rotation) → `sector_flow` to drill into the leader.

## Dealer positioning (Heatseeker)

> Where are the gamma walls on SPY right now?

`heat_heatmap` for the current per-strike gamma exposure + live velocity.

> What did the SPY gamma profile look like at the open on March 5?

`heat_historical_heatmap` with `at=2026-03-05T14:30:00Z`.

## Combining both products

> SPY has a gamma wall at 600 — is the flow defending it or pushing through?

`heat_heatmap` (locate the wall) → `flow_strikes` / `flow_tide` around that strike
to see whether premium is accumulating into or fading away from it. This pairing —
positioning from Heatseeker, intent from Flowseeker — is the core reason the two
products share one gateway and one key.

<Tip>
  Agents work best when you give them a ticker and a timeframe. "TSLA, last hour"
  beats "show me some flow." If a result looks empty, ask the agent to widen the
  window or lower the `min_premium` filter.
</Tip>
