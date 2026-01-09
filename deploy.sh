#!/bin/bash
# ==========================================
# Django Multi-Env Deploy Script
# Workflow: Dev (Commit) -> Test (Merge Dev) -> Live (Merge Test)
# ==========================================
set -euo pipefail

# 1. Detect environment based on directory name
ENV_NAME=$(basename "$(pwd)" | sed 's/MikesLists_//')
ENV_NAME_UPPER=$(echo "$ENV_NAME" | tr '[:lower:]' '[:upper:]')
BASE_PATH="/srv/django"

echo "------------------------------------------"
echo "🚀 TARGET ENV: $ENV_NAME_UPPER"
echo "------------------------------------------"

# 2. Execute Logic per Environment
case "$ENV_NAME" in
    dev)
        echo "📦 DEV: Committing and Pushing local changes..."
        # Remove .env from tracking if it was accidentally added
        git rm --cached .env 2>/dev/null || true

        if [[ -n "$(git status --porcelain)" ]]; then
            MESSAGE="${1:-"Dev update: $(date)"}"
            git add .
            git commit -m "$MESSAGE"
            git push origin dev
        else
            echo "✅ No local changes to commit. Pushing existing commits..."
            git push origin dev || echo "Up to date."
        fi
        ;;

    test|live)
        # Set source: Test pulls from Dev | Live pulls from Test
        SOURCE_BRANCH="dev"
        [[ "$ENV_NAME" == "live" ]] && SOURCE_BRANCH="test"

        echo "🔄 $ENV_NAME_UPPER: Force-merging changes from $SOURCE_BRANCH..."

        # FIX: Discard local changes to the script itself or gitignore
        # to prevent "overwritten by merge" errors.
        git checkout .gitignore deploy.sh 2>/dev/null || true

        git fetch origin
        git checkout "$ENV_NAME"

        # STRATEGY: '-X theirs' automatically resolves conflicts by favoring
        # the incoming code from your source branch.
        if git merge "origin/$SOURCE_BRANCH" --no-edit -X theirs; then
            git push origin "$ENV_NAME"
        else
            echo "❌ ERROR: Merge failed. You may have a manual conflict."
            echo "Try running: git merge --abort"
            exit 1
        fi
        ;;

    *)
        echo "❌ ERROR: Could not identify environment from folder '$ENV_NAME'."
        exit 1
        ;;
esac

# 3. Environment File Setup
echo "🧪 Syncing environment file..."
ENV_SOURCE="$BASE_PATH/deploy/.env_${ENV_NAME}"
ENV_TARGET="$(pwd)/.env"

if [[ -f "$ENV_SOURCE" ]]; then
    # Copy the master .env for this specific stage
    cp "$ENV_SOURCE" "$ENV_TARGET"
    # Safety: Ensure git never tracks this local copy
    git rm --cached .env 2>/dev/null || true
else
    echo "⚠️  Warning: $ENV_SOURCE not found. Check /srv/django/deploy/"
fi

# 4. Django Tasks
echo "⚙️  Running Django tasks..."
# Ensure we use python3 and handle migration errors
if ! python3 manage.py migrate --noinput; then
    echo "❌ ERROR: Database migration failed. Check your models."
    exit 1
fi

python3 manage.py collectstatic --noinput

# 5. Restart Services
echo "🔁 Restarting Gunicorn and Nginx..."
SERVICE_NAME="gunicorn-${ENV_NAME}"

# Try to restart specific service, fallback to generic if necessary
if systemctl list-unit-files | grep -q "${SERVICE_NAME}.service"; then
    sudo systemctl restart "$SERVICE_NAME"
else
    echo "⚠️  $SERVICE_NAME not found. Attempting generic gunicorn restart..."
    sudo systemctl restart gunicorn || echo "❌ Service restart failed."
fi

sudo systemctl reload nginx

echo "------------------------------------------"
echo "🎉 $ENV_NAME_UPPER Deployment Complete!"
echo "------------------------------------------"
