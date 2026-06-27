#!/usr/bin/env sh
set -eu

MEDIA_ROOT="${MEDIA_ROOT:-./backend/media}"
BACKUP_DIR="${BACKUP_DIR:-./backups/media}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

tar -czf "$BACKUP_DIR/media-$TIMESTAMP.tar.gz" -C "$MEDIA_ROOT" .
find "$BACKUP_DIR" -type f -name "media-*.tar.gz" -mtime +"${BACKUP_RETENTION_DAYS:-30}" -delete
