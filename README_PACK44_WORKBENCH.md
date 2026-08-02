# Pack 44 – Data & Identifier Analysis Workbench

## Co přináší

- **Nová stránka `/workbench`** – plnohodnotný analyzační a reverzní inženýrský lab
- **`services/workbench_service.py`** – core logika:
  - `ingest_identifier()` – normalizace a typování (url, hex, ean, imei, jwt, base64, json, uuid, mac, data_uri)
  - `run_analysis_pipeline()` – rizikové skóre, EAN/IMEI validace, JWT audit, URL analýza
  - `run_reverse_engineering()` – base64, hex→ASCII, zlib, URL-decode, Shannon entropie
  - `run_test_harness()` – automatické fuzzování HTTP endpointů
- **`services/workbench_routes.py`** – Flask blueprint s `register_workbench(app)`, navazuje na stávající volání v `app.py`
- **`templates/pages/workbench.html`** – UI se 4 sekcemi (Ingest, Pipeline, Reverse, Test Harness)
- **`static/js/workbench.js`** – frontend JS s auto-paste detekcí, type badges, risk bar, entropy bar
- **`requirements.txt`** – doplněn balíček `requests` pro Test Harness

## Stávající funkčnost

Žádný existující soubor nebyl upraven. Workbench blueprint se registruje přes `register_workbench(app)`,
která je v `app.py` již volána (`from services.workbench_routes import register_workbench`).

## Deploy

Nahrát na PythonAnywhere jako Pack 44, provést `pip install -r requirements.txt` a `touch` WSGI souboru.
