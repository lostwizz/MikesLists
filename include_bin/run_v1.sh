#!/bin/bash
# ==========================================
# Django run script to make sure all is ready for development
#
# ==========================================
# __version__ = "0.1.0.000050-dev"

echo "--- Starting MikesLists Dev Environment Checks ---"

# 1. Verify Environment File
echo "[1/7] Verifying environment file..."
if [ -f "/srv/django/MikesLists_dev/.env" ]; then
    echo "✔ .env file found."
else
    echo "✘ ERROR: .env file is missing at /srv/django/MikesLists_dev/.env"
    exit 1
fi

# 2. Cleanup Orphaned Processes
echo "[2/7] Hunting for orphaned Django processes on port 8000..."
ORPHAN_PID=$(lsof -t -i:8000)
if [ ! -z "$ORPHAN_PID" ]; then
    echo "⚠ Found orphaned process (PID: $ORPHAN_PID). Cleaning up..."
    sudo kill -9 $ORPHAN_PID
else
    echo "✔ No orphaned processes found."
fi

# 3. Check for Pending Migrations
echo "[3/7] Checking for pending database migrations..."
# Using the virtual env python to run the check
if ! /srv/django/venv-dev/bin/python /srv/django/MikesLists_dev/manage.py showmigrations | grep -q '\[ \]'; then
    echo "✔ Database schema is up to date."
else
    echo "⚠ WARNING: There are unapplied migrations!"
    echo "Please run: python manage.py migrate"
    # Optional: uncomment 'exit 1' if you want to force migrations before starting
    # exit 1
fi

# 4. Refresh Services
echo "[4/7] Restarting systemd services..."
sudo systemctl daemon-reload || { echo "✘ Failed to reload daemon"; exit 1; }
sudo systemctl restart mikeslists-dev.service || { echo "✘ Failed to start Django service"; exit 1; }
sudo systemctl restart nginx || { echo "✘ Failed to restart Nginx"; exit 1; }

# 5. Verify Django Service Status
echo "[5/7] Checking Django service status..."
if ! systemctl is-active --quiet mikeslists-dev.service; then
    echo "✘ ERROR: Django service failed to stay active."
    echo "Recent logs for mikeslists-dev.service:"
    sudo journalctl -u mikeslists-dev.service -n 20 --no-pager
    exit 1
fi

# 6. Verify Nginx Listener
echo "[6/7] Checking Nginx port 8999..."
if ss -tuln | grep -q ":8999"; then
    echo "✔ Nginx is listening on port 8999."
else
    echo "✘ ERROR: Nginx is NOT listening on port 8999."
    exit 1
fi

# 7. Internal Connectivity Check
echo "[7/7] Verifying Django response (Port 8000)..."
echo "Waiting for Django to initialize..."
sleep 2  # Give Django 5 seconds to boot up
if curl -s --head http://127.0.0.1:8000 | grep -q "200 OK"; then
    echo "✔ Django is responding correctly."
else
    echo "✘ ERROR: Django is NOT responding on port 8000."
    exit 1
fi

echo "--- All checks passed. Starting Log Follow ---"
# Add a visual separator in the logs
#sudo systemd-cat -t "DEV_START" echo "---------- NEW DEV SESSION STARTED AT $(date) ----------"
#Bash

# Add a visual separator that WILL show up in your filtered logs
#echo "---------- NEW DEV SESSION STARTED AT $(date) ----------" | sudo logger -t mikeslists-dev.service
echo "---------- NEW DEV SESSION STARTED AT $(date) ----------" | sudo systemd-cat -u mikeslists-dev.service




# Follow the journal logs
sudo journalctl -u mikeslists-dev.service -f
