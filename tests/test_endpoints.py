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
    """Prazdny payload nesmi zpusobit 500."""
    r = auth_client.post("/api/v1/decode/chain", json={"payload": ""})
    assert r.status_code == 200

def test_decode_chain_invalid_b64(auth_client):
    """Neplatny base64 nesmi vratit 500."""
    r = auth_client.post("/api/v1/decode/chain", json={"payload": "YWJjZGVmZ2h"})
    assert r.status_code == 200

def test_decode_chain_url(auth_client):
    r = auth_client.post("/api/v1/decode/chain", json={"payload": "Hello%20World%21"})
    assert r.status_code == 200
    types = [c["type"] for c in json.loads(r.data)["candidates"]]
    assert "url-decode" in types

def test_decode_library(auth_client):
    r = auth_client.post("/api/v1/decode/library", json={"payloads": ["48656C6C6F", "Hello%20World"]})
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "rows" in data and "groups" in data

# --- Registry ---

def test_registry_list(client):
    r = client.get("/api/v1/registry")
    assert r.status_code == 200
    assert "items" in json.loads(r.data)

# --- Locations ---

def test_locations_requires_auth(client):
    r = client.get("/api/v1/locations")
    assert r.status_code == 401

def test_locations_list(auth_client):
    r = auth_client.get("/api/v1/locations")
    assert r.status_code == 200
    assert "locations" in json.loads(r.data)

# --- Debug ---

def test_debug_routes(auth_client):
    r = auth_client.get("/api/v1/debug/routes")
    assert r.status_code == 200
    assert "/health" in json.loads(r.data)["routes"]

# --- Dashboard ---

def test_dashboard_stats(auth_client):
    r = auth_client.get("/api/v1/dashboard/stats")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "kpis" in data and "chart" in data

# --- Admin API ---

def test_admin_users_list(auth_client):
    """Admin může získat seznam uživatelů."""
    r = auth_client.get("/api/v1/admin/users")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "users" in data

def test_admin_user_create(auth_client):
    """Admin může vytvořit nového uživatele."""
    r = auth_client.post(
        "/api/v1/admin/users",
        json={"username": "testuser", "password": "test123", "role": "viewer"}
    )
    # Může vrátit 201 (vytvořeno) nebo 400 (uživatel existuje)
    assert r.status_code in (201, 400)

def test_admin_user_role(auth_client):
    """Admin může změnit roli uživatele."""
    r = auth_client.post(
        "/api/v1/admin/users/role",
        json={"username": "admin", "role": "admin"}
    )
    # Může vrátit 200 (OK) nebo 404 (user not found)
    assert r.status_code in (200, 404)

def test_admin_user_toggle(auth_client):
    """Admin může toggle aktivaci uživatele."""
    r = auth_client.post(
        "/api/v1/admin/users/toggle",
        json={"username": "admin"}
    )
    # Může vrátit 200 (OK) nebo 404 (user not found)
    assert r.status_code in (200, 404)

def test_admin_audit(auth_client):
    """Admin může získat audit log."""
    r = auth_client.get("/api/v1/admin/audit")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "entries" in data

def test_admin_unauthorized(client):
    """Neauth uživatel nemůže přistupovat k admin API."""
    r = client.get("/api/v1/admin/users")
    assert r.status_code == 403

    r = client.post("/api/v1/admin/users", json={"username": "x", "password": "y"})
    assert r.status_code == 403
