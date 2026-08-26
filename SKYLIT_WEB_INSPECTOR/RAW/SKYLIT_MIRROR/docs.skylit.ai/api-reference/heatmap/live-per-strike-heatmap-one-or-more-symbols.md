> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Live per-strike heatmap (one or more symbols)

> Current per-strike heatmap for one or more symbols at the latest
snapshot. Includes the live `velocityPct` per strike. Pass multiple
comma-separated symbols for a single cross-asset (Trinity) call.




## OpenAPI

````yaml /openapi.yaml get /v1/heatmap
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
  /v1/heatmap:
    get:
      tags:
        - Heatmap
      summary: Live per-strike heatmap (one or more symbols)
      description: |
        Current per-strike heatmap for one or more symbols at the latest
        snapshot. Includes the live `velocityPct` per strike. Pass multiple
        comma-separated symbols for a single cross-asset (Trinity) call.
      operationId: getHeatmap
      parameters:
        - $ref: '#/components/parameters/Symbols'
        - $ref: '#/components/parameters/Metric'
        - $ref: '#/components/parameters/MaxStrikes'
      responses:
        '200':
          description: Live heatmap snapshot(s).
          headers:
            Cache-Control:
              schema:
                type: string
                example: private, max-age=5
            X-RateLimit-Limit:
              schema:
                type: integer
            X-RateLimit-Remaining:
              schema:
                type: integer
            X-RateLimit-Reset:
              schema:
                type: integer
          content:
            application/json:
              schema:
                type: object
                required:
                  - data
                  - meta
                properties:
                  data:
                    type: object
                    required:
                      - symbols
                    properties:
                      symbols:
                        type: array
                        items:
                          $ref: '#/components/schemas/SymbolHeatmap'
                  meta:
                    $ref: '#/components/schemas/Meta'
              examples:
                live:
                  summary: SPY live (truncated)
                  value:
                    data:
                      symbols:
                        - symbol: SPY
                          asOf: '2026-05-22T14:31:00Z'
                          spot: 591.23
                          previousClose: 589.1
                          priceChange: 2.13
                          priceChangePercent: 0.36
                          expirations:
                            - '2026-05-22'
                            - '2026-05-23'
                            - '2026-05-30'
                          strikes:
                            - strike: 590
                              value: 1894300.4
                              nodeType: king
                              velocityPct: 12.4
                            - strike: 595
                              value: 642100.2
                              nodeType: gatekeeper
                              velocityPct: -3.1
                            - strike: 585
                              value: 88010
                              nodeType: normal
                              velocityPct: 0.4
                    meta:
                      metric: gamma
                      resolution: 1m
                      mode: live
                      cached: false
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
        '503':
          $ref: '#/components/responses/Unavailable'
components:
  parameters:
    Symbols:
      name: symbols
      in: query
      required: true
      description: |
        One ticker, or a comma-separated list for a single cross-asset call
        (e.g. `SPY` or `SPY,SPX,QQQ`). Each is returned as an element of
        `data.symbols`.
      schema:
        type: string
        example: SPY,SPX,QQQ
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
  schemas:
    SymbolHeatmap:
      type: object
      required:
        - symbol
        - asOf
        - spot
        - previousClose
        - priceChange
        - priceChangePercent
        - expirations
        - strikes
      properties:
        symbol:
          type: string
          description: Canonical ticker for the returned data.
        asOf:
          type: string
          format: date-time
          description: >-
            RFC3339 timestamp of the snapshot actually returned (nearest to the
            requested instant).
        spot:
          type: number
          description: Spot price at the snapshot.
        previousClose:
          type: number
        priceChange:
          type: number
          description: Spot minus previous close.
        priceChangePercent:
          type: number
        expirations:
          type: array
          description: >-
            Expiration dates (YYYY-MM-DD) contributing to each strike's net
            value.
          items:
            type: string
            format: date
        strikes:
          type: array
          description: Per-strike nodes, ordered by strike ascending.
          items:
            $ref: '#/components/schemas/StrikeNode'
    Meta:
      type: object
      required:
        - metric
        - resolution
        - mode
        - cached
      properties:
        metric:
          type: string
          enum:
            - gamma
            - vanna
        resolution:
          type: string
          example: 1m
        mode:
          type: string
          enum:
            - live
            - historical
        cached:
          type: boolean
          description: True if served from the in-process cache.
    StrikeNode:
      type: object
      required:
        - strike
        - value
        - nodeType
      properties:
        strike:
          type: number
          description: Strike price.
        value:
          type: number
          description: >-
            Net exposure for the selected `metric` at this strike (summed across
            the returned expirations).
        nodeType:
          type: string
          description: Skylit's node classification for this strike.
          enum:
            - king
            - gatekeeper
            - pika
            - barney
            - significant
            - normal
        velocityPct:
          type: number
          description: |
            Live percent change of this strike's value over the velocity window.
            Present on `/v1/heatmap` only; omitted on `/v1/historical`.
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
    Unavailable:
      description: Heatmap data is temporarily unavailable.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
  securitySchemes:
    bearerApiKey:
      type: http
      scheme: bearer
      description: |
        Skylit API key in the `Authorization` header
        (`Authorization: Bearer <key>`). `X-API-Key` is also accepted.

````