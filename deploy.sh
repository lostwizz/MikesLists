#!/bin/bash
# ==========================================
# Django deploy changes to dev/test/live
# ==========================================
# __version__="0.2.2-stable"

set -euo pipefail

# 1. Detect environment from folder name
ENV_NAME=$(basename "$(pwd)" | sed 's/MikesLists_//')
ENV_NAME_UPPER=$(echo "$ENV_NAME" | tr '[:lower:]' '[:upper:]')

echo "------------------------------------------"
echo "🚀 DEPLOYING TO: $ENV_NAME_UPPER"
echo "------------------------------------------"

# 2. GIT AUTOMATION
# On DEV: Auto-commit and Push
# On TEST/LIVE: Reset local folder to match GitHub exactly
if [[ "$ENV_NAME" == "dev" ]]; then
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "📦 DEV: Changes detected. Committing and Pushing..."
        MESSAGE="${1:-"Automatic deploy: $(date)"}"
        git add .
        git commit -m "$MESSAGE"
        git push origin "$ENV_NAME"
    else
        echo "✅ DEV: No local changes to commit."
    fi
else
    echo "🔄 $ENV_NAME_UPPER: Forcing sync with GitHub..."
    # Ensure we fetch the latest from all branches
    git fetch --all

    # CRITICAL: This overwrites local files with the latest from the branch.
    # If core.py is still old, make sure you merged 'dev' into 'test' on GitHub first.
    git reset --hard origin/"$ENV_NAME"
fi

# 3. ENVIRONMENT FILE SETUP
ENV_SOURCE="/srv/django/deploy/.env_${ENV_NAME}"
ENV_TARGET="/srv/django/MikesLists_${ENV_NAME}/.env"

echo "🧪 Setting environment file..."
if [[ -f "$ENV_SOURCE" ]]; then
    cp "$ENV_SOURCE" "$ENV_TARGET"
else
    echo "❌ ERROR: Missing $ENV_SOURCE"
    exit 1
fi

# 4. DJANGO TASKS
echo "⚙️  Running Django tasks..."
# This ensures your migrations and static files are updated
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput

# 5. RESTART SERVICES
# This is mandatory because Django loads settings (like core.py) at startup
echo "🔁 Restarting Gunicorn and Nginx..."

# Check if the specific service unit exists
if systemctl list-unit-files | grep -q "gunicorn-${ENV_NAME}.service"; then
    sudo systemctl restart gunicorn-"$ENV_NAME"
else
    # Fallback to your primary gunicorn service if the environment-specific one isn't found
    echo "⚠️  gunicorn-${ENV_NAME}.service not found. Restarting main gunicorn service..."
    sudo systemctl restart gunicorn || echo "❌ Could not restart Gunicorn."
fi

sudo systemctl reload nginx

echo "------------------------------------------"
echo "🎉 Deployment to $ENV_NAME_UPPER complete!"
echo "------------------------------------------"
