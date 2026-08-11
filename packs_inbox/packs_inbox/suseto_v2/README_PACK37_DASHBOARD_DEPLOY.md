# Pack 37 — Dashboard, CSV Exports & Smart Deploy

Tento balík přináší jak administrativní vylepšení, tak novou funkci:

1. **Chytrý Deploy Skript (`scripts/deploy_latest.sh`)**
   Tento nový skript kromě kopírování souborů automaticky spustí instalaci závislostí a na konci udělá `touch` na WSGI souboru. To znamená, že PythonAnywhere by se měl po deployi **sám restartovat** bez nutnosti klikat na Reload v administraci!

2. **Plnohodnotný Dashboard**
   Stránka `/dashboard` nyní obsahuje reálná data: počty uživatelů, lokací, velikost auditu, vizualizaci skenů za posledních 7 dní (graf vytvořený čistě přes HTML/CSS) a výpis posledních 10 událostí.

3. **Exporty dat do CSV**
   - V sekci **Status** si můžete stáhnout celou historii položek (Timeline) do Excelu/CSV.
   - V sekci **Admin** je nově tlačítko pro export celého Audit logu do CSV pro kontrolní účely.
