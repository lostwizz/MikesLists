#!/bin/bash
# ==========================================
# Django deploy changes to dev/test/live
# ==========================================
# __version__="0.2.0.00006-dev"

set -euo pipefail

###############################################
# DEPLOY SCRIPT — CLEAN, SAFE, NO SYMLINK HELL
###############################################

# Detect environment from folder name
ENV_NAME=$(basename "$(pwd)" | sed 's/MikesLists_//')
ENV_NAME_UPPER=$(echo "$ENV_NAME" | tr '[:lower:]' '[:upper:]')

echo "------------------------------------------"
echo "🚀 DEPLOYING TO: $ENV_NAME_UPPER"
echo "------------------------------------------"

###############################################
# 1. Ensure working tree is clean
###############################################
if [[ -n "$(git status --porcelain)" ]]; then
    echo "❌ ERROR: Working tree is dirty."
    echo "   Fix the following before deploying:"
    git status
    exit 1
fi

###############################################
# 2. Sync from Git
###############################################
echo "🔄 Pulling latest changes..."
git pull --rebase origin "$ENV_NAME"




###############################################
# 3. Copy correct .env file (NO SYMLINKS)
###############################################
ENV_SOURCE="/srv/django/deploy/.env_${ENV_NAME}"
ENV_TARGET="/srv/django/MikesLists_${ENV_NAME}/.env"

echo "🧪 Setting environment file:"
echo "    $ENV_SOURCE → $ENV_TARGET"

if [[ ! -f "$ENV_SOURCE" ]]; then
    echo "❌ ERROR: Missing $ENV_SOURCE"
    exit 1
fi

# Copy .env BEFORE Django runs
cp "$ENV_SOURCE" "$ENV_TARGET"


###############################################
# 3.5. copy the deploy.sh to the curent env
###############################################
ENV_SOURCE="/srv/django/deploy/deploy.sh"
ENV_TARGET="/srv/django/MikesLists_${ENV_NAME}/deploy.sh"

cp "$ENV_SOURCE" "$ENV_TARGET"


###############################################
# 4. Run Django tasks
###############################################
echo "⚙️  Running Django migrations..."
python3 manage.py migrate --noinput

echo "📦 Collecting static files..."
python3 manage.py collectstatic --noinput

###############################################
# 5. Restart services
###############################################
echo "🔁 Restarting Gunicorn..."
sudo systemctl restart gunicorn-"$ENV_NAME"

echo "🔁 Restarting Nginx..."
sudo systemctl reload nginx

###############################################
# DONE
###############################################
echo "🎉 Deployment to $ENV_NAME_UPPER complete!"
echo "------------------------------------------"
