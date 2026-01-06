#!/bin/bash
# ==========================================
# Django Restart all services
# ==========================================
# __version__ = "0.1.0.000047-dev"




set -euo pipefail

# Colors
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
MAGENTA="\e[35m"
RESET="\e[0m"

SERVICES=(
    "gunicorn-MikesLists-dev"
    "gunicorn-MikesLists-test"
    "gunicorn-MikesLists-live"
)

echo -e "${MAGENTA}=========================================="
echo -e "      Reloading Django + Nginx Services"
echo -e "==========================================${RESET}"

# 1. Validate Nginx configuration
echo -e "\n${MAGENTA}Checking Nginx configuration...${RESET}"
if sudo nginx -t > /dev/null 2>&1; then
    echo -e "  ${GREEN}✔ Nginx configuration is valid${RESET}"
else
    echo -e "  ${RED}✖ Nginx configuration is INVALID${RESET}"
    sudo nginx -t
    exit 1
fi

# 2. Sync Systemd (CRITICAL FIX)
echo -e "\n${MAGENTA}Syncing systemd configurations...${RESET}"
sudo systemctl daemon-reload
echo -e "  ${GREEN}✔ daemon-reload complete${RESET}"

# 3. Restart Nginx
echo -e "\n${MAGENTA}Restarting nginx...${RESET}"
sudo systemctl restart nginx
echo -e "  ${GREEN}✔ nginx restarted${RESET}"

# 4. Restart Django Gunicorn services
for SVC in "${SERVICES[@]}"; do
    echo -e "\n${MAGENTA}Restarting $SVC...${RESET}"
    if sudo systemctl restart "$SVC"; then
        echo -e "  ${GREEN}✔ $SVC restarted successfully${RESET}"
    else
        echo -e "  ${RED}✖ $SVC FAILED to restart${RESET}"
        sudo journalctl -u "$SVC" -n 20 --no-pager
        exit 1
    fi

    # Give it a moment to create the socket
    sleep 1

    if sudo systemctl is-active --quiet "$SVC"; then
        echo -e "  ${GREEN}✔ $SVC is ACTIVE${RESET}"
    else
        echo -e "  ${RED}✖ $SVC is NOT ACTIVE${RESET}"
        exit 1
    fi
done

sudo journalctl -u gunicorn -n 50 --no-pager


# 5. Final Verification
echo -e "\n${MAGENTA}Running health verification...${RESET}"
chk.sh

echo -e "\n${MAGENTA}=========================================="
echo -e "        All services bounced cleanly"
echo -e "==========================================${RESET}"
