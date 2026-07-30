#!/bin/bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/home/Suseto/suseto_v2}"
ARCHIVE="${1:-/home/Suseto/suseto_v2_pack_latest.zip}"
TEMP_DIR="$(mktemp -d /home/Suseto/suseto_pack_XXXXXX)"

# Zajištění malých písmen pro název WSGI souboru
PA_USERNAME=$(whoami | tr '[:upper:]' '[:lower:]')
WSGI_FILE="/var/www/${PA_USERNAME}_pythonanywhere_com_wsgi.py"

trap 'rm -rf "$TEMP_DIR"' EXIT

[ -f "$ARCHIVE" ] || { echo "ERROR: ZIP nenalezen: $ARCHIVE" >&2; exit 1; }

echo "1. Rozbaluji archiv do dočasné složky..."
unzip -q -o "$ARCHIVE" -d "$TEMP_DIR"

[ -f "$TEMP_DIR/suseto_v2/app.py" ] || { echo "ERROR: ZIP nema ocekavanou strukturu." >&2; exit 2; }

echo "2. Kopíruji soubory do projektu..."
cp -a "$TEMP_DIR/suseto_v2/." "$PROJECT_DIR/"

chmod 700 "$PROJECT_DIR/scripts/deploy_latest.sh" 2>/dev/null || true

echo "3. Instaluji případné nové závislosti z requirements.txt..."
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    python3 -m pip install --user -r "$PROJECT_DIR/requirements.txt" --quiet || echo "Upozornění: PIP install se nepodařilo kompletně dokončit, ale pokračuji..."
fi

echo "4. Automatický WSGI reload..."
if [ -f "$WSGI_FILE" ]; then
    touch "$WSGI_FILE"
    echo "WSGI soubor aktualizován ($WSGI_FILE). PythonAnywhere restartuje aplikaci."
else
    echo "Upozornění: WSGI soubor $WSGI_FILE nenalezen. Bude nutné provést ruční Reload v GUI."
fi

echo "=== OK: Nasazeno. Otevři web a stiskni Ctrl+F5. ==="
