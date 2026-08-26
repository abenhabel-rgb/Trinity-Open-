import{j as e}from"./index-Cv6VCl5d.js";import{u as i,C as r,P as o}from"./ArticlePage-BzhK0Axy.js";import"./ArticleTag-BCz4VRd4.js";function s(n){const t={a:"a",code:"code",em:"em",h2:"h2",h3:"h3",li:"li",ol:"ol",p:"p",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",ul:"ul",...i(),...n.components};return e.jsxs(e.Fragment,{children:[e.jsx(t.h2,{children:"The Three Pages"}),`
`,e.jsxs(t.p,{children:["Flowseeker isn't one screen — it's three connected ones. The ",e.jsx(t.a,{href:"/learn/intro-to-flowseeker",children:"Introduction to Flowseeker"})," article covered the live feed in depth, but that's only one of three sibling pages that work together. Knowing what each one is for, and how to move between them, is the difference between fighting the UI and using it."]}),`
`,e.jsx(t.p,{children:"The three pages are:"}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Live Feed"}),' — the real-time tape, one row per print. This is what most people mean when they say "Flowseeker."']}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Flow Scanner"})," — a contract-level view of the day's activity. Every print for a given contract (ticker + expiration + strike + C/P) is rolled up into a single row with aggregated totals, sentiment breakdowns, and OI dynamics."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Flow Tracker"})," — a persistent list of prints you've bookmarked, with live P/L and close-detection."]}),`
`]}),`
`,e.jsxs(t.p,{children:["They share a common drill-down — the chart modal — and they share the same underlying data. What changes between them is the ",e.jsx(t.em,{children:"unit of analysis"}),": individual prints vs. aggregated per-contract activity vs. bookmarked follow-up."]}),`
`,e.jsx(r,{type:"analogy",children:e.jsx(t.p,{children:"Live Feed is the tape printing trade by trade. Scanner is the scoreboard showing how each contract's day totals look. Tracker is a notebook of positions you want to remember. Same underlying data, three different ways of seeing it."})}),`
`,e.jsx(t.h2,{children:"How You Get There"}),`
`,e.jsxs(t.p,{children:["On desktop, all three pages sit together in the left sidebar under a ",e.jsx(t.strong,{children:"FLOWSEEKER"})," section:"]}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsx(t.li,{children:"Live Feed (the radio icon)"}),`
`,e.jsx(t.li,{children:"Flow Scanner (the magnifying-glass icon)"}),`
`,e.jsx(t.li,{children:"Flow Tracker (the radar icon)"}),`
`]}),`
`,e.jsxs(t.p,{children:["On mobile, you pick ",e.jsx(t.strong,{children:"FLOWSEEKER"})," from the module selector in the bottom navigation and then switch between Live / Scanner / Tracker from the sub-pills."]}),`
`,e.jsxs(t.p,{children:["Some users will also see a fourth item — ",e.jsx(t.strong,{children:"Settings"})," — for configuring programmatic access and integrations. That's out of scope for this article; if you're here to figure out how to read and react to flow, the three pages above are all you need."]}),`
`,e.jsx(r,{type:"tip",children:e.jsx(t.p,{children:"If you ever see a small number badge on the Tracker icon, it means one or more of your tracked trades has had a close event detected (partial exit, full exit, expiration). Clicking through clears the badge. More on that in the Tracker section."})}),`
`,e.jsx(t.h2,{children:"Live Feed: What's There Beyond the Basics"}),`
`,e.jsxs(t.p,{children:["The ",e.jsx(t.a,{href:"/learn/intro-to-flowseeker",children:"Introduction"})," walks through the overview bar, the 22 columns in the feed, and the basic filter sidebar. Those are the fundamentals. But the Live Feed page has several features that aren't obvious until someone points them out — and most of them dramatically improve how you work in it once you know they exist."]}),`
`,e.jsx(t.h3,{children:"Multiple Feed Tabs"}),`
`,e.jsxs(t.p,{children:["You can keep up to ",e.jsx(t.strong,{children:"10 named tabs"})," across the top of the Live Feed. Each tab holds its own filter configuration, its own column layout, its own ticker-scope, and its own flow-highlighting rules. Right-clicking a tab gives you ",e.jsx(t.strong,{children:"Rename"}),", ",e.jsx(t.strong,{children:"Duplicate"}),", and ",e.jsx(t.strong,{children:"Delete"}),"."]}),`
`,e.jsx(t.p,{children:"This is the single most underused feature in Flowseeker. Most people work from the default tab forever. Instead:"}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsx(t.li,{children:'Set up a "Big Tech Only" tab with Ticker scope locked to AAPL, MSFT, NVDA, META, GOOGL.'}),`
`,e.jsx(t.li,{children:`Duplicate it, change the tickers, and you've got "Semiconductors" for AMD, INTC, AVGO, TSM.`}),`
`,e.jsx(t.li,{children:'Set up a "High Conviction Sweeps" tab with $250K+ premium, Sweeps Only, and |Flow Score| > 60.'}),`
`,e.jsx(t.li,{children:'Keep a "Full Firehose" tab with minimal filters for when you want to watch unfiltered tape.'}),`
`]}),`
`,e.jsx(t.p,{children:"Switching between tabs is instant and your filter state is preserved. Tabs persist across sessions — close the browser and your setup is still there when you come back."}),`
`,e.jsx(t.h3,{children:"Ticker-Scope Search at the Top"}),`
`,e.jsxs(t.p,{children:["The search bar at the top of the Live Feed lets you ",e.jsx(t.strong,{children:"include or exclude tickers"})," from the current tab. Type a ticker and press Enter (or comma) to add it to the include list. To ",e.jsx(t.strong,{children:"exclude"})," a ticker, prefix it with ",e.jsx(t.code,{children:"!"})," — e.g. ",e.jsx(t.code,{children:"!TSLA"})," to drop all Tesla prints."]}),`
`,e.jsx(t.p,{children:"Backspace with an empty input pops the most recently added tag. This is separate from the Ticker filter in the sidebar — think of the search bar as the fast, ad-hoc way to focus or de-focus the tape in the moment, without digging into the filter panel."}),`
`,e.jsx(t.h3,{children:"Pause, Resume, and Historical Mode"}),`
`,e.jsxs(t.p,{children:["The live feed has a connection indicator at the top-right showing the current state: ",e.jsx(t.strong,{children:"LIVE"}),", ",e.jsx(t.strong,{children:"PAUSED"}),", ",e.jsx(t.strong,{children:"CONNECTING"}),", or ",e.jsx(t.strong,{children:"OFFLINE"}),". Clicking it toggles between Live and Paused."]}),`
`,e.jsxs(t.p,{children:["Pausing freezes the visible feed so you can study a cluster of prints without the tape scrolling out from under you. Incoming trades are held in a buffer while you're paused and merged in when you resume — but the buffer is bounded by your ",e.jsx(t.strong,{children:"Results limit"})," (50 / 100 / 250 / 500), so a long pause during heavy flow can push older buffered trades out before you ever see them. For short pauses, you'll catch up to everything that came in. For long ones, treat resume as ",e.jsx(t.em,{children:'"catch up to roughly the last N prints"'}),", not ",e.jsx(t.em,{children:'"play back everything I missed."'})]}),`
`,e.jsxs(t.p,{children:["You can also switch the feed into ",e.jsx(t.strong,{children:"Historical"})," mode by picking a past trading day. The control changes to a ",e.jsx(t.strong,{children:"HISTORICAL"})," badge instead of the live-connection indicator. Useful for reviewing yesterday's tape — or comparing today's session against a prior one by opening a second tab in historical mode."]}),`
`,e.jsx(t.h3,{children:"Results Cap and Sort"}),`
`,e.jsxs(t.p,{children:["The ",e.jsx(t.strong,{children:"Results"})," dropdown in the header sets how many rows are shown — ",e.jsx(t.strong,{children:"50, 100, 250, or 500"}),". The ",e.jsx(t.strong,{children:"Sort by"})," dropdown lets you order the feed by ",e.jsx(t.strong,{children:"Time"}),", ",e.jsx(t.strong,{children:"Premium"}),", or ",e.jsx(t.strong,{children:"Size"}),"."]}),`
`,e.jsxs(t.p,{children:["One important quirk: when you sort by anything other than Time, Flowseeker applies a size floor — results are restricted to trades with at least ",e.jsx(t.strong,{children:"$25K premium or 150+ contracts"}),". This is intentional. Sorting a raw feed by Premium without a floor would bury most of your session under a single whale print; the floor keeps the non-Time sorts useful across the whole session."]}),`
`,e.jsx(t.h3,{children:"Columns Panel"}),`
`,e.jsxs(t.p,{children:["Clicking ",e.jsx(t.strong,{children:"Columns"})," opens a panel where you can:"]}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsx(t.li,{children:"Toggle individual columns on or off."}),`
`,e.jsx(t.li,{children:"Drag the grip handles to reorder columns."}),`
`,e.jsxs(t.li,{children:["Configure ",e.jsx(t.strong,{children:"Flow Highlighting"})," — conditional color-coding rules that highlight rows when specific ratios (like Volume/OI or Size/OI) exceed thresholds you define."]}),`
`]}),`
`,e.jsx(t.p,{children:`Each of these is per-tab. That's important: your "High Conviction Sweeps" tab can hide columns like OTM % that don't matter for that use case and show a custom Flow Highlighting rule that fires when V/OI > 2.0. Your "Full Firehose" tab can show everything and skip the highlighting. They don't conflict.`}),`
`,e.jsx(t.h3,{children:"Sharing What You're Looking At"}),`
`,e.jsxs(t.p,{children:["The ",e.jsx(t.strong,{children:"Share"})," button in the header gives you two options: ",e.jsx(t.strong,{children:"Copy Image"})," and ",e.jsx(t.strong,{children:"Save Image"}),". It captures a snapshot of the current feed state — tab name, filters applied, visible rows — as a PNG you can drop into Slack or a Discord message."]}),`
`,e.jsxs(t.p,{children:["This is feed-level sharing. Per-trade sharing to Discord (with the chart and context) lives inside the ",e.jsx(t.strong,{children:"chart modal"}),", covered later in this article."]}),`
`,e.jsx(t.h3,{children:"Multi-Leg Strategy Modal"}),`
`,e.jsxs(t.p,{children:["When a multi-leg strategy prints (vertical spread, straddle, iron condor, etc.), the affected rows in the feed are tagged with a ",e.jsx(t.strong,{children:"Layers icon"}),". A single leg of a complex trade by itself is hard to read — you're seeing one piece of a structured position, and trying to interpret it as a directional bet will mislead you. Clicking the Layers icon (or the strategy badge on the row) opens a modal that shows the entire strategy in one place:"]}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsxs(t.li,{children:["The ",e.jsx(t.strong,{children:"strategy type"})," (Vertical Spread, Iron Condor, Strangle, etc.) and ",e.jsx(t.strong,{children:"leg count"})," in the header."]}),`
`,e.jsxs(t.li,{children:["A ",e.jsx(t.strong,{children:"summary"})," of the trade: Net Premium across all legs, Total Size, the Strike Range, and a Net Sentiment label color-coded bullish, bearish, or neutral."]}),`
`,e.jsxs(t.li,{children:["A ",e.jsx(t.strong,{children:"Strike Structure"})," diagram positioning each leg by strike on a horizontal axis, with calls and puts visually distinguished. This is the fastest way to recognize the trade's shape — a put credit spread shows up as two puts close together, a strangle as a put low and a call high, an iron condor as four legs in a tight symmetric pattern."]}),`
`,e.jsxs(t.li,{children:["A ",e.jsx(t.strong,{children:"per-leg chart"})," for every leg, so you can see how each individual contract has traded since the strategy was put on."]}),`
`]}),`
`,e.jsxs(t.p,{children:["The difference is between ",e.jsx(t.em,{children:`"I see one of three legs of a print I don't understand"`})," and ",e.jsx(t.em,{children:`"I see the full structure of what just got put on, and I can watch each leg's behavior independently."`})," Escape closes the modal."]}),`
`,e.jsx(t.h3,{children:'The "Expand Trades" Link Back From a Chart'}),`
`,e.jsxs(t.p,{children:["When you click a row in the Live Feed and open the chart modal, select a candle on the contract chart, and click ",e.jsx(t.strong,{children:"Expand Trades"}),", Flowseeker ",e.jsx(t.strong,{children:"creates a new feed tab"})," filtered down to that candle's ticker, strike, expiration, and time window."]}),`
`,e.jsx(t.p,{children:`This is a live-feed-only workflow — you get to instantly see every print that made up a specific candle, without reconfiguring filters by hand. If you're trying to understand "what actually drove that spike at 10:47?", this is the fastest path. (The Scanner doesn't have this action — see the next section.)`}),`
`,e.jsx(t.h2,{children:"Flow Scanner: The Day's Activity, Aggregated by Contract"}),`
`,e.jsx(t.p,{children:"The Scanner looks superficially like the Live Feed — it has tabs, filters, and a table of rows — but it's a fundamentally different unit of analysis."}),`
`,e.jsxs(t.p,{children:["In the Live Feed, ",e.jsx(t.strong,{children:"every row is a single trade"}),". A large buyer sweeping 2,000 contracts on SPY $580 calls might produce 3, 5, or even 10 rows on the tape (one per exchange, one per fill). Each row is a print."]}),`
`,e.jsxs(t.p,{children:["In the Scanner, ",e.jsx(t.strong,{children:"every row is a single contract"}),". That same SPY $580 call is one row — and on that one row you see the ",e.jsx(t.em,{children:"aggregate"})," of everything that happened to it today: total volume, total premium, total trade count, bid/ask breakdown, sentiment scores, OI change since yesterday, sweep percentage, multi-leg percentage. If you want to know ",e.jsx(t.em,{children:"which contracts were active today and how they traded"}),", the Scanner is the view."]}),`
`,e.jsx(t.p,{children:"You pick a trading day with the date control at the top, and previous days work the same as today."}),`
`,e.jsx(t.p,{children:"That difference in unit cascades into a lot of UI differences:"}),`
`,e.jsxs(t.table,{children:[e.jsx(t.thead,{children:e.jsxs(t.tr,{children:[e.jsx(t.th,{children:"Feature"}),e.jsx(t.th,{children:"Live Feed"}),e.jsx(t.th,{children:"Flow Scanner"})]})}),e.jsxs(t.tbody,{children:[e.jsxs(t.tr,{children:[e.jsx(t.td,{children:"Unit of analysis"}),e.jsx(t.td,{children:"One row per print (real-time)"}),e.jsx(t.td,{children:"One row per contract (day-aggregated)"})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:"Max tabs"}),e.jsx(t.td,{children:"10"}),e.jsx(t.td,{children:"5"})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:"Date control"}),e.jsx(t.td,{children:"Historical mode picker"}),e.jsx(t.td,{children:"Trading-day picker (prev / next / calendar)"})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:"Filter sidebar"}),e.jsx(t.td,{children:"Premium, Equity Type, Sweeps, Flow Score, DTE, Earnings, Sector, Side"}),e.jsx(t.td,{children:"Same plus OI Growth, contract/chain sentiment sliders, strike ranges, OTM/ITM/0DTE toggles, OPEX Only"})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:"Flow Highlighting"}),e.jsx(t.td,{children:"Per-tab"}),e.jsx(t.td,{children:"Not available"})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:"Columns customization"}),e.jsx(t.td,{children:"Show/hide + drag-reorder"}),e.jsx(t.td,{children:"Drag-reorder (sort)"})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:"Per-row right-click"}),e.jsx(t.td,{children:"Yes"}),e.jsx(t.td,{children:"No"})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:'Chart modal "Expand Trades"'}),e.jsx(t.td,{children:"Creates a new live tab"}),e.jsx(t.td,{children:"Not wired up"})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:"Share"}),e.jsx(t.td,{children:"Image export"}),e.jsx(t.td,{children:"Image export"})]})]})]}),`
`,e.jsx(t.h3,{children:"What Each Scanner Row Tells You"}),`
`,e.jsx(t.p,{children:"Because every row aggregates an entire contract's day, the columns on each row are telling you things the Live Feed can't show in a single line:"}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Total premium, total volume, total trade count"})," — how much real activity hit that contract today, across all prints."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Bid / ask execution mix"})," — what percentage of today's volume hit near the bid vs. near the ask vs. mid-spread. A contract that traded 80% near the ask says something very different than one that traded 60% at the bid."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Bull / bear / neutral percentages"})," — the sentiment breakdown at the contract level and the ticker-chain level, derived from that execution mix and whether the contract is a call or put."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Sweep %, multi-leg %"})," — what fraction of today's volume came through as sweeps or as legs of a complex strategy."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"OI change"})," — the day-over-day change in open interest for that specific contract. This is one of the most important numbers on the Scanner: growing OI + high volume + aggressive bid/ask skew is a much stronger signal than growing volume alone."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Stock price, OTM %, IV, DTE"})," — the positioning context for that contract relative to where the underlying was."]}),`
`]}),`
`,e.jsxs(t.p,{children:["Each row is effectively ",e.jsx(t.em,{children:"a contract's day-long story"}),", compressed to one line."]}),`
`,e.jsx(t.h3,{children:"When to Use the Scanner"}),`
`,e.jsxs(t.p,{children:["The Scanner is where you go when the question you're asking is about ",e.jsx(t.strong,{children:"contracts"}),", not about individual prints. Typical uses:"]}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Which contracts actually moved today?"})," Sort by premium or trade count. The top of the list is where the day's money concentrated."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Which strikes had real new positioning?"})," Filter on positive OI change plus high volume. That's where risk is actually being put on, not rolled."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Which contracts traded aggressively to one side?"})," Use the bid-skew and ask-skew filters, or the contract sentiment slider. You'll surface contracts where one side dominated the day."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Historical review."})," Pick a past date and re-run the same questions. What did unusual activity look like the day before earnings?"]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Structural filters you don't get in the Live Feed."})," OI Growth signal, contract and chain sentiment sliders, OPEX Only, strike-range filters — these only exist on the Scanner because they're aggregate concepts that don't apply to a single print."]}),`
`]}),`
`,e.jsx(t.p,{children:"You won't use the Scanner for real-time reactions — its whole purpose is a day's activity, aggregated at once, and that's not the shape of problem you're solving when the tape is moving."}),`
`,e.jsx(t.h3,{children:"Clicking a Scanner Row"}),`
`,e.jsxs(t.p,{children:["Clicking a row in the Scanner opens the ",e.jsx(t.strong,{children:"same chart modal"})," as the Live Feed, with the same five views. Because the row you clicked is an aggregate, the chart modal's ",e.jsx(t.strong,{children:"Flow Orders"})," footer is especially useful here — it expands the aggregate back out into the individual prints that made it up. One thing that ",e.jsx(t.em,{children:"doesn't"})," work from the Scanner is ",e.jsx(t.strong,{children:"Expand Trades"})," from a candle — that action creates a new Live Feed tab, and the Scanner isn't wired to do that. Everything else (Share to Discord from the modal, switching views, selecting candles, viewing the Strike Distribution) works identically."]}),`
`,e.jsx(t.h2,{children:"Flow Tracker: Following Prints After the Fact"}),`
`,e.jsx(t.p,{children:"The Tracker is a persistent list of trades you've chosen to remember. Unlike the Live Feed (ephemeral — rows scroll off) and the Scanner (query-driven — results change as filters change), the Tracker holds onto a specific set of prints across sessions so you can watch what happens to them."}),`
`,e.jsx(t.h3,{children:"How Trades Get There"}),`
`,e.jsx(t.p,{children:"From the Live Feed, there are two ways to track a trade:"}),`
`,e.jsxs(t.ol,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Bookmark icon"})," — click the star on a trade row."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Right-click → Track trade"})," — from the row context menu."]}),`
`]}),`
`,e.jsxs(t.p,{children:["Both do the same thing: the trade is saved to your account. There's ",e.jsx(t.strong,{children:"no manual add"})," on the Tracker page itself. If you want to track a trade, you do it from the Live Feed at the moment it catches your eye."]}),`
`,e.jsx(r,{type:"tip",children:e.jsx(t.p,{children:"Bookmark aggressively. Trades that look interesting when they print are the ones worth checking an hour later, the next morning, at expiration, or right before earnings. The Tracker is where you build that memory. Removing a trade is a single click — there's no cost to bookmarking one that turns out to be noise."})}),`
`,e.jsx(t.h3,{children:"Two Tabs at the Top: Tracked Flow and Tracked Contracts"}),`
`,e.jsx(t.p,{children:"When you open the Tracker, there are two tabs at the top:"}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Tracked Flow"})," — the active one. This is the list of individual prints you've bookmarked. Each row is one specific trade."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Tracked Contracts"})," — currently locked (you'll see a lock icon and the tab is unclickable). This is a planned surface for tracking by ",e.jsx(t.em,{children:"contract identity"})," (ticker + strike + expiration + C/P) across multiple prints, rather than print-by-print. Not yet available."]}),`
`]}),`
`,e.jsx(t.p,{children:"If you click the locked tab and nothing happens, that's expected — the feature is shipping later."}),`
`,e.jsx(t.h3,{children:"What the Tracked Flow View Shows"}),`
`,e.jsxs(t.p,{children:[e.jsx(t.strong,{children:"On desktop"}),", the page is a split view:"]}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Left"}),": a scroll-synced table of the trade's saved data at the time you bookmarked it — time, ticker, strike, type, expiration, spot, premium, etc. The fixed reference point for the trade."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Right (500px panel)"}),": ",e.jsx(t.strong,{children:"live-updating"})," fields — ",e.jsx(t.strong,{children:"Mid"})," (current mid price of the contract), ",e.jsx(t.strong,{children:"Spot"})," (current underlying price), ",e.jsx(t.strong,{children:"P/L %"}),", ",e.jsx(t.strong,{children:"P/L $"}),", and ",e.jsx(t.strong,{children:"Status"}),"."]}),`
`]}),`
`,e.jsx(t.p,{children:"These live fields update continuously during market hours, so you can leave the Tracker open and watch your bookmarked prints move in real time."}),`
`,e.jsxs(t.p,{children:[e.jsx(t.strong,{children:"On mobile"}),", the desktop split-view is replaced with a vertical card stack. Each card shows the same fields; you swipe between cards instead of scrolling a table."]}),`
`,e.jsx(t.h3,{children:"Whale Status and OI Drift"}),`
`,e.jsxs(t.p,{children:["The ",e.jsx(t.strong,{children:"Status"}),` pill on each tracked trade isn't just "up" or "down" — Flowseeker detects close events by watching the contract's volume and OI and reports where the original whale (the institution that took the position) appears to be:`]}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"STILL IN"})," — the trade is active, no close signal detected."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"PENDING"})," — a partial close is in progress."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"PARTIAL N%"})," — the position is N% closed out. The whale is unwinding."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"EXITED"})," — the position has been fully closed."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"EXPIRED"})," — the contract reached expiration while still open."]}),`
`]}),`
`,e.jsx(t.p,{children:"These transitions are detected automatically throughout the session — you don't have to watch for them. When a new close is detected, the Tracker badge on the sidebar increments, so you know to check even if the page isn't open."}),`
`,e.jsxs(t.p,{children:["A secondary ",e.jsx(t.strong,{children:"OI Drift"})," badge on each row shows how much open interest has moved on that specific strike since the bookmark — a fast visual of whether the position sizing is growing, shrinking, or holding."]}),`
`,e.jsx(t.h3,{children:"Removing a Trade"}),`
`,e.jsx(t.p,{children:"Hover a row on desktop, or scroll to the top-right of a card on mobile, and you'll see a trash icon. Click it to remove the trade from your tracker. The action is instant and not reversible — but since the trade itself is just a saved reference, you can always re-bookmark the same print from a historical day in the Live Feed if you change your mind."}),`
`,e.jsx(t.h2,{children:"The Chart Modal: The Shared Drill-Down"}),`
`,e.jsx(t.p,{children:"All three pages — Live Feed, Scanner, Tracker — open the same chart modal when you click into a specific trade. This is the deep-dive surface, and understanding its layout saves you a lot of navigation."}),`
`,e.jsx(t.h3,{children:"The Five Views"}),`
`,e.jsx(t.p,{children:"Every chart modal has five views:"}),`
`,e.jsxs(t.table,{children:[e.jsx(t.thead,{children:e.jsxs(t.tr,{children:[e.jsx(t.th,{children:"View"}),e.jsx(t.th,{children:"What It Shows"})]})}),e.jsxs(t.tbody,{children:[e.jsxs(t.tr,{children:[e.jsx(t.td,{children:e.jsx(t.strong,{children:"Contract Flow"})}),e.jsx(t.td,{children:"Stacked volume bars (no-side, bid, mid, ask) showing how aggressive the contract's intraday volume has been, with the contract's average fill price (VWAP) plotted on the right axis. Toggleable IV overlay and RVOL baseline."})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:e.jsx(t.strong,{children:"Underlying (Vol)"})}),e.jsx(t.td,{children:"Stock price history with options volume by bar."})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:e.jsx(t.strong,{children:"Underlying ($)"})}),e.jsx(t.td,{children:"Stock price history with options dollar premium by bar."})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:e.jsx(t.strong,{children:"Net Premium"})}),e.jsx(t.td,{children:"Cumulative net premium for that ticker over 1/2/5 day or longer intervals. This is where you read divergences between price and flow."})]}),e.jsxs(t.tr,{children:[e.jsx(t.td,{children:e.jsx(t.strong,{children:"Strike Distribution"})}),e.jsx(t.td,{children:"Bar chart of option activity by strike. 1D or 1W view. Clicking a strike opens a per-expiration breakdown."})]})]})]}),`
`,e.jsxs(t.p,{children:[e.jsx(t.strong,{children:"On desktop"}),", the modal is a split pane: ",e.jsx(t.strong,{children:"Contract Flow is always on the left"}),", and a dropdown at the top-right of the right panel lets you pick any of the other four views. This means you can look at the contract's own price chart and the ticker-level Net Premium trend side-by-side without switching tabs."]}),`
`,e.jsxs(t.p,{children:[e.jsx(t.strong,{children:"On mobile"}),", all five views are exposed as horizontal tabs — no split pane. Tap between them."]}),`
`,e.jsx(t.h3,{children:"The Footer"}),`
`,e.jsx(t.p,{children:"Below the charts, the footer has two tables you can switch between:"}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Flow Orders"})," — the list of individual trades that make up the candles you're viewing."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Vol / OI History"})," — a daily breakdown of volume and open interest for the contract, useful for seeing whether today's activity is outsized against recent history."]}),`
`]}),`
`,e.jsxs(t.p,{children:["When you select a candle on the Contract Flow chart, the ",e.jsx(t.strong,{children:"Expand Trades"})," button at the top of the footer becomes active. On the Live Feed, clicking it creates a new filtered feed tab (as mentioned earlier). On the Scanner and Tracker, the button is there but doesn't open a new tab — it's a live-feed-specific action. Use ",e.jsx(t.strong,{children:"Clear Selection"})," to reset the candle filter back to the full contract."]}),`
`,e.jsx(t.h3,{children:"Header Actions"}),`
`,e.jsx(t.p,{children:"The header of the modal has three controls:"}),`
`,e.jsxs(t.ul,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Refresh"})," — manually reload the chart data. Has a short cooldown so rapid clicks don't stack."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Share to Discord"})," — sends a PNG of the current chart (plus the trade context) to a configured Discord channel. Some users will see an upgrade prompt here instead; that's role-based."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Close (×)"})," — closes the modal. ",e.jsx(t.strong,{children:"Escape"})," also closes it."]}),`
`]}),`
`,e.jsx(t.h2,{children:"How the Three Pages Fit Together"}),`
`,e.jsx(t.p,{children:"A typical Flowseeker session uses all three pages in sequence:"}),`
`,e.jsxs(t.ol,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Open the Live Feed."})," Read the overview bar. Glance at the tape to understand the session's tone."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Set your filters."})," Pick a tab configured for what you're watching today — sweeps only, a specific sector, whatever matters."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Click interesting prints."})," Use the chart modal's Net Premium and Strike Distribution views to get context. Use Expand Trades on any candle that looks structurally interesting."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Bookmark what's worth following."})," Trades that passed your filters ",e.jsx(t.em,{children:"and"})," had clean structural context go into the Tracker. Trades that were interesting but didn't pan out stay in the Live Feed and scroll off."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Check the Tracker once an hour or so."})," See which of your bookmarked trades are still live, which have started closing out, and which the whale has already exited."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"At the end of the session, open the Scanner."})," Switch to today's date and ask contract-level questions — which contracts had the most premium, which strikes had the biggest OI growth, which contracts had aggressive ask-side execution all day. The Scanner rolls up what the tape showed as thousands of prints into one line per contract, so patterns that the live tape was too fast to see become obvious."]}),`
`]}),`
`,e.jsx(t.p,{children:"The Live Feed is for reactive tape reading. The Scanner is for contract-level review. The Tracker is for memory. Using them together is how you build a real flow-reading workflow, rather than just staring at the live tape and hoping something jumps out."}),`
`,e.jsx(t.h2,{children:"First Steps"}),`
`,e.jsxs(t.p,{children:["If you've just read the ",e.jsx(t.a,{href:"/learn/intro-to-flowseeker",children:"Introduction to Flowseeker"})," and this article, here's what to actually do when you open the terminal:"]}),`
`,e.jsxs(t.ol,{children:[`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Go to the Live Feed."})," Rename the default tab to something meaningful. Duplicate it once, rename the duplicate — you now have two tabs."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Set different filter configurations on each tab."})," Tab 1: broad view ($100K premium, Stocks only). Tab 2: narrow view ($250K premium, Sweeps Only, |Flow Score| > 50)."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Open the Columns panel."})," Hide columns you don't use and drag the ones you do to the left."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Try the ticker-scope search."})," Type ",e.jsx(t.code,{children:"!SPY"})," and press Enter to drop all SPY prints for the rest of the session. Toggle it back by removing the tag."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"Bookmark your first interesting trade."})," It's now in the Tracker. Check back in an hour."]}),`
`,e.jsxs(t.li,{children:[e.jsx(t.strong,{children:"After the close, switch to the Scanner."})," Pick today's date and sort contracts by premium. The top of the list is where the day's institutional activity concentrated — scan it for contracts with high OI change, aggressive ask-side skew, or sweep percentages above baseline."]}),`
`]}),`
`,e.jsx(t.p,{children:"Do that for a week and the four-page workflow starts to feel natural rather than fragmented."}),`
`,e.jsx(o,{product:"flowseeker",description:"Flowseeker is a real-time institutional options flow scanner built into the Skylit Terminal, with a live feed, a full-day screener, and a persistent tracker for following prints after the fact."}),`
`,e.jsxs(t.p,{children:["For the column-by-column breakdown of what you see in each row, see the ",e.jsx(t.a,{href:"/learn/intro-to-flowseeker",children:"Introduction to Flowseeker"}),". For the conceptual foundation of why options flow matters at all, start with the ",e.jsx(t.a,{href:"/learn/options-flow",children:"Options Flow Trading"})," guide. For understanding why dealer positioning at the strike level determines whether flow amplifies or gets absorbed, see the ",e.jsx(t.a,{href:"/learn/dealer-positioning",children:"Dealer Positioning"})," guide."]}),`
`,e.jsx(t.h2,{children:"Frequently Asked Questions"}),`
`,e.jsx(t.h3,{children:"What's the difference between the Live Feed and the Scanner?"}),`
`,e.jsxs(t.p,{children:["It's the ",e.jsx(t.strong,{children:"unit of analysis"}),". The Live Feed is a real-time tape where every row is a single print — trades appear as they happen and the feed keeps flowing. The Scanner is a contract-level view where every row is one contract (ticker + expiration + strike + C/P) with all of today's activity aggregated — total premium, total volume, bid/ask execution mix, sentiment scores, OI change, sweep percentage, and so on. Live Feed tells you ",e.jsx(t.em,{children:"what just happened"}),". Scanner tells you ",e.jsx(t.em,{children:"which contracts mattered today and how they traded as a whole"}),". They share the same underlying data and the same chart modal, but they answer different questions."]}),`
`,e.jsx(t.h3,{children:'What does "tracking" a trade actually do?'}),`
`,e.jsxs(t.p,{children:["Bookmarking a trade from the Live Feed saves the full print data to your account. The Tracker then keeps the ",e.jsx(t.strong,{children:"Mid"}),", ",e.jsx(t.strong,{children:"Spot"}),", ",e.jsx(t.strong,{children:"P/L %"}),", and ",e.jsx(t.strong,{children:"P/L $"})," fields updated throughout market hours, automatically watches for the whale exiting the position, and flags status transitions (STILL IN → PARTIAL → EXITED). Your tracked trades persist across sessions, so you can bookmark during one day and check back the next."]}),`
`,e.jsx(t.h3,{children:"What's the fastest workflow from seeing a print to following it?"}),`
`,e.jsx(t.p,{children:"Three clicks: bookmark the row in the Live Feed (or right-click → Track trade), then click the Tracker in the sidebar to see it alongside everything else you're watching. If you want the chart context first, click the row to open the chart modal, look at the Net Premium view to confirm it fits the session's flow, then close the modal and bookmark. Two or three extra seconds for a lot more certainty about what you're tracking."})]})}function c(n={}){const{wrapper:t}={...i(),...n.components};return t?e.jsx(t,{...n,children:e.jsx(s,{...n})}):s(n)}export{c as default};
