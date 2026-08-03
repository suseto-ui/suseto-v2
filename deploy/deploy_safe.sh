#!/bin/bash
set -euo pipefail
APP_ROOT="${APP_ROOT:-/home/Suseto/suseto_v2}"
APP_NAME="${APP_NAME:-suseto_pythonanywhere_com}"
WSGI_FILE="${WSGI_FILE:-/var/www/${APP_NAME}_wsgi.py}"
ZIP_FILE="${1:-suseto_bundle_login_deploy.zip}"
TMP_DIR="/tmp/suseto_deploy_$$"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${APP_ROOT}_backup_${STAMP}"

if [ ! -f "$ZIP_FILE" ]; then
  echo "ZIP not found: $ZIP_FILE"
  exit 1
fi

mkdir -p "$TMP_DIR"
unzip -q "$ZIP_FILE" -d "$TMP_DIR"

if [ ! -d "$TMP_DIR/suseto_v2" ]; then
  echo "Archive must contain suseto_v2/"
  exit 1
fi

mkdir -p "$(dirname "$APP_ROOT")"
if [ -d "$APP_ROOT" ]; then
  cp -a "$APP_ROOT" "$BACKUP_DIR"
fi

mkdir -p "$APP_ROOT"
rsync -a --delete "$TMP_DIR/suseto_v2/" "$APP_ROOT/"

if [ -f "$APP_ROOT/requirements.txt" ]; then
  pip3 install --user -r "$APP_ROOT/requirements.txt"
fi

if [ -f "$WSGI_FILE" ]; then
  touch "$WSGI_FILE"
fi

echo "Deploy complete: $APP_ROOT"
if [ -d "$BACKUP_DIR" ]; then
  echo "Backup: $BACKUP_DIR"
fi
