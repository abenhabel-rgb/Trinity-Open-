> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Moneyness breakdown with pattern detection

> Splits calls and puts across `deep_itm / itm / atm / otm /
deep_otm` buckets with premium, sentiment, percentage of total,
and trade count. Surfaces detected patterns (e.g. heavy OTM call
accumulation, ATM concentration, deep-OTM lottery tickets) and a
directional `signal`/`dominantStrategy` interpretation.




## OpenAPI

````yaml /flowseeker-openapi.yaml get /v1/moneyness/{ticker}
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
  /v1/moneyness/{ticker}:
    get:
      tags:
        - Analytics
      summary: Moneyness breakdown with pattern detection
      description: |
        Splits calls and puts across `deep_itm / itm / atm / otm /
        deep_otm` buckets with premium, sentiment, percentage of total,
        and trade count. Surfaces detected patterns (e.g. heavy OTM call
        accumulation, ATM concentration, deep-OTM lottery tickets) and a
        directional `signal`/`dominantStrategy` interpretation.
      operationId: getMoneyness
      parameters:
        - $ref: '#/components/parameters/Ticker'
        - name: timeframe
          in: query
          required: false
          schema:
            type: string
            enum:
              - intraday
              - daily
              - 7d
              - 30d
            default: daily
        - name: date
          in: query
          required: false
          schema:
            type: string
            format: date
        - name: min_premium
          in: query
          required: false
          schema:
            type: number
            format: double
      responses:
        '200':
          description: Moneyness breakdown with patterns + interpretation.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MoneynessSuccess'
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
    MoneynessSuccess:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          $ref: '#/components/schemas/MoneynessResponse'
        meta:
          $ref: '#/components/schemas/Meta'
    MoneynessResponse:
      type: object
      required:
        - ticker
        - timeframe
        - moneynessBreakdown
        - notablePatterns
        - interpretation
      properties:
        ticker:
          type: string
        timeframe:
          type: string
        moneynessBreakdown:
          $ref: '#/components/schemas/MoneynessFullBreakdown'
        notablePatterns:
          type: array
          items:
            $ref: '#/components/schemas/MoneynessNotablePattern'
        interpretation:
          $ref: '#/components/schemas/MoneynessInterpretation'
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
    MoneynessFullBreakdown:
      type: object
      required:
        - calls
        - puts
      properties:
        calls:
          $ref: '#/components/schemas/MoneynessOptionTypeBreakdown'
        puts:
          $ref: '#/components/schemas/MoneynessOptionTypeBreakdown'
    MoneynessNotablePattern:
      type: object
      required:
        - pattern
        - description
        - significance
      properties:
        pattern:
          type: string
          enum:
            - otm_call_accumulation
            - otm_put_accumulation
            - atm_concentration
            - lottery_ticket_calls
            - itm_stock_replacement
            - heavy_put_skew
            - heavy_call_skew
        description:
          type: string
          description: Human-readable description of the pattern.
        significance:
          type: string
          enum:
            - high
            - medium
            - low
        metrics:
          $ref: '#/components/schemas/MoneynessPatternMetrics'
    MoneynessInterpretation:
      type: object
      required:
        - convictionFocus
        - dominantStrategy
        - signal
      properties:
        convictionFocus:
          type: string
          enum:
            - otm_calls
            - otm_puts
            - atm
            - distributed
            - none
        dominantStrategy:
          type: string
          enum:
            - speculative_bullish
            - call_selling
            - bearish_speculation
            - put_selling
            - directional_bullish
            - directional_bearish
            - mixed
            - no_activity
        signal:
          type: string
          enum:
            - bullish
            - moderately_bullish
            - neutral
            - moderately_bearish
            - bearish
    MoneynessOptionTypeBreakdown:
      type: object
      required:
        - deepItm
        - itm
        - atm
        - otm
        - deepOtm
        - totalPremium
        - totalTrades
      properties:
        deepItm:
          $ref: '#/components/schemas/MoneynessCategoryMetrics'
        itm:
          $ref: '#/components/schemas/MoneynessCategoryMetrics'
        atm:
          $ref: '#/components/schemas/MoneynessCategoryMetrics'
        otm:
          $ref: '#/components/schemas/MoneynessCategoryMetrics'
        deepOtm:
          $ref: '#/components/schemas/MoneynessCategoryMetrics'
        totalPremium:
          type: number
        totalTrades:
          type: integer
          minimum: 0
    MoneynessPatternMetrics:
      type: object
      required:
        - premium
        - pctOfTotal
        - sentiment
      properties:
        premium:
          type: number
        pctOfTotal:
          type: number
        sentiment:
          type: integer
    MoneynessCategoryMetrics:
      type: object
      required:
        - premium
        - sentiment
        - pctOfTotal
        - tradeCount
        - weightedPremium
      properties:
        premium:
          type: number
        sentiment:
          type: integer
          minimum: -100
          maximum: 100
        pctOfTotal:
          type: number
        tradeCount:
          type: integer
          minimum: 0
        weightedPremium:
          type: number
          description: >-
            Premium scaled by a moneyness weight (deeper OTM = higher
            multiplier).
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