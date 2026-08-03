"""Test endpoints pro Suseto v2.

Spusteni:
    cd /home/Suseto/suseto_v2
    python3 -m pytest tests/test_endpoints.py -v
"""

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app

flask_app.config["TESTING"] = True
flask_app.config["SECRET_KEY"] = "test-secret"


@pytest.fixture
def client():
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def auth_client(client):
    """Vytvoří přihlášeného admina přes session."""
    with client.session_transaction() as sess:
        sess["username"] = "admin"
        sess["role"] = "admin"
    return client


# --- Health / Ping ---

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert json.loads(r.data)["status"] == "ok"


def test_ping(client):
    r = client.post("/api/v1/debug/ping", json={"hello": "world"})
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["ok"] is True
    assert data["received"]["hello"] == "world"


# --- Auth ---

def test_auth_me_unauthenticated(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert json.loads(r.data)["user"] is None


def test_auth_me_authenticated(auth_client):
    r = auth_client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert json.loads(r.data)["user"] is not None


def test_login_invalid(client):
    r = client.post("/api/v1/auth/login", json={"username": "nobody", "password": "wrong"})
    assert r.status_code == 401


def test_logout(auth_client):
    r = auth_client.post("/api/v1/auth/logout")
    assert r.status_code == 200
    assert json.loads(r.data)["ok"] is True


# --- Decode chain ---

def test_decode_chain_requires_auth(client):
    r = client.post("/api/v1/decode/chain", json={"payload": "48656C6C6F"})
    assert r.status_code == 401


def test_decode_chain_hex(auth_client):
    r = auth_client.post("/api/v1/decode/chain", json={"payload": "48656C6C6F2053555345544F"})
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "candidates" in data
    assert data["best"] is not None


def test_decode_chain_empty(auth_client):
    r = auth_client.post("/api/v1/decode/chain", json={"payload": ""})
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "candidates" in data


def test_decode_chain_invalid_b64(auth_client):
    r = auth_client.post("/api/v1/decode/chain", json={"payload": "%%%invalid%%%"})
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "candidates" in data


def test_decode_chain_url(auth_client):
    r = auth_client.post("/api/v1/decode/chain", json={"payload": "https://example.com/item/123"})
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "candidates" in data


def test_decode_library(auth_client):
    r = auth_client.post("/api/v1/decode/library", json={"payloads": ["123", "abc"]})
    assert r.status_code == 200
    data = json.loads(r.data)

    assert "rows" in data
    assert "groups" in data
    assert isinstance(data["rows"], list)
    assert isinstance(data["groups"], list)
    assert len(data["rows"]) == 2

    first = data["rows"][0]
    assert "payload" in first
    assert "best_type" in first
    assert "best_confidence" in first


# --- Registry / Inventory ---

def test_registry_list(auth_client):
    r = auth_client.get("/api/v1/registry")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "items" in data
    assert "profiles" in data


def test_registry_sessions_list(auth_client):
    r = auth_client.get("/api/v1/inventory/sessions")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "sessions" in data


def test_registry_session_create(auth_client):
    r = auth_client.post("/api/v1/inventory/sessions", json={"name": "Test Session"})
    assert r.status_code in (200, 201)
    data = json.loads(r.data)
    assert "id" in data or "name" in data


def test_registry_backup_endpoint(auth_client):
    r = auth_client.get("/api/v1/backup")
    assert r.status_code == 200
    assert "application/zip" in r.content_type


def test_restore_endpoint_missing(auth_client):
    r = auth_client.post("/api/v1/restore")
    assert r.status_code == 404


# --- Locations ---

def test_locations_requires_auth(client):
    r = client.get("/api/v1/locations")
    assert r.status_code == 401


def test_locations_list(auth_client):
    r = auth_client.get("/api/v1/locations")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "locations" in data


# --- Debug ---

def test_debug_routes(auth_client):
    r = auth_client.get("/api/v1/debug/routes")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "routes" in data
    assert len(data["routes"]) > 0


# --- Dashboard ---

def test_dashboard_stats(auth_client):
    r = auth_client.get("/api/v1/dashboard/stats")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "kpis" in data
    assert "chart" in data
    assert "recent" in data


# --- Admin API ---

def test_admin_users_list(auth_client):
    r = auth_client.get("/api/v1/admin/users")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "users" in data


def test_admin_user_create(auth_client):
    r = auth_client.post(
        "/api/v1/admin/users",
        json={"username": "testuser", "password": "test123", "role": "viewer"}
    )
    assert r.status_code in (201, 400)


def test_admin_user_role(auth_client):
    r = auth_client.post(
        "/api/v1/admin/users/role",
        json={"username": "admin", "role": "admin"}
    )
    assert r.status_code in (200, 404)


def test_admin_user_toggle(auth_client):
    r = auth_client.post(
        "/api/v1/admin/users/toggle",
        json={"username": "admin"}
    )
    assert r.status_code in (200, 404)


def test_admin_audit(auth_client):
    r = auth_client.get("/api/v1/admin/audit")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "entries" in data


def test_admin_unauthorized(client):
    r = client.get("/api/v1/admin/users")
    assert r.status_code == 403

    r = client.post("/api/v1/admin/users", json={"username": "x", "password": "y"})
    assert r.status_code == 403