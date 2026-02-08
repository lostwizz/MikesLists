#!/usr/bin/env bash
# ==========================================
# version_watcher.sh
#
# __version__ = "0.1.0.000014-dev"
#
# __author__ = "Mike Merrett"
# __updated__ = "2026-02-08 01:14:42"
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
# sudo journalctl --unit=gunicorn-MikesLists-test.service --vacuum-time=1s

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
    local line
    line=$(grep "$VERSION_KEY" "$file" | head -n 1)
    echo "$line" | sed -E 's/.*__version__[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/'
}

bump_version() {
    local version="$1"
    echo "$version" | awk -F. '
        BEGIN {OFS="."}
        {
            prefix = $1 "." $2 "." $3;
            split($4, suffix_parts, "-");
            build_num = suffix_parts[1] + 1;
            label = (suffix_parts[2] != "") ? "-" suffix_parts[2] : "";
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

    # Update Version and Timestamp
    sed -i -E "s|([#[:space:]]*${VERSION_KEY}[[:space:]]*=[[:space:]]*\")$from_v\"|\1$to_v\"|" "$file"
    sed -i -E "s|([#[:space:]]*__updated__[[:space:]]*=[[:space:]]*\")[^\"]*\"|\1$current_ts\"|" "$file"

    log "INFO" "File Updated: $file"
    log "INFO" "   Version:   [$from_v] -> [$to_v]"
    log "INFO" "------------------------------------------------"
}

process_file() {
    local file="$1"
    # Use a per-file lock based on the path hash to prevent global blocking
    local lock_file="/tmp/bump_$(echo "$file" | md5sum | awk '{print $1}').lock"

    [[ ! -f "$file" || ! -r "$file" ]] && return 0
    has_allowed_extension "$file" || return 1

    # Check for Lock: If the lock file exists and is less than 2 seconds old, skip
    if [[ -f "$lock_file" ]]; then
        local now=$(date +%s)
        local mtime=$(stat -c %Y "$lock_file")
        if (( now - mtime < 2 )); then
            debug "Lock active for $file. Skipping."
            return 0
        fi
    fi

    if ! grep -q "$VERSION_KEY" "$file" 2>/dev/null; then
        return 0
    fi

    local from_v to_v
    from_v=$(extract_version "$file") || return 0
    to_v=$(bump_version "$from_v")

    [[ "$from_v" == "$to_v" ]] && return 0

    # Refresh lock and update
    touch "$lock_file"
    update_version_in_file "$file" "$from_v" "$to_v"
}

########################################
# Execution
########################################

if [[ -n "$TEST_FILE" ]]; then
    log "INFO" "Running in TEST mode on file: $TEST_FILE"
    process_file "$TEST_FILE"
    exit 0
fi

touch "$LOG_FILE" 2>/dev/null || {
    echo "ERROR: Cannot write to log file: $LOG_FILE" >&2
    exit 1
}

log "INFO" "Starting version watcher (DRY_RUN=$DRY_RUN, DEBUG=$DEBUG)"

# Listen for close_write (file saved) and moved_to (atomic saves used by editors)
# Removed 'attrib' as it triggers too many redundant events during sed/touch
stdbuf -oL inotifywait -m -r \
    -e close_write -e moved_to \
    --format '%w %f' \
    --exclude '(\.tmp$|~$|\.swp$|\.swx$|\.git/)' \
    "${WATCH_DIRS[@]}" 2>>"$LOG_FILE" | while read -r W_DIR W_FILE; do

    FULL_PATH="${W_DIR}${W_FILE}"
    [[ "$FULL_PATH" == "$LOG_FILE" ]] && continue

    # Background the process with a tiny delay to ensure editor atomic-renames finish
    (
        sleep 0.2
        process_file "$FULL_PATH"
    ) &
done
