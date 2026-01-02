#!/usr/bin/env bash
set -euo pipefail

# Colors
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
BLUE="\e[34m"
RESET="\e[0m"

SERVICES=(
    "gunicorn-MikesLists-dev"
    "gunicorn-MikesLists-test"
    "gunicorn-MikesLists-live"
)

echo -e "${BLUE}=========================================="
echo -e "     Reloading Django + Nginx Services"
echo -e "==========================================${RESET}"

# ---------------------------------------------------------
# 1. Validate Nginx configuration
# ---------------------------------------------------------
echo -e "\n${BLUE}Checking Nginx configuration...${RESET}"

if sudo nginx -t > /dev/null 2>&1; then
    echo -e "  ${GREEN}✔ Nginx configuration is valid${RESET}"
else
    echo -e "  ${RED}✖ Nginx configuration is INVALID${RESET}"
    echo -e "  ${YELLOW}Showing nginx error output:${RESET}"
    sudo nginx -t
    exit 1
fi

# ---------------------------------------------------------
# 2. Restart Nginx
# ---------------------------------------------------------
echo -e "\n${BLUE}Restarting nginx...${RESET}"

if sudo systemctl restart nginx; then
    echo -e "  ${GREEN}✔ nginx restarted successfully${RESET}"
else
    echo -e "  ${RED}✖ nginx FAILED to restart${RESET}"
    echo -e "  ${YELLOW}Tailing nginx error log:${RESET}"
    sudo journalctl -u nginx -n 40 --no-pager
    exit 1
fi

# ---------------------------------------------------------
# 3. Restart Django Gunicorn services
# ---------------------------------------------------------
for SVC in "${SERVICES[@]}"; do
    echo -e "\n${BLUE}Restarting $SVC...${RESET}"

    if sudo systemctl restart "$SVC"; then
        echo -e "  ${GREEN}✔ $SVC restarted successfully${RESET}"
    else
        echo -e "  ${RED}✖ $SVC FAILED to restart${RESET}"
        echo -e "  ${YELLOW}Tailing logs for $SVC:${RESET}"
        sudo journalctl -u "$SVC" -n 40 --no-pager
        exit 1
    fi

    # Verify service is active
    if sudo systemctl is-active --quiet "$SVC"; then
        echo -e "  ${GREEN}✔ $SVC is ACTIVE${RESET}"
    else
        echo -e "  ${RED}✖ $SVC is NOT ACTIVE after restart${RESET}"
        echo -e "  ${YELLOW}Tailing logs for $SVC:${RESET}"
        sudo journalctl -u "$SVC" -n 40 --no-pager
        exit 1
    fi
done

echo -e "\n${BLUE}=========================================="
echo -e "        All services restarted cleanly"
echo -e "==========================================${RESET}"
