import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    # Ensures FastAPI startup/shutdown events run (DB tables get created)
    with TestClient(app) as c:
        yield c

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_create_link_minimal(client):
    r = client.post("/api/links", json={"original_url": "https://example.com"})
    assert r.status_code == 201
    body = r.json()
    assert "short_code" in body
    assert body["original_url"].rstrip("/") == "https://example.com"