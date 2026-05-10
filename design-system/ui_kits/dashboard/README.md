# BoC Tracker — Dashboard UI Kit

A high-fidelity recreation of the BoC Tracker splash and deep-dive surfaces using the design system in this project.

## Files
- `index.html` — splash page: masthead, status read, 5 KPI tiles, policy-rate chart, CPI components chart, deep-dive index.
- `inflation.html` — sample deep-dive page for the Inflation section.
- `components.jsx` — shared components: `Masthead`, `Eyebrow`, `FoilRule`, `FoilDot`, `StatusPill`, `TierTag`, `KPITile`, `ChartCard`, `ToolbarPills`, `LegendChips`, `Footer`.
- `policy-chart.jsx` — overnight rate vs. neutral band, with editorial Fed funds reference line. SVG, no deps.
- `cpi-chart.jsx` — multi-series CPI components chart with 2% target reference. SVG, no deps.
- `sparkline.jsx` — KPI-tile spark with anchor dot.

## Conventions
- All charts are hand-rolled SVG against the system's CSS variables — they reskin instantly when `data-theme="vault"` is applied to an ancestor.
- The 2% inflation target is always shown as a dotted reference, never as a solid line (per the chart style guide).
- The neutral-band fill uses `var(--band-fill)` so light/dark modes stay readable.
- Numerals everywhere use `font-variant-numeric: tabular-nums` (applied globally to `.mono` and `[data-num]`).
- Deltas show direction with `↑` / `↓` plus colour; magnitudes always carry units (`pp`, `bp`, `%`).

## What's faked
This is a UI kit, not the live site. Series are stylised representations of real BoC/StatsCan/FRED data shapes — they're shaped to tell the right macro story at a glance but are not the live numbers. Drop real values into the same series arrays to ship.
