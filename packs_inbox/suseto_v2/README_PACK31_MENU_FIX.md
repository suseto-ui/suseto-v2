# Pack 31 - Menu Delay Fix

Opravuje chování menu na 3 sekundy zpoždění. Původní HTML totiž používá `<details>` prvky, které prohlížeč ovládá sám kliknutím. Pokud jsme chtěli, aby to fungovalo na hover s prodlevou, musíme přepsat otevírání `<details>` na události `mouseenter` a `mouseleave` a zpožďovat odstranění atributu `open`.
