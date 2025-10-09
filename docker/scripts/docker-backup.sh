#!/bin/bash

# Docker backup script for DKP application
# Usage: ./docker/scripts/docker-backup.sh

set -e

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_BACKUP_FILE="${BACKUP_DIR}/dkp_db_${DATE}.sql.gz"
VOLUME_BACKUP_FILE="${BACKUP_DIR}/dkp_volumes_${DATE}.tar.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting backup process at $(date)"

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
docker-compose exec -T postgres pg_dump -U ${DB_USER} -d ${DB_NAME} | gzip > "$DB_BACKUP_FILE"
echo "Database backup saved to: $DB_BACKUP_FILE"

# Backup volumes
echo "Backing up Docker volumes..."
docker run --rm \
    -v dkp_postgres_data:/data/postgres \
    -v dkp_redis_data:/data/redis \
    -v dkp_static_volume:/data/static \
    -v dkp_media_volume:/data/media \
    -v "$(pwd)/${BACKUP_DIR}":/backup \
    alpine:latest \
    tar czf "/backup/$(basename $VOLUME_BACKUP_FILE)" -C /data .

echo "Volume backup saved to: $VOLUME_BACKUP_FILE"

# Backup Docker compose configuration
echo "Backing up Docker configuration..."
tar czf "${BACKUP_DIR}/dkp_config_${DATE}.tar.gz" \
    docker-compose.yml \
    Dockerfile \
    .env.production \
    docker/ \
    --exclude=*.log

echo "Configuration backup saved to: ${BACKUP_DIR}/dkp_config_${DATE}.tar.gz"

# Clean up old backups (keep last 7 days)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "dkp_*_${DATE}*" -mtime +7 -delete

echo "Backup completed successfully at $(date)"
echo "Backup files:"
ls -la "$BACKUP_DIR"/dkp_*_"${DATE}"*