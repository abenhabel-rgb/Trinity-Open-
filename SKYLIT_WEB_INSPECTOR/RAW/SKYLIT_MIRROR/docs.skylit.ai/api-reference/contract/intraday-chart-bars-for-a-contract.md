> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Intraday chart bars for a contract

> Time-bucketed bars for a single contract — granular bid/mid/ask
execution split, premium and volume per side, daily cumulative
totals, VWAP, and (when available) IV and 30D average baselines.




## OpenAPI

````yaml /flowseeker-openapi.yaml get /v1/contract/{symbol}/chart
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
  /v1/contract/{symbol}/chart:
    get:
      tags:
        - Contract
      summary: Intraday chart bars for a contract
      description: |
        Time-bucketed bars for a single contract — granular bid/mid/ask
        execution split, premium and volume per side, daily cumulative
        totals, VWAP, and (when available) IV and 30D average baselines.
      operationId: getContractChart
      parameters:
        - $ref: '#/components/parameters/OptionSymbol'
        - in: query
          name: interval
          required: true
          description: Trailing window — `{N}D` where N is 1–365 (e.g. `1D`, `7D`).
          schema:
            type: string
            example: 1D
        - in: query
          name: bucket
          required: true
          schema:
            type: string
            enum:
              - 1min
              - 5min
              - 10min
              - 15min
              - 30min
              - 1d
              - 1w
      responses:
        '200':
          description: Intraday bars for the contract.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ContractChartSuccess'
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
    OptionSymbol:
      name: symbol
      in: path
      required: true
      description: |
        OPRA option symbol in URL-safe form:
        `{ticker}__{YYMMDD}{C|P}{strike×1000, 8 digits}` — the ticker and the
        15-character contract block are joined by a **double underscore**
        (`__`). For example, an AAPL $250 call expiring 2026-01-17 is
        `AAPL__260117C00250000`. (A space-padded 21-char OCC form such as
        `AAPL  260117C00250000` is also accepted on some endpoints, but the
        `__` form is canonical and works across all contract routes.)
      schema:
        type: string
        example: SPY__250516C00580000
  schemas:
    ContractChartSuccess:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/ContractChartBar'
        meta:
          $ref: '#/components/schemas/Meta'
    ContractChartBar:
      type: object
      description: |
        One bucketed bar in the contract-chart response.
      required:
        - timestamp
        - timestampEnd
        - belowBidVolume
        - bidVolume
        - aboveBidVolume
        - midVolume
        - belowAskVolume
        - askVolume
        - aboveAskVolume
        - noSideVolume
        - candleVolume
        - candlePremium
        - belowBidPremium
        - bidPremium
        - aboveBidPremium
        - midPremium
        - belowAskPremium
        - askPremium
        - aboveAskPremium
        - noSidePremium
        - dailyVolume
        - dailyPremium
        - vwap
      properties:
        timestamp:
          type: string
        timestampEnd:
          type: string
        belowBidVolume:
          type: integer
          minimum: 0
        bidVolume:
          type: integer
          minimum: 0
        aboveBidVolume:
          type: integer
          minimum: 0
        midVolume:
          type: integer
          minimum: 0
        belowAskVolume:
          type: integer
          minimum: 0
        askVolume:
          type: integer
          minimum: 0
        aboveAskVolume:
          type: integer
          minimum: 0
        noSideVolume:
          type: integer
          minimum: 0
        candleVolume:
          type: integer
          minimum: 0
        candleVolumeNoMl:
          type: integer
          minimum: 0
          description: Single-leg volume (used for multi-leg % calculation).
        candlePremium:
          type: number
          format: double
        belowBidPremium:
          type: number
          format: double
        bidPremium:
          type: number
          format: double
        aboveBidPremium:
          type: number
          format: double
        midPremium:
          type: number
          format: double
        belowAskPremium:
          type: number
          format: double
        askPremium:
          type: number
          format: double
        aboveAskPremium:
          type: number
          format: double
        noSidePremium:
          type: number
          format: double
        dailyVolume:
          type: integer
          minimum: 0
        dailyPremium:
          type: number
          format: double
        vwap:
          type: number
          format: double
        iv:
          type: number
          format: double
          nullable: true
        avgVolume:
          type: number
          format: double
        avgPremium:
          type: number
          format: double
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