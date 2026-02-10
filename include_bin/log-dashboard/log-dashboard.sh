#!/bin/bash
# ==========================================
# log combiner
# __version__="2.2.3"
# ==========================================


set -euo pipefail


# Colors
CYAN=$'\033[36m'
GREEN=$'\033[32m'
YELLOW=$'\033[33m'
RED=$'\033[31m'
RESET=$'\033[0m'

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF="$BASE_DIR/logs.conf"

echo -e "${CYAN}Starting Log Dashboard...${RESET}"

# Read config (skip blank lines + comments)
mapfile -t ENTRIES < <(grep -vE '^\s*$|^\s*#' "$CONF")
[[ ${#ENTRIES[@]} -gt 0 ]] || { echo "[ERROR] No entries in logs.conf"; exit 1; }

# Build multitail arguments
ARGS=()

for ENTRY in "${ENTRIES[@]}"; do
    TITLE="${ENTRY%%|*}"
    CMD="${ENTRY#*|}"

    # Wrap the command in a shell to handle arguments correctly
    # ARGS+=( "-t" "$TITLE" "-l" "sh -c \"$CMD\"" )
    ARGS+=( "-t" "$TITLE" "-l" "sh -c '$CMD'" )
done

# Debug: uncomment to see the final command
# printf '%s\n' "${ARGS[@]}"

# exec multitail  -H 30 -Cs --mark-interval 300 -n 200 "${ARGS[@]}"
exec multitail -H 30 -Cs --mark-interval 300 -n 200 "${ARGS[@]}"
