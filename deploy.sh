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

        mkdir -p "$PROJECT_DIR/include_bin/log-dashboard"
        cp -rv /home/pi/log-dashboard/* "$PROJECT_DIR/include_bin/log-dashboard"

        mkdir -p "$PROJECT_DIR/include_bin/services"
        cp -rv /etc/systemd/system/full-backup.service   "$PROJECT_DIR/include_bin/services"
        cp -rv /etc/systemd/system/full-backup.timer     "$PROJECT_DIR/include_bin/services"
        cp -rv /etc/systemd/system/gunicorn-MikesLists-live.service     "$PROJECT_DIR/include_bin/services"
        cp -rv /etc/systemd/system/gunicorn-MikesLists-test.service     "$PROJECT_DIR/include_bin/services"
        cp -rv /etc/systemd/system/watcher.service     "$PROJECT_DIR/include_bin/services"
        cp -rv /etc/systemd/system/mikeslists-dev.service     "$PROJECT_DIR/include_bin/services"
        cp -rv /etc/systemd/system/check-ip-change.service     "$PROJECT_DIR/include_bin/services"

        cp -rv /usr/local/bin/check_ip_change.sh  "$PROJECT_DIR/include_bin/services"

        echo "📦 DEV: Committing and Pushing..."
        git rm --cached .env 2>/dev/null || true
        if [[ -n "$(git status --porcelain)" ]]; then
            git add .
            git commit -m "${1:-"Dev update: $(date)"}"
            git push origin dev
        else
            git push origin dev || echo "Already up to date."
        fi
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
