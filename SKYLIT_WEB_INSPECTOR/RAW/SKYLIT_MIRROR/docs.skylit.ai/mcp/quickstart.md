> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Quickstart

> Connect Claude Desktop, Cursor, or any MCP client to the Skylit MCP server.

<div className="skylit-soon">
  <span><strong>Limited beta</strong> — the Skylit API is in limited beta. Create and manage keys in the Developer tab of the <a href="https://app.skylit.ai">Skylit app</a>.</span>
</div>

You need two things: the endpoint and your API key.

|              |                                                                         |
| ------------ | ----------------------------------------------------------------------- |
| **Endpoint** | `https://mcp.skylit.ai/mcp`                                             |
| **Auth**     | `Authorization: Bearer <your-api-key>` (or `X-API-Key: <your-api-key>`) |

Get a key from your [account console](https://app.skylit.ai), then pick your
client below.

## Cursor

Add the server to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` in a
project:

```json theme={null}
{
  "mcpServers": {
    "skylit": {
      "url": "https://mcp.skylit.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

Reload Cursor; you should see the **skylit** server connect with its tools listed.

## Claude Desktop

Claude Desktop connects to remote MCP servers in one of two ways.

<Tabs>
  <Tab title="Custom Connector (recommended)">
    In **Settings → Connectors → Add custom connector**, paste the endpoint:

    ```
    https://mcp.skylit.ai/mcp
    ```

    When prompted for authentication, provide your key as a bearer token. (Custom
    connectors require a Claude plan that supports them.)
  </Tab>

  <Tab title="Config file (mcp-remote)">
    If your build only supports local (stdio) servers, bridge to the remote
    endpoint with [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) in
    `claude_desktop_config.json`:

    ```json theme={null}
    {
      "mcpServers": {
        "skylit": {
          "command": "npx",
          "args": [
            "-y",
            "mcp-remote",
            "https://mcp.skylit.ai/mcp",
            "--header",
            "Authorization: Bearer YOUR_API_KEY"
          ]
        }
      }
    }
    ```

    Restart Claude Desktop after saving.
  </Tab>
</Tabs>

## Try it

Once connected, ask a question that maps to a tool:

> Were there any unusual bullish sweeps on TSLA today?

The agent will typically call `flow_search` to confirm the ticker, then `sweeps`
(or `unusual_volume`) and summarize. Browse [example prompts](/mcp/examples)
for more.

## Raw HTTP (for developers)

The server speaks standard MCP over streamable HTTP, so you can drive it directly.
Initialize a session, list tools, then call one:

```bash theme={null}
BASE=https://mcp.skylit.ai/mcp
KEY="Bearer YOUR_API_KEY"

# 1. initialize — returns an Mcp-Session-Id header (responses are SSE)
curl -sS "$BASE" \
  -H "Authorization: $KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize",
       "params":{"protocolVersion":"2025-06-18",
                 "capabilities":{},
                 "clientInfo":{"name":"curl","version":"0"}}}'

# 2. complete the handshake — REQUIRED before any other call.
#    Reuse the Mcp-Session-Id from step 1. Returns 202 with an empty body.
curl -sS "$BASE" \
  -H "Authorization: $KEY" -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: <id-from-initialize>" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

# 3. list tools
curl -sS "$BASE" \
  -H "Authorization: $KEY" -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: <id-from-initialize>" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'

# 4. call a tool
curl -sS "$BASE" \
  -H "Authorization: $KEY" -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: <id-from-initialize>" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call",
       "params":{"name":"flow_search","arguments":{"q":"TSLA"}}}'
```

<Note>
  Responses stream as `text/event-stream`, so send an `Accept` header that includes
  `text/event-stream`. The `notifications/initialized` call in step 2 is required —
  skip it and `tools/list` comes back empty. Send `DELETE` with the `Mcp-Session-Id`
  header to end a session. (Most MCP clients perform this handshake for you; it only
  matters when driving the server by hand.)
</Note>

<Warning>
  A `401` means the key is missing or invalid; a `403` means the key is recognized
  but its plan doesn't grant API access. Check the key and that your account has
  API access enabled.
</Warning>
