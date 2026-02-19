#!/bin/bash
# diag_utils.sh - Reusable utility functions for Django diagnostics

#############################################
# STATUS TRACKING
#############################################
declare -A SUMMARY_STATUS
declare -a SUMMARY_ORDER

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

# Run command in verbose mode - always shows output
run_verbose_command() {
    local label="$1"
    shift
    local cmd=( "$@" )

    echo -e "${BLUE}running:${RESET} ${CYAN}${cmd[*]}${RESET}"

    # Try to preserve colors without mangling output
    local line_count=0
    local max_lines=100

    # Direct execution with line limiting
    "${cmd[@]}" 2>&1 | while IFS= read -r line; do
        if (( line_count < max_lines )); then
            echo "$line"
            ((line_count++))
        elif (( line_count == max_lines )); then
            echo -e "${YELLOW}... (output truncated at $max_lines lines)${RESET}"
            ((line_count++))
        fi
    done

    local status=${PIPESTATUS[0]}

    if [[ $status -ne 0 ]]; then
        echo -e "${YELLOW}⚠ ${label} completed with warnings${RESET}"
    else
        echo -e "${GREEN}✓ ${label} completed${RESET}"
    fi

    return 0  # Don't fail on verbose commands
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

    local results=$(grep -rl "$filename" "$PROJECT_PATH" \
        --exclude-dir={venv,venv-dev,venv-test,venv-live,.git,staticfiles_collected,__pycache__,coverage_html} \
        --include=\*.{py,html})

    if [ -z "$results" ]; then
        echo -e "            ${B_YELLOW}  ⚠️  No references found! This template may be unused.${RESET}"
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

check_git_comprehensive() {
    echo -e "${CYAN}Comprehensive Git diagnostics${RESET}"
    local fail=false

    # 1. Repository check
    if [[ ! -d "$PROJECT_PATH/.git" ]]; then
        echo -e "${YELLOW}⚠ No git repository found${RESET}"
        return 0
    fi

    # 2. Current branch
    echo -e "\n${YELLOW}[1] Current Branch${RESET}"
    local branch=$(git -C "$PROJECT_PATH" rev-parse --abbrev-ref HEAD 2>&1)
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}❌ Cannot determine branch${RESET}"
        fail=true
    else
        echo -e "${GREEN}✓ Branch:${RESET} ${CYAN}$branch${RESET}"
    fi

    # 3. Working tree status
    echo -e "\n${YELLOW}[2] Working Tree Status${RESET}"
    local changes=$(git -C "$PROJECT_PATH" status --porcelain)
    if [[ -z "$changes" ]]; then
        echo -e "${GREEN}✓ Working tree clean${RESET}"
    else
        echo -e "${YELLOW}⚠ Working tree has changes:${RESET}"
        echo "$changes" | head -20
        local change_count=$(echo "$changes" | wc -l)
        if (( change_count > 20 )); then
            echo -e "${YELLOW}... and $((change_count - 20)) more${RESET}"
        fi
    fi

    # 4. Untracked files
    echo -e "\n${YELLOW}[3] Untracked Files${RESET}"
    local untracked=$(git -C "$PROJECT_PATH" ls-files --others --exclude-standard)
    if [[ -z "$untracked" ]]; then
        echo -e "${GREEN}✓ No untracked files${RESET}"
    else
        local untracked_count=$(echo "$untracked" | wc -l)
        echo -e "${YELLOW}⚠ $untracked_count untracked files${RESET}"
        echo "$untracked" | head -10
        if (( untracked_count > 10 )); then
            echo -e "${YELLOW}... and $((untracked_count - 10)) more${RESET}"
        fi
    fi

    # 5. Staged changes
    echo -e "\n${YELLOW}[4] Staged Changes${RESET}"
    local staged=$(git -C "$PROJECT_PATH" diff --cached --name-only)
    if [[ -z "$staged" ]]; then
        echo -e "${GREEN}✓ No staged changes${RESET}"
    else
        echo -e "${YELLOW}⚠ Staged but uncommitted:${RESET}"
        echo "$staged"
    fi

    # 6. Last commit
    echo -e "\n${YELLOW}[5] Last Commit${RESET}"
    local hash=$(git -C "$PROJECT_PATH" rev-parse HEAD 2>/dev/null)
    if [[ -z "$hash" ]]; then
        echo -e "${RED}❌ Cannot read last commit${RESET}"
        fail=true
    else
        local author=$(git -C "$PROJECT_PATH" log -1 --pretty='%an')
        local date=$(git -C "$PROJECT_PATH" log -1 --pretty='%ad' --date=local)
        local msg=$(git -C "$PROJECT_PATH" log -1 --pretty='%B')

        echo -e "${GREEN}✓ Commit:${RESET} ${CYAN}${hash:0:8}${RESET}"
        echo -e "  Author: ${CYAN}$author${RESET}"
        echo -e "  Date:   ${CYAN}$date${RESET}"
        echo -e "  Message: ${CYAN}$msg${RESET}"
    fi

    # 7. Detached HEAD check
    echo -e "\n${YELLOW}[6] HEAD State${RESET}"
    local detached=$(git -C "$PROJECT_PATH" symbolic-ref --short -q HEAD 2>/dev/null || echo "DETACHED")
    if [[ "$detached" == "DETACHED" ]]; then
        echo -e "${YELLOW}⚠ Detached HEAD state${RESET}"
    else
        echo -e "${GREEN}✓ Normal HEAD state${RESET}"
    fi

    # 8. Upstream tracking
    echo -e "\n${YELLOW}[7] Remote Tracking${RESET}"
    local upstream=$(git -C "$PROJECT_PATH" rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)
    if [[ -z "$upstream" ]]; then
        echo -e "${YELLOW}⚠ No upstream tracking branch${RESET}"
    else
        echo -e "${GREEN}✓ Tracking:${RESET} ${CYAN}$upstream${RESET}"

        # Ahead/behind
        local ahead=$(git -C "$PROJECT_PATH" rev-list --left-right --count "$upstream"...HEAD 2>/dev/null | awk '{print $2}')
        local behind=$(git -C "$PROJECT_PATH" rev-list --left-right --count "$upstream"...HEAD 2>/dev/null | awk '{print $1}')

        if [[ -n "$ahead" && -n "$behind" ]]; then
            if (( ahead > 0 )); then
                echo -e "  ${YELLOW}↑ $ahead commits ahead${RESET}"
            fi
            if (( behind > 0 )); then
                echo -e "  ${YELLOW}↓ $behind commits behind${RESET}"
            fi
            if (( ahead == 0 && behind == 0 )); then
                echo -e "  ${GREEN}✓ In sync with remote${RESET}"
            fi
        fi
    fi

    # 9. Merge conflicts
    echo -e "\n${YELLOW}[8] Merge Conflicts${RESET}"
    local conflicts=$(git -C "$PROJECT_PATH" diff --name-only --diff-filter=U 2>/dev/null)
    if [[ -n "$conflicts" ]]; then
        echo -e "${RED}❌ Unresolved merge conflicts:${RESET}"
        echo "$conflicts"
        fail=true
    else
        echo -e "${GREEN}✓ No merge conflicts${RESET}"
    fi

    # 10. Ignored but modified files
    echo -e "\n${YELLOW}[9] Ignored Files${RESET}"
    local ignored=$(git -C "$PROJECT_PATH" ls-files -i -o -m --exclude-standard 2>/dev/null | \
        grep -v -E "__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|runserver\.log")

    if [[ -n "$ignored" ]]; then
        echo -e "${YELLOW}⚠ Modified ignored files:${RESET}"
        echo "$ignored" | head -10
    else
        echo -e "${GREEN}✓ No modified ignored files${RESET}"
    fi

    # 11. Submodules
    echo -e "\n${YELLOW}[10] Submodules${RESET}"
    if [[ -f "$PROJECT_PATH/.gitmodules" ]]; then
        git -C "$PROJECT_PATH" submodule status
    else
        echo -e "${GREEN}✓ No submodules${RESET}"
    fi

    # 12. Remote info
    echo -e "\n${YELLOW}[11] Remote${RESET}"
    local remote_url=$(git -C "$PROJECT_PATH" remote get-url origin 2>/dev/null)
    if [[ -n "$remote_url" ]]; then
        echo -e "${GREEN}✓ Origin:${RESET} ${CYAN}$remote_url${RESET}"
    else
        echo -e "${YELLOW}⚠ No remote configured${RESET}"
    fi

    # 13. Recent commits
    echo -e "\n${YELLOW}[12] Recent Commits${RESET}"
    git -C "$PROJECT_PATH" log -5 --pretty=format:"  ${CYAN}%h${RESET} %ad ${GREEN}%an${RESET} %s" --date=short 2>/dev/null
    echo ""

    # 14. Unpushed commits
    if [[ -n "$upstream" ]]; then
        echo -e "\n${YELLOW}[13] Local Commits (not pushed)${RESET}"
        local unpushed=$(git -C "$PROJECT_PATH" log "$upstream"..HEAD --oneline 2>/dev/null)
        if [[ -z "$unpushed" ]]; then
            echo -e "${GREEN}✓ All commits pushed${RESET}"
        else
            echo -e "${YELLOW}⚠ Unpushed commits:${RESET}"
            echo "$unpushed" | head -10
        fi

        echo -e "\n${YELLOW}[14] Remote Commits (not pulled)${RESET}"
        local unpulled=$(git -C "$PROJECT_PATH" log HEAD.."$upstream" --oneline 2>/dev/null)
        if [[ -z "$unpulled" ]]; then
            echo -e "${GREEN}✓ Up to date with remote${RESET}"
        else
            echo -e "${YELLOW}⚠ Commits to pull:${RESET}"
            echo "$unpulled" | head -10
        fi
    fi

    $fail && return 1 || return 0
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
    "$VENV_PATH/bin/pip" freeze 2>/dev/null | grep -i "^${package}==" | cut -d= -f3
}

get_package_summary() {
    local package="$1"
    local summary
    summary=$("$VENV_PATH/bin/pip" show "$package" 2>/dev/null | grep -i "^Summary:" | sed 's/Summary: //')
    echo "${summary:-No description available}"
}

check_packages() {
    echo -e "${CYAN}checking python package consistency${RESET}"
    local fail=false

    local req_main="$PROJECT_PATH/requirements.txt"
    local req_dev="$PROJECT_PATH/requirements-dev.txt"

    # --- [10.1] requirements.txt exists ---
    echo -e "\n${YELLOW}[10.1] Requirements file${RESET}"
    if [[ ! -f "$req_main" ]]; then
        echo -e "${YELLOW}⚠ requirements.txt not found — skipping${RESET}"
        return 0
    fi
    echo -e "${GREEN}✓ requirements.txt found${RESET}"
    [[ -f "$req_dev" ]] && echo -e "${GREEN}✓ requirements-dev.txt found${RESET}" \
                        || echo -e "${YELLOW}⚠ requirements-dev.txt not found${RESET}"

    # --- [10.2] Get installed packages ---
    echo -e "\n${YELLOW}[10.2] Installed packages${RESET}"
    local installed
    installed=$("$VENV_PATH/bin/pip" freeze 2>&1)
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}❌ pip freeze failed${RESET}"
        echo "$installed"
        return 1
    fi
    local pkg_count=$(echo "$installed" | wc -l)
    echo -e "${GREEN}✓ $pkg_count packages installed${RESET}"

    # --- [10.3] Missing packages (in requirements but not installed) ---
    echo -e "\n${YELLOW}[10.3] Missing packages (required but not installed)${RESET}"
    local missing=0
    while IFS= read -r req; do
        [[ -z "$req" || "$req" =~ ^# ]] && continue
        local pkg=$(echo "$req" | sed -E 's/[=<>!@].*//')
        if ! echo "$installed" | grep -Eqi "^${pkg}([=<>!@]| |$)"; then
            echo -e "  ${RED}❌ missing:${RESET} $req"
            (( missing++ ))
        fi
    done < "$req_main"
    (( missing == 0 )) && echo -e "${GREEN}✓ No missing packages${RESET}" \
                       || fail=true

    # --- [10.4] Version mismatches ---
    echo -e "\n${YELLOW}[10.4] Version mismatches${RESET}"
    local mismatches=0
    while IFS= read -r req; do
        [[ -z "$req" || "$req" =~ ^# ]] && continue
        # Only check pinned versions (==)
        [[ "$req" != *"=="* ]] && continue
        local pkg=$(echo "$req" | cut -d'=' -f1)
        local req_ver=$(echo "$req" | cut -d'=' -f3)
        local inst_ver=$(echo "$installed" | grep -i "^${pkg}==" | cut -d'=' -f3)
        if [[ -n "$inst_ver" && -n "$req_ver" && "$inst_ver" != "$req_ver" ]]; then
            echo -e "  ${YELLOW}⚠ $pkg:${RESET} installed ${CYAN}$inst_ver${RESET} vs required ${CYAN}$req_ver${RESET}"
            (( mismatches++ ))
        fi
    done < "$req_main"
    (( mismatches == 0 )) && echo -e "${GREEN}✓ No version mismatches${RESET}" \
                          || fail=true

    # --- [10.5] Extra packages (installed but not in any requirements) ---
    echo -e "\n${YELLOW}[10.5] Extra packages (installed but not documented)${RESET}"
    local allowed
    allowed=$(cat "$req_main" "$req_dev" 2>/dev/null \
        | grep -v '^#' \
        | sed -E 's/[=<>!@].*//' \
        | tr '[:upper:]' '[:lower:]')

    local extras=0
    while IFS= read -r inst; do
        [[ -z "$inst" ]] && continue
        local pkg=$(echo "$inst" | sed -E 's/[=<>!@].*//' | tr '[:upper:]' '[:lower:]')
        if ! echo "$allowed" | grep -qw "$pkg"; then
            local summary=$(get_package_summary "$pkg")
            printf "  ${YELLOW}⚠ extra:${RESET} %-35s %s\n" \
                "${pkg}==$(get_package_version "$pkg")" "- $summary"
            (( extras++ ))
        fi
    done <<< "$installed"
    (( extras == 0 )) && echo -e "${GREEN}✓ All packages documented${RESET}"

    # --- Final result ---
    $fail && return 1 || return 0
}

#############################################
# STATIC ANALYSIS
#############################################
check_static_analysis() {
    local mode="${1:-both}"  # "ruff", "flake", or "both"

    echo -e "${CYAN}running python static analysis (mode: $mode)${RESET}"
    local fail=false

    # --- [11.1] Ruff ---
    if [[ "$mode" == "ruff" || "$mode" == "both" ]]; then
        echo -e "\n${YELLOW}[11.1] Ruff${RESET}"
        echo -e "  ${BLUE}running:${RESET} ruff check $PROJECT_PATH --ignore ${RUFF_IGNORE_CODES}"

        local ruff_out
        ruff_out=$("$VENV_PATH/bin/ruff" check "$PROJECT_PATH" \
            --ignore "${RUFF_IGNORE_CODES}" 2>&1)

        if [[ $? -ne 0 ]]; then
            echo -e "  ${RED}❌ ruff reported issues:${RESET}"
            echo "$ruff_out" | head -30 | sed 's/^/  /'
            fail=true
        else
            echo -e "  ${GREEN}✓ ruff found no issues${RESET}"
        fi
    fi

    # --- [11.2] Flake8 ---
    if [[ "$mode" == "flake" || "$mode" == "both" ]]; then
        echo -e "\n${YELLOW}[11.2] Flake8${RESET}"
        echo -e "  ${BLUE}running:${RESET} flake8 $PROJECT_PATH --ignore ${FLAKE_IGNORE_CODES}"

        local flake_out
        flake_out=$("$VENV_PATH/bin/flake8" "$PROJECT_PATH" \
            --config=/dev/null \
            --ignore="${FLAKE_IGNORE_CODES}" 2>&1)

        if [[ $? -ne 0 ]]; then
            echo -e "  ${RED}❌ flake8 reported issues:${RESET}"
            echo "$flake_out" | head -30 | sed 's/^/  /'
            fail=true
        else
            echo -e "  ${GREEN}✓ flake8 found no issues${RESET}"
        fi
    fi

    $fail && return 1 || return 0
}

#############################################
# ENVIRONMENT VARIABLE VALIDATION
#############################################
check_envvars() {
    echo -e "${CYAN}validating environment variables${RESET}"
    local fail=false

    # 1. Ensure .env exists
    echo -e "\n${YELLOW}[1] .env file${RESET}"
    echo -e "${BLUE}checking:${RESET} $ENV_FILE"
    if [[ ! -f "$ENV_FILE" ]]; then
        echo -e "${RED}❌ .env file missing: $ENV_FILE${RESET}"
        return 1
    fi
    echo -e "${GREEN}✓ .env found${RESET}"

    # 2. Parse key=value pairs, detecting duplicates
    echo -e "\n${YELLOW}[2] Parsing .env${RESET}"
    declare -A _VARS
    declare -A _DUPES

    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        [[ -z "$key" || "$key" =~ ^# || "$key" =~ ^[[:space:]]*$ ]] && continue
        # Trim whitespace from key
        key=$(echo "$key" | tr -d '[:space:]')

        if [[ -n "${_VARS[$key]:-}" ]]; then
            _DUPES["$key"]=true
        fi
        _VARS["$key"]="$value"
    done < "$ENV_FILE"

    local total=${#_VARS[@]}
    echo -e "${GREEN}✓ $total variables parsed${RESET}"

    # 3. Required variables (from diag_config.sh)
    echo -e "\n${YELLOW}[3] Required variables${RESET}"
    local missing_list=()

    for key in "${REQUIRED_ENV_VARS[@]}"; do
        if [[ -z "${_VARS[$key]:-}" ]]; then
            echo -e "  ${RED}❌ missing:${RESET} $key"
            missing_list+=("$key")
            fail=true
        else
            # Mask sensitive values
            local display="${_VARS[$key]}"
            case "$key" in
                *PASSWORD*|*SECRET*|*KEY*)
                    display="********"
                    ;;
            esac
            echo -e "  ${GREEN}✓${RESET} $key=${CYAN}$display${RESET}"
        fi
    done

    # 4. Empty values
    echo -e "\n${YELLOW}[4] Empty values${RESET}"
    local empty_count=0
    for key in "${!_VARS[@]}"; do
        if [[ -z "${_VARS[$key]}" ]]; then
            echo -e "  ${YELLOW}⚠ defined but empty:${RESET} $key"
            (( empty_count++ ))
        fi
    done
    (( empty_count == 0 )) && echo -e "  ${GREEN}✓ No empty values${RESET}"

    # 5. Duplicate keys
    echo -e "\n${YELLOW}[5] Duplicate keys${RESET}"
    if (( ${#_DUPES[@]} > 0 )); then
        for key in "${!_DUPES[@]}"; do
            echo -e "  ${YELLOW}⚠ duplicate:${RESET} $key (last value wins)"
        done
    else
        echo -e "  ${GREEN}✓ No duplicates${RESET}"
    fi

    # 6. Suspicious variables
    echo -e "\n${YELLOW}[6] Suspicious variables${RESET}"
    local suspicious=0
    for key in "${!_VARS[@]}"; do
        case "$key" in
            PATH)
                echo -e "  ${YELLOW}⚠ PATH found — belongs to OS, not .env${RESET}"
                (( suspicious++ ))
                ;;
            TMP|TEMP)
                echo -e "  ${YELLOW}⚠ $key found — temp dirs should not be in .env${RESET}"
                (( suspicious++ ))
                ;;
            PWD)
                echo -e "  ${YELLOW}⚠ PWD found — this is your shell working directory${RESET}"
                (( suspicious++ ))
                ;;
        esac
    done
    (( suspicious == 0 )) && echo -e "  ${GREEN}✓ No suspicious variables${RESET}"

    # 7. Summary
    if [[ ${#missing_list[@]} -gt 0 ]]; then
        echo -e "\n${RED}❌ Missing required variables:${RESET}"
        for k in "${missing_list[@]}"; do
            echo -e "  - ${CYAN}$k${RESET}"
        done
    fi

    $fail && return 1 || return 0
}
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

#############################################
# ERROR LOG CHECKS
#############################################
check_recent_errors() {
    local lookback="${LOG_LOOKBACK_SECONDS:-30} seconds ago"

    echo -e "${BLUE}checking for errors in last $lookback${RESET}"

    local errors=$(journalctl -u "$SERVICE_NAME" --since "$lookback" --no-pager 2>/dev/null | \
        grep -i -E "AttributeError|ImportError|ModuleNotFoundError|NameError|TypeError|KeyError")

    if [[ -n "$errors" ]]; then
        echo -e "${RED}❌ Recent errors detected:${RESET}"
        echo "$errors" | head -10 | sed 's/^/  /'

        # Check for specific common errors
        if echo "$errors" | grep -q "AttributeError.*context_processors"; then
            echo -e "${YELLOW}⚠ Context processor error detected${RESET}"
        fi
        if echo "$errors" | grep -q "NoReverseMatch"; then
            echo -e "${YELLOW}⚠ URL routing error detected${RESET}"
        fi
        if echo "$errors" | grep -q "TemplateDoesNotExist"; then
            echo -e "${YELLOW}⚠ Missing template detected${RESET}"
        fi

        return 1
    else
        echo -e "${GREEN}✓ No Python errors in recent logs${RESET}"
        return 0
    fi
}

#############################################
# URL AUDIT FUNCTIONS
#############################################

# Audit URL patterns to ensure views exist
audit_url_patterns_to_views() {
    echo -e "\n${YELLOW}[1] Auditing URL Patterns → Views${RESET}"
    local fail=false
    local warn=false

    # Get all URL patterns
    cd "$PROJECT_PATH" || return 1
    $MANAGE show_urls 2>/dev/null | sort -u | while read -r line; do
        local url_pattern=$(echo "$line" | awk '{print $1}')
        local view_path=$(echo "$line" | awk '{print $NF}')

        # Skip empty lines
        [[ -z "$url_pattern" ]] && continue

        # Skip if it's just a bare URL name without a path
        [[ "$url_pattern" == "DEBUG:" ]] && continue

        # Check if it's a Django internal view
        if [[ "$view_path" == *"django."* ]] || \
           [[ "$view_path" == *":"* ]] || \
           [[ "$view_path" =~ ^(password_|login|logout|reset) ]]; then
            echo -e "    ${B_GREEN}✓${RESET} $url_pattern → ${CYAN}$view_path${RESET} (Django internal)"
            continue
        fi

        # Extract clean view name (handle Class-Based Views)
        local clean_name=$(echo "$view_path" | rev | cut -d. -f1 | rev | sed 's/.as_view//g')

        # Search for view definition
        local file_loc=$(grep -rlE --include="*.py" "(def|class) $clean_name" "$PROJECT_PATH" \
            --exclude-dir={venv,venv-dev,venv-test,__pycache__,static,media,.git,staticfiles_collected,tests,coverage_html} \
            --exclude="urls.py" 2>/dev/null | head -1)

        if [[ -n "$file_loc" ]]; then
            local short_loc=$(echo "$file_loc" | sed "s|$PROJECT_PATH/||g")
            echo -e "    ${B_GREEN}✓${RESET} $url_pattern → ${CYAN}$clean_name${RESET} in $short_loc"
        else
            # Check if it's actually a URL name (not a function name)
            # URL pattern name syntax is: app:name or just name
            if [[ "$clean_name" == *"_"* || "$clean_name" =~ ^[a-z]+$ ]]; then
                # This might be a URL name, not a view function - skip warning
                echo -e "    ${B_GREEN}✓${RESET} $url_pattern → ${CYAN}$view_path${RESET} (URL name)"
                continue
            fi

            # Fallback: check if referenced anywhere in views
            local fallback=$(grep -rl "$clean_name" "$PROJECT_PATH" \
                --include="*views*.py" \
                --exclude-dir={venv,venv-dev,__pycache__,tests} 2>/dev/null | head -1)

            if [[ -n "$fallback" ]]; then
                local short_loc=$(echo "$fallback" | sed "s|$PROJECT_PATH/||g")
                echo -e "    ${B_YELLOW}⚠${RESET} $url_pattern → ${CYAN}$clean_name${RESET} referenced in $short_loc"
            else
                echo -e "    ${B_YELLOW}⚠${RESET} $url_pattern → ${RED}$clean_name NOT FOUND${RESET}"
            fi
        fi
    done
}

# Audit views to ensure they have URL patterns
audit_views_to_url_patterns() {
    echo -e "\n${YELLOW}[2] Auditing Views → URL Patterns (Reverse Check)${RESET}"

    cd "$PROJECT_PATH" || return 1

    # Use Python to check for orphaned views
    $VENV_PATH/bin/python3 << 'PYEOF'
import os
import sys
import re

# Setup Django
project_path = os.getcwd()
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.dev')

try:
    import django
    django.setup()
    from django.urls import get_resolver
    from django.urls.resolvers import URLPattern, URLResolver

    # Get all URL names
    def get_all_url_names(resolver, namespace=''):
        url_names = set()
        for pattern in resolver.url_patterns:
            if isinstance(pattern, URLResolver):
                new_namespace = f"{namespace}{pattern.namespace}:" if pattern.namespace else namespace
                url_names.update(get_all_url_names(pattern, new_namespace))
            elif isinstance(pattern, URLPattern):
                if pattern.name:
                    full_name = f"{namespace}{pattern.name}"
                    url_names.add(full_name)
                # Also get view function name
                if hasattr(pattern.callback, '__name__'):
                    url_names.add(pattern.callback.__name__)
        return url_names

    resolver = get_resolver()
    registered_urls = get_all_url_names(resolver)

    # Find all view functions
    orphaned_views = []
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in ['venv', 'venv-dev', '__pycache__', '.git', 'tests', 'migrations']]

        for file in files:
            if file.endswith('views.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Find function/class definitions
                    for match in re.finditer(r'^(def|class)\s+(\w+)', content, re.MULTILINE):
                        view_name = match.group(2)
                        # Skip private/test functions
                        if view_name.startswith('_') or view_name.startswith('test'):
                            continue
                        # Skip known helper functions (not routed directly)
                        if view_name in ['get_stage_info', 'build_pet_context']:
                            continue
                        # Check if registered
                        if view_name not in registered_urls:
                            orphaned_views.append((filepath, view_name))

    if orphaned_views:
        print(f"\033[1;33m⚠ Found {len(orphaned_views)} potentially orphaned views:\033[0m")
        for filepath, view_name in orphaned_views[:10]:  # Limit output
            short_path = filepath.replace('./', '')
            print(f"    \033[33m⚠\033[0m {short_path} → \033[36m{view_name}\033[0m")
        if len(orphaned_views) > 10:
            print(f"    ... and {len(orphaned_views) - 10} more")
        sys.exit(2)  # Warning exit code
    else:
        print("\033[1;32m✓ No orphaned views found\033[0m")
        sys.exit(0)

except Exception as e:
    print(f"\033[1;31mCRITICAL: Django setup failed: {e}\033[0m")
    sys.exit(1)
PYEOF

    local result=$?
    if [[ $result -eq 0 ]]; then
        echo -e "${B_GREEN}✓ All views have URL patterns${RESET}"
        return 0
    elif [[ $result -eq 2 ]]; then
        echo -e "${B_YELLOW}⚠ Review warnings above${RESET}"
        return 0  # Don't fail on warnings
    else
        echo -e "${B_RED}❌ URL audit failed${RESET}"
        return 1
    fi
}

# Main URL audit function
check_url_consistency() {
    echo -e "${BLUE}Checking URL-View consistency${RESET}"
    local fail=false

    audit_url_patterns_to_views || fail=true
    audit_views_to_url_patterns || fail=true

    $fail && return 1 || return 0
}


#############################################
# TEMPLATE VALIDATION
#############################################
check_django_templates() {
    echo -e "${BLUE}checking Django templates${RESET}"
    local fail=false

    # Track which templates we've explicitly checked
    declare -A checked_templates

    # Check app_core templates (has subdirectories)
    local core_base_templates=(base.html home.html)
    check_templates "app_core (base)" \
        "${PROJECT_PATH}/app_core/templates/app_core" \
        "${core_base_templates[@]}" || fail=true
    for tmpl in "${core_base_templates[@]}"; do checked_templates["$tmpl"]=1; done

    local core_partial_templates=(head.html navbar.html footer.html messages.html sidebar.html extra_js.html )
    check_templates "app_core (partials)" \
        "${PROJECT_PATH}/app_core/templates/app_core/partials" \
        "${core_partial_templates[@]}" || fail=true
    for tmpl in "${core_partial_templates[@]}"; do checked_templates["$tmpl"]=1; done



    local core_status_partial_templates=(basic_info_panel.html _iface_speed.html _wifi_band.html _wifi_data.html _wifi_health.html _wifi_signal.html \
                checks_panel.html interfaces_panel.html network_diagnostics.html \
                restart_panel.html )
    check_templates "app_core Status (partials)" \
        "${PROJECT_PATH}/app_core/templates/app_core/status/partials" \
        "${core_status_partial_templates[@]}" || fail=true
    for tmpl in "${core_status_partial_templates[@]}"; do checked_templates["$tmpl"]=1; done



    local core_dash_templates=(admin.html editor.html readonly.html)
    check_templates "app_core (dashboard)" \
        "${PROJECT_PATH}/app_core/templates/app_core/dashboard" \
        "${core_dash_templates[@]}" || fail=true
    for tmpl in "${core_dash_templates[@]}"; do checked_templates["$tmpl"]=1; done

    # Check app_accounts templates
    local accounts_templates=(dashboard.html edit_profile.html profile_detail.html group_manager.html dashboard_stats.html)
    check_templates "app_accounts" \
        "${PROJECT_PATH}/app_accounts/templates/app_accounts" \
        "${accounts_templates[@]}" || fail=true
    for tmpl in "${accounts_templates[@]}"; do checked_templates["$tmpl"]=1; done

    local reg_templates=(logged_out.html login.html password_change_done.html password_change_form.html password_reset_complete.html \
    password_reset_confirm.html password_reset_done.html password_reset_form.html register.html)
    check_templates "registration" \
        "${PROJECT_PATH}/app_accounts/templates/registration" \
        "${reg_templates[@]}" || fail=true
    for tmpl in "${reg_templates[@]}"; do checked_templates["$tmpl"]=1; done


    # check app_todo templates
    local check_todo_templates=(todo_list.html )
    check_templates "ToDo_apps" \
        "${PROJECT_PATH}/app_ToDo/templates/app_ToDo" \
        "${check_todo_templates[@]}" || fail=true
    for tmpl in "${check_todo_templates[@]}"; do checked_templates["$tmpl"]=1; done


    # check app_pet templates
    local check_pet_templates=(pet_dashboard.html )
    check_templates "pet_apps" \
        "${PROJECT_PATH}/app_pet/templates/app_pet" \
        "${check_pet_templates[@]}" || fail=true
    for tmpl in "${check_pet_templates[@]}"; do checked_templates["$tmpl"]=1; done






    # # Check app_pet templates
    # if [[ -d "${PROJECT_PATH}/app_pet/templates/app_pet" ]]; then
    #     local pet_templates=(dashboard.html)
    #     check_templates "app_pet" \
    #         "${PROJECT_PATH}/app_pet/templates/app_pet" \
    #         "${pet_templates[@]}" || fail=true
    #     for tmpl in "${pet_templates[@]}"; do checked_templates["$tmpl"]=1; done
    # fi

    echo '..........................................................'

    # Now discover ALL templates and check for unchecked ones
    echo -e "\n${B_YELLOW}[Auto-Discovery] Finding unchecked templates...${RESET}"
    find_unchecked_templates checked_templates || fail=true

    $fail && return 1 || return 0
}





# Find and validate templates that weren't explicitly checked
find_unchecked_templates() {
    local -n checked_ref=$1
    local found_unchecked=false

    # Find all .html files in template directories
    while IFS= read -r template_file; do
        local basename=$(basename "$template_file")
        local dirname=$(dirname "$template_file")

        # Skip if already checked
        if [[ -n "${checked_ref[$basename]}" ]]; then
            continue
        fi

        # Skip admin templates (Django built-in)
        if [[ "$template_file" == *"/admin/"* ]]; then
            continue
        fi

        # Skip test templates
        if [[ "$template_file" == *"/tests/"* || "$template_file" == *"/test_"* ]]; then
            continue
        fi

        # Found an unchecked template
        if [[ "$found_unchecked" == false ]]; then
            echo -e "${B_CYAN}Unchecked templates found:${RESET}"
            found_unchecked=true
        fi

        echo -e "\n${B_YELLOW}[Unchecked] $dirname${RESET}"
        echo -e "       ${B_GREEN}✓  ${RESET}Found $basename"
        check_usage "$basename"

    done < <(find "${PROJECT_PATH}" -path "*/templates/*.html" \
        -not -path "*/venv*" \
        -not -path "*/.git/*" \
        -not -path "*/staticfiles_collected/*" \
        -not -path "*/__pycache__/*" \
        -not -path "*/tests/*" \
        -not -path "*/test_*" \
        -type f)

    if [[ "$found_unchecked" == false ]]; then
        echo -e "${GREEN}✓ All templates are explicitly validated${RESET}"
    else
        echo -e "\n${YELLOW}⚠ Found unchecked templates - consider adding to explicit checks${RESET}"
    fi

    return 0
}
