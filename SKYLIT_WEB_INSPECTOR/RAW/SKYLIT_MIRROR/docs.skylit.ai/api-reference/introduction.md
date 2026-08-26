> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# API Reference

> Skylit's real-time options-Greeks heatmaps as a versioned HTTP API.

<div className="skylit-soon">
  <span><strong>Limited beta</strong> — the Skylit API is in limited beta. Create and manage keys in the Developer tab of the <a href="https://app.skylit.ai">Skylit app</a>.</span>
</div>

The **Skylit Public API** exposes the same real-time options-Greeks (gamma / vanna)
heatmaps that power Heatseeker — per strike, with the live velocity metric and
Skylit's node classification (King, Gatekeeper, Pika, Barney, and more).

<CardGroup cols={2}>
  <Card title="Live heatmap" icon="activity" href="/api-reference/heatmap/live-per-strike-heatmap-one-or-more-symbols">
    Current per-strike heatmap for one or more symbols, including live `velocityPct`.
  </Card>

  <Card title="Historical replay" icon="rewind" href="/api-reference/heatmap/replay-per-strike-heatmap-at-a-past-instant-one-or-more-symbols">
    The snapshot nearest any past instant — up to 365 days back.
  </Card>

  <Card title="Live stream (SSE)" icon="radio" href="/api-reference/heatmap/live-sse-stream-one-symbol-per-connection">
    A Server-Sent Events feed of live heatmap updates, one symbol per connection.
  </Card>

  <Card title="Authentication" icon="key" href="/api-reference/authentication">
    Bearer API keys, credit metering, and rate limits.
  </Card>

  <Card title="Use it over MCP" icon="plug" href="/mcp/overview">
    Every endpoint here is also an MCP tool (`heat_*`) — query it from Claude or
    Cursor in natural language, same key and credits.
  </Card>
</CardGroup>

## Base URL

```bash theme={null}
https://api.skylit.ai
```

## Quickstart

<Steps>
  <Step title="Get an API key">
    Generate a key from your [account console](https://app.skylit.ai). New accounts are
    seeded with **5,000 credits**.
  </Step>

  <Step title="Fetch a live heatmap">
    Pull the current per-strike gamma heatmap for SPY:

    <CodeGroup>
      ```bash cURL theme={null}
      curl "https://api.skylit.ai/v1/heatmap?symbols=SPY&metric=gamma" \
        -H "Authorization: Bearer sk_live_your_key"
      ```

      ```python Python theme={null}
      import requests

      r = requests.get(
          "https://api.skylit.ai/v1/heatmap",
          params={"symbols": "SPY", "metric": "gamma"},
          headers={"Authorization": "Bearer sk_live_your_key"},
      )
      print(r.json()["data"]["symbols"][0]["strikes"][:3])
      ```

      ```javascript Node theme={null}
      const res = await fetch(
        "https://api.skylit.ai/v1/heatmap?symbols=SPY&metric=gamma",
        { headers: { Authorization: "Bearer sk_live_your_key" } },
      );
      const { data } = await res.json();
      console.log(data.symbols[0].strikes.slice(0, 3));
      ```
    </CodeGroup>
  </Step>

  <Step title="Go cross-asset">
    Comma-separate symbols for a single **Trinity** call — `symbols=SPY,SPX,QQQ` — and
    each comes back as an element of `data.symbols`.
  </Step>
</Steps>

## How responses look

Every success returns a `data` / `meta` envelope; errors return an `error` object. Fields are camelCase.

```json theme={null}
{
  "data": {
    "symbols": [
      {
        "symbol": "SPY",
        "asOf": "2026-05-22T14:31:00Z",
        "spot": 591.23,
        "strikes": [
          { "strike": 590, "value": 1894300.4, "nodeType": "king", "velocityPct": 12.4 },
          { "strike": 595, "value": 642100.2, "nodeType": "gatekeeper", "velocityPct": -3.1 }
        ]
      }
    ]
  },
  "meta": { "metric": "gamma", "resolution": "1m", "mode": "live", "cached": false }
}
```

<ResponseField name="Node types" type="king · gatekeeper · pika · barney · significant · normal">
  Each strike carries Skylit's node classification — the same vocabulary used throughout
  [Patternpedia](/patternpedia/pattern-the-whipsaw).
</ResponseField>

<ResponseField name="velocityPct" type="live only">
  Present on `/v1/heatmap`; omitted on `/v1/historical` (velocity is a live metric).
</ResponseField>

<ResponseField name="Credits" type="metered per request">
  `/v1/heatmap` costs 1, `/v1/historical` costs 5, `/v1/stream` 1 per minute open.
  Every response carries `X-Credits-Remaining`. See [Authentication](/api-reference/authentication).
</ResponseField>
