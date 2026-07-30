# Pack 35 — State Lab Queue Fix

Opravuje problém ve State Labu, kam se nepřesouval payload ze Scanner Labu. Když operátor ve Scanner Labu vybere payload z historie a klikne na "Vybrané do State Lab", uloží se záznam do `susetoStateQueue`. Tento balík zajistí, že po načtení `/state-lab` si JavaScript tuto frontu přečte, první payload vloží do vstupního pole a automaticky spustí prvotní vytvoření State grafu.
