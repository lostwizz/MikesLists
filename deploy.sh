#!/bin/bash
# ==========================================
# Django Multi-Env Deploy Script (V9 - Sparse-Aware)
# ==========================================
set -euo pipefail

BASE_PATH="/srv/django"
ENV_NAME=$(basename "$(pwd)" | sed 's/MikesLists_//')
ENV_NAME_UPPER=$(echo "$ENV_NAME" | tr '[:lower:]' '[:upper:]')

echo "------------------------------------------"
echo "🚀 TARGET ENV: $ENV_NAME_UPPER"
echo "------------------------------------------"

case "$ENV_NAME" in
    dev)

        # --- 4. Sync Local Binaries & Django Tasks ---
        PROJECT_DIR="/srv/django/MikesLists_$ENV_NAME"
        echo -e "\e[34m📂 Syncing local binaries...\e[0m"
        mkdir -p "$PROJECT_DIR/include_bin"
        cp -rv /home/pi/bin/* "$PROJECT_DIR/include_bin/"

        # mkdir -p "$PROJECT_DIR/include_bin/log-dashboard"
        # cp -rv /home/pi/log-dashboard/* "$PROJECT_DIR/include_bin/log-dashboard"

        mkdir -p "$PROJECT_DIR/include_bin/services"
        # Verbose copy so you see the files moving
        cp -rv /home/pi/bin/* "$PROJECT_DIR/include_bin/"
        cp -rv /home/pi/log-dashboard/* "$PROJECT_DIR/include_bin/log-dashboard"
        cp -rv /etc/systemd/system/{full-backup.service,full-backup.timer,gunicorn-MikesLists-live.service,gunicorn-MikesLists-test.service,watcher.service,mikeslists-dev.service,check-ip-change.service} "$PROJECT_DIR/include_bin/services/"
        cp -rv /usr/local/bin/check_ip_change.sh "$PROJECT_DIR/include_bin/services"


        echo "📦 DEV: Reviewing Changes..."
        # echo -e "\n🔍 \e[32mCURRENT GIT STATUS:\e[0m"
        # 1. Shows a short summary of branch/files
        git status -sb

        # Ensure .env is ignored before checking for changes
        git rm --cached .env 2>/dev/null || true

        # 2. Shows the ACTUAL code changes you just made (the cp commands)
        # This is better than 'git show' here because 'git show' looks at the PAST.
        # git diff

        # git status
        # git status -sbv
        # git status -v
        git --no-pager log --oneline --graph --all
        # git --no-pager show --oneline
        # git branch -vv

        # git clean -n

        echo "📦 DEV: Committing and Pushing..."
        git rm --cached .env 2>/dev/null || true
        if [[ -n "$(git status --porcelain)" ]]; then
            echo -e "\n📝 \e[33mChanges detected. Enter commit message:\e[0m"
            # This reads your input and stores it in $COMMIT_MSG
            read -r -p "> " COMMIT_MSG

            COMMIT_MSG="Dev update: $(date +'%Y-%m-%d %H:%M') - ${COMMIT_MSG}"

            # COMMIT_MSG="${USER_INPUT:-"Manual update"}"
            git add .
            git commit -m "${COMMIT_MSG}"
            git push origin dev
        else
            git push origin dev || echo "Already up to date."
        fi
        git --no-pager log --oneline --graph --all
        git status
        ;;

    test|live)
        SOURCE_BRANCH="dev"
        [[ "$ENV_NAME" == "live" ]] && SOURCE_BRANCH="test"

        echo "🔄 $ENV_NAME_UPPER: Force-syncing from $SOURCE_BRANCH..."

        # NEW: Disable sparse-checkout if it's blocking us
        git sparse-checkout disable 2>/dev/null || true

        git fetch origin
        git checkout "$ENV_NAME" 2>/dev/null || git checkout -b "$ENV_NAME"

        # Hard reset is better for Test/Live as it ensures a clean environment
        if ! git reset --hard "origin/$SOURCE_BRANCH"; then
            echo "⚠️ Reset failed. Clearing locks and retrying..."
            rm -f .git/index.lock
            git reset --hard "origin/$SOURCE_BRANCH"
        fi

        git push origin "$ENV_NAME" --force
        ;;

    *)
        echo "❌ ERROR: Unknown environment '$ENV_NAME'."
        exit 1
        ;;
esac

# 3. Environment File Setup
echo "🧪 Syncing environment file..."
cp "$BASE_PATH/deploy/.env_${ENV_NAME}" "$(pwd)/.env"
git rm --cached .env 2>/dev/null || true

# 4. Django Tasks
echo "⚙️  Running Django tasks..."
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput

# 5. Restart Services
echo "🔁 Restarting Services..."
SERVICE_NAME="gunicorn-${ENV_NAME}"
sudo systemctl restart "$SERVICE_NAME" || sudo systemctl restart gunicorn
sudo systemctl reload nginx

echo "------------------------------------------"
echo "🎉 $ENV_NAME_UPPER Deployment Complete!"
echo "------------------------------------------"
