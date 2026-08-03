# Návrh CI workflow pro Suseto

Tento návrh je zaměřený na Flask/Python projekt se strukturou `app.py`, `services/`, `routes/`, `templates/` a `static/`. Využívá path filtering, pip cache, paralelní joby a concurrency cancel, aby CI neběžela zbytečně při nerelevantních změnách. [web:117][web:121][web:122]

## Proč je workflow rychlejší

- `paths-ignore` přeskočí CI při změnách jen v dokumentaci nebo metadatech. [web:117][web:124][web:131]
- `dorny/paths-filter` rozlišuje backend, frontend, workflow a deploy změny, takže neběží všechno vždy. [web:125][web:131]
- `actions/setup-python` s `cache: pip` zrychlí opakované běhy bez ruční cache logiky. [web:121]
- Matrix pro Python 3.12 a 3.13 ověří kompatibilitu paralelně místo sekvenčně. [web:122][web:127]
- `concurrency.cancel-in-progress` ruší staré běhy při nových commitech do stejné větve. [web:122]

## Co bych ještě doplnil později

- Samostatný `deploy-prod.yml` s ručním schválením.
- Frontend lint, pokud přidáš Node toolchain.
- `pytest-xdist` nebo shardování testů, až bude suite delší. [web:122]
- Povinné status checks pro PR a samostatný lehký workflow pro docs-only změny, pokud chceš mít check vždy zelený i při path filtrech. [web:129]
