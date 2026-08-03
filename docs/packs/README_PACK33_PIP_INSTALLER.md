# Pack 33 — Pip Installer

Přidává na stránku `/debug` záchranné tlačítko **Vynutit PIP Install**. To využívá modul `subprocess` ke spuštění `pip install --user qrcode[pil] python-barcode[images]` přímo pomocí binárky Pythonu, která aktuálně pohání webový server (`sys.executable`).

Tím se obejde jakýkoliv nesoulad mezi verzemi Pythonu v konzoli a na webu – balíčky se zkompilují a uloží přesně pro ten interpret, který zrovna vyřizuje HTTP požadavky. Následně se aplikace pokusí rovnou namapovat příslušný `site-packages` adresář.
