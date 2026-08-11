# services/decision_engine.py
# Rozhodovací··engine pro payloady – využívá··heuristiky a scoring.

from typing import Dict, Any, Optional

from .heuristic_engine import heuristic_engine


class DecisionEngine:
    """Engine pro rozhodov\u00e1n\u00ed o zpracov\u00e1n\u00ed payload\u016f.

    Na z\u00e1klad\u011b heuristick\u00e9 anal\u00fdzy a scoringu rozhoduje:
    - zda payload pokra\u010dovat do dal\u0161\u00edho zpracov\u00e1n\u00ed,
    - zda je t\u0159eba upozornit u\u017eivatele,
    - zda payload zam\u00edtnout.
    """

    def evaluate(self, payload: str) -> Dict[str, Any]:
        """Vyhodnot\u00ed payload a vr\u00e1t\u00ed rozhodnut\u00ed.

        Vrac\u00ed dict s:
        - 'decision': 'allow' / 'warn' / 'reject'
        - 'reason': textov\u00e9 vysv\u011btlen\u00ed
        - 'score_data': data z heuristic engine
        """
        score_data = heuristic_engine.score_payload(payload)
        score = score_data["score"]
        risk_level = score_data["risk_level"]

        if risk_level == "high" or score >= 4:
            decision = "reject"
            reason = "Payload je ozna\u010den jako vysoce rizikov\u00fd"
        elif risk_level == "medium" or score >= 2:
            decision = "warn"
            reason = "Payload st\u0159edn\u00edho rizika – doporu\u010deno opatrnost"
        else:
            decision = "allow"
            reason = "Payload je bezpe\u010dn\u00fd pro dal\u0161\u00ed zpracov\u00e1n\u00ed"

        return {
            "decision": decision,
            "reason": reason,
            "score_data": score_data,
        }

    def should_process(self, payload: str) -> bool:
        """Rychl\u00e1 kontrola, zda payload zpracovat.

        Vrac\u00ed True pro 'allow' a 'warn', False pro 'reject'.
        """
        result = self.evaluate(payload)
        return result["decision"] != "reject"


# Glob\u00e1ln\u00ed instance pro snadn\u00e9 pou\u017eit\u00ed
decision_engine = DecisionEngine()
