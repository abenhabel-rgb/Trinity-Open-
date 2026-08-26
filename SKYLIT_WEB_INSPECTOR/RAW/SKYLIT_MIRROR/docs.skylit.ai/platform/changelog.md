> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Changelog

> What's new across Skylit products.

<Update label="2026-06-29" tags={["Platform", "API"]}>
  ## Skylit API: limited beta is open

  **New** · API key generation is live for limited-beta accounts. Approved users can now create and manage their own keys directly from the **Developer** tab of the [Skylit app](https://app.skylit.ai) — no more waiting on manual provisioning.

  * One key works across both Flowseeker (`flow_*`) and Heatseeker (`heat_*`) endpoints, plus the [Skylit MCP Server](/mcp/overview).
  * Rotate or revoke keys at any time from the Developer tab.
  * Access is still gated while we expand the beta — reach out if you'd like to be considered.

  Banners across the [API reference](/api-reference/introduction), [authentication guide](/api-reference/authentication), and [Skylit MCP](/mcp/overview) pages have been updated to reflect the new flow.
</Update>

<Update label="2026-06-29" tags={["Flowseeker"]}>
  ## Skylit MCP Server

  **New** · Connect Claude, Cursor, or any [Model Context Protocol](https://modelcontextprotocol.io) client directly to Skylit's options-flow and dealer-positioning data. Ask questions in natural language and let your agent call the right tools.

  * **Unified gateway** at `https://mcp.skylit.ai/mcp` — one API key covers Flowseeker (`flow_*`) and Heatseeker (`heat_*`).
  * **38 tools** spanning scored options trades, sweeps, tide, momentum, moneyness, ratios, sector and market-wide flow, plus live and historical gamma/vanna heatmaps.
  * **Drop-in setup** for Cursor and Claude Desktop, with a raw HTTP/JSON-RPC walkthrough for custom clients.
  * **Per-call credit costs** match the equivalent REST endpoints, with remaining balance returned in every result.

  <Note>
    The Skylit API is in limited beta. Approved accounts can create and manage keys in the **Developer** tab of the [Skylit app](https://app.skylit.ai).
  </Note>

  Learn more:

  * [MCP Server overview](/mcp/overview)
  * [Quickstart](/mcp/quickstart)
  * [Tool catalog](/mcp/tools)
  * [Example prompts](/mcp/examples)

  ***

  ## Flowseeker API reference refreshed

  **Updated** · The [Flowseeker API reference](/flowseeker/overview) is back in sync with production. Endpoints, schemas, and parameters now reflect the current Flowseeker service — previous copies of the spec had fallen behind.
</Update>
