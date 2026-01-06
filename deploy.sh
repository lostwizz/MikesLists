#!/usr/bin/env bash
#!/bin/bash
# ==========================================
# deploy script which manages the git workflow of dev -> test -> live
# ==========================================
# __version__ = "0.0.0.000059-dev"

set -euo pipefail


# --- EMERGENCY MANUAL COMMANDS ---
print_emergency_help() {
    echo -e "\e[36m\nEMERGENCY MANUAL COMMANDS\e[0m"
    echo -e "If the script ever fails and you need to clear the way manually, run these commands:"
    echo -e "To wipe all local changes and start fresh: \e[36mgit reset --hard HEAD\e[0m"
    echo -e "To delete all untracked files: \e[36mgit clean -fd\e[0m"
    echo -e "To cancel a stuck merge process: \e[36mgit merge --abort\e[0m"
}

# if [[ "$ENV" == "live" && "$USER" != "pi" ]]; then
#     echo "Refusing to deploy to LIVE unless run as pi."
#     exit 1
# fi





# Ensure the script can be updated during merge by running from /tmp
SCRIPT_PATH="$(readlink -f "$0")"
if [[ "$SCRIPT_PATH" == "$(pwd)"* ]]; then
    TMP_SCRIPT="/tmp/$(basename "$0").$$"
    cp "$0" "$TMP_SCRIPT"
    chmod +x "$TMP_SCRIPT"
    exec bash "$TMP_SCRIPT" "$@"
fi

# --- 1. AUTO-DETECT ENVIRONMENT ---
ENV_ARG="${1:-}"
if [[ -z "$ENV_ARG" ]]; then
    if [[ "$PWD" == *"_dev"* ]]; then ENV="dev";
    elif [[ "$PWD" == *"_test"* ]]; then ENV="test";
    elif [[ "$PWD" == *"_live"* ]]; then ENV="live";
    else
        echo -e "\e[31mError: Could not detect environment.\e[0m"
        print_emergency_help
        exit 1
    fi
else
    ENV="$ENV_ARG"
fi

PROJECT_DIR="/srv/django/MikesLists_$ENV"
VENV_BIN="/srv/django/venv-$ENV/bin"
SERVICE_NAME="gunicorn-MikesLists-$ENV.service"

echo -e "\e[35m------------------------------------------"
echo -e "🚀 DEPLOYING TO: ${ENV^^}"
echo -e "------------------------------------------\e[0m"

cd "$PROJECT_DIR"

# --- 2. SAFETY & CLEANUP ---
echo -e "\e[34m🧹 Checking environment state...\e[0m"

# Abort any previous failed merges that are blocking the index
git merge --abort 2>/dev/null || true

# If in TEST or LIVE, offer to auto-clean uncommitted changes
if [[ "$ENV" != "dev" ]] && [[ -n "$(git status --porcelain)" ]]; then
    echo -e "\e[33m⚠️  Uncommitted changes detected in $ENV!\e[0m"
    read -p "Force reset and clean to ensure a successful merge? (y/n): " AUTO_CLEAN
    if [[ "$AUTO_CLEAN" == "y" ]]; then
        echo -e "\e[34m🔄 Performing hard reset and cleaning untracked files...\e[0m"
        git reset --hard HEAD
        git clean -fd
    else
        echo -e "\e[31mDeployment paused. Please resolve changes manually.\e[0m"
        print_emergency_help
        exit 1
    fi
fi

# --- 3. BRANCH PROMOTION LOGIC ---
echo -e "\e[34m🔄 Handling Git Sync...\e[0m"
git fetch origin

if [[ "$ENV" == "dev" ]]; then
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "📦 Changes detected in DEV. Committing..."
        read -p "Enter commit message: " COMMIT_MSG
        git add .
        git commit -m "$COMMIT_MSG"
        git push origin dev
    fi
elif [[ "$ENV" == "test" ]]; then
    echo "🔀 Merging DEV branch into TEST environment..."
    git checkout test
    # Ensure local is matched with origin before merge
    git reset --hard origin/test
    if ! git merge origin/dev --no-edit; then
        echo -e "\e[31mMerge conflicts detected!\e[0m"
        echo "Conflicting files:"
        git status --porcelain | grep '^UU' | awk '{print $2}'
        echo ""
        echo "Differences in conflicting files:"
        for file in $(git diff --name-only --diff-filter=U); do
            echo "=== $file ==="
            git diff $file
        done
        echo ""
        echo "To resolve conflicts by accepting incoming changes (from DEV branch):"
        echo -e "\e[36mgit checkout --theirs deploy.sh\e[0m"
        echo -e "\e[36mgit add deploy.sh\e[0m"
        echo -e "\e[36mgit commit --no-edit\e[0m"
        echo ""
        echo "Or to discard incoming changes (keep TEST version):"
        echo -e "\e[36mgit checkout --ours deploy.sh\e[0m"
        echo -e "\e[36mgit add deploy.sh\e[0m"
        echo -e "\e[36mgit commit --no-edit\e[0m"
        echo ""
        echo "For other files, replace 'deploy.sh' with the filename."
        print_emergency_help
        exit 1
    fi
    git push origin test
elif [[ "$ENV" == "live" ]]; then
    echo "🔀 Merging TEST branch into LIVE environment..."
    git checkout live
    git reset --hard origin/live
    if ! git merge origin/test --no-edit; then
        git checkout --theirs include_bin/
        git add include_bin/
        git commit --no-edit || echo "No conflicts left to commit."
        print_emergency_help
        exit 1
    fi
    git push origin live
fi

# --- 4. Sync Local Binaries & Django Tasks ---
echo -e "\e[34m📂 Syncing local binaries...\e[0m"
mkdir -p "$PROJECT_DIR/include_bin"
cp -r /home/pi/bin/* "$PROJECT_DIR/include_bin/"

echo -e "\e[34m⚙️  Running Django Tasks...\e[0m"
$VENV_BIN/python manage.py migrate
$VENV_BIN/python manage.py collectstatic --noinput

if [[ "$ENV" == "dev" ]]; then PORT=8000
elif [[ "$ENV" == "test" ]]; then PORT=9000
elif [[ "$ENV" == "live" ]]; then PORT=80
fi


echo -e "\e[34m♻️  Restarting application for $ENV...\e[0m"

if [[ "$ENV" == "dev" ]]; then
    echo -e "\e[36m→ Using Django runserver (DEV)\e[0m"

    # Kill any existing runserver
    pkill -f "manage.py runserver" 2>/dev/null || true

    # Start runserver in background
    # nohup $VENV_BIN/python manage.py runserver 0.0.0.0:8000 \
    #     > "$PROJECT_DIR/runserver.log" 2>&1 &
    nohup $VENV_BIN/python manage.py runserver 0.0.0.0:$PORT \
            > "$PROJECT_DIR/runserver.log" 2>&1 &

    sleep 1
    if pgrep -f "manage.py runserver" >/dev/null; then
        echo -e "\e[32mRunserver started successfully.\e[0m"
    else
        echo -e "\e[31mRunserver failed to start!\e[0m"
    fi

else
    # TEST or LIVE → use Gunicorn
    SERVICE_NAME="gunicorn-MikesLists-$ENV.service"
    echo -e "\e[36m→ Restarting systemd service: $SERVICE_NAME\e[0m"

    if systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
        sudo systemctl restart "$SERVICE_NAME"
        sudo systemctl status "$SERVICE_NAME" --no-pager || true
    else
        echo -e "\e[31mERROR: $SERVICE_NAME does not exist!\e[0m"
        echo "Check: /etc/systemd/system/"
        exit 1
    fi
fi

# --- 5. VERIFICATION ---
echo -e "\e[35m------------------------------------------"
echo -e "🔍 RUNNING HEALTH CHECK..."
echo -e "------------------------------------------\e[0m"

~/bin/chk.sh || true

VERSION=$(git rev-parse --short HEAD)
echo -e "\n\e[32m🎉 ${ENV^^} is up and working! (v.$VERSION)\e[0m"
