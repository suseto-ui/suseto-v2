# Pack 42 - Import Debug & Hardcoded Path

V předchozím kroku jsme sice zkusili přidat `user_site`, ale možná se vyhodnotil špatně. Tento balíček:
1. Natvrdo injektuje cestu `/home/Suseto/.local/lib/python3.13/site-packages` do `sys.path`.
2. Místo tichého skrytí chyby (`MISSING`) zachytí skutečnou chybovou hlášku (`ERROR: ...`) a vypíše ji do tlačítka "Kontrola prostředí".
3. Vypíše rovnou i celý zjištěný `sys.path`, abychom viděli, kde přesně systém balíčky hledá.
