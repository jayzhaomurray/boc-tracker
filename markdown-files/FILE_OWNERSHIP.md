# Agent File Ownership — BoC Tracker

Defines exclusive file zones for parallel agent dispatch. Agents must not touch files outside their zone without explicit coordinator approval.

---

## Agent 1: Fetcher
**Owns:** fetch.py, analyze.py, data/*.csv, data/blurbs.json, data/*.json, requirements.txt, .github/workflows/update.yml

## Agent 2: Charter
**Owns:** build.py only
**Read access:** data/ (read-only inputs)

## Agent 3: Auditor
**Owns:** analyses/*.py, analyses/*.md, analyses/*.csv, analyses/*.png, analyses/*.html, markdown-files/verification/

## Agent 4: Doc Writer
**Owns:** markdown-files/HANDOFF.md, markdown-files/dashboard_purpose.md, markdown-files/chart_style_guide.md, markdown-files/analysis_framework.md, markdown-files/distribution_conventions.md, markdown-files/blurb_quality_log.md, markdown-files/archive/, reference/

## Agent 5: Deployer
**Owns:** .github/workflows/, .claude/settings.local.json, CLAUDE.md, .gitignore, README.md
**Read-only access:** All HTML outputs (index.html, *.html at root) — Deployer may run build.py to verify but does not own build.py

---

## Cross-cutting rules
- HTML root files (index.html, policy.html, etc.) are generated artifacts — no agent owns them exclusively; the Charter's build run is authoritative
- experiments/ is unowned; coordinate with user before touching
- No agent commits directly — stage changes and hand off to merge-review agent
