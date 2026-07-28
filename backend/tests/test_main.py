import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


class MainApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_root_returns_message(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("MarketMind API is running", response.json()["message"])

    def test_valid_ticker_returns_json(self) -> None:
        response = self.client.get("/api/stock/AAPL")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["ticker"], "AAPL")
        self.assertIsNotNone(payload["price"])
        self.assertIsNotNone(payload["market_cap"])
        self.assertIsNotNone(payload["pe_ratio"])

    def test_invalid_ticker_returns_404(self) -> None:
        response = self.client.get("/api/stock/ZZZZZ")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Ticker 'ZZZZZ' not found")

    def test_chat_returns_answer(self) -> None:
        class FakeMessage:
            content = "AAPL's P/E is high because the current price is elevated relative to trailing earnings."

        class FakeChoice:
            message = FakeMessage()

        class FakeResponse:
            choices = [FakeChoice()]

        class FakeCompletions:
            def create(self, **kwargs):
                return FakeResponse()

        class FakeChat:
            def __init__(self) -> None:
                self.completions = FakeCompletions()

        class FakeClient:
            def __init__(self) -> None:
                self.chat = FakeChat()

        with patch("main.groq_client", FakeClient()):
            response = self.client.post(
                "/api/chat",
                json={"ticker": "AAPL", "question": "why is the P/E high?"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["answer"].startswith("AAPL"))

    def test_chat_falls_back_when_groq_fails(self) -> None:
        class FakeCompletions:
            def create(self, **kwargs):
                raise RuntimeError("429 quota exceeded")

        class FakeChat:
            def __init__(self) -> None:
                self.completions = FakeCompletions()

        class FakeClient:
            def __init__(self) -> None:
                self.chat = FakeChat()

        with patch("main.groq_client", FakeClient()):
            response = self.client.post(
                "/api/chat",
                json={"ticker": "AAPL", "question": "what is the price?"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("AAPL", response.json()["answer"])
        self.assertIn("price", response.json()["answer"].lower())

    def test_build_chat_prompt_includes_historical_summary(self) -> None:
        from main import build_chat_prompt

        prompt = build_chat_prompt(
            {"ticker": "AAPL", "price": 200.0},
            "should I consider buying?",
            history_summary={
                "change_30d_pct": 4.2,
                "change_90d_pct": 12.5,
                "change_1y_pct": 18.7,
                "range": {"low": 150.0, "high": 220.0},
                "trend": "up",
            },
        )

        self.assertIn("Historical performance summary", prompt)
        self.assertIn("last 30 days", prompt)
        self.assertIn("last 90 days", prompt)
        self.assertIn("52-week range", prompt)


if __name__ == "__main__":
    unittest.main()
