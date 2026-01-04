#!/bin/bash

# ============================
#  Django Multi‑Env Health Check
# ============================

# Ensure jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: 'jq' is not installed. Please install it to run this script."
    exit 1
fi

ENVS=("dev" "test" "live")
SERVICES=("gunicorn-MikesLists-dev" "gunicorn-MikesLists-test" "gunicorn-MikesLists-live" "nginx")

declare -A URLS
URLS["dev"]="http://localhost:8001/health/"
URLS["test"]="http://localhost:8002/health/"
URLS["live"]="http://localhost:80/health/"

# Colors
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
BLUE="\e[34m"
RESET="\e[0m"

OK_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

echo -e "${BLUE}=========================================="
echo -e "        Django Environment Health Check"
echo -e "==========================================${RESET}"

# [1] Systemd Service Status
echo -e "\n${BLUE}[1] Service Status:${RESET}"
for SVC in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$SVC"; then
        echo -e "  ${GREEN}✔ $SVC is RUNNING${RESET}"
        ((OK_COUNT++))
    else
        echo -e "  ${RED}✖ $SVC is NOT RUNNING${RESET}"
        ((FAIL_COUNT++))
    fi
done

# [2] Socket Verification
echo -e "\n${BLUE}[2] Socket Verification:${RESET}"
for ENV in "${ENVS[@]}"; do
    SOCK="/srv/django/MikesLists_${ENV}/MikesLists.sock"
    if [ -S "$SOCK" ]; then
        OWNER=$(stat -c '%U:%G' "$SOCK")
        if [[ "$OWNER" == "pi:www-data" || "$OWNER" == "pi:root" ]]; then
            echo -e "  ${GREEN}✔ $ENV Socket: Found (Owned by $OWNER)${RESET}"
            ((OK_COUNT++))
        else
            echo -e "  ${YELLOW}⚠ $ENV Socket: WRONG OWNER ($OWNER)${RESET}"
            ((WARN_COUNT++))
        fi
    else
        echo -e "  ${RED}✖ $ENV Socket: NOT FOUND at $SOCK${RESET}"
        ((FAIL_COUNT++))
    fi
done

# [3] Recent App Errors
echo -e "\n${BLUE}[3] Recent App Errors (Last 5 lines):${RESET}"
for ENV in "${ENVS[@]}"; do
    echo -e "  --- ${ENV} ---"
    # Using -q to suppress "no entries" messages
    ERRORS=$(sudo journalctl -u "gunicorn-MikesLists-$ENV" -n 5 --no-pager 2>/dev/null | grep -iE "error|exception|fail")
    if [[ -z "$ERRORS" ]]; then
        echo -e "    ${GREEN}No immediate errors found.${RESET}"
        ((OK_COUNT++))
    else
        echo -e "${RED}$ERRORS${RESET}"
        ((WARN_COUNT++))
    fi
done

# [4] Nginx Configuration Syntax
echo -e "\n${BLUE}[4] Nginx Config Test:${RESET}"
if sudo nginx -t > /dev/null 2>&1; then
    echo -e "  ${GREEN}✔ Nginx configuration is VALID${RESET}"
    ((OK_COUNT++))
else
    echo -e "  ${RED}✖ Nginx configuration has ERRORS${RESET}"
    ((FAIL_COUNT++))
fi

# [5] HTTP Endpoint Checks
echo -e "\n${BLUE}[5] HTTP Endpoint Checks:${RESET}"
for ENV in "${ENVS[@]}"; do
    URL="${URLS[$ENV]}"
    echo -e "  Checking ${ENV} (${URL})"

    # Store JSON in a variable to avoid writing to disk
    RESPONSE=$(curl -s -w "\n%{http_code} %{time_total}" "$URL")
    
    # Extract data from the response
    HTTP_BODY=$(echo "$RESPONSE" | sed '$d')
    HTTP_STATS=$(echo "$RESPONSE" | tail -n1)
    HTTP_CODE=$(echo "$HTTP_STATS" | awk '{print $1}')
    TIME=$(echo "$HTTP_STATS" | awk '{print $2}')

    if [[ "$HTTP_CODE" == "200" ]]; then
        echo -e "    ${GREEN}✔ HTTP 200 OK${RESET} (${TIME}s)"
        ((OK_COUNT++))
    else
        echo -e "    ${RED}✖ HTTP $HTTP_CODE${RESET} (${TIME}s)"
        ((FAIL_COUNT++))
        continue
    fi

    # Validate JSON directly from variable
    if echo "$HTTP_BODY" | jq empty 2>/dev/null; then
        echo -e "    ${GREEN}✔ JSON valid${RESET}"
        ((OK_COUNT++))
        
        STATUS=$(echo "$HTTP_BODY" | jq -r '.status // empty')
        if [[ "$STATUS" == "ok" ]]; then
            echo -e "    ${GREEN}✔ Status field OK${RESET}"
            ((OK_COUNT++))
        else
            echo -e "    ${YELLOW}⚠ Missing or unexpected status field${RESET}"
            ((WARN_COUNT++))
        fi
    else
        echo -e "    ${RED}✖ Invalid JSON${RESET}"
        ((FAIL_COUNT++))
    fi
done

# ---------------------------------------------------------
# [6] Django Deployment Check
# ---------------------------------------------------------
echo -e "\n${BLUE}[6] Django Deployment Check:${RESET}"
for ENV in "${ENVS[@]}"; do
    echo -e "  --- ${ENV} ---"
    # Capture the output and look for "WARNINGS" or "ERRORS"
    CHECK_OUT=$(/srv/django/venv-${ENV}/bin/python /srv/django/MikesLists_${ENV}/manage.py check --deploy 2>&1)
    echo "$CHECK_OUT"

    if [[ "$CHECK_OUT" == *"System check identified no issues"* ]]; then
        echo -e "    ${GREEN}✔ Deployment check passed${RESET}"
        ((OK_COUNT++))
    else
        # If there are warnings but no "ERRORS", count as warning
        if [[ "$CHECK_OUT" == *"ERRORS:"* ]]; then
             echo -e "    ${RED}✖ Deployment check found CRITICAL ERRORS${RESET}"
             ((FAIL_COUNT++))
        else
             echo -e "    ${YELLOW}⚠ Deployment check found configuration warnings${RESET}"
             ((WARN_COUNT++))
        fi
    fi
done
echo -e "\n${BLUE}[7] Disk Space (Root):${RESET}"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo -e "  ${RED}✖ Disk is critically full: ${DISK_USAGE}%${RESET}"
    ((FAIL_COUNT++))
else
    echo -e "  ${GREEN}✔ Disk usage is OK: ${DISK_USAGE}%${RESET}"
    ((OK_COUNT++))
fi

echo -e "\n${BLUE}[8] Memory Usage:${RESET}"
FREE_MEM=$(free | grep Mem | awk '{print $3/$2 * 100.0}' | cut -d. -f1)
if [ "$FREE_MEM" -gt 85 ]; then
    echo -e "  ${YELLOW}⚠ High RAM usage: ${FREE_MEM}%${RESET}"
    ((WARN_COUNT++))
else
    echo -e "  ${GREEN}✔ RAM usage is OK: ${FREE_MEM}%${RESET}"
    ((OK_COUNT++))
fi

# Summary (Matches your original logic)
echo -e "\n${BLUE}=========================================="
echo -e "                SUMMARY"
echo -e "==========================================${RESET}"
echo -e "${GREEN}✔ OK: $OK_COUNT${RESET}"
echo -e "${YELLOW}⚠ WARNINGS: $WARN_COUNT${RESET}"
echo -e "${RED}✖ FAILURES: $FAIL_COUNT${RESET}"

if (( FAIL_COUNT > 0 )); then
    echo -e "\n${RED}Overall Status: FAIL${RESET}"
elif (( WARN_COUNT > 0 )); then
    echo -e "\n${YELLOW}Overall Status: WARN${RESET}"
else
    echo -e "\n${GREEN}Overall Status: OK${RESET}"
fi
echo -e "${BLUE}==========================================${RESET}"
