#!/bin/bash
# ==========================================
# Django Restart all services (DEV + TEST + LIVE)
# ==========================================
# __version__ = "0.2.0.000049-dev"

set -euo pipefail

# Colors
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
MAGENTA="\e[35m"
RESET="\e[0m"

SERVICES=(
    "mikeslists-dev.service"
    "gunicorn-MikesLists-test"
    "gunicorn-MikesLists-live"
)

echo -e "${MAGENTA}=========================================="
echo -e "      Reloading Django + Nginx Services"
echo -e "==========================================${RESET}"

# ---------------------------------------------------------
# 1. DEV RUNSERVER CLEANUP
# ---------------------------------------------------------
echo -e "\n${MAGENTA}Checking for Django runserver (DEV)...${RESET}"


echo -e "\n${MAGENTA}Checking for processes on port 8000 (DEV)...${RESET}"

# Find the PID specifically using port 8000
PORT_PID=$(sudo lsof -t -i:8000 || true)

if [[ -n "$PORT_PID" ]]; then
    echo -e "  ${YELLOW}Found process $PORT_PID occupying port 8000${RESET}"

    echo -e "  ${YELLOW}Forcefully clearing port 8000...${RESET}"
    sudo kill -9 "$PORT_PID" 2>/dev/null || true
    sleep 2

    # Verify the port is free
    if sudo lsof -i:8000 >/dev/null; then
        echo -e "  ${RED}✖ FAILED to clear port 8000. Manual intervention required.${RESET}"
        exit 1
    else
        echo -e "  ${GREEN}✔ Port 8000 is now free${RESET}"
    fi
else
    echo -e "  ${GREEN}✔ Port 8000 is already clear${RESET}"
fi



PIDS=$(pgrep -f "manage.py runserver" || true)

if [[ -n "$PIDS" ]]; then
    echo -e "  ${YELLOW}Found runserver processes:${RESET}"
    echo "$PIDS" | sed 's/^/    PID: /'

    echo -e "  ${YELLOW}Killing runserver processes...${RESET}"
    pkill -9 -f "manage.py runserver" 2>/dev/null || true
    sleep 1

    # Double-check
    if pgrep -f "manage.py runserver" >/dev/null; then
        echo -e "  ${RED}✖ Some runserver processes survived. Killing individually...${RESET}"
        for PID in $PIDS; do
            kill -9 "$PID" 2>/dev/null || true
        done
    fi

    if pgrep -f "manage.py runserver" >/dev/null; then
        echo -e "  ${RED}✖ FAILED to kill runserver processes${RESET}"
        exit 1
    else
        echo -e "  ${GREEN}✔ All runserver processes terminated${RESET}"
    fi
else
    echo -e "  ${GREEN}✔ No runserver processes running${RESET}"
fi

# ---------------------------------------------------------
# 2. Validate Nginx configuration
# ---------------------------------------------------------
echo -e "\n${MAGENTA}Checking Nginx configuration...${RESET}"
if sudo nginx -t > /dev/null 2>&1; then
    echo -e "  ${GREEN}✔ Nginx configuration is valid${RESET}"
else
    echo -e "  ${RED}✖ Nginx configuration is INVALID${RESET}"
    sudo nginx -t
    exit 1
fi

# ---------------------------------------------------------
# 3. Reload systemd
# ---------------------------------------------------------
echo -e "\n${MAGENTA}Syncing systemd configurations...${RESET}"
sudo systemctl daemon-reload
echo -e "  ${GREEN}✔ daemon-reload complete${RESET}"

# ---------------------------------------------------------
# 4. Restart Nginx
# ---------------------------------------------------------
echo -e "\n${MAGENTA}Restarting nginx...${RESET}"
sudo systemctl restart nginx
echo -e "  ${GREEN}✔ nginx restarted${RESET}"

# ---------------------------------------------------------
# 5. Restart TEST + LIVE Gunicorn services
# ---------------------------------------------------------
for SVC in "${SERVICES[@]}"; do
    echo -e "\n${MAGENTA}Restarting $SVC...${RESET}"
    if sudo systemctl restart "$SVC"; then
        echo -e "  ${GREEN}✔ $SVC restarted successfully${RESET}"
    else
        echo -e "  ${RED}✖ $SVC FAILED to restart${RESET}"
        sudo journalctl -u "$SVC" -n 20 --no-pager
        exit 1
    fi

    sleep 1

    if sudo systemctl is-active --quiet "$SVC"; then
        echo -e "  ${GREEN}✔ $SVC is ACTIVE${RESET}"
    else
        echo -e "  ${RED}✖ $SVC is NOT ACTIVE${RESET}"
        exit 1
    fi
done

# ---------------------------------------------------------
# 6. OPTIONAL: Restart DEV runserver
# ---------------------------------------------------------
echo -e "\n${MAGENTA}Starting Django runserver (DEV)...${RESET}"

DEV_DIR="/srv/django/MikesLists_dev"
DEV_VENV="/srv/django/venv-dev/bin/python"

if [[ -d "$DEV_DIR" ]]; then
    cd "$DEV_DIR"
    nohup $DEV_VENV manage.py runserver 0.0.0.0:8000 \
        > "$DEV_DIR/runserver.log" 2>&1 &
    echo -e "  ${GREEN}✔ runserver started on port 8000${RESET}"
else
    echo -e "  ${YELLOW}⚠ DEV directory not found — skipping runserver start${RESET}"
fi

# ---------------------------------------------------------
# 7. Final Output
# ---------------------------------------------------------
echo -e "\n${MAGENTA}=========================================="
echo -e "        All services bounced cleanly"
echo -e "==========================================${RESET}"
