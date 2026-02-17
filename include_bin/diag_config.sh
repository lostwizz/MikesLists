#!/bin/bash
# diag_config.sh v2.3.1 - Fully Parameterized Configuration
# All app definitions centralized here - single source of truth

#############################################
# VERSION
#############################################
DIAG_VERSION="2.3.1"

#############################################
# ENVIRONMENT DEFAULTS
#############################################
DEFAULT_ENV="dev"
DEFAULT_PROJECT_BASE="/srv/django"
DEFAULT_VENV_BASE="/srv/django"

#############################################
# APP DEFINITIONS (SINGLE SOURCE OF TRUTH)
#############################################
# List of all Django apps in the project
declare -a DJANGO_APPS=(
    "app_core"
    "app_accounts"
    "app_ToDo"
    "app_pet"
)

# App display names
declare -A APP_DISPLAY_NAMES=(
    ["app_core"]="Core"
    ["app_accounts"]="Accounts"
    ["app_ToDo"]="ToDo"
    ["app_pet"]="Pet"
)

# Coverage thresholds per app
declare -A COVERAGE_THRESHOLDS=(
    ["app_core"]=85
    ["app_accounts"]=95
    ["app_ToDo"]=75
    ["app_pet"]=85
)

#############################################
# REQUIRED ENVIRONMENT VARIABLES
#############################################
REQUIRED_ENV_VARS=(
    "ENV_NAME"
    "DJANGO_SETTINGS_MODULE"
    "DEBUG"
    "SECRET_KEY"
    "DB_ENGINE"
    "DB_HOST"
    "DB_PORT"
    "DB_USER"
    "DB_PASSWORD"
    "DB_NAME"
    "EMAIL_HOST_PASSWORD"
)

#############################################
# LINT IGNORE CODES
#############################################
LINT_IGNORE_CODES="E302,E303,E402,E501,E231,E222,E251,E265,W292,F401,F811,F405,F403,W503,W504"

#############################################
# FILE PERMISSION EXPECTATIONS
#############################################
EXPECTED_PROJECT_OWNER="pi:pi"
EXPECTED_VENV_OWNER="pi:django"
EXPECTED_MANAGE_PERMS="644"
EXPECTED_STATIC_PERMS="755"
EXPECTED_MEDIA_PERMS="775"

#############################################
# PORT CONFIGURATIONS
#############################################
HTTP_PORTS=(8000 9000 80)
NGINX_UPSTREAM_PORT=8000

#############################################
# TEST CONFIGURATIONS
#############################################
PYTEST_BASE_ARGS="--cache-clear --verbosity=3 --disable-warnings --color=yes"
DJANGO_TEST_ARGS="--noinput -v 3 --debug-mode --traceback --force-color --shuffle"

#############################################
# GIT/PACKAGE/LOG CONFIGURATIONS
#############################################
GIT_IGNORE_PATTERNS="__pycache__|.pytest_cache|.mypy_cache|.ruff_cache|runserver.log"
REQUIREMENTS_FILES=("requirements.txt" "requirements-dev.txt")
SERVICE_NAME="mikeslists-dev.service"
LOG_LOOKBACK_SECONDS=30
NGINX_LOG_LINES=50
HEALTH_CHECK_URL="http://127.0.0.1:8000/health/"

#############################################
# COLORS (ANSI)
#############################################
export RED=$'\033[31m'
export GREEN=$'\033[32m'
export YELLOW=$'\033[33m'
export CYAN=$'\033[36m'
export BLUE=$'\033[34m'
export MAGENTA=$'\033[35m'
export RESET=$'\033[0m'

export B_RED=$'\033[1;31m'
export B_GREEN=$'\033[1;32m'
export B_YELLOW=$'\033[1;33m'
export B_CYAN=$'\033[1;36m'
export B_BLUE=$'\033[1;34m'
export B_MAGENTA=$'\033[1;35m'

#############################################
# COMPUTED PATHS
#############################################
compute_paths() {
    local env="$1"
    export PROJECT_PATH="${DEFAULT_PROJECT_BASE}/MikesLists_${env}"
    export VENV_PATH="${DEFAULT_VENV_BASE}/venv-${env}"
    export MANAGE="$VENV_PATH/bin/python $PROJECT_PATH/manage.py"
    export ENV_FILE="$PROJECT_PATH/.env"
    export STATIC_DIR="$PROJECT_PATH/staticfiles_collected"
    export MEDIA_DIR="$PROJECT_PATH/media"
}

#############################################
# APP HELPER FUNCTIONS
#############################################

# Get list of apps based on SUB_SECTION filter
get_filtered_apps() {
    local sub_section="$1"

    case "$sub_section" in
        ALL|all|"")
            echo "${DJANGO_APPS[@]}"
            ;;
        core)
            echo "app_core"
            ;;
        accounts)
            echo "app_accounts"
            ;;
        todo)
            echo "app_ToDo"
            ;;
        pet)
            echo "app_pet"
            ;;
        x)
            echo "tests"
            ;;
        *)
            echo "${DJANGO_APPS[@]}"
            ;;
    esac
}

# Get app short name (without 'app_' prefix)
get_app_short_name() {
    local app="$1"
    echo "${app#app_}"
}

# Get coverage threshold for app
get_app_threshold() {
    local app="$1"
    echo "${COVERAGE_THRESHOLDS[$app]:-80}"
}

# Get display name for app
get_app_display_name() {
    local app="$1"
    echo "${APP_DISPLAY_NAMES[$app]:-$app}"
}
