> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Paginated off-exchange (TRF) prints

> Server-side filtered dark-pool prints from the off-exchange tape
(FINRA TRF, publisher FINN/FINC). Defaults to **today (ET)** with a
**$1,000,000** minimum notional (the blocks-by-default rule); pass
`min_notional=0` for the full firehose. The trade-date span is capped
at **31 days** per request — page with `limit`/`offset` or narrow the
range for more. Prints carry **no side, BBO, or greeks**. Pagination
state (`limit`, `offset`, `count`, `hasMore`) is returned in `meta`.




## OpenAPI

````yaml /flowseeker-openapi.yaml get /v1/dark-pool/trades
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
  /v1/dark-pool/trades:
    get:
      tags:
        - Dark Pool
      summary: Paginated off-exchange (TRF) prints
      description: |
        Server-side filtered dark-pool prints from the off-exchange tape
        (FINRA TRF, publisher FINN/FINC). Defaults to **today (ET)** with a
        **$1,000,000** minimum notional (the blocks-by-default rule); pass
        `min_notional=0` for the full firehose. The trade-date span is capped
        at **31 days** per request — page with `limit`/`offset` or narrow the
        range for more. Prints carry **no side, BBO, or greeks**. Pagination
        state (`limit`, `offset`, `count`, `hasMore`) is returned in `meta`.
      operationId: getDarkPoolTrades
      parameters:
        - name: tickers
          in: query
          required: false
          description: >-
            Comma-separated tickers to include (e.g. `AAPL,NVDA`). Omit for all
            names.
          schema:
            type: string
            example: AAPL,NVDA
        - name: date
          in: query
          required: false
          description: Single trade date (`YYYY-MM-DD`, ET). Defaults to today (ET).
          schema:
            type: string
            format: date
        - name: date_start
          in: query
          required: false
          description: >-
            Inclusive start of a trade-date range (`YYYY-MM-DD`, ET). Max span
            31 days.
          schema:
            type: string
            format: date
        - name: date_end
          in: query
          required: false
          description: >-
            Inclusive end of a trade-date range (`YYYY-MM-DD`, ET). Max span 31
            days.
          schema:
            type: string
            format: date
        - name: time_start
          in: query
          required: false
          description: Inclusive lower bound of the time-of-day window (`HH:MM`, ET).
          schema:
            type: string
            example: '09:30'
        - name: time_end
          in: query
          required: false
          description: Inclusive upper bound of the time-of-day window (`HH:MM`, ET).
          schema:
            type: string
            example: '16:00'
        - name: min_notional
          in: query
          required: false
          description: >-
            Minimum notional (USD). Defaults to 1,000,000. Pass 0 for the
            firehose.
          schema:
            type: number
            format: double
            default: 1000000
        - name: max_notional
          in: query
          required: false
          schema:
            type: number
            format: double
        - name: min_size
          in: query
          required: false
          schema:
            type: integer
            minimum: 0
        - name: max_size
          in: query
          required: false
          schema:
            type: integer
            minimum: 0
        - name: min_price
          in: query
          required: false
          schema:
            type: number
            format: double
        - name: max_price
          in: query
          required: false
          schema:
            type: number
            format: double
        - name: sectors
          in: query
          required: false
          description: Comma-separated GICS sectors to include.
          schema:
            type: string
        - name: industries
          in: query
          required: false
          description: Comma-separated GICS industries to include.
          schema:
            type: string
        - name: venue
          in: query
          required: false
          description: Reporting venue filter. Omit for both.
          schema:
            type: string
            enum:
              - FINN
              - FINC
        - name: limit
          in: query
          required: false
          description: Page size (server caps at 5000).
          schema:
            type: integer
            default: 500
            minimum: 1
            maximum: 5000
        - name: offset
          in: query
          required: false
          description: Row offset for pagination.
          schema:
            type: integer
            default: 0
            minimum: 0
            maximum: 50000
        - name: order
          in: query
          required: false
          description: Sort by trade time.
          schema:
            type: string
            enum:
              - asc
              - desc
            default: desc
      responses:
        '200':
          description: Paginated dark-pool prints for the requested filters.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DarkPoolTradesSuccess'
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
    DarkPoolTradesSuccess:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/DarkPoolPrint'
        meta:
          $ref: '#/components/schemas/DarkPoolTradesMeta'
    DarkPoolPrint:
      type: object
      description: |
        One off-exchange (TRF) print. Carries no side / BBO / greeks.
      required:
        - timestamp
        - ticker
        - price
        - size
        - notional
        - venue
        - sector
        - industry
      properties:
        timestamp:
          type: string
          format: date-time
          description: Trade time, ISO-8601 UTC (millisecond precision).
          example: '2026-07-02T14:31:05.123Z'
        ticker:
          type: string
          description: Underlying (dotted equity symbol, e.g. `BRK.B`).
          example: SPY
        price:
          type: number
          format: double
        size:
          type: integer
          minimum: 0
          description: Shares.
        notional:
          type: number
          format: double
          description: '`price × size` (USD).'
        venue:
          type: string
          enum:
            - FINN
            - FINC
          description: FINRA TRF reporting venue.
        sector:
          type: string
          description: GICS sector of the underlying.
        industry:
          type: string
          description: GICS industry of the underlying.
    DarkPoolTradesMeta:
      allOf:
        - $ref: '#/components/schemas/Meta'
        - type: object
          required:
            - limit
            - offset
            - count
            - hasMore
          properties:
            limit:
              type: integer
              description: Page size applied (after clamping to 1..=5000).
            offset:
              type: integer
              description: Row offset applied.
            count:
              type: integer
              description: Number of prints returned in this page.
            hasMore:
              type: boolean
              description: |
                `true` when the page is full (`count == limit`), so more rows
                may exist. Offset-based heuristic, not an exact total.
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