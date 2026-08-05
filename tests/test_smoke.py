from app import app as flask_app


def test_app_imports():
    assert flask_app is not None


def test_health_endpoint():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as client:
        resp = client.get('/health')
        assert resp.status_code == 200
