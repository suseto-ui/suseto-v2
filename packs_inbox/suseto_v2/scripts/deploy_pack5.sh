#!/bin/bash
set -euo pipefail
PROJECT_DIR="${PROJECT_DIR:-/home/Suseto/suseto_v2}"
ARCHIVE="${1:-/home/Suseto/suseto_v2_pack5.zip}"
TEMP_DIR="$(mktemp -d /home/Suseto/suseto_pack5_XXXXXX)"
trap 'rm -rf "$TEMP_DIR"' EXIT

[ -f "$ARCHIVE" ] || { echo "ERROR: ZIP nenalezen: $ARCHIVE" >&2; exit 1; }
unzip -q -o "$ARCHIVE" -d "$TEMP_DIR"
[ -f "$TEMP_DIR/suseto_v2/app.py" ] || { echo "ERROR: ZIP nema ocekavanou strukturu." >&2; exit 2; }
cp -r "$TEMP_DIR/suseto_v2/." "$PROJECT_DIR/"
chmod 700 "$PROJECT_DIR/scripts/check_and_reload.sh" "$PROJECT_DIR/scripts/deploy_pack5.sh"
"$PROJECT_DIR/scripts/check_and_reload.sh"
echo "OK: pack 5 nasazen. Otevri /health pro sanity check."
