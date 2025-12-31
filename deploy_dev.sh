#!/usr/bin/env bash
set -euo pipefail

ENV="dev"


echo "Running safety checks for ENV=${ENV}..."

# 1. Ensure we are on the correct branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "$ENV" ]]; then
    echo "ERROR: You are on branch '$CURRENT_BRANCH', but this script deploys the '$ENV' branch."
    echo "Aborting deployment."
    exit 1
fi

# 2. Ensure there are no uncommitted changes
if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: There are uncommitted changes in the working directory."
    echo "Please commit or stash them before deploying."
    git status
    exit 1
fi

# 3. Ensure local branch is up to date with origin/ENV
git fetch origin
LOCAL_HASH=$(git rev-parse "$ENV")
REMOTE_HASH=$(git rev-parse "origin/$ENV")

if [[ "$LOCAL_HASH" != "$REMOTE_HASH" ]]; then
    echo "ERROR: Local '$ENV' branch is not up to date with origin/$ENV."
    echo "Please run: git pull origin $ENV"
    exit 1
fi

echo "✔ Safety checks passed for ENV=${ENV}."



echo "=== DEPLOY DEV ==="
LOGFILE="/srv/django/deploy_logs/$(date +'%Y-%m-%d_%H-%M-%S')_${ENV}.log"
mkdir -p /srv/django/deploy_logs
exec > >(tee -a "$LOGFILE") 2>&1

cd /srv/django/MikesLists_dev

echo "Creating rollback tag..."
git tag -f rollback_before_deploy
git push -f origin rollback_before_deploy

echo "Pulling latest code from origin/dev..."
git fetch origin
git checkout dev
git pull origin dev

echo "Activating virtual environment..."
source /srv/django/venv-dev/bin/activate

echo "Applying migrations..."
python manage.py migrate --settings=MikesLists.settings.dev

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=MikesLists.settings.dev

echo "Restarting gunicorn-dev..."
#sudo systemctl restart gunicorn-dev.service
sudo systemctl restart gunicorn-MikesLists-dev.service

echo "DEV deployment complete."
