#!/usr/bin/env bash
set -e

BASE="/srv/django"
ENVS=("MikesLists_dev" "MikesLists_live" "MikesLists_test")

RED="\033[1;31m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

check_owner() {
    local path="$1"
    local expected="$2"
    local actual
    actual=$(stat -c "%U:%G" "$path" 2>/dev/null || echo "missing")

    if [[ "$actual" != "$expected" ]]; then
        echo -e "${RED}✖ $path → $actual (expected $expected)${NC}"
    else
        echo -e "${GREEN}✔ $path${NC}"
    fi
}

echo -e "${YELLOW}=== Django Permissions Audit ===${NC}"

for env in "${ENVS[@]}"; do
    DIR="$BASE/$env"
    echo -e "\n${YELLOW}--- Checking $env ---${NC}"

    # Codebase
    find "$DIR" -type f -not -path "*/media/*" -not -path "*/staticfiles_collected/*" \
        -not -name "*.sock" | while read -r f; do
        check_owner "$f" "pi:pi"
    done

    # Static files
    if [[ -d "$DIR/staticfiles_collected" ]]; then
        find "$DIR/staticfiles_collected" -type f | while read -r f; do
            check_owner "$f" "pi:pi"
        done
    fi

    # Media files
    if [[ -d "$DIR/media" ]]; then
        find "$DIR/media" -type f | while read -r f; do
            check_owner "$f" "pi:www-data"
        done
    fi

    # Gunicorn socket
    if [[ -f "$DIR/MikesLists.sock" ]]; then
        check_owner "$DIR/MikesLists.sock" "www-data:www-data"
    fi
done

echo -e "\n${YELLOW}Audit complete.${NC}"
