import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_password_policy_and_user_creation(tmp_path, monkeypatch):
    import services.auth_service as auth_service

    monkeypatch.setattr(auth_service, 'ROOT', tmp_path)
    monkeypatch.setattr(auth_service, 'FILE', tmp_path / 'users.json')

    user = auth_service.create_user('alice', 'StrongPass1', 'viewer')
    assert user['username'] == 'alice'
    assert auth_service.verify('alice', 'StrongPass1')['username'] == 'alice'

    try:
        auth_service.create_user('bob', 'weak', 'viewer')
    except ValueError as exc:
        assert 'min. 8 znaků' in str(exc)
    else:
        raise AssertionError('Weak password should be rejected')
