#!/usr/bin/env sh
set -eu

BACKUP_FILE="${1:?Usage: restore_db.sh path/to/backup.dump}"

PGHOST="${POSTGRES_HOST:-db}"
PGPORT="${POSTGRES_PORT:-5432}"
PGDATABASE="${POSTGRES_DB:-lms}"
PGUSER="${POSTGRES_USER:-lms}"
export PGPASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"

pg_restore -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" --clean --if-exists "$BACKUP_FILE"
