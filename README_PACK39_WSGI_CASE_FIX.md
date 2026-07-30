# Pack 39 - WSGI Case Fix

Tento balíček upravuje `deploy_latest.sh`. Opravuje problém na PythonAnywhere, kde příkaz `whoami` vrací uživatelské jméno s velkým písmenem (např. `Suseto`), zatímco systémový název WSGI souboru je striktně malými písmeny (`suseto_pythonanywhere_com_wsgi.py`). 

Do skriptu byla přidána utilita `tr '[:upper:]' '[:lower:]'`, která jméno bezpečně převede na malá písmena.
