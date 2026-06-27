#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_DIR="$ROOT_DIR/backend"

cd "$FRONTEND_DIR"
VITE_PUBLIC_BASE=/static/frontend/ VITE_API_BASE_URL=/api/v1 npm run build

mkdir -p "$BACKEND_DIR/templates/frontend" "$BACKEND_DIR/static/frontend"
rm -rf "$BACKEND_DIR/static/frontend"
mkdir -p "$BACKEND_DIR/static/frontend"
cp "$FRONTEND_DIR/dist/index.html" "$BACKEND_DIR/templates/frontend/index.html"
cp -R "$FRONTEND_DIR/dist/." "$BACKEND_DIR/static/frontend/"
