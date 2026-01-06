#!/bin/bash
# ==========================================
#  Script for Finding and Updating Version Numbers (with highest numbers in folder)
# ==========================================
# __version__ = "0.0.1.000049-dev"






# Configuration
SEARCH_DIR="${1:-.}" # Default to current directory if not provided
TARGET_PATTERN="__version__ ="
echo "Examining files in $SEARCH_DIR..."
echo "------------------------------------------"

# 1. Find all files and their versions, then display them
# We store the grep results to avoid searching the disk multiple times
MAP_DATA=$(grep -r "$TARGET_PATTERN" "$SEARCH_DIR" --include="*.py" --include="*.sh")

if [[ -z "$MAP_DATA" ]]; then
    echo "No version strings found in $SEARCH_DIR."
    exit 1
fi

# Output the examined files and their versions
echo "$MAP_DATA" | while read -r line; do
    FILE=$(echo "$line" | cut -d: -f1)
    VER=$(echo "$line" | awk -F'"' '{print $2}')
    # Shorten the path for the display
    SHORT_PATH=$(echo "$FILE" | awk -F/ '{if (NF>2) print "..." $(NF-2) "/" $(NF-1) "/" $NF; else print $0}')
    echo "$SHORT_PATH: $VER"
done

# 2. Identify the highest version and which file it belongs to
# We sort the data and take the very last line
WINNER_LINE=$(echo "$MAP_DATA" | \
    sort -t. -k1,1n -k2,2n -k3,3n -k4,4n -k5,5n | \
    tail -n 1)

MAX_FILE=$(echo "$WINNER_LINE" | cut -d: -f1)
HIGHEST_VERSION=$(echo "$WINNER_LINE" | awk -F'"' '{print $2}')

echo "------------------------------------------"
echo "Highest version found: $HIGHEST_VERSION"
echo "Found in: $MAX_FILE"
echo "------------------------------------------"

# 3. Optional: Prompt user to update all files
read -p "Do you want to update all other files to $HIGHEST_VERSION? (y/n): " confirm

if [[ "$confirm" == [yY] ]]; then
    echo "Updating files..."
    echo "$MAP_DATA" | while read -r line; do
        FILE=$(echo "$line" | cut -d: -f1)
        CURRENT_FILE_VERSION=$(echo "$line" | awk -F'"' '{print $2}')

        if [[ "$CURRENT_FILE_VERSION" != "$HIGHEST_VERSION" ]]; then
            # Perform the replacement
            sed -i "s|__version__ = \".*\"|__version__ = \"$HIGHEST_VERSION\"|" "$FILE"

            SHORT_PATH=$(echo "$FILE" | awk -F/ '{if (NF>2) print "..." $(NF-2) "/" $(NF-1) "/" $NF; else print $0}')
            echo "Updated $SHORT_PATH: $CURRENT_FILE_VERSION -> $HIGHEST_VERSION"
        fi
    done
    echo "Update complete."
else
    echo "No changes made."
fi
