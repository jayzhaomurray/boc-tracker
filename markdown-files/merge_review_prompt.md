# Merge-Review Agent Prompt

Paste this after all parallel agents have completed their edits.

---

You are the merge-review agent for boc-tracker. Parallel agents have just finished editing files on branch `{{BRANCH}}` at `C:\Users\jayzh\Documents\boc-tracker`.

**Your job:**
1. Run `git diff --stat` to see all unstaged changes
2. Run `git diff` (full) and read every changed file
3. Check for conflicts or unintended overlaps between agent edits
4. Verify each change is consistent with CLAUDE.md conventions and the chart_style_guide.md
5. Run `python build.py` and confirm it exits 0 with no errors
6. If build passes: stage all changes and produce a single commit message summarising what each agent did (one bullet per agent)
7. If build fails: identify which agent's change broke it, report the error, do NOT commit

**Commit message format:**
```
Parallel fleet: {{one-line summary}}

- Charter: {{what changed in build.py}}
- Doc Writer: {{what changed in HANDOFF.md}}
- Auditor: {{what the audit found / any files changed}}
- Deployer: {{deploy check result}}
```

**Report back:** files committed, any conflicts found, build exit code, and whether any cross-zone issue requires user attention.
