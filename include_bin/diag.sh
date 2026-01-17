#!/bin/bash
# ==========================================
# Django Deep Diagnostic Tool v2.1 (verbose)
# ==========================================
# __version__="2.2.2"

#############################################
# COLORS (ANSI-safe)
#############################################
RED=$'\033[31m'
GREEN=$'\033[32m'
YELLOW=$'\033[33m'
BLUE=$'\033[34m'
CYAN=$'\033[36m'
MAGENTA=$'\033[35m'
RESET=$'\033[0m'

#############################################
# DEFAULTS
#############################################
ENV="dev"
FAIL_FAST=false
RUN_ALL=true
declare -A RUN_SECTION

#############################################
# HELP TEXT
#############################################
show_help() {
    echo -e "${CYAN}Django Deep Diagnostic Tool v2.1 (verbose)${RESET}"
    echo
    echo "Usage:"
    echo "  diag.sh [environment] [options]"
    echo
    echo "Environments:"
    echo "  dev (default), test, live"
    echo
    echo "Options:"
    echo "  --all              Run all diagnostics (default)"
    echo "  --fail-fast        Stop on first failure"
    echo " "
    echo "  --environment      Only run environment diagnostics"
    echo "  --gunicorn         Only run Gunicorn diagnostics"
    echo "  --django           Only run Django diagnostics"
    echo "  --ruff             Only run Ruff diagnostics"
    echo "  --flake            Only run flake8 diagnostics"
    echo "  --lint             Only run Lint (ruff and flake)"
    echo "  --static           Only run statics diagnostics"
    echo "  --db               Only run database diagnostics"
    echo "  --check_tests      Only run python test scripts"
    echo "  --nginx            Only run Nginx diagnostics"
    echo "  --git              Only run Git diagnostics"
    echo "  --env              Only validate environment variables"
    echo "  --permissions      Only check file permissions"
    echo "  --packages         Only check Python packages"
    echo "  --help             Show this help and exit"
    echo
}

#############################################
# ARGUMENT PARSING
#############################################
for arg in "$@"; do
    case "$arg" in
        dev|test|live)
            ENV="$arg"
            ;;
        --fail-fast)
            FAIL_FAST=true
            ;;
        --all)
            RUN_ALL=true
            ;;
        --gunicorn|--django|--db|--nginx|--git|--env|--permissions|--packages|--lint|--static|--environment|--check_tests)
            RUN_ALL=false
            RUN_SECTION["$arg"]=true
            ;;
        --ruff|--flake|--lint|--static)
            RUN_ALL=false
            RUN_SECTION["$arg"]=true
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown argument: $arg${RESET}"
            show_help
            exit 1
            ;;
    esac
done

#############################################
# PATHS
#############################################
PROJECT_PATH="/srv/django/MikesLists_${ENV}"
VENV_PATH="/srv/django/venv-${ENV}"
MANAGE="$VENV_PATH/bin/python $PROJECT_PATH/manage.py"
ENV_FILE="$PROJECT_PATH/.env"


#############################################
# VERBOSE COMMAND RUNNER
#############################################
run_cmd() {
    local label="$1"
    shift
    local cmd=( "$@" )

    echo -e "${BLUE}running:${RESET} ${CYAN}${cmd[*]}${RESET}"
    local OUTPUT
    OUTPUT=$("${cmd[@]}" 2>&1)
    local STATUS=$?

    if [[ $STATUS -ne 0 ]]; then
        echo -e "${RED}✖ ${label} failed (exit ${STATUS})${RESET}"
        echo -e "${YELLOW}output:${RESET}"
        echo "$OUTPUT"
        return $STATUS
    else
        echo -e "${GREEN}✔ ${label} succeeded${RESET}"
        return 0
    fi
}

#############################################
# SECTION EXECUTION WRAPPER
#############################################
run_section() {
    local name="$1"
    local func="$2"

    if $RUN_ALL || [[ ${RUN_SECTION["--$name"]} == true ]]; then
        echo -e "\n${MAGENTA}=== [$name] --> use --$name =========================================${RESET}"
        $func
        local status=$?

        if [[ $status -ne 0 ]]; then
            echo -e "${RED}****** section results — [$name] failed ******${RESET}"
            if $FAIL_FAST; then
                echo -e "${RED}fail-fast enabled. stopping.${RESET}"
                exit 1
            fi
        else
            echo -e "${GREEN}****** section results — [$name] passed ******${RESET}"
        fi

        return $status
    fi

    return 0
}


#############################################
# SECTION 2 — Environment Validation
#############################################
validate_environment() {

    echo -e "${CYAN}validating environment: ${ENV}${RESET}"

    local fail=false

    echo -e "${BLUE}checking project directory:${RESET} $PROJECT_PATH"
    if [[ ! -d "$PROJECT_PATH" ]]; then
        echo -e "${RED}✖ missing project directory${RESET}"
        fail=true
    else
        echo -e "${GREEN}✔ project directory exists${RESET}"
    fi

    echo -e "${BLUE}checking virtualenv:${RESET} $VENV_PATH"
    if [[ ! -d "$VENV_PATH" ]]; then
        echo -e "${RED}✖ missing virtualenv${RESET}"
        fail=true
    else
        echo -e "${GREEN}✔ virtualenv exists${RESET}"
    fi

    echo -e "${BLUE}checking python binary:${RESET} $VENV_PATH/bin/python"
    if [[ ! -x "$VENV_PATH/bin/python" ]]; then
        echo -e "${RED}✖ python binary missing or not executable${RESET}"
        fail=true
    else
        echo -e "${GREEN}✔ python binary found${RESET}"
    fi

    echo -e "${BLUE}checking manage.py:${RESET} $PROJECT_PATH/manage.py"
    if [[ ! -f "$PROJECT_PATH/manage.py" ]]; then
        echo -e "${RED}✖ manage.py missing${RESET}"
        fail=true
    else
        echo -e "${GREEN}✔ manage.py found${RESET}"
    fi

    echo -e "${BLUE}checking .env:${RESET} $ENV_FILE"
    if [[ ! -f "$ENV_FILE" ]]; then
        echo -e "${RED}✖ .env missing${RESET}"
        fail=true
    else
        echo -e "${GREEN}✔ .env found${RESET}"
    fi

    $fail && return 1 || return 0
}

#############################################
# SECTION 3 — Gunicorn (skipped in dev)
#############################################
check_gunicorn() {

    if [[ "$ENV" == "dev" ]]; then
        echo -e "${YELLOW}skipping gunicorn — dev uses runserver${RESET}"
        return 0
    fi

    local SERVICE="gunicorn-MikesLists-${ENV}.service"
    local fail=false

    echo -e "${BLUE}checking systemd unit:${RESET} $SERVICE"
    if ! systemctl list-unit-files | grep -q "$SERVICE"; then
        echo -e "${RED}✖ gunicorn service not found${RESET}"
        return 1
    fi
    echo -e "${GREEN}✔ gunicorn service exists${RESET}"

    echo -e "${BLUE}checking systemctl state:${RESET}"
    STATE=$(systemctl is-active "$SERVICE")
    SUBSTATE=$(systemctl show -p SubState --value "$SERVICE")
    echo -e "  state: ${CYAN}$STATE${RESET}"
    echo -e "  substate: ${CYAN}$SUBSTATE${RESET}"
    [[ "$STATE" != "active" ]] && echo -e "${RED}✖ gunicorn not active${RESET}" && fail=true

    echo -e "${BLUE}checking restart count:${RESET}"
    RESTARTS=$(systemctl show "$SERVICE" -p NRestarts --value)
    echo -e "  restarts: ${CYAN}$RESTARTS${RESET}"
    (( RESTARTS > 3 )) && echo -e "${RED}✖ restart loop detected${RESET}" && fail=true

    echo -e "${BLUE}checking worker processes:${RESET}"
    WORKERS=$(pgrep -f "gunicorn.*MikesLists_${ENV}" | wc -l)
    echo -e "  workers: ${CYAN}$WORKERS${RESET}"
    (( WORKERS == 0 )) && echo -e "${RED}✖ no workers running${RESET}" && fail=true

    echo -e "${BLUE}checking master processes:${RESET}"
    MASTERS=$(pgrep -f "gunicorn.*master.*MikesLists_${ENV}" | wc -l)
    echo -e "  masters: ${CYAN}$MASTERS${RESET}"
    (( MASTERS > 1 )) && echo -e "${RED}✖ multiple masters detected${RESET}" && fail=true

    echo -e "${BLUE}checking socket:${RESET} /run/gunicorn.sock"
    [[ -S "/run/gunicorn.sock" ]] && echo -e "${GREEN}✔ socket exists${RESET}" || echo -e "${YELLOW}⚠ socket missing (maybe using TCP)${RESET}"

    echo -e "${BLUE}recent logs:${RESET}"
    sudo journalctl -u "$SERVICE" -n 20 --no-pager | sed \
        -e "s/error/${RED}error${RESET}/Ig" \
        -e "s/warning/${YELLOW}warning${RESET}/Ig"

    $fail && return 1 || return 0
}


#############################################
# SECTION 4 — Django Diagnostics
#############################################
check_django() {

    echo -e "${CYAN}running django diagnostics${RESET}"

    local fail=false

    echo -e "\n${YELLOW}[1] manage.py check${RESET}"
    run_cmd "manage.py check" \
        $VENV_PATH/bin/python "$PROJECT_PATH/manage.py" check
    [[ $? -ne 0 ]] && fail=true


    echo -e "\n${YELLOW}[1.5] manage.py check --deploy${RESET}"
    run_cmd "manage.py check" \
        $VENV_PATH/bin/python "$PROJECT_PATH/manage.py" check --deploy
    [[ $? -ne 0 ]] && fail=true




    echo -e "\n${YELLOW}[2] python syntax scan${RESET}"
    SYNTAX_ERRORS=0
    while IFS= read -r -d '' file; do
        echo -e "${BLUE}compiling:${RESET} $file"
        $VENV_PATH/bin/python -m py_compile "$file" 2>&1 || {
            echo -e "${RED}✖ syntax error:${RESET} $file"
            ((SYNTAX_ERRORS++))
        }
    done < <(find "$PROJECT_PATH" -name '*.py' -print0)

    if (( SYNTAX_ERRORS == 0 )); then
        echo -e "${GREEN}✔ no syntax errors${RESET}"
    else
        echo -e "${RED}✖ $SYNTAX_ERRORS python files contain syntax errors${RESET}"
        fail=true
    fi

    echo -e "\n${YELLOW}[3] migration status${RESET}"
    MIG=$($MANAGE showmigrations 2>&1)
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}✖ showmigrations failed${RESET}"
        echo "$MIG"
        fail=true
    else
        UNAPPLIED=$(echo "$MIG" | grep '\[ \]' | wc -l)
        if (( UNAPPLIED > 0 )); then
            echo -e "${YELLOW}⚠ unapplied migrations:${RESET}"
            echo "$MIG" | grep '\[ \]'
            fail=true
        else
            echo -e "${GREEN}✔ all migrations applied${RESET}"
        fi
    fi

    echo -e "\n${YELLOW}[4] checking staticfiles_collected${RESET}"
    STATIC_DIR="$PROJECT_PATH/staticfiles_collected"
    if [[ -d "$STATIC_DIR" ]]; then
        echo -e "${GREEN}✔ staticfiles_collected exists${RESET}"
    else
        echo -e "${YELLOW}⚠ staticfiles_collected missing — run collectstatic${RESET}"
    fi

    $fail && return 1 || return 0
}




#############################################
# SECTION 5 — Git Inspection
#############################################
check_git() {

    echo -e "${CYAN}checking git repository${RESET}"

    local fail=false

    # 1. Ensure .git exists
    if [[ ! -d "$PROJECT_PATH/.git" ]]; then
        echo -e "${YELLOW}⚠ no git repository found in project${RESET}"
        return 0
    fi

    # 2. Current branch
    echo -e "${BLUE}reading current branch:${RESET}"
    BRANCH=$(git -C "$PROJECT_PATH" rev-parse --abbrev-ref HEAD 2>&1)
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}✖ cannot determine git branch${RESET}"
        echo "$BRANCH"
        fail=true
    else
        echo -e "${GREEN}✔ branch:${RESET} ${CYAN}$BRANCH${RESET}"
    fi

    # 3. Working tree status
    echo -e "${BLUE}checking working tree status:${RESET}"
    CHANGES=$(git -C "$PROJECT_PATH" status --porcelain)
    if [[ -z "$CHANGES" ]]; then
        echo -e "${GREEN}✔ working tree clean${RESET}"
    else
        echo -e "${YELLOW}⚠ working tree has changes:${RESET}"
        echo "$CHANGES"
    fi

    # 4. Untracked files
    echo -e "${BLUE}checking untracked files:${RESET}"
    UNTRACKED=$(git -C "$PROJECT_PATH" ls-files --others --exclude-standard)
    if [[ -z "$UNTRACKED" ]]; then
        echo -e "${GREEN}✔ no untracked files${RESET}"
    else
        echo -e "${YELLOW}⚠ untracked files:${RESET}"
        echo "$UNTRACKED"
    fi

    # 5. Staged but uncommitted changes
    echo -e "${BLUE}checking staged changes:${RESET}"
    STAGED=$(git -C "$PROJECT_PATH" diff --cached --name-only)
    if [[ -z "$STAGED" ]]; then
        echo -e "${GREEN}✔ no staged changes${RESET}"
    else
        echo -e "${YELLOW}⚠ staged but uncommitted changes:${RESET}"
        echo "$STAGED"
    fi

    # 6. Last commit info
    echo -e "${BLUE}reading last commit:${RESET}"
    HASH=$(git -C "$PROJECT_PATH" rev-parse HEAD 2>/dev/null)
    if [[ -z "$HASH" ]]; then
        echo -e "${RED}✖ cannot read last commit${RESET}"
        fail=true
    else
        LAST_AUTHOR=$(git -C "$PROJECT_PATH" log -1 --pretty='%an')
        LAST_DATE=$(git -C "$PROJECT_PATH" log -1 --pretty='%ad' --date=local)
        LAST_MSG=$(git -C "$PROJECT_PATH" log -1 --pretty='%B')

        echo -e "  hash:   ${CYAN}$HASH${RESET}"
        echo -e "  author: ${CYAN}$LAST_AUTHOR${RESET}"
        echo -e "  date:   ${CYAN}$LAST_DATE${RESET}"
        echo -e "  msg:    ${CYAN}$LAST_MSG${RESET}"
    fi

    $fail && return 1 || return 0
}



#############################################
# SECTION 6 — Database Connectivity
#############################################
check_db() {

    echo -e "${CYAN}checking database connectivity${RESET}"

    local fail=false

    echo -e "${BLUE}loading DB settings from .env${RESET}"

    DB_ENGINE=$(grep -E '^DB_ENGINE=' "$ENV_FILE" | cut -d '=' -f2-)
    DB_HOST=$(grep -E '^DB_HOST=' "$ENV_FILE" | cut -d '=' -f2-)
    DB_PORT=$(grep -E '^DB_PORT=' "$ENV_FILE" | cut -d '=' -f2-)
    DB_USER=$(grep -E '^DB_USER=' "$ENV_FILE" | cut -d '=' -f2-)
    DB_PASSWORD=$(grep -E '^DB_PASSWORD=' "$ENV_FILE" | cut -d '=' -f2-)
    DB_NAME=$(grep -E '^DB_NAME=' "$ENV_FILE" | cut -d '=' -f2-)

    echo -e "  DB_ENGINE=${CYAN}${DB_ENGINE:-<not in .env>}${RESET}"
    echo -e "  DB_HOST=${CYAN}${DB_HOST:-<missing>}${RESET}"
    echo -e "  DB_PORT=${CYAN}${DB_PORT:-<missing>}${RESET}"
    echo -e "  DB_USER=${CYAN}${DB_USER:-<missing>}${RESET}"
    echo -e "  DB_PASSWORD=${CYAN}${DB_PASSWORD:+********}${RESET}"
    echo -e "  DB_NAME=${CYAN}${DB_NAME:-<missing>}${RESET}"

    # Required vars
    for var in DB_HOST DB_PORT DB_USER DB_PASSWORD DB_NAME; do
        if [[ -z "${!var}" ]]; then
            echo -e "${RED}✖ missing required DB variable: $var${RESET}"
            fail=true
        fi
    done

    # Determine DB engine if missing
    if [[ -z "$DB_ENGINE" ]]; then
        echo -e "${BLUE}DB_ENGINE not in .env — reading from Django settings${RESET}"
        DB_ENGINE=$($MANAGE shell -c "from django.conf import settings; print(settings.DATABASES['default']['ENGINE'])" 2>&1)
        if [[ $? -ne 0 ]]; then
            echo -e "${YELLOW}⚠ cannot read DB engine from Django settings${RESET}"
        else
            echo -e "${GREEN}✔ DB engine from settings:${RESET} $DB_ENGINE"
        fi
    else
        echo -e "${GREEN}✔ DB engine from .env:${RESET} $DB_ENGINE"
    fi

    echo -e "${YELLOW}note:${RESET} django.db.backends.mysql is a python module, not a file — correct for MariaDB"

    #############################################
    # 3. Ping DB host
    #############################################
    echo -e "\n${YELLOW}[2] ping DB host${RESET}"
    echo -e "${BLUE}running:${RESET} ping -c 1 -W 1 \"$DB_HOST\""

    if ping -c 1 -W 1 "$DB_HOST" >/dev/null 2>&1; then
        echo -e "${GREEN}✔ ping successful${RESET}"
    else
        echo -e "${RED}✖ cannot reach DB host: $DB_HOST${RESET}"
        fail=true
    fi

    #############################################
    # 2. Django ensure_connection()
    #############################################
    echo -e "\n${YELLOW}[1] django ensure_connection test${RESET}"
    echo -e "${BLUE}running:${RESET} $MANAGE  shell -c 'from django.db import connection; connection.ensure_connection(); print(\"OK\")'"

    DB_OUTPUT=$( $MANAGE shell -c "from django.db import connection; connection.ensure_connection(); print('OK')" 2>&1  )
    echo "${BLUE}  will remove   'objects imported automatically' ${RESET}"
    echo "${CYAN}raw output: ${DB_OUTPUT} ${RESET}"

    DB_OUTPUT=$(
        $MANAGE shell -c "from django.db import connection; connection.ensure_connection(); print('OK')" 2>&1 \
        | grep -v "objects imported automatically"
    )
    if echo "$DB_OUTPUT" | grep -q "OK"; then
        echo -e "${GREEN}✔ django connected successfully${RESET}"
    else
        echo -e "${RED}✖ django failed to connect to the database${RESET}"
        echo -e "${YELLOW}reason (exception from Django):${RESET}"
        echo "$DB_OUTPUT"
        fail=true
    fi

    $fail && return 1 || return 0
}



#############################################
# SECTION 6.5 — python test code
#############################################
check_tests() {
    echo -e "${CYAN}checking python tests${RESET}"

    local fail=false

    echo -e "\n${YELLOW}[1] manage.py test --noinput -v 3 --debug-mode --debug-sql --shuffle ${RESET}"
    echo "--- Running Django Tests ---"
    run_cmd "manage.py test" $VENV_PATH/bin/python "$PROJECT_PATH/manage.py" test --noinput -v 3 --debug-mode --debug-sql --shuffle;
    [[ $? -ne 0 ]] && fail=true

    echo -e "\n${YELLOW}[2] manage.py test ToDo.tests --settings=MikesLists.settings.dev --noinput${RESET}"
    echo "--- Running Django Tests ---"
    run_cmd "manage.py test2" $VENV_PATH/bin/python "$PROJECT_PATH/manage.py" test ToDo.tests --settings=MikesLists.settings.dev --noinput;
    [[ $? -ne 0 ]] && fail=true

    echo -e "\n${YELLOW}[3] manage.py makemigrations --dry-run --check ${RESET}"
    echo "--- Running Django migrations ---"
    run_cmd "manage.py makemigrations" $VENV_PATH/bin/python "$PROJECT_PATH/manage.py" makemigrations --dry-run --check;
    [[ $? -ne 0 ]] && fail=true


    echo -e "\n${YELLOW}[4] Checking for unapplied migrations...${RESET}"
    echo "--- Running Django migrations check ---"
    # Capture the output of showmigrations
    MIGRATIONS_STATUS=$($VENV_PATH/bin/python "$PROJECT_PATH/manage.py" showmigrations | grep "\[ \]")

    if [ -n "$MIGRATIONS_STATUS" ]; then
        echo -e "${RED}Error: Unapplied migrations found:${RESET}"
        echo "$MIGRATIONS_STATUS"
        fail=true
    else
        echo -e "${GREEN}All migrations are applied.${RESET}"
    fi

    echo -e "\n${YELLOW}[5] manage.py test ToDo.tests --settings=MikesLists.settings.dev --noinput${RESET}"
    echo "--- Running Django Tests ---"
    run_cmd "manage.py test2" $VENV_PATH/bin/python "$PROJECT_PATH/manage.py" test ToDo.tests --settings=MikesLists.settings.dev --noinput --force-color;
    [[ $? -ne 0 ]] && fail=true

    echo -e "\n${YELLOW}[6]Checking Extension Dependencies --- ${RESET}"
    run_cmd "check for libstdc++6" dpkg -l | grep -q libstdc++6
    if dpkg -l | grep -q libstdc++6; then
        echo "[OK] libstdc++6 is installed."
    else
        echo "[WARN] libstdc++6 missing. This may cause Todo Tree issues."
        echo -e "${RED}✖ tests failed ${RESET}"
        fail=true
    fi

    $fail && return 1 || return 0
}


#############################################
# SECTION 7 — Nginx Diagnostics
#############################################
check_nginx() {

    echo -e "${CYAN}checking nginx${RESET}"

    local fail=false

    #############################################
    # 1. Check nginx binary
    #############################################
    echo -e "${BLUE}checking nginx binary (command -v nginx)${RESET}"
    if ! command -v nginx >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ nginx is not installed on this system${RESET}"
        return 0
    else
        echo -e "${GREEN}✔ nginx binary found${RESET}"
    fi

    #############################################
    # 2. Check nginx service state
    #############################################
    echo -e "${BLUE}checking nginx service state (systemctl is-active nginx)${RESET}"
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✔ nginx service is running${RESET}"
    else
        echo -e "${RED}✖ nginx service is NOT running${RESET}"
        fail=true
    fi

    #############################################
    # 3. Validate nginx configuration
    #############################################
    echo -e "\n${YELLOW}[1] testing nginx configuration (nginx -t)${RESET}"
    run_cmd "nginx -t" sudo nginx -t
    [[ $? -ne 0 ]] && fail=true

    #############################################
    # 4. Check for upstream errors in logs
    #############################################
    echo -e "\n${YELLOW}[2] checking nginx error logs for upstream issues${RESET}"
    echo -e "${BLUE}running:${RESET} journalctl -u nginx -n 50 --no-pager | grep -Ei \"upstream|connect|refused|timeout\""

    UPSTREAM_ERRORS=$(sudo journalctl -u nginx -n 50 --no-pager 2>&1 | grep -Ei "upstream|connect|refused|timeout")

    if [[ -z "$UPSTREAM_ERRORS" ]]; then
        echo -e "${GREEN}✔ no upstream-related errors found in recent logs${RESET}"
    else
        echo -e "${RED}✖ upstream-related errors detected:${RESET}"
        echo "$UPSTREAM_ERRORS" | sed \
            -e "s/error/${RED}error${RESET}/Ig" \
            -e "s/warning/${YELLOW}warning${RESET}/Ig" \
            -e "s/upstream/${MAGENTA}upstream${RESET}/Ig"
        fail=true
    fi

    #############################################
    # 5. Test local HTTP connectivity
    #############################################
    echo -e "\n${YELLOW}[3] testing nginx → local HTTP connectivity${RESET}"
    echo -e "${BLUE}running:${RESET} curl -s -o /dev/null -w \"%{http_code}\" http://127.0.0.1"

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1 2>/dev/null || echo "000")

    echo -e "  http status: ${CYAN}${HTTP_CODE}${RESET}"

    if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "301" || "$HTTP_CODE" == "302" ]]; then
        echo -e "${GREEN}✔ nginx (or local HTTP server) is responding on 127.0.0.1${RESET}"
    else
        echo -e "${RED}✖ nginx/local HTTP upstream not returning a healthy status${RESET}"
        fail=true
    fi

    $fail && return 1 || return 0
}


#############################################
# SECTION 8 — Environment Variable Validation
#############################################
check_envvars() {

    echo -e "${CYAN}validating environment variables (.env)${RESET}"

    local fail=false
    local missing_list=()

    #############################################
    # 1. Ensure .env exists
    #############################################
    echo -e "${BLUE}checking .env file:${RESET} $ENV_FILE"
    if [[ ! -f "$ENV_FILE" ]]; then
        echo -e "${RED}✖ .env file missing: $ENV_FILE${RESET}"
        return 1
    fi

    #############################################
    # 2. Load all variables
    #############################################
    declare -A VARS
    declare -A DUPES

    echo -e "${BLUE}parsing .env key=value pairs${RESET}"
    while IFS='=' read -r key value; do
        [[ -z "$key" || "$key" =~ ^# ]] && continue

        # detect duplicates
        if [[ -n "${VARS[$key]}" ]]; then
            DUPES["$key"]=true
        fi

        VARS["$key"]="$value"
    done < "$ENV_FILE"

    #############################################
    # 3. Required variables
    #############################################
    REQUIRED=(
        "SECRET_KEY"
        "DEBUG"
        "DB_HOST"
        "DB_PORT"
        "DB_USER"
        "DB_PASSWORD"
        "DB_NAME"
    )

    echo -e "\n${YELLOW}[1] checking required variables${RESET}"

    for key in "${REQUIRED[@]}"; do
        if [[ -z "${VARS[$key]}" ]]; then
            echo -e "${RED}✖ missing required variable:${RESET} $key"
            missing_list+=("$key")
            fail=true
        else
            echo -e "${GREEN}✔ $key=${CYAN}${VARS[$key]}${RESET}"
        fi
    done

    #############################################
    # 4. Empty values
    #############################################
    echo -e "\n${YELLOW}[2] checking for empty values${RESET}"

    EMPTY_COUNT=0
    for key in "${!VARS[@]}"; do
        if [[ -z "${VARS[$key]}" ]]; then
            echo -e "${YELLOW}⚠ $key is defined but empty${RESET}"
            ((EMPTY_COUNT++))
        fi
    done

    if (( EMPTY_COUNT == 0 )); then
        echo -e "${GREEN}✔ no empty values found${RESET}"
    fi

    #############################################
    # 5. Duplicate keys
    #############################################
    echo -e "\n${YELLOW}[3] checking for duplicate keys${RESET}"

    if (( ${#DUPES[@]} > 0 )); then
        for key in "${!DUPES[@]}"; do
            echo -e "${YELLOW}⚠ duplicate key found:${RESET} $key (later entries override earlier ones)"
        done
    else
        echo -e "${GREEN}✔ no duplicate keys${RESET}"
    fi

    #############################################
    # 6. Suspicious variables
    #############################################
    echo -e "\n${YELLOW}[4] checking for suspicious variables${RESET}"

    for key in "${!VARS[@]}"; do
        case "$key" in
            PATH)
                echo -e "${YELLOW}⚠ PATH found — should not be in .env; belongs to OS environment${RESET}"
                ;;
            TMP|TEMP)
                echo -e "${YELLOW}⚠ $key found — temp dirs should not be in .env${RESET}"
                ;;
            PWD)
                echo -e "${YELLOW}⚠ PWD found — this is your shell’s working directory, not a config value${RESET}"
                ;;
        esac
    done

    #############################################
    # Final summary for envvars
    #############################################
    if $fail; then
        echo -e "\n${RED}environment variable check FAILED.${RESET}"
        if (( ${#missing_list[@]} > 0 )); then
            echo -e "${YELLOW}missing required keys:${RESET}"
            for k in "${missing_list[@]}"; do
                echo -e "  - ${CYAN}$k${RESET}"
            done
        fi
        echo -e "${YELLOW}note:${RESET} suspicious variables do NOT cause failure by themselves."
        return 1
    else
        echo -e "\n${GREEN}environment variable check PASSED.${RESET}"
        return 0
    fi
}



#############################################
# SECTION 9 — Permissions & Ownership Checks
#############################################
check_permissions() {

    echo -e "${CYAN}checking file permissions & ownership${RESET}"

    local fail=false

    #############################################
    # 1. Project directory ownership
    #############################################
    echo -e "\n${YELLOW}[1] project directory ownership${RESET}"

    if [[ -d "$PROJECT_PATH" ]]; then
        echo -e "${BLUE}running:${RESET} stat -c \"%U:%G\" \"$PROJECT_PATH\""
        OWNER=$(stat -c "%U:%G" "$PROJECT_PATH")
        echo -e "owner: ${CYAN}$OWNER${RESET}"

        if [[ "$OWNER" != "pi:pi" ]]; then
            echo -e "${YELLOW}⚠ expected owner pi:www-data (current: $OWNER)${RESET}"
        else
            echo -e "${GREEN}✔ ownership OK${RESET}"
        fi
    else
        echo -e "${RED}✖ project directory missing${RESET}"
        fail=true
    fi

    #############################################
    # 2. Virtualenv ownership
    #############################################
    echo -e "\n${YELLOW}[2] virtualenv ownership${RESET}"

    if [[ -d "$VENV_PATH" ]]; then
        echo -e "${BLUE}running:${RESET} stat -c \"%U:%G\" \"$VENV_PATH\""
        VENV_OWNER=$(stat -c "%U:%G" "$VENV_PATH")
        echo -e "owner: ${CYAN}$VENV_OWNER${RESET}"

        if [[ "$VENV_OWNER" != "pi:django" ]]; then
            echo -e "${YELLOW}⚠ virtualenv should typically be owned by pi:pi (current: $VENV_OWNER)${RESET}"
        else
            echo -e "${GREEN}✔ virtualenv ownership OK${RESET}"
        fi
    else
        echo -e "${RED}✖ virtualenv directory missing${RESET}"
        fail=true
    fi

    #############################################
    # 3. manage.py permissions
    #############################################
    echo -e "\n${YELLOW}[3] manage.py permissions${RESET}"

    if [[ -f "$PROJECT_PATH/manage.py" ]]; then
        echo -e "${BLUE}running:${RESET} stat -c \"%a\" \"$PROJECT_PATH/manage.py\""
        PERMS=$(stat -c "%a" "$PROJECT_PATH/manage.py")
        echo -e "permissions: ${CYAN}$PERMS${RESET}"

        if [[ "$PERMS" -lt 644 ]]; then
            echo -e "${YELLOW}⚠ manage.py permissions are restrictive (expected 644 or more)${RESET}"
        else
            echo -e "${GREEN}✔ manage.py permissions OK${RESET}"
        fi
    else
        echo -e "${RED}✖ manage.py missing${RESET}"
        fail=true
    fi

    #############################################
    # 4. staticfiles_collected permissions
    #############################################
    echo -e "\n${YELLOW}[4] staticfiles_collected directory permissions${RESET}"

    STATIC_DIR="$PROJECT_PATH/staticfiles_collected"
    echo -e "${BLUE}checking directory:${RESET} $STATIC_DIR"
    if [[ -d "$STATIC_DIR" ]]; then
        echo -e "${BLUE}running:${RESET} stat -c \"%a\" \"$STATIC_DIR\""
        STATIC_PERMS=$(stat -c "%a" "$STATIC_DIR")
        echo -e "static perms: ${CYAN}$STATIC_PERMS${RESET}"

        if [[ "$STATIC_PERMS" -lt 755 ]]; then
            echo -e "${YELLOW}⚠ staticfiles_collected should be world-readable (755) for nginx${RESET}"
        else
            echo -e "${GREEN}✔ staticfiles_collected permissions OK${RESET}"
        fi
    else
        echo -e "${YELLOW}⚠ staticfiles_collected directory missing${RESET}"
    fi

    #############################################
    # 5. media directory permissions
    #############################################
    echo -e "\n${YELLOW}[5] media directory permissions (under staticfiles_collected)${RESET}"

    MEDIA_DIR="$PROJECT_PATH/media"
    echo -e "${BLUE}checking directory:${RESET} $MEDIA_DIR"
    if [[ -d "$MEDIA_DIR" ]]; then
        echo -e "${BLUE}running:${RESET} stat -c \"%a\" \"$MEDIA_DIR\""
        MEDIA_PERMS=$(stat -c "%a" "$MEDIA_DIR")
        echo -e "media perms: ${CYAN}$MEDIA_PERMS${RESET}"

        if [[ "$MEDIA_PERMS" -lt 775 ]]; then
            echo -e "${YELLOW}⚠ media directory should be writable (775) for uploads${RESET}"
        else
            echo -e "${GREEN}✔ media directory permissions OK${RESET}"
        fi
    else
        echo -e "${YELLOW}⚠ media directory under staticfiles_collected missing${RESET}"
    fi

    #############################################
    # 6. Writable directory test
    #############################################
    echo -e "\n${YELLOW}[6] writable directory test on project root${RESET}"

    TEST_FILE="$PROJECT_PATH/.diag_write_test"
    echo -e "${BLUE}running:${RESET} touch \"$TEST_FILE\""
    if touch "$TEST_FILE" 2>/dev/null; then
        echo -e "${GREEN}✔ project directory is writable${RESET}"
        rm -f "$TEST_FILE"
    else
        echo -e "${RED}✖ project directory is NOT writable by current user (${USER})${RESET}"
        fail=true
    fi

    $fail && return 1 || return 0
}



#############################################
# SECTION 10 — Python Package Drift
#############################################
check_packages() {

    echo -e "${CYAN}checking python package consistency${RESET}"

    local fail=false

    REQUIREMENTS_FILE="$PROJECT_PATH/requirements.txt"

    #############################################
    # 1. Ensure requirements.txt exists
    #############################################
    echo -e "${BLUE}checking requirements file:${RESET} $REQUIREMENTS_FILE"
    if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
        echo -e "${YELLOW}⚠ requirements.txt not found — skipping package drift check${RESET}"
        return 0
    fi

    echo -e "${GREEN}✔ requirements.txt found${RESET}"

    #############################################
    # 2. Get installed packages
    #############################################
    echo -e "${BLUE}running:${RESET} $VENV_PATH/bin/pip freeze"
    INSTALLED=$($VENV_PATH/bin/pip freeze 2>&1)
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}✖ unable to read installed packages from pip${RESET}"
        echo -e "${YELLOW}output:${RESET}"
        echo "$INSTALLED"
        return 1
    fi

    #############################################
    # 3. Missing packages
    #############################################
    echo -e "\n${YELLOW}[1] checking for missing packages (required but not installed)${RESET}"

    MISSING=0
    while IFS= read -r req; do
        [[ -z "$req" || "$req" =~ ^# ]] && continue

        pkg=$(echo "$req" | cut -d'=' -f1 | cut -d'<' -f1 | cut -d'>' -f1)

        if ! echo "$INSTALLED" | grep -qi "^${pkg}=="; then
            echo -e "${RED}✖ missing:${RESET} $req"
            MISSING=$((MISSING + 1))
        fi
    done < "$REQUIREMENTS_FILE"

    if (( MISSING == 0 )); then
        echo -e "${GREEN}✔ no missing packages${RESET}"
    else
        fail=true
    fi

    #############################################
    # 4. Version mismatches
    #############################################
    echo -e "\n${YELLOW}[2] checking for version mismatches${RESET}"

    MISMATCH=0
    while IFS= read -r req; do
        [[ -z "$req" || "$req" =~ ^# ]] && continue

        pkg=$(echo "$req" | cut -d'=' -f1)
        req_ver=$(echo "$req" | cut -d'=' -f3)

        inst_ver=$(echo "$INSTALLED" | grep -i "^${pkg}==" | cut -d'=' -f3)

        if [[ -n "$inst_ver" && -n "$req_ver" && "$inst_ver" != "$req_ver" ]]; then
            echo -e "${YELLOW}⚠ version mismatch:${RESET} $pkg (installed $inst_ver, required $req_ver)"
            MISMATCH=$((MISMATCH + 1))
        fi
    done < "$REQUIREMENTS_FILE"

    if (( MISMATCH == 0 )); then
        echo -e "${GREEN}✔ no version mismatches${RESET}"
    fi

    #############################################
    # 5. Extra packages
    #############################################
    echo -e "\n${YELLOW}[3] checking for extra installed packages (not in requirements.txt)${RESET}"

    EXTRA=0
    while IFS= read -r inst; do
        pkg=$(echo "$inst" | cut -d'=' -f1)

        if ! grep -qi "^${pkg}==" "$REQUIREMENTS_FILE"; then
            echo -e "${YELLOW}⚠ extra package installed:${RESET} $pkg"
            EXTRA=$((EXTRA + 1))
        fi
    done <<< "$INSTALLED"

    if (( EXTRA == 0 )); then
        echo -e "${GREEN}✔ no extra packages${RESET}"
    fi

    #############################################
    # Final result
    #############################################
    if (( MISSING > 0 )) || (( MISMATCH > 0 )); then
        return 1
    else
        return 0
    fi
}

#############################################
# SECTION — Python Static Analysis (ruff + flake8)
#############################################
check_static_analysis() {

    # list of codes to ignore ( like unused imports )
    # error codes found here -> https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes
    #      or at https://flake8.pycqa.org/en/latest/user/error-codes.html
    #
    IGNORES="E302,E303,E402,E501,E231,E222,E251,E265,W292,F401,F811,F405,F403"
    #IGNORES=""

    local mode="$1"   # "ruff", "flake", or empty for both

    echo -e "${CYAN}running python static analysis${RESET}"

    local fail=false

    #############################################
    # 1. Ruff
    #############################################
    if [[ -z "$mode" || "$mode" == "ruff" ]]; then
        echo -e "\n${YELLOW}[1] running ruff (undefined names, unused imports, etc.)${RESET}"
        ###echo -e "${BLUE}running:${RESET} ruff check $PROJECT_PATH --ignore E302,E303,E402,E501,E231,E222,E251,E265,W292,F401,F811"
        echo -e "${BLUE}running:${RESET} ruff check $PROJECT_PATH --ignore ${IGNORES}"

        RUFF_OUT=$("$VENV_PATH/bin/ruff" check "$PROJECT_PATH" \
            --ignore ${IGNORES} 2>&1)
            ###--ignore E302,E303,E402,E501,E231,E222,E251,E265,W292,F401,F811 2>&1)
        RUFF_STATUS=$?

        if [[ $RUFF_STATUS -ne 0 ]]; then
            echo -e "${RED}✖ ruff reported issues${RESET}"
            echo "$RUFF_OUT"
            fail=true
        else
            echo -e "${GREEN}✔ ruff found no issues${RESET}"
        fi
    fi

    #############################################
    # 2. Flake8
    #############################################
    if [[ -z "$mode" || "$mode" == "flake" ]]; then
        echo -e "\n${YELLOW}[2] running flake8 (pyflakes + style checks)${RESET}"
        # echo -e "${BLUE}running:${RESET} flake8 $PROJECT_PATH --config=/dev/null --ignore=E302,E303,E402,E501,E231,E222,E251,E265,W292,F401,F811"
        echo -e "${BLUE}running:${RESET} flake8 $PROJECT_PATH --config=/dev/null --ignore=${IGNORES}"

        FLAKE_OUT=$("$VENV_PATH/bin/flake8" "$PROJECT_PATH" \
            --config=/dev/null  \
            --ignore=${IGNORES}  2>&1)
            # --ignore=E302,E303,E402,E501,E231,E222,E251,E265,W292,F401,F811 2>&1)
        FLAKE_STATUS=$?

        if [[ $FLAKE_STATUS -ne 0 ]]; then
            echo -e "${RED}✖ flake8 reported issues${RESET}"
            echo "$FLAKE_OUT"
            fail=true
        else
            echo -e "${GREEN}✔ flake8 found no issues${RESET}"
        fi
    fi

    #############################################
    # Final result
    #############################################
    $fail && return 1 || return 0
}






#############################################
# SECTION 11 — Summary Block
#############################################
declare -A SUMMARY_STATUS

record_summary() {
    local section="$1"
    local status="$2"
    SUMMARY_STATUS["$section"]="$status"
}

print_summary() {

    echo -e "\n${MAGENTA}==================== SUMMARY ====================${RESET}"

    local overall_fail=false
    local overall_warn=false

    for section in "${!SUMMARY_STATUS[@]}"; do
        status="${SUMMARY_STATUS[$section]}"

        case "$status" in
            PASS)
                echo -e "${GREEN}✔ $section${RESET}"
                ;;
            WARN)
                echo -e "${YELLOW}⚠ $section${RESET}"
                overall_warn=true
                ;;
            FAIL)
                echo -e "${RED}✖ $section${RESET}"
                overall_fail=true
                ;;
        esac
    done

    echo -e "${MAGENTA}-------------------------------------------------${RESET}"

    if $overall_fail; then
        echo -e "${RED}OVERALL STATUS: FAIL${RESET}"
    elif $overall_warn; then
        echo -e "${YELLOW}OVERALL STATUS: WARN${RESET}"
    else
        echo -e "${GREEN}OVERALL STATUS: PASS${RESET}"
    fi

    echo
}



#############################################
# SECTION 12 — Main Execution Logic
#############################################
check_ruff_only() {
    check_static_analysis "ruff"
}

check_flake_only() {
    check_static_analysis "flake"
}



main() {

    # If no arguments were passed, show help first but continue
    if [[ $# -eq 0 ]]; then
        show_help
        echo -e "${YELLOW}running full diagnostics with default settings...${RESET}"
    fi

    echo -e "${MAGENTA}=================================================${RESET}"
    echo -e "${MAGENTA}     Django Deep Diagnostic Tool v2.2 (${ENV})    ${RESET}"
    echo -e "${MAGENTA}=================================================${RESET}"

    #############################################
    # Run each section and record results
    #############################################

    run_section "environment" validate_environment
    record_summary "environment" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "gunicorn" check_gunicorn
    record_summary "gunicorn" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "django" check_django
    record_summary "django" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "ruff" check_ruff_only
    record_summary "ruff only" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "flake" check_flake_only
    record_summary "flake only" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "lint" check_static_analysis
    record_summary "lint (ruff+flake)" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "static" check_static_analysis
    record_summary "static analysis" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "db" check_db
    record_summary "db" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "check_tests" check_tests
    record_summary "check_tests"  $([[ $? -eq 0 ]] && echo PASS || echo FAIL)


    run_section "nginx" check_nginx
    record_summary "nginx" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "git" check_git
    record_summary "git" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "env" check_envvars
    record_summary "env vars" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "permissions" check_permissions
    record_summary "permissions" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "packages" check_packages
    record_summary "packages" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    #############################################
    # Print final summary
    #############################################
    print_summary
}

main "$@"
