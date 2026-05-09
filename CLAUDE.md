# CLAUDE.md — BoC Tracker

A real, in-use personal data dashboard tracking Bank of Canada indicators. Live at https://jayzhaomurray.github.io/boc-tracker/. Not a learning project — practitioner-level rigor expected.

## First moves in any session

Read these four documents in order before doing anything substantive. They are the source of truth.

1. **`markdown-files/HANDOFF.md`** — current state, file structure, ordered next-steps. Orient here.
2. **`markdown-files/chart_style_guide.md`** — formatting principles + workflow rules (§8 governs how to break or revise a principle).
3. **`markdown-files/analysis_framework.md`** — internal analytical brief for blurb generation. Per-section questions, signals, thresholds.
4. **`markdown-files/reading_guide.md`** — short reader-facing dashboard orientation.

**One-source-of-truth rule:** these docs reference each other rather than duplicate. If a fact lives in the style guide, HANDOFF should link to it not copy it. Drift between docs has been a real risk; treat it seriously.

## Workflow conventions

- **Discuss → plan → implement** for any non-trivial design choice. Don't jump straight to code. The user often says "let's discuss first" — they use chat as where they push back on framing or correct my premises before I commit.
- **Three surfaces, three uses.** When I have basis to recommend, write the analysis in prose, weigh candidates, name a recommendation; the user agrees or pushes back. When the user genuinely needs to choose between paths and proceeding the wrong way means rework, use AskUserQuestion so the decision is visible — not buried in prose. When it's a conversational follow-up ("want me to commit?", "move on?"), plain text is fine. Avoid menus when I could argue. Avoid burying action-blocking decisions in prose.
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
  - Same applies to the other canonical docs when the change touches their domain: chart_style_guide.md when introducing a new chart treatment pattern; analysis_framework.md when adding a new section signal; reading_guide.md when a section's chart contents change.

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

## Model allocation — proactive subagent delegation

This project's main thread runs on Opus by default (design + analytical work needs it). To save the user wait time, **proactively delegate bounded mechanical tasks to faster subagents** rather than doing them on the main thread. Do this without asking when the criteria below are met.

### Delegate when ALL of these are true

- The task has a clear input and clear output (you can describe it in 2 sentences)
- The task does NOT need to integrate with the in-flight conversation as it runs
- The task would take more than ~30 seconds of work on the main thread (multiple file reads, multi-step API queries, multi-file searches)

### Use Haiku (`model: "haiku"`) for bounded one-shot tasks

- Multi-step API queries: "Find the right BoC Valet series ID matching X criteria"
- Sanity checks: "Run this Bash command and report whether the value is in range Y–Z"
- Specific file lookups: "Read file X and report whether Y appears"
- HTML verification: "Verify the new chart's traces are present in index.html and report counts"

### Use Sonnet (`model: "sonnet"`) for tasks requiring some context-handling

- Multi-file codebase searches with summary
- Reading several markdown docs and summarizing what each says about a topic
- Multi-step API exploration with intermediate decisions
- Format / structural verification across a built artifact
- Mechanical code edits with some judgment (e.g. "add a new line to PAGES following the existing pattern")

### Keep on the main Opus thread

Don't delegate when the overhead would be slower than just doing it inline:
- Single Edit calls (faster on the main thread than spinning up a subagent)
- Single Read of a file you'll continue to reference
- Single Grep for a known pattern in known files
- Git commit + push (sequential, fast, depends on just-completed work)
- Anything that's part of an ongoing design discussion or analytical reasoning

### Session-level model switch (manual)

When entering a long pure-implementation phase where no design decisions remain (e.g. "design is locked; I'll implement these five steps"), suggest the user run `/model sonnet` for the whole session. The user runs the switch. Switch back to Opus before the next design discussion.

**Opus stays on the main thread** for: blurb generation (analyze.py), framework / style-guide writing, judgment-heavy code review, design decisions. These are the places where Opus quality genuinely shows.

## Other context

- Memory files in `~/.claude/projects/C--Users-jayzh-Documents-boc-tracker/memory/` carry cross-session context (analytical bar, decision style, project state).
- Repo on GitHub at https://github.com/jayzhaomurray/boc-tracker; GitHub Actions cron runs the fetch + build pipeline on a schedule.
- All work goes on `main`. No feature branches needed for this project's scale.
