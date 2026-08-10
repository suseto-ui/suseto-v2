import io
import json
import base64
import hmac
import hashlib
import textwrap
import unicodedata
import re
from flask import send_file
from PIL import Image, ImageDraw, ImageFont
import qrcode
import qrcode.image.svg
import barcode
<<<<<<< HEAD
from barcode.writer import ImageWriter, SVGWriter from services.config import CONFIG
# PO (čte z env proměnné přes CONFIG):
=======
from barcode.writer import ImageWriter, SVGWriter
from services.config import CONFIG

>>>>>>> 78f6633 (fix(lint): E401 multi-imports, E722 bare except, E302 blank lines, aidc_core typo [S105])
SECRET_KEY = CONFIG["SECRET_KEY"]

def to_base36(number):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if number == 0:
        return "0"
    base36 = ""
    while number > 0:
        number, i = divmod(number, 36)
        base36 = chars[i] + base36
    return base36


def generuj_jwt(payload_dict, secret):
    header = (
        base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        .decode()
        .rstrip("=")
    )
    payload = (
        base64.urlsafe_b64encode(json.dumps(payload_dict).encode()).decode().rstrip("=")
    )
    signature = (
        base64.urlsafe_b64encode(
            hmac.new(
                secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256
            ).digest()
        )
        .decode()
        .rstrip("=")
    )
    return f"{header}.{payload}.{signature}"


def xor_sifra(text, klic):
    if not klic:
        return text
    return "".join(chr(ord(c) ^ ord(klic[i % len(klic)])) for i, c in enumerate(text))
<<<<<<< HEAD
from services.config import CONFIG
def normalizuj_text(text, mod='utf8'):
    if mod == 'ascii':
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    elif mod == 'hexa':
        return text.encode('utf-8').hex().upper()
    elif mod == 'binarni':
        return ' '.join(format(ord(c), '08b') for c in text)
=======


def normalizuj_text(text, mod="utf8"):
    if mod == "ascii":
        return (
            unicodedata.normalize("NFKD", text)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    elif mod == "hexa":
        return text.encode("utf-8").hex().upper()
    elif mod == "binarni":
        return " ".join(format(ord(c), "08b") for c in text)
>>>>>>> 78f6633 (fix(lint): E401 multi-imports, E722 bare except, E302 blank lines, aidc_core typo [S105])
    return text


def vytvor_qr_obrazek(
    text,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    format_vystupu="png",
    vodoznak_text=None,
    inverze=False,
    spodni_text=None,
):
    fill_col = "white" if inverze else "black"
    back_col = "black" if inverze else "white"

    if format_vystupu == "svg" and not vodoznak_text and not spodni_text:
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(
            version=None,
            error_correction=error_correction,
            box_size=10,
            border=4,
            image_factory=factory,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img_io = io.BytesIO()
        qr.make_image().save(img_io)
        img_io.seek(0)
        return send_file(
            img_io,
            mimetype="image/svg+xml",
            as_attachment=True,
            download_name="matrix.svg",
        )

    qr = qrcode.QRCode(
        version=None, error_correction=error_correction, box_size=10, border=4
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_col, back_color=back_col).convert("RGBA")

    if vodoznak_text:
        draw = ImageDraw.Draw(img)
        w, h = img.size
        box_size = int(w * 0.22)
        x0, y0 = (w - box_size) // 2, (h - box_size) // 2
        draw.rectangle([x0, y0, x0 + box_size, y0 + box_size], fill=back_col)
        try:
            font = ImageFont.truetype("arial.ttf", int(box_size * 0.4))
        except IOError:
            font = ImageFont.load_default()
        draw.text(
            (w // 2, h // 2), vodoznak_text, fill=fill_col, font=font, anchor="mm"
        )

    if spodni_text:
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
            font = ImageFont.load_default()
        radek_sirka = (img.width - 20) // 8
        radky = textwrap.wrap(spodni_text, width=max(15, radek_sirka))
        navyseni = len(radky) * 22 + 20
        nove_platno = Image.new("RGBA", (img.width, img.height + navyseni), back_col)
        nove_platno.paste(img, (0, 0))
        draw = ImageDraw.Draw(nove_platno)
        y_text = img.height + 15
        for radek in radky:
            draw.text(
                (img.width // 2, y_text), radek, fill=fill_col, font=font, anchor="mm"
            )
            y_text += 22
        img = nove_platno

    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)
    return send_file(
        img_io, mimetype="image/png", as_attachment=False, download_name="matrix.png"
    )


def vytvor_1d_kod(text, typ="code128", format_vystupu="png"):
    try:
        if typ in ["ean13", "upca"]:
            text = re.sub(r"\D", "", text)
            if typ == "ean13":
                text = text[:12].zfill(12)
            if typ == "upca":
                text = text[:11].zfill(11)
        kod_class = barcode.get_barcode_class(typ)
    except (barcode.errors.BarcodeNotFoundError, barcode.errors.IllegalCharacterError):
        return "Chyba: Nepodporovaný formát nebo neplatné znaky čárového kódu", 400
    writer = SVGWriter() if format_vystupu == "svg" else ImageWriter()
    generovany_kod = kod_class(text, writer=writer)
    img_io = io.BytesIO()
    generovany_kod.write(img_io)
    img_io.seek(0)
    mimetype = "image/svg+xml" if format_vystupu == "svg" else "image/png"
    return send_file(
        img_io,
        mimetype=mimetype,
        as_attachment=(format_vystupu == "svg"),
        download_name=f"barcode_{typ}.{format_vystupu}",
    )


def vytvor_qr_edukacni(text):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    velikost, box, border = len(matrix), 10, 4
    img = Image.new(
        "RGB", ((velikost + border * 2) * box, (velikost + border * 2) * box), "#FFFFFF"
    )
    draw = ImageDraw.Draw(img)
    for r in range(velikost):
        for c in range(velikost):
            if not matrix[r][c]:
                continue
            color = "#333333"
            if (
                (r < 7 and c < 7)
                or (r < 7 and c >= velikost - 7)
                or (r >= velikost - 7 and c < 7)
            ):
                color = "#E63946"
            elif r == 6 or c == 6:
                color = "#1D3557"
            elif (
                (r <= 8 and c == 8)
                or (r == 8 and c <= 8)
                or (r == 8 and c >= velikost - 8)
                or (r >= velikost - 8 and c == 8)
            ):
                color = "#2A9D8F"
            elif (
                (r > 10 and c > 10 and r < velikost - 5 and c < velikost - 5)
                and (r % 28 == 22 or c % 28 == 22)
                and qr.version > 1
            ):
                color = "#9B5DE5"
            x0, y0 = (c + border) * box, (r + border) * box
            draw.rectangle([x0, y0, x0 + box - 1, y0 + box - 1], fill=color)
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png")
