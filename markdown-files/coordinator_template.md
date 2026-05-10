# Coordinator Prompt Template

Use this template to dispatch a parallel agent fleet for boc-tracker. Fill in the TASK LIST section, then paste as a prompt.

---

## Instructions to coordinator (Claude main thread)

You are coordinating a parallel agent fleet for boc-tracker at `C:\Users\jayzh\Documents\boc-tracker`. The current branch is `{{BRANCH}}`.

Consult `markdown-files/FILE_OWNERSHIP.md` for the authoritative zone map. Assign each task below to the agent whose zone covers the required files. If a task spans zones, split it or flag it for sequential handling.

**Rules:**
- Dispatch all non-conflicting agents simultaneously in a single message
- Each agent must edit files only within its zone
- No agent commits — they stage or just edit; merge-review agent handles the commit
- Pass each agent its zone's file list explicitly so it doesn't stray

## Task List (fill in before dispatching)

| # | Task description | Zone | Agent |
|---|---|---|---|
| 1 | {{TASK_1}} | {{ZONE}} | Fetcher / Charter / Auditor / Doc Writer / Deployer |
| 2 | {{TASK_2}} | {{ZONE}} | |
| 3 | {{TASK_3}} | {{ZONE}} | |
| 4 | {{TASK_4}} | {{ZONE}} | |

## Per-agent prompt scaffold

> You are the **{{AGENT_NAME}}** agent for boc-tracker.
> Repo: `C:\Users\jayzh\Documents\boc-tracker`, branch: `{{BRANCH}}`
> **Your exclusive file zone:** {{FILE_LIST}}
> **Do not edit files outside your zone.**
> **Do not commit. Make your edits and report what you changed.**
>
> Task: {{TASK_DESCRIPTION}}
>
> On completion, report: files changed, lines added/removed, and any cross-zone dependencies the merge-review agent should know about.

## After all agents complete

Run the merge-review agent using the prompt in `merge_review_prompt.md`.
