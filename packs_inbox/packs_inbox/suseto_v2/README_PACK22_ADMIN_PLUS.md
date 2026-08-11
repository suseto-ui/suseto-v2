# Pack 22 — Admin Plus

Rozšiřuje základní administraci o běžné provozní prvky: změnu vlastního hesla, reset hesla adminem, požadavek na změnu hesla po vytvoření nebo resetu účtu, smazání uživatele, auditní log a jednoduchou profilovou stránku. Přihlášení a odhlášení se zapisuje do auditu stejně jako vytváření uživatelů, změna role, aktivace/deaktivace, záloha, obnova a inventurní akce.

Hesla nově podléhají základní kontrole síly: minimálně 8 znaků, malé i velké písmeno a číslo. Bootstrap účet `admin` zůstává chráněný proti smazání, aby aplikace nezůstala bez správce.
