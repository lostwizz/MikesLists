#!/usr/bin/env bash
# ==========================================
# version_watcher.sh
#
# __version__ = "0.1.0.000006-dev"
#
# __author__ = "Mike Merrett"
# __updated__ = "2026-01-02 19:49:31"
# __created__ = "2026-01-02 19:49:31"
# __description__ = "Auto version bump watcher"
# ==========================================

set -euo pipefail




# Reload the system: sudo systemctl daemon-reload
# Enable it to start at boot: sudo systemctl enable version-bumper.service
# sudo systemctl start version-bumper.service
# Start it now: sudo systemctl start version-bumper.service

# Check status: sudo systemctl status version-bumper.service
# View logs: If it’s not working, check the output with journalctl -u version-bumper.service -f
#    to see the complete log use   --- journalctl -u version-bumper.service

# Stop it: sudo systemctl stop version-bumper.service


########################################
# Configuration
########################################

WATCH_DIRS=(
    "/srv/django"
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

    # First line containing __version__, tolerant to spacing
    local line
    if ! line=$(grep -m1 "$VERSION_KEY" "$file" 2>/dev/null); then
        return 1
    fi

    # Extract the string inside the first pair of double quotes
    local version
    version=$(echo "$line" | sed -E 's/.*__version__[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/')

    if [[ -z "$version" || "$version" == "$line" ]]; then
        return 1
    fi

    echo "$version"
    return 0
}

bump_version() {
    local version="$1"

    # Expect something like 1.2.3.000011-dev
    # Split into 4 segments by '.', then split 4th by '-'
    echo "$version" | awk -F. '
        BEGIN {OFS="."}
        {
            if (NF < 4) {
                print $0;
                exit;
            }
            split($4, s, "-");
            build = s[1] + 1;
            suffix = s[2];
            $4 = sprintf("%06d-%s", build, suffix);
            print $0;
        }
    '
}

update_version_in_file() {
    local file="$1"
    local from="$2"
    local to="$3"

    if $DRY_RUN; then
        log "INFO" "[DRY-RUN] Would update $file: $from → $to"
        return 0
    fi

    # Replace the value only, preserving spacing and key
    # Match: __version__ [spaces] = [spaces] "old"
    # Replace: same prefix + "new"
    sed -i -E "s|(__version__[[:space:]]*=[[:space:]]*\")$from\"|\1$to\"|" "$file"

    log "INFO" "Version bump: $file → $to"
}

process_file() {
    local file="$1"

    debug "Processing candidate: $file"

    # Ensure it's a regular readable file
    if [[ ! -f "$file" || ! -r "$file" ]]; then
        debug "Skipping non-regular or unreadable file: $file"
        return 0
    fi

    if ! has_allowed_extension "$file"; then
        debug "Skipping due to extension filter: $file"
        return 0
    fi

    if ! grep -q "$VERSION_KEY" "$file" 2>/dev/null; then
        debug "No __version__ key in: $file"
        return 0
    fi

    local from to
    from=$(extract_version "$file") || {
        debug "Could not extract version from: $file"
        return 0
    }

    to=$(bump_version "$from")

    if [[ "$from" == "$to" ]]; then
        debug "Version unchanged for $file ($from)"
        return 0
    fi

    update_version_in_file "$file" "$from" "$to"
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
INOTIFY_ARGS=(
    -m          # monitor
    -r          # recursive
    -e close_write
    --format '%w%f'
    --exclude '(\.tmp$|~$|\.swp$|\.swx$)'
)

log "INFO" "Watching directories:"
for d in "${WATCH_DIRS[@]}"; do
    log "INFO" "  - $d"
done

# Main watch loop
stdbuf -oL inotifywait "${INOTIFY_ARGS[@]}" "${WATCH_DIRS[@]}" 2>>"$LOG_FILE" \
| while read -r FILE_PATH; do
    debug "Event: close_write on $FILE_PATH"
    process_file "$FILE_PATH"
done
