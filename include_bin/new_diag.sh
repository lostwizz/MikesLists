#!/bin/bash
# diag.sh v3.0 - Modular Django Deep Diagnostic Tool
#
# Usage: diag.sh [environment] [options]
#
# This is a refactored, parameterized version that sources configuration
# and utility functions from separate files for better maintainability.

set -euo pipefail

#############################################
# SCRIPT DIRECTORY & SOURCING
#############################################
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source configuration and utilities
source "${SCRIPT_DIR}/diag_config.sh"
source "${SCRIPT_DIR}/diag_utils.sh"

#############################################
# DEFAULTS
#############################################
ENV="${DEFAULT_ENV}"
FAIL_FAST=false
DEBUG=false
RUN_ALL=true
declare -A RUN_SECTION
SUB_SECTION="ALL"

#############################################
# HELP TEXT
#############################################
show_help() {
    cat << EOF
${CYAN}Django Deep Diagnostic Tool v${DIAG_VERSION}${RESET}

Usage:
  diag.sh [environment] [options] [subfunc]

Environments:
  dev (default), test, live

Options:
  --all              Run all diagnostics (default)
  --fail-fast, --ff  Stop on first failure
  --debug            Show command output

Section Filters:
  --environment      Environment validation only
  --gunicorn         Gunicorn diagnostics only
  --django           Django diagnostics only
  --db               Database diagnostics only
  --git              Git diagnostics only
  --nginx            Nginx diagnostics only
  --check_tests      Django tests only
  --check_tests67    Pytest coverage only
  --permissions      File permissions only
  --packages         Python packages only
  --lint             Linting (ruff + flake8) only
  --ruff             Ruff only
  --flake            Flake8 only

Sub-app Filters:
  --sub_core         Test app_core only
  --sub_accounts     Test app_accounts only
  --sub_todo         Test app_ToDo only
  --sub_pet          Test app_pet only
  --sub_x            Test miscellaneous

  --help             Show this help

Examples:
  ./diag.sh                          # Run all checks on dev
  ./diag.sh test --ff                # Run all on test, stop on first fail
  ./diag.sh --django --db            # Only Django and DB checks
  ./diag.sh --check_tests67 --sub_accounts  # Only pytest for app_accounts
EOF
}

#############################################
# ARGUMENT PARSING
#############################################
parse_arguments() {
    for arg in "$@"; do
        case "$arg" in
            dev|test|live)
                ENV="$arg"
                ;;
            --fail-fast|--ff)
                FAIL_FAST=true
                ;;
            --debug)
                DEBUG=true
                ;;
            --all)
                RUN_ALL=true
                ;;
            --help)
                show_help
                exit 0
                ;;
            --sub_*)
                SUB_SECTION=${arg#*--sub_}
                ;;
            --*)
                RUN_ALL=false
                RUN_SECTION["$arg"]=true
                ;;
            *)
                echo -e "${RED}Unknown argument: $arg${RESET}"
                show_help
                exit 1
                ;;
        esac
    done
}

#############################################
# SECTION EXECUTION WRAPPER
#############################################
run_section() {
    local name="$1"
    local func="$2"

    # Check if section should run (safe from unbound variable errors)
    if $RUN_ALL || [[ "${RUN_SECTION[--$name]:-false}" == "true" ]]; then
        echo -e "\n${MAGENTA}=== [$name] =========================================${RESET}"
        $func
        local status=$?

        if [[ $status -ne 0 ]]; then
            echo -e "${RED}****** [$name] FAILED ******${RESET}"
            if $FAIL_FAST; then
                echo -e "${RED}Fail-fast enabled. Stopping.${RESET}"
                exit 1
            fi
        else
            echo -e "${GREEN}****** [$name] PASSED ******${RESET}"
        fi

        return $status
    fi

    return 0
}

#############################################
# SECTION 2 — Environment Validation
#############################################
validate_environment() {
    echo "========================================
   2 - Environment Validation
========================================"

    local fail=false

    check_path_exists "directory" "$PROJECT_PATH" "Project directory" || fail=true
    check_path_exists "directory" "$VENV_PATH" "Virtual environment" || fail=true
    check_path_exists "executable" "$VENV_PATH/bin/python" "Python binary" || fail=true
    check_path_exists "file" "$PROJECT_PATH/manage.py" "manage.py" || fail=true
    check_path_exists "file" "$ENV_FILE" ".env file" || fail=true

    $fail && return 1 || return 0
}

#############################################
# SECTION 3 — Gunicorn
#############################################
check_gunicorn() {
    echo "========================================
   3 - Gunicorn
========================================"

    if [[ "$ENV" == "dev" ]]; then
        echo -e "${YELLOW}Skipping — dev uses runserver${RESET}"
        return 0
    fi

    local service="gunicorn-MikesLists-${ENV}.service"
    check_systemd_service "$service"
}

#############################################
# SECTION 4 — Django Diagnostics
#############################################
check_django() {
    echo "========================================
   4 - Django Diagnostics
========================================"

    local fail=false

    echo -e "\n${YELLOW}[4.1] Django check${RESET}"
    run_cmd "manage.py check" $MANAGE check || fail=true

    echo -e "\n${YELLOW}[4.2] Django check --deploy${RESET}"
    run_cmd "manage.py check --deploy" $MANAGE check --deploy || fail=true

    echo -e "\n${YELLOW}[4.3] Migration status${RESET}"
    check_migrations "$MANAGE" || fail=true

    echo -e "\n${YELLOW}[4.4] Static files${RESET}"
    check_path_exists "directory" "$STATIC_DIR" "staticfiles_collected" || \
        echo -e "${YELLOW}⚠ Run collectstatic${RESET}"

    $fail && return 1 || return 0
}

#############################################
# SECTION 5 — Git
#############################################
check_git() {
    echo "========================================
   5 - Git Inspection
========================================"

    check_git_status "$PROJECT_PATH"
}

#############################################
# SECTION 6 — Database
#############################################
check_db() {
    echo "========================================
   6 - Database Connectivity
========================================"

    local fail=false

    echo -e "\n${YELLOW}[6.1] Loading DB config${RESET}"
    load_db_config "$ENV_FILE"

    for var in DB_HOST DB_PORT DB_USER DB_PASSWORD DB_NAME; do
        if [[ -z "${!var}" ]]; then
            echo -e "${RED}❌ Missing: $var${RESET}"
            fail=true
        fi
    done

    echo -e "\n${YELLOW}[6.2] Ping DB host${RESET}"
    if ping -c 1 -W 1 "$DB_HOST" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Ping successful${RESET}"
    else
        echo -e "${RED}❌ Cannot reach $DB_HOST${RESET}"
        fail=true
    fi

    echo -e "\n${YELLOW}[6.3] Django DB connection${RESET}"
    check_db_connection "$MANAGE" || fail=true

    $fail && return 1 || return 0
}

#############################################
# SECTION 6.7 — Pytest Coverage
#############################################
check_tests67() {
    echo "========================================
   6.7 - Pytest Coverage
========================================"

    local fail=false
    cd "$PROJECT_PATH" || exit 1

    # Define test targets based on SUB_SECTION
    local test_apps=()
    case "$SUB_SECTION" in
        ALL)
            test_apps=("app_core" "app_accounts" "app_ToDo" "app_pet")
            ;;
        core|accounts|todo|pet)
            test_apps=("app_${SUB_SECTION}")
            ;;
        *)
            test_apps=("app_core" "app_accounts" "app_ToDo" "app_pet")
            ;;
    esac

    for app in "${test_apps[@]}"; do
        echo -e "\n${YELLOW}Testing: $app${RESET}"
        local threshold=${COVERAGE_THRESHOLDS[$app]:-80}

        coverage erase >/dev/null 2>&1

        run_cmd "pytest $app" \
            $VENV_PATH/bin/pytest \
            "$app" \
            --cov="$app" \
            $PYTEST_BASE_ARGS \
            --cov-fail-under="$threshold"

        if [[ $? -ne 0 ]]; then
            fail=true
            if [[ "$FAIL_FAST" == true ]]; then
                return 1
            fi
        fi
    done

    $fail && return 1 || return 0
}

#############################################
# SECTION 7 — Nginx
#############################################
check_nginx() {
    echo "========================================
   7 - Nginx Diagnostics
========================================"

    if ! command -v nginx >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Nginx not installed${RESET}"
        return 0
    fi

    local fail=false

    check_systemd_service "nginx" || fail=true

    echo -e "\n${YELLOW}Validating config${RESET}"
    run_cmd "nginx -t" sudo nginx -t || fail=true

    echo -e "\n${YELLOW}Testing endpoints${RESET}"
    for port in "${HTTP_PORTS[@]}"; do
        check_http_endpoint "http://127.0.0.1:$port" "Port $port" || fail=true
    done

    $fail && return 1 || return 0
}

#############################################
# SECTION 9 — Permissions
#############################################
check_permissions_section() {
    echo "========================================
   9 - Permissions & Ownership
========================================"

    local fail=false

    check_ownership "$PROJECT_PATH" "$EXPECTED_PROJECT_OWNER" "Project" || fail=true
    check_ownership "$VENV_PATH" "$EXPECTED_VENV_OWNER" "Virtualenv" || fail=true
    check_permissions "$PROJECT_PATH/manage.py" "$EXPECTED_MANAGE_PERMS" "manage.py" || fail=true

    if [[ -d "$STATIC_DIR" ]]; then
        check_permissions "$STATIC_DIR" "$EXPECTED_STATIC_PERMS" "Static files" || fail=true
    fi

    $fail && return 1 || return 0
}

#############################################
# MAIN EXECUTION
#############################################
main() {
    parse_arguments "$@"

    # Compute paths based on environment
    compute_paths "$ENV"

    echo -e "${MAGENTA}================================================="
    echo "Django Diagnostic Tool v${DIAG_VERSION} (${ENV})"
    echo -e "=================================================${RESET}"

    # Run sections
    run_section "environment" validate_environment
    record_summary "2-environment" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "gunicorn" check_gunicorn
    record_summary "3-gunicorn" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "django" check_django
    record_summary "4-django" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "git" check_git
    record_summary "5-git" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "db" check_db
    record_summary "6-db" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "check_tests67" check_tests67
    record_summary "6.7-pytest" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "nginx" check_nginx
    record_summary "7-nginx" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "permissions" check_permissions_section
    record_summary "9-permissions" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    # Print summary
    print_summary
}

main "$@"
