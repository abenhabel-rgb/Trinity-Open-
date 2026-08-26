> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Datafeed configuration

> The static UDF `DatafeedConfiguration` — supported resolutions,
exchanges, symbol types, and feature flags. Free.




## OpenAPI

````yaml /atlas-openapi.yaml get /v1/config
openapi: 3.1.0
info:
  title: Atlas Public API
  version: 1.0.0
  summary: OHLCV price history as a TradingView-UDF datafeed.
  description: >
    Atlas exposes Skylit's real-time and historical **OHLCV** (open / high / low

    / close / volume) price bars as a versioned public HTTP API that implements

    the TradingView **UDF** (Universal Data Feed) datafeed contract. Point a

    TradingView Charting Library datafeed at `https://atlas-api.skylit.ai/v1`,
    or

    call the endpoints directly.


    **Authentication.** Send your Skylit API key as a bearer token:

        Authorization: Bearer <key>

    (`X-API-Key: <key>` is also accepted.) One Skylit key spans every product —

    the same key and credit balance work for Heatseeker and Flowseeker.


    **Credit metering.** Each chargeable request debits a fixed cost from your

    balance:


    | Endpoint       | Cost |

    |----------------|-----:|

    | `/v1/history`  | 1    |

    | `/v1/search`   | 1    |

    | `/v1/symbols`  | 1    |

    | `/v1/config`   | 0    |

    | `/v1/time`     | 0    |


    New customers are seeded with 5,000 credits. Every chargeable response

    carries `X-Credits-Remaining: <balance>`. Out of credits → `402`

    `insufficient_credits`; an admin-suspended account → `403`

    `account_suspended`. `/v1/config` and `/v1/time` are free metadata calls.


    Note that a charting client fetches `/v1/history` in **pages** (it walks the

    `to` cursor backward to fill the requested range), so a deep history pull

    naturally costs one credit per page — the cost scales with the data you

    actually retrieve.


    **Rate limits.** A safety ceiling of 600 requests / minute is enforced by

    the Skylit gateway and surfaced via `X-RateLimit-Limit`,

    `X-RateLimit-Remaining`, and `X-RateLimit-Reset`. `429` includes

    `Retry-After`. This is runaway protection, not a quota — credit metering

    does the per-customer accounting.


    **The datafeed flow.** A UDF client calls `/v1/config` once for the feed's

    capabilities, `/v1/symbols` to resolve a ticker (price scale, session,

    supported resolutions), then `/v1/history` for the bars; `/v1/search` powers

    the symbol picker and `/v1/time` the server clock. History follows the UDF

    convention: a `200` with `{ "s": "ok", ... }` on success and `{ "s":

    "no_data" }` when the window has no bars (not a `404`). Auth and credit

    errors, which aren't part of UDF, use the envelope

    `{ "error": { "code": "...", "message": "..." } }`.
servers:
  - url: https://atlas-api.skylit.ai
    description: Production
security:
  - bearerApiKey: []
tags:
  - name: History
    description: OHLCV price bars.
  - name: Symbols
    description: Symbol search and resolution.
  - name: Meta
    description: Datafeed configuration and server time (free).
paths:
  /v1/config:
    get:
      tags:
        - Meta
      summary: Datafeed configuration
      description: |
        The static UDF `DatafeedConfiguration` — supported resolutions,
        exchanges, symbol types, and feature flags. Free.
      operationId: getConfig
      responses:
        '200':
          description: Datafeed configuration.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DatafeedConfig'
              examples:
                config:
                  value:
                    supports_search: true
                    supports_group_request: false
                    supports_marks: false
                    supports_timescale_marks: false
                    supports_time: true
                    supported_resolutions:
                      - '1'
                      - '2'
                      - '3'
                      - '5'
                      - '15'
                      - '30'
                      - '60'
                      - '240'
                      - '480'
                      - D
                      - W
                    intraday_multipliers:
                      - '1'
                      - '60'
                    exchanges:
                      - value: NASDAQ
                        name: NASDAQ
                        desc: NASDAQ
                      - value: NYSE
                        name: NYSE
                        desc: NYSE
                      - value: ARCA
                        name: NYSE ARCA
                        desc: NYSE ARCA
                    symbols_types:
                      - name: stock
                        value: stock
                      - name: etf
                        value: etf
                      - name: index
                        value: index
        '401':
          $ref: '#/components/responses/Unauthorized'
components:
  schemas:
    DatafeedConfig:
      type: object
      properties:
        supports_search:
          type: boolean
        supports_group_request:
          type: boolean
        supports_marks:
          type: boolean
        supports_timescale_marks:
          type: boolean
        supports_time:
          type: boolean
        supported_resolutions:
          type: array
          items:
            type: string
        intraday_multipliers:
          type: array
          items:
            type: string
        exchanges:
          type: array
          items:
            type: object
            properties:
              value:
                type: string
              name:
                type: string
              desc:
                type: string
        symbols_types:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              value:
                type: string
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
              description: Stable machine-readable code.
              example: insufficient_credits
            message:
              type: string
  responses:
    Unauthorized:
      description: Missing or invalid API key.
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
        (`Authorization: Bearer <key>`). `X-API-Key` is also accepted. The same
        key works across Atlas, Heatseeker, and Flowseeker.

````