#!/bin/bash
# diag_config.sh - Configuration for Django Deep Diagnostic Tool
# Source this file from the main diagnostic script

#############################################
# VERSION
#############################################
DIAG_VERSION="2.3.0"

#############################################
# ENVIRONMENT DEFAULTS
#############################################
DEFAULT_ENV="dev"
DEFAULT_PROJECT_BASE="/srv/django"
DEFAULT_VENV_BASE="/srv/django"

#############################################
# COVERAGE THRESHOLDS (per app)
#############################################
declare -gA COVERAGE_THRESHOLDS=(
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
# Error codes: https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes
# Flake8 codes: https://flake8.pycqa.org/en/latest/user/error-codes.html
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
# TEMPLATE CHECKS
#############################################
declare -gA TEMPLATE_PATHS=(
    ["core_base"]="/srv/django/MikesLists_dev/app_core/templates/app_core"
    ["core_partials"]="/srv/django/MikesLists_dev/app_core/templates/app_core/partials"
    ["core_dashboard"]="/srv/django/MikesLists_dev/app_core/templates/app_core/dashboard"
    ["core_status"]="/srv/django/MikesLists_dev/app_core/templates/app_core/status"
    ["accounts"]="/srv/django/MikesLists_dev/app_accounts/templates/app_accounts"
    ["registration"]="/srv/django/MikesLists_dev/app_accounts/templates/registration"
    ["pet"]="/srv/django/MikesLists_dev/app_pet/templates/app_pet"
)

declare -gA TEMPLATE_FILES=(
    ["core_base"]="base.html home.html _wifi_band.html restart_panel.html checks_panel.html"
    ["core_partials"]="head.html navbar.html footer.html messages.html sidebar.html"
    ["core_dashboard"]="admin.html editor.html readonly.html"
    ["core_status"]="dashboard.html"
    ["accounts"]="dashboard_stats.html dashboard.html edit_profile.html group_manager.html profile_detail.html"
    ["registration"]="logged_out.html password_change_done.html password_change_form.html register.html"
    ["pet"]="dashboard.html"
)

#############################################
# TEST CONFIGURATIONS
#############################################
TEST_TARGETS=("" "tests" "app_ToDo.tests" "app_accounts.tests" "app_core.tests" "app_pet.tests")
PYTEST_BASE_ARGS="--cache-clear --verbosity=3 --disable-warnings --color=yes"

#############################################
# GIT EXCLUDE PATTERNS
#############################################
GIT_IGNORE_PATTERNS="__pycache__|.pytest_cache|.mypy_cache|.ruff_cache|runserver.log"

#############################################
# PACKAGE CHECK PATHS
#############################################
REQUIREMENTS_FILES=("requirements.txt" "requirements-dev.txt")

#############################################
# LOG INSPECTION
#############################################
SERVICE_NAME="mikeslists-dev.service"
LOG_LOOKBACK_SECONDS=30
NGINX_LOG_LINES=50

#############################################
# HEALTH CHECK ENDPOINTS
#############################################
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
# COMPUTED PATHS (based on ENV)
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
