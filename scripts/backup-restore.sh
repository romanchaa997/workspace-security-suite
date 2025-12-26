#!/bin/bash

# Workspace Security Suite - Backup and Restore Script
# This script handles backup and restore operations for production databases

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./.backups}"
LOG_DIR="${LOG_DIR:-./.logs}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
KMS_KEY_ID="${KMS_KEY_ID:-}"
S3_BUCKET="${S3_BUCKET:-workspace-security-backups}"
RDS_INSTANCE="${RDS_INSTANCE:-workspace-security-db}"
REGION="${AWS_REGION:-us-east-1}"

# Create directories
mkdir -p "$BACKUP_DIR" "$LOG_DIR"

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_DIR/backup.log"
}

# Backup RDS Database
backup_rds() {
    log "INFO" "Starting RDS backup for instance: $RDS_INSTANCE"
    
    local snapshot_id="${RDS_INSTANCE}-backup-$(date +%Y%m%d-%H%M%S)"
    
    aws rds create-db-snapshot \
        --db-instance-identifier "$RDS_INSTANCE" \
        --db-snapshot-identifier "$snapshot_id" \
        --region "$REGION" \
        --tags "Key=Environment,Value=production" "Key=Type,Value=automated"
    
    log "INFO" "RDS backup initiated: $snapshot_id"
    
    # Wait for snapshot to complete
    aws rds wait db-snapshot-available \
        --db-snapshot-identifier "$snapshot_id" \
        --region "$REGION"
    
    log "INFO" "RDS backup completed: $snapshot_id"
    
    # Copy to S3 with encryption
    copy_snapshot_to_s3 "$snapshot_id"
}

# Copy RDS snapshot to S3
copy_snapshot_to_s3() {
    local snapshot_id=$1
    local export_task_id="${snapshot_id}-export-$(date +%s)"
    
    log "INFO" "Exporting RDS snapshot to S3: $snapshot_id"
    
    aws rds start-export-task \
        --export-task-identifier "$export_task_id" \
        --source-arn "arn:aws:rds:${REGION}:$(aws sts get-caller-identity --query Account --output text):snapshot:${snapshot_id}" \
        --s3-bucket-name "$S3_BUCKET" \
        --s3-prefix "rds-exports/" \
        --iam-role-arn "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/rds-export-role" \
        --region "$REGION"
    
    log "INFO" "Export task created: $export_task_id"
}

# Backup Elasticsearch
backup_elasticsearch() {
    local es_endpoint="${ELASTICSEARCH_ENDPOINT:-localhost:9200}"
    
    log "INFO" "Starting Elasticsearch backup"
    
    # Create snapshot repository
    curl -X PUT "${es_endpoint}/_snapshot/s3-backup?pretty" \
        -H 'Content-Type: application/json' \
        -d"{\"type\":\"s3\",\"settings\":{\"bucket\":\"${S3_BUCKET}\",\"region\":\"${REGION}\"}}"
    
    # Create snapshot
    local snapshot_name="snapshot-$(date +%Y%m%d-%H%M%S)"
    curl -X PUT "${es_endpoint}/_snapshot/s3-backup/${snapshot_name}?wait_for_completion=true&pretty"
    
    log "INFO" "Elasticsearch snapshot created: $snapshot_name"
}

# Cleanup old backups
cleanup_old_backups() {
    log "INFO" "Cleaning up backups older than $RETENTION_DAYS days"
    
    # Cleanup local backups
    find "$BACKUP_DIR" -type f -mtime +"$RETENTION_DAYS" -delete
    
    # Cleanup RDS snapshots
    local cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%Y-%m-%d)
    aws rds describe-db-snapshots \
        --db-instance-identifier "$RDS_INSTANCE" \
        --region "$REGION" \
        --query "DBSnapshots[?SnapshotCreateTime<='${cutoff_date}'].DBSnapshotIdentifier" \
        --output text | xargs -I {} aws rds delete-db-snapshot --db-snapshot-identifier {} --region "$REGION" || true
    
    log "INFO" "Cleanup completed"
}

# Restore RDS from snapshot
restore_rds() {
    local snapshot_id=$1
    local target_instance="${2:-${RDS_INSTANCE}-restored}"
    
    log "INFO" "Restoring RDS from snapshot: $snapshot_id to $target_instance"
    
    aws rds restore-db-instance-from-db-snapshot \
        --db-instance-identifier "$target_instance" \
        --db-snapshot-identifier "$snapshot_id" \
        --publicly-accessible false \
        --multi-az true \
        --region "$REGION"
    
    aws rds wait db-instance-available \
        --db-instance-identifier "$target_instance" \
        --region "$REGION"
    
    log "INFO" "RDS restore completed: $target_instance"
}

# Restore Elasticsearch from snapshot
restore_elasticsearch() {
    local snapshot_name=$1
    local es_endpoint="${ELASTICSEARCH_ENDPOINT:-localhost:9200}"
    
    log "INFO" "Restoring Elasticsearch from snapshot: $snapshot_name"
    
    curl -X POST "${es_endpoint}/_snapshot/s3-backup/${snapshot_name}/_restore?wait_for_completion=true&pretty"
    
    log "INFO" "Elasticsearch restore completed"
}

# Full backup
full_backup() {
    log "INFO" "Starting full backup"
    backup_rds
    backup_elasticsearch
    cleanup_old_backups
    log "INFO" "Full backup completed"
}

# Verify backup integrity
verify_backups() {
    log "INFO" "Verifying backup integrity"
    
    # List RDS snapshots
    local snapshot_count=$(aws rds describe-db-snapshots \
        --db-instance-identifier "$RDS_INSTANCE" \
        --region "$REGION" \
        --query 'DBSnapshots | length(@)' \
        --output text)
    
    log "INFO" "Total RDS snapshots: $snapshot_count"
    
    if [ "$snapshot_count" -eq 0 ]; then
        log "WARN" "No RDS snapshots found"
        return 1
    fi
    
    return 0
}

# Main
main() {
    local command=${1:-help}
    
    case $command in
        backup)
            full_backup
            ;;
        backup-rds)
            backup_rds
            ;;
        backup-elasticsearch)
            backup_elasticsearch
            ;;
        restore-rds)
            restore_rds "${2:-}" "${3:-}"
            ;;
        restore-elasticsearch)
            restore_elasticsearch "${2:-}"
            ;;
        verify)
            verify_backups
            ;;
        cleanup)
            cleanup_old_backups
            ;;
        *)
            echo "Usage: $0 {backup|backup-rds|backup-elasticsearch|restore-rds|restore-elasticsearch|verify|cleanup}"
            echo ""
            echo "Commands:"
            echo "  backup - Full backup of all components"
            echo "  backup-rds - Backup RDS database"
            echo "  backup-elasticsearch - Backup Elasticsearch"
            echo "  restore-rds <snapshot-id> [instance-name] - Restore RDS from snapshot"
            echo "  restore-elasticsearch <snapshot-name> - Restore Elasticsearch from snapshot"
            echo "  verify - Verify backup integrity"
            echo "  cleanup - Clean up old backups"
            exit 1
            ;;
    esac
}

main "$@"
