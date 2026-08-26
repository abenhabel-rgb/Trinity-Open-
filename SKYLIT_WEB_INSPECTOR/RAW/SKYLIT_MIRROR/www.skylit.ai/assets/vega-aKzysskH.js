import{j as e}from"./index-Cv6VCl5d.js";import{u as a,C as s,P as r}from"./ArticlePage-BzhK0Axy.js";import"./ArticleTag-BCz4VRd4.js";function i(t){const n={a:"a",h2:"h2",h3:"h3",li:"li",p:"p",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",ul:"ul",...a(),...t.components};return e.jsxs(e.Fragment,{children:[e.jsx(n.h2,{children:"What is Vega?"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Vega (ν)"})," measures the sensitivity of an option's price to a one-point change in implied volatility (IV). It's one of the core ",e.jsx(n.a,{href:"/learn/options-greeks",children:"options greeks"})," and sits at the heart of how options premiums expand and contract around events, fear cycles, and calm regimes."]}),`
`,e.jsx(n.p,{children:"When implied volatility rises, option premiums expand. Long vega positions benefit. When implied volatility falls, premiums contract. Short vega positions benefit. Every option has vega, but its magnitude depends heavily on time to expiry and moneyness."}),`
`,e.jsx(s,{type:"analogy",children:e.jsx(n.p,{children:"Vega is the market's breathing. When fear enters, the market inhales, implied volatility rises and premiums inflate. When calm returns, the market exhales, IV compresses and premiums deflate. Trading vega is trading the breath itself, not the direction."})}),`
`,e.jsx(n.h2,{children:"How Vega Works"}),`
`,e.jsxs(n.table,{children:[e.jsx(n.thead,{children:e.jsxs(n.tr,{children:[e.jsx(n.th,{children:"Role"}),e.jsx(n.th,{children:"Behavior"})]})}),e.jsxs(n.tbody,{children:[e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Dealer"})}),e.jsx(n.td,{children:"Usually short vol; hedges exposure by trading options against inventory"})]}),e.jsxs(n.tr,{children:[e.jsx(n.td,{children:e.jsx(n.strong,{children:"Player (retail/fund)"})}),e.jsx(n.td,{children:"Buys vol in fear, sells vol in calm"})]})]})]}),`
`,e.jsx(n.p,{children:"Dealers who sell options to meet demand accumulate short vega. As IV rises, their books lose value, so they must hedge by buying volatility. Players do the opposite, leaning into fear by purchasing protection or speculative calls, adding to long vega exposure across the market."}),`
`,e.jsxs(n.p,{children:["This structural dynamic means that ",e.jsx(n.strong,{children:"vol regime changes often feed themselves"}),": a spike in fear pushes IV higher, forcing dealer hedging that can amplify the move further."]}),`
`,e.jsx(n.h2,{children:"Key Properties of Vega"}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Vega is highest at-the-money (ATM)."})," An ATM option has the greatest uncertainty about where it will land at expiry, so its price is most sensitive to changes in the market's implied volatility estimate."]}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Vega scales approximately with √T."})," Long-dated options carry large vega; short-dated options carry very little. A 90-day option might have ten times the vega sensitivity of a 1-week option at the same strike. At 0DTE, vega is effectively zero. There's no time left for volatility to matter in dollar terms."]}),`
`,e.jsxs(n.p,{children:[e.jsx(n.strong,{children:"Time decay reduces dollar vega."})," As expiry approaches, even if IV stays constant, the absolute dollar sensitivity of the option to vol changes shrinks. Vega risk bleeds away over time for held positions."]}),`
`,e.jsx(s,{type:"idea",children:e.jsx(n.p,{children:"IV crush after an earnings event is pure vega mechanics. Before the event, implied volatility inflates as market participants pay up for protection or speculation. The moment results are announced, uncertainty resolves and IV collapses, even if the stock moves significantly. Long options holders lose on vega faster than they gain on delta."})}),`
`,e.jsx(n.h2,{children:"Vega and Cross-Greek Interactions"}),`
`,e.jsx(n.p,{children:"Vega feeds two important second-order greeks:"}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:e.jsx(n.a,{href:"/learn/vanna-exposure",children:"Vanna"})}),", the sensitivity of delta to changes in IV (∂Δ/∂σ). When vega is large and IV moves, vanna governs how dealer delta hedges need to be adjusted. This drives vanna flows during vol spikes."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:e.jsx(n.a,{href:"/learn/vomma",children:"Vomma"})}),", the sensitivity of vega itself to changes in IV (∂ν/∂σ). High vomma means a position's vega exposure accelerates as IV rises, making it particularly powerful in vol expansion regimes."]}),`
`]}),`
`,e.jsx(n.p,{children:"Understanding these interactions is what separates surface-level options analysis from genuine structural edge."}),`
`,e.jsx(n.h2,{children:"Event Runs and IV Crush"}),`
`,e.jsx(n.p,{children:"Vega governs the lifecycle of event trades:"}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Pre-event:"})," Market participants buy options ahead of earnings, macro data, or Fed decisions. IV rises, lifting all premiums regardless of direction."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"Post-event:"})," Uncertainty resolves. IV collapses rapidly, a phenomenon known as ",e.jsx(n.strong,{children:"IV crush"}),". Long options positions that were right on direction can still lose money if the vega loss outweighs the delta gain."]}),`
`]}),`
`,e.jsx(n.p,{children:"That's why experienced traders distinguish between buying premium ahead of events versus selling it. The direction trade is separate from the volatility trade."}),`
`,e.jsx(n.h2,{children:"Vega Across Tenors"}),`
`,e.jsxs(n.ul,{children:[`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"0DTE:"})," Vega is near zero. Delta and gamma dominate intraday."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"1–7 DTE:"})," Transition zone. Small but non-trivial vega; IV events can still move premiums meaningfully."]}),`
`,e.jsxs(n.li,{children:[e.jsx(n.strong,{children:"30+ DTE:"})," Vega world. The IV path, not just spot price, determines whether a position is profitable."]}),`
`]}),`
`,e.jsx(n.p,{children:"Long-dated options are fundamentally vol instruments. Short-dated options become increasingly directional as expiry nears."}),`
`,e.jsx(r,{product:"heatseeker",description:"Track how implied volatility shifts affect dealer positioning across strikes with Heatseeker."}),`
`,e.jsx(n.h2,{children:"Summary"}),`
`,e.jsxs(n.p,{children:["Vega measures how much an option's price changes for each one-point move in implied volatility. It's highest at-the-money, scales with the square root of time to expiry, and drives the premium expansion and contraction traders experience around events. Long vega benefits from vol rises; short vega benefits from vol crush. Vega also feeds ",e.jsx(n.a,{href:"/learn/vanna-exposure",children:"vanna"})," and ",e.jsx(n.a,{href:"/learn/vomma",children:"vomma"}),", making it central to understanding how dealer hedging flows propagate through the market during volatility regime changes."]}),`
`,e.jsx(n.h2,{children:"Frequently Asked Questions"}),`
`,e.jsx(n.h3,{children:"What is vega in options?"}),`
`,e.jsx(n.p,{children:"Vega measures the sensitivity of an option's price to a one-point change in implied volatility. When implied volatility rises, option premiums expand and long vega positions gain value. When implied volatility falls, premiums contract and short vega positions benefit. It's the greek that captures the market's fear or complacency, not its direction."}),`
`,e.jsx(n.h3,{children:"How does implied volatility affect options prices?"}),`
`,e.jsx(n.p,{children:"Implied volatility is the market's expectation of future movement embedded in an option's price. When fear enters the market, IV rises and all option premiums inflate regardless of direction. When calm returns, IV compresses and premiums deflate. This is why a trader who was right on direction can still lose money after an earnings event: the vega loss from IV crush can outweigh the delta gain from the stock's actual move."}),`
`,e.jsx(n.h3,{children:"What happens to vega near expiration?"}),`
`,e.jsx(n.p,{children:"Vega decays toward zero as expiration approaches. A 90-day option can have ten times the vega sensitivity of a 1-week option at the same strike, and at 0DTE vega is effectively zero. Short-dated options are increasingly driven by delta and gamma, not volatility. Long-dated options are fundamentally vol instruments where the IV path matters as much as the direction of spot price."})]})}function d(t={}){const{wrapper:n}={...a(),...t.components};return n?e.jsx(n,{...t,children:e.jsx(i,{...t})}):i(t)}export{d as default};
