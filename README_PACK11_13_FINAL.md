# Unified Pack 11–13 — Compatibility, Operations & Finalization

Tento jeden balík uzavírá plánované etapy 11 až 13.

- **Transform Lab** (`/transform-lab`): lokální převody UTF-8/HEX/binární/Base64, bezpečné dekódovací pokusy, volitelný XOR a HMAC nad vlastním vstupem a časové reprezentace. Neobsahuje generování přihlašovacích tokenů ani obcházení přístupových kontrol.
- **Advanced Scanner workflow**: lokální historie posledních 20 scanů v prohlížeči a Registry match.
- **Dashboard** (`/dashboard`): souhrn Registry, stavů, profilů, posledních změn a rychlá CSV záloha.
- **Finalization**: export/import Registry, tiskové štítky a validace z předchozích packů zůstávají zachované.

Po deployi udělej Reload v PythonAnywhere a Ctrl+F5 v prohlížeči. Pro zálohu používej Dashboard → Záloha CSV a průběžně zálohuj `data/registry.json`.
