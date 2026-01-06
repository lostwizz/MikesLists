#!/usr/bin/env bash
# ==========================================
# full_backup_image.sh
#   - Automatically detects NVMe/Root drive
#   - Optimized for NVMe (16M blocks)
#   - Post-backup .gz integrity health check
#   - Self-managing lock file (24h)
#
# __version__ = "0.1.0.000054-dev"
# ==========================================

set -euo pipefail

# Configuration
BACKUP_ROOT="/mnt/AlienMikesBackup"
BACKUP_SUBDIR="/softwareBackups"
TARGET_DIR="${BACKUP_ROOT}${BACKUP_SUBDIR}"
DATE="$(date +'%Y-%m-%d')"
TIMESTAMP="$(date +'%Y-%m-%d_%H-%M-%S')"

OUTPUT="${TARGET_DIR}/pi-full-backup-${DATE}.img.gz"
LOGFILE="${TARGET_DIR}/image-backup-${TIMESTAMP}.log"
LOCKFILE="/var/lock/pi_full_backup.lock"

# ------------------------------------------------------------------------------
# Logging Function
# ------------------------------------------------------------------------------
log() {
    echo "[$(date +'%F %T')] $*" | sudo tee -a "${LOGFILE}"
}

# ------------------------------------------------------------------------------
# 1. Prevent multiple runs per day (Self-Managing)
# ------------------------------------------------------------------------------
if [[ -f "${LOCKFILE}" ]]; then
    if [[ $(find "${LOCKFILE}" -mmin +1440) ]]; then
        echo "Old lock file found (>24h), removing..."
        sudo rm "${LOCKFILE}"
    else
        echo "Backup already completed within the last 24 hours."
        exit 0
    fi
fi

# ------------------------------------------------------------------------------
# 2. Wait for SMB share to be mounted
# ------------------------------------------------------------------------------
while ! mountpoint -q "${BACKUP_ROOT}"; do
    echo "Waiting for SMB share to mount at ${BACKUP_ROOT}..."
    sleep 300
done

mkdir -p "${TARGET_DIR}"
log "=== Starting Full Image Backup ==="

# ------------------------------------------------------------------------------
# 3. Auto-detect the Root Device (NVMe or SD)
# ------------------------------------------------------------------------------
ROOT_PART=$(findmnt -nvo SOURCE /)
ROOT_DISK=$(lsblk -no PKNAME "$ROOT_PART")
INPUT_DEV="/dev/${ROOT_DISK}"

if [[ ! -b "$INPUT_DEV" ]]; then
    log "ERROR: Could not determine root block device."
    exit 1
fi

log "Detected Root Device: ${INPUT_DEV}"
echo "${DATE}" | sudo tee "${LOCKFILE}" >/dev/null

# ------------------------------------------------------------------------------
# 4. Run optimized backup
# ------------------------------------------------------------------------------
log "Target File: ${OUTPUT}"
log "Running dd with 16M blocks and 20MB/s throttle..."

# Performance: bs=16M is ideal for NVMe; pv limits I/O to keep system snappy
sudo ionice -c3 nice -n 19 dd if="$INPUT_DEV" bs=16M iflag=fullblock status=progress 2>>"${LOGFILE}" \
    | pv -q -L 20m \
    | gzip -1 \
    | sudo tee "${OUTPUT}" >/dev/null

sync

# ------------------------------------------------------------------------------
# 5. Health Check: Verify GZIP Integrity
# ------------------------------------------------------------------------------
log "Verifying image integrity..."

if gzip -t "${OUTPUT}" 2>>"${LOGFILE}"; then
    log "HEALTH CHECK PASSED: Image is valid."
else
    log "CRITICAL ERROR: Image integrity check FAILED!"
    # We leave the lockfile so a failed backup isn't ignored
    exit 1
fi

# ------------------------------------------------------------------------------
# 6. Cleanup old logs (keep newest 5)
# ------------------------------------------------------------------------------
(
    cd "${TARGET_DIR}" || exit
    OLD_LOGS=$(ls -1t image-backup-*.log 2>/dev/null | tail -n +6)
    for oldlog in $OLD_LOGS; do
        sudo rm "$oldlog"
    done
)

log "=== Backup completed successfully ==="
