# Pack 7.1 — Scanner Library Fix

Oprava Scanner Labu: načítání `html5-qrcode` se nyní provádí až po stisku **Zapnout kameru**. Nejprve se použije jsDelivr, při chybě automaticky unpkg. Řeší případ, kdy šablona layoutu nemá Jinja `head` block, takže původní `<script>` nebyl do výsledné stránky vykreslen.

Nasazení: `/home/Suseto/suseto_v2/scripts/deploy_pack5.sh /home/Suseto/suseto_v2_pack7_1_scanner_fix.zip`, následně hard refresh `Ctrl+F5` na `/scanner-lab`.
