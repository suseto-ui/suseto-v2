# Pack 27 — Debug Suite

Přidává samostatnou stránku `/debug` pro rychlé ověření webu přímo z klienta. Umožňuje načíst seznam rout, udělat ping na API a spustit základní smoke test důležitých endpointů jako `/health`, `/api/v1/auth/me`, `/api/v1/system-status`, `/api/v1/inventory/sessions` a `/api/v1/locations`. Debug výpis ukazuje i HTTP statusy, takže je snadné odlišit problém frontendu, session nebo backendu.
