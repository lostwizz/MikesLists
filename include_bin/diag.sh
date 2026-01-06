#!/bin/bash
# ==========================================
# Django Deep Diagnostic Tool v1.0
# ==========================================
# __version__ = "0.1.0.000046-dev"

# Configuration - Adjust based on environment
ENV=${1:-dev} # Default to dev if not specified
PROJECT_PATH="/srv/django/MikesLists_$ENV"
VENV_PATH="/srv/django/venv-$ENV"
GUNICORN_SERVICE="gunicorn-MikesLists-$ENV"

# Colors
RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
CYAN="\e[36m"
RESET="\e[0m"

echo -e "${CYAN}Starting deep diagnostics for: ${ENV}${RESET}"

# 1. Check Gunicorn Service Status
echo -e "\n${YELLOW}[1] Checking Gunicorn Service Status...${RESET}"
if systemctl is-active --quiet "$GUNICORN_SERVICE"; then
    echo -e "${GREEN}✔ Gunicorn is active.${RESET}"
else
    echo -e "${RED}✖ Gunicorn is NOT active. Showing last 20 error logs:${RESET}"
    sudo journalctl -u "$GUNICORN_SERVICE" -n 20 --no-pager
fi

# 2. Syntax & Django Integrity Check
echo -e "\n${YELLOW}[2] Running Django System Check (Syntax & Config)...${RESET}"
CHECK_OUTPUT=$($VENV_PATH/bin/python $PROJECT_PATH/manage.py check 2>&1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✔ No syntax or configuration errors found.${RESET}"
else
    echo -e "${RED}✖ ERROR DETECTED in Django code:${RESET}"
    echo "$CHECK_OUTPUT"
    echo -e "\n${CYAN}Recommendation: Run the test server manually to see live traceback:${RESET}"
    echo -e "Command: $VENV_PATH/bin/python $PROJECT_PATH/manage.py runserver 0.0.0.0:9001"
fi

# 3. Check for recent 500/Traceback errors in Logs
echo -e "\n${YELLOW}[3] Scanning Journal for Tracebacks (HTTP 500)...${RESET}"
TRACEBACK=$(sudo journalctl -u "$GUNICORN_SERVICE" -n 100 --no-pager | grep -A 10 "Traceback")

if [[ -z "$TRACEBACK" ]]; then
    echo -e "${GREEN}No recent Python tracebacks found in system logs.${RESET}"
else
    echo -e "${RED}Found Traceback in logs:${RESET}"
    echo "$TRACEBACK"
fi

# 4. Database Connection Test
echo -e "\n${YELLOW}[4] Testing Database Connectivity...${RESET}"
DB_STATUS=$($VENV_PATH/bin/python $PROJECT_PATH/manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('OK')" 2>/dev/null)

if [ "$DB_STATUS" == "OK" ]; then
    echo -e "${GREEN}✔ Database is reachable.${RESET}"
else
    echo -e "${RED}✖ Database connection failed. Check database settings or service.${RESET}"
fi

echo -e "\n${CYAN}Diagnostics complete.${RESET}"