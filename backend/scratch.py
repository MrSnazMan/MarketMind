from __future__ import annotations

from pprint import pprint
from typing import Any

import yfinance as yf


def normalize_symbol(symbol: str) -> str:
    normalized = (symbol or "").strip().upper()
    if not normalized:
        raise ValueError("Ticker symbol cannot be empty")
    return normalized


def extract_stock_metrics(info: dict[str, Any], symbol: str) -> dict[str, Any]:
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    market_cap = info.get("marketCap")
    pe_ratio = info.get("trailingPE") or info.get("forwardPE") or info.get("peRatio")

    return {
        "symbol": normalize_symbol(symbol),
        "price": price,
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
    }


def show_ticker(symbol: str) -> None:
    try:
        normalized_symbol = normalize_symbol(symbol)
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    try:
        ticker = yf.Ticker(normalized_symbol)
        info = ticker.info
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Error fetching data for {normalized_symbol}: {exc}")
        return

    print(f"\n=== {normalized_symbol} ===")
    if not info:
        print("No info returned for this ticker.")
        return

    pprint(info)

    metrics = extract_stock_metrics(info, normalized_symbol)

    print("\nSelected fields:")
    print(f"Current price: {metrics['price']}")
    print(f"Market cap: {metrics['market_cap']}")
    print(f"P/E ratio: {metrics['pe_ratio']}")


if __name__ == "__main__":
    show_ticker("AAPL")
    show_ticker("ZZZZZ")
    show_ticker("   ")
