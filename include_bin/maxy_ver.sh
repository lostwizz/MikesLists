#!/bin/bash
# ==========================================
#  Script for Finding and Updating Version Numbers
# ==========================================
# __version__ = "0.0.1.000052-dev"

# Configuration
SEARCH_DIR="${1:-.}"
TARGET_PATTERN='__version__ = "'
SCRIPT_NAME=$(basename "$0")

echo "Examining files in $SEARCH_DIR..."
echo "------------------------------------------"

# 1. Gather data, explicitly excluding this script file by name
MAP_DATA=$(grep -r "$TARGET_PATTERN" "$SEARCH_DIR" --include="*.py" --include="*.sh" | grep -v "$SCRIPT_NAME")

if [[ -z "$MAP_DATA" ]]; then
    echo "No version strings found (excluding $SCRIPT_NAME)."
    exit 1
fi

# Clean output for display
echo "$MAP_DATA" | while read -r line; do
    FILE=$(echo "$line" | cut -d: -f1)
    # Extract just the version string between quotes
    VER=$(echo "$line" | sed 's/.*"\(.*\)".*/\1/')
    echo "$FILE: $VER"
done

# 2. Determine default (highest) version
# This extracts all versions, sorts them correctly, and picks the top one
AUTO_VERSION=$(echo "$MAP_DATA" | sed 's/.*"\(.*\)".*/\1/' | sort -V | tail -n 1)

echo "------------------------------------------"
echo "Highest version found: $AUTO_VERSION"
echo "------------------------------------------"

# 3. Prompt for Manual Version Entry
read -p "Enter new version number [Leave blank for $AUTO_VERSION]: " MANUAL_VERSION

# Use manual version if provided, otherwise use auto version
FINAL_VERSION=${MANUAL_VERSION:-$AUTO_VERSION}

if [[ -z "$FINAL_VERSION" ]]; then
    echo "Error: No version determined."
    exit 1
fi

echo "Target Version: $FINAL_VERSION"
read -p "Update all files to $FINAL_VERSION? (y/n): " confirm

if [[ "$confirm" == [yY] ]]; then
    echo "Updating files..."

    # Get unique list of files to process
    FILES_TO_UPDATE=$(echo "$MAP_DATA" | cut -d: -f1 | sort -u)

    for FILE in $FILES_TO_UPDATE; do
        # Use @ as sed delimiter to safely handle dots and dashes
        sed -i "s@__version__ = \".*\"@__version__ = \"$FINAL_VERSION\"@" "$FILE"
        echo "Updated $FILE"
    done
    echo "Update complete."
else
    echo "No changes made."
fi
