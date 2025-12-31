#!/usr/bin/env bash
set -euo pipefail

# --- CONFIGURATION ---
ENV="dev"
PROJECT_DIR="/srv/django/MikesLists_dev"
VENV_PATH="/srv/django/venv-dev/bin/activate"
SETTINGS="MikesLists.settings.dev"
SERVICE_NAME="gunicorn-MikesLists-dev.service"

echo "=== STARTING CONSOLIDATED $ENV WORKFLOW ==="

cd "$PROJECT_DIR"

# 1. AUTOMATED GIT WORKFLOW
if [[ -n "$(git status --porcelain)" ]]; then
    echo "Detected uncommitted changes. Preparing to push..."
    
    # Ask for a commit message if not provided as an argument
    if [ -z "${1:-}" ]; then
        read -p "Enter commit message: " COMMIT_MSG
    else
        COMMIT_MSG="$1"
    fi

    git add .
    git commit -m "$COMMIT_MSG"
    echo "✔ Changes committed."
else
    echo "No local changes to commit."
fi

echo "Pushing to origin $ENV..."
git push origin "$ENV"

# 2. RUN SAFETY CHECKS (From your original script)
echo "Running safety checks..."
git fetch origin
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse "origin/$ENV")

if [[ "$LOCAL_HASH" != "$REMOTE_HASH" ]]; then
    echo "ERROR: Local branch and Remote branch are out of sync."
    exit 1
fi
echo "✔ Safety checks passed."

# 3. SERVER DEPLOYMENT TASKS
echo "Creating rollback tag..."
git tag -f rollback_before_deploy
git push -f origin rollback_before_deploy

echo "Activating virtual environment..."
source "$VENV_PATH"

echo "Applying migrations..."
python manage.py migrate --settings="$SETTINGS"

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings="$SETTINGS"

echo "Restarting service..."
sudo systemctl restart "$SERVICE_NAME"

echo "✅ $ENV Deployment and Push Complete!"
