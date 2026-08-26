> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Atlas

> Atlas brings Skylit data directly onto the chart so users can review price action, dealer positioning, dark pool levels, and options-flow context in one place.

Atlas brings charting directly into Skylit Terminal so users can review important market data without switching between separate tools.

Instead of comparing Heatseeker, Flowseeker, Dark Pool levels, and price action across multiple screens, Atlas brings relevant Skylit data directly onto the chart. The goal is to make the relationship between price, positioning, and platform signals easier to see in one place.

<Note>
  This page covers product guidance for Atlas: what the feature is, how the main settings work, and what users should understand before configuring it. The Atlas Academy module inside Skylit Terminal covers deeper applied walkthroughs and examples.
</Note>

## Atlas in the Skylit ecosystem

Atlas acts as a visual hub inside Skylit Terminal. As the platform evolved, Heatseeker, Flowseeker, Agenthub, and Nexus have been integrated directly into charts so users can review relevant data while price action is developing.

* **Heatseeker** helps identify dealer-positioning levels.
* **Dark Pool levels** help surface areas where large hidden activity may be present.
* **Flowseeker** helps show where options activity is coming in.
* **Price action** shows how the market is reacting in real time.

Atlas is designed to make these layers easier to inspect together, especially when users want a cleaner view of how Skylit data relates to the chart.

## Confluence on the chart

Atlas can display multiple independent data layers on the same chart. This makes it easier to see when several platform signals are appearing around a similar price area.

For public documentation, confluence should be understood as product visibility. Atlas helps users observe where Skylit data overlaps with chart levels. Academy content covers how users may apply that context in practice.

***

## Understanding expirations in Atlas

In Heatseeker, gamma exposure is organized by expiration. Each column on the heatmap represents a different contract expiration, such as the current expiration, next week, two weeks out, or later periods.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=4c4afeec981549711d023f3cc9f91eaf" alt="Image" width="3294" height="1896" data-path="images/image.png" />
</Frame>

Atlas can bring that same expiration logic directly onto the chart. The **Expiration** setting controls which expiration data is displayed through Atlas overlays.

***

### Why expiration selection matters

The same strike can look different depending on the expiration selected. A major node several expirations out may not be a major node for the current expiration.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-1.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=58835d71f73b698b10a0c6c2674d7425" alt="Image" width="3294" height="1896" data-path="images/image-1.png" />
</Frame>

Changing the expiration setting does not change the underlying data. It changes which expiration data is displayed on the chart.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-2.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=afcb02c6284ae098cccbf39877ef414d" alt="Image" width="3294" height="1896" data-path="images/image-2.png" />
</Frame>

### Common expiration concepts

| Concept             | What it means                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Current             | Displays data from the current expiration.                                                                               |
| Current + Next N    | Displays the current expiration plus a chosen number of upcoming expirations.                                            |
| Further expirations | Can reveal positioning that exists beyond the current contract period.                                                   |
| Display difference  | Atlas may look different as the selected expiration range changes because different expiration data is being visualized. |

<Tip>
  Match the displayed expiration range to the context you are trying to inspect. Atlas is changing the view of the data, not changing the data itself.
</Tip>

***

## Orbs overview

Orbs are visual chart overlays that represent Heatseeker node data inside Atlas. They help users see important levels from the heatmap directly on the chart.

Atlas currently includes three Orb-related display modes:

* **Orbs Classic**
* **Orbs V2**
* **Derived Orbs**, designed for futures-related overlays

***

## Orbs Classic

Orbs Classic provides a simpler visual design for displaying node strength.

* Brighter or more intense colors indicate higher-value nodes.
* Duller colors indicate smaller or less intense nodes.
* **Opacity** adjusts the maximum brightness or intensity of the Orbs.
* **Orb size** controls how large or small the Orbs appear on the chart.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-3.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=2c51d55de2b80543d66a24f4571e9277" alt="Image" width="1060" height="904" data-path="images/image-3.png" />
</Frame>

***

## Orbs V2 settings

Orbs V2 gives users more control over how Heatseeker nodes appear on the chart.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-4.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=664110969059edee9f313a58425b952b" alt="Image" width="1060" height="904" data-path="images/image-4.png" />
</Frame>

| Setting      | What it controls                                                                                                                                |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Orb Size     | Controls the overall size of the Orbs. Higher values make zones larger and more prominent; lower values create a smaller, cleaner appearance.   |
| Min Clamp    | Sets the minimum size an Orb can be. Higher values make smaller nodes easier to see; lower values allow weak nodes to stay subtle.              |
| Max Clamp    | Sets the maximum size an Orb can reach. Higher values make dominant nodes larger; lower values prevent large nodes from overwhelming the chart. |
| Min Opacity  | Controls how visible weaker nodes are. Higher values make all nodes easier to see; lower values fade weaker nodes into the background.          |
| Max Opacity  | Controls the visibility of major nodes. Higher values make strong nodes stand out more; lower values create a more uniform appearance.          |
| King Opacity | Controls the visibility of the single strongest node on the chart, known as the King Node.                                                      |

### Scroll as Replay

When **Scroll as Replay** is enabled, Orbs V2 only uses information that was available at the selected historical point in time as the user scrolls backward through the chart.

This helps users:

* Review how dealer positioning developed throughout the session.
* Study historical chart action without future data influencing the visualization.
* Create a more realistic replay experience when reviewing prior sessions.

***

## Derived Orbs

Some charts inside Atlas use derived exposure. This means the chart can borrow GEX or VEX levels from a related product.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-5.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=f78b8e5d60047492ab89232fa096ffed" alt="Image" width="1096" height="919" data-path="images/image-5.png" />
</Frame>

| Chart or product | Borrowed or related levels         |
| ---------------- | ---------------------------------- |
| ES               | Can borrow levels from SPXW / SPY. |
| NQ               | Can borrow levels from QQQ.        |
| SPY              | Levels can be seen on SPXW.        |
| SPXW             | Levels can be seen on SPY.         |

Derived Orbs allow users to see important dealer-positioning levels from the options market directly on futures or related instruments.

## Understanding the wiggle

Because ES, NQ, SPX, SPY, SPXW, and QQQ do not always move perfectly together, borrowed levels may shift slightly as the session develops. This small movement is referred to as the **wiggle**.

The wiggle does not mean the data is wrong. It means Atlas is adjusting borrowed levels so they remain aligned with live price movement instead of forcing them to stay frozen in one place.

What users should know:

* Derived levels may move slightly minute to minute. This is expected.
* Atlas adjusts derived levels to keep them synced with the live market.
* If a derived level briefly disappears, the source data may have temporarily dropped. Atlas may hide the level rather than display it in the wrong place.

<Note>
  Public Docs explain what derived levels are and why they may move. Atlas Academy covers applied walkthroughs for using these views in context.
</Note>

***

## Chart tools

Atlas includes additional chart tools that help users keep related context visible without leaving the chart workspace. These tools are designed to make the chart more informative while keeping the core price view in focus.

***

### Projections (Beta)

**Projections** are a beta Atlas feature that helps users visualize potential forward price-gravity zones directly on the chart.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/skylit-screenshot-1782572144524.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=5c3b5173057892f8b937b6af19fa2002" alt="Skylit Screenshot 1782572144524" width="2960" height="1276" data-path="images/skylit-screenshot-1782572144524.png" />
</Frame>

When enabled, projections display a forward-looking range based on the selected chart context. This gives users a rough visual view of where price gravity may develop over the chosen projection window.

Projections can show:

* A projected forward range on the chart.
* Possible upper and lower gravity zones.
* Estimated percentage levels around the current price area.
* A visual path for how price gravity may develop over the selected window.

Users can adjust the projection window from the chart controls. T**he available projection length depends on the active candlestick timeframe.** Shorter chart timeframes may support shorter projection windows, while higher timeframes may support longer projection views.

<Warning>
  Projections are currently in beta. They should be treated as contextual estimates, not guarantees, signals, or trade recommendations.
</Warning>

***

### Heatmap sidecar

The **Heatmap sidecar** brings Heatseeker-style positioning data directly beside the Atlas chart.

This allows users to keep dealer-positioning context visible while reviewing price action. The sidecar can show strike levels, expiration columns, exposure values, high-value nodes, and current price location relative to nearby levels.

Users can adjust the sidecar from the filter control. Common filters include the number of expirations shown, the number of nodes shown, the selected exposure type, and current versus expanded expiration views.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-6.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=ba76546586c8cf973e1846ed4f615a6e" alt="Image" width="1838" height="909" data-path="images/image-6.png" />
</Frame>

***

### Trinity sidecar

**Trinity** extends the heatmap sidecar by showing related market heatmaps together in one view.

Instead of reviewing each product separately, users can use Trinity to see broader cross-market positioning context from the Atlas workspace. Trinity may include related products such as SPX, SPY, and QQQ.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-7.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=2aefc01e2184beda39c66574d7a0d7e2" alt="Image" width="1838" height="909" data-path="images/image-7.png" />
</Frame>

<Note>
  Public Docs explain what Trinity displays and how it fits into the Atlas workspace. Deeper interpretation and trading application belongs in Academy.
</Note>

***

### Flowseeker in Atlas

Atlas can display **Flowseeker** activity directly on the chart.

When the Flow toggle is enabled, flow activity appears beneath the price chart so users can compare options-flow activity with chart movement. Users can click a flow bar to open more detail for the selected time range.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-8.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=688f3264ed154eb5e1d62a2c2e36507a" alt="Image" width="1838" height="909" data-path="images/image-8.png" />
</Frame>

### Flow Bucket

The **Flow Bucket** shows detailed Flowseeker data for a selected time window.

After clicking a flow bar, Atlas opens a bucket view with summary metrics and contract-level detail. Depending on the selected window, the Flow Bucket may include:

* Selected time range.
* Number of trades.
* Net flow.
* Calls and puts.
* Bucket put/call ratio.
* Day put/call ratio.
* Top contracts.
* Contract expiration and DTE.
* Contract premium or notional value.

Flow Bucket helps users inspect the flow behind a specific moment on the chart without leaving Atlas.

***

### Dark Pool levels

Atlas can display **Dark Pool levels** directly on the chart.

When enabled, Dark Pool levels may appear as horizontal levels with labels showing the associated price area and activity context. Users can toggle Dark Pool levels from the chart toolbar and configure them through the filter icon.

This gives users another layer of market structure to compare against price action, Heatseeker nodes, Flowseeker activity, and other Atlas overlays.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-9.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=81206bbf6c3106a747072f9027ee0ebc" alt="Image" width="1838" height="856" data-path="images/image-9.png" />
</Frame>

***

### Replay and backtesting

Atlas includes replay functionality for reviewing prior chart behavior.

Replay allows users to move through historical chart action and study how Atlas data appeared at the time. This can help users review prior price action, node behavior, flow activity, and chart overlays as they existed during a selected period.

<Note>
  Replay is designed for review and education. It should be used to understand how data changed over time, not to imply that future outcomes will repeat exactly.
</Note>

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-10.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=eb10acab1ba22031f014a3ad06afc06b" alt="Image" width="1838" height="856" data-path="images/image-10.png" />
</Frame>

***

### Exposure views

Atlas allows users to switch between different exposure views. These views control which exposure layer is displayed on the chart.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/j8H4JcIQ5dD5_6Jf/images/image-11.png?fit=max&auto=format&n=j8H4JcIQ5dD5_6Jf&q=85&s=81a3819d57ab999941d214863e655b77" alt="Image" width="1838" height="856" data-path="images/image-11.png" />
</Frame>

| View      | Description                                                                                                                  |
| --------- | ---------------------------------------------------------------------------------------------------------------------------- |
| GEX       | Displays gamma exposure context.                                                                                             |
| VEX       | Displays vanna exposure context.                                                                                             |
| GEX + VEX | Combines both exposure views into one chart context.                                                                         |
| Derived   | Uses related products to display derived exposure levels where supported. See [Derived Orbs](#derived-orbs) for more detail. |

Changing the exposure view changes what layer of positioning data Atlas displays. It does not change the underlying price chart.

***

## Chart layouts

Atlas supports **named chart layouts** so users can save complete chart workspaces and switch between them instantly.

Each layout saves the full state of the Atlas workspace:

* The pane arrangement (single chart, side-by-side, stacked, quad, and other multi-chart grids).
* Each pane's symbol, timeframe, candle style, and overlay settings.
* Which Atlas layers are enabled — Orbs, Projections, Flow, Dark Pool levels, the Heatmap and Trinity side panels, and other toggles.
* Chart preferences such as timezone and session view.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/FrAOx_6nK8kwKXDk/images/atlas-layout-switcher.png?fit=max&auto=format&n=FrAOx_6nK8kwKXDk&q=85&s=224f349eeac25e6cf0794d9d4d231aca" alt="Layout switcher open in the Atlas chart header" width="1228" height="1084" data-path="images/atlas-layout-switcher.png" />
</Frame>

The layout switcher appears in the chart header next to the arrangement picker, and inside the chart settings panel. From the switcher, users can:

| Action          | How                                                                                       |
| --------------- | ----------------------------------------------------------------------------------------- |
| Switch layouts  | Click a layout in the list, or press `[` and `]` to cycle to the previous or next layout. |
| Create a layout | **New layout from current** saves the current workspace as a new layout.                  |
| Rename a layout | Click the pencil icon (or double-click the name), edit, and confirm.                      |
| Delete a layout | Click delete, then confirm. Deleting is a two-step action to prevent accidents.           |

There is no Save button. Changes to the active layout — a symbol, a timeframe, a toggle, an arrangement — are saved automatically a moment after they happen.

Layouts are stored with the user's Skylit account, so the same layouts are available across devices. A layout edited on one device updates on the others.

<Tip>
  Keep separate layouts for separate routines — for example an index multi-chart for the open, a single-chart flow view for midday review — and move between them with `[` and `]`.
</Tip>

On mobile, layouts that use desktop-only arrangements are hidden from the switcher and remain available on desktop.

## Continue learning

For deeper applied education, use the Atlas Academy module inside Skylit Terminal. Academy is where Skylit teaches practical application, while public Docs remain focused on product guidance, settings, and best practices.
