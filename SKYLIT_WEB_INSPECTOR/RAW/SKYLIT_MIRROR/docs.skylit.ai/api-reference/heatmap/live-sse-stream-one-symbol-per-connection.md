> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Live SSE stream (one symbol per connection)

> A **Server-Sent Events** (`text/event-stream`) feed of live per-strike
heatmap updates for **one** symbol. Open one connection per symbol.

**Events:**
- `connected` — handshake, payload `{symbol, creditsRemaining}`.
- `initial_data` — current heatmap snapshot on connect.
- `snapshot_update` — full heatmap on each change.
- `velocity_update` — per-strike % change.
- `credits` — emitted every minute boundary, payload `{remaining}`.
- `closed` — stream terminates with `{reason: "insufficient_credits"
  | "account_suspended" | "credit_check_failed"}`.
- `reconnect` — server is recycling the connection (after ~1h),
  payload `{reason: "max_duration"}`. Reconnect to continue.
- `: keepalive` comment every 30s for proxy keepalive.

**Pricing.** 1 credit on connect (charged before the SSE upgrade —
an under-funded client gets a clean `402` HTTP response, not a
half-open stream), then 1 credit per minute open. The per-minute
ticker emits `event: credits {remaining: N}` after each successful
debit so clients can budget the next minute.

**Concurrency.** Up to 5 concurrent streams per customer per pod.
Exceeding the cap returns `429` `stream_limit_reached`.

> OpenAPI is request/response-oriented and can't fully model an event
> stream. See [docs/api-credits.md](https://github.com/SkylitAI/skylit-main/blob/main/docs/api-credits.md#live-stream-v1stream)
> for the full stream lifecycle.




## OpenAPI

````yaml /openapi.yaml get /v1/stream
openapi: 3.1.0
info:
  title: Skylit Public API
  version: 1.0.0
  summary: Options-Greeks heatmaps as a public HTTP API.
  description: >
    Skylit exposes its real-time options-Greeks (gamma / vanna) heatmaps as a

    versioned public HTTP API, per strike, with the live velocity metric and

    Skylit's node classification (King / Gatekeeper / etc.).


    **Authentication.** Send your Skylit API key as a bearer token:

        Authorization: Bearer <key>

    (`X-API-Key: <key>` is also accepted.)


    **Credit metering.** Every chargeable request debits a fixed cost from

    your credit balance:


    | Endpoint        | Cost |

    |-----------------|-----:|

    | `/v1/heatmap`    | 1   |

    | `/v1/historical` | 5   |

    | `/v1/stream`     | 1 per minute open |

    | `/v1/openapi.json` | 0 |


    New customers are seeded with 5,000 credits. Every chargeable response

    carries `X-Credits-Remaining: <balance>`. Out of credits → `402`

    `insufficient_credits`; an admin-suspended account → `403`

    `account_suspended`. Top up via your account console.


    **Rate limits.** A safety ceiling of 600 requests / minute is enforced

    by the Skylit gateway and surfaced via `X-RateLimit-Limit`,

    `X-RateLimit-Remaining`, and `X-RateLimit-Reset`. `429` includes

    `Retry-After`. This is a runaway-protection ceiling, not a quota —

    credit metering does the per-customer accounting.


    See [the credits
    doc](https://github.com/SkylitAI/skylit-main/blob/main/docs/api-credits.md)

    for the full lifecycle, including live-stream pricing.


    **Resolution.** The heatmap is a 1-second time series. Endpoints return the

    single snapshot nearest the requested instant — poll `/v1/heatmap` every

    60-90s for live, or query `/v1/historical` at any minute boundary for a

    1-minute replay grid (no server-side downsampling needed).


    **Velocity is live-only.** The `velocityPct` field is present on

    `/v1/heatmap` (live) and absent on `/v1/historical` (replay).


    **Response shape.** Success → `{ "data": ..., "meta": { ... } }`; errors →

    `{ "error": { "code": "...", "message": "..." } }`. camelCase throughout.

    `data.symbols` is always an array (one element per requested symbol), so a

    single-symbol call and a multi-symbol "Trinity" call share one shape.
servers:
  - url: https://api.skylit.ai
    description: Production
security:
  - bearerApiKey: []
tags:
  - name: Heatmap
  - name: Meta
paths:
  /v1/stream:
    get:
      tags:
        - Heatmap
      summary: Live SSE stream (one symbol per connection)
      description: >
        A **Server-Sent Events** (`text/event-stream`) feed of live per-strike

        heatmap updates for **one** symbol. Open one connection per symbol.


        **Events:**

        - `connected` — handshake, payload `{symbol, creditsRemaining}`.

        - `initial_data` — current heatmap snapshot on connect.

        - `snapshot_update` — full heatmap on each change.

        - `velocity_update` — per-strike % change.

        - `credits` — emitted every minute boundary, payload `{remaining}`.

        - `closed` — stream terminates with `{reason: "insufficient_credits"
          | "account_suspended" | "credit_check_failed"}`.
        - `reconnect` — server is recycling the connection (after ~1h),
          payload `{reason: "max_duration"}`. Reconnect to continue.
        - `: keepalive` comment every 30s for proxy keepalive.


        **Pricing.** 1 credit on connect (charged before the SSE upgrade —

        an under-funded client gets a clean `402` HTTP response, not a

        half-open stream), then 1 credit per minute open. The per-minute

        ticker emits `event: credits {remaining: N}` after each successful

        debit so clients can budget the next minute.


        **Concurrency.** Up to 5 concurrent streams per customer per pod.

        Exceeding the cap returns `429` `stream_limit_reached`.


        > OpenAPI is request/response-oriented and can't fully model an event

        > stream. See
        [docs/api-credits.md](https://github.com/SkylitAI/skylit-main/blob/main/docs/api-credits.md#live-stream-v1stream)

        > for the full stream lifecycle.
      operationId: streamHeatmap
      parameters:
        - name: symbol
          in: query
          required: true
          description: Single ticker to stream (e.g. `SPY`). One symbol per connection.
          schema:
            type: string
            example: SPY
        - $ref: '#/components/parameters/Metric'
        - $ref: '#/components/parameters/MaxStrikes'
      responses:
        '200':
          description: An SSE stream of heatmap events.
          content:
            text/event-stream:
              schema:
                type: string
                description: >
                  SSE frames, e.g. `event: snapshot_update` then `data:
                  {SymbolHeatmap}`.

                  The snapshot_update `data` payload matches
                  #/components/schemas/SymbolHeatmap.
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'
        '404':
          $ref: '#/components/responses/NotFound'
        '429':
          $ref: '#/components/responses/RateLimited'
components:
  parameters:
    Metric:
      name: metric
      in: query
      required: false
      description: Which Greek exposure to return per strike.
      schema:
        type: string
        enum:
          - gamma
          - vanna
        default: gamma
    MaxStrikes:
      name: maxStrikes
      in: query
      required: false
      description: Maximum number of strikes around spot to return.
      schema:
        type: integer
        default: 92
        minimum: 1
        maximum: 400
  responses:
    BadRequest:
      description: Request validation failed.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Unauthorized:
      description: Missing or invalid API key.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Forbidden:
      description: Key revoked or expired, or monthly quota exceeded.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    NotFound:
      description: Unknown symbol or no data available.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    RateLimited:
      description: Per-minute rate limit exceeded.
      headers:
        Retry-After:
          schema:
            type: integer
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
  schemas:
    Error:
      type: object
      required:
        - error
      properties:
        error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: string
              description: Stable, machine-readable error code.
              example: no_data
            message:
              type: string
              description: Human-readable explanation.
  securitySchemes:
    bearerApiKey:
      type: http
      scheme: bearer
      description: |
        Skylit API key in the `Authorization` header
        (`Authorization: Bearer <key>`). `X-API-Key` is also accepted.

````