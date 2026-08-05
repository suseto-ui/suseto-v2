import pytest

from app import app as flask_app


@pytest.fixture()
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'ok'


def test_auth_me(client):
    resp = client.get('/api/v1/auth/me')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'user' in data


def test_debug_routes(client):
    resp = client.get('/api/v1/debug/routes')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'routes' in data
