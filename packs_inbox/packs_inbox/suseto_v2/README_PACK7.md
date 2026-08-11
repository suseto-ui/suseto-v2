# Pack 7 — AIDC Core Reintegration

Vrací QR/1D barcode generátor a Scanner Lab do moderního Suseto UI. `/aidc-studio` generuje QR, Code 128, EAN-13 a UPC-A do PNG/SVG. `/scanner-lab` podporuje WebRTC kameru, USB keyboard wedge a ruční vstup. Scanner analyzuje payload výhradně lokálně v aplikaci a neposílá ho ven.

## Jednorázová instalace knihoven

Ve virtuálním prostředí PythonAnywhere spusť `pip install -r /home/Suseto/suseto_v2/requirements.txt`. Poté nasaď balík přes stávající deploy helper.
