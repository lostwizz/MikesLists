#!/bin/bash
# ==========================================
# Django deploy changes to dev/test/live
# ==========================================
# __version__="0.2.1-stable"

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
    git fetch origin "$ENV_NAME"
    # This command is critical: it overwrites any local core.py blocks
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
# Ensure the correct venv is used if necessary
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput

# 5. RESTART SERVICES
# Settings are loaded at process start; a restart is mandatory
echo "🔁 Restarting Gunicorn and Nginx..."

# Use a generic name if 'gunicorn-test' doesn't exist, or
# sudo systemctl restart gunicorn
if systemctl list-unit-files | grep -q "gunicorn-${ENV_NAME}.service"; then
    sudo systemctl restart gunicorn-"$ENV_NAME"
else
    echo "⚠️  Warning: gunicorn-${ENV_NAME}.service not found. Attempting generic restart..."
    sudo systemctl restart gunicorn || echo "❌ Could not restart Gunicorn."
fi

sudo systemctl reload nginx

echo "------------------------------------------"
echo "🎉 Deployment to $ENV_NAME_UPPER complete!"
echo "------------------------------------------"
