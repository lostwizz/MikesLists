#!/bin/bash
# ==========================================
# Django Health Check - Magenta Edition v3.2
# ==========================================
# __version__ = "0.1.0.000048-dev"


ENVS=("dev" "test" "live")
SERVICES=("mikeslists-dev" "gunicorn-MikesLists-test" "gunicorn-MikesLists-live" "nginx")

declare -A URLS
URLS["dev"]="http://localhost:8000/health/"
URLS["test"]="http://localhost:9000/health/"
URLS["live"]="http://localhost:80/health/"

# Colors
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
MAGENTA="\e[35m"
RESET="\e[0m"

OK_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

echo -e "${MAGENTA}=========================================="
echo -e "        Django Environment Health Check"
echo -e "==========================================${RESET}"

# [1] Service Status
echo -e "\n${MAGENTA}[1] Service Status:${RESET}"
for SVC in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$SVC"; then
        echo -e "  ${GREEN}✔ $SVC is RUNNING${RESET}"
        ((OK_COUNT++))
    else
        echo -e "  ${RED}✖ $SVC is NOT RUNNING${RESET}"
        ((FAIL_COUNT++))
    fi
done

# [2] Environment Integrity & DEBUG Check
echo -e "\n${MAGENTA}[2] Environment & Settings Verification:${RESET}"
for ENV in "${ENVS[@]}"; do
    echo -e "  --- ${ENV} ---"
    VENV_PY="/srv/django/venv-${ENV}/bin/python"
    MANAGE_PY="/srv/django/MikesLists_${ENV}/manage.py"

    # 1. Verify Python Interpreter
    ACTUAL_PY=$($VENV_PY -c "import sys; print(sys.executable)" 2>/dev/null)
    if [[ "$ACTUAL_PY" == *"/venv-${ENV}/"* ]]; then
        echo -e "    Python:   ${GREEN}✔ Correct${RESET}"
    else
        echo -e "    Python:   ${RED}✖ MISMATCH${RESET} ($ACTUAL_PY)"
    fi

    # 2. Verify Settings Module
    ACTIVE_SETTING=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.SETTINGS_MODULE)" 2>/dev/null | tail -n 1)

    if [[ "$ACTIVE_SETTING" == *"$ENV"* ]]; then
        echo -e "    Settings: ${GREEN}✔ Correct${RESET} ($ACTIVE_SETTING)"
        ((OK_COUNT++))
    else
        echo -e "    Settings: ${RED}✖ WRONG MODULE${RESET} ($ACTIVE_SETTING)"
        ((FAIL_COUNT++))
    fi

    # 3. Explicit DEBUG Check
    DEBUG_STATUS=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.DEBUG)" 2>/dev/null | tail -n 1)

    if [[ "$DEBUG_STATUS" == "True" ]]; then
        if [[ "$ENV" == "live" ]]; then
            echo -e "    DEBUG:    ${RED}✖ TRUE (Security Risk!)${RESET}"
            ((FAIL_COUNT++))
        else
            echo -e "    DEBUG:    ${YELLOW}⚠ True (Standard for Dev)${RESET}"
            ((WARN_COUNT++))
        fi
    else
        echo -e "    DEBUG:    ${GREEN}✔ False${RESET}"
        ((OK_COUNT++))
    fi

    ENV_NAME=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.ENV_NAME)" 2>/dev/null | tail -n 1)
    echo -e "    ENV_NAME = ${ENV_NAME}"

    SET_MODL=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.SETTINGS_MODULE)" 2>/dev/null | tail -n 1)
    echo -e "    SETTINGS_MODULE = ${SET_MODL}"
    BASE_DIR=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.BASE_DIR)" 2>/dev/null | tail -n 1)
    echo -e "    BASE_DIR = ${BASE_DIR}"
    TEMPL_DIRS=$($VENV_PY $MANAGE_PY shell -c "from django.conf import settings; print(settings.TEMPLATES[0]['DIRS'])" 2>/dev/null | tail -n 1)
    echo -e "    Template DIRS = ${TEMPL_DIRS}"
    ENGINE=$($VENV_PY $MANAGE_PY shell -c "from django.template import engines; print(engines['django'].engine.dirs)" 2>/dev/null | tail -n 1)
    echo -e "    Engine: ${ENGINE}"
    echo -e
done

# [3] Socket Verification
echo -e "\n${MAGENTA}[3] Socket Verification:${RESET}"
for ENV in "${ENVS[@]}"; do

    # DEV uses runserver → no socket expected
    if [[ "$ENV" == "dev" ]]; then
        echo -e "  ${YELLOW}⚠ dev uses runserver — skipping socket check${RESET}"
        ((WARN_COUNT++))
        continue
    fi

    # TEST + LIVE use Gunicorn sockets
    SOCK="/srv/django/MikesLists_${ENV}/MikesLists.sock"
    if [ -S "$SOCK" ]; then
        echo -e "  ${GREEN}✔ $ENV Socket Found${RESET}"
        ((OK_COUNT++))
    else
        echo -e "  ${RED}✖ $ENV Socket MISSING${RESET} ($SOCK)"
        ((FAIL_COUNT++))
    fi
done



# Add to chk.sh
LOG_FILE="/srv/django/MikesLists_dev/logs/debug.log"
MAX_SIZE=500000000 # 500MB
if [ -f "$LOG_FILE" ]; then
    SIZE=$(stat -c%s "$LOG_FILE")
    if [ "$SIZE" -gt "$MAX_SIZE" ]; then
        echo -e "  ${YELLOW}⚠ Log file too large: $(du -h $LOG_FILE | awk '{print $1}')${RESET}"
        ((WARN_COUNT++))
    fi
fi


# [4] HTTP Endpoint Checks (Enforcing Detailed JSON)
echo -e "\n${MAGENTA}[4] HTTP Endpoint Checks:${RESET}"
for ENV in "${ENVS[@]}"; do
    URL="${URLS[$ENV]}"
    RESPONSE_DATA=$(curl -s -L -w "\n%{http_code}" "$URL")
    HTTP_BODY=$(echo "$RESPONSE_DATA" | sed '$d')
    HTTP_CODE=$(echo "$RESPONSE_DATA" | tail -n 1)

    if [ "$HTTP_CODE" == "200" ]; then
        # Check for the NEW 'details' key to prove the code is updated
        if [[ "$HTTP_BODY" == *'"details":'* ]]; then
            echo -e "  ${GREEN}✔ $ENV (200 OK + New Code Active)${RESET}"
            # Extract and print just the details for quick viewing
            echo -e "     $(echo "$HTTP_BODY" | grep -oP '"details":\s*\{.*?\}' || echo 'Details key found but empty')"
            ((OK_COUNT++))
        else
            echo -e "  ${YELLOW}⚠ $ENV (200 OK but OLD CODE detected)${RESET}"
            echo "     Body: $HTTP_BODY"
            ((WARN_COUNT++))
        fi
    else
        echo -e "  ${RED}✖ $ENV (HTTP $HTTP_CODE)${RESET}"
        ((FAIL_COUNT++))
    fi
done


echo -e "\n${MAGENTA}[4.5] Server Header Identification:${RESET}"
for ENV in "${ENVS[@]}"; do
    URL="${URLS[$ENV]}"

    echo -ne "  ${ENV}: "

    # Fetch only headers, extract the Server: line
    SERVER_HEADER=$(curl -sI "$URL" | grep -i "^Server:" | sed 's/Server:[ ]*//I')

    if [[ -z "$SERVER_HEADER" ]]; then
        echo -e "${RED}✖ No Server header returned${RESET}"
        ((FAIL_COUNT++))
        continue
    fi

    # Identify server type
    if [[ "$SERVER_HEADER" == *"WSGIServer"* ]]; then
        echo -e "${GREEN}✔ Django runserver detected${RESET} (${SERVER_HEADER})"
        ((OK_COUNT++))

    elif [[ "$SERVER_HEADER" == *"nginx"* ]]; then
        echo -e "${GREEN}✔ Nginx detected${RESET} (${SERVER_HEADER})"
        ((OK_COUNT++))

    else
        echo -e "${YELLOW}⚠ Unknown server type${RESET} (${SERVER_HEADER})"
        ((WARN_COUNT++))
    fi
done


# [5] Django Deployment Check
echo -e "\n${MAGENTA}[5] Django Security Check (--deploy):${RESET}"
for ENV in "${ENVS[@]}"; do
    echo -ne "  --- ${ENV} --- "
    CHECK_OUT=$(/srv/django/venv-${ENV}/bin/python /srv/django/MikesLists_${ENV}/manage.py check --deploy 2>&1)

    if [[ "$CHECK_OUT" == *"System check identified no issues"* ]]; then
        echo -e "${GREEN}✔ Clean${RESET}"
        ((OK_COUNT++))
    else
        if [[ "$CHECK_OUT" == *"ERRORS:"* ]]; then
            echo -e "${RED}✖ ERRORS FOUND${RESET}"
            ((FAIL_COUNT++))
        else
            echo -e "${YELLOW}⚠ Warnings Exist${RESET}"
            ((WARN_COUNT++))
        fi
    fi
done

# Git Repository Diagnostics
echo -e "\n${MAGENTA}=========================================="
echo "        Git Repository Diagnostics"
echo -e "==========================================${RESET}"

check_git_repo() {
    local env_name="$1"
    local root="$2"
    echo -e "\n  --- $env_name ---"
    if [[ ! -d "$root/.git" ]]; then
        echo "    ⚠ Not a Git repository ($root)"
        return
    fi
    branch=$(git -C "$root" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "UNKNOWN")
    echo "    ✔ Branch: $branch"
    changes=$(git -C "$root" status --porcelain)
    if [[ -z "$changes" ]]; then
        echo "    ✔ Working tree clean"
    else
        echo "    ⚠ Pending changes detected:"
        echo "$changes" | sed 's/^/       /'
    fi
}

check_git_repo "dev"  "/srv/django/MikesLists_dev"
check_git_repo "test" "/srv/django/MikesLists_test"
check_git_repo "live" "/srv/django/MikesLists_live"

# Final Summary
echo -e "\n${MAGENTA}=========================================="
echo -e "                SUMMARY"
echo -e "==========================================${RESET}"
echo -e "${GREEN}✔ OK: $OK_COUNT${RESET}  ${YELLOW}⚠ WARN: $WARN_COUNT${RESET}  ${RED}✖ FAIL: $FAIL_COUNT${RESET}"

if (( FAIL_COUNT > 0 )); then
    echo -e "OVERALL STATUS: ${RED}FAIL${RESET}"
elif (( WARN_COUNT > 0 )); then
    echo -e "OVERALL STATUS: ${YELLOW}WARN${RESET}"
else
    echo -e "OVERALL STATUS: ${GREEN}PASS${RESET}"
fi
echo -e "${MAGENTA}==========================================${RESET}"
