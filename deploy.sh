#!/bin/bash
# ==========================================
# Django Environment-Aware Deploy
# ==========================================
set -euo pipefail

# 1. Detect environment from folder name
# Assumes folder naming convention: MikesLists_dev, MikesLists_test, etc.
ENV_NAME=$(basename "$(pwd)" | sed 's/MikesLists_//')
ENV_NAME_UPPER=$(echo "$ENV_NAME" | tr '[:lower:]' '[:upper:]')
BASE_PATH="/srv/django"

echo "------------------------------------------"
echo "🚀 TARGET ENV: $ENV_NAME_UPPER"
echo "------------------------------------------"

# 2. Define Logic per Environment
case "$ENV_NAME" in
    dev)
        echo "📦 DEV: Committing and Pushing local changes..."
        if [[ -n "$(git status --porcelain)" ]]; then
            MESSAGE="${1:-"Dev update: $(date)"}"
            git add .
            git commit -m "$MESSAGE"
            git push origin dev
        else
            echo "✅ No changes to commit in DEV."
            git push origin dev || echo "Already up to date."
        fi
        ;;

    test)
        echo "🔄 TEST: Merging changes from DEV..."
        git fetch origin
        git checkout test
        if git merge origin/dev --no-edit; then
            git push origin test
        else
            echo "❌ ERROR: Merge conflict between Dev and Test."
            echo "Action: Resolve conflicts manually, commit, and re-run."
            exit 1
        fi
        ;;

    live)
        echo "🔥 LIVE: Merging changes from TEST..."
        git fetch origin
        git checkout live
        if git merge origin/test --no-edit; then
            git push origin live
        else
            echo "❌ ERROR: Merge conflict between Test and Live."
            echo "Action: Ensure Test is fully merged and pushed before Live."
            exit 1
        fi
        ;;

    *)
        echo "❌ ERROR: Could not identify environment from folder name '$ENV_NAME'."
        echo "Ensure you are in MikesLists_dev, MikesLists_test, or MikesLists_live."
        exit 1
        ;;
esac

# 3. Shared Deployment Tasks (Runs for all environments after Git is synced)
echo "🧪 Updating .env file..."
ENV_SOURCE="$BASE_PATH/deploy/.env_${ENV_NAME}"
if [[ -f "$ENV_SOURCE" ]]; then
    cp "$ENV_SOURCE" "$(pwd)/.env"
else
    echo "⚠️  Warning: $ENV_SOURCE not found."
fi

echo "⚙️  Running Django tasks..."
# Handling common migration errors
if ! python3 manage.py migrate --noinput; then
    echo "❌ ERROR: Migration failed!"
    echo "Action: Check 'python3 manage.py showmigrations' or logs."
    exit 1
fi

python3 manage.py collectstatic --noinput

# 4. Restart Services
echo "🔁 Restarting Gunicorn and Nginx..."
SERVICE_NAME="gunicorn-${ENV_NAME}"

if systemctl list-unit-files | grep -q "${SERVICE_NAME}.service"; then
    sudo systemctl restart "$SERVICE_NAME"
else
    echo "⚠️  ${SERVICE_NAME}.service not found. Trying generic gunicorn..."
    sudo systemctl restart gunicorn || echo "❌ Service restart failed."
fi

sudo systemctl reload nginx

echo "------------------------------------------"
echo "🎉 $ENV_NAME_UPPER Deployment Complete!"
echo "------------------------------------------"
