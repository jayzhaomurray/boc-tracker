#!/usr/bin/env bash
# Increment the edit-burst counter on each Edit/Write call.
# When the count crosses 4, inject a reminder via additionalContext.
# Counter is reset by edit-burst-reset.sh (Agent dispatch or post-commit).

STATE_DIR="$(dirname "$0")/../state"
STATE_FILE="$STATE_DIR/edit-burst-counter"
mkdir -p "$STATE_DIR" 2>/dev/null

count=0
if [ -f "$STATE_FILE" ]; then
  count=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
fi
count=$((count + 1))
echo "$count" > "$STATE_FILE"

if [ "$count" -ge 4 ]; then
  cat <<EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"EDIT-BURST: ${count} consecutive Edit/Write calls without Agent dispatch or commit. This is the over-Opus pattern. Pick a model for the rest: SONNET for multi-step work with established patterns (sweeps, framework updates, HANDOFF passes); HAIKU for bounded one-shots (single citation fix, single threshold value, single mechanical patch). DISPATCH instead of continuing on main thread."}}
EOF
fi

exit 0
