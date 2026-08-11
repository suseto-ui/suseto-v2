import base64, io, re
from flask import send_file

def _libraries():
    try:
        import qrcode
        import barcode
        from barcode.writer import ImageWriter, SVGWriter
        return qrcode, barcode, ImageWriter, SVGWriter, None
    except ImportError as exc:
        return None, None, None, None, str(exc)

def _response_error(message, status=503):
    from flask import jsonify
    return jsonify({"error":message,"hint":"Nainstaluj requirements.txt do virtualenvu."}), status

def generate_qr(data, fmt="png"):
    qrcode, _, _, _, err = _libraries()
    if err: return _response_error(f"QR knihovna není připravena: {err}")
    data=str(data or "").strip()
    if not data: return _response_error("Payload nesmí být prázdný",400)
    qr=qrcode.QRCode(box_size=10,border=4,error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data); qr.make(fit=True); image=qr.make_image(fill_color="#111827",back_color="#ffffff")
    buf=io.BytesIO()
    if fmt=="svg":
        import qrcode.image.svg
        svg=qrcode.make(data,image_factory=qrcode.image.svg.SvgPathImage); svg.save(buf); mime="image/svg+xml"; name="suseto-qr.svg"
    else:
        image.save(buf,format="PNG"); mime="image/png"; name="suseto-qr.png"
    buf.seek(0); return send_file(buf,mimetype=mime,as_attachment=False,download_name=name)

def generate_barcode(data, kind="code128", fmt="png"):
    _, barcode, ImageWriter, SVGWriter, err = _libraries()
    if err: return _response_error(f"Barcode knihovna není připravena: {err}")
    kind=(kind or "code128").lower(); raw=str(data or "").strip()
    if kind not in {"code128","ean13","upca"}: return _response_error("Nepodporovaný typ",400)
    if kind in {"ean13","upca"}:
        raw=re.sub(r"\D","",raw); required=12 if kind=="ean13" else 11
        if len(raw)>required: return _response_error(f"{kind.upper()} očekává maximálně {required} číslic bez kontrolní číslice",400)
        raw=raw.zfill(required)
    if not raw: return _response_error("Payload nesmí být prázdný",400)
    try: code=barcode.get(kind,raw,writer=SVGWriter() if fmt=="svg" else ImageWriter())
    except Exception as exc: return _response_error(f"Neplatná data: {exc}",400)
    buf=io.BytesIO(); code.write(buf); buf.seek(0)
    return send_file(buf,mimetype="image/svg+xml" if fmt=="svg" else "image/png",as_attachment=False,download_name=f"suseto-{kind}.{fmt}")

def scan_analysis(payload):
    text=str(payload or "").strip(); findings=[]
    if not text: return {"payload":"","classification":"empty","findings":["Vlož payload ze scanneru nebo ručního vstupu."],"hex":"","safe":True}
    if text.startswith("WIFI:"): findings.append("Wi-Fi QR konfigurace")
    if text.count(".")==2: findings.append("JWT-like struktura")
    if text.startswith(("http://","https://")): findings.append("URL / URI")
    if re.fullmatch(r"[0-9A-Fa-f]+",text) and len(text)%2==0: findings.append("hexadecimální kandidát")
    if re.fullmatch(r"[A-Za-z0-9+/=_-]{12,}",text): findings.append("base64/base64url kandidát")
    cls=findings[0] if findings else "obecný textový payload"
    return {"payload":text,"classification":cls,"findings":findings or ["Bez zvláštní signatury; vhodné pro Navigator."],"length":len(text),"hex":text.encode("utf-8").hex(" ").upper(),"ascii":"".join(c if 32<=ord(c)<127 else "." for c in text),"safe":True}
