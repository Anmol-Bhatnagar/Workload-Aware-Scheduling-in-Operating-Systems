#!/usr/bin/env bash
# ==============================================================================
# Linux Block I/O Scheduler Safe Control and Restoration Helper
# ==============================================================================

set -euo pipefail

DEV="${1:-}"
ACTION="${2:-status}"
SCHEDULER="${3:-}"

if [ -z "$DEV" ]; then
    echo "Usage: $0 <device_name> [status|switch|restore] [scheduler_name]"
    echo "Example: $0 sda status"
    echo "Example: $0 sda switch mq-deadline"
    echo "Example: $0 sda restore"
    exit 1
fi

SYSFS_PATH="/sys/block/${DEV}/queue/scheduler"
BACKUP_FILE="/tmp/original_scheduler_${DEV}.txt"

if [ ! -f "$SYSFS_PATH" ]; then
    echo "Error: Device /sys/block/${DEV}/queue/scheduler does not exist."
    exit 1
fi

case "$ACTION" in
    status)
        echo "Device: ${DEV}"
        echo "Current & available schedulers: $(cat "$SYSFS_PATH")"
        if [ -w "$SYSFS_PATH" ]; then
            echo "Write permission: YES (current user can switch)"
        else
            echo "Write permission: NO (root/sudo required to change)"
        fi
        ;;
    switch)
        if [ -z "$SCHEDULER" ]; then
            echo "Error: Must specify target scheduler (e.g. mq-deadline, bfq, none)."
            exit 1
        fi
        # Backup current scheduler first if not backed up
        if [ ! -f "$BACKUP_FILE" ]; then
            # Extract bracketed scheduler
            CURRENT_SCHED=$(grep -o '\[.*\]' "$SYSFS_PATH" | tr -d '[]' || true)
            echo "$CURRENT_SCHED" > "$BACKUP_FILE"
            echo "Saved original scheduler: $CURRENT_SCHED to $BACKUP_FILE"
        fi
        echo "Switching ${DEV} to ${SCHEDULER}..."
        echo "$SCHEDULER" | sudo tee "$SYSFS_PATH" > /dev/null
        echo "Active scheduler is now: $(cat "$SYSFS_PATH")"
        ;;
    restore)
        if [ ! -f "$BACKUP_FILE" ]; then
            echo "No backup file found at $BACKUP_FILE. Cannot restore."
            exit 1
        fi
        ORIG=$(cat "$BACKUP_FILE")
        echo "Restoring ${DEV} to original scheduler: ${ORIG}..."
        echo "$ORIG" | sudo tee "$SYSFS_PATH" > /dev/null
        rm -f "$BACKUP_FILE"
        echo "Restoration complete. Current state: $(cat "$SYSFS_PATH")"
        ;;
    *)
        echo "Unknown action: $ACTION"
        exit 1
        ;;
esac
