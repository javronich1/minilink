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

def test_update_link_url(client):
    # create
    r = client.post("/api/links", json={"original_url": "https://example.com"})
    code = r.json()["short_code"]
    # update URL
    r2 = client.patch(f"/api/links/{code}", json={"original_url": "https://example.org"})
    assert r2.status_code == 200
    assert r2.json()["original_url"].rstrip("/") == "https://example.org"

def test_update_link_custom_code_conflict(client):
    # create two links
    r1 = client.post("/api/links", json={"original_url": "https://a.com"})
    code1 = r1.json()["short_code"]
    r2 = client.post("/api/links", json={"original_url": "https://b.com"})
    code2 = r2.json()["short_code"]
    # try to rename code1 to existing code2
    r3 = client.patch(f"/api/links/{code1}", json={"custom_code": code2})
    assert r3.status_code == 409

def test_update_link_not_found(client):
    r = client.patch("/api/links/__nope__", json={"original_url": "https://x.com"})
    assert r.status_code == 404

def test_delete_link(client):
    # create
    r = client.post("/api/links", json={"original_url": "https://to-delete.com"})
    code = r.json()["short_code"]

    # delete
    r2 = client.delete(f"/api/links/{code}")
    assert r2.status_code == 204

    # verify it's gone
    r3 = client.get(f"/api/links/{code}")
    assert r3.status_code == 404

def test_delete_link_not_found(client):
    r = client.delete("/api/links/__nope__")
    assert r.status_code == 404

def test_redirect_and_analytics(client):
    # create a link
    r = client.post("/api/links", json={"original_url": "https://example.org"})
    assert r.status_code == 201
    code = r.json()["short_code"]

    # hit redirect (don't follow it)
    r2 = client.get(f"/r/{code}", allow_redirects=False)
    assert r2.status_code == 307
    assert r2.headers["location"].rstrip("/") == "https://example.org"

    # verify analytics updated via read endpoint
    r3 = client.get(f"/api/links/{code}")
    assert r3.status_code == 200
    body = r3.json()
    assert body["click_count"] >= 1
    assert body["last_accessed"] is not None