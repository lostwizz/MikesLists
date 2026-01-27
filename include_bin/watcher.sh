#!/usr/bin/env bash
# ==========================================
# version_watcher.sh
#
# __version__ = "0.1.0.000010-dev"
#
# __author__ = "Mike Merrett"
# __updated__ = "2026-01-26 21:23:51"
# __created__ = "2026-01-02 19:49:31"
# __description__ = "Auto version bump watcher"
# ==========================================

set -euo pipefail



# Reload the system: sudo systemctl daemon-reload
# Enable it to start at boot: sudo systemctl enable watcher.service
# sudo systemctl start watcher.service
# Start it now: sudo systemctl start watcher.service

# Check status: sudo systemctl status watcher.service
# View logs: If it’s not working, check the output with journalctl -u watcher.service -f
#    to see the complete log use   --- journalctl -u watcher.service

# Stop it: sudo systemctl stop watcher.service


# sudo systemctl daemon-reload
# sudo systemctl restart  watcher.service
# tail 500 -f /var/log/version_watcher.log


########################################
# Configuration
########################################


WATCH_DIRS=(
    "/srv/django/MikesLists_dev/"
    "/srv/django/MikesLists_test/"
    "/srv/django/MikesLists_live/"
    "/home/pi/bin"
)

LOG_FILE="/var/log/version_watcher.log"

# File filters: only consider these extensions
ALLOWED_EXTENSIONS=("sh" "py" "service" "conf")

# Pattern for version line (flexible spacing, double quotes)
VERSION_KEY="__version__"

########################################
# Runtime options
########################################

DRY_RUN=false
TEST_FILE=""
FOREGROUND=false
DEBUG=false

usage() {
    cat <<EOF
Usage: $(basename "$0") [options]

Options:
  --dry-run           Show what would be changed, but don't modify files.
  --test PATH         Run once on a single file and exit.
  --foreground        Run in foreground (no daemon-like behavior).
  --debug             Verbose logging to stdout.
  -h, --help          Show this help.

Typical systemd usage:
  systemctl start version-watcher.service
EOF
}

log() {
    local level="$1"; shift
    local msg="$*"
    local ts
    ts="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$ts] [$level] $msg" >> "$LOG_FILE"
    if $FOREGROUND || $DEBUG; then
        echo "[$ts] [$level] $msg"
    fi
}

debug() {
    $DEBUG && log "DEBUG" "$*"
}

########################################
# CLI parsing
########################################

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --test)
            TEST_FILE="${2:-}"
            if [[ -z "$TEST_FILE" ]]; then
                echo "Error: --test requires a path." >&2
                exit 1
            fi
            shift 2
            ;;
        --foreground)
            FOREGROUND=true
            shift
            ;;
        --debug)
            DEBUG=true
            FOREGROUND=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
done

########################################
# Helpers
########################################

has_allowed_extension() {
    local file="$1"
    local ext="${file##*.}"

    for allowed in "${ALLOWED_EXTENSIONS[@]}"; do
        if [[ "$ext" == "$allowed" ]]; then
            return 0
        fi
    done
    return 1
}


extract_version() {
    local file="$1"
    # Find the line, even if it's commented out
    local line
    line=$(grep "$VERSION_KEY" "$file" | head -n 1)

    # Extract just the version string between the quotes
    echo "$line" | sed -E 's/.*__version__[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/'
}


bump_version() {
    local version="$1"

    # Input format example: 0.1.0.000006-dev
    # This AWK handles:
    # 1. Splitting by '.'
    # 2. Taking the last segment and splitting by '-'
    # 3. Incrementing and padding with leading zeros
    echo "$version" | awk -F. '
        BEGIN {OFS="."}
        {
            # Store the prefix (e.g., 0.1.0)
            prefix = $1 "." $2 "." $3;

            # Grab the 4th segment (e.g., 000006-dev)
            split($4, suffix_parts, "-");

            # Increment the numeric part
            build_num = suffix_parts[1] + 1;

            # Preserve the text suffix (dev) if it exists
            label = (suffix_parts[2] != "") ? "-" suffix_parts[2] : "";

            # Reconstruct with 6-digit padding
            printf "%s.%06d%s\n", prefix, build_num, label;
        }
    '
}
update_version_in_file() {
    local file="$1"
    local from_v="$2"
    local to_v="$3"
    local current_ts
    current_ts=$(date '+%Y-%m-%d %H:%M:%S')

    if $DRY_RUN; then
        log "INFO" "[DRY-RUN] $file: Version $from_v -> $to_v"
        return 0
    fi

    # 1. Update Version
    # Removed the ^ anchor and added support for optional leading # and spaces
    # This matches both: __version__ = "..." AND # __version__ = "..."
    sed -i -E "s|([#[:space:]]*${VERSION_KEY}[[:space:]]*=[[:space:]]*\")$from_v\"|\1$to_v\"|" "$file"

    # 2. Update Timestamp
    sed -i -E "s|([#[:space:]]*__updated__[[:space:]]*=[[:space:]]*\")[^\"]*\"|\1$current_ts\"|" "$file"

    log "INFO" "File Updated: $file"
    log "INFO" "   Version:   [$from_v] -> [$to_v]"
    log "INFO" "------------------------------------------------"
}



process_file() {
    local file="$1"
    local lock_file="/tmp/bump_$(echo "$file" | md5sum | awk '{print $1}').lock"

    # 1. Basic Filters
    [[ ! -f "$file" || ! -r "$file" ]] && return 0
    has_allowed_extension "$file" || return 0

    # 2. Check for Lock (The Loop Killer)
    if [[ -f "$lock_file" ]]; then
        debug "Lock exists for $file. Skipping to prevent loop."
        return 0
    fi

    # 3. Check for Version Key
    if ! grep -q "$VERSION_KEY" "$file" 2>/dev/null; then
        return 0
    fi

    # 4. Extract and Bump
    local from_v to_v
    from_v=$(extract_version "$file") || return 0
    to_v=$(bump_version "$from_v")

    [[ "$from_v" == "$to_v" ]] && return 0

    # 5. Create Lock, Update File, then remove Lock after a delay
    touch "$lock_file"

    update_version_in_file "$file" "$from_v" "$to_v"

    # Remove lock after 1 second to allow future legitimate saves
    (sleep 1 && rm -f "$lock_file") &
}


########################################
# Test mode (one-shot on a single file)
########################################

if [[ -n "$TEST_FILE" ]]; then
    log "INFO" "Running in TEST mode on file: $TEST_FILE (DRY_RUN=$DRY_RUN)"
    process_file "$TEST_FILE"
    exit 0
fi

########################################
# Watch mode
########################################

# Ensure log file exists and is writable
touch "$LOG_FILE" 2>/dev/null || {
    echo "ERROR: Cannot write to log file: $LOG_FILE" >&2
    exit 1
}

log "INFO" "Starting version watcher (DRY_RUN=$DRY_RUN, DEBUG=$DEBUG)"

# Build inotifywait arguments
# We add -e attrib to catch metadata changes (like touch)
# We add -e close_write and -e moved_to to catch all editor types
INOTIFY_ARGS=(
    -m -r
    -e close_write -e moved_to -e attrib
    --format '%w %f'
    --exclude '(\.tmp$|~$|\.swp$|\.swx$|\.git/)'
)

log "INFO" "Watching directories..."

# Main watch loop
# We use two variables (dir and file) to ensure the path is joined correctly
stdbuf -oL inotifywait "${INOTIFY_ARGS[@]}" "${WATCH_DIRS[@]}" 2>>"$LOG_FILE" \
| while read -r W_DIR W_FILE; do
    FULL_PATH="${W_DIR}${W_FILE}"

    # Safety: Ignore the log file
    [[ "$FULL_PATH" == "$LOG_FILE" ]] && continue

# Check if we recently processed this file (simple 1-second gate)
    # This prevents the "sed" write from re-triggering the script
    if [[ -f "/tmp/last_bump" ]]; then
        last_time=$(cat /tmp/last_bump)
        now=$(date +%s)
        if [[ $((now - last_time)) -lt 1 ]]; then
             continue
        fi
    fi
    date +%s > /tmp/last_bump
    # ----------------------
    # Debug: log EVERY event to see if inotify is even firing
    # Uncomment the next line if you still see nothing
    # log "DEBUG" "Event detected on: $FULL_PATH"

    process_file "$FULL_PATH"
done
