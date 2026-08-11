# Pack 40 - PIP Executable Fix

Opravuje chybu `/usr/local/bin/uwsgi: unrecognized option '--user'`.

**Důvod chyby:** Ve WSGI prostředí na PythonAnywhere není `sys.executable` samotný Python, ale webový server `uwsgi`. Zkoušeli jsme tedy spustit `uwsgi -m pip install`, což samozřejmě uWSGI neumí.
**Oprava:** Skript teď explicitně volá `python3 -m pip install ...` a tím obchází WSGI daemon.
