#!/bin/bash
# ==========================================
# Django Multi-Env Deploy Script (V7 - Stable)
# ==========================================
set -euo pipefail

# 1. Initialize variables early to avoid "unbound variable" errors
BASE_PATH="/srv/django"
ENV_NAME=$(basename "$(pwd)" | sed 's/MikesLists_//')
ENV_NAME_UPPER=$(echo "$ENV_NAME" | tr '[:lower:]' '[:upper:]')

echo "------------------------------------------"
echo "🚀 TARGET ENV: $ENV_NAME_UPPER"
echo "------------------------------------------"

# 2. Execute Logic per Environment
case "$ENV_NAME" in
    dev)
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

        git fetch origin
        git checkout "$ENV_NAME" 2>/dev/null || git checkout -b "$ENV_NAME"

        # Try a clean merge first
        if ! git merge "origin/$SOURCE_BRANCH" --no-edit -X theirs; then
            echo "⚠️  Merge blocked. Forcing local state to match $SOURCE_BRANCH..."
            git reset --hard "origin/$SOURCE_BRANCH"
        fi

        # Ensure the remote branch is updated
        git push origin "$ENV_NAME" --force
        ;;

    *)
        echo "❌ ERROR: Unknown environment '$ENV_NAME'."
        exit 1
        ;;
esac

# 3. Environment File Setup
echo "🧪 Syncing environment file..."
ENV_SOURCE="$BASE_PATH/deploy/.env_${ENV_NAME}"
ENV_TARGET="$(pwd)/.env"

if [[ -f "$ENV_SOURCE" ]]; then
    cp "$ENV_SOURCE" "$ENV_TARGET"
    # Ensure Git never tracks the active .env
    git rm --cached .env 2>/dev/null || true
else
    echo "⚠️ Warning: $ENV_SOURCE not found."
fi

# 4. Django Tasks
echo "⚙️  Running Django tasks..."
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput

# 5. Restart Services
echo "🔁 Restarting Services..."
SERVICE_NAME="gunicorn-${ENV_NAME}"

# Check if the specific service unit exists
if systemctl list-unit-files | grep -q "${SERVICE_NAME}.service"; then
    sudo systemctl restart "$SERVICE_NAME"
else
    # Fallback to standard gunicorn if naming differs
    sudo systemctl restart gunicorn || echo "❌ Could not restart Gunicorn."
fi

sudo systemctl reload nginx

echo "------------------------------------------"
echo "🎉 $ENV_NAME_UPPER Deployment Complete!"
echo "------------------------------------------"
