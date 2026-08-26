import{j as e}from"./index-Cv6VCl5d.js";import{u as t,C as r,P as a}from"./ArticlePage-BzhK0Axy.js";import"./ArticleTag-BCz4VRd4.js";function i(n){const s={em:"em",h2:"h2",h3:"h3",li:"li",p:"p",strong:"strong",table:"table",tbody:"tbody",td:"td",th:"th",thead:"thead",tr:"tr",ul:"ul",...t(),...n.components};return e.jsxs(e.Fragment,{children:[e.jsx(s.h2,{children:"What is Gamma Exposure?"}),`
`,e.jsxs(s.p,{children:[e.jsx(s.strong,{children:"Gamma (Γ)"})," measures the rate of change of delta per $1 move in the underlying. It controls whether the market mean-reverts or accelerates."]}),`
`,e.jsxs(s.p,{children:["When dealers are ",e.jsx(s.strong,{children:"long gamma (+GEX)"}),", shown as yellow Pika nodes on Heatseeker, their hedges oppose the market's move. They buy dips and sell rips. That creates stability and mean reversion."]}),`
`,e.jsxs(s.p,{children:["When dealers are ",e.jsx(s.strong,{children:"short gamma (–GEX)"}),", shown as purple Barney nodes on Heatseeker, their hedges chase the move. They sell dips and buy rips. That amplifies volatility."]}),`
`,e.jsx(r,{type:"analogy",children:e.jsx(s.p,{children:"Gamma is a car's suspension: smooth in calm conditions, but unstable on ice. In +GEX, the shocks absorb bumps. In –GEX, every bump throws you further off course."})}),`
`,e.jsx(s.h2,{children:"How GEX Affects Market Behavior"}),`
`,e.jsxs(s.table,{children:[e.jsx(s.thead,{children:e.jsxs(s.tr,{children:[e.jsx(s.th,{children:"Condition"}),e.jsx(s.th,{children:"Dealer Hedge"}),e.jsx(s.th,{children:"Market Behavior"})]})}),e.jsxs(s.tbody,{children:[e.jsxs(s.tr,{children:[e.jsx(s.td,{children:e.jsx(s.strong,{children:"+GEX (Long Γ)"})}),e.jsx(s.td,{children:"Buys dips, sells rips"}),e.jsx(s.td,{children:"Stability, mean reversion"})]}),e.jsxs(s.tr,{children:[e.jsx(s.td,{children:e.jsx(s.strong,{children:"–GEX (Short Γ)"})}),e.jsx(s.td,{children:"Sells dips, buys rips"}),e.jsx(s.td,{children:"Volatility amplification"})]})]})]}),`
`,e.jsxs(s.p,{children:[e.jsx(s.strong,{children:"Above/Below Spot:"})," +GEX below spot acts as support. +GEX above spot acts as resistance. Where GEX sign changes is where polarity flips, and where the most violent moves occur. The strongest +GEX node across the heatmap is called the ",e.jsx(s.strong,{children:"King Node"}),", it acts as the primary structural gravity center for price, where dealer stabilizing pressure is most concentrated."]}),`
`,e.jsx(s.h2,{children:"Vol Behavior and GEX"}),`
`,e.jsxs(s.p,{children:["Volatility rising amplifies –GEX effects. Volatility falling strengthens +GEX pins. GEX defines ",e.jsx(s.em,{children:"potential"}),". VIX defines ",e.jsx(s.em,{children:"reality"}),"."]}),`
`,e.jsx(r,{type:"idea",children:e.jsx(s.p,{children:"Each Greek is a dimension of risk the dealer must neutralize. When crowd exposure shifts, dealers rebalance. Their hedges feed back into price, volatility, and liquidity."})}),`
`,e.jsx(s.h2,{children:"Cross-Greek Mechanics"}),`
`,e.jsxs(s.ul,{children:[`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"If dealer is long delta → they sell stock"})," to neutralize; ",e.jsx(s.strong,{children:"short delta → they buy stock"}),"."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Long gamma (+GEX)"})," makes those buy/sell actions ",e.jsx(s.strong,{children:"contrarian"})," to price (stabilizing)."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"Short gamma (–GEX)"})," makes them ",e.jsx(s.strong,{children:"pro-cyclical"})," (amplifying)."]}),`
`]}),`
`,e.jsx(a,{product:"heatseeker",description:"Visualize live GEX levels across all strikes and expirations with Heatseeker's gamma exposure heatmaps."}),`
`,e.jsx(s.h2,{children:"Time and Tenor"}),`
`,e.jsxs(s.ul,{children:[`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"0DTE:"})," Gamma and Charm dominate. Vanna is near zero. Same-day pins and breaks rule intraday."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:"1–7 DTE:"})," Transition zone. Gamma is still large, but Vanna begins to matter."]}),`
`,e.jsxs(s.li,{children:[e.jsx(s.strong,{children:">30 DTE:"})," Vanna/Vega world. The IV path drives price drift via hedging."]}),`
`]}),`
`,e.jsxs(s.p,{children:["Gamma scales approximately as ",e.jsx(s.strong,{children:"1/√T"}),". Short-dated options have explosive gamma. Long-dated options have very little."]}),`
`,e.jsx(s.h2,{children:"Frequently Asked Questions"}),`
`,e.jsx(s.h3,{children:"What is gamma exposure (GEX)?"}),`
`,e.jsx(s.p,{children:"Gamma exposure measures the rate of change of delta per $1 move in the underlying asset. It determines whether market makers' hedging activity stabilizes or amplifies price moves. When you see a GEX reading on a heatmap, you're seeing how much mechanical buying or selling pressure dealers are obligated to apply as price moves through that level."}),`
`,e.jsx(s.h3,{children:"How does GEX affect stock prices?"}),`
`,e.jsx(s.p,{children:"Positive GEX means dealers are long gamma, so their hedges are contrarian: they buy dips and sell rips, which creates stability and mean reversion around those levels. Negative GEX flips that dynamic entirely. Dealers are short gamma, so their hedges chase the move by selling dips and buying rips, which amplifies volatility and accelerates trends."}),`
`,e.jsx(s.h3,{children:"What is the difference between positive and negative GEX?"}),`
`,e.jsx(s.p,{children:"Positive GEX nodes (shown as yellow Pika nodes on Heatseeker) represent strikes where dealer hedging is contrarian to price, producing mean-reversion behavior. Negative GEX nodes (shown as purple Barney nodes) represent strikes where dealer hedging is pro-cyclical, accelerating moves away from that level. The sign change between the two is where polarity flips and the most violent price moves tend to occur."}),`
`,e.jsx(s.h3,{children:"What is a King Node?"}),`
`,e.jsx(s.p,{children:"The King Node is the strike with the largest absolute GEX value across the entire heatmap. It acts as the primary structural gravity center for price, where dealer stabilizing pressure is most concentrated. Market makers are most likely to pin price near the King Node at close, making it one of the most actionable reference points in any GEX-based analysis."})]})}function d(n={}){const{wrapper:s}={...t(),...n.components};return s?e.jsx(s,{...n,children:e.jsx(i,{...n})}):i(n)}export{d as default};
