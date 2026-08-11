# Pack 21 — Image Upload Scanner + Web Login & Roles

Doplňuje dvě chybějící oblasti z původní verze a z požadavků na provozní správu: čtení QR/čárových kódů z nahrané fotografie a základní webovou administraci uživatelů. Scanner Lab nově přijímá JPG/PNG/WEBP soubory a přes lokální knihovnu se pokusí přečíst QR nebo podporovaný 1D kód přímo z obrázku. Při úspěchu vloží payload do standardního analyzačního toku a historie.

Současně přidává login, session a role `admin`, `operator`, `viewer`. Výchozí bootstrap účet po prvním nasazení je `admin / admin123`; po přihlášení může admin vytvářet uživatele, měnit role a deaktivovat účty přímo z webu. Záloha nově zahrnuje i `users.json` a obnova jej vrací zpět spolu s Registry a inventurními relacemi.
