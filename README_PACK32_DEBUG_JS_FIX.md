# Pack 32 - Debug JS Fix

Opravuje zablokovaná tlačítka v `/debug`. Původní JS přiřazoval `onclick` události rovnou při startu skriptu. Pokud DOM ještě nebyl plně načtený, přiřazení selhalo a tlačítka nic nedělala. Nyní je veškerá logika obalena do `DOMContentLoaded` a přidáno bezpečnější vkládání HTML do `chip()` funkce, aby se nerozbíjely výsledky formátované značkami jako `<br>`.
