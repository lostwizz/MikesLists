#!/bin/bash

# File to store last known IP
LAST_IP_FILE="/var/local/last_ip.txt"

# Wait for network to be ready
sleep 20

# Get current Wi-Fi IP (first address)
CURRENT_IP=$(hostname -I | awk '{print $1}')

# If no IP, exit silently
if [[ -z "$CURRENT_IP" ]]; then
    exit 0
fi

# If file doesn't exist, create it and store current IP
if [[ ! -f "$LAST_IP_FILE" ]]; then
    echo "$CURRENT_IP" > "$LAST_IP_FILE"
    exit 0
fi

# Read last known IP
LAST_IP=$(cat "$LAST_IP_FILE")

# Compare
if [[ "$CURRENT_IP" != "$LAST_IP" ]]; then
    echo "Raspberry Pi IP changed from $LAST_IP to $CURRENT_IP" \
        | mail -s "Raspberry Pi IP Changed"  public@merrett.ca

    # Update stored IP
    echo "$CURRENT_IP" > "$LAST_IP_FILE"
fi
