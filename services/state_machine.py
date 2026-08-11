# services/state_machine.py
# Jednoduch\u00fd stavov\u00fd stroj pro \u00falohy (workbench, AIDC batchy, runy).

from typing import Dict, Any, List, Optional, Set
from datetime import datetime


class StateMachine:
    """Stavov\u00fd stroj s definovan\u00fdmi stavy a p\u0159echody.

    Defaultn\u00ed stavy:
    - created
    - running
    - paused
    - completed
    - failed
    - cancelled

    P\u0159echody jsou omezeny, aby ne\u0161lo do nep\u0159\u00edpustn\u00fdch stav\u016f.
    """

    # Definice stav\u016f
    STATES = ["created", "running", "paused", "completed", "failed", "cancelled"]

    # Povolen\u00e9 p\u0159echody: z stavu -> {event: nov\u00fd stav}
    TRANSITIONS: Dict[str, Dict[str, str]] = {
        "created": {"start": "running", "cancel": "cancelled", "fail": "failed"},
        "running": {"pause": "paused", "complete": "completed", "fail": "failed", "cancel": "cancelled"},
        "paused": {"resume": "running", "cancel": "cancelled", "fail": "failed"},
        "completed": {},  # termin\u00e1ln\u00ed stav
        "failed": {"retry": "created"},  # mo\u017enost retry z failed
        "cancelled": {},  # termin\u00e1ln\u00ed stav
    }

    def __init__(self, initial_state: str = "created"):
        if initial_state not in self.STATES:
            raise ValueError(f"Nezn\u00e1m\u00fd po\u010d\u00e1te\u010dn\u00ed stav: {initial_state}")
        self._state = initial_state
        self._history: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Any] = {}

    @property
    def state(self) -> str:
        """Aktu\u00e1ln\u00ed stav stroje."""
        return self._state

    def transition(self, event: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Provest p\u0159echod na z\u00e1klad\u011b ud\u00e1losti.

        Vrac\u00ed True, pokud byl p\u0159echod proveden, False pokud nebyl povolen.
        """
        current = self._state
        allowed = self.TRANSITIONS.get(current, {})
        if event not in allowed:
            return False

        new_state = allowed[event]
        self._state = new_state
        self._history.append({
            "from_state": current,
            "to_state": new_state,
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        })
        if metadata:
            self._metadata.update(metadata)
        return True

    def get_allowed_transitions(self, state: Optional[str] = None) -> List[str]:
        """Vr\u00e1t\u00ed seznam povolen\u00fdch ud\u00e1lost\u00ed pro dan\u00fd stav.

        Pokud state není zad\u00e1no, pou\u017eije se aktu\u00e1ln\u00ed stav.
        """
        state = state or self._state
        return list(self.TRANSITIONS.get(state, {}).keys())

    def is_terminal(self) -> bool:
        """Vrac\u00ed True, pokud je stav termin\u00e1ln\u00ed (completed/cancelled)."""
        return self._state in ("completed", "cancelled")

    def history(self) -> List[Dict[str, Any]]:
        """Vr\u00e1t\u00ed historii p\u0159echod\u016f."""
        return self._history.copy()

    def metadata(self) -> Dict[str, Any]:
        """Vr\u00e1t\u00ed metadata stroje."""
        return self._metadata.copy()

    def reset(self, new_initial_state: str = "created") -> None:
        """Resetovat stroj do po\u010d\u00e1te\u010dn\u00edho stavu."""
        if new_initial_state not in self.STATES:
            raise ValueError(f"Nezn\u00e1m\u00fd stav: {new_initial_state}")
        self._state = new_initial_state
        self._history.clear()
        self._metadata.clear()


# Helper funkce pro snadn\u00e9 vytv\u00e1\u0159en\u00ed stavov\u00fdch stroj\u016f
def create_state_machine(initial_state: str = "created") -> StateMachine:
    """Vytvoř\u00it nov\u00fd stavov\u00fd stroj."""
    return StateMachine(initial_state=initial_state)
