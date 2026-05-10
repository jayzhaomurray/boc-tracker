---
name: chart
description: Build a new chart for boc-tracker from a natural language description. Follows a fixed workflow: 2-question popup → description → approve/modify popup → build + verify. Use whenever the user says "chart X", "add a chart for X", or "I want a chart showing X".
tools: Read, Glob, Grep, Edit, Write, Bash, PowerShell, AskUserQuestion, Agent
---

# Chart Builder

Build a chart from a natural language description using the standard 4-step workflow below. Do not skip steps or reorder them.

---

## Step 1: Orient

Before asking anything, read:
- `build.py` — understand the PAGES structure, existing specs on each deep-dive page, placeholder sections, and available dataclasses (ChartSpec, MultiLineSpec, NativeChartSpec)
- `fetch.py` — understand STATSCAN_SERIES, BOC_VALET_SERIES, FRED_SERIES and which series are already fetched
- `data/` — check which CSVs already exist
- `markdown-files/HANDOFF.md` — understand current state of each deep-dive page

---

## Step 2: 2-question popup

Identify the **2 decisions where your assumption could be wrong and the user would care**. These are chart-specific — not a fixed list. Typical candidates:

- Page placement (when the topic spans two sections, e.g. productivity could be GDP or Labour)
- Transformation (level vs % YoY change vs index — when "growth" is ambiguous)
- Primary data source (when multiple series exist with different methodology, e.g. LFS wages vs SEPH earnings)
- Comparison series (standalone vs alongside another indicator)

**Do NOT ask about:** colors, smoothing, y-axis range, date range (default: max available), chart title (derive from intent), chart type (default: line for time series).

Fire a single `AskUserQuestion` popup with exactly 2 questions. 2–3 options per question.

---

## Step 3: Description

Write a two-part description. Do not proceed to the approve popup until this is shown.

**Part 1 — paragraph:** What the chart looks like. Which page, what story it tells, display choices. Keep to 3–4 sentences. Include smoothing decision with reasoning (see smoothing heuristic below).

**Part 2 — Series block:**
```
**Series:**
- [Role]: [description], [frequency] [SA/NSA] — [Source: StatsCan vXXXXX | BoC Valet series_key | FRED series_id] (`csv_name.csv`)
- [Note: any methodological caveat worth flagging]
```

If a required series isn't in fetch.py yet, note: "will fetch from [source]" with the vector/series ID.

---

## Step 4: Approve/modify popup

Fire an `AskUserQuestion` popup:
- **Looks good, build it**
- **Change something** *(with a notes field)*

If "Change something": incorporate the change into your plan. Re-show the description only if the change is major (different data source, different transformation). Then proceed to build.

---

## Step 5: Build

Execute in order:

1. **Fetch if needed:** If a required CSV doesn't exist, add the series to the appropriate dict in `fetch.py` (STATSCAN_SERIES / BOC_VALET_SERIES / FRED_SERIES), then run `python fetch.py`.

2. **Add chart spec:** Add the ChartSpec or MultiLineSpec to `build.py` PAGES in the correct deep-dive page section. Follow existing spec patterns exactly. Scale values if needed (e.g. trade C$M → C$B: use `_add_derived_series` pattern or scale_factor).

3. **Build:** Run `python build.py`.

4. **Verify:** Check the output HTML:
   - Build exited clean (exit code 0)
   - Chart section/heading is present in the page
   - CSV last date is within 6 months of today
   - Values are in a plausible range (catches unit errors: unemployment should be 0–30, not 0–0.3; trade balance in C$B not C$M)

5. **If verification fails:** Fix the issue and rebuild. Max 3 iterations. If still failing after 3, report what's blocking.

---

## Step 6: Report

Tell the user:
- What was built and on which page
- Iterations needed and what was fixed (if any)
- How to view it: `python build.py` then open the page

**Also flag:** build.py was edited, so HANDOFF.md needs an update per the trip-wire rule. Run `/handoff` or note it for the next commit.

---

## Smoothing heuristic

Load the primary series CSV. Compute coefficient of variation (std / mean) on the value column, ignoring NaNs.
- CV > 0.3: apply 12-month MA (or 4-quarter MA for quarterly). Toggle raw line off by default.
- CV ≤ 0.3: show raw. No smoothing needed.

State the choice and CV in the description paragraph.

---

## Data source preference order

When multiple series could serve the chart:
1. StatsCan SA series (primary source)
2. StatsCan NSA series (with MA applied)
3. BoC Valet series
4. Derived series (computed from existing CSVs)
5. FRED (last resort for non-Canadian context series)
