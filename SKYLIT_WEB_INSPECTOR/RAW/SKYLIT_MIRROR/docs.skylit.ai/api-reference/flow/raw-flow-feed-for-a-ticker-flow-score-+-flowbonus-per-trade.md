> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Raw flow feed for a ticker (Flow Score + FlowBonus per trade)

> Returns the most recent options trades for `{ticker}` within the
requested timeframe, each scored on Skylit's directional Flow Score
(-100 → +100) and conviction-weighted FlowBonus. The response also
includes timeframe-level VWF / SDF / FIR aggregates.




## OpenAPI

````yaml /flowseeker-openapi.yaml get /v1/flow/{ticker}
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
  /v1/flow/{ticker}:
    get:
      tags:
        - Flow
      summary: Raw flow feed for a ticker (Flow Score + FlowBonus per trade)
      description: |
        Returns the most recent options trades for `{ticker}` within the
        requested timeframe, each scored on Skylit's directional Flow Score
        (-100 → +100) and conviction-weighted FlowBonus. The response also
        includes timeframe-level VWF / SDF / FIR aggregates.
      operationId: getFlow
      parameters:
        - $ref: '#/components/parameters/Ticker'
        - $ref: '#/components/parameters/Timeframe'
        - name: limit
          in: query
          required: false
          description: Max trades returned. Server caps this at 500.
          schema:
            type: integer
            default: 100
            minimum: 1
            maximum: 500
        - name: min_premium
          in: query
          required: false
          description: Minimum total premium per trade (USD).
          schema:
            type: number
            format: double
            example: 50000
        - name: option_type
          in: query
          required: false
          description: Filter to calls or puts. `all` returns both.
          schema:
            type: string
            enum:
              - call
              - put
              - all
            default: all
        - name: trade_type
          in: query
          required: false
          description: Filter by trade type. Comma-separated for multiple.
          schema:
            type: string
            enum:
              - sweep
              - multi_leg
              - all
            default: all
        - name: moneyness
          in: query
          required: false
          description: |
            Moneyness category filter. Comma-separated for multiple
            (e.g. `otm,deep_otm`). Unknown tokens are ignored.
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
        - name: start_time
          in: query
          required: false
          description: |
            Optional lower bound for the trade window. Accepts RFC 3339
            (`2026-05-27T13:30:00Z`) or Unix seconds. Omit to use the timeframe.
          schema:
            type: string
        - name: end_time
          in: query
          required: false
          description: Optional upper bound (RFC 3339 or Unix seconds).
          schema:
            type: string
        - name: max_premium
          in: query
          required: false
          description: Maximum total premium per trade (USD).
          schema:
            type: number
            format: double
        - name: min_contracts
          in: query
          required: false
          description: Minimum contract size per trade.
          schema:
            type: integer
            minimum: 0
        - name: max_contracts
          in: query
          required: false
          description: Maximum contract size per trade.
          schema:
            type: integer
            minimum: 0
        - name: single_leg_only
          in: query
          required: false
          description: If `true`, exclude trades flagged as part of a multi-leg structure.
          schema:
            type: boolean
            default: false
        - name: min_dte
          in: query
          required: false
          description: Minimum days to expiration.
          schema:
            type: integer
        - name: max_dte
          in: query
          required: false
          description: Maximum days to expiration.
          schema:
            type: integer
        - name: min_strike
          in: query
          required: false
          description: Minimum strike price (inclusive).
          schema:
            type: number
            format: double
        - name: max_strike
          in: query
          required: false
          description: Maximum strike price (inclusive).
          schema:
            type: number
            format: double
        - name: expiration
          in: query
          required: false
          description: Filter to a single expiration date (YYYY-MM-DD).
          schema:
            type: string
            format: date
        - name: conviction_weights
          in: query
          required: false
          description: |
            Optional JSON object overriding the Flow Score conviction weights.
            Weights must be non-negative and sum to within 0.95–1.05, else 400.
          schema:
            type: string
        - name: min_flow_score
          in: query
          required: false
          description: Filter to trades with `flowScore` ≥ this value (-100..100).
          schema:
            type: integer
            minimum: -100
            maximum: 100
        - name: min_flow_bonus
          in: query
          required: false
          description: Filter to trades with `flowBonus` ≥ this value.
          schema:
            type: integer
            minimum: 0
        - name: min_rvol
          in: query
          required: false
          description: Filter to trades with relative volume ≥ this multiple.
          schema:
            type: number
            format: double
            minimum: 0
            example: 2
        - name: include_clusters
          in: query
          required: false
          description: |
            If `true`, attach `cluster*` fields when a trade is part of a
            multi-leg cluster (sweep, condor, etc.).
          schema:
            type: boolean
            default: true
        - name: date
          in: query
          required: false
          description: Trading date (YYYY-MM-DD). Defaults to current trading date.
          schema:
            type: string
            format: date
            example: '2026-05-27'
      responses:
        '200':
          description: Flow feed for `{ticker}`.
          headers:
            X-RateLimit-Limit:
              schema:
                type: integer
            X-RateLimit-Remaining:
              schema:
                type: integer
            X-RateLimit-Reset:
              schema:
                type: integer
            X-Credits-Remaining:
              description: Credit balance remaining after this request was charged.
              schema:
                type: integer
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FlowSuccess'
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
    Timeframe:
      name: timeframe
      in: query
      required: false
      description: |
        Trailing window label for the request. Supported values:
        `5m`, `15m`, `1h`, `4h`, `1d`.
      schema:
        type: string
        enum:
          - 5m
          - 15m
          - 1h
          - 4h
          - 1d
        default: 1h
  schemas:
    FlowSuccess:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          $ref: '#/components/schemas/FlowResponse'
        meta:
          $ref: '#/components/schemas/Meta'
    FlowResponse:
      type: object
      required:
        - ticker
        - timeframe
        - trades
        - aggregate
        - tradeCount
        - sweepCount
        - totalPremium
        - queryTimeMs
      properties:
        ticker:
          type: string
        timeframe:
          type: string
        trades:
          type: array
          items:
            $ref: '#/components/schemas/FlowTradeItem'
        aggregate:
          $ref: '#/components/schemas/AggregateScores'
        tradeCount:
          type: integer
          minimum: 0
        sweepCount:
          type: integer
          minimum: 0
        totalPremium:
          type: number
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
    FlowTradeItem:
      type: object
      description: |
        One options trade with full Skylit scoring + context. A subset of
        the most-relevant fields is documented inline; the response may add
        new fields under additive evolution rules.
      required:
        - timestamp
        - tradeId
        - optionType
        - strike
        - expiration
        - dte
        - contracts
        - premium
        - price
        - bid
        - ask
        - mid
        - underlyingPrice
        - isSweep
        - isMultiLeg
        - moneyness
        - scores
      properties:
        timestamp:
          type: string
          format: date-time
        tradeId:
          type: string
          example: flow_188afe42c3a77af2_0
        optionType:
          type: string
          enum:
            - CALL
            - PUT
        strike:
          type: number
        expiration:
          type: string
          format: date
        dte:
          type: integer
          minimum: 0
        dteCategory:
          type: string
          enum:
            - zero_dte
            - weekly
            - monthly
            - leap
        dteFactor:
          type: number
        dteMultiplier:
          type: number
        contracts:
          type: integer
          minimum: 1
        premium:
          type: number
          description: Total premium in USD.
        price:
          type: number
          description: Trade price per contract.
        bid:
          type: number
        ask:
          type: number
        mid:
          type: number
        spreadWidth:
          type: number
        spreadWidthPct:
          type: number
        liquidityGrade:
          type: string
          enum:
            - A
            - B
            - C
            - D
            - F
        underlyingPrice:
          type: number
        isSweep:
          type: boolean
        isMultiLeg:
          type: boolean
        exchangeCount:
          type: integer
          nullable: true
          description: Number of distinct OPRA exchanges that filled the order.
        moneyness:
          type: string
          enum:
            - DEEP_ITM
            - ITM
            - ATM
            - OTM
            - DEEP_OTM
        moneynessPct:
          type: number
        moneynessWeight:
          type: number
        combinedMoneynessDteWeight:
          type: number
        delta:
          type: number
          nullable: true
        notionalDeltaExposure:
          type: number
          nullable: true
        openInterest:
          type: integer
          minimum: 0
        dailyVolume:
          type: integer
          minimum: 0
        volOiRatio:
          type: number
          nullable: true
        volOiScore:
          type: integer
        sizeOiRatio:
          type: number
          nullable: true
        sizeOiScore:
          type: integer
        oiIsZero:
          type: boolean
        rvol:
          type: number
          nullable: true
        rvolScore:
          type: integer
        rvolCategory:
          type: string
          nullable: true
        iv:
          type: number
          nullable: true
        ivChangePct:
          type: number
          nullable: true
        relativePremium:
          type: number
          description: Premium relative to the contract's average premium.
        scores:
          $ref: '#/components/schemas/FlowTradeScores'
        cluster:
          $ref: '#/components/schemas/ClusterInfo'
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
    FlowTradeScores:
      type: object
      description: Per-trade scoring outputs (PRD Section 10).
      required:
        - flowScore
        - flowScoreInterpretation
        - flowBonus
        - flowBonusInterpretation
        - baseDirection
        - convictionMultiplier
      properties:
        flowScore:
          type: integer
          description: Composite directional score (-100..+100).
          minimum: -100
          maximum: 100
        flowScoreInterpretation:
          type: string
          example: strong_bullish
        flowBonus:
          type: integer
          description: Conviction bonus (0..+100).
          minimum: 0
          maximum: 100
        flowBonusInterpretation:
          type: string
          example: high_conviction
        baseDirection:
          type: integer
          description: Pre-conviction directional score (-100..+100).
        convictionMultiplier:
          type: number
          description: Multiplier applied to base direction to yield `flowScore`.
    ClusterInfo:
      type: object
      description: |
        Present when `includeClusters=true` and the trade is part of a sweep,
        condor, or other multi-leg cluster.
      required:
        - clusterId
        - clusterTradeCount
        - clusterTotalPremium
        - clusterTimeSpanSeconds
      properties:
        clusterId:
          type: string
        clusterTradeCount:
          type: integer
          minimum: 1
        clusterTotalPremium:
          type: number
        clusterTimeSpanSeconds:
          type: integer
          minimum: 0
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