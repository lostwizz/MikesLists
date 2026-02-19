#!/bin/bash
# diag.sh v3.0 - Modular Django Deep Diagnostic Tool
#
# Usage: diag.sh [environment] [options]
#
# This is a refactored, parameterized version that sources configuration
# and utility functions from separate files for better maintainability.
# __version__="3.1.2.000153"



#############################################
# SCRIPT DIRECTORY & SOURCING
#############################################
# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source configuration and utilities
if [[ -f "${SCRIPT_DIR}/diag_config.sh" ]]; then
    source "${SCRIPT_DIR}/diag_config.sh"
else
    echo "ERROR: Cannot find diag_config.sh in ${SCRIPT_DIR}"
    exit 1
fi

if [[ -f "${SCRIPT_DIR}/diag_utils.sh" ]]; then
    source "${SCRIPT_DIR}/diag_utils.sh"
else
    echo "ERROR: Cannot find diag_utils.sh in ${SCRIPT_DIR}"
    exit 1
fi

#############################################
# DEFAULTS
#############################################
ENV="${DEFAULT_ENV}"
FAIL_FAST=false
DEBUG=false
VERBOSE=false
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
  --verbose, -v      Enable verbose output (show_urls, permissions, models)

Section Filters:
  --environment      Environment validation only
  --gunicorn         Gunicorn diagnostics only
  --django           Django diagnostics only
  --db               Database diagnostics only
  --git              Git diagnostics only
  --nginx            Nginx diagnostics only
  --envvars          Environment variable validation (section 8)
  --check_tests      Django tests only
  --check_tests67    Pytest coverage only
  --permissions      File permissions only
  --packages         Python package drift (section 10)
  --static           Static analysis - ruff + flake8 (section 11)
  --ruff             Ruff only
  --flake            Flake8 only
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
            --verbose|-v)
                VERBOSE=true
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
        echo -e "\n${MAGENTA}=== [$name] =======--> use --$name ==================================${RESET}"
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

    echo -e "\n${YELLOW}[4.3] Python syntax compilation${RESET}"
    run_cmd "Python compileall" \
        $VENV_PATH/bin/python -m compileall "$PROJECT_PATH" -q || fail=true

    echo -e "\n${YELLOW}[4.4] Migration status${RESET}"
    check_migrations "$MANAGE" || fail=true

    echo -e "\n${YELLOW}[4.5] Static files${RESET}"
    check_path_exists "directory" "$STATIC_DIR" "staticfiles_collected" || \
        echo -e "${YELLOW}⚠ Run collectstatic${RESET}"

    echo -e "\n${YELLOW}[4.6] Recent error log check (last ${LOG_LOOKBACK_SECONDS}s)${RESET}"
    check_recent_errors || fail=true

    echo -e "\n${YELLOW}[4.7] Template validation${RESET}"
    check_django_templates || fail=true

    # Verbose mode: Additional diagnostics
    if [[ "$VERBOSE" == true ]]; then
        echo -e "\n${B_CYAN}=== VERBOSE MODE: Additional Django Diagnostics ===${RESET}"

        echo -e "\n${YELLOW}[4.8-V] URL Patterns${RESET}"
        run_verbose_command "show_urls" $MANAGE show_urls --format verbose

        echo -e "\n${YELLOW}[4.9-V] Model Information${RESET}"
        run_verbose_command "list_model_info" $MANAGE list_model_info

        echo -e "\n${YELLOW}[4.10-V] Permissions${RESET}"
        run_verbose_command "show_permissions" $MANAGE show_permissions --all

        echo -e "\n${YELLOW}[4.11-V] Template Validation${RESET}"
        run_verbose_command "validate_templates" $MANAGE validate_templates
    fi

    $fail && return 1 || return 0
}

#############################################
# SECTION 4.5 — URL Audit
#############################################
check_url_audit() {
    echo "========================================
   4.5 - URL & View Consistency Audit
========================================"

    check_url_consistency
}

#############################################
# SECTION 5 — Git
#############################################
check_git() {
    echo "========================================
   5 - Git Inspection
========================================"

    check_git_comprehensive
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
# SECTION 6.5 - manage.py test code
#############################################
check_tests() {
    echo "========================================
   6.5 - manage.py test code
========================================"

    local fail=false
    cd "$PROJECT_PATH" || exit 1

    # Get filtered apps based on SUB_SECTION
    local test_apps_str=$(get_filtered_apps "$SUB_SECTION")
    local test_apps=($test_apps_str)

    echo -e "${CYAN}Testing apps: ${test_apps[*]}${RESET}"

    for app in "${test_apps[@]}"; do
        local display_name=$(get_app_display_name "$app")
        local threshold=$(get_app_threshold "$app")

        echo -e "\n${YELLOW}Testing: $app ($display_name) - threshold: ${threshold}%${RESET}"

        $MANAGE test $app

        # run_cmd $MANAGE \
        #     $VENV_PATH/bin/pytest \
        #     "$app" \
        #     --cov="$app" \
        #     $PYTEST_BASE_ARGS \
        #     --cov-fail-under="$threshold"

        # if [[ $? -ne 0 ]]; then
        #     fail=true
        #     if [[ "$FAIL_FAST" == true ]]; then
        #         return 1
        #     fi
        # fi
    done

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

    # Get filtered apps based on SUB_SECTION
    local test_apps_str=$(get_filtered_apps "$SUB_SECTION")
    local test_apps=($test_apps_str)

    echo -e "${CYAN}Testing apps: ${test_apps[*]}${RESET}"

    for app in "${test_apps[@]}"; do
        local display_name=$(get_app_display_name "$app")
        local threshold=$(get_app_threshold "$app")

        echo -e "\n${YELLOW}Testing: $app ($display_name) - threshold: ${threshold}%${RESET}"

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
# SECTION 8 — Environment Variable Validation
#############################################
check_envvars_section() {
    echo "========================================
   8 - Environment Variable Validation
========================================"
    check_envvars
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
# SECTION 10 — Package Drift
#############################################
check_packages_section() {
    echo "========================================
   10 - Python Package Drift
========================================"
    check_packages
}

#############################################
# SECTION 11 — Static Analysis
#############################################
check_static_section() {
    echo "========================================
   11 - Python Static Analysis
========================================"
    check_static_analysis "both"
}

check_ruff_section() {
    echo "========================================
   11 - Ruff Only
========================================"
    check_static_analysis "ruff"
}

check_flake_section() {
    echo "========================================
   11 - Flake8 Only
========================================"
    check_static_analysis "flake"
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

    run_section "url_audit" check_url_audit
    record_summary "4.5-url_audit" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "git" check_git
    record_summary "5-git" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "db" check_db
    record_summary "6-db" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "check_tests" check_tests
    record_summary "6.5-pytest" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "check_tests67" check_tests67
    record_summary "6.7-pytest" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "nginx" check_nginx
    record_summary "7-nginx" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "envvars" check_envvars_section
    record_summary "8-envvars" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "permissions" check_permissions_section
    record_summary "9-permissions" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "packages" check_packages_section
    record_summary "10-packages" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "static" check_static_section
    record_summary "11-static" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "ruff" check_ruff_section
    record_summary "11-ruff" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    run_section "flake" check_flake_section
    record_summary "11-flake" $([[ $? -eq 0 ]] && echo PASS || echo FAIL)

    # Print summary
    print_summary
}

main "$@"
