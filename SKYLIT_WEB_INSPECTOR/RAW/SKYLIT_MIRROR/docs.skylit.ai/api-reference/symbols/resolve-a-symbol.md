> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Resolve a symbol

> The TradingView `LibrarySymbolInfo` for one ticker — price scale,
session, timezone, and supported resolutions the charting library needs
before requesting history.




## OpenAPI

````yaml /atlas-openapi.yaml get /v1/symbols
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
  /v1/symbols:
    get:
      tags:
        - Symbols
      summary: Resolve a symbol
      description: |
        The TradingView `LibrarySymbolInfo` for one ticker — price scale,
        session, timezone, and supported resolutions the charting library needs
        before requesting history.
      operationId: resolveSymbol
      parameters:
        - $ref: '#/components/parameters/Symbol'
      responses:
        '200':
          description: Symbol info.
          headers:
            X-Credits-Remaining:
              $ref: '#/components/headers/CreditsRemaining'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SymbolInfo'
              examples:
                spy:
                  value:
                    ticker: SPY
                    name: SPY
                    description: SPDR S&P 500 ETF Trust
                    type: etf
                    session: 0930-1600
                    timezone: America/New_York
                    exchange: ARCA
                    minmov: 1
                    pricescale: 100
                    has_intraday: true
                    has_daily: true
                    has_weekly_and_monthly: true
                    intraday_multipliers:
                      - '1'
                      - '60'
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
                    volume_precision: 0
                    data_status: streaming
                    format: price
        '400':
          description: Malformed symbol.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UdfError'
              examples:
                invalid:
                  value:
                    success: false
                    error: invalid symbol
        '401':
          $ref: '#/components/responses/Unauthorized'
        '402':
          $ref: '#/components/responses/InsufficientCredits'
        '403':
          $ref: '#/components/responses/AccountSuspended'
        '404':
          description: Unknown symbol.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UdfError'
              examples:
                notFound:
                  value:
                    success: false
                    error: symbol not found
        '429':
          $ref: '#/components/responses/RateLimited'
components:
  parameters:
    Symbol:
      name: symbol
      in: query
      required: true
      description: Ticker (e.g. `SPY`).
      schema:
        type: string
        example: SPY
  headers:
    CreditsRemaining:
      description: Credit balance remaining after this request was debited.
      schema:
        type: integer
        example: 4999
  schemas:
    SymbolInfo:
      type: object
      description: TradingView `LibrarySymbolInfo`.
      required:
        - ticker
        - name
        - description
        - type
        - session
        - timezone
        - exchange
        - minmov
        - pricescale
        - supported_resolutions
      properties:
        ticker:
          type: string
        name:
          type: string
        description:
          type: string
        type:
          type: string
          enum:
            - stock
            - etf
            - index
        session:
          type: string
          example: 0930-1600
        timezone:
          type: string
          example: America/New_York
        exchange:
          type: string
          example: ARCA
        minmov:
          type: integer
          example: 1
        pricescale:
          type: integer
          example: 100
        has_intraday:
          type: boolean
        has_daily:
          type: boolean
        has_weekly_and_monthly:
          type: boolean
        intraday_multipliers:
          type: array
          items:
            type: string
        supported_resolutions:
          type: array
          items:
            type: string
        volume_precision:
          type: integer
          example: 0
        data_status:
          type: string
          example: streaming
        format:
          type: string
          example: price
    UdfError:
      type: object
      description: Symbol-resolution error (UDF-native shape).
      required:
        - success
        - error
      properties:
        success:
          type: boolean
          enum:
            - false
        error:
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
    InsufficientCredits:
      description: Credit balance is below the request cost.
      headers:
        X-Credits-Remaining:
          $ref: '#/components/headers/CreditsRemaining'
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            outOfCredits:
              value:
                error:
                  code: insufficient_credits
                  message: Out of credits.
    AccountSuspended:
      description: Account is not API-eligible (suspended).
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            suspended:
              value:
                error:
                  code: account_suspended
                  message: Account suspended.
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
  securitySchemes:
    bearerApiKey:
      type: http
      scheme: bearer
      description: |
        Skylit API key in the `Authorization` header
        (`Authorization: Bearer <key>`). `X-API-Key` is also accepted. The same
        key works across Atlas, Heatseeker, and Flowseeker.

````