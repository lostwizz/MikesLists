#!/usr/bin/env bash
# ==============================================================================
# backup.sh
# Backup Script for Raspberry Pi 5
# Backs up Django dev/test/live environments and system configs
# Stores everything in /mnt/AlienMikesBackup/softwareBackups with timestamped filenames
# Keeps only the newest 15 backups
#
# __version__ = "0.1.0.000055-dev"
# ==============================================================================

set -euo pipefail

BACKUP_ROOT="/mnt/AlienMikesBackup"
BACKUP_SUBDIR="/softwareBackups"
TIMESTAMP="$(date +'%Y-%m-%d_%H-%M-%S')"
TARGET_DIR="${BACKUP_ROOT}${BACKUP_SUBDIR}"
LOGFILE="${TARGET_DIR}/backup-${TIMESTAMP}.log"

ENV_DIRS=(
    "/srv/django/venv-dev"
    "/srv/django/venv-test"
    "/srv/django/venv-live"
)

CONFIG_DIRS=(
    "/etc/nginx"
    "/etc/systemd/system"
    "/etc/ssh"
    "/etc/dhcpcd.conf"
    "/etc/fstab"
    "/etc/hosts"
)

# ------------------------------------------------------------------------------
# Ensure mount point is connected
# ------------------------------------------------------------------------------
if ! mountpoint -q "${BACKUP_ROOT}"; then
    echo "[$(date +'%F %T')] ERROR: Backup location not mounted: ${BACKUP_ROOT}"
    exit 1
fi

mkdir -p "${TARGET_DIR}"

log() {
    echo "[$(date +'%F %T')] $*" | tee -a "${LOGFILE}"
}

log "=== Starting backup at ${TIMESTAMP} ==="

# ------------------------------------------------------------------------------
# 1. Backup environments
# ------------------------------------------------------------------------------
for ENV in "${ENV_DIRS[@]}"; do
    NAME=$(basename "${ENV}")
    OUTFILE="${TARGET_DIR}/${NAME}-${TIMESTAMP}.tar.gz"

    if [[ -d "${ENV}" ]]; then
        log "Archiving environment: ${ENV}"
        tar -czf "${OUTFILE}" "${ENV}" 2>>"${LOGFILE}"
    else
        log "WARNING: Environment directory not found: ${ENV}"
    fi
done

# ------------------------------------------------------------------------------
# 2. Backup system configs
# ------------------------------------------------------------------------------
CONFIG_OUT="${TARGET_DIR}/configs-${TIMESTAMP}.tar.gz"
log "Archiving system configs"

# Allow tar to fail without killing the script
tar -czf "${CONFIG_OUT}" "${CONFIG_DIRS[@]}" 2>>"${LOGFILE}" \
    || log "WARNING: Some config files could not be archived (permission denied or missing)"


# ------------------------------------------------------------------------------
# 3. Backup installed packages
# ------------------------------------------------------------------------------
log "Saving installed package list"
dpkg --get-selections > "${TARGET_DIR}/packages-${TIMESTAMP}.list"

# ------------------------------------------------------------------------------
# 4. Backup Python requirements for each environment
# ------------------------------------------------------------------------------
for ENV in "${ENV_DIRS[@]}"; do
    NAME=$(basename "${ENV}")
    REQ_OUT="${TARGET_DIR}/pip-${NAME}-${TIMESTAMP}.txt"

    if [[ -d "${ENV}" ]]; then
        if [[ -f "${ENV}/bin/pip" ]]; then
            log "Saving pip freeze for ${NAME}"
            "${ENV}/bin/pip" freeze > "${REQ_OUT}" 2>>"${LOGFILE}"
        else
            log "WARNING: No venv found for ${NAME}"
        fi
    fi
done

# ------------------------------------------------------------------------------
# 5. Cleanup old backups (keep only the newest 15)
# ------------------------------------------------------------------------------
log "Keeping only the newest 15 backups"

# Use a subshell to avoid changing the main script's working directory
(
    cd "${TARGET_DIR}" || exit

    # Identify timestamps of logs older than the newest 15
    # sed extracts the unique YYYY-MM-DD_HH-MM-SS string
    OLD_TIMESTAMPS=$(ls -1t backup-*.log 2>/dev/null | tail -n +16 | sed 's/backup-\(.*\)\.log/\1/')

    if [[ -n "$OLD_TIMESTAMPS" ]]; then
        for ts in $OLD_TIMESTAMPS; do
            log "Deleting old backup set with timestamp: $ts"
            # Deletes all files (log, tar.gz, list, txt) associated with this timestamp
            rm -f *-"${ts}".*
        done
    else
        log "No old backups to clean up."
    fi
)

log "=== Backup completed successfully ==="
