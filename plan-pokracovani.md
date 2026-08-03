# Plán pokračování refaktoru

## Priorita 1: stabilizace konfigurace

- Zavést `services/config.py` s mapováním `FLASK_CONFIG` na `development`, `staging` a `production`.
- Vytáhnout citlivé hodnoty do environment variables.
- Ověřit, že start aplikace vrací stejná API data jako dřív.

## Priorita 2: zachování chování při splitu rout

- Migrace `app.py` do blueprintů po blocích.
- U každého bloku držet stejné URL, stejné payloady a stejné chybové hlášky.
- Přidat smoke test na import aplikace a základní endpointy.

## Priorita 3: CI a notifikace

- CI s path filtry.
- Cache pro Python závislosti.
- Slack notifikace na finální výsledek pipeline.

## Provozní pravidlo

Každý krok musí být malý, rollbackovatelný a otestovaný. Smysl funkce má zůstat stejný, mění se jen struktura a prostředí.
