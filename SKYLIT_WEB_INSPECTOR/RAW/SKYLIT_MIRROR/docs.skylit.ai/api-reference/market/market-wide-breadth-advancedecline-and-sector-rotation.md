> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Market-wide breadth, advance/decline, and sector rotation

> Combines SPY/QQQ/IWM aggregate sentiment with an advance/decline
ratio (over directional FIR) and per-sector rotation signals. Ideal
as a single "is the market risk-on or risk-off right now" probe.




## OpenAPI

````yaml /flowseeker-openapi.yaml get /v1/flow/market-breadth
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
  /v1/flow/market-breadth:
    get:
      tags:
        - Market
      summary: Market-wide breadth, advance/decline, and sector rotation
      description: |
        Combines SPY/QQQ/IWM aggregate sentiment with an advance/decline
        ratio (over directional FIR) and per-sector rotation signals. Ideal
        as a single "is the market risk-on or risk-off right now" probe.
      operationId: getMarketBreadth
      parameters:
        - name: date
          in: query
          required: false
          description: Trading date (YYYY-MM-DD). Defaults to today.
          schema:
            type: string
            format: date
        - name: fir_threshold
          in: query
          required: false
          description: |
            Absolute FIR threshold (in %) used to classify a ticker as
            advancing or declining. Tickers with `|fir| < threshold` count
            as unchanged.
          schema:
            type: number
            format: double
            default: 10
      responses:
        '200':
          description: Market breadth + advance/decline + sector rotation.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MarketBreadthSuccess'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '402':
          $ref: '#/components/responses/InsufficientCredits'
        '403':
          $ref: '#/components/responses/Forbidden'
        '429':
          $ref: '#/components/responses/RateLimited'
        '503':
          $ref: '#/components/responses/Unavailable'
components:
  schemas:
    MarketBreadthSuccess:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          $ref: '#/components/schemas/MarketBreadthResponse'
        meta:
          $ref: '#/components/schemas/Meta'
    MarketBreadthResponse:
      type: object
      required:
        - date
        - majorIndices
        - aggregateSentiment
        - advanceDecline
        - sectorRotation
      properties:
        date:
          type: string
          format: date
        majorIndices:
          type: array
          items:
            $ref: '#/components/schemas/IndexSentiment'
        aggregateSentiment:
          $ref: '#/components/schemas/AggregateSentiment'
        advanceDecline:
          $ref: '#/components/schemas/AdvanceDecline'
        sectorRotation:
          type: array
          items:
            $ref: '#/components/schemas/SectorRotation'
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
    IndexSentiment:
      type: object
      required:
        - ticker
        - bullishPremium
        - bearishPremium
        - netPremium
        - fir
        - sentiment
      properties:
        ticker:
          type: string
        bullishPremium:
          type: number
        bearishPremium:
          type: number
        netPremium:
          type: number
        fir:
          type: number
        sentiment:
          type: string
          enum:
            - strong_bullish
            - bullish
            - slightly_bullish
            - neutral
            - slightly_bearish
            - bearish
            - strong_bearish
    AggregateSentiment:
      type: object
      required:
        - combinedBullish
        - combinedBearish
        - combinedNetPremium
        - combinedFir
        - sentiment
      properties:
        combinedBullish:
          type: number
        combinedBearish:
          type: number
        combinedNetPremium:
          type: number
        combinedFir:
          type: number
        sentiment:
          type: string
          enum:
            - strong_bullish
            - bullish
            - slightly_bullish
            - neutral
            - slightly_bearish
            - bearish
            - strong_bearish
    AdvanceDecline:
      type: object
      required:
        - advancing
        - declining
        - unchanged
        - total
        - ratio
        - breadthPct
        - marketAvgFir
      properties:
        advancing:
          type: integer
          minimum: 0
        declining:
          type: integer
          minimum: 0
        unchanged:
          type: integer
          minimum: 0
        total:
          type: integer
          minimum: 0
        ratio:
          type: number
          description: Advancing / declining (capped). 0.0 means no decliners.
        breadthPct:
          type: number
          description: Share (0–100) of tickers classified as advancing.
        marketAvgFir:
          type: number
          description: Mean FIR across all tickers (-100..+100).
    SectorRotation:
      type: object
      required:
        - sector
        - etf
        - fir
        - netPremium
        - signal
      properties:
        sector:
          type: string
        etf:
          type: string
        fir:
          type: number
        netPremium:
          type: number
        signal:
          type: string
          enum:
            - strong_inflow
            - inflow
            - neutral
            - outflow
            - strong_outflow
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