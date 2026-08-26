> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Contracts with significant OI changes

> Contracts whose open interest changed by at least
`min_oi_change` (or `min_oi_change_pct`) on the target date. `direction`
narrows the result to opening (OI ↑) or closing (OI ↓) flow.




## OpenAPI

````yaml /flowseeker-openapi.yaml get /v1/contract/unusual-oi
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
  /v1/contract/unusual-oi:
    get:
      tags:
        - Contract
      summary: Contracts with significant OI changes
      description: |
        Contracts whose open interest changed by at least
        `min_oi_change` (or `min_oi_change_pct`) on the target date. `direction`
        narrows the result to opening (OI ↑) or closing (OI ↓) flow.
      operationId: getContractUnusualOi
      parameters:
        - $ref: '#/components/parameters/DiscoveryLimit'
        - in: query
          name: min_oi_change
          schema:
            type: integer
            default: 500
        - in: query
          name: min_oi_change_pct
          schema:
            type: number
            format: double
            default: 25
        - in: query
          name: ticker
          schema:
            type: string
        - in: query
          name: right
          schema:
            type: string
            enum:
              - C
              - P
        - in: query
          name: min_dte
          schema:
            type: integer
        - in: query
          name: max_dte
          schema:
            type: integer
        - in: query
          name: min_premium
          schema:
            type: number
            format: double
        - in: query
          name: min_volume
          schema:
            type: integer
            minimum: 0
        - in: query
          name: date
          required: false
          description: |
            Target trading date (`YYYY-MM-DD`). Defaults to the **previous
            calendar day** (not the current trading date).
          schema:
            type: string
            format: date
        - in: query
          name: order_by
          schema:
            type: string
            enum:
              - oi_change
              - oi_change_pct
              - volume
              - premium
            default: oi_change
        - in: query
          name: direction
          schema:
            type: string
            enum:
              - opening
              - closing
              - both
            default: both
        - in: query
          name: only_sweeps
          schema:
            type: boolean
        - in: query
          name: only_multi_leg
          schema:
            type: boolean
        - in: query
          name: exclude_multi_leg
          schema:
            type: boolean
      responses:
        '200':
          description: Contracts ranked by OI change.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnusualOiListSuccess'
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
    DiscoveryLimit:
      name: limit
      in: query
      required: false
      description: Maximum rows to return.
      schema:
        type: integer
        minimum: 1
        maximum: 200
        default: 50
  schemas:
    UnusualOiListSuccess:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/UnusualOiItem'
        meta:
          $ref: '#/components/schemas/Meta'
    UnusualOiItem:
      type: object
      required:
        - symbol
        - ticker
        - expiration
        - strike
        - right
        - dte
        - date
        - openInterest
        - prevOi
        - oiChange
        - oiChangePct
        - volume
        - premium
        - volumeOiRatio
        - bidVolume
        - askVolume
        - lastPrice
        - underlyingPrice
        - iv
        - positionType
        - sweepVolume
        - sweepPremium
        - multiLegVolume
        - multiLegPremium
      properties:
        symbol:
          type: string
        ticker:
          type: string
        expiration:
          type: string
          format: date
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
        date:
          type: string
          format: date
        openInterest:
          type: integer
          minimum: 0
        prevOi:
          type: integer
          minimum: 0
        oiChange:
          type: integer
        oiChangePct:
          type: number
          format: double
        volume:
          type: integer
          minimum: 0
        premium:
          type: number
          format: double
        volumeOiRatio:
          type: number
          format: double
        bidVolume:
          type: integer
          minimum: 0
        askVolume:
          type: integer
          minimum: 0
        lastPrice:
          type: number
          format: double
        underlyingPrice:
          type: number
          format: double
        iv:
          type: number
          format: double
        positionType:
          type: string
          enum:
            - opening
            - closing
        sweepVolume:
          type: integer
          minimum: 0
        sweepPremium:
          type: number
          format: double
        multiLegVolume:
          type: integer
          minimum: 0
        multiLegPremium:
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