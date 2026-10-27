from fastapi.testclient import TestClient

from mosaic.app import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Find the fit" in response.text


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_catalogue_metadata():
    data = client.get("/api/catalogue").json()
    assert data["count"] == 48
    assert data["synthetic"] is True


def test_search():
    response = client.post("/api/search", json={"query": "headphones under $180 with ANC", "top_k": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["parser_used"] == "rules"
    assert len(data["results"]) <= 3
    assert all(x["product"]["price_usd"] <= 180 for x in data["results"])


def test_no_matches():
    response = client.post("/api/search", json={"query": "mouse under $1", "top_k": 3})
    assert response.status_code == 200
    assert response.json()["eligible_count"] == 0


def test_query_validation():
    assert client.post("/api/search", json={"query": "x"}).status_code == 422
    assert client.post("/api/search", json={"query": "headphones", "top_k": 99}).status_code == 422


def test_anthropic_requires_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    response = client.post("/api/search", json={"query": "headphones under $100", "parser": "anthropic"})
    assert response.status_code == 503
    assert "ANTHROPIC_API_KEY" in response.json()["detail"]
