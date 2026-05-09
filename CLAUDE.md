# CLAUDE.md — BoC Tracker

A real, in-use personal data dashboard tracking Bank of Canada indicators. Live at https://jayzhaomurray.github.io/boc-tracker/. Not a learning project — practitioner-level rigor expected.

## First moves in any session

Read these documents in order before doing anything substantive. They are the source of truth.

1. **`markdown-files/dashboard_purpose.md`** — what the dashboard exists to answer. Six sub-questions across six sections. Every chart and blurb earns its place against this filter.
2. **`markdown-files/HANDOFF.md`** — current state, file structure, ordered next-steps. Orient here.
3. **`markdown-files/chart_style_guide.md`** — formatting principles + workflow rules (§8 governs how to break or revise a principle).
4. **`markdown-files/analysis_framework.md`** — internal analytical brief for blurb generation. Per-section questions, signals, thresholds.

**Escape hatch:** for genuinely trivial edits — typo fix, single comment edit, single color tweak, one-line text change — skip the canonical reading. Anything that touches logic, data, analytical framing, or chart structure still earns the full first-moves pass.

**One-source-of-truth rule:** these docs reference each other rather than duplicate. If a fact lives in the style guide, HANDOFF should link to it not copy it. Drift between docs has been a real risk; treat it seriously.

## Workflow conventions

- **Discuss → plan → implement** for any non-trivial design choice. Don't jump straight to code. The user often says "let's discuss first" — they use chat as where they push back on framing or correct my premises before I commit.
- **Skip plan mode for genuinely small changes.** Adding one toggleable line to an existing chart doesn't need the 5-step planning workflow. Plan mode is for design decisions, not implementation steps.
- **Concise commit messages.** 5–10 lines max for routine changes; long-form only for genuinely complex commits. (Past sessions have over-explained.)
- **Never silently break a principle, never silently rewrite one.** chart_style_guide.md §8 has the exception/revision protocol. Surface the case, propose either revising the principle (if it'll recur) or documenting an exception.
- **Keep HANDOFF.md current as part of the same commit that changes reality.** Don't let the doc drift. Triggers:
  - Adding/removing a chart, adding a data series, renaming a section: update HANDOFF's "Current PAGES definition" and/or the data series table.
  - Completing a Next Steps item or verifying a framework section: cross it off / move it.
  - Architectural changes (new spec class, new pipeline step, new helper): document in HANDOFF's architecture section.
  - Tiny commits (typo, single-color tweak, comment fix) don't need HANDOFF updates.
  - Level of detail: enough that a fresh session reading HANDOFF understands current state, not a per-commit changelog.
  - Model: routine HANDOFF updates (table row, marking a todo done, adding a sub-bullet) run fine on Sonnet via subagent — delegate it after the main code commit. Major restructuring (re-prioritising the entire Next Steps list, rewriting an architecture section because the architecture changed) needs Opus on the main thread.
  - Same applies to the other canonical docs when the change touches their domain: chart_style_guide.md when introducing a new chart treatment pattern; analysis_framework.md when adding a new section signal.

## Analytical bar

Concrete project anchors (the practitioner-level expectation is in memory):
- Use BoC's canonical numbers and framings (e.g. neutral rate band 2.25–3.25% from the Bank's annual r* update, not "the commonly cited ~2.5–3%").
- When a metric is a proxy with known issues (e.g. 2Y yield embeds term premium when used as rate-expectations proxy), surface the cleaner alternative (OIS).

## Common operations

- **Add a chart:** edit `PAGES` in `build.py`. Most chart types are reusable spec dataclasses (ChartSpec, MultiLineSpec, CpiSpec, WageSpec, CoreInflationSpec, CpiBreadthSpec).
- **Add a data series:** edit `STATSCAN_SERIES`, `BOC_VALET_SERIES`, or `FRED_SERIES` in `fetch.py`. BoC Valet entries support an optional 3-tuple `(series_key, start_date, scale_factor)` for unit conversion.
- **Add a section blurb:** add a `compute_<section>_values` + `format_<section>_values` to `analyze.py` and register in `SECTIONS`. Pipeline: `analyze.py` → `data/blurbs.json` → `build.py` injection.
- **Run tests:** `python build.py` (offline; verifies HTML builds clean) and `python fetch.py` (network; refreshes data).
- **One-off research scripts:** put in `analyses/` with descriptive names. Read from `data/`, write outputs into the same folder. Not run by the pipeline.

## What NOT to do

- Don't add optional fields to spec dataclasses for every per-chart variation. Restructure rather than crowd.
- Don't speculate when verification with data is possible. The framework's "verification, not speculation" rule is enforced.
- Don't generalize from a single chart's behavior; verify against multiple charts before codifying.
- Don't write probe scripts at the project root — gitignored as `probe_*.py`. New probes go in `analyses/`.
- Don't write CSVs that aren't part of the pipeline into `data/`. That folder is the build's source of truth.

## Model allocation — project-specific examples

(Dispatch criteria and motivation are in global memory `workflow_dispatch_default.md`. This section just lists the project-specific shapes those criteria typically map to.)

**Dispatch on Haiku** for bounded one-shot tasks: BoC Valet / StatsCan vector ID lookups; "verify these vector IDs return SUCCESS"; specific file lookups; HTML verification ("confirm the new chart's traces are present and report counts").

**Dispatch on Sonnet** for context-handling tasks: multi-file searches with summary; reading several markdown docs and summarizing what each says about a topic; multi-step API exploration with intermediate decisions; mechanical code edits with some judgment ("add a new line to PAGES following the existing pattern"); HANDOFF.md refresh passes; the experiments harness was built by a Sonnet sub-agent.

**Keep on Opus main thread** for: blurb generation in `analyze.py`; `analysis_framework.md` / `chart_style_guide.md` / `dashboard_purpose.md` writing; judgment-heavy code review; design decisions; single Edit / Read / Grep where dispatch overhead exceeds the work itself.

**Session-level switch:** when entering a long pure-implementation phase with no design decisions remaining, suggest the user run `/model sonnet` for the whole session. Switch back to Opus before the next design discussion.

## Other context

- Memory files in `~/.claude/projects/C--Users-jayzh-Documents-boc-tracker/memory/` carry cross-session context (analytical bar, decision style, project state).
- Repo on GitHub at https://github.com/jayzhaomurray/boc-tracker; GitHub Actions cron runs the fetch + build pipeline on a schedule.
- All work goes on `main`. No feature branches needed for this project's scale.
