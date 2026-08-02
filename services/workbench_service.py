# services/workbench_service.py
import base64, zlib, re, time, random, string
from dataclasses import dataclass, field
from typing import Dict, Any, List
from urllib.parse import urlparse, parse_qs, unquote

try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class Identifier:
    raw: str
    type: str
    normalized: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self):
        return {"raw": self.raw, "type": self.type, "normalized": self.normalized,
                "attributes": self.attributes, "warnings": self.warnings}


def parse_access_gate(raw: str) -> Dict[str, Any]:
    """MM YY DD HH MM SS FL(2) TY(2) PADD(4) ID(6) = 26 digits"""
    s = raw.strip()
    if len(s) != 26 or not s.isdigit():
        return {}
    try:
        MM, YY, DD = s[0:2], s[2:4], s[4:6]
        HH, mi, SS = s[6:8], s[8:10], s[10:12]
        FL, TY, PADD, ID = s[12:14], s[14:16], s[16:20], s[20:26]
        if not (1 <= int(MM) <= 12): return {}
        if not (1 <= int(DD) <= 31): return {}
        if not (0 <= int(HH) <= 23): return {}
        if not (0 <= int(mi) <= 59): return {}
        if not (0 <= int(SS) <= 59): return {}
        flag_map = {"00": "vstup", "01": "vystup", "02": "alarm", "03": "odmitnuto"}
        return {
            "datum": f"{DD}.{MM}.20{YY}",
            "cas": f"{HH}:{mi}:{SS}",
            "datetime_iso": f"20{YY}-{MM}-{DD}T{HH}:{mi}:{SS}",
            "mesic": int(MM), "rok": int("20"+YY), "den": int(DD),
            "hodiny": int(HH), "minuty": int(mi), "sekundy": int(SS),
            "flag": FL, "flag_label": flag_map.get(FL, f"neznamy ({FL})"),
            "typ_brany": TY, "padding": PADD,
            "id_karty": ID, "id_karty_int": int(ID),
        }
    except Exception:
        return {}


def classify_identifier(raw: str) -> str:
    s = raw.strip()
    if len(s) == 26 and s.isdigit():
        if parse_access_gate(s):
            return "access_gate"
    if s.startswith(("http://", "https://")):
        return "url"
    if s.startswith("{") or s.startswith("["):
        try:
            import json; json.loads(s); return "json"
        except Exception:
            pass
    if re.match(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$', s):
        return "jwt"
    if re.match(r'^([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}$', s):
        return "mac"
    if re.match(r'^\d{15}$', s): return "imei"
    if re.match(r'^\d{13}$', s): return "ean13"
    if re.match(r'^\d{8}$', s):  return "ean8"
    if re.match(r'^\d{12}$', s): return "upc_a"
    if re.match(r'^[0-9A-Fa-f]+$', s) and len(s) % 2 == 0 and len(s) >= 8:
        return "hex"
    try:
        if re.match(r'^[A-Za-z0-9+/]+=*$', s) and len(s) % 4 == 0 and len(s) >= 8:
            base64.b64decode(s); return "base64"
    except Exception:
        pass
    if re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', s):
        return "uuid"
    return "unknown"


def normalize_identifier(raw: str, id_type: str) -> str:
    if id_type == "hex": return raw.strip().lower()
    if id_type == "mac": return raw.upper().replace("-", ":")
    return raw.strip()


def enrich_attributes(identifier: Identifier) -> None:
    t, raw = identifier.type, identifier.normalized
    if t == "access_gate":
        identifier.attributes.update(parse_access_gate(raw))
    elif t == "url":
        u = urlparse(raw)
        identifier.attributes.update({"host": u.netloc, "path": u.path,
                                       "params": parse_qs(u.query), "scheme": u.scheme})
    elif t == "hex":
        identifier.attributes["length_bytes"] = len(raw) // 2
    elif t == "base64":
        try:
            d = base64.b64decode(raw + "===")
            identifier.attributes["decoded_hex"] = d.hex()
            identifier.attributes["decoded_len"] = len(d)
            try: identifier.attributes["decoded_utf8"] = d.decode("utf-8")
            except Exception: pass
        except Exception:
            identifier.warnings.append("base64 decode failed")
    elif t == "jwt":
        parts = raw.split(".")
        try:
            import json as _j
            def pad(s): return s + "=" * (-len(s) % 4)
            identifier.attributes["header"]  = _j.loads(base64.urlsafe_b64decode(pad(parts[0])))
            identifier.attributes["payload"] = _j.loads(base64.urlsafe_b64decode(pad(parts[1])))
        except Exception as e:
            identifier.warnings.append(f"JWT: {e}")
    elif t == "ean13":
        identifier.attributes.update({"check_digit": raw[-1],
                                       "company_prefix": raw[:7], "gs1_prefix": raw[:3]})
    elif t == "imei":
        identifier.attributes.update({"tac": raw[:8], "serial": raw[8:14], "check": raw[14]})
    elif t == "mac":
        p = raw.upper().replace("-",":").split(":")
        identifier.attributes.update({"oui": ":".join(p[:3]), "nic": ":".join(p[3:])})


def ingest_identifier(raw: str, meta: Dict[str, Any] = None) -> Identifier:
    id_type = classify_identifier(raw)
    norm = normalize_identifier(raw, id_type)
    ident = Identifier(raw=raw, type=id_type, normalized=norm,
                       attributes=dict(meta or {}), warnings=[])
    enrich_attributes(ident)
    return ident


def run_analysis_pipeline(identifier_data: Dict[str, Any]) -> Dict[str, Any]:
    ident = Identifier(
        raw=identifier_data.get("raw", ""),
        type=identifier_data.get("type", "unknown"),
        normalized=identifier_data.get("normalized", identifier_data.get("raw", "")),
        attributes=dict(identifier_data.get("attributes", {})),
        warnings=list(identifier_data.get("warnings", [])),
    )
    if ident.type in ("unknown", ""):
        ident.type = classify_identifier(ident.raw)
        ident.normalized = normalize_identifier(ident.raw, ident.type)
        enrich_attributes(ident)

    risk_score = 0
    notes = []

    if ident.type == "access_gate":
        ag = ident.attributes
        notes.append(f"Pruchod branou: {ag.get('datum','')} {ag.get('cas','')}")
        notes.append(f"ID karty: {ag.get('id_karty','')} | Typ brany: {ag.get('typ_brany','')}")
        notes.append(f"Status: {ag.get('flag_label','')}")
        if ag.get("flag") not in ("00", "01"):
            risk_score += 30
            notes.append("Nestandardni flag pruchodu!")
    elif ident.type == "url":
        path = ident.attributes.get("path", "")
        if any(x in path for x in ("login", "auth", "token")):
            risk_score += 20; notes.append("URL obsahuje autentizacni cestu.")
        if not ident.normalized.startswith("https://"):
            risk_score += 15; notes.append("Nezabezpecene HTTP.")
    elif ident.type == "jwt":
        payload = ident.attributes.get("payload", {})
        import time as _t
        if "exp" in payload and payload["exp"] < _t.time():
            risk_score += 25; notes.append("JWT token vypršel.")
        notes.append(f"Algoritmus: {ident.attributes.get('header',{}).get('alg','?')}")

    return {"identifier": ident.to_dict(), "risk_score": risk_score, "notes": notes}


def run_reverse_engineering(raw: str) -> Dict[str, Any]:
    results = []
    s = raw.strip()
    if len(s) == 26 and s.isdigit():
        ag = parse_access_gate(s)
        if ag:
            results.append({"metoda": "access_gate_parser", "ok": True,
                            "typ": "Kod vstupni brany", "vysledek": ag})
    try:
        d = base64.b64decode(s + "===")
        results.append({"metoda": "base64", "ok": True, "decoded_hex": d.hex(),
                        "decoded_utf8": d.decode("utf-8", errors="replace")})
        try:
            dc = zlib.decompress(d)
            results.append({"metoda": "base64+zlib", "ok": True,
                            "decoded": dc.decode("utf-8", errors="replace")})
        except Exception:
            pass
    except Exception:
        results.append({"metoda": "base64", "ok": False})
    if re.match(r'^[0-9A-Fa-f]+$', s) and len(s) % 2 == 0:
        rb = bytes.fromhex(s)
        results.append({"metoda": "hex_decode", "ok": True,
                        "decoded_utf8": rb.decode("utf-8", errors="replace"),
                        "length_bytes": len(rb)})
        try:
            dc = zlib.decompress(rb)
            results.append({"metoda": "hex+zlib", "ok": True,
                            "decoded": dc.decode("utf-8", errors="replace")})
        except Exception:
            pass
    du = unquote(s)
    if du != s:
        results.append({"metoda": "url_decode", "ok": True, "decoded": du})
    if re.match(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$', s):
        parts = s.split(".")
        try:
            import json as _j
            def pad(x): return x + "=" * (-len(x) % 4)
            results.append({"metoda": "jwt_decode", "ok": True,
                            "header": _j.loads(base64.urlsafe_b64decode(pad(parts[0]))),
                            "payload": _j.loads(base64.urlsafe_b64decode(pad(parts[1])))})
        except Exception as e:
            results.append({"metoda": "jwt_decode", "ok": False, "error": str(e)})
    return {"input": raw, "candidates": results}


def _gen_payload(mode: str) -> str:
    if mode == "url":
        t = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        return f"https://example.com/gate?token={t}"
    if mode == "hex":
        return "".join(random.choices("0123456789ABCDEF", k=32))
    if mode == "base64":
        return base64.b64encode("".join(random.choices(string.ascii_letters, k=12)).encode()).decode()
    if mode == "gtin":
        return "".join(random.choices(string.digits, k=13))
    if mode == "access_gate":
        import datetime
        n = datetime.datetime.now()
        card = f"{random.randint(1000,99999):06d}"
        return f"{n.month:02d}{n.year%100:02d}{n.day:02d}{n.hour:02d}{n.minute:02d}{n.second:02d}00100000{card}"
    return "TEST"


def run_test_harness(target: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    runs = min(int(profile.get("runs", 5)), 20)
    mode = profile.get("mode", "url")
    results = []
    for _ in range(runs):
        payload = _gen_payload(mode)
        row: Dict[str, Any] = {"payload": payload}
        if HAS_REQUESTS:
            try:
                r = _requests.post(target, json={"raw": payload}, timeout=5)
                row.update({"status": r.status_code,
                            "time_ms": int(r.elapsed.total_seconds()*1000),
                            "body_sample": r.text[:300]})
            except Exception as e:
                row["error"] = str(e)
        else:
            import urllib.request as _ur
            import json as _j
            try:
                req = _ur.Request(target, method="POST")
                req.add_header("Content-Type", "application/json")
                req.data = _j.dumps({"raw": payload}).encode()
                with _ur.urlopen(req, timeout=5) as resp:
                    row.update({"status": resp.status,
                                "body_sample": resp.read(300).decode("utf-8", errors="replace")})
            except Exception as e:
                row["error"] = str(e)
        results.append(row)
        time.sleep(0.1)
    return {"target": target, "profile": profile, "runs": runs, "results": results}
