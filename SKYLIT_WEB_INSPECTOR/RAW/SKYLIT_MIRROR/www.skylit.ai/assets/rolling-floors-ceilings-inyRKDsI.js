import{j as e}from"./index-Cv6VCl5d.js";import{u as t,C as r,A as a,P as o}from"./ArticlePage-BzhK0Axy.js";import"./ArticleTag-BCz4VRd4.js";function n(s){const i={a:"a",h2:"h2",h3:"h3",li:"li",p:"p",ul:"ul",...t(),...s.components};return e.jsxs(e.Fragment,{children:[e.jsx(i.h2,{children:"What Rolling Means"}),`
`,e.jsx(i.p,{children:"Floors and ceilings move. That's the core idea, and most traders miss it because they're looking at a single snapshot of the map instead of watching it across multiple updates."}),`
`,e.jsx(i.p,{children:"When the largest floor node migrates higher strike by strike across two or three consecutive map updates, the floor is rolling up. When the largest ceiling node migrates lower, the ceiling is rolling down. The range itself is shifting, not just price inside it."}),`
`,e.jsx(i.p,{children:"This matters because the structural opportunity set changes with it. A floor that was at 5400 yesterday at 5420 today and 5440 tomorrow is telling you something specific about where dealers are repositioning their hedges. The downside is shrinking. The upside of buying dips is improving. Not because price went up, but because the mechanical floor beneath spot keeps climbing."}),`
`,e.jsx(i.h2,{children:"Rolling Floor Up"}),`
`,e.jsx(i.p,{children:"A rolling floor up is a bullish structural condition. Each new floor forms higher than the last. Dealers are repositioning their hedges upward, which compresses the range from below."}),`
`,e.jsx(i.p,{children:"Here is what's happening mechanically. As price climbs and call positioning accumulates at higher strikes, dealers carry increasing long gamma at those strikes. Their hedging obligations shift upward with each roll in positioning. The structural support level that dealer activity creates climbs with it."}),`
`,e.jsx(i.p,{children:"The practical implication: fading dips becomes higher probability. The floor keeps rising. You're not fighting gravity when you buy weakness because the mechanical support itself is moving in your direction. Each new floor is a fresh node, untested, carrying maximum structural weight."}),`
`,e.jsx(i.p,{children:"Three things to watch for on a rolling floor:"}),`
`,e.jsxs(i.ul,{children:[`
`,e.jsx(i.li,{children:"The dominant floor node at the same time of day is 1-2 strikes higher today than yesterday"}),`
`,e.jsx(i.li,{children:"Adjacent nodes below the floor are weakening or disappearing as exposure migrates upward"}),`
`,e.jsx(i.li,{children:"The migration is gradual and consistent across updates, not a single-session spike"}),`
`]}),`
`,e.jsx(i.p,{children:"A single-session jump isn't rolling. Rolling is sustained repositioning across multiple updates. That distinction matters for how much weight you give it."}),`
`,e.jsx(r,{type:"idea",children:e.jsx(i.p,{children:"Rolling is gradual repositioning. A breakout is a sudden structural event. These are not the same thing and should not be traded the same way. Rolling reflects dealers systematically adjusting hedges as the underlying exposure profile shifts. A breakout reflects a sudden disruptive event in positioning that overwhelms the existing structure. Rolling floor up means the floor keeps working. A gamma breakout means the floor is gone."})}),`
`,e.jsx(i.h2,{children:"Rolling Ceiling Down"}),`
`,e.jsx(i.p,{children:"A rolling ceiling down is the bearish mirror. Each new ceiling forms lower than the last. Dealers are repositioning downward. The range compresses from above."}),`
`,e.jsx(i.p,{children:"Rallies into a rolling ceiling face progressively heavier resistance. The ceiling isn't a fixed level you can break once and clear. It descends. A rally that looked like it had room to run gets capped sooner than the map from three sessions ago would have suggested."}),`
`,e.jsx(i.p,{children:"This is persistent selling pressure built into the structure itself, not sentiment, not news flow. The mechanical ceiling keeps descending and dealer hedging activity reinforces it on every touch. Buying breakouts into a rolling ceiling is buying into a headwind that is actively getting stronger."}),`
`,e.jsx(i.p,{children:"What a rolling ceiling down looks like in practice:"}),`
`,e.jsxs(i.ul,{children:[`
`,e.jsx(i.li,{children:"The dominant ceiling node is at a lower strike today than yesterday and two days ago"}),`
`,e.jsx(i.li,{children:"Overhead nodes are growing as positioning shifts lower into the structure"}),`
`,e.jsx(i.li,{children:"The compression is confirmed when the distance between ceiling and spot narrows across multiple sessions"}),`
`]}),`
`,e.jsx(a,{type:"video"}),`
`,e.jsx(i.h2,{children:"What Rolling Means for Trade Bias"}),`
`,e.jsxs(i.p,{children:["Rolling floor up with ",e.jsx(i.a,{href:"/learn/gamma-regimes",children:"negative gamma below"})," is a strong trending environment. The floors keep climbing, which is itself bullish, but if price does break lower, negative gamma below the floor means that break accelerates. The combination creates asymmetry in both directions: dips are well-supported structurally, but the failure case is fast."]}),`
`,e.jsx(i.p,{children:"Rolling ceiling down with negative gamma above is persistent selling pressure. Rallies face a descending ceiling and mechanical dealer selling reinforces every rejection. Short positions gain structural support as the ceiling migrates lower."}),`
`,e.jsx(i.p,{children:"The cleaner your read on which type of rolling is occurring, the more clearly you can set directional bias for the session. Rolling floor up tilts toward buying structure. Rolling ceiling down tilts toward selling structure. Neither is a standalone signal, but both sharpen the probability distribution on the next meaningful price test."}),`
`,e.jsx(i.h2,{children:"Identifying Rolling in Real Time"}),`
`,e.jsx(i.p,{children:"The workflow is simple. Pull the last two to three map updates. Find the largest floor node and the largest ceiling node in each. Check whether either has migrated."}),`
`,e.jsx(i.p,{children:"Floor migration checklist:"}),`
`,e.jsxs(i.ul,{children:[`
`,e.jsx(i.li,{children:"Locate the single largest positive exposure node below spot in each update"}),`
`,e.jsx(i.li,{children:"Is that node at the same strike, a higher strike, or a lower strike compared to the prior update?"}),`
`,e.jsx(i.li,{children:"If it's migrating higher consistently, that's a rolling floor"}),`
`]}),`
`,e.jsx(i.p,{children:"Ceiling migration checklist:"}),`
`,e.jsxs(i.ul,{children:[`
`,e.jsx(i.li,{children:"Locate the single largest positive exposure node above spot in each update"}),`
`,e.jsx(i.li,{children:"Is it at the same strike, a lower strike, or a higher strike compared to the prior update?"}),`
`,e.jsx(i.li,{children:"If it's migrating lower consistently, that's a rolling ceiling"}),`
`]}),`
`,e.jsx(i.p,{children:"One migration across one update is noise. Two consecutive migrations in the same direction are signal. Three is confirmation."}),`
`,e.jsx(i.p,{children:"The speed of migration matters too. A floor that jumps two strikes in a single update is different from one that moves one strike per session over a week. The faster the migration, the more urgency there is in the dealer repositioning and the more aggressive the trading implication becomes."}),`
`,e.jsxs(i.h2,{children:["Rolling Floors and ",e.jsx(i.a,{href:"/learn/air-pockets-velocity",children:"Air Pockets"})]}),`
`,e.jsx(i.p,{children:"Rolling floors and ceilings interact with air pockets in a specific way. As the floor migrates up, it often leaves air pockets in its wake. The strikes the floor just vacated have lower structural significance than they did before the migration. If price retraces into those vacated strikes, there's less mechanical support there than the prior map would suggest."}),`
`,e.jsx(i.p,{children:"Recognizing this prevents a common error: using an old floor level as support after the floor has already rolled above it. The structure moves. The levels from two sessions ago are not necessarily the levels that matter today."}),`
`,e.jsxs(i.p,{children:["For context on how gamma regimes interact with rolling structure, see the ",e.jsx(i.a,{href:"/learn/gamma-regimes",children:"gamma regimes guide"}),". For how to read these shifts in the heatmap interface, see ",e.jsx(i.a,{href:"/learn/reading-heatseeker",children:"reading Heatseeker"}),"."]}),`
`,e.jsx(o,{product:"heatseeker",description:"Track rolling floors and ceilings across consecutive map updates, see exactly when the structural range is migrating and in which direction."}),`
`,e.jsx(i.h2,{children:"Frequently Asked Questions"}),`
`,e.jsx(i.h3,{children:"What does it mean when floors roll higher?"}),`
`,e.jsx(i.p,{children:"When floors roll higher, the dominant floor node is printing at successively higher strikes across multiple consecutive map updates. Dealers are repositioning their hedges upward as the market advances, which compresses the structural range from below. It's a bullish condition because each new floor is fresh, untested, and carrying maximum structural weight. The mechanical support itself is moving in your favor when you're buying dips, and prior ceilings become new floors as the range shifts up."}),`
`,e.jsx(i.h3,{children:"How do rolling ceilings signal a bearish trend?"}),`
`,e.jsx(i.p,{children:"A rolling ceiling down means the dominant ceiling node is printing at successively lower strikes across updates. Dealers are repositioning their hedges downward, and each new ceiling forms lower than the last. Rallies face progressively heavier resistance because the ceiling isn't a fixed level you can break and clear. It descends. Buying breakouts into a rolling ceiling means buying into a headwind that's actively getting stronger. Prior floors become overhead resistance as the structural range shifts lower."}),`
`,e.jsx(i.h3,{children:"What is the difference between rolling and a breakout?"}),`
`,e.jsx(i.p,{children:"Rolling is gradual, sustained repositioning across multiple map updates, reflecting dealers systematically adjusting hedges as the underlying exposure profile shifts. A breakout is a sudden structural event where a catalyst overwhelms existing structure. A rolling floor means the floor keeps working and the dip-buying thesis remains intact. A gamma breakout means the floor is gone entirely. These aren't the same thing and shouldn't be traded the same way. Rolling requires patience and bias in the direction of migration. A breakout requires recognizing the structural shift and not leaning on the old level."})]})}function d(s={}){const{wrapper:i}={...t(),...s.components};return i?e.jsx(i,{...s,children:e.jsx(n,{...s})}):n(s)}export{d as default};
