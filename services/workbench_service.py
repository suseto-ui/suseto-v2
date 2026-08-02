import base64, re, zlib, json, string, random, time
from urllib.parse import urlparse, parse_qs
from collections import Counter
import math

# ── Identifier model ──────────────────────────────────────────────────────────
class Identifier:
    def __init__(self, raw, id_type="unknown", normalized="", attributes=None, warnings=None):
        self.raw = raw
        self.type = id_type
        self.normalized = normalized or raw
        self.attributes = attributes or {}
        self.warnings = warnings or []

    def to_dict(self):
        return {
            "raw": self.raw,
            "type": self.type,
            "normalized": self.normalized,
            "attributes": self.attributes,
            "warnings": self.warnings,
        }

# ── Classification ─────────────────────────────────────────────────────────────
def classify(raw: str) -> str:
    t = (raw or "").strip()
    if not t:
        return "empty"
    if t.startswith("http://") or t.startswith("https://"):
        return "url"
    if t.startswith("WIFI:"):
        return "wifi-qr"
    if t.startswith("{") and t.endswith("}"):
        try: json.loads(t); return "json"
        except: pass
    if t.count(".") == 2:
        return "jwt-like"
    compact = re.sub(r"\s+", "", t)
    if compact and all(c in "0123456789abcdefABCDEF" for c in compact) and len(compact) >= 8 and len(compact) % 2 == 0:
        return "hex"
    try:
        dec = base64.b64decode(t + "===")
        if len(t) >= 8:
            return "base64-like"
    except Exception:
        pass
    if re.fullmatch(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", t):
        return "mac"
    if t.isdigit() and len(t) in (8, 12, 13, 14):
        return "numeric-gtin"
    return "unknown"


def normalize(raw: str, id_type: str) -> str:
    t = (raw or "").strip()
    if id_type == "hex":
        return re.sub(r"\s+", "", t).lower()
    if id_type == "mac":
        return t.lower()
    return t


def enrich(identifier: Identifier) -> None:
    t = identifier.type
    n = identifier.normalized
    if t == "url":
        p = urlparse(n)
        identifier.attributes.update({
            "scheme": p.scheme, "host": p.netloc,
            "path": p.path, "params": parse_qs(p.query),
        })
        if any(x in p.path.lower() for x in ("login","admin","auth","reset","password")):
            identifier.warnings.append("URL vypadá jako citlivý endpoint.")
    elif t == "json":
        try:
            obj = json.loads(n)
            identifier.attributes["keys"] = list(obj.keys())[:20] if isinstance(obj, dict) else []
            identifier.attributes["json_type"] = type(obj).__name__
        except Exception as ex:
            identifier.warnings.append(f"JSON parse chyba: {ex}")
    elif t == "hex":
        identifier.attributes["length_bytes"] = len(n) // 2
        try:
            identifier.attributes["ascii_preview"] = bytes.fromhex(n).decode("utf-8","replace")[:120]
        except Exception as ex:
            identifier.warnings.append(f"HEX decode chyba: {ex}")
    elif t == "base64-like":
        try:
            dec = base64.b64decode(n + "===")
            identifier.attributes["decoded_len"] = len(dec)
            identifier.attributes["decoded_preview"] = dec[:80].decode("utf-8","replace")
        except Exception as ex:
            identifier.warnings.append(f"Base64 decode chyba: {ex}")
    elif t == "numeric-gtin":
        identifier.attributes["length"] = len(n)
        identifier.attributes["gtin_type"] = {8:"GTIN-8",12:"GTIN-12",13:"GTIN-13",14:"GTIN-14"}.get(len(n),"unknown")


# ── Analysis pipeline ─────────────────────────────────────────────────────────
def run_analysis_pipeline(identifier_data: dict) -> dict:
    identifier = Identifier(
        raw=identifier_data.get("raw", ""),
        id_type=identifier_data.get("type", "unknown"),
        normalized=identifier_data.get("normalized", ""),
        attributes=identifier_data.get("attributes", {}),
        warnings=identifier_data.get("warnings", []),
    )
    if identifier.type in ("unknown", ""):
        identifier.type = classify(identifier.raw)
    identifier.normalized = normalize(identifier.raw, identifier.type)
    enrich(identifier)
    risk_score = 0
    notes = []
    if identifier.warnings:
        risk_score += 25
        notes.extend(identifier.warnings)
    if identifier.type in ("base64-like","hex","jwt-like"):
        risk_score += 10
        notes.append("Payload doporučen k reverzní analýze.")
    return {
        "identifier": identifier.to_dict(),
        "risk_score": risk_score,
        "notes": notes,
    }


def ingest_identifier(raw: str, meta: dict = None) -> Identifier:
    id_type = classify(raw)
    return Identifier(raw=raw, id_type=id_type, normalized=normalize(raw, id_type), attributes=meta or {})


# ── Reverse engineering engine ─────────────────────────────────────────────────
def _ascii_ratio(s):
    if not s: return 0
    good = sum(1 for ch in s if 32 <= ord(ch) < 127 or ch in "\n\r\t")
    return round(good / len(s), 4)

def _entropy(s):
    if not s: return 0.0
    n = len(s); c = Counter(s)
    return round(-sum((v/n)*math.log2(v/n) for v in c.values()), 4)

def run_reverse_engineering(raw: str) -> dict:
    candidates = []
    # raw
    candidates.append({"kind":"raw","ok":True,"preview":raw[:120],"entropy":_entropy(raw),"ascii_ratio":_ascii_ratio(raw)})
    # base64
    try:
        dec = base64.b64decode(raw + "===")
        preview = dec[:120].decode("utf-8","replace")
        candidates.append({"kind":"base64","ok":True,"decoded_hex":dec.hex()[:80],"preview":preview,"entropy":_entropy(preview),"ascii_ratio":_ascii_ratio(preview)})
        # zlib after base64
        try:
            z = zlib.decompress(dec)
            zp = z[:120].decode("utf-8","replace")
            candidates.append({"kind":"base64+zlib","ok":True,"preview":zp,"entropy":_entropy(zp),"ascii_ratio":_ascii_ratio(zp)})
        except: pass
    except: candidates.append({"kind":"base64","ok":False,"error":"Not valid base64"})
    # hex
    compact = re.sub(r"\s+","",raw)
    if all(c in "0123456789abcdefABCDEF" for c in compact) and len(compact) % 2 == 0:
        try:
            dec = bytes.fromhex(compact)
            preview = dec[:120].decode("utf-8","replace")
            candidates.append({"kind":"hex","ok":True,"preview":preview,"length_bytes":len(dec),"entropy":_entropy(preview),"ascii_ratio":_ascii_ratio(preview)})
            # zlib after hex
            try:
                z = zlib.decompress(dec)
                zp = z[:120].decode("utf-8","replace")
                candidates.append({"kind":"hex+zlib","ok":True,"preview":zp,"entropy":_entropy(zp),"ascii_ratio":_ascii_ratio(zp)})
            except: pass
        except: candidates.append({"kind":"hex","ok":False,"error":"Not valid hex"})
    # URL-decode
    from urllib.parse import unquote_plus
    if "%" in raw or "+" in raw:
        ud = unquote_plus(raw)
        candidates.append({"kind":"url-decode","ok":True,"preview":ud[:120],"entropy":_entropy(ud),"ascii_ratio":_ascii_ratio(ud)})
    candidates.sort(key=lambda x: x.get("ascii_ratio",0) if x.get("ok") else -1, reverse=True)
    return {"input": raw, "candidates": candidates, "best": next((c for c in candidates if c.get("ok") and c.get("kind") != "raw"), candidates[0] if candidates else None)}


# ── Test harness / fuzzer ─────────────────────────────────────────────────────
def generate_test_payload(mode: str) -> str:
    if mode == "url":
        token = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        return f"https://example.test/login?token={token}"
    if mode == "hex":
        return "".join(random.choice("0123456789ABCDEF") for _ in range(32))
    if mode == "base64":
        return base64.b64encode(os.urandom(12).replace(b"\x00",b"x")).decode()
    if mode == "gtin":
        return str(random.randint(1000000000000, 9999999999999))
    return "TEST-WORKBENCH-PAYLOAD"

def run_test_harness(target: str, profile: dict) -> dict:
    import urllib.request as ureq
    runs = int(profile.get("runs", 3))
    mode = profile.get("mode", "url")
    results = []
    for _ in range(runs):
        payload = generate_test_payload(mode)
        try:
            data = json.dumps({"raw": payload}).encode()
            req = ureq.Request(target, data=data, headers={"Content-Type":"application/json"}, method="POST")
            started = time.time()
            with ureq.urlopen(req, timeout=5) as r:
                body = r.read().decode("utf-8","replace")[:200]
                elapsed = int((time.time() - started) * 1000)
            results.append({"payload": payload, "status": r.status, "time_ms": elapsed, "body_sample": body})
        except Exception as ex:
            results.append({"payload": payload, "error": str(ex)})
        time.sleep(0.15)
    return {"target": target, "profile": {"mode": mode, "runs": runs}, "results": results}