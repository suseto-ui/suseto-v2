# Pack 43 - Dependencies Version Fix

Ukázalo se, že balíčky jsou od začátku správně nainstalované a importované. Zmátla nás chybová hláška.
Moduly `qrcode` a `barcode` v nejnovějších verzích totiž vůbec nepoužívají atribut `__version__`. Samotný pokus o jejich import byl úspěšný, ale crashlo to na tom, že jsme se z nich snažili přečíst číslo verze, které tam není definované. V debugu se pak ukázalo slovo MISSING (nyní jsme viděli reálnou chybu `has no attribute __version__`).

**Oprava:** Nyní kontrola modulu zjišťuje verzi bezpečně přes `getattr()` a nespadne. Knihovny by měly začít fungovat a generovat kódy.
