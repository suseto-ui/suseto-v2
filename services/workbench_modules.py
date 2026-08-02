# services/workbench_modules.py
# Rozšiřující analytické moduly pro Workbench
import re, math, base64, json, csv, io
from typing import Dict, Any, List

# ── BATCH ANALYZER ────────────────────────────────────────────────────────────
def batch_analyze(csv_text: str, column: str = "code") -> Dict[str, Any]:
    from services.workbench_service import ingest_identifier, run_analysis_pipeline
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)
    if not rows:
        return {"ok": False, "error": "Prazdny CSV"}
    col = column if column in rows[0] else list(rows[0].keys())[0]
    results = []
    stats: Dict[str, int] = {}
    for row in rows:
        raw = row.get(col, "").strip()
        if not raw:
            continue
        ident = ingest_identifier(raw)
        analysis = run_analysis_pipeline(ident.to_dict())
        t = ident.type
        stats[t] = stats.get(t, 0) + 1
        results.append({
            "raw": raw,
            "type": t,
            "datetime": ident.attributes.get("datum", "") + " " + ident.attributes.get("cas", ""),
            "id_karty": ident.attributes.get("id_karty", ""),
            "risk_score": analysis.get("risk_score", 0),
            "notes": "; ".join(analysis.get("notes", [])),
            "attributes": ident.attributes,
        })
    return {"ok": True, "total": len(results), "stats": stats, "results": results}


def batch_to_csv(results: List[Dict]) -> str:
    if not results:
        return ""
    fields = ["raw", "type", "datetime", "id_karty", "risk_score", "notes"]
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(results)
    return out.getvalue()


# ── TIMELINE VIEWER ───────────────────────────────────────────────────────────
def build_timeline(codes: List[str]) -> Dict[str, Any]:
    from services.workbench_service import parse_access_gate
    events = []
    errors = []
    for code in codes:
        c = code.strip()
        if not c:
            continue
        ag = parse_access_gate(c)
        if ag:
            events.append({
                "code": c,
                "datetime_iso": ag["datetime_iso"],
                "datum": ag["datum"],
                "cas": ag["cas"],
                "id_karty": ag["id_karty"],
                "typ_brany": ag["typ_brany"],
                "flag": ag["flag"],
                "flag_label": ag["flag_label"],
            })
        else:
            errors.append(c)
    events.sort(key=lambda x: x["datetime_iso"])
    # Seskupit podle ID karty
    by_card: Dict[str, List] = {}
    for e in events:
        k = e["id_karty"]
        by_card.setdefault(k, []).append(e)
    return {
        "ok": True,
        "total": len(events),
        "errors": errors,
        "events": events,
        "by_card": by_card,
        "cards": sorted(by_card.keys()),
    }


# ── PATTERN DETECTOR ─────────────────────────────────────────────────────────
def detect_patterns(codes: List[str]) -> Dict[str, Any]:
    from services.workbench_service import parse_access_gate
    parsed = [parse_access_gate(c.strip()) for c in codes if c.strip()]
    parsed = [p for p in parsed if p]
    if not parsed:
        return {"ok": False, "error": "Zadne platne access_gate kody"}

    patterns = []
    card_counts: Dict[str, int] = {}
    hour_counts: Dict[int, int] = {}
    flag_counts: Dict[str, int] = {}
    dates: List[str] = []

    for p in parsed:
        card_counts[p["id_karty"]] = card_counts.get(p["id_karty"], 0) + 1
        hour_counts[p["hodiny"]] = hour_counts.get(p["hodiny"], 0) + 1
        flag_counts[p["flag_label"]] = flag_counts.get(p["flag_label"], 0) + 1
        dates.append(p["datetime_iso"])

    # Detekce anomalií
    for card, cnt in card_counts.items():
        if cnt > 5:
            patterns.append({"typ": "high_frequency", "zprava": f"Karta {card} prochazela {cnt}x", "zavaznost": "stredni"})

    for h, cnt in hour_counts.items():
        if (h < 6 or h > 22) and cnt > 0:
            patterns.append({"typ": "off_hours", "zprava": f"Pruchody v nestandardni hodine {h}:00 ({cnt}x)", "zavaznost": "vysoka"})

    if "alarm" in flag_counts:
        patterns.append({"typ": "alarm_flag", "zprava": f"Detekovan alarm flag ({flag_counts['alarm']}x)", "zavaznost": "kriticka"})

    if "odmitnuto" in flag_counts:
        patterns.append({"typ": "denied_entry", "zprava": f"Odmitnute vstupy ({flag_counts['odmitnuto']}x)", "zavaznost": "vysoka"})

    dates.sort()
    return {
        "ok": True,
        "total": len(parsed),
        "card_counts": card_counts,
        "hour_distribution": hour_counts,
        "flag_summary": flag_counts,
        "date_range": {"od": dates[0] if dates else "", "do": dates[-1] if dates else ""},
        "patterns": patterns,
    }


# ── GS1 / GTIN PARSER ────────────────────────────────────────────────────────
GS1_PREFIXES = {
    "000-019": "USA/Kanada", "020-029": "Lokalni",
    "040-049": "Lokalni", "050-059": "Kupony",
    "060-139": "USA/Kanada", "300-379": "Francie",
    "380": "Bulharsko", "383": "Slovinsko",
    "385": "Chorvatsko", "387": "Bosna",
    "400-440": "Nemecko", "450-459": "Japonsko",
    "460-469": "Rusko", "477": "Estonsko",
    "478": "Lotyssko", "479": "Sri Lanka",
    "480": "Filipiny", "482": "Ukrajina",
    "484": "Moldavsko", "485": "Armenie",
    "486": "Gruzie", "487": "Kazachstan",
    "489": "Hongkong", "490-499": "Japonsko",
    "500-509": "UK", "520": "Recko",
    "528": "Libanon", "529": "Kypr",
    "531": "Makedonie", "535": "Malta",
    "539": "Irsko", "540-549": "Belgie/Lucembursko",
    "560": "Portugalsko", "569": "Island",
    "570-579": "Dansko", "590": "Polsko",
    "594": "Rumunsko", "599": "Madarsko",
    "600-601": "JAR", "603": "Ghana",
    "608": "Bahrain", "609": "Mauricius",
    "611": "Maroko", "613": "Alzirsko",
    "616": "Kena", "618": "Pobrezi slonoviny",
    "619": "Tunisko", "621": "Syrie",
    "622": "Egypt", "624": "Libye",
    "625": "Jordansko", "626": "Iran",
    "627": "Kuvajt", "628": "SAE",
    "629": "Saudska Arabie", "640-649": "Finsko",
    "690-699": "Cina", "700-709": "Norsko",
    "729": "Izrael", "730-739": "Svedsko",
    "740": "Guatemala", "741": "Salvador",
    "742": "Honduras", "743": "Nikaragua",
    "744": "Kostarika", "745": "Panama",
    "746": "Dominikanska rep.", "750": "Mexiko",
    "754-755": "Kanada", "759": "Venezuela",
    "760-769": "Svycarsko", "770": "Kolumbie",
    "773": "Uruguay", "775": "Peru",
    "777": "Bolivie", "779": "Argentina",
    "780": "Chile", "784": "Paraguay",
    "786": "Ekvador", "789-790": "Brazilie",
    "800-839": "Italie", "840-849": "Spanelsko",
    "850": "Kuba", "858": "Slovensko",
    "859": "Ceska republika", "860": "Srbsko",
    "865": "Mongolsko", "867": "Severni Korea",
    "868-869": "Turecko", "870-879": "Nizozemsko",
    "880": "Jizni Korea", "884": "Kambodza",
    "885": "Thajsko", "888": "Singapur",
    "890": "Indie", "893": "Vietnam",
    "896": "Pakistan", "899": "Indonesie",
    "900-919": "Rakousko", "930-939": "Australie",
    "940-949": "Novy Zeland", "950": "GS1 Global",
    "955": "Malajsie", "958": "Macao",
    "977": "ISSN", "978-979": "ISBN",
    "980": "Refundace", "981-982": "Platby",
    "990-999": "Kupony",
}

def lookup_gs1_prefix(digits: str) -> str:
    p3 = digits[:3]
    for k, v in GS1_PREFIXES.items():
        if "-" in k:
            lo, hi = k.split("-")
            if lo <= p3 <= hi:
                return v
        elif k == p3:
            return v
    return "Neznamy"

def luhn_check_ean(digits: str) -> bool:
    total = 0
    for i, d in enumerate(digits[:-1]):
        n = int(d)
        total += n * (3 if i % 2 else 1) if len(digits) == 13 else n * (1 if i % 2 == 0 else 3)
    check = (10 - (total % 10)) % 10
    return check == int(digits[-1])

def parse_gs1(raw: str) -> Dict[str, Any]:
    s = raw.strip()
    if not s.isdigit():
        return {"ok": False, "error": "Neni cislo"}
    result: Dict[str, Any] = {"raw": s, "delka": len(s)}
    if len(s) == 13:
        result["format"] = "EAN-13"
        result["gs1_prefix"] = s[:3]
        result["zeme"] = lookup_gs1_prefix(s)
        result["company_prefix"] = s[:7]
        result["product_ref"] = s[7:12]
        result["check_digit"] = s[12]
        result["check_ok"] = luhn_check_ean(s)
    elif len(s) == 12:
        result["format"] = "UPC-A"
        result["system_digit"] = s[0]
        result["manufacturer"] = s[1:6]
        result["product"] = s[6:11]
        result["check_digit"] = s[11]
        result["check_ok"] = luhn_check_ean("0" + s)
    elif len(s) == 8:
        result["format"] = "EAN-8"
        result["gs1_prefix"] = s[:3]
        result["zeme"] = lookup_gs1_prefix(s)
        result["check_digit"] = s[7]
        result["check_ok"] = luhn_check_ean(s)
    elif len(s) == 14:
        result["format"] = "GTIN-14 / ITF-14"
        result["indicator"] = s[0]
        result["ean13"] = s[1:14]
        result["check_digit"] = s[13]
    elif len(s) == 18:
        result["format"] = "SSCC"
        result["extension"] = s[0]
        result["company_prefix"] = s[1:8]
        result["serial_ref"] = s[8:17]
        result["check_digit"] = s[17]
    else:
        result["format"] = f"Neznamy GS1 format ({len(s)} cislic)"
    return result


# ── RFID / NFC DUMP PARSER ───────────────────────────────────────────────────
MIFARE_BLOCK_SIZE = 16

def parse_rfid_dump(hex_dump: str) -> Dict[str, Any]:
    s = hex_dump.replace(" ", "").replace("\n", "").replace(":", "").upper()
    if not re.match(r'^[0-9A-F]+$', s):
        return {"ok": False, "error": "Neni platny HEX dump"}
    byte_len = len(s) // 2
    raw_bytes = bytes.fromhex(s)
    result: Dict[str, Any] = {
        "ok": True,
        "hex": s,
        "byte_length": byte_len,
        "blocks": [],
        "card_type": "Neznamy",
        "uid_candidate": "",
        "hints": [],
    }

    # Detekce typu karty podle velikosti
    if byte_len == 64:
        result["card_type"] = "Mifare Classic 1K (64 bloku x 16B)"
    elif byte_len == 256:
        result["card_type"] = "Mifare Classic 4K"
    elif byte_len == 16:
        result["card_type"] = "NFC NDEF / jeden blok"
    elif byte_len >= 4:
        result["card_type"] = f"Fragment ({byte_len} B)"

    # UID z prvnich 4-7 bytu
    result["uid_candidate"] = s[:8]
    result["uid_4b"] = s[:8]
    if byte_len >= 7:
        result["uid_7b"] = s[:14]

    # Parsovani bloku
    for i in range(0, min(len(s), 32*32), MIFARE_BLOCK_SIZE*2):
        block_hex = s[i:i+MIFARE_BLOCK_SIZE*2]
        if len(block_hex) < 2:
            break
        block_num = i // (MIFARE_BLOCK_SIZE*2)
        block_bytes = bytes.fromhex(block_hex.ljust(MIFARE_BLOCK_SIZE*2, "0"))
        ascii_repr = "".join(chr(b) if 32 <= b < 127 else "." for b in block_bytes)
        is_sector_trailer = (block_num + 1) % 4 == 0 and block_num > 0
        result["blocks"].append({
            "cislo": block_num,
            "hex": block_hex,
            "ascii": ascii_repr,
            "sector_trailer": is_sector_trailer,
        })

    # Heuristiky
    if s.startswith("00000000"):
        result["hints"].append("UID = 00000000 — mozna nulova/testovaci karta")
    if "FFFFFFFFFFFF" in s:
        result["hints"].append("Nalezeny vychozi klic FF FF FF FF FF FF (karta nebyla zmenena)")
    if "A0A1A2A3A4A5" in s:
        result["hints"].append("Nalezen transport klic A0A1A2A3A4A5")

    return result


# ── ENTROPY ANALYZER ─────────────────────────────────────────────────────────
def shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    freq: Dict[str, int] = {}
    for c in data:
        freq[c] = freq.get(c, 0) + 1
    n = len(data)
    return -sum((f/n) * math.log2(f/n) for f in freq.values())

def analyze_entropy(raw: str) -> Dict[str, Any]:
    s = raw.strip()
    entropy = shannon_entropy(s)
    max_entropy = math.log2(len(set(s))) if len(set(s)) > 1 else 0
    ratio = entropy / max_entropy if max_entropy > 0 else 0

    charset_score = 0
    has_upper = bool(re.search(r'[A-Z]', s))
    has_lower = bool(re.search(r'[a-z]', s))
    has_digit = bool(re.search(r'[0-9]', s))
    has_special = bool(re.search(r'[^A-Za-z0-9]', s))
    charset_score = sum([has_upper, has_lower, has_digit, has_special])

    verdict = "nezname"
    if entropy < 1.5:
        verdict = "velmi_nizka — pravdepodobne konstantni/prazdny retezec"
    elif entropy < 2.5:
        verdict = "nizka — pravdepodobne strukturovana data nebo opakovani"
    elif entropy < 3.5:
        verdict = "stredni — pravdepodobne text nebo ID"
    elif entropy < 4.5:
        verdict = "vysoka — pravdepodobne nahodna data, hash nebo sifrovany retezec"
    else:
        verdict = "velmi_vysoka — pravdepodobne kryptograficka data, klice nebo binarni data"

    return {
        "shannon_entropy": round(entropy, 4),
        "max_entropy": round(max_entropy, 4),
        "ratio": round(ratio, 4),
        "length": len(s),
        "unique_chars": len(set(s)),
        "charset": {
            "uppercase": has_upper, "lowercase": has_lower,
            "digits": has_digit, "special": has_special,
            "score": charset_score
        },
        "verdict": verdict,
        "pravdepodobne_nahodne": ratio > 0.85,
        "pravdepodobne_sifrovane": entropy > 4.0 and charset_score >= 3,
    }


# ── JWT INSPECTOR ─────────────────────────────────────────────────────────────
def inspect_jwt(raw: str) -> Dict[str, Any]:
    import time as _time
    s = raw.strip()
    parts = s.split(".")
    if len(parts) != 3:
        return {"ok": False, "error": "Neni JWT (ocekavano 3 casti oddelene teckou)"}
    def b64pad(x): return x + "=" * (-len(x) % 4)
    try:
        header  = json.loads(base64.urlsafe_b64decode(b64pad(parts[0])))
        payload = json.loads(base64.urlsafe_b64decode(b64pad(parts[1])))
    except Exception as e:
        return {"ok": False, "error": f"Decode selhal: {e}"}

    now = _time.time()
    warnings = []
    alg = header.get("alg", "?")
    if alg == "none":
        warnings.append("KRITICKY: alg=none — token bez podpisu!")
    if alg in ("HS256", "HS384", "HS512"):
        warnings.append("Symetricky algoritmus HMAC — klic musi zustat tajny")
    if "exp" in payload:
        exp = payload["exp"]
        if exp < now:
            warnings.append(f"Token VYPRŠEL: {_time.strftime('%d.%m.%Y %H:%M:%S', _time.localtime(exp))}")
        else:
            remaining = int(exp - now)
            warnings.append(f"Platnost vyprsi za {remaining//3600}h {(remaining%3600)//60}m")
    if "iat" in payload:
        iat = payload["iat"]
        payload["iat_human"] = _time.strftime("%d.%m.%Y %H:%M:%S", _time.localtime(iat))
    if "nbf" in payload and payload["nbf"] > now:
        warnings.append("Token jeste neni platny (nbf v budoucnosti)")
    sensitive_claims = ["password", "passwd", "secret", "key", "token", "credit", "ssn"]
    for k in payload:
        if any(s in k.lower() for s in sensitive_claims):
            warnings.append(f"Citlivy claim nalezen: '{k}'")

    return {
        "ok": True,
        "header": header,
        "payload": payload,
        "signature_b64": parts[2][:20] + "...",
        "algorithm": alg,
        "warnings": warnings,
        "risk_score": len(warnings) * 10,
    }


# ── CREDENTIAL SCANNER ───────────────────────────────────────────────────────
PATTERNS = [
    ("api_key_generic",    r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([A-Za-z0-9_\-]{20,})',     "API klic"),
    ("jwt_token",          r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',             "JWT token"),
    ("aws_access_key",     r'AKIA[0-9A-Z]{16}',                                                    "AWS Access Key"),
    ("aws_secret",         r'(?i)aws.{0,20}secret.{0,20}["\']?([A-Za-z0-9/+=]{40})',             "AWS Secret"),
    ("github_pat",         r'ghp_[A-Za-z0-9]{36}',                                                "GitHub PAT"),
    ("private_key_header", r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----',                    "Privatni klic PEM"),
    ("password_field",     r'(?i)(password|passwd|heslo)\s*[=:]\s*["\']?([^\s"\']{4,})',          "Heslo v textu"),
    ("ip_private",         r'\b(10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)\b', "Privatni IP"),
    ("email",              r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',                 "E-mail"),
    ("uuid",               r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', "UUID/GUID"),
    ("hex_key_32",         r'\b[0-9a-fA-F]{64}\b',                                                "HEX klic 256bit"),
    ("base64_secret",      r'(?i)(secret|token|key)\s*[=:]\s*["\']?([A-Za-z0-9+/]{32,}={0,2})',  "Base64 tajny retezec"),
    ("connection_string",  r'(?i)(mongodb|mysql|postgres|redis|mssql)://[^\s"\']+',               "Connection string"),
    ("bearer_token",       r'(?i)bearer\s+([A-Za-z0-9\-._~+/]+=*)',                              "Bearer token"),
]

def scan_credentials(text: str) -> Dict[str, Any]:
    findings = []
    for name, pattern, label in PATTERNS:
        for m in re.finditer(pattern, text):
            snippet = m.group(0)
            if len(snippet) > 60:
                snippet = snippet[:30] + "..." + snippet[-10:]
            findings.append({
                "typ": name,
                "label": label,
                "pozice": m.start(),
                "snippet": snippet,
                "zavaznost": "kriticka" if name in ("private_key_header","aws_access_key","aws_secret","github_pat") else "vysoka" if name in ("jwt_token","password_field","connection_string","bearer_token") else "stredni",
            })
    findings.sort(key=lambda x: x["pozice"])
    return {
        "ok": True,
        "celkem_nalez": len(findings),
        "kritickych": sum(1 for f in findings if f["zavaznost"] == "kriticka"),
        "vysokych": sum(1 for f in findings if f["zavaznost"] == "vysoka"),
        "findings": findings,
    }


# ── COMPARISON VIEW ───────────────────────────────────────────────────────────
def compare_identifiers(raw_a: str, raw_b: str) -> Dict[str, Any]:
    from services.workbench_service import ingest_identifier
    a = ingest_identifier(raw_a)
    b = ingest_identifier(raw_b)
    diff = []
    if a.type != b.type:
        diff.append(f"Ruzny typ: A={a.type}, B={b.type}")
    all_keys = set(a.attributes) | set(b.attributes)
    field_diff = {}
    for k in sorted(all_keys):
        va, vb = a.attributes.get(k, "—"), b.attributes.get(k, "—")
        field_diff[k] = {"a": va, "b": vb, "shoda": va == vb}
        if va != vb:
            diff.append(f"{k}: A={va} vs B={vb}")
    return {
        "a": a.to_dict(), "b": b.to_dict(),
        "shoda_typu": a.type == b.type,
        "shoda_normalized": a.normalized == b.normalized,
        "rozdily": diff,
        "pole_diff": field_diff,
    }


# ── HEX DUMP VIEWER ──────────────────────────────────────────────────────────
def hex_dump_view(raw: str) -> Dict[str, Any]:
    """Analyza libovolneho hex retezce - offset tabulka, ASCII preview, detekce hlavicek."""
    clean = re.sub(r'[^0-9a-fA-F]', '', raw)
    if len(clean) % 2 != 0:
        clean = clean[:-1]
    if not clean:
        return {"ok": False, "error": "Zadny platny HEX vstup"}

    data = bytes.fromhex(clean)
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append({
            "offset": f"{i:04X}",
            "hex": hex_part,
            "ascii": ascii_part,
        })

    # Detekce znamych hlavicek
    signatures = {
        "FFD8FF": "JPEG image",
        "89504E47": "PNG image",
        "504B0304": "ZIP/Office file",
        "25504446": "PDF file",
        "4D5A": "Windows PE/EXE",
        "1F8B": "GZIP compressed",
        "7F454C46": "ELF binary (Linux)",
        "CAFEBABE": "Java class file",
        "D0CF11E0": "OLE2 (old Office)",
        "3082": "ASN.1 / X.509 cert",
    }
    detected_sig = None
    for sig, label in signatures.items():
        if clean.upper().startswith(sig):
            detected_sig = label
            break

    # Shannon entropie dat
    if data:
        from collections import Counter
        counts = Counter(data)
        entropy = -sum((c/len(data)) * math.log2(c/len(data)) for c in counts.values())
    else:
        entropy = 0.0

    return {
        "ok": True,
        "length_bytes": len(data),
        "lines": lines,
        "signature": detected_sig,
        "entropy": round(entropy, 3),
        "entropy_verdict": "nahodny/sifrovany" if entropy > 7.0 else "strukturovany" if entropy < 4.0 else "smiseny",
        "raw_hex": clean.upper(),
    }


# ── URL DECODER / ANALYZER ────────────────────────────────────────────────────
def url_decode_analyze(raw: str) -> Dict[str, Any]:
    """Dekodovani a forenzni analyza URL - parametry, tokeny, rizika."""
    from urllib.parse import urlparse, parse_qs, unquote, unquote_plus
    import base64 as b64

    # Postupne dekodovat %xx
    decoded_once = unquote(raw)
    decoded_twice = unquote(decoded_once)

    result = {
        "original": raw,
        "decoded_once": decoded_once,
        "decoded_twice": decoded_twice,
        "double_encoded": decoded_once != decoded_twice,
    }

    # Parsovat jako URL
    try:
        parsed = urlparse(decoded_once)
        params = parse_qs(parsed.query)
        result["parsed"] = {
            "scheme": parsed.scheme,
            "host": parsed.netloc,
            "path": parsed.path,
            "params": {k: v[0] if len(v)==1 else v for k,v in params.items()},
            "fragment": parsed.fragment,
        }

        # Analyza parametru
        risks = []
        interesting_params = []
        for k, vals in params.items():
            v = vals[0] if vals else ""
            # JWT v parametru?
            if v.count('.') == 2 and len(v) > 50:
                interesting_params.append({"param": k, "hint": "mozny JWT token"})
                risks.append(f"Parametr '{k}' obsahuje JWT-like hodnotu")
            # Base64?
            if len(v) > 8 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in v):
                try:
                    dec = b64.b64decode(v + '===').decode('utf-8', 'ignore')
                    if any(c.isprintable() and not c.isspace() for c in dec[:20]):
                        interesting_params.append({"param": k, "hint": "base64", "decoded": dec[:80]})
                except Exception:
                    pass
            # Redirect?
            kl = k.lower()
            if kl in ('redirect', 'return', 'next', 'url', 'goto', 'redirect_uri', 'callback'):
                risks.append(f"Open redirect parametr: '{k}'")
            # SQL injection znaky?
            if any(s in v for s in ("'", '"', '--', 'OR 1', 'UNION', 'SELECT')):
                risks.append(f"Mozny SQLi v parametru '{k}'")

        result["interesting_params"] = interesting_params
        result["risks"] = risks
        result["risk_score"] = len(risks) * 15
    except Exception as e:
        result["parse_error"] = str(e)

    return result


# ── CHECKSUM LAB ──────────────────────────────────────────────────────────────
def checksum_lab(raw: str, mode: str = "auto") -> Dict[str, Any]:
    """Vypocet a validace ruznych kontrolnich souctu."""
    import hashlib
    import binascii

    results: Dict[str, Any] = {"input": raw, "mode": mode, "checksums": {}}

    # Standardni hashe (vzdy)
    raw_b = raw.encode('utf-8')
    results["checksums"]["md5"] = hashlib.md5(raw_b).hexdigest()
    results["checksums"]["sha1"] = hashlib.sha1(raw_b).hexdigest()
    results["checksums"]["sha256"] = hashlib.sha256(raw_b).hexdigest()
    results["checksums"]["crc32"] = format(binascii.crc32(raw_b) & 0xFFFFFFFF, '08X')

    # Luhn (kreditni karty, IMEI)
    digits = re.sub(r'\D', '', raw)
    if digits and (mode in ('auto', 'luhn')):
        def luhn_check(n):
            s = 0
            odd = True
            for d in reversed(n):
                x = int(d)
                if not odd:
                    x *= 2
                    if x > 9: x -= 9
                s += x
                odd = not odd
            return s % 10 == 0
        luhn_valid = luhn_check(digits)
        results["checksums"]["luhn"] = {"digits": digits, "valid": luhn_valid}

    # EAN checksum
    if len(digits) in (8, 13) and (mode in ('auto', 'ean')):
        weights = [1, 3] * 10
        total = sum(int(d) * w for d, w in zip(digits[:-1], weights[:len(digits)-1]))
        check_digit = (10 - (total % 10)) % 10
        results["checksums"]["ean"] = {
            "digits": digits,
            "computed_check": check_digit,
            "provided_check": int(digits[-1]),
            "valid": check_digit == int(digits[-1]),
        }

    # GTIN-14
    if len(digits) == 14 and (mode in ('auto', 'gtin14')):
        weights = [3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3]
        total = sum(int(d) * w for d, w in zip(digits[:-1], weights))
        check_digit = (10 - (total % 10)) % 10
        results["checksums"]["gtin14"] = {
            "computed_check": check_digit,
            "provided_check": int(digits[-1]),
            "valid": check_digit == int(digits[-1]),
        }

    # ISBN-13 (= EAN-13 s prefixem 978/979)
    if len(digits) == 13 and digits[:3] in ('978', '979') and (mode in ('auto', 'isbn')):
        results["checksums"]["isbn13_valid"] = results["checksums"].get("ean", {}).get("valid", False)

    return results
