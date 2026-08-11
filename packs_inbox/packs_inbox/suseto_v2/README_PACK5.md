# Suseto v2 — Pack 5

Pack 5 pridava interaktivni State Lab: klikaci uzly, aktivni frontier, detail vybraneho stavu a krokovy replay. Obsahuje take lokalni deployment helper, ktery pred reloaderem provede `py_compile` nad `app.py` a moduly `services/`.

## Bezpecne nasazeni

1. Nahraj `suseto_v2_pack5.zip` do `/home/Suseto/`.
2. Jednou spust:

```bash
mkdir -p /home/Suseto/unpack_tmp5
cd /home/Suseto/unpack_tmp5
unzip -o /home/Suseto/suseto_v2_pack5.zip
cp -r /home/Suseto/unpack_tmp5/suseto_v2/. /home/Suseto/suseto_v2/
chmod 700 /home/Suseto/suseto_v2/scripts/*.sh
/home/Suseto/suseto_v2/scripts/check_and_reload.sh
```

Pro priste lze spustit jedinym prikazem:

```bash
/home/Suseto/suseto_v2/scripts/deploy_pack5.sh /home/Suseto/suseto_v2_pack5.zip
```

Script nikam neposila token ani tajne udaje. WSGI hledá pod `/var/www/`; pri nestandardnim nazvu lze zadat `WSGI_PATH=/var/www/tvuj_wsgi.py`.
