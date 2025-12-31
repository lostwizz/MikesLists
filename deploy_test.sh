#!/usr/bin/env bash
set -euo pipefail

ENV="test"

echo "=== DEPLOY TEST ==="

# Logging
LOGFILE="/srv/django/deploy_logs/$(date +'%Y-%m-%d_%H-%M-%S')_${ENV}.log"
mkdir -p /srv/django/deploy_logs
exec > >(tee -a "$LOGFILE") 2>&1

cd /srv/django/MikesLists_test

echo "--- Checking branch ---"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "test" ]]; then
    echo "ERROR: Not on test branch (current: $BRANCH). Aborting."
    exit 1
fi

echo "--- Checking for uncommitted changes ---"
if ! git diff-index --quiet HEAD --; then
    echo "ERROR: Uncommitted changes in TEST. Aborting."
    exit 1
fi

echo "--- Creating rollback tag ---"
git tag -f rollback_before_deploy_test
git push -f origin rollback_before_deploy_test

echo "--- Pulling latest code ---"
git fetch origin
git pull origin test

echo "--- Activating virtual environment ---"
source /srv/django/venv-test/bin/activate

echo "--- Applying migrations ---"
python manage.py migrate --settings=MikesLists.settings.test

echo "--- Collecting static files ---"
python manage.py collectstatic --noinput --settings=MikesLists.settings.test

echo "--- Restarting gunicorn-test ---"
#sudo systemctl restart gunicorn-test.service
sudo systemctl restart gunicorn-MikesLists-test.service

echo "=== TEST deployment complete ==="
