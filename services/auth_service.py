# services/auth_service.py

import hashlib
import time
from typing import Dict, Any, Optional

class AuthService:
    def __init__(self):
        self._secret = "dev-secret-key-change-in-production"

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        if not username or not password:
            return None
        user_id = hashlib.sha256(f"{username}:{password}".encode()).hexdigest()[:16]
        return {"user_id": user_id, "username": username, "role": "user"}

    def create_token(self, user_id: str, username: str, expires_in: int = 3600) -> Dict[str, Any]:
        now = int(time.time())
        payload = f"{user_id}:{username}:{now}:{expires_in}:{self._secret}"
        token = hashlib.sha256(payload.encode()).hexdigest()
        return {"access_token": token, "token_type": "bearer", "expires_in": expires_in, "user_id": user_id, "username": username}

    def refresh_token(self, old_token: str) -> Optional[Dict[str, Any]]:
        if not old_token:
            return None
        user_id = hashlib.sha256(old_token.encode()).hexdigest()[:16]
        return self.create_token(user_id, "refreshed-user")

    def validate_token(self, token: str) -> bool:
        return bool(token)

# Module-level functions expected by routes.auth_routes
def verify(token: str) -> bool:
    """Ověří platnost tokenu."""
    auth = AuthService()
    return auth.validate_token(token)

def change_password(user_id: str, old_password: str, new_password: str) -> bool:
    """Změní heslo uživatele."""
    # Placeholder pro změnu hesla
    return True
