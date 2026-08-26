> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Aggregate sentiment scoring across timeframes (VWF / SDF / FIR / Composite)

> Returns a Composite directional score plus its VWF / SDF / FIR
components for one or more trailing timeframes (intraday or
multi-day). Optional moneyness breakdown, optional time-decay
weighting, and a comparative trend block contrasting short- vs
long-horizon sentiment. Reference: PRD Section 8.




## OpenAPI

````yaml /flowseeker-openapi.yaml get /v1/aggregate/{ticker}
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
  /v1/aggregate/{ticker}:
    get:
      tags:
        - Analytics
      summary: >-
        Aggregate sentiment scoring across timeframes (VWF / SDF / FIR /
        Composite)
      description: |
        Returns a Composite directional score plus its VWF / SDF / FIR
        components for one or more trailing timeframes (intraday or
        multi-day). Optional moneyness breakdown, optional time-decay
        weighting, and a comparative trend block contrasting short- vs
        long-horizon sentiment. Reference: PRD Section 8.
      operationId: getAggregate
      parameters:
        - $ref: '#/components/parameters/Ticker'
        - name: timeframes
          in: query
          required: false
          description: |
            Comma-separated timeframes, or `all`. Supported atoms:
            `1h, 4h, 1d, 7d, 30d, 90d`. `all` expands to all six. Unknown
            atoms are treated as a single trading day.
          schema:
            type: string
            default: 1d
            example: 1d,7d,30d
        - name: include_breakdown
          in: query
          required: false
          description: Attach the per-timeframe VWF/SDF/FIR component split.
          schema:
            type: boolean
            default: true
        - name: include_moneyness
          in: query
          required: false
          description: Attach a `byMoneyness` array (deep_itm → deep_otm).
          schema:
            type: boolean
            default: false
        - name: moneyness_filter
          in: query
          required: false
          schema:
            type: string
            enum:
              - deep_itm
              - itm
              - atm
              - otm
              - deep_otm
              - all
            default: all
        - name: expiration_filter
          in: query
          required: false
          description: Restrict to one expiration bucket.
          schema:
            type: string
            enum:
              - 0dte
              - weekly
              - monthly
              - leaps
              - all
            default: all
        - name: time_decay
          in: query
          required: false
          description: Apply exponential time decay to VWF / SDF / FIR components.
          schema:
            type: boolean
            default: false
        - name: time_decay_half_life
          in: query
          required: false
          description: >-
            Half-life in minutes for the decay (only applied when
            `timeDecay=true`).
          schema:
            type: integer
            minimum: 1
            default: 30
        - name: date
          in: query
          required: false
          schema:
            type: string
            format: date
      responses:
        '200':
          description: Aggregate sentiment by timeframe.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AggregateSuccess'
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
  schemas:
    AggregateSuccess:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          $ref: '#/components/schemas/AggregateResponse'
        meta:
          $ref: '#/components/schemas/Meta'
    AggregateResponse:
      type: object
      required:
        - ticker
        - generatedAt
        - byTimeframe
        - trend
      properties:
        ticker:
          type: string
        generatedAt:
          type: string
          format: date-time
        byTimeframe:
          type: object
          additionalProperties:
            $ref: '#/components/schemas/TimeframeAggregate'
          description: |
            Map keyed by timeframe id (`1h`, `4h`, `1d`, `7d`, `30d`,
            `90d`, …). Only the requested timeframes appear; missing
            entries indicate the underlying query failed for that horizon.
        trend:
          $ref: '#/components/schemas/TrendAnalysis'
        byMoneyness:
          type: array
          description: Present when `includeMoneyness=true`.
          items:
            $ref: '#/components/schemas/MoneynessAggregate'
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
    TimeframeAggregate:
      type: object
      required:
        - composite
        - direction
        - signalStrength
        - confidence
        - sweepAlignment
        - tradeCount
        - totalPremium
        - sweepCount
        - avgFlowScore
      properties:
        composite:
          type: integer
          minimum: -100
          maximum: 100
          description: 0.4×VWF + 0.35×SDF + 0.25×FIR (clamped to ±100).
        direction:
          type: string
          enum:
            - strong_bullish
            - bullish
            - neutral
            - bearish
            - strong_bearish
        signalStrength:
          type: string
          enum:
            - strong
            - moderate
            - weak
            - neutral
        confidence:
          type: number
          minimum: 0
          maximum: 1
        sweepAlignment:
          type: boolean
          description: True when VWF and SDF agree in direction.
        components:
          $ref: '#/components/schemas/ScoreComponents'
        tradeCount:
          type: integer
          minimum: 0
        totalPremium:
          type: number
        sweepCount:
          type: integer
          minimum: 0
        avgFlowScore:
          type: number
        timeDecayApplied:
          type: boolean
          description: Present only when time decay was applied.
    TrendAnalysis:
      type: object
      required:
        - shortVsLong
        - momentum
        - description
      properties:
        shortVsLong:
          type: string
          enum:
            - stable
            - bullish_divergence
            - bearish_divergence
            - improving
            - deteriorating
        momentum:
          type: string
          enum:
            - stable
            - accelerating_bullish
            - accelerating_bearish
            - mixed
        description:
          type: string
          description: Human-readable interpretation of the short→long horizon contour.
    MoneynessAggregate:
      type: object
      required:
        - category
        - composite
        - tradeCount
        - premium
        - pctOfTotal
      properties:
        category:
          type: string
          enum:
            - DEEP_ITM
            - ITM
            - ATM
            - OTM
            - DEEP_OTM
        composite:
          type: integer
        tradeCount:
          type: integer
          minimum: 0
        premium:
          type: number
        pctOfTotal:
          type: number
    ScoreComponents:
      type: object
      required:
        - vwf
        - sdf
        - fir
        - bullishPremium
        - bearishPremium
        - sweepPremium
      properties:
        vwf:
          type: number
          description: 'Volume-Weighted Flow: Σ(premium × flowScore) / Σ(premium)'
        sdf:
          type: number
          description: Sweep Dominance Factor.
        fir:
          type: number
          description: 'Flow Imbalance Ratio: (bullish − bearish) / total directional × 100'
        bullishPremium:
          type: number
        bearishPremium:
          type: number
        sweepPremium:
          type: number
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