# CLAUDE.md — BoC Tracker

A real, in-use personal data dashboard tracking Bank of Canada indicators. Live at https://jayzhaomurray.github.io/boc-tracker/. Not a learning project — practitioner-level rigor expected.

## First moves in any session

Read these four documents in order before doing anything substantive. They are the source of truth.

1. **`markdown-files/HANDOFF.md`** — current state, file structure, ordered next-steps. Orient here.
2. **`markdown-files/chart_style_guide.md`** — formatting principles + workflow rules (§7 governs how to break or revise a principle).
3. **`markdown-files/analysis_framework.md`** — internal analytical brief for blurb generation. Per-section questions, signals, thresholds.
4. **`markdown-files/reading_guide.md`** — short reader-facing dashboard orientation.

**One-source-of-truth rule:** these docs reference each other rather than duplicate. If a fact lives in the style guide, HANDOFF should link to it not copy it. Drift between docs has been a real risk; treat it seriously.

## Workflow conventions

- **Discuss → plan → implement** for any non-trivial design choice. Don't jump straight to code. The user often says "let's discuss first" — they use chat as where they push back on framing or correct my premises before I commit.
- **Argue and recommend, don't menu options.** When facing a choice, write the analysis, weigh the candidates, name a recommendation. Use AskUserQuestion only for clarification I can't infer — not for "pick one of these." The user's decision rule: a strong recommendation is something to agree with or push back on; a menu shifts the decision burden back to them.
- **Skip plan mode for genuinely small changes.** Adding one toggleable line to an existing chart doesn't need the 5-step planning workflow. Plan mode is for design decisions, not implementation steps.
- **Concise commit messages.** 5–10 lines max for routine changes; long-form only for genuinely complex commits. (Past sessions have over-explained.)
- **Never silently break a principle, never silently rewrite one.** chart_style_guide.md §7 has the exception/revision protocol. Surface the case, propose either revising the principle (if it'll recur) or documenting an exception.

## Analytical bar

This is a **practitioner-level** tool. Default to the rigorous version of any read, not "good enough for an overview."
- When a metric is a proxy with known issues (e.g. 2Y yield embeds term premium when used as rate-expectations proxy), surface that and propose the cleaner alternative (OIS) — don't shrug it off.
- Don't omit a category of analysis just because the data is harder to fetch. Flag the cost; include it in scope.
- Use BoC's canonical numbers and framings (e.g. neutral rate band 2.25–3.25% from the Bank's annual r* update, not "the commonly cited ~2.5–3%").

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

## Model allocation

Default to **Opus** for the main thread (this is a high-judgment project; design discussions and analytical decisions need it).

Delegate to **Sonnet via the Agent tool** when the task is bounded and mechanical:
- Long file reads with summary requested
- Focused codebase searches
- Format-checking, sanity-checking outputs
- Use `model: "sonnet"` on the Agent tool call

Suggest a manual **`/model sonnet`** session-wide switch when entering a long pure-implementation phase where no design decisions remain (e.g. "design is locked; I'll implement these five steps"). User runs the switch.

**Haiku** for trivial fixes (single-line edits, typos) — same delegation pattern as Sonnet.

## Other context

- Memory files in `~/.claude/projects/C--Users-jayzh-Documents-boc-tracker/memory/` carry cross-session context (analytical bar, decision style, project state).
- Repo on GitHub at https://github.com/jayzhaomurray/boc-tracker; GitHub Actions cron runs the fetch + build pipeline on a schedule.
- All work goes on `main`. No feature branches needed for this project's scale.
