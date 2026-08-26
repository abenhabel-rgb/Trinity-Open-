> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Raw enriched trades for a ticker

> Returns the raw enriched trade rows that feed the chart bars and
the live feed. Supports rich filtering — sweep-only / multi-leg,
moneyness, premium floor, DTE / strike / expiration windows.
See `OptionTradeRow` below.




## OpenAPI

````yaml /flowseeker-openapi.yaml get /v1/underlying/{ticker}/trades
openapi: 3.1.0
info:
  title: Flowseeker — Skylit Public API
  version: 1.0.0
  summary: Real-time and historical options-flow analytics as a public HTTP API.
  description: >
    Flowseeker exposes Skylit's real-time options-flow scoring stack — Flow

    Score, FlowBonus, VWF/SDF/FIR aggregates, sector rotation, and market

    breadth — as a versioned public HTTP API. Data is sourced from the full

    OPRA options feed with sub-second freshness during market hours.


    **Authentication.** Send your Skylit API key as a bearer token:

        Authorization: Bearer fs_live_<key>

    (`X-API-Key: fs_live_<key>` is also accepted.) Your rate limit and monthly

    quota are determined by your account plan.


    **Rate limits & quotas.** Per-minute limits are enforced by the Skylit

    gateway and surfaced on every response via `X-RateLimit-Limit`,

    `X-RateLimit-Remaining`, and `X-RateLimit-Reset`. `429` includes

    `Retry-After`; quota exhaustion returns `403` with `code: QUOTA_EXCEEDED`.


    **Credits & billing.** Every `/v1/*` data request debits a fixed number of

    **credits** from your account's shared Skylit balance (the same balance used

    across all Skylit public APIs). Each chargeable response carries

    `X-Credits-Remaining: <balance>`. The credit is charged before the request

    is served, so a `5xx` still bills. Cost is priced by server-side work and

    data volume returned:


    | Tier | Credits | Routes |

    |------|--------:|--------|

    | Light | 1 | single-key reads, ratios, scores, discovery/search lists,
    expirations, rvol, per-contract bull/bear, the flow feed |

    | Medium | 3 | charts, full chains, by-strike matrix,
    momentum/baseline/strikes, tide, aggregate, sweeps, market, sector,
    market-breadth, chain bull/bear, unusual-volume/oi screeners, dark-pool
    top-prints |

    | Heavy | 5 | trade feeds (`/trades`, dark-pool trades), history
    (`/history`, `historical-compare`), bulk endpoints |


    `/v1/openapi.json` is free. When you run out of credits the API returns

    `402` `insufficient_credits`; a suspended account returns `403`

    `account_suspended`; a transient billing-store error returns `503`

    `credit_check_failed` (safe to retry). These billing codes are lowercase

    (`insufficient_credits`, `account_suspended`, `credit_check_failed`) — the

    platform-wide convention for credit errors.


    **Response envelope.** All success responses share one shape:

        { "data": <payload>, "meta": { "timestamp": "...", "requestId": "..." } }

    All errors share one shape:

        { "error": { "code": "NOT_FOUND", "message": "..." } }

    Field names are camelCase throughout. Codes are stable, machine-readable

    `SCREAMING_SNAKE_CASE` strings — the message text may evolve.


    **Freshness.** Endpoints with a `timeframe` parameter (e.g.
    `/v1/flow/{ticker}`)

    return data through the last completed bucket. Intra-bucket fills land on
    the

    next request. The cumulative `/v1/flow/market-breadth` and aggregate scoring

    endpoints update at most once per second.
servers:
  - url: https://flow-api.skylit.ai
    description: Production
  - url: https://d2kehby0dtx1a6.cloudfront.net
    description: Staging (subject to wipes; do not use for billing-relevant work)
security:
  - bearerApiKey: []
tags:
  - name: Flow
    description: Per-ticker flow feed, aggregate scoring, baselines, and momentum.
  - name: Sweeps
    description: Aggregated multi-exchange sweeps and sweep-only feeds.
  - name: Sector
    description: Sector- and industry-level flow rollups.
  - name: Market
    description: >-
      Market-wide overview, breadth, advance/decline, sector rotation, and
      net-premium tide.
  - name: Analytics
    description: >
      Standalone analytics endpoints — Vol/OI accumulation, moneyness
      segmentation,

      and timeframe-aggregated sentiment scores.
  - name: Ratios
    description: |
      Bid/ask/mid distribution analyses at chain and contract granularity, plus
      call/put-aware bull/bear pressure breakdowns.
  - name: Scoring
    description: Per-trade scoring, sentiment, and intent classification.
  - name: Underlying
    description: |
      Ticker-level discovery and analytics — top tickers by flow,
      bulk stats, intraday chart bars, raw enriched trades, strike /
      expiration distributions, option chain, and historical rollups.
  - name: Contract
    description: |
      Per-contract discovery and analytics — top contracts by flow,
      unusual volume / OI scans, contract stats, intraday chart bars,
      raw enriched trades, and historical rollups.
  - name: Dark Pool
    description: |
      Off-exchange (TRF) prints — paginated dark-pool trades and the
      largest individual prints per ticker. No side / BBO / greeks.
  - name: Meta
    description: API metadata (this OpenAPI document, etc.).
paths:
  /v1/underlying/{ticker}/trades:
    get:
      tags:
        - Underlying
      summary: Raw enriched trades for a ticker
      description: |
        Returns the raw enriched trade rows that feed the chart bars and
        the live feed. Supports rich filtering — sweep-only / multi-leg,
        moneyness, premium floor, DTE / strike / expiration windows.
        See `OptionTradeRow` below.
      operationId: getUnderlyingTrades
      parameters:
        - $ref: '#/components/parameters/Ticker'
        - in: query
          name: start
          description: |
            Lower time bound — ISO 8601 (e.g. `2026-01-12T09:30:00Z`) or
            Unix seconds. Defaults to start-of-trading-day.
          schema:
            type: string
        - in: query
          name: end
          description: |
            Upper time bound — ISO 8601 or Unix seconds. Defaults to now.
          schema:
            type: string
        - in: query
          name: limit
          schema:
            type: integer
            minimum: 1
            maximum: 500
            default: 50
        - in: query
          name: only_sweeps
          schema:
            type: boolean
            default: false
        - in: query
          name: only_multi_leg
          schema:
            type: boolean
            default: false
        - in: query
          name: exclude_multi_leg
          schema:
            type: boolean
            default: false
        - in: query
          name: moneyness
          schema:
            type: string
            enum:
              - ITM
              - ATM
              - OTM
        - in: query
          name: min_moneyness_pct
          schema:
            type: number
            format: double
        - in: query
          name: max_moneyness_pct
          schema:
            type: number
            format: double
        - in: query
          name: min_premium
          schema:
            type: number
            format: double
            minimum: 0
        - in: query
          name: min_dte
          schema:
            type: integer
        - in: query
          name: max_dte
          schema:
            type: integer
        - in: query
          name: min_strike
          schema:
            type: number
            format: double
        - in: query
          name: max_strike
          schema:
            type: number
            format: double
        - in: query
          name: expiration
          schema:
            type: string
            format: date
      responses:
        '200':
          description: Filtered enriched trades.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OptionTradeListSuccess'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '402':
          $ref: '#/components/responses/InsufficientCredits'
        '429':
          $ref: '#/components/responses/RateLimited'
components:
  parameters:
    Ticker:
      name: ticker
      in: path
      required: true
      description: Underlying ticker symbol (uppercase, e.g. `SPY`, `AAPL`).
      schema:
        type: string
        example: SPY
  schemas:
    OptionTradeListSuccess:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/OptionTradeRow'
        meta:
          $ref: '#/components/schemas/Meta'
    OptionTradeRow:
      type: object
      description: |
        Enriched single-trade row served by the trades endpoints. Most
        fields are always present; `*Pct`, `nextIv`, `agg*`, `strategy*`,
        and `earnings*` are optional.
      required:
        - date
        - tsEvent
        - instrumentId
        - rawSymbol
        - ticker
        - expiration
        - strike
        - right
        - dte
        - price
        - size
        - side
        - publisherId
        - neutralSz
        - totalPremium
        - underlyingPrice
        - moneyness
        - moneynessPercent
        - openInterest
        - prevOi
        - dailyVolume
        - sweepTrade
        - blockTrade
        - multiLeg
        - ivDirection
        - ingestionTimestamp
      properties:
        date:
          type: integer
          description: Days since 1970-01-01 (compact session date).
        tsEvent:
          type: integer
          format: int64
          description: Trade event timestamp in milliseconds since epoch.
        tsEventUs:
          type: integer
          format: int64
          description: Microsecond-precision timestamp (contract-trades endpoint only).
        instrumentId:
          type: integer
          format: int64
        rawSymbol:
          type: string
          example: SPY   250516C00580000
        ticker:
          type: string
          example: SPY
        expiration:
          type: integer
          description: Expiration as days since 1970-01-01.
        strike:
          type: number
          format: double
        right:
          type: string
          enum:
            - C
            - P
        dte:
          type: integer
        price:
          type: number
          format: double
        size:
          type: integer
          minimum: 0
        side:
          type: string
          description: |
            Granular execution-side label — `BB` (below bid), `B` (bid),
            `AB` (above bid), `M` (mid), `BA` (below ask), `A` (ask),
            `AA` (above ask), or `N` (no BBO).
          enum:
            - BB
            - B
            - AB
            - M
            - BA
            - A
            - AA
            - 'N'
        publisherId:
          type: integer
        bidPx:
          type: number
          format: double
          nullable: true
        askPx:
          type: number
          format: double
          nullable: true
        bidSz:
          type: integer
          nullable: true
        askSz:
          type: integer
          nullable: true
        neutralSz:
          type: integer
        totalPremium:
          type: number
          format: double
        spread:
          type: number
          format: double
          nullable: true
        underlyingPrice:
          type: number
          format: double
        iv:
          type: number
          format: double
          nullable: true
        moneyness:
          type: string
          enum:
            - ITM
            - ATM
            - OTM
        moneynessPercent:
          type: number
          format: double
        openInterest:
          type: integer
          minimum: 0
        prevOi:
          type: integer
          minimum: 0
        prevClose:
          type: number
          format: double
          nullable: true
        prevCloseAge:
          type: integer
          minimum: 0
          nullable: true
          description: Trading days back the `prevClose` came from (0 = yesterday).
        priceChange:
          type: number
          format: double
          nullable: true
        dailyVolume:
          type: integer
          minimum: 0
        sweepTrade:
          type: boolean
        blockTrade:
          type: boolean
        multiLeg:
          type: boolean
        ivDirection:
          type: integer
          enum:
            - -1
            - 0
            - 1
          description: '-1 = down, 0 = flat/unknown, 1 = up.'
        ingestionTimestamp:
          type: integer
          format: int64
          description: Server ingest time in milliseconds since epoch.
        prevIv:
          type: number
          format: double
          nullable: true
        nextIv:
          type: number
          format: double
          nullable: true
        premiumPercentile:
          type: integer
          enum:
            - 0
            - 50
            - 75
            - 90
            - 95
            - 99
          description: Bucketed premium percentile band (0 = below P50, 99 = P99+).
        flowScore:
          type: integer
          minimum: -100
          maximum: 100
        chainBidPct:
          type: number
          format: double
        chainAskPct:
          type: number
          format: double
        contractBidPct:
          type: number
          format: double
        contractAskPct:
          type: number
          format: double
        aggCount:
          type: integer
          minimum: 0
        aggTotalPremium:
          type: number
          format: double
        aggTotalSize:
          type: integer
          minimum: 0
        mlSibling:
          type: boolean
          description: >-
            True when this leg was included via spread association rather than
            its own filter match.
        strategyGroupId:
          type: string
        strategyType:
          type: string
        strategyLegCount:
          type: integer
          minimum: 1
        earningsDte:
          type: integer
        nextEarningsDate:
          type: integer
        cacheMiss:
          type: boolean
        sector:
          type: string
        industry:
          type: string
    Meta:
      type: object
      required:
        - timestamp
        - requestId
      properties:
        timestamp:
          type: string
          format: date-time
          description: Server-side timestamp the response was generated at.
        requestId:
          type: string
          description: Short opaque ID for log correlation.
          example: d7574836
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
              description: |
                Stable machine-readable error code. Common values:
                `BAD_REQUEST`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`,
                `RATE_LIMITED`, `QUOTA_EXCEEDED`, `INTERNAL_ERROR`,
                `UNAVAILABLE`.
              example: NOT_FOUND
            message:
              type: string
              description: Human-readable explanation. Wording may evolve; key off `code`.
  responses:
    BadRequest:
      description: Request validation failed.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            invalidParam:
              value:
                error:
                  code: BAD_REQUEST
                  message: >-
                    Invalid parameter 'timeframe': must be one of [1m, 5m, 15m,
                    1h, 4h, 1d, 1w, 1M]
    Unauthorized:
      description: Missing or invalid API key.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            missingKey:
              value:
                error:
                  code: UNAUTHORIZED
                  message: Authentication required
    InsufficientCredits:
      description: >-
        The account's shared Skylit credit balance is lower than this route's
        cost. Top up to continue. Carries `X-Credits-Remaining: 0`.
      headers:
        X-Credits-Remaining:
          description: Remaining credit balance (0 on this response).
          schema:
            type: integer
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            outOfCredits:
              value:
                error:
                  code: insufficient_credits
                  message: Out of credits. Top up to continue making requests.
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
          examples:
            tooFast:
              value:
                error:
                  code: RATE_LIMITED
                  message: Rate limit of 100 req/min exceeded. Retry after 18s.
  securitySchemes:
    bearerApiKey:
      type: http
      scheme: bearer
      bearerFormat: fs_live_*
      description: |
        Skylit API key in the `Authorization` header
        (`Authorization: Bearer fs_live_<key>`). `X-API-Key` is also accepted.

````