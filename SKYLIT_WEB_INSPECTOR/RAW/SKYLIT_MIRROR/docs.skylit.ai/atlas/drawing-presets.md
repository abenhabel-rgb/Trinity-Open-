> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Drawing Presets

> Save your drawing styles as named presets that sync across devices — Fibonacci level sets, line styles, and defaults for every new drawing.

Drawing presets let you save a drawing's full configuration under a name and reuse it anywhere. Set up your Fibonacci levels once — ratios, colors, fills, line style, extensions — save it as a preset, and every device signed into your Skylit account can apply it with one click.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/iHjUu2CNHfYLdhQi/images/atlas-drawing-presets-golden-pocket.png?fit=max&auto=format&n=iHjUu2CNHfYLdhQi&q=85&s=c8fe066e453fe3a33d82aba12201b763" alt="A Golden Pocket preset applied to a Fibonacci drawing, with fills extended right into developing price" width="1790" height="1376" data-path="images/atlas-drawing-presets-golden-pocket.png" />
</Frame>

Presets exist for two families of tools:

| Preset type | Tools covered                                                                      | What gets saved                                                                                                                                        |
| ----------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Fibonacci   | Fib retracement                                                                    | Level ratios, per-level colors and visibility, fills and fill opacity, line width and style, extensions, trend line, label options, log scale, reverse |
| Line style  | Trendline, rectangle, arrow, horizontal line, horizontal ray, vertical line, brush | Color, line width, line style, opacity                                                                                                                 |

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/iHjUu2CNHfYLdhQi/images/atlas-drawing-presets-panel.png?fit=max&auto=format&n=iHjUu2CNHfYLdhQi&q=85&s=c7489e0b50d83014bd6afbd751e81305" alt="The Fibonacci panel with the preset controls at the top" width="884" height="1046" data-path="images/atlas-drawing-presets-panel.png" />
</Frame>

## Where to find presets

Select any drawing on the chart and its style toolbar appears.

* **Fibonacci drawing selected** — the Fibonacci button on the toolbar shows the active preset's name next to the icon. Click it to open the Fibonacci panel; the preset controls sit at the top, above the level editor.
* **Line-style drawing selected** — the Line style button works the same way: it carries the active preset's name and opens a compact preset panel.

<Note>
  Presets are saved to your Skylit account — they belong to you, not to any single chart or layout, and follow you across every device you sign into.
</Note>

## The preset controls

| Control         | What it does                                                                                                                                                     |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Preset dropdown | Applies the chosen preset to the selected drawing and makes it your active preset. Choose **Built-in defaults** to reset the drawing to the stock configuration. |
| Save as…        | Saves the selected drawing's current configuration as a new named preset and makes it active.                                                                    |
| Update          | Overwrites the active preset with the drawing's current configuration. Enabled only when the drawing actually differs from the preset.                           |
| Star            | Marks the preset as the default for **all** new drawings — it takes priority over the active selection. Click again to unstar.                                   |
| Delete          | Removes the preset from your account.                                                                                                                            |

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/iHjUu2CNHfYLdhQi/images/atlas-drawing-presets-dropdown.png?fit=max&auto=format&n=iHjUu2CNHfYLdhQi&q=85&s=bfb19bc53c63162a05c0a0cf31c18859" alt="The preset dropdown with named presets and the starred default" width="1076" height="1034" data-path="images/atlas-drawing-presets-dropdown.png" />
</Frame>

## The unsaved-changes dot

When your selected drawing drifts from its preset — a level ratio edited, a different line width, an extension toggled — a dot appears next to the preset name on the toolbar button, and **Update** lights up in the panel.

<Frame>
  <img src="https://mintcdn.com/skylit-490c28ef/iHjUu2CNHfYLdhQi/images/atlas-drawing-presets-dirty.png?fit=max&auto=format&n=iHjUu2CNHfYLdhQi&q=85&s=39f7e9e41d5ef7b0f8b763706b459c9e" alt="A modified drawing: the dot next to the preset name and the enabled Update button signal unsaved changes" width="1096" height="1098" data-path="images/atlas-drawing-presets-dirty.png" />
</Frame>

* **Dot visible** — the drawing no longer matches the preset. Click **Update** to save the changes into the preset, or re-apply the preset from the dropdown to discard them.
* **No dot, Update disabled** — the drawing matches the preset exactly. Nothing to save.

<Tip>
  Update's disabled state doubles as a saved indicator: if you can't click it, your preset already reflects what's on the chart.
</Tip>

Edits never save into a preset automatically. Changing a drawing changes that drawing only — other drawings using the same preset keep their look, and the preset itself changes only when you click **Update**.

## Defaults for new drawings

Every new drawing starts from the first match in this order:

1. **Starred preset** — the preset you've marked with the **Star** control. It's your house-style default and always wins, so new drawings come out styled no matter what's selected in the dropdown.
2. **Active preset** — whatever is currently selected in the preset dropdown, used only when no preset is starred.
3. **Built-in defaults** — the stock configuration.

Star the preset you want as your house style and every new Fibonacci or line drawing comes out styled without any setup. The star stays in charge until you unstar it or delete the preset — selecting a different preset (or **Built-in defaults**) restyles the drawing you have selected, but doesn't change what new drawings start from.

## Applying a preset

Applying a preset makes the selected drawing match it exactly — every setting the preset covers is restored, including settings you changed since. Right after applying, the drawing is in sync with the preset and Update is disabled.

<Warning>
  Applying a preset restyles the selected drawing only. Drawings already on your charts keep their own configuration — select one and re-apply the preset if you want it updated too.
</Warning>

## A note on Fibonacci colors

Fibonacci drawings color each level individually — those per-level colors live in the preset. The general drawing color swatch does not apply to Fibonacci drawings, which is why the color picker is not shown on the toolbar while a Fibonacci drawing is selected. For line-style presets, color is part of the preset.

## Sync and limits

* Presets sync across all devices signed into the same Skylit account. A preset saved on desktop is available on mobile immediately.
* If the same account edits presets on two devices at once, the most recent save wins.
* Accounts can store up to 50 presets across both preset types.
