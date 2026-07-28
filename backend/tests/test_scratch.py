import unittest

from scratch import extract_stock_metrics, normalize_symbol


class ScratchHelpersTests(unittest.TestCase):
    def test_extracts_metrics_from_info(self) -> None:
        info = {
            "symbol": "AAPL",
            "currentPrice": 123.45,
            "marketCap": 999999999,
            "trailingPE": 12.3,
        }

        result = extract_stock_metrics(info, "AAPL")

        self.assertEqual(result["price"], 123.45)
        self.assertEqual(result["market_cap"], 999999999)
        self.assertEqual(result["pe_ratio"], 12.3)

    def test_missing_fields_become_none(self) -> None:
        result = extract_stock_metrics({"symbol": "AAPL"}, "AAPL")

        self.assertIsNone(result["price"])
        self.assertIsNone(result["market_cap"])
        self.assertIsNone(result["pe_ratio"])

    def test_normalize_symbol_uppercases_and_strips(self) -> None:
        self.assertEqual(normalize_symbol(" aapl "), "AAPL")

    def test_empty_symbol_raises(self) -> None:
        with self.assertRaises(ValueError):
            normalize_symbol("   ")


if __name__ == "__main__":
    unittest.main()
