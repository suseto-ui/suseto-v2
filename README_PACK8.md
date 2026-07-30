# Pack 8 — AIDC Batch, Validation & Export

Přidává `/aidc-batch`: CSV UTF-8 preview, výběr sloupce payloadu, generování QR/Code 128/EAN-13/UPC-A a ZIP export. Balík obsahuje `batch_report.csv` s řádky vygenerovanými i přeskočenými (prázdný payload, duplicita, nevalidní vstup). Limit je 250 datových řádků. Data se nezapisují na disk serveru.

Deploy: `/home/Suseto/suseto_v2/scripts/deploy_pack5.sh /home/Suseto/suseto_v2_pack8.zip`, pak reload aplikace a hard refresh prohlížeče.
