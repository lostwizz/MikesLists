#!/bin/bash
# ==========================================
# Django Health Check - Unified Edition
# ==========================================
# __version__="0.2.0.00005-dev"

ENVS=("dev" "test" "live")

# Ports
declare -A PORTS
PORTS["dev"]=8000
PORTS["test"]=9000
PORTS["live"]=80

# Health URLs
declare -A URLS
URLS["dev"]="http://localhost:8000/health/"
URLS["test"]="http://localhost:9000/health/"
URLS["live"]="http://localhost/health/"

# Expected ownership
# EXPECTED_OWNER="pi:www-data"
EXPECTED_OWNER="pi:pi"

# Colors
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
MAGENTA="\e[35m"
CYAN="\e[36m"
RESET="\e[0m"

OK=0
WARN=0
FAIL=0

echo -e "${MAGENTA}=========================================="
echo -e "        Unified Django Health Check"
echo -e "==========================================${RESET}"

# ---------------------------------------------------------
# [1] Version Checks
# ---------------------------------------------------------
echo -e "\n${MAGENTA}[1] Version Checks${RESET}"

NGINX_VERSION=$(nginx -v 2>&1)
echo -e "  Nginx:   ${CYAN}${NGINX_VERSION}${RESET}"

MARIADB_VERSION=$(mariadb --version 2>/dev/null)
if [[ -n "$MARIADB_VERSION" ]]; then
    echo -e "  MariaDB: ${CYAN}${MARIADB_VERSION}${RESET}"
else
    echo -e "  MariaDB: ${YELLOW}⚠ mariadb client not found${RESET}"
    ((WARN++))
fi

for ENV in "${ENVS[@]}"; do
    echo -e "\n  --- ${ENV} ---"
    VENV="/srv/django/venv-${ENV}/bin/python"
    MANAGE="/srv/django/MikesLists_${ENV}/manage.py"

    PYV=$($VENV -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>/dev/null)
    echo -e "    Python Version:  ${CYAN}${PYV:-UNKNOWN}${RESET}"

    DJV=$($VENV -c "import django; print(django.get_version())" 2>/dev/null)
    echo -e "    Django Version:  ${CYAN}${DJV:-UNKNOWN}${RESET}"

    if [[ "$ENV" != "dev" ]]; then
        GUNV=$(/srv/django/venv-${ENV}/bin/gunicorn --version 2>/dev/null)
        echo -e "    Gunicorn:        ${CYAN}${GUNV:-NOT FOUND}${RESET}"
    fi
done

# ---------------------------------------------------------
# [2] Environment & Settings Verification
# ---------------------------------------------------------
echo -e "\n${MAGENTA}[2] Environment & Settings Verification${RESET}"

for ENV in "${ENVS[@]}"; do
    echo -e "  --- ${ENV} ---"
    VENV_PY="/srv/django/venv-${ENV}/bin/python"
    MANAGE_PY="/srv/django/MikesLists_${ENV}/manage.py"

    ACTUAL_PY=$($VENV_PY -c "import sys; print(sys.executable)" 2>/dev/null)
    if [[ "$ACTUAL_PY" == *"/venv-${ENV}/"* ]]; then
        echo -e "    Python:   ${GREEN}✔ Correct${RESET}"
    else
        echo -e "    Python:   ${RED}✖ MISMATCH${RESET} (${ACTUAL_PY})"
        ((FAIL++))
    fi

    ACTIVE_SETTING=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.SETTINGS_MODULE)" 2>/dev/null | tail -n 1)
    if [[ "$ACTIVE_SETTING" == *"$ENV"* ]]; then
        echo -e "    Settings: ${GREEN}✔ Correct${RESET} (${ACTIVE_SETTING})"
    else
        echo -e "    Settings: ${RED}✖ WRONG MODULE${RESET} (${ACTIVE_SETTING})"
        ((FAIL++))
    fi

    DEBUG_STATUS=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.DEBUG)" 2>/dev/null | tail -n 1)
    if [[ "$DEBUG_STATUS" == "True" ]]; then
        if [[ "$ENV" == "live" ]]; then
            echo -e "    DEBUG:    ${RED}✖ TRUE (Security Risk!)${RESET}"
            ((FAIL++))
        else
            echo -e "    DEBUG:    ${YELLOW}⚠ True (Standard for Dev/Test)${RESET}"
            ((WARN++))
        fi
    else
        echo -e "    DEBUG:    ${GREEN}✔ False${RESET}"
    fi

    ENV_NAME=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.ENV_NAME)" 2>/dev/null | tail -n 1)
    echo -e "    ENV_NAME = ${CYAN}${ENV_NAME}${RESET}"

    SET_MODL=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.SETTINGS_MODULE)" 2>/dev/null | tail -n 1)
    echo -e "    SETTINGS_MODULE = ${CYAN}${SET_MODL}${RESET}"

    BASE_DIR=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.BASE_DIR)" 2>/dev/null | tail -n 1)
    echo -e "    BASE_DIR = ${CYAN}${BASE_DIR}${RESET}"

    TEMPL_DIRS=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.TEMPLATES[0]['DIRS'])" 2>/dev/null | tail -n 1)
    echo -e "    Template DIRS = ${CYAN}${TEMPL_DIRS}${RESET}"

    ENGINE=$($VENV_PY $MANAGE_PY shell -c "from django.template import engines; print(engines['django'].engine.dirs)" 2>/dev/null | tail -n 1)
    echo -e "    Engine: ${CYAN}${ENGINE}${RESET}"
    echo
done



# ---------------------------------------------------------
# [3] Socket / Runserver + Port Summary
# ---------------------------------------------------------
echo -e "\n${MAGENTA}[3] Socket / Runserver + Port Summary${RESET}"

# nginx FIRST (Option B)
echo -e "  nginx service status:"
if systemctl is-active --quiet nginx; then
    echo -e "    ${GREEN}✔ nginx service RUNNING${RESET}"
else
    echo -e "    ${RED}✖ nginx service NOT RUNNING${RESET}"
    ((FAIL++))
fi
echo

for ENV in "${ENVS[@]}"; do
    PORT=${PORTS[$ENV]}
    echo -e "  --- ${ENV} ---"
    echo -e "    Expected Port: ${CYAN}${PORT}${RESET}"

    if [[ "$ENV" == "dev" ]]; then
        echo -e "    Mode: ${CYAN}Django runserver${RESET}"
        if ss -tuln | grep -q ":${PORT}"; then
            echo -e "    ${GREEN}✔ runserver listening on ${PORT}${RESET}"
        else
            echo -e "    ${RED}✖ runserver NOT listening on ${PORT}${RESET}"
            ((FAIL++))
        fi
    else
        echo -e "    Mode: ${CYAN}Nginx → Gunicorn (socket)${RESET}"
        SOCK="/srv/django/MikesLists_${ENV}/MikesLists.sock"
        if [[ -S "$SOCK" ]]; then
            echo -e "    ${GREEN}✔ Socket found${RESET} (${SOCK})"
        else
            echo -e "    ${RED}✖ Socket MISSING${RESET} (${SOCK})"
            ((FAIL++))
        fi
    fi
done

# ---------------------------------------------------------
# [4] HTTP Endpoint Checks
# ---------------------------------------------------------
echo -e "\n${MAGENTA}[4] HTTP Endpoint Checks${RESET}"

for ENV in "${ENVS[@]}"; do
    URL="${URLS[$ENV]}"
    PORT=${PORTS[$ENV]}

    RESPONSE_DATA=$(curl -s -L -w "\n%{http_code}" "$URL")
    HTTP_BODY=$(echo "$RESPONSE_DATA" | sed '$d')
    HTTP_CODE=$(echo "$RESPONSE_DATA" | tail -n 1)

    EFFECTIVE_URL=$(curl -s -L -w "%{url_effective}" -o /dev/null "$URL")

    if [[ "$EFFECTIVE_URL" =~ ^https?://[^:/]+:([0-9]+) ]]; then
        REPORTED_PORT="${BASH_REMATCH[1]}"
    else
        REPORTED_PORT="80"
    fi

    if [[ "$REPORTED_PORT" == "$PORT" ]]; then
        echo -e "  ${ENV}: ${GREEN}✔ Port matches expected (${PORT})${RESET}"
    else
        echo -e "  ${ENV}: ${RED}✖ Port mismatch${RESET} (expected ${PORT}, got ${REPORTED_PORT})"
        ((FAIL++))
    fi

    if [ "$HTTP_CODE" == "200" ]; then
        if [[ "$HTTP_BODY" == *'"details":'* ]]; then
            echo -e "     ${GREEN}✔ 200 OK + New Code Active${RESET}"
            echo -e "        $(echo "$HTTP_BODY" | grep -oP '"details":\s*\{.*?\}' || echo 'Details key found but empty')"
        else
            echo -e "     ${YELLOW}⚠ 200 OK but OLD CODE detected${RESET}"
            ((WARN++))
        fi
    else
        echo -e "     ${RED}✖ HTTP $HTTP_CODE${RESET}"
        ((FAIL++))
    fi
done

# ---------------------------------------------------------
# [5] Server Header Identification
# ---------------------------------------------------------
echo -e "\n${MAGENTA}[5] Server Header Identification${RESET}"

for ENV in "${ENVS[@]}"; do
    URL="${URLS[$ENV]}"

    # Print environment label cleanly
    echo -e "  ${ENV}:"

    # Fetch Server header
    SERVER_HEADER=$(curl -sI "$URL" | grep -i "^Server:" | sed 's/Server:[ ]*//I')

    if [[ -z "$SERVER_HEADER" ]]; then
        echo -e "    ${RED}✖ No Server header returned${RESET}"
        ((FAIL++))
        continue
    fi

    # Identify server type
    if [[ "$SERVER_HEADER" == *"WSGIServer"* ]]; then
        echo -e "    ${GREEN}✔ Django runserver detected${RESET} (${CYAN}${SERVER_HEADER}${RESET})"
    elif [[ "$SERVER_HEADER" == *"nginx"* ]]; then
        echo -e "    ${GREEN}✔ Nginx detected${RESET} (${CYAN}${SERVER_HEADER}${RESET})"
    else
        echo -e "    ${YELLOW}⚠ Unknown server type${RESET} (${CYAN}${SERVER_HEADER}${RESET})"
        ((WARN++))
    fi
done


# ---------------------------------------------------------
# [6] Dependency Drift (Detailed)
# ---------------------------------------------------------
echo -e "\n${MAGENTA}[6] Dependency Drift (Detailed)${RESET}"

check_drift() {
    local FROM_ENV=$1
    local TO_ENV=$2

    echo -e "  Comparing ${FROM_ENV} → ${TO_ENV}"

    FROM_REQ=$(/srv/django/venv-${FROM_ENV}/bin/pip freeze | sort)
    TO_REQ=$(/srv/django/venv-${TO_ENV}/bin/pip freeze | sort)

    DIFF=$(diff <(echo "$FROM_REQ") <(echo "$TO_REQ"))

    if [[ -z "$DIFF" ]]; then
        echo -e "    ${GREEN}✔ No drift${RESET}"
        return
    fi

    echo -e "    ${YELLOW}⚠ Drift detected${RESET}"

    echo "$DIFF" | while read -r LINE; do
        case "$LINE" in
            \<\ *)
                PKG=$(echo "$LINE" | sed 's/^< //')
                echo -e "      ${RED}- Missing in ${TO_ENV}:${RESET} ${PKG}"
                ;;
            \>\ *)
                PKG=$(echo "$LINE" | sed 's/^> //')
                echo -e "      ${YELLOW}+ Extra in ${TO_ENV}:${RESET} ${PKG}"
                ;;
        esac
    done
    echo "run this line to do the updates: \n /srv/django/venv-dev/bin/pip freeze > /tmp/reqs.txt && /srv/django/venv-test/bin/pip install -r /tmp/reqs.txt"

}

check_drift "dev" "test"
check_drift "test" "live"

# ---------------------------------------------------------
# [7] System Health
# ---------------------------------------------------------
echo -e "\n${MAGENTA}[7] System Health${RESET}"

LOAD=$(uptime | awk -F'load average:' '{print $2}')
echo -e "  Load Averages (1, 5, 15 min):${CYAN}${LOAD}${RESET}"
echo -e "    Hint: On a 4‑core system, load < 4 means CPU is not saturated."
echo -e "          Values below 1 indicate the system is mostly idle."

echo -e "  Memory:"
echo -e "              total   used    free    shared  buff/cache  available"
free -h | awk '/^Mem:/ {
    printf "  Mem:      %-7s %-7s %-7s %-7s %-10s %-10s\n",$2,$3,$4,$5,$6,$7
}'

ZOMBIES=$(ps aux | awk '{ if ($8=="Z") print $0 }' | wc -l)
echo -e "  Zombies: ${CYAN}${ZOMBIES}${RESET}"
echo -e "    Hint: 0 is ideal; non-zero and growing means investigate."

# ---------------------------------------------------------
# [8] Permissions
# ---------------------------------------------------------
echo -e "\n${MAGENTA}[8] Permissions${RESET}"

for ENV in "${ENVS[@]}"; do
    ROOT="/srv/django/MikesLists_${ENV}"
    OWNER=$(stat -c "%U:%G" "$ROOT")

    if [[ "$OWNER" == "$EXPECTED_OWNER" ]]; then
        echo -e "  ${ENV}: ${GREEN}✔ Ownership correct${RESET} (${OWNER})"
    else
        echo -e "  ${ENV}: ${RED}✖ Ownership mismatch${RESET} (got ${OWNER}, expected ${EXPECTED_OWNER})"
        ((FAIL++))
    fi
done

# ---------------------------------------------------------
# [9] Git Repository Diagnostics
# ---------------------------------------------------------
echo -e "\n${MAGENTA}[9] Git Repository Diagnostics${RESET}"

for ENV in "${ENVS[@]}"; do
    ROOT="/srv/django/MikesLists_${ENV}"
    echo -e "  --- ${ENV} ---"
    if [[ ! -d "$ROOT/.git" ]]; then
        echo -e "    ${YELLOW}⚠ Not a Git repository${RESET} (${ROOT})"
        continue
    fi
    BRANCH=$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "UNKNOWN")
    echo -e "    Branch: ${CYAN}${BRANCH}${RESET}"
    CHANGES=$(git -C "$ROOT" status --porcelain)
    if [[ -z "$CHANGES" ]]; then
        echo -e "    ${GREEN}✔ Working tree clean${RESET}"
    else
        echo -e "    ${YELLOW}⚠ Pending changes:${RESET}"
        echo "$CHANGES" | sed 's/^/       /'
    fi
done

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------
echo -e "\n${MAGENTA}=========================================="
echo -e "                SUMMARY"
echo -e "==========================================${RESET}"

echo -e "${GREEN}✔ OK: ${OK}${RESET}  ${YELLOW}⚠ WARN: ${WARN}${RESET}  ${RED}✖ FAIL: ${FAIL}${RESET}"

if (( FAIL > 0 )); then
    echo -e "OVERALL STATUS: ${RED}FAIL${RESET}"
elif (( WARN > 0 )); then
    echo -e "OVERALL STATUS: ${YELLOW}WARN${RESET}"
else
    echo -e "OVERALL STATUS: ${GREEN}PASS${RESET}"
fi

echo -e "${MAGENTA}==========================================${RESET}"
