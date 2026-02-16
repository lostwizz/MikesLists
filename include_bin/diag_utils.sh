#!/bin/bash
# diag_utils.sh - Reusable utility functions for Django diagnostics

#############################################
# STATUS TRACKING
#############################################
declare -gA SUMMARY_STATUS
declare -ga SUMMARY_ORDER

record_summary() {
    local section="$1"
    local status="$2"

    # Check if key exists without triggering unbound variable error
    if [[ -z "${SUMMARY_STATUS[$section]:-}" ]]; then
        SUMMARY_ORDER+=("$section")
    fi

    SUMMARY_STATUS["$section"]="$status"
}

print_summary() {
    echo -e "\n${MAGENTA}==================== SUMMARY ====================${RESET}"

    local overall_fail=false
    local overall_warn=false

    for section in "${SUMMARY_ORDER[@]}"; do
        status="${SUMMARY_STATUS[$section]}"

        case "$status" in
            PASS) echo -e "${GREEN}✓ $section${RESET}" ;;
            WARN) echo -e "${YELLOW}⚠ $section${RESET}"; overall_warn=true ;;
            FAIL) echo -e "${RED}❌ $section${RESET}"; overall_fail=true ;;
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
}

#############################################
# COMMAND EXECUTION
#############################################
run_cmd() {
    local label="$1"
    shift
    local cmd=( "$@" )
    local output_shown=false

    echo -e "${BLUE}running:${RESET} ${CYAN}${cmd[*]}${RESET}"
    local OUTPUT
    OUTPUT=$("${cmd[@]}" 2>&1)
    local STATUS=$?

    # Detect coverage commands
    if printf '%s ' "${cmd[@]}" | grep -q -- '--cov'; then
        echo -e "${YELLOW}--- Coverage Output ---${RESET}"
        echo "$OUTPUT"
        output_shown=true
        echo -e "${YELLOW}----------cov command--------------${RESET}"
    fi

    if $DEBUG && [[ "$output_shown" == false ]]; then
        echo -e "${YELLOW}output:${RESET}"
        echo "$OUTPUT"
        output_shown=true
    fi

    if [[ $STATUS -ne 0 ]]; then
        echo -e "${RED}❌ ${label} failed (exit ${STATUS})${RESET}"
        if [[ "$output_shown" == false ]]; then
            echo -e "${YELLOW}output:${RESET}"
            echo "$OUTPUT"
        fi

        if [[ "$FAIL_FAST" == true ]]; then
            exit 99
        fi
        return $STATUS
    else
        echo -e "${GREEN}✓ ${label} succeeded${RESET}"
        return 0
    fi
}

#############################################
# FILE/DIRECTORY CHECKS
#############################################
check_path_exists() {
    local path_type="$1"  # "file" or "directory"
    local path="$2"
    local label="$3"

    case "$path_type" in
        file)
            if [[ -f "$path" ]]; then
                echo -e "${GREEN}✓ $label found${RESET}"
                return 0
            else
                echo -e "${RED}❌ $label missing${RESET}"
                return 1
            fi
            ;;
        directory)
            if [[ -d "$path" ]]; then
                echo -e "${GREEN}✓ $label exists${RESET}"
                return 0
            else
                echo -e "${RED}❌ $label missing${RESET}"
                return 1
            fi
            ;;
        executable)
            if [[ -x "$path" ]]; then
                echo -e "${GREEN}✓ $label executable${RESET}"
                return 0
            else
                echo -e "${RED}❌ $label not executable${RESET}"
                return 1
            fi
            ;;
    esac
}

check_ownership() {
    local path="$1"
    local expected_owner="$2"
    local label="$3"

    if [[ ! -e "$path" ]]; then
        echo -e "${RED}❌ $label does not exist${RESET}"
        return 1
    fi

    local actual_owner=$(stat -c "%U:%G" "$path")
    echo -e "${BLUE}$label owner:${RESET} ${CYAN}$actual_owner${RESET}"

    if [[ "$actual_owner" != "$expected_owner" ]]; then
        echo -e "${YELLOW}⚠ expected $expected_owner${RESET}"
        return 1
    else
        echo -e "${GREEN}✓ ownership OK${RESET}"
        return 0
    fi
}

check_permissions() {
    local path="$1"
    local min_perms="$2"
    local label="$3"

    if [[ ! -e "$path" ]]; then
        echo -e "${RED}❌ $label does not exist${RESET}"
        return 1
    fi

    local actual_perms=$(stat -c "%a" "$path")
    echo -e "${BLUE}$label permissions:${RESET} ${CYAN}$actual_perms${RESET}"

    if [[ "$actual_perms" -lt "$min_perms" ]]; then
        echo -e "${YELLOW}⚠ expected at least $min_perms${RESET}"
        return 1
    else
        echo -e "${GREEN}✓ permissions OK${RESET}"
        return 0
    fi
}

#############################################
# SERVICE CHECKS
#############################################
check_systemd_service() {
    local service_name="$1"
    local fail=false

    echo -e "${BLUE}checking systemd service:${RESET} $service_name"

    if ! systemctl list-unit-files | grep -q "$service_name"; then
        echo -e "${RED}❌ service not found${RESET}"
        return 1
    fi
    echo -e "${GREEN}✓ service exists${RESET}"

    local state=$(systemctl is-active "$service_name")
    echo -e "${BLUE}state:${RESET} ${CYAN}$state${RESET}"
    [[ "$state" != "active" ]] && echo -e "${RED}❌ service not active${RESET}" && fail=true

    local restarts=$(systemctl show "$service_name" -p NRestarts --value)
    echo -e "${BLUE}restarts:${RESET} ${CYAN}$restarts${RESET}"
    (( restarts > 3 )) && echo -e "${RED}❌ restart loop detected${RESET}" && fail=true

    $fail && return 1 || return 0
}

check_http_endpoint() {
    local url="$1"
    local label="$2"

    echo -e "${BLUE}testing HTTP:${RESET} $url"
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    echo -e "${BLUE}status:${RESET} ${CYAN}$http_code${RESET}"

    if [[ "$http_code" == "200" || "$http_code" == "301" || "$http_code" == "302" ]]; then
        echo -e "${GREEN}✓ $label responding${RESET}"
        return 0
    else
        echo -e "${RED}❌ $label unhealthy${RESET}"
        return 1
    fi
}

#############################################
# TEMPLATE CHECKS
#############################################
check_usage() {
    local filename="$1"
    echo -e "          ${B_CYAN}Searching references to: $filename...${RESET}"

    local results=$(grep -rl "$filename" /srv/django/MikesLists_dev/ \
        --exclude-dir={venv,.git,staticfiles_collected,__pycache__} \
        --include=\*.{py,html})

    if [ -z "$results" ]; then
        echo -e "            ${B_YELLOW}  ⚠️  No references found!${RESET}"
    else
        echo -e "            ${B_GREEN}  ✓  Used in:${RESET}"
        echo "$results" | sed 's/^/                 /'
    fi
}

check_templates() {
    local label="$1"
    local dir="$2"
    shift 2
    local files=("$@")
    local fail=false

    echo -e "\n${B_YELLOW}[$label] checking: $dir${RESET}"

    if [ ! -d "$dir" ]; then
        echo -e "      ${B_RED}❌  Directory missing: $dir${RESET}"
        return 1
    fi

    for file in "${files[@]}"; do
        if [ -f "$dir/$file" ]; then
            echo -e "       ${B_GREEN}✓  ${RESET}Found $file"
        else
            echo -e "      ${B_RED}❌  ${RESET}Missing $file"
            fail=true
        fi
        check_usage "$file"
    done

    $fail && return 1 || return 0
}

#############################################
# DATABASE CHECKS
#############################################
check_db_connection() {
    local manage_cmd="$1"

    echo -e "${BLUE}testing Django DB connection${RESET}"
    local db_output=$(
        $manage_cmd shell -v 2 -c "from django.db import connection; connection.ensure_connection(); print('OK')" \
        | grep -v "objects imported automatically"
    )

    if echo "$db_output" | grep -q "OK"; then
        echo -e "${GREEN}✓ Django connected to DB${RESET}"
        return 0
    else
        echo -e "${RED}❌ Django DB connection failed${RESET}"
        echo "$db_output"
        return 1
    fi
}

load_db_config() {
    local env_file="$1"

    DB_ENGINE=$(grep -E '^DB_ENGINE=' "$env_file" | cut -d '=' -f2-)
    DB_HOST=$(grep -E '^DB_HOST=' "$env_file" | cut -d '=' -f2-)
    DB_PORT=$(grep -E '^DB_PORT=' "$env_file" | cut -d '=' -f2-)
    DB_USER=$(grep -E '^DB_USER=' "$env_file" | cut -d '=' -f2-)
    DB_PASSWORD=$(grep -E '^DB_PASSWORD=' "$env_file" | cut -d '=' -f2-)
    DB_NAME=$(grep -E '^DB_NAME=' "$env_file" | cut -d '=' -f2-)

    echo -e "  DB_HOST=${CYAN}${DB_HOST:-<missing>}${RESET}"
    echo -e "  DB_PORT=${CYAN}${DB_PORT:-<missing>}${RESET}"
    echo -e "  DB_USER=${CYAN}${DB_USER:-<missing>}${RESET}"
    echo -e "  DB_PASSWORD=${CYAN}${DB_PASSWORD:+********}${RESET}"
    echo -e "  DB_NAME=${CYAN}${DB_NAME:-<missing>}${RESET}"
}

#############################################
# GIT CHECKS
#############################################
check_git_status() {
    local project_path="$1"

    if [[ ! -d "$project_path/.git" ]]; then
        echo -e "${YELLOW}⚠ no git repository${RESET}"
        return 0
    fi

    local branch=$(git -C "$project_path" rev-parse --abbrev-ref HEAD 2>&1)
    echo -e "${GREEN}✓ branch:${RESET} ${CYAN}$branch${RESET}"

    local changes=$(git -C "$project_path" status --porcelain)
    if [[ -z "$changes" ]]; then
        echo -e "${GREEN}✓ working tree clean${RESET}"
    else
        echo -e "${YELLOW}⚠ uncommitted changes${RESET}"
    fi

    return 0
}

#############################################
# COVERAGE EXTRACTION
#############################################
extract_coverage() {
    local output="$1"
    echo "$output" \
        | awk '/^TOTAL/ {print $4}' \
        | sed 's/%//'
}

check_coverage_threshold() {
    local app="$1"
    local output="$2"
    local threshold="$3"

    local percent=$(extract_coverage "$output")

    if [[ -z "$percent" ]]; then
        echo -e "${YELLOW}⚠️  $app: No coverage data${RESET}"
        return 1
    fi

    if (( $(echo "$percent >= $threshold" | bc -l) )); then
        echo -e "${GREEN}✔ $app: ${percent}% (>= ${threshold}%)${RESET}"
        return 0
    else
        echo -e "${RED}✘ $app: ${percent}% (< ${threshold}%)${RESET}"
        return 1
    fi
}

#############################################
# PACKAGE CHECKS
#############################################
check_package_in_requirements() {
    local package="$1"
    shift
    local req_files=("$@")

    for req_file in "${req_files[@]}"; do
        if grep -qi "^${package}==" "$req_file" 2>/dev/null; then
            return 0
        fi
    done
    return 1
}

get_package_version() {
    local package="$1"
    pip freeze | grep -i "^$package==" | cut -d= -f3
}

#############################################
# MIGRATION CHECKS
#############################################
check_migrations() {
    local manage_cmd="$1"

    echo -e "${BLUE}checking migrations${RESET}"
    local mig_output=$($manage_cmd showmigrations 2>&1)

    if [[ $? -ne 0 ]]; then
        echo -e "${RED}❌ showmigrations failed${RESET}"
        return 1
    fi

    local unapplied=$(echo "$mig_output" | grep '\[ \]' | wc -l)
    if (( unapplied > 0 )); then
        echo -e "${YELLOW}⚠ $unapplied unapplied migrations${RESET}"
        echo "$mig_output" | grep '\[ \]'
        return 1
    else
        echo -e "${GREEN}✓ all migrations applied${RESET}"
        return 0
    fi
}
