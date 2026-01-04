#!/bin/bash
# ==========================================
# auto increment the build number (4th number in 1.2.3.4-dev)
# ==========================================
# __version__ = "0.1.0.00012-dev"


# Reload the system: sudo systemctl daemon-reload
# Enable it to start at boot: sudo systemctl enable version-bumper.service
# sudo systemctl start version-bumper.serviceStart it now: sudo systemctl start version-bumper.service

# Check status: sudo systemctl status version-bumper.service
# View logs: If it’s not working, check the output with journalctl -u version-bumper.service -f
# Stop it: sudo systemctl stop version-bumper.service


#!/bin/bash
# __version__ = "0.1.0.00012-dev"

PROJECT_DIR="/srv/django/MikesLists_dev"
BIN_DIR="/home/pi/bin"

# 1. Use stdbuf to prevent log delays in journalctl
stdbuf -oL inotifywait -m -r -e close_write --exclude ".*\.tmp|.*~" --format '%w%f' "$PROJECT_DIR" "$BIN_DIR" | while read FILE_PATH; do

    if [[ "$FILE_PATH" == *.py || "$FILE_PATH" == *.sh ]]; then
        # 2. HIDE THE STRING: By splitting this, the script won't match itself
        S_PART1="__version__"
        S_PART2=" ="
        S_STR="${S_PART1}${S_PART2}"

        # 3. Use a more flexible grep to handle different spacing/quotes
        if grep -q "__version__[[:space:]]*=[[:space:]]*[\"']" "$FILE_PATH"; then

            # Extract current version
            VERSION_FROM=$(grep "$S_STR" "$FILE_PATH" | awk -F'"' '{print $2}' | head -n 1)

            if [[ -n "$VERSION_FROM" ]]; then
                # 4. Corrected Increment logic for 1.2.3.4-dev format
                VERSION_TO=$(echo "$VERSION_FROM" | awk -F. 'BEGIN {OFS="."} {
                    if ($4 ~ /-/) {
                        split($4, s, "-");
                        $4 = sprintf("%05d-%s", s[1] + 1, s[2]);
                    } else {
                        $4 = sprintf("%05d", $4 + 1);
                    }
                    print $0
                }')

                # 5. Only perform update if it's not already updated (prevents loops)
                if [ "$VERSION_FROM" != "$VERSION_TO" ]; then
                    SHORT_PATH=$(echo "$FILE_PATH" | awk -F/ '{print "..." $(NF-2) "/" $(NF-1) "/" $NF}')

                    # 6. Secure replacement using | as delimiter
                    sed -i "s|__version__ = \".*\"|__version__ = \"$VERSION_TO\"|" "$FILE_PATH"

                    echo "Bumping version in: $SHORT_PATH"
                    echo "$FILE_PATH $VERSION_FROM -> $VERSION_TO"
                fi
            fi
        fi
    fi
done
