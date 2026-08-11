# Pack 36 — Decode Submit Fix

Opravuje chování Decode Labu, kdy odeslání formuláře (submit) pravděpodobně způsobovalo standardní HTML reload stránky místo asynchronního volání API. 
Díky tomu payload z políčka zmizel (stránka se znovunačetla) a zdánlivě se nic nestalo.

Nyní je logika vyčleněna do samostatné funkce a zavěšena bezpečněji.
