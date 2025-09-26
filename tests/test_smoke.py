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

def test_list_links(client):
    # ensure at least one exists
    client.post("/api/links", json={"original_url": "https://example.com"})
    r = client.get("/api/links")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "short_code" in data[0]

def test_read_link_by_code(client):
    r = client.post("/api/links", json={"original_url": "https://example.com"})
    code = r.json()["short_code"]

    r2 = client.get(f"/api/links/{code}")
    assert r2.status_code == 200
    assert r2.json()["short_code"] == code

def test_read_link_not_found(client):
    r = client.get("/api/links/__nope__")
    assert r.status_code == 404