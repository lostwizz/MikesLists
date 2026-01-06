#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Restore Script for Raspberry Pi 5
# Restores system configs, environments, packages, and Python venvs
# ==============================================================================

BACKUP_ROOT="/mnt/AlienMikesBackup"
RESTORE_TIMESTAMP="$1"

if [[ -z "${RESTORE_TIMESTAMP}" ]]; then
    echo "Usage: $0 <timestamp>"
    echo "Example: $0 2026-01-04_18-30-00"
    exit 1
fi

log() {
    echo "[$(date +'%F %T')] $*"
}

log "=== Starting restore for timestamp ${RESTORE_TIMESTAMP} ==="

# ------------------------------------------------------------------------------
# 1. Restore system configs
# ------------------------------------------------------------------------------
CONFIG_ARCHIVE="${BACKUP_ROOT}/configs-${RESTORE_TIMESTAMP}.tar.gz"
log "Restoring system configs"
sudo tar -xzf "${CONFIG_ARCHIVE}" -C /

# ------------------------------------------------------------------------------
# 2. Restore environments
# ------------------------------------------------------------------------------
for ENV in MikesLists_dev MikesLists_test MikesLists_live; do
    ARCHIVE="${BACKUP_ROOT}/${ENV}-${RESTORE_TIMESTAMP}.tar.gz"
    if [[ -f "${ARCHIVE}" ]]; then
        log "Restoring environment: ${ENV}"
        sudo tar -xzf "${ARCHIVE}" -C /
    else
        log "WARNING: Missing environment archive: ${ARCHIVE}"
    fi
done

# ------------------------------------------------------------------------------
# 3. Restore installed packages
# ------------------------------------------------------------------------------
PKG_LIST="${BACKUP_ROOT}/packages-${RESTORE_TIMESTAMP}.list"
log "Restoring package selections"
sudo dpkg --set-selections < "${PKG_LIST}"
sudo apt-get -y dselect-upgrade

# ------------------------------------------------------------------------------
# 4. Rebuild Python venvs and reinstall requirements
# ------------------------------------------------------------------------------
for ENV in MikesLists_dev MikesLists_test MikesLists_live; do
    ENV_DIR="/srv/django/${ENV}"
    REQ_FILE="${BACKUP_ROOT}/pip-${ENV}-${RESTORE_TIMESTAMP}.txt"

    if [[ -d "${ENV_DIR}" ]]; then
        log "Rebuilding venv for ${ENV}"
        python3 -m venv "${ENV_DIR}/venv"
        "${ENV_DIR}/venv/bin/pip" install --upgrade pip
        "${ENV_DIR}/venv/bin/pip" install -r "${REQ_FILE}"
    fi
done

# ------------------------------------------------------------------------------
# 5. Reload systemd
# ------------------------------------------------------------------------------
log "Reloading systemd"
sudo systemctl daemon-reload

log "=== Restore completed successfully ==="

