# BoC Tracker — Project Handoff

Current state of the project. Written so a fresh session can continue without any prior context.

---

## What this project is

A personal data dashboard tracking Bank of Canada indicators between MPRs. Output: a single interactive HTML file on GitHub Pages.

**Live URL:** https://jayzhaomurray.github.io/boc-tracker/
**GitHub repo:** https://github.com/jayzhaomurray/boc-tracker
**Tech stack:** Python → Plotly → static HTML → GitHub Pages
**Data sources:** Statistics Canada WDS API, Bank of Canada Valet API, FRED, Alberta Economic Dashboard API

---

## Open next steps

1. **Flesh out deep-dive pages** — most deep-dives have placeholder stubs. Per `analyses/deep-dive-design-2026-05-09.md` (43 charts, 9 judgment calls resolved). Start with Labour and GDP.

2. **Blurb iteration** — Inflation and Policy blurbs are user-iterated (Tier 3); Labour, Financial, GDP, Housing are autonomous-draft (Tier 1). Regen with `python analyze.py --section <id>` then iterate with user on voice and framing. Remaining sub-items: RBA two-sided labour methodology; BOS labour-shortage series probe (Valet `BOS_*`); real-wage benchmark prose in Labour Thresholds block.

3. **Tier 2 pending** — `units_under_construction.csv` (v52300170) — vector inferred from magnitude; verify with `getSeriesInfoFromVector` before treating as authoritative.

4. **BoE/RBA rates** — FRED series `IRSTCB01GBM156N` (BoE) and `IRSTCB01AUM156N` (RBA) return HTTP 400 "series does not exist" as of 2026-05-10; CSVs missing. These series IDs are likely discontinued or renamed. Peer Central Banks chart currently shows BoC + Fed + ECB only until replacement IDs are found.

5. **Wishlist charts** — Headline CPI + CPI ex-indirect-taxes overlay; Employment by sector reliant on US exports (LFS Table 14-10-0023); Goods exports excluding gold (Table 12-10-0011); BOS hiring intentions / pass-through.

---

## Current dashboard state

Live chart counts per page (updated 2026-05-10):

| Page | Live charts | Placeholder stubs | Notes |
|---|---|---|---|
| `index.html` (main dashboard) | 5 charts, no sections, 6 blurbs | — | |
| `policy.html` | 5 | 0 | Order: Peer Central Banks, BoC Assets (5 lines), BoC Liabilities (5 lines), CORRA (spread default), Real Policy Rate (1 line). GoC Yield Curve + 2Y–10Y Spread moved to financial.html (2026-05-10). |
| `housing.html` | 9 | 0 | |
| `labour.html` | 5 | 4 | |
| `gdp.html` | 5 | 4 | |
| `trade.html` | 2 | 3 | |
| `demographics.html` | 1 | 4 | |
| `inflation.html` | 5 | 4 | |
| `financial.html` | 7 | 3 | Charts 5–6 (0-indexed): GoC Yield Curve, 2Y–10Y Spread (moved from policy.html 2026-05-10). |

For the full PAGES definition (spec dataclasses, series table, API docs) see `markdown-files/ARCHITECTURE.md`.

**Fleet skill:** `/fleet` skill at `~/.claude/skills/fleet/SKILL.md` replaces the deleted `FILE_OWNERSHIP.md` / `coordinator_template.md` / `merge_review_prompt.md`. Generates zone map fresh each run.

---

## Parked / blocked

**WCS-WTI spread** — Alberta API is monthly/lagged; daily WCS not available free. Blurb prose omits the spread until resolved.

**Market-Implied Rate Path** — no free programmatic access to Canadian OIS/CORRA-swap forward curve. BoC Valet has no OIS series; TMX CRA futures have no public API. Unblocks on paid feed or BoC publishing a CORRA-OIS Valet series.

---

## Known issues

1. **`fed_funds` frequency mixing** — monthly pre-2009, daily post-2009. Step rendering handles it visually; gotcha if charted against a purely daily/monthly series.
2. **Vector ID label drift** — always verify new vector IDs with `getSeriesInfoFromVector`; past mislabels caught on `cpi_services` and `cpi_all_items`.
3. **Hook `if` filter mis-firing** — `pre-commit-checkpoint.sh` fires on any Bash tool call, not just `git commit`. Adds noise; doesn't block work.
4. **`analyze.py` auth-path resolution** — default: prefer `claude` CLI if on PATH, fall back to SDK if `ANTHROPIC_API_KEY` is set. Override with `CLAUDE_AUTH_MODE=api|cli`. Local `python analyze.py --section <id>` works without an API key if `claude` is authenticated.
