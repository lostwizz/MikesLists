#!/usr/bin/env bash
set -euo pipefail

# --- 1. AUTO-DETECT ENVIRONMENT ---
ENV_ARG="${1:-}"
if [[ -z "$ENV_ARG" ]]; then
    if [[ "$PWD" == *"_dev"* ]]; then ENV="dev";
    elif [[ "$PWD" == *"_test"* ]]; then ENV="test";
    elif [[ "$PWD" == *"_live"* ]]; then ENV="live";
    else
        echo "Error: Could not detect environment. Use: ./deploy.sh [dev|test|live]"
        exit 1
    fi
else
    ENV="$ENV_ARG"
fi

# --- 2. DYNAMIC CONFIGURATION ---
PROJECT_DIR="/srv/django/MikesLists_$ENV"
VENV_PATH="/srv/django/venv-$ENV/bin/activate"
SETTINGS="MikesLists.settings.$ENV"
SERVICE_NAME="gunicorn-MikesLists-$ENV.service"
BACKUP_DIR="/srv/django/backups"

echo "------------------------------------------"
echo "🚀 DEPLOYING TO: ${ENV^^}"
echo "------------------------------------------"

cd "$PROJECT_DIR"

# --- 3. GIT AUTOMATION (Only if in DEV) ---
# Usually, we only "commit" directly in dev. Test and Live get code via Merge.
if [[ "$ENV" == "dev" ]] && [[ -n "$(git status --porcelain)" ]]; then
    echo "📦 Changes detected in DEV. Committing..."
    read -p "Enter commit message: " COMMIT_MSG
    git add .
    git commit -m "$COMMIT_MSG"
    git push origin "$ENV"
fi

# --- 4. SAFETY CHECK: SYNC ---
git fetch origin
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse "origin/$ENV")

if [[ "$LOCAL_HASH" != "$REMOTE_HASH" ]]; then
    echo "❌ ERROR: Local branch and Remote ($ENV) are out of sync."
    exit 1
fi

# --- 5. DATABASE BACKUP ---
#echo "💾 Backing up database..."
#mkdir -p "$BACKUP_DIR"
## This assumes you are using SQLite. If using Postgres/MySQL, this command changes.
#cp db.sqlite3 "$BACKUP_DIR/${ENV}_$(date +%Y%m%d_%H%M%S).sqlite3"
#echo "✔ Backup saved to $BACKUP_DIR"

# --- 6. DJANGO TASKS ---
source "$VENV_PATH"
echo "⚙️  Running migrations..."
python manage.py migrate --settings="$SETTINGS"

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --settings="$SETTINGS"

# --- 7. RESTART ---
echo "♻️  Restarting $SERVICE_NAME..."
sudo systemctl restart "$SERVICE_NAME"

echo "------------------------------------------"
echo "🎉 ${ENV^^} IS LIVE!"
echo "------------------------------------------"
