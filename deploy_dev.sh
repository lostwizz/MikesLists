#!/usr/bin/env bash
set -euo pipefail

ENV="dev"

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
