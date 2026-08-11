# services/auth_lab.py
# Pomocné funkce a "lab" pro testování autentikace.

from typing import Dict, Any, Optional

from .auth_service import AuthService


class AuthLab:
    """Laboratorní nástroje pro práci s AuthService.

    Umožňuje rychle ověřit autentikaci, generování tokenů a jejich validaci.
    """

    def __init__(self):
        self._auth = AuthService()

    def try_login(self, username: str, password: str) -> Dict[str, Any]:
        """Vyzkouší přihlášení a případně vrátí token."""
        user = self._auth.authenticate(username, password)
        if not user:
            return {"success": False, "error": "Invalid credentials", "token": None}
        token = self._auth.create_token(user["user_id"], user["username"])
        return {"success": True, "user": user, "token": token}

    def validate(self, token: str) -> Dict[str, Any]:
        """Zkontroluje, zda token vypadá platně."""
        is_valid = self._auth.validate_token(token)
        return {"token": token, "valid": is_valid}

    def refresh(self, token: str) -> Dict[str, Any]:
        """Vyzkouší refresh tokenu."""
        new_token = self._auth.refresh_token(token)
        if not new_token:
            return {"success": False, "error": "Cannot refresh token", "token": None}
        return {"success": True, "token": new_token}


# Globální instance pro snadné použití
auth_lab = AuthLab()
