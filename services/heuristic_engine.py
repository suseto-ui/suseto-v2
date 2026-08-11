# services/heuristic_engine.py
# Heuristick\u00e1 anal\u00fdza payload\u016f – detekce vzor\u016f, podez\u0159el\u00fdch struktur a scoring.

import re
from typing import Dict, Any


class HeuristicEngine:
    """Heuristick\u00fd engine pro anal\u00fdzu payload\u016f (QR/1D).

    Poskytuje:
    - základníıı anal\u00fdzu obsahu,
    - jednoduch\u00fd scoring "rizika" / "spolehlivosti",
    - detekci podez\u0159el\u00fdch vzor\u016f.
    """

    # Jednoduch\u00e9 regexy pro detekci podez\u0159el\u00fdch vzor\u016f
    SUSPICIOUS_PATTERNS = [
        r"javascript:",
        r"data:",
        r"vbscript:",
        r"file:",
        r"\.exe",  # odkazy na .exe soubory
        r"bit\.ly",  # zkracova\u010de URL (mohou skr\u00fdvat c\u00edl)
    ]

    def analyze_payload(self, payload: str) -> Dict[str, Any]:
        """Z\u00e1kladn\u00ed anal\u00fdza payloadu.

        Vrac\u00ed:
        - d\u00e9lku,
        - typ (URL, text, atd.),
        - detekovan\u00e9 vzory.
        """
        text = payload or ""
        is_url = text.startswith("http://") or text.startswith("https://")
        is_numeric = text.isdigit()
        is_alnum = text.isalnum()

        detected_patterns = []
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                detected_patterns.append(pattern)

        return {
            "payload": text,
            "length": len(text),
            "is_url": is_url,
            "is_numeric": is_numeric,
            "is_alnum": is_alnum,
            "suspicious_patterns": detected_patterns,
        }

    def score_payload(self, payload: str) -> Dict[str, Any]:
        """Jednoduch\u00fd scoring payloadu.

        Sk\u00f3rov\u00e1n\u00ed:
        - +1 za ka\u017ed\u00fd podez\u0159el\u00fd vzor,
        - +1 za velmi dlouh\u00fd payload (> 500 znak\u016f),
        - +1 za URL s nezn\u00e1mou dom\u00e9nou (z\u00e1t\u00edm jen jednoduch\u00e1 kontrola).

        Niž\u0161\u00ed sk\u00f3re = bezpe\u010dn\u011bj\u0161\u00ed, vy\u0161\u0161\u00ed = rizikov\u011bj\u0161\u00ed.
        """
        text = payload or ""
        score = 0
        reasons = []

        analysis = self.analyze_payload(text)
        if analysis["suspicious_patterns"]:
            score += len(analysis["suspicious_patterns"])
            reasons.append(f"Detekov\u00e1ny podez\u0159el\u00e9 vzory: {analysis['suspicious_patterns']}")

        if len(text) > 500:
            score += 1
            reasons.append("Velmi dlouh\u00fd payload (>500 znak\u016f)")

        if analysis["is_url"]:
            # Jednoduch\u00e1 kontrola: pokud neza\u010d\u00edn\u00e1 na https://, p\u0159idat bod
            if not text.startswith("https://"):
                score += 1
                reasons.append("URL nepouž\u00edv\u00e1 HTTPS")

        return {
            "payload": text,
            "score": score,
            "reasons": reasons,
            "risk_level": "low" if score <= 1 else "medium" if score <= 3 else "high",
        }

    def is_suspicious(self, payload: str) -> bool:
        """Rychl\u00e1 kontrola, zda payload vypad\u00e1 podez\u0159ele.

        Vrac\u00ed True, pokud je detekov\u00e1n alespo\u0148 jeden podez\u0159el\u00fd vzor.
        """
        analysis = self.analyze_payload(payload)
        return len(analysis["suspicious_patterns"]) > 0


# Glob\u00e1ln\u00ed instance pro snadn\u00e9 pou\u017eit\u00ed
heuristic_engine = HeuristicEngine()
