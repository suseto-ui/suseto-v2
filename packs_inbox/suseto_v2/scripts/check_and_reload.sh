#!/bin/bash
set -euo pipefail
PROJECT_DIR="${PROJECT_DIR:-/home/Suseto/suseto_v2}"
DOMAIN_HINT="${DOMAIN_HINT:-suseto_pythonanywhere_com_wsgi.py}"

if [ ! -f "$PROJECT_DIR/app.py" ]; then
  echo "ERROR: app.py nebyl nalezen v $PROJECT_DIR" >&2
  exit 1
fi

python3 -m py_compile "$PROJECT_DIR/app.py"
while IFS= read -r -d '' file; do
  python3 -m py_compile "$file"
done < <(find "$PROJECT_DIR/services" -type f -name '*.py' -print0)

WSGI_PATH="${WSGI_PATH:-/var/www/$DOMAIN_HINT}"
if [ ! -f "$WSGI_PATH" ]; then
  WSGI_PATH=$(find /var/www -maxdepth 1 -type f -name '*_pythonanywhere_com_wsgi.py' | head -n 1 || true)
fi
if [ -z "${WSGI_PATH:-}" ] || [ ! -f "$WSGI_PATH" ]; then
  echo "ERROR: WSGI soubor nenalezen. Nastav WSGI_PATH=/var/www/...wsgi.py" >&2
  exit 2
fi

touch "$WSGI_PATH"
echo "OK: syntax validni; reload vyzadan pres $WSGI_PATH"
