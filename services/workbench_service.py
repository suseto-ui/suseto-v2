# services/workbench_service.py
# Data & Identifier Analysis Workbench – core logic
import base64
import binascii
import hashlib
import json
import random
import string
import time
import zlib
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Ingest & Normalization
# ---------------------------------------------------------------------------

def _classify(raw: str) -> str:
    s = raw.strip()
    if s.startswith(("http://", "https://")):
        return "url"
    if s.startswith("data:"):
        return "data_uri"
    if all(c in "0123456789ABCDEFabcdef" for c in s) and len(s) >= 8 and len(s) % 2 == 0:
        return "hex"
    # MAC address
    if s.count(":") == 5 and all(len(p) == 2 for p in s.split(":")):
        return "mac"
    # IMEI – 15 digits
    if s.isdigit() and len(s) == 15:
        return "imei"
    # EAN-13 / EAN-8
    if s.isdigit() and len(s) in (8, 13):
        return "ean"
    # UUID / GUID
    import re
    if re.fullmatch(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', s):
        return "uuid"
    # JWT
    parts = s.split(".")
    if len(parts) == 3 and all(p.replace("-", "+").replace("_", "/") for p in parts):
        try:
            base64.b64decode(parts[0] + "==")
            base64.b64decode(parts[1] + "==")
            return "jwt"
        except Exception:
            pass
    # Base64 heuristic (length divisible by 4, only valid chars)
    b64_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
    if len(s) % 4 == 0 and all(c in b64_chars for c in s) and len(s) >= 8:
        return "base64"
    # JSON
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        try:
            json.loads(s)
            return "json"
        except Exception:
            pass
    return "unknown"


def _normalize(raw: str, id_type: str) -> str:
    s = raw.strip()
    if id_type == "hex":
        return s.upper()
    if id_type == "mac":
        return s.upper()
    if id_type == "url":
        return s
    return s


def ingest_identifier(raw: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and type an arbitrary raw identifier."""
    id_type = _classify(raw)
    normalized = _normalize(raw, id_type)
    attributes: Dict[str, Any] = dict(meta)
    warnings: List[str] = []

    if id_type == "url":
        from urllib.parse import urlparse, parse_qs
        u = urlparse(normalized)
        attributes["scheme"] = u.scheme
        attributes["host"] = u.netloc
        attributes["path"] = u.path
        attributes["params"] = parse_qs(u.query)

    elif id_type == "hex":
        attributes["length_bytes"] = len(normalized) // 2
        attributes["sha256"] = hashlib.sha256(bytes.fromhex(normalized)).hexdigest()

    elif id_type == "ean":
        digits = [int(c) for c in normalized]
        # EAN check digit validation
        if len(digits) == 13:
            total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
            expected = (10 - (total % 10)) % 10
            attributes["check_digit_valid"] = digits[-1] == expected
        elif len(digits) == 8:
            total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(digits[:7]))
            expected = (10 - (total % 10)) % 10
            attributes["check_digit_valid"] = digits[-1] == expected

    elif id_type == "imei":
        # Luhn algorithm
        d = [int(c) for c in normalized]
        total = 0
        for i, n in enumerate(reversed(d)):
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        attributes["luhn_valid"] = (total % 10) == 0

    elif id_type == "jwt":
        parts = normalized.split(".")
        try:
            header = json.loads(base64.b64decode(parts[0] + "==").decode("utf-8", errors="replace"))
            payload_decoded = json.loads(base64.b64decode(parts[1] + "==").decode("utf-8", errors="replace"))
            attributes["header"] = header
            attributes["payload_claims"] = payload_decoded
            if "exp" in payload_decoded:
                import datetime
                exp_dt = datetime.datetime.utcfromtimestamp(payload_decoded["exp"]).isoformat()
                attributes["expires"] = exp_dt
                if payload_decoded["exp"] < time.time():
                    warnings.append("JWT je expirován.")
        except Exception as e:
            warnings.append(f"JWT decode error: {e}")

    elif id_type == "base64":
        try:
            decoded = base64.b64decode(normalized + "==")
            attributes["decoded_hex"] = decoded.hex()
            attributes["decoded_length"] = len(decoded)
        except Exception:
            warnings.append("base64 decode selhal.")

    elif id_type == "json":
        try:
            obj = json.loads(normalized)
            attributes["keys"] = list(obj.keys()) if isinstance(obj, dict) else []
            attributes["json_type"] = type(obj).__name__
        except Exception:
            pass

    return {
        "raw": raw,
        "type": id_type,
        "normalized": normalized,
        "attributes": attributes,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Analysis Pipeline
# ---------------------------------------------------------------------------

def run_analysis_pipeline(identifier: Dict[str, Any]) -> Dict[str, Any]:
    """Run risk/enrichment analysis on an already-ingested identifier dict."""
    if not identifier.get("type") or identifier["type"] == "unknown":
        enriched = ingest_identifier(identifier.get("raw", ""), identifier.get("attributes", {}))
    else:
        enriched = dict(identifier)

    risk_score = 0
    notes: List[str] = []

    id_type = enriched.get("type", "unknown")
    attrs = enriched.get("attributes", {})

    if id_type == "url":
        path = attrs.get("path", "")
        params = attrs.get("params", {})
        if any(kw in path.lower() for kw in ("login", "auth", "token", "password", "reset", "admin")):
            risk_score += 25
            notes.append("URL obsahuje citlivé klíčové slovo v cestě.")
        if len(params) > 5:
            risk_score += 10
            notes.append(f"URL obsahuje {len(params)} parametrů – potenciální data exfiltrace.")
        if attrs.get("scheme") == "http":
            risk_score += 15
            notes.append("Nezabezpečené HTTP schéma.")

    elif id_type == "jwt":
        claims = attrs.get("payload_claims", {})
        if "exp" not in claims:
            risk_score += 20
            notes.append("JWT nemá expiraci (chybí 'exp' claim).")
        header = attrs.get("header", {})
        if header.get("alg", "").upper() in ("NONE", ""):
            risk_score += 50
            notes.append("JWT algoritmus je 'none' – kritická zranitelnost.")
        if "HS256" == header.get("alg", ""):
            notes.append("JWT používá HS256 – symetrický podpis, bezpečný pokud je tajemství silné.")

    elif id_type == "ean":
        if attrs.get("check_digit_valid") is False:
            risk_score += 30
            notes.append("EAN check digit neplatný – pravděpodobně poškozený nebo falzifikát.")
        else:
            notes.append("EAN check digit OK.")

    elif id_type == "imei":
        if attrs.get("luhn_valid") is False:
            risk_score += 40
            notes.append("IMEI Luhn check selhal – neplatné IMEI.")
        else:
            notes.append("IMEI Luhn check OK.")

    elif id_type == "hex":
        length = attrs.get("length_bytes", 0)
        if length in (16, 32):
            notes.append(f"HEX délka {length} bajtů odpovídá MD5 nebo SHA-256 hash.")

    elif id_type == "base64":
        if not attrs.get("decoded_hex"):
            risk_score += 10
            notes.append("base64 dekódování selhalo.")
        else:
            notes.append("base64 úspěšně dekódován.")

    if risk_score == 0 and not notes:
        notes.append("Žádné rizikové faktory nebyly detekovány.")

    return {
        "identifier": enriched,
        "risk_score": min(risk_score, 100),
        "risk_level": "critical" if risk_score >= 70 else "high" if risk_score >= 40 else "medium" if risk_score >= 20 else "low",
        "notes": notes,
    }


# ---------------------------------------------------------------------------
# Reverse Engineering Engine
# ---------------------------------------------------------------------------

def _try_base64(raw: str) -> Dict[str, Any]:
    try:
        decoded = base64.b64decode(raw + "===")
        return {"ok": True, "method": "base64", "decoded_hex": decoded.hex(),
                "decoded_text": decoded.decode("utf-8", errors="replace"), "length": len(decoded)}
    except Exception:
        return {"ok": False, "method": "base64"}


def _try_zlib(data: bytes) -> Dict[str, Any]:
    try:
        out = zlib.decompress(data)
        return {"ok": True, "method": "zlib", "decoded_text": out.decode("utf-8", errors="replace"), "length": len(out)}
    except Exception:
        return {"ok": False, "method": "zlib"}


def _try_hex_decode(raw: str) -> Dict[str, Any]:
    try:
        data = bytes.fromhex(raw)
        text = data.decode("utf-8", errors="replace")
        return {"ok": True, "method": "hex_to_ascii", "decoded_text": text, "length": len(data)}
    except Exception:
        return {"ok": False, "method": "hex_to_ascii"}


def _try_url_decode(raw: str) -> Dict[str, Any]:
    from urllib.parse import unquote
    decoded = unquote(raw)
    if decoded != raw:
        return {"ok": True, "method": "url_decode", "decoded_text": decoded}
    return {"ok": False, "method": "url_decode"}


def _detect_encoding_layers(raw: str) -> List[str]:
    layers = []
    s = raw.strip()
    # Layer detection heuristics
    if all(c in "0123456789ABCDEFabcdef" for c in s) and len(s) % 2 == 0:
        layers.append("hex")
    b64ok = True
    try:
        base64.b64decode(s + "===")
    except Exception:
        b64ok = False
    if b64ok and len(s) % 4 <= 2:
        layers.append("base64")
    if "%" in s:
        layers.append("url_encoded")
    if s.startswith("{") or s.startswith("["):
        layers.append("json")
    if not layers:
        layers.append("plaintext")
    return layers


def run_reverse_engineering(raw: str) -> Dict[str, Any]:
    candidates = []
    layers = _detect_encoding_layers(raw)

    b64_result = _try_base64(raw)
    candidates.append(b64_result)
    if b64_result["ok"]:
        # Try zlib on base64-decoded bytes
        try:
            inner = bytes.fromhex(b64_result["decoded_hex"])
            z = _try_zlib(inner)
            candidates.append(z)
        except Exception:
            pass

    hex_result = _try_hex_decode(raw)
    candidates.append(hex_result)
    if hex_result["ok"]:
        try:
            inner = bytes.fromhex(raw)
            z = _try_zlib(inner)
            candidates.append(z)
        except Exception:
            pass

    url_result = _try_url_decode(raw)
    candidates.append(url_result)

    # Shannon entropy
    if raw:
        from collections import Counter
        import math
        freq = Counter(raw)
        entropy = -sum((c / len(raw)) * math.log2(c / len(raw)) for c in freq.values())
    else:
        entropy = 0.0

    return {
        "input": raw,
        "detected_layers": layers,
        "entropy": round(entropy, 3),
        "candidates": [c for c in candidates if c["ok"]],
        "all_attempts": candidates,
    }


# ---------------------------------------------------------------------------
# Test Harness
# ---------------------------------------------------------------------------

def _generate_payload(mode: str) -> str:
    if mode == "url":
        token = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        return f"https://example.com/scan?id={token}"
    if mode == "hex":
        return "".join(random.choice("0123456789ABCDEF") for _ in range(32))
    if mode == "ean13":
        digits = [random.randint(0, 9) for _ in range(12)]
        total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
        check = (10 - (total % 10)) % 10
        return "".join(str(d) for d in digits) + str(check)
    if mode == "base64":
        data = "".join(random.choice(string.printable[:62]) for _ in range(12))
        return base64.b64encode(data.encode()).decode()
    return f"TESTPAYLOAD-{random.randint(1000, 9999)}"


def run_test_harness(target: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    """Send synthetic test payloads to a target endpoint and collect results."""
    runs = min(int(profile.get("runs", 5)), 20)
    mode = profile.get("mode", "url")
    results: List[Dict[str, Any]] = []

    try:
        import requests as req_lib
        timeout = int(profile.get("timeout", 5))
        for _ in range(runs):
            payload = _generate_payload(mode)
            t0 = time.time()
            try:
                resp = req_lib.post(target, json={"payload": payload}, timeout=timeout)
                elapsed = int((time.time() - t0) * 1000)
                results.append({
                    "payload": payload,
                    "status": resp.status_code,
                    "time_ms": elapsed,
                    "body_sample": resp.text[:300],
                    "ok": resp.status_code < 400,
                })
            except Exception as e:
                results.append({"payload": payload, "error": str(e), "ok": False})
            time.sleep(0.1)
    except ImportError:
        return {
            "target": target,
            "profile": profile,
            "error": "Balíček 'requests' není nainstalován. Spusť instalaci přes Debug > Instalovat závislosti.",
            "results": [],
        }

    passed = sum(1 for r in results if r.get("ok"))
    return {
        "target": target,
        "profile": profile,
        "total": runs,
        "passed": passed,
        "failed": runs - passed,
        "results": results,
    }
