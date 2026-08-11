# Pack 41 - Sys Path Fix

Zatímco PIP přes terminál (a `sys.executable`) balíčky našel, webová aplikace je hlásila jako `MISSING`.
**Důvod:** Na PythonAnywhere se balíčky nainstalované s flagem `--user` ukládají do složky `~/.local/lib/python3.13/site-packages`. Z nějakého důvodu WSGI server PythonAnywhere tuto složku do cesty nenačte automaticky, takže ačkoliv balíčky fyzicky na disku jsou (jak jsme viděli v PIP výstupu), aplikace `app.py` je nedokáže importovat.

**Oprava:** Do úplného začátku `app.py` byl přidán kód, který pomocí knihovny `site` detekuje cestu k uživatelským balíčkům a explicitně ji přidá do `sys.path`.
