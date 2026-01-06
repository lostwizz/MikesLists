#!/usr/bin/env bash
set -e

BASE="/srv/django"
ENVS=("MikesLists_dev" "MikesLists_live" "MikesLists_test")

echo "=== Fixing Django Permissions ==="

for env in "${ENVS[@]}"; do
    DIR="$BASE/$env"
    echo "--- Fixing $env ---"

    # Fix code ownership
    sudo chown -R pi:pi "$DIR"

    # Fix static files
    if [[ -d "$DIR/staticfiles_collected" ]]; then
        sudo chown -R pi:pi "$DIR/staticfiles_collected"
        sudo chmod -R 755 "$DIR/staticfiles_collected"
    fi

    # Fix media files
    if [[ -d "$DIR/media" ]]; then
        sudo chown -R pi:www-data "$DIR/media"
        sudo chmod -R 775 "$DIR/media"
    fi

    # Fix Gunicorn socket
    if [[ -f "$DIR/MikesLists.sock" ]]; then
        sudo chown www-data:www-data "$DIR/MikesLists.sock"
        sudo chmod 660 "$DIR/MikesLists.sock"
    fi

    # Fix logs (choose your model)
    if [[ -d "$DIR/logs" ]]; then
        # If Gunicorn writes logs:
        sudo chown -R www-data:pi "$DIR/logs"
        sudo chmod -R 775 "$DIR/logs"

        # If YOU write logs instead, replace above with:
        # sudo chown -R pi:pi "$DIR/logs"
        # sudo chmod -R 755 "$DIR/logs"
    fi
done

echo "Permissions fixed."
