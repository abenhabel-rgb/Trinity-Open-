> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Aggregate flow over an arbitrary [start, end] window

> Server-side aggregation across an arbitrary `[startTime, endTime]`
window — no row cap. Returns trade/sweep counts, VWF/SDF/FIR, and a
bullish/bearish/neutral premium split with a one-line interpretation.
Useful for arbitrary slicing without paging the full trade list.




## OpenAPI

````yaml /flowseeker-openapi.yaml get /v1/flow/{ticker}/aggregate
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
  /v1/flow/{ticker}/aggregate:
    get:
      tags:
        - Flow
      summary: Aggregate flow over an arbitrary [start, end] window
      description: |
        Server-side aggregation across an arbitrary `[startTime, endTime]`
        window — no row cap. Returns trade/sweep counts, VWF/SDF/FIR, and a
        bullish/bearish/neutral premium split with a one-line interpretation.
        Useful for arbitrary slicing without paging the full trade list.
      operationId: getFlowAggregate
      parameters:
        - $ref: '#/components/parameters/Ticker'
        - $ref: '#/components/parameters/StartTime'
        - $ref: '#/components/parameters/EndTime'
        - name: option_type
          in: query
          required: false
          schema:
            type: string
            enum:
              - call
              - put
              - all
            default: all
        - name: min_premium
          in: query
          required: false
          schema:
            type: number
            format: double
        - name: exclude_multi_leg
          in: query
          required: false
          description: Exclude trades flagged as part of a multi-leg structure.
          schema:
            type: boolean
            default: false
        - name: min_dte
          in: query
          required: false
          schema:
            type: integer
            minimum: 0
        - name: max_dte
          in: query
          required: false
          schema:
            type: integer
            minimum: 0
        - name: date
          in: query
          required: false
          schema:
            type: string
            format: date
      responses:
        '200':
          description: Window-aggregated flow scores.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FlowAggregateSuccess'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '402':
          $ref: '#/components/responses/InsufficientCredits'
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
    Ticker:
      name: ticker
      in: path
      required: true
      description: Underlying ticker symbol (uppercase, e.g. `SPY`, `AAPL`).
      schema:
        type: string
        example: SPY
    StartTime:
      name: start_time
      in: query
      required: true
      description: |
        Lower bound of the window. Accepts RFC 3339
        (`2026-05-27T13:30:00Z`) or Unix seconds.
      schema:
        type: string
        example: '2026-05-27T13:30:00Z'
    EndTime:
      name: end_time
      in: query
      required: true
      description: Upper bound of the window (RFC 3339 or Unix seconds).
      schema:
        type: string
        example: '2026-05-27T20:00:00Z'
  schemas:
    FlowAggregateSuccess:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          $ref: '#/components/schemas/FlowAggregateResponse'
        meta:
          $ref: '#/components/schemas/Meta'
    FlowAggregateResponse:
      type: object
      required:
        - ticker
        - startTime
        - endTime
        - tradeCount
        - sweepCount
        - totalPremium
        - aggregate
        - premiumSplit
        - interpretation
        - queryTimeMs
      properties:
        ticker:
          type: string
        startTime:
          type: string
          format: date-time
        endTime:
          type: string
          format: date-time
        tradeCount:
          type: integer
          minimum: 0
        sweepCount:
          type: integer
          minimum: 0
        totalPremium:
          type: number
        aggregate:
          $ref: '#/components/schemas/WindowAggregateScores'
        premiumSplit:
          $ref: '#/components/schemas/WindowPremiumSplit'
        interpretation:
          $ref: '#/components/schemas/WindowInterpretation'
        queryTimeMs:
          type: integer
          minimum: 0
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
    WindowAggregateScores:
      allOf:
        - $ref: '#/components/schemas/AggregateScores'
        - type: object
          required:
            - composite
          properties:
            composite:
              type: number
              description: Composite roll-up of VWF/SDF/FIR for the window.
    WindowPremiumSplit:
      type: object
      required:
        - bullishPremium
        - bearishPremium
        - neutralPremium
        - netPremium
        - bullishCount
        - bearishCount
        - neutralCount
        - sweepPremium
      properties:
        bullishPremium:
          type: number
        bearishPremium:
          type: number
        neutralPremium:
          type: number
        netPremium:
          type: number
        bullishCount:
          type: integer
          minimum: 0
        bearishCount:
          type: integer
          minimum: 0
        neutralCount:
          type: integer
          minimum: 0
        sweepPremium:
          type: number
    WindowInterpretation:
      type: object
      required:
        - bias
        - signalStrength
      properties:
        bias:
          type: string
          enum:
            - bullish
            - bearish
            - neutral
            - mixed
        signalStrength:
          type: string
          enum:
            - strong
            - moderate
            - weak
    AggregateScores:
      type: object
      description: Window-level scoring components.
      required:
        - vwf
        - sdf
        - fir
      properties:
        vwf:
          type: number
          description: Volume-Weighted Flow score (-100..+100).
        sdf:
          type: number
          description: Sweep-Dominant Flow score (-100..+100).
        fir:
          type: number
          description: Flow Imbalance Ratio (-100..+100).
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
    Forbidden:
      description: >-
        API key revoked/expired, monthly quota exceeded, or the account's API
        access is suspended (`account_suspended`).
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            quotaExhausted:
              value:
                error:
                  code: QUOTA_EXCEEDED
                  message: Monthly quota for this API key has been exhausted.
            accountSuspended:
              value:
                error:
                  code: account_suspended
                  message: >-
                    API access has been suspended for this account. Contact
                    support.
    NotFound:
      description: Unknown resource (ticker / sector / window with no data).
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            noData:
              value:
                error:
                  code: NOT_FOUND
                  message: No trades found for AAPL on 2026-05-27 with timeframe 1d
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
    Unavailable:
      description: >-
        Underlying data source temporarily unavailable, or the credit balance
        could not be verified (`credit_check_failed`). Safe to retry.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            ingestionLag:
              value:
                error:
                  code: UNAVAILABLE
                  message: Live feed is degraded; please retry in a few seconds.
            creditCheckFailed:
              value:
                error:
                  code: credit_check_failed
                  message: Could not verify credit balance. Please retry.
  securitySchemes:
    bearerApiKey:
      type: http
      scheme: bearer
      bearerFormat: fs_live_*
      description: |
        Skylit API key in the `Authorization` header
        (`Authorization: Bearer fs_live_<key>`). `X-API-Key` is also accepted.

````