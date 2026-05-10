# BoC Tracker — Project Handoff

Current state of the project. Written so a fresh session can continue without any prior context.

---

## What this project is

A personal data dashboard that tracks the economic indicators the Bank of Canada watches between its quarterly Monetary Policy Reports (MPRs). The output is a single interactive HTML file hosted publicly on GitHub Pages.

**Live URL:** https://jayzhaomurray.github.io/boc-tracker/
**GitHub repo:** https://github.com/jayzhaomurray/boc-tracker
**Owner GitHub handle:** jayzhaomurray

**Tech stack:** Python → Plotly → static HTML → GitHub Pages
**Data sources:** Statistics Canada WDS API, Bank of Canada Valet API, Federal Reserve (FRED) API, Alberta Economic Dashboard API

**Long-term vision:** `vision.md` has been archived to `markdown-files/archive/` and is not a first-read doc for session startup.

---

## Open next steps

1. **Flesh out deep-dive pages** — most deep-dives have placeholder stubs. Per `analyses/deep-dive-design-2026-05-09.md` (43 charts, 9 judgment calls resolved). Start with Labour and GDP.

2. **Blurb iteration** — Inflation and Policy blurbs are user-iterated (Tier 3); Labour, Financial, GDP, Housing are autonomous-draft (Tier 1). Regen with `python analyze.py --section <id>` then iterate with the user on voice and framing.

3. **Tier 2 pending** — `units_under_construction.csv` (v52300170) — vector was inferred from magnitude; verify with `getSeriesInfoFromVector` before treating as authoritative.

4. **ECB/BoE/RBA rates** — FRED timed out 2026-05-09; retry pending. No code changes needed — just run `python fetch.py` with `FRED_API_KEY` set. The Peer Central Banks chart on `policy.html` currently shows BoC + Fed only.

5. **Framework and blurb work** — regenerate the four autonomous-draft blurbs (Labour, Financial, GDP, Housing); user iteration on voice and framing. Remaining open items: RBA two-sided labour methodology; BOS labour-shortage series probe (Valet `BOS_*`); real-wage benchmark prose extension in Labour Thresholds block.

6. **Wishlist charts** — Headline CPI + CPI ex-indirect-taxes overlay; Employment by sector reliant on US exports (LFS Table 14-10-0023); Goods exports excluding gold (Table 12-10-0011); BOS hiring intentions / pass-through.

---

## Current dashboard state

Live chart counts per page (updated 2026-05-10):

| Page | Live charts | Placeholder stubs |
|---|---|---|
| `index.html` (main dashboard) | 20 charts, 6 section headings, 6 blurbs | — |
| `policy.html` | 7 | 0 (complete per design doc) |
| `housing.html` | 6 | 0 |
| `labour.html` | 4 | 4 |
| `gdp.html` | 3 | 4 |
| `trade.html` | 2 | 3 |
| `demographics.html` | 1 | 4 |
| `inflation.html` | 1 | 4 |
| `financial.html` | 1 | 5 |

For the full PAGES definition (which specs each chart uses, derived series, etc.) see `markdown-files/ARCHITECTURE.md`.

---

## Parked / blocked

### WCS–WTI spread (Financial Conditions blurb)

**Status:** Placeholder only. Current WCS source (Alberta Economic Dashboard) is monthly and lagged; the live spread in `compute_external_values` mixes monthly-average WCS against a single daily WTI value — not directly comparable. Distribution thresholds in `distribution_conventions.md` were calibrated from monthly vs monthly (correct pairing), but the live compute is not that. Blurb prose is instructed to omit the spread until resolved.

**What would unblock it:** A free daily (or at least weekly) WCS series. Alberta Economic Dashboard is the only accessible free source and it publishes monthly. TMX / Refinitiv / Bloomberg carry daily differentials but are paid.

### Market-Implied Rate Path chart

**Status:** Investigated May 2026. Blocked on free programmatic access to Canadian implied-rate data.

**Goal:** Forward curve drawn as a dotted continuation of the historical BoC overnight rate, showing the market's expected policy rate at each future date.

**Why it's blocked:**
- BoC Valet has no OIS / swap / forward-rate series.
- TMX CRA (3-Month CORRA) futures are the right instrument but no public API exists.
- Yahoo Finance carries CME ZQ / SR3 but not CRA.
- CME DataMine, paid aggregators out of scope for a free personal dashboard.

**What was incorporated instead:** 2Y term-premium literature sharpened the framework. `analysis_framework.md` Monetary Policy now codifies BoC ACM-model term-premium magnitudes and regime distortions. The 2-Year Yields chart footnote carries the short version.

**Unblocks the chart:** paid feed (Bloomberg / Refinitiv / TMX Datalinx); BoC publishing a CORRA-OIS series via Valet; or a free aggregator emerging.

---

## Known issues

1. **`fed_funds` frequency mixing** — CSV is monthly pre-2009, daily post-2009. Step-function rendering on Policy Rates handles it visually. No problems in practice. Real gotcha if you try to chart it against a purely daily or purely monthly series.

2. **Vector ID label drift** — `cpi_services` was historically mislabelled (claimed table 18-10-0006-01; actually 18-10-0004-01); `cpi_all_items` was mislabelled NSA but is SA. Both fixed. **Always verify any new vector ID against cube metadata (`getSeriesInfoFromVector`) before adding it.**

3. **Hook `if` filter mis-firing** — `pre-commit-checkpoint.sh` fires the system-reminder on any Bash tool call, not just `git commit`-prefixed commands. The configured `if "Bash(git commit*)"` permission-rule filter isn't gating the hook as expected. Doesn't block work; adds noise.

4. **`analyze.py` auth-path resolution** — `call_claude()` resolves auth in this order: (1) `CLAUDE_AUTH_MODE=api` forces SDK path, requires `ANTHROPIC_API_KEY`; (2) `CLAUDE_AUTH_MODE=cli` forces CLI subprocess; (3) default: prefer `claude` CLI if on PATH, fall back to SDK if `ANTHROPIC_API_KEY` is set, otherwise raise. Locally, `python analyze.py --section <id>` works without any API key if `claude` is installed and authenticated.
