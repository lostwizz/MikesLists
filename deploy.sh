#!/usr/bin/env bash
set -euo pipefail

# --- 1. AUTO-DETECT ENVIRONMENT ---
ENV_ARG="${1:-}"
if [[ -z "$ENV_ARG" ]]; then
    if [[ "$PWD" == *"_dev"* ]]; then ENV="dev";
    elif [[ "$PWD" == *"_test"* ]]; then ENV="test";
    elif [[ "$PWD" == *"_live"* ]]; then ENV="live";
    else
        echo -e "\e[31mError: Could not detect environment.\e[0m"
        exit 1
    fi
else
    ENV="$ENV_ARG"
fi

PROJECT_DIR="/srv/django/MikesLists_$ENV"
VENV_BIN="/srv/django/venv-$ENV/bin"
SERVICE_NAME="gunicorn-MikesLists-$ENV.service"

echo -e "\e[35m------------------------------------------"
echo -e "🚀 DEPLOYING TO: ${ENV^^}"
echo -e "------------------------------------------\e[0m"

cd "$PROJECT_DIR"

# --- 2. BRANCH PROMOTION LOGIC ---
echo -e "\e[34m🔄 Handling Git Sync...\e[0m"
git fetch origin

if [[ "$ENV" == "dev" ]]; then
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "📦 Changes detected in DEV. Committing..."
        read -p "Enter commit message: " COMMIT_MSG
        git add .
        git commit -m "$COMMIT_MSG"
        git push origin dev
    fi
elif [[ "$ENV" == "test" ]]; then
    echo "🔀 Merging DEV branch into TEST environment..."
    git checkout test
    git merge origin/dev --no-edit
    git push origin test
elif [[ "$ENV" == "live" ]]; then
    echo "🔀 Merging TEST branch into LIVE environment..."
    git checkout live
    git merge origin/test --no-edit
    git push origin live
fi

# --- NEW: Sync Local Binaries ---
echo -e "\e[34m📂 Syncing local binaries...\e[0m"
# Create the directory if it doesn't exist
mkdir -p "$PROJECT_DIR/include_bin"
# Copy files from your pi home bin to the project folder
cp -r /home/pi/bin/* "$PROJECT_DIR/include_bin/"


# --- 3. DJANGO TASKS ---
echo -e "\e[34m⚙️  Running Django Tasks...\e[0m"
# Use the specific venv python
$VENV_BIN/python manage.py migrate
$VENV_BIN/python manage.py collectstatic --noinput

# --- 4. RESTART SERVICE ---
echo -e "\e[34m♻️  Restarting $SERVICE_NAME...\e[0m"
sudo systemctl restart "$SERVICE_NAME"

# --- 5. AUTOMATED VERIFICATION ---
echo -e "\e[35m------------------------------------------"
echo -e "🔍 RUNNING HEALTH CHECK..."
echo -e "------------------------------------------\e[0m"

# Call your existing chk.sh script
if command -v chk.sh &> /dev/null; then
    chk.sh
else
    # Fallback if chk.sh isn't in path
    ~/bin/chk.sh
fi

VERSION=$(git rev-parse --short HEAD)


#echo -e "\n\e[32m🎉 ${ENV^^} Deployment Finished!\e[0m"
#echo -e "\n\e[32m🎉 ${ENV^^} is up and working!\e[0m"
echo -e "\n\e[32m🎉 ${ENV^^} is up and working! (v.$VERSION)\e[0m"
