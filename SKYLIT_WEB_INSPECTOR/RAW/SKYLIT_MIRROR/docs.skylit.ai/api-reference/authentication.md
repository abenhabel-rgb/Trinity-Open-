> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Authentication

> Authenticate with a Skylit API key, and how credits and rate limits work.

<div className="skylit-soon">
  <span><strong>Limited beta</strong> — the Skylit API is in limited beta. Create and manage keys in the Developer tab of the <a href="https://app.skylit.ai">Skylit app</a>.</span>
</div>

The Skylit Public API uses **bearer authentication**. Send your API key in the
`Authorization` header on every request:

```bash theme={null}
Authorization: Bearer <your-api-key>
```

<Tip>
  `X-API-Key: <your-api-key>` is also accepted if a bearer header is inconvenient.
</Tip>

<Warning>
  Treat API keys like passwords. Never commit them to source control or expose them in
  client-side code. Use environment variables and rotate keys if one leaks.
</Warning>

## Getting a key

Generate and manage keys from your [account console](https://app.skylit.ai). New accounts
are seeded with **5,000 credits**.

<CodeGroup>
  ```bash cURL theme={null}
  curl "https://api.skylit.ai/v1/heatmap?symbols=SPY" \
    -H "Authorization: Bearer $SKYLIT_API_KEY"
  ```

  ```python Python theme={null}
  import os, requests

  session = requests.Session()
  session.headers["Authorization"] = f"Bearer {os.environ['SKYLIT_API_KEY']}"
  print(session.get("https://api.skylit.ai/v1/heatmap", params={"symbols": "SPY"}).json())
  ```

  ```javascript Node theme={null}
  const skylit = (path) =>
    fetch(`https://api.skylit.ai${path}`, {
      headers: { Authorization: `Bearer ${process.env.SKYLIT_API_KEY}` },
    }).then((r) => r.json());

  console.log(await skylit("/v1/heatmap?symbols=SPY"));
  ```
</CodeGroup>

## Credits

Every chargeable request debits a fixed cost from your credit balance.

| Endpoint           |              Cost |
| ------------------ | ----------------: |
| `/v1/heatmap`      |                 1 |
| `/v1/historical`   |                 5 |
| `/v1/stream`       | 1 per minute open |
| `/v1/openapi.json` |                 0 |

Every chargeable response carries `X-Credits-Remaining: <balance>`.

<ResponseField name="402 insufficient_credits">
  You're out of credits. Top up in the [account console](https://app.skylit.ai).
</ResponseField>

<ResponseField name="403 account_suspended">
  The account has been administratively suspended.
</ResponseField>

## Rate limits

A safety ceiling of **600 requests / minute** is enforced by the Skylit gateway and
surfaced via `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset`.
This is runaway protection, not your quota — credit metering does the per-customer accounting.

| Status                  | Meaning                                          |
| ----------------------- | ------------------------------------------------ |
| `401 Unauthorized`      | Missing or invalid API key.                      |
| `403 Forbidden`         | Key revoked/expired, or account suspended.       |
| `429 Too Many Requests` | Rate ceiling hit — back off using `Retry-After`. |

<Card title="Make your first call" icon="arrow-right" href="/api-reference/heatmap/live-per-strike-heatmap-one-or-more-symbols">
  Jump to **GET /v1/heatmap** and try it live in the playground.
</Card>
