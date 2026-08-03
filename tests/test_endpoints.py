"""
Test endpoints pro Suseto v2.
Spusteni:
    cd /home/Suseto/suseto_v2
    python3 -m pytest tests/test_endpoints.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import pytest

from app import app as flask_app
flask_app.config["TESTING"] = True
flask_app.config["SECRET_KEY"] = "test-secret"


@pytest.fixture
def client():
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def auth_client(client):
    from services.config import CONFIG
    r = client.post(
        "/api/v1/auth/login",
        json={"username": CONFIG["ADMIN_USERNAME"], "password": CONFIG["DEFAULT_ADMIN_PASSWORD"]}
    )
    assert r.status_code == 200, f"Login failed: {r.data}"
    yield client


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
