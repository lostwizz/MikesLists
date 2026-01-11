#!/usr/bin/env bash
##set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF="$BASE_DIR/logs.conf"

echo "[INFO] Starting multitail dashboard..."

# Read config
mapfile -t ENTRIES < <(grep -vE '^\s*$|^\s*#' "$CONF")
[[ ${#ENTRIES[@]} -gt 0 ]] || { echo "[ERROR] No entries in logs.conf"; exit 1; }

# Build multitail arguments
ARGS=()

for ENTRY in "${ENTRIES[@]}"; do
    TITLE="${ENTRY%%|*}"
    CMD="${ENTRY#*|}"
    # Wrap the command in a shell to handle the arguments correctly
    ARGS+=( "-t" "$TITLE" "-l" "sh -c $CMD" )
done

exec multitail -du -H 30 -Cs --mark-interval 60 "${ARGS[@]}"
