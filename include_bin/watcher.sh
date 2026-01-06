#!/bin/bash
# ==========================================
# Version Auto‑Bumper
# Increments the 4th number in 1.2.3.000003-dev
#
# __version__ = "0.0.0.000012-dev"
#
# __author__ = "Mike Merrett"
# __updated__ = "2026-01-02 19:49:31"
# __created__ = "2026-01-02 19:49:31"
# __description__ = "Auto version bump watcher"
# ==========================================


# Reload the system: sudo systemctl daemon-reload
# Enable it to start at boot: sudo systemctl enable version-bumper.service
# sudo systemctl start version-bumper.service
# Start it now: sudo systemctl start version-bumper.service

# Check status: sudo systemctl status version-bumper.service
# View logs: If it’s not working, check the output with journalctl -u version-bumper.service -f
#    to see the complete log use   --- journalctl -u version-bumper.service

# Stop it: sudo systemctl stop version-bumper.service


WATCH_DIR="/srv/django"
BIN_DIR="/home/pi/bin"

stdbuf -oL inotifywait -m -r \
    -e close_write \
    --exclude ".*\.tmp|.*~" \
    --format '%w%f' \
    "$WATCH_DIR" "$BIN_DIR" | while read FILE_PATH; do

    if grep -q "__version__[[:space:]]*=[[:space:]]*[\"']" "$FILE_PATH"; then

        VERSION_FROM=$(grep "__version__" "$FILE_PATH" | head -n 1 | awk -F'"' '{print $2}')

        if [[ -n "$VERSION_FROM" ]]; then
            VERSION_TO=$(echo "$VERSION_FROM" | awk -F. '
                BEGIN {OFS="."}
                {
                    split($4, s, "-");
                    build = s[1] + 1;
                    suffix = s[2];
                    $4 = sprintf("%06d-%s", build, suffix);
                    print $0
                }
            ')

            if [[ "$VERSION_FROM" != "$VERSION_TO" ]]; then
                sed -i "s|__version__ = \".*\"|__version__ = \"$VERSION_TO\"|" "$FILE_PATH"
                echo "Version bump: $FILE_PATH → $VERSION_TO"
            fi
        fi
    fi
done
