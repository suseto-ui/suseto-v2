# services/workbench_service.py
# Data & Identifier Analysis Workbench — backend service

import base64
import zlib
import re
import time
import random
import string
from dataclasses import dataclass, field
from typing import Dict, Any, List
from urllib.parse import urlparse, parse_qs, unquote

try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ── Datový model ──────────────────────────────────────────────────────────────

@dataclass
class Identifier:
    raw: str
    type: str
    normalized: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw": self.raw,
            "type": self.type,
            "normalized": self.normalized,
            "attributes": self.attributes,
            "warnings": self.warnings,
        }


# ── ACCESS GATE parser ────────────────────────────────────────────────────────

def parse_access_gate(raw: str) -> Dict[str, Any]:
    """
    Formát vstupní brány (26 číslic):
    MM YY DD HH MM SS FL TY PADD(4) ID(6)
    Pozice: 0-1 měsíc, 2-3 rok(20xx), 4-5 den,
            6-7 hodiny, 8-9 minuty, 10-11 sekundy,
            12-13 flag, 14-15 typ brány, 16-19 padding, 20-25 ID karty
    """
    s = raw.strip()
    if len(s) != 26 or not s.isdigit():
        return {}
    try:
        MM   = s[0:2]
        YY   = s[2:4]
        DD   = s[4:6]
        HH   = s[6:8]
        mi   = s[8:10]
        SS   = s[10:12]
        FL   = s[12:14]
        TY   = s[14:16]
        PADD = s[16:20]
        ID   = s[20:26]

        # validace
        if not (1 <= int(MM) <= 12): return {}
        if not (1 <= int(DD) <= 31): return {}
        if not (0 <= int(HH) <= 23): return {}
        if not (0 <= int(mi) <= 59): return {}
        if not (0 <= int(SS) <= 59): return {}

        flag_map = {"00": "vstup", "01": "výstup", "02": "alarm", "03": "odmítnut"}
        flag_label = flag_map.get(FL, f"neznámý ({FL})")

        return {
            "datum": f"{DD}.{MM}.20{YY}",
            "cas": f"{HH}:{mi}:{SS}",
            "datetime_iso": f"20{YY}-{MM}-{DD}T{HH}:{mi}:{SS}",
            "mesic": int(MM),
            "rok": int("20" + YY),
            "den": int(DD),
            "hodiny": int(HH),
            "minuty": int(mi),
            "sekundy": int(SS),
            "flag": FL,
            "flag_label": flag_label,
            "typ_brany": TY,
            "padding": PADD,
            "id_karty": ID,
            "id_karty_int": int(ID),
        }
    except Exception:
        return {}


# ── Klasifikace ───────────────────────────────────────────────────────────────

def classify_identifier(raw: str) -> str:
    s = raw.strip()

    # Access gate: přesně 26 číslic + validní datum/čas
    if len(s) == 26 and s.isdigit():
        ag = parse_access_gate(s)
        if ag:
            return "access_gate"

    if s.startswith(("http://", "https://")):
        return "url"
    if s.startswith("{") or s.startswith("["):
        try:
            import json
            json.loads(s)
            return "json"
        except Exception:
            pass
    # JWT: xxx.yyy.zzz base64url
    if re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$", s):
        return "jwt"
    # MAC adresa
    if re.match(r"^([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}$", s):
        return "mac"
    # IMEI: 15 číslic
    if re.match(r"^\d{15}$", s):
        return "imei"
    # EAN-13 / GTIN: 13 číslic
    if re.match(r"^\d{13}$", s):
        return "ean13"
    # EAN-8
    if re.match(r"^\d{8}$", s):
        return "ean8"
    # UPC-A: 12 číslic
    if re.match(r"^\d{12}$", s):
        return "upc_a"
    # HEX string
    if re.match(r"^[0-9A-Fa-f]+$", s) and len(s) % 2 == 0 and len(s) >= 8:
        return "hex"
    # Base64
    try:
        if re.match(r"^[A-Za-z0-9+/]+=*$", s) and len(s) % 4 == 0 and len(s) >= 8:
            base64.b64decode(s)
            return "base64"
    except Exception:
        pass
    # UUID / GUID
    if re.match(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", s):
        return "uuid"
    return "unknown"


def normalize_identifier(raw: str, id_type: str) -> str:
    if id_type == "url":
        return raw.strip()
    if id_type in ("hex",):
        return raw.strip().lower()
    if id_type == "mac":
        return raw.upper().replace("-", ":")
    return raw.strip()


# ── Enrich attributes ─────────────────────────────────────────────────────────

def enrich_attributes(identifier: Identifier) -> None:
    t = identifier.type
    raw = identifier.normalized

    if t == "access_gate":
        ag = parse_access_gate(raw)
        identifier.attributes.update(ag)

    elif t == "url":
        u = urlparse(raw)
        identifier.attributes["host"] = u.netloc
        identifier.attributes["path"] = u.path
        identifier.attributes["params"] = parse_qs(u.query)
        identifier.attributes["scheme"] = u.scheme

    elif t == "hex":
        identifier.attributes["length_bytes"] = len(raw) // 2
        identifier.attributes["hex_upper"] = raw.upper()

    elif t == "base64":
        try:
            decoded = base64.b64decode(raw + "===")
            identifier.attributes["decoded_hex"] = decoded.hex()
            identifier.attributes["decoded_len"] = len(decoded)
            try:
                identifier.attributes["decoded_utf8"] = decoded.decode("utf-8")
            except Exception:
                pass
        except Exception:
            identifier.warnings.append("base64 decode failed")

    elif t == "jwt":
        parts = raw.split(".")
        try:
            def b64pad(s):
                return s + "=" * (-len(s) % 4)
            import json as _json
            header = _json.loads(base64.urlsafe_b64decode(b64pad(parts[0])))
            payload = _json.loads(base64.urlsafe_b64decode(b64pad(parts[1])))
            identifier.attributes["header"] = header
            identifier.attributes["payload"] = payload
        except Exception as e:
            identifier.warnings.append(f"JWT decode partial: {e}")

    elif t == "ean13":
        identifier.attributes["check_digit"] = raw[-1]
        identifier.attributes["company_prefix"] = raw[:7]
        identifier.attributes["gs1_prefix"] = raw[:3]

    elif t == "imei":
        identifier.attributes["tac"] = raw[:8]
        identifier.attributes["serial"] = raw[8:14]
        identifier.attributes["check"] = raw[14]

    elif t == "mac":
        parts = raw.upper().replace("-", ":").split(":")
        identifier.attributes["oui"] = ":".join(parts[:3])
        identifier.attributes["nic"] = ":".join(parts[3:])


# ── Ingest ────────────────────────────────────────────────────────────────────

def ingest_identifier(raw: str, meta: Dict[str, Any] = None) -> Identifier:
    id_type = classify_identifier(raw)
    normalized = normalize_identifier(raw, id_type)
    identifier = Identifier(
        raw=raw,
        type=id_type,
        normalized=normalized,
        attributes=dict(meta or {}),
        warnings=[]
    )
    enrich_attributes(identifier)
    return identifier


# ── Analysis pipeline ─────────────────────────────────────────────────────────

def run_analysis_pipeline(identifier_data: Dict[str, Any]) -> Dict[str, Any]:
    identifier = Identifier(
        raw=identifier_data.get("raw", ""),
        type=identifier_data.get("type", "unknown"),
        normalized=identifier_data.get("normalized", identifier_data.get("raw", "")),
        attributes=dict(identifier_data.get("attributes", {})),
        warnings=list(identifier_data.get("warnings", [])),
    )

    if identifier.type in ("unknown", ""):
        identifier.type = classify_identifier(identifier.raw)
        identifier.normalized = normalize_identifier(identifier.raw, identifier.type)
        enrich_attributes(identifier)

    risk_score = 0
    notes = []

    if identifier.type == "access_gate":
        ag = identifier.attributes
        notes.append(f"Průchod branou: {ag.get('datum','')} {ag.get('cas','')}")
        notes.append(f"ID karty: {ag.get('id_karty','')} | Typ brány: {ag.get('typ_brany','')}")
        notes.append(f"Status: {ag.get('flag_label','')}")
        if ag.get("flag") not in ("00", "01"):
            risk_score += 30
            notes.append("Nestandardní flag průchodu!")

    elif identifier.type == "url":
        host = identifier.attributes.get("host", "")
        path = identifier.attributes.get("path", "")
        if "login" in path or "auth" in path or "token" in path:
            risk_score += 20
            notes.append("URL obsahuje autentizační cestu.")
        if not identifier.normalized.startswith("https://"):
            risk_score += 15
            notes.append("Nezabezpečené HTTP.")

    elif identifier.type == "jwt":
        payload = identifier.attributes.get("payload", {})
        import time as _time
        if "exp" in payload and payload["exp"] < _time.time():
            risk_score += 25
            notes.append("JWT token vypršel.")
        notes.append(f"Algoritmus: {identifier.attributes.get('header', {}).get('alg', '?')}")

    return {
        "identifier": identifier.to_dict(),
        "risk_score": risk_score,
        "notes": notes,
    }


# ── Reverse engineering ───────────────────────────────────────────────────────

def run_reverse_engineering(raw: str) -> Dict[str, Any]:
    results = []
    s = raw.strip()

    # Access gate detekce
    if len(s) == 26 and s.isdigit():
        ag = parse_access_gate(s)
        if ag:
            results.append({
                "metoda": "access_gate_parser",
                "ok": True,
                "typ": "Kód vstupní brány",
                "vysledek": ag
            })

    # Base64 pokus
    try:
        decoded = base64.b64decode(s + "===")
        results.append({"metoda": "base64", "ok": True, "decoded_hex": decoded.hex(),
                        "decoded_utf8": decoded.decode("utf-8", errors="replace")})
        # zlib na base64 výstupu
        try:
            decompressed = zlib.decompress(decoded)
            results.append({"metoda": "base64+zlib", "ok": True,
                            "decoded": decompressed.decode("utf-8", errors="replace")})
        except Exception:
            pass
    except Exception:
        results.append({"metoda": "base64", "ok": False})

    # HEX pokus
    if re.match(r"^[0-9A-Fa-f]+$", s) and len(s) % 2 == 0:
        raw_bytes = bytes.fromhex(s)
        results.append({"metoda": "hex_decode", "ok": True,
                        "decoded_utf8": raw_bytes.decode("utf-8", errors="replace"),
                        "length_bytes": len(raw_bytes)})
        try:
            decompressed = zlib.decompress(raw_bytes)
            results.append({"metoda": "hex+zlib", "ok": True,
                            "decoded": decompressed.decode("utf-8", errors="replace")})
        except Exception:
            pass

    # URL decode
    try:
        decoded_url = unquote(s)
        if decoded_url != s:
            results.append({"metoda": "url_decode", "ok": True, "decoded": decoded_url})
    except Exception:
        pass

    # JWT
    if re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$", s):
        parts = s.split(".")
        try:
            import json as _json
            def b64pad(x): return x + "=" * (-len(x) % 4)
            header = _json.loads(base64.urlsafe_b64decode(b64pad(parts[0])))
            payload = _json.loads(base64.urlsafe_b64decode(b64pad(parts[1])))
            results.append({"metoda": "jwt_decode", "ok": True,
                            "header": header, "payload": payload})
        except Exception as e:
            results.append({"metoda": "jwt_decode", "ok": False, "error": str(e)})

    return {"input": raw, "candidates": results}


# ── Test harness ──────────────────────────────────────────────────────────────

def _gen_payload(mode: str) -> str:
    if mode == "url":
        tok = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        return f"https://example.com/gate?token={tok}"
    if mode == "hex":
        return "".join(random.choices("0123456789ABCDEF", k=32))
    if mode == "base64":
        data = "".join(random.choices(string.ascii_letters, k=12)).encode()
        return base64.b64encode(data).decode()
    if mode == "gtin":
        return "".join(random.choices(string.digits, k=13))
    if mode == "access_gate":
        import datetime
        now = datetime.datetime.now()
        mm = f"{now.month:02d}"
        yy = f"{now.year % 100:02d}"
        dd = f"{now.day:02d}"
        hh = f"{now.hour:02d}"
        mi = f"{now.minute:02d}"
        ss = f"{now.second:02d}"
        card_id = f"{random.randint(1000, 99999):06d}"
        return f"{mm}{yy}{dd}{hh}{mi}{ss}00100000{card_id}"
    return "TEST_PAYLOAD"


def run_test_harness(target: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    runs = min(int(profile.get("runs", 5)), 20)
    mode = profile.get("mode", "url")
    results = []

    for _ in range(runs):
        payload = _gen_payload(mode)
        row: Dict[str, Any] = {"payload": payload}
        if HAS_REQUESTS:
            try:
                resp = _requests.post(target, json={"raw": payload}, timeout=5)
                row["status"] = resp.status_code
                row["time_ms"] = int(resp.elapsed.total_seconds() * 1000)
                row["body_sample"] = resp.text[:300]
            except Exception as e:
                row["error"] = str(e)
        else:
            import urllib.request as _ur
            import urllib.error
            try:
                req = _ur.Request(target, method="POST")
                req.add_header("Content-Type", "application/json")
                import json as _json
                req.data = _json.dumps({"raw": payload}).encode()
                with _ur.urlopen(req, timeout=5) as r:
                    row["status"] = r.status
                    row["body_sample"] = r.read(300).decode("utf-8", errors="replace")
            except Exception as e:
                row["error"] = str(e)
        results.append(row)
        time.sleep(0.1)

    return {"target": target, "profile": profile, "runs": runs, "results": results}
