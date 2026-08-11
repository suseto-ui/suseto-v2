# Pack 14 — Scanner History & State Lab Queue

Doplňuje viditelnou historii scanů přímo do Scanner Labu. Historie se drží lokálně v `localStorage` aktuálního prohlížeče, maximálně 50 unikátních payloadů. Každý záznam lze znovu načíst, označit, nebo vymazat.

Tlačítko **Vybrané do State Lab** předá označené položky (pokud nic není označeno, celou historii) do lokální fronty State Labu. V State Labu se vybere jeden payload jako seed pro profilaci a heuristické řazení. Funkce nezkouší přístup k cizím systémům; vyhodnocuje jen strukturu vlastních načtených payloadů.
