#!/bin/bash
# ==========================================
# Django Dashboard Summary
# ==========================================
# __version__="0.1.2.0-dev"

ENVS=("dev" "test" "live")

declare -A PORTS
PORTS["dev"]=8000
PORTS["test"]=9000
PORTS["live"]=80

declare -A URLS
URLS["dev"]="http://localhost:8000/health/"
URLS["test"]="http://localhost:9000/health/"
URLS["live"]="http://localhost/health/"

EXPECTED_OWNER="pi:www-data"

# Colors
GREEN=$'\033[32m'
RED=$'\033[31m'
YELLOW=$'\033[33m'
CYAN=$'\033[36m'
RESET=$'\033[0m'

# ANSI-safe padding
pad_color() {
    local text="$1"
    local width="$2"
    local plain=$(echo -e "$text" | sed 's/\x1b\[[0-9;]*m//g')
    local len=${#plain}
    local pad=$((width - len))
    (( pad < 0 )) && pad=0
    printf "%s%*s" "$text" $pad ""
}

# =========================
# Table 1: Per-environment
# =========================

printf "\n%-6s %-10s %-8s %-8s %-8s %-8s %-10s %-10s %-8s %-6s %-19s %-20s\n" \
"ENV" "SERVER" "PORT" "API" "DEBUG" "OWNER" "GIT" "BRANCH" "UPTIME" "DB" "DEPLOY" "STATUS"
echo "------------------------------------------------------------------------------------------------------------------------------------------------------"

for ENV in "${ENVS[@]}"; do
    PORT=${PORTS[$ENV]}
    URL="${URLS[$ENV]}"
    ROOT="/srv/django/MikesLists_${ENV}"
    VENV_PY="/srv/django/venv-${ENV}/bin/python"
    MANAGE_PY="${ROOT}/manage.py"
    ENV_FILE="${ROOT}/.env"

    # Load DB vars
    DB_HOST=$(grep -E '^DB_HOST=' "$ENV_FILE" | cut -d '=' -f2-)
    DB_PORT=$(grep -E '^DB_PORT=' "$ENV_FILE" | cut -d '=' -f2-)
    DB_USER=$(grep -E '^DB_USER=' "$ENV_FILE" | cut -d '=' -f2-)
    DB_PASSWORD=$(grep -E '^DB_PASSWORD=' "$ENV_FILE" | cut -d '=' -f2-)

    # Server type
    SERVER_HEADER=$(curl -sI "$URL" | grep -i "^Server:" | sed 's/Server:[ ]*//I')
    if [[ "$SERVER_HEADER" == *"WSGIServer"* ]]; then
        SERVER="RUNSERVER"
    elif [[ "$SERVER_HEADER" == *"nginx"* ]]; then
        SERVER="NGINX"
    else
        SERVER="UNKNOWN"
    fi

    # API
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
    if [[ "$HTTP_CODE" == "200" ]]; then
        API_COLOR="${GREEN}OK${RESET}"
        API_BAD=0
    else
        API_COLOR="${RED}BAD${RESET}"
        API_BAD=1
    fi

    # DEBUG
    DEBUG_STATUS=$($VENV_PY "$MANAGE_PY" shell -c "from django.conf import settings; print(settings.DEBUG)" 2>/dev/null)
    if [[ "$DEBUG_STATUS" == "True" ]]; then
        if [[ "$ENV" == "live" ]]; then
            DEBUG_COLOR="${RED}BAD${RESET}"
            DEBUG_BAD=1
        else
            DEBUG_COLOR="${YELLOW}DEV${RESET}"
            DEBUG_BAD=0
        fi
    else
        DEBUG_COLOR="${GREEN}OK${RESET}"
        DEBUG_BAD=0
    fi

    # OWNER
    OWNER_VAL=$(stat -c "%U:%G" "$ROOT")
    if [[ "$OWNER_VAL" == "$EXPECTED_OWNER" ]]; then
        OWNER_COLOR="${GREEN}OK${RESET}"
        OWNER_BAD=0
    else
        OWNER_COLOR="${RED}BAD${RESET}"
        OWNER_BAD=1
    fi

    # GIT CLEAN/DIRTY
    if [[ -d "$ROOT/.git" ]]; then
        CHANGES=$(git -C "$ROOT" status --porcelain)
        if [[ -z "$CHANGES" ]]; then
            GIT_COLOR="${GREEN}CLEAN${RESET}"
        else
            GIT_COLOR="${YELLOW}DIRTY${RESET}"
        fi
    else
        GIT_COLOR="${YELLOW}-${RESET}"
    fi

    # BRANCH
    if [[ -d "$ROOT/.git" ]]; then
        BRANCH=$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null)
        [[ -z "$BRANCH" ]] && BRANCH="-"
        BRANCH_COLOR="${CYAN}${BRANCH}${RESET}"
    else
        BRANCH_COLOR="${YELLOW}-${RESET}"
    fi

    # Uptime
    RAW_UP=$(uptime -p | sed 's/up //')
    UPTIME=$(echo "$RAW_UP" | sed -E 's/ hours?/h/; s/ minutes?/m/; s/, //g')

    # DB ping (simple OK/BAD)
    if mariadb -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" --password="$DB_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
        DB_COLOR="${GREEN}OK${RESET}"
    else
        DB_COLOR="${RED}BAD${RESET}"
    fi

    # Deploy timestamp
    DEPLOY_TS=$(stat -c %y "$MANAGE_PY" 2>/dev/null | cut -d'.' -f1)

    # STATUS
    if [[ "$API_COLOR" == *"BAD"* ]] || [[ "$DEBUG_COLOR" == *"BAD"* ]] || [[ "$OWNER_COLOR" == *"BAD"* ]] || [[ "$DB_COLOR" == *"BAD"* ]]; then
        STATUS="${RED}FAIL${RESET}"
    elif [[ "$GIT_COLOR" == *"DIRTY"* ]] || [[ "$DEBUG_COLOR" == *"DEV"* ]]; then
        STATUS="${YELLOW}WARN${RESET}"
    else
        STATUS="${GREEN}PASS${RESET}"
    fi

    # Print row
    printf "%-6s %-10s %-8s %s %s %s %s %s %-8s %s %-19s %b\n" \
        "$ENV" "$SERVER" ":$PORT" \
        "$(pad_color "$API_COLOR" 8)" \
        "$(pad_color "$DEBUG_COLOR" 8)" \
        "$(pad_color "$OWNER_COLOR" 8)" \
        "$(pad_color "$GIT_COLOR" 10)" \
        "$(pad_color "$BRANCH_COLOR" 10)" \
        "$UPTIME" \
        "$(pad_color "$DB_COLOR" 6)" \
        "$DEPLOY_TS" \
        "$STATUS"

done

echo

# =========================
# Table 2: NODE HEALTH
# =========================

NODE_NAME=$(hostname)
NODE_IP=$(hostname -I | awk '{print $1}')

# Disk usage
DISK_PCT=$(df -h / | awk 'NR==2 {gsub("%","",$5); print $5}')
if (( DISK_PCT < 70 )); then
    DISK_COLOR="${GREEN}${DISK_PCT}%${RESET}"
elif (( DISK_PCT < 90 )); then
    DISK_COLOR="${YELLOW}${DISK_PCT}%${RESET}"
else
    DISK_COLOR="${RED}${DISK_PCT}%${RESET}"
fi

# Temperature
if [[ -r /sys/class/thermal/thermal_zone0/temp ]]; then
    RAW_TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
    TEMP_C=$(awk "BEGIN {printf \"%.1f\", $RAW_TEMP/1000}")
    if (( ${TEMP_C%.*} < 60 )); then
        TEMP_COLOR="${GREEN}${TEMP_C}°C${RESET}"
    elif (( ${TEMP_C%.*} < 75 )); then
        TEMP_COLOR="${YELLOW}${TEMP_C}°C${RESET}"
    else
        TEMP_COLOR="${RED}${TEMP_C}°C${RESET}"
    fi
else
    TEMP_COLOR="${YELLOW}-${RESET}"
fi

# MariaDB ping
DB_PING="-"
if ping -c 1 -W 1 "$DB_HOST" >/dev/null 2>&1; then
    AVG=$(ping -c 5 -W 1 "$DB_HOST" | awk -F'/' 'END {print $5}')
    DB_PING="${GREEN}${AVG}ms${RESET}"
fi

# Gateway ping
GW_PING="-"
GW=$(ping -c 5 -W 1 10.0.0.1 2>/dev/null | awk -F'/' 'END {print $5}')
if [[ -n "$GW" ]]; then
    GW_PING="${GREEN}${GW}ms${RESET}"
fi

# Print NODE HEALTH table
printf "%-10s %-12s %-15s %-10s %-10s %-10s\n" \
"NODE" "HOSTNAME" "IP" "DISK" "TEMP" "PING"
echo "-----------------------------------------------------------------------------------------"

# Row 1: Pi
printf "%-10s %-12s %-15s %s %s %s\n" \
"pi80" "$NODE_NAME" "$NODE_IP" \
"$(pad_color "$DISK_COLOR" 10)" \
"$(pad_color "$TEMP_COLOR" 10)" \
"-"

# Row 2: MariaDB
printf "%-10s %-12s %-15s %-10s %-10s %s\n" \
"MariaDB" "Pi240" "$DB_HOST" \
"-" "-" \
"$(pad_color "$DB_PING" 10)"

# Row 3: Gateway
printf "%-10s %-12s %-15s %-10s %-10s %s\n" \
"gateway" "gateway" "10.0.0.1" \
"-" "-" \
"$(pad_color "$GW_PING" 10)"

echo
