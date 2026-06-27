#!/usr/bin/env sh
set -eu

ARCHIVE="${1:?Usage: restore_media.sh path/to/media.tar.gz}"
MEDIA_ROOT="${MEDIA_ROOT:-./backend/media}"
mkdir -p "$MEDIA_ROOT"

tar -xzf "$ARCHIVE" -C "$MEDIA_ROOT"
