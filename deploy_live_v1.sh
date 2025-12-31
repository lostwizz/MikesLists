#!/usr/bin/env bash
set -euo pipefail

ENV="live"

echo "=== DEPLOY LIVE ==="

# Logging
LOGFILE="/srv/django/deploy_logs/$(date +'%Y-%m-%d_%H-%M-%S')_${ENV}.log"
mkdir -p /srv/django/deploy_logs
exec > >(tee -a "$LOGFILE") 2>&1

cd /srv/django/MikesLists_live

echo "--- Checking branch ---"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "main" ]]; then
    echo "ERROR: Not on main branch (current: $BRANCH). Aborting."
    exit 1
fi

echo "--- Checking for uncommitted changes ---"
if ! git diff-index --quiet HEAD --; then
    echo "ERROR: Uncommitted changes in LIVE. Aborting."
    exit 1
fi

echo "--- Checking gunicorn-live status before deploy ---"
if ! systemctl is-active --quiet gunicorn-live.service; then
    echo "WARNING: gunicorn-live is not active before deploy."
fi

echo "--- Creating rollback tag ---"
git tag -f rollback_before_deploy_live
git push -f origin rollback_before_deploy_live

echo "--- Pulling latest code ---"
git fetch origin
git pull origin main

echo "--- Activating virtual environment ---"
source /srv/django/venv-live/bin/activate

echo "--- Applying migrations ---"
python manage.py migrate --settings=MikesLists.settings.live

echo "--- Collecting static files ---"
python manage.py collectstatic --noinput --settings=MikesLists.settings.live

echo "--- Restarting gunicorn-live ---"
#sudo systemctl restart gunicorn-live.service
sudo systemctl restart gunicorn-MikesLists-live.service

echo "=== LIVE deployment complete ==="
