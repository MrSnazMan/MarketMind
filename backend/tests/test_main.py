from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_root_returns_message() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "MarketMind API is running" in response.json()["message"]


def test_valid_ticker_returns_json() -> None:
    response = client.get("/api/stock/AAPL")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ticker"] == "AAPL"
    assert payload["price"] is not None
    assert payload["market_cap"] is not None
    assert payload["pe_ratio"] is not None


def test_invalid_ticker_returns_404() -> None:
    response = client.get("/api/stock/ZZZZZ")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticker 'ZZZZZ' not found"
