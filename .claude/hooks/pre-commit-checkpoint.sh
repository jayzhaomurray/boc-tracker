#!/usr/bin/env bash
# Pre-commit model-fit checkpoint.
# Fired on PreToolUse Bash matching `git commit *`.
# Injects a reminder: was this commit's work Opus-grade or Sonnet-able?

cat <<EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"PRE-COMMIT CHECKPOINT: Before this commit lands, briefly assess the work batch and pick a model for the NEXT similar batch. (a) OPUS-grade: design decisions, judgment calls, multi-axial reasoning, blurb voice iteration, judgment-heavy code review. (b) SONNET-able: multi-step mechanical work with established patterns, applying a locked-in design, framework prose updates, multi-file convention sweeps, HANDOFF passes. (c) HAIKU-able: bounded one-shots - single factual lookup, single citation fix, single percentile computation, vector-ID verification, single-file mechanical edit. If the next batch fits (b) or (c), DISPATCH it - don't continue on the main thread. Continue with this commit; this is for the next batch."}}
EOF
exit 0
