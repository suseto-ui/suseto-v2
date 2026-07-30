# Pack 30 — Self Check

Přidává nástroj pro kontrolu prostředí do `/debug` stránky. Tlačítko **Kontrola prostředí** zjistí:
1. Verzi Pythonu a Flasku.
2. Zda má aplikace oprávnění zapisovat do složky `data/`.
3. Zda jsou správně nainstalované knihovny z `requirements.txt` (qrcode, barcode, Pillow).
4. Data poslední změny klíčových souborů (`app.py`, `decode_lab.js`, `menu-delay.js`). Podle toho lze snadno poznat, zda server běží na staré nebo nové verzi z gitu/zipu.

Ideální pro případy, kdy "něco nefunguje" a není jasné, zda se změny vůbec propsaly na server.
