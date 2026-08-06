# Repository Overview – Suseto v2

> **Stav:** Návrh k revizi (draft) – nezapracovávejte do produkce bez schválení.

---

## 1. Struktura repozitáře
suseto-v2/
├── docs/                          # Dokumentace, audity, plány
│   ├── AUDIT_REPORT.md            # Kompletní audit kódu
│   ├── CHANGELOG.md               # Historie změn
│   ├── PR_REVIEW.md               # Přehled pull request review
│   ├── README_AUDIT_FINDINGS.md   # Shrnutí nálezů auditu
│   ├── bulk-commit-plan.md        # Plán hromadných commitů
│   ├── github-implementation-pack.md  # GitHub implementační balíček
│   ├── hierarchicky-plan.md       # Hierarchický plán projektu
│   ├── repair_analysis.md         # Analýza oprav (Ruff + kód)
│   ├── packs/                     # Dílčí balíčky dokumentace
│   └── repository_overview_draft.md   # ← tento soubor
├── src/ nebo moduly               # Zdrojový kód aplikace
├── tests/                         # Testy
├── pyproject.toml / ruff.toml     # Konfigurace nástrojů
└── README.md                      # Hlavní popis projektu

---

## 2. Přehled dokumentů v `docs/`

| Soubor | Účel |
|---|---|
| `AUDIT_REPORT.md` | Detailní audit – chyby, varování, doporučení |
| `CHANGELOG.md` | Chronologický přehled změn |
| `PR_REVIEW.md` | Review otevřených/uzavřených PR |
| `README_AUDIT_FINDINGS.md` | Stručné shrnutí auditních nálezů |
| `bulk-commit-plan.md` | Strategie pro hromadné commity oprav |
| `github-implementation-pack.md` | Návod na GitHub workflow a CI/CD |
| `hierarchicky-plan.md` | Prioritizace úkolů podle hierarchie |
| `repair_analysis.md` | Analýza Ruff chyb a plán jejich oprav |
| `packs/` | Dílčí balíčky pro specifické oblasti |

---

## 3. Plán oprav Ruff

Opravy jsou rozděleny do tří vln podle závažnosti:

### Vlna 1 – Kritické (blokující CI)
- `F401` – Nepoužívané importy
- `E501` – Příliš dlouhé řádky (> 88 znaků)
- `F821` – Nedefinované proměnné

### Vlna 2 – Důležité (kvalita kódu)
- `E711` / `E712` – Porovnání s `None` / `True` / `False`
- `W291` / `W293` – Zbytečné mezery
- `B006` – Mutable default argumenty

### Vlna 3 – Volitelné (styl)
- `I001` – Třídění importů (isort)
- `UP` pravidla – Modernizace syntaxe (Python 3.10+)
- `ANN` – Typové anotace

---

## 4. Prioritní soubory

Na základě `repair_analysis.md` a auditů jsou prioritní tyto soubory (sestupně podle počtu nálezů):

1. Hlavní modul aplikace (`main.py` nebo ekvivalent)
2. Moduly se síťovou komunikací / API klienty
3. Pomocné utility (`utils/`, `helpers/`)
4. Konfigurační loader
5. Testy (nižší priorita, ale neměly by selhávat)

---

## 5. Doporučená strategie commitů
fix(ruff): remove unused imports [F401] – vlna 1
fix(ruff): fix line length violations [E501] – vlna 1
fix(ruff): resolve undefined names [F821] – vlna 1
fix(ruff): fix comparison style [E711/E712] – vlna 2
fix(ruff): remove trailing whitespace [W291/W293] – vlna 2
fix(ruff): sort imports [I001] – vlna 3
chore(ruff): modernize syntax [UP] – vlna 3

**Zásady:**
- Jeden commit = jeden typ opravy (nebo jedna vlna pro malé projekty)
- Neměň logiku kódu souběžně s Ruff opravami
- Po každé vlně spusť testy: `pytest` + `ruff check .`

---

## 6. Podmínky dokončení oprav

Opravy jsou považovány za dokončené, když jsou splněny **všechny** tyto podmínky:

- [ ] `ruff check .` vrátí **0 chyb** (bez `--exit-zero`)
- [ ] `ruff format --check .` projde bez rozdílů
- [ ] Všechny stávající testy projdou (`pytest`)
- [ ] CI pipeline (pokud existuje) je zelená
- [ ] `repair_analysis.md` aktualizován se stavem „DONE"
- [ ] `CHANGELOG.md` doplněn o záznam oprav

---

## 7. Reference

- [`docs/repair_analysis.md`](./repair_analysis.md) – Detailní analýza Ruff nálezů
- [`docs/AUDIT_REPORT.md`](./AUDIT_REPORT.md) – Kompletní audit
- [`docs/bulk-commit-plan.md`](./bulk-commit-plan.md) – Commit strategie
- [`docs/github-implementation-pack.md`](./github-implementation-pack.md) – GitHub workflow
- [Ruff dokumentace](https://docs.astral.sh/ruff/) – Oficiální docs

---

*Dokument vytvořen: 2026-08-06 | Autor: AI asistent | Stav: DRAFT*
