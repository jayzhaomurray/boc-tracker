#!/usr/bin/env bash
# Reset the edit-burst counter to zero.
# Fired on Agent dispatch (PreToolUse) and successful git commit (PostToolUse).

STATE_DIR="$(dirname "$0")/../state"
STATE_FILE="$STATE_DIR/edit-burst-counter"
mkdir -p "$STATE_DIR" 2>/dev/null
echo "0" > "$STATE_FILE"
exit 0
