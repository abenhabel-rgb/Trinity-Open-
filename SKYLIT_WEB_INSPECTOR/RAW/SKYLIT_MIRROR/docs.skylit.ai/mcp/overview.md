> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# MCP Server

> Connect an AI agent to Skylit's options-flow and dealer-positioning data over the Model Context Protocol.

<div className="skylit-soon">
  <span><strong>Limited beta</strong> — the Skylit API is in limited beta. Create and manage keys in the Developer tab of the <a href="https://app.skylit.ai">Skylit app</a>.</span>
</div>

The **Skylit MCP server** lets an AI agent — Claude, Cursor, or any
[Model Context Protocol](https://modelcontextprotocol.io) client — query Skylit's
market data directly, in natural language. Ask *"were there unusual bullish
sweeps on TSLA on Friday?"* and the agent calls the right tool, reads the result,
and answers.

It is a **single unified gateway** over both Skylit products:

* **Flowseeker** (`flow_*`, plus screeners and stats) — scored options trades,
  sweeps, tide, momentum, moneyness, ratios, sector and market-wide flow.
* **Heatseeker** (`heat_*`) — live and historical per-strike gamma/vanna
  heatmaps.

One API key works across both. See the [full tool catalog](/mcp/tools).

## Endpoint

```
https://mcp.skylit.ai/mcp
```

The transport is **streamable HTTP** (JSON-RPC over `POST`, responses as
Server-Sent Events). Most MCP clients only need the URL plus your key — see the
[quickstart](/mcp/quickstart).

<Note>
  Every tool call costs the **same credits** as the equivalent REST endpoint. The
  per-tool cost is listed in the [tool catalog](/mcp/tools), and each
  result's `meta` carries your remaining credit balance.
</Note>

## Authentication

Supply your Skylit API key on the MCP connection — either header works, and the
same key spans both products:

```bash theme={null}
Authorization: Bearer <your-api-key>
# or
X-API-Key: <your-api-key>
```

<Warning>
  Treat API keys like passwords. Never commit them to source control or paste them
  into a shared agent prompt. Use environment variables and rotate a key if it leaks.
</Warning>

## Guardrails

To keep agent sessions predictable, the gateway enforces a **per-session call
budget** and an **in-flight concurrency limit**. If a session exceeds them, the
tool returns an error explaining the limit rather than running unbounded — credits
are only ever debited for calls that actually reach the data API.

<CardGroup cols={2}>
  <Card title="Quickstart" icon="rocket" href="/mcp/quickstart">
    Connect Claude Desktop or Cursor in a couple of minutes.
  </Card>

  <Card title="Tool catalog" icon="wrench" href="/mcp/tools">
    All 38 tools, grouped, with credit costs.
  </Card>

  <Card title="Example prompts" icon="messages-square" href="/mcp/examples">
    What to ask, and which tools answer it.
  </Card>

  <Card title="REST API Reference" icon="code" href="/flowseeker/overview">
    Prefer plain HTTP? Use the same data over REST.
  </Card>
</CardGroup>
