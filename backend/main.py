from __future__ import annotations

from typing import Any

import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class StockResponse(BaseModel):
    ticker: str
    price: float | None
    market_cap: int | None
    pe_ratio: float | None
    eps: float | None
    dividend_yield: float | None


app = FastAPI(title="MarketMind API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_symbol(symbol: str) -> str:
    normalized = (symbol or "").strip().upper()
    if not normalized:
        raise ValueError("Ticker symbol cannot be empty")
    return normalized


def extract_stock_metrics(info: dict[str, Any], symbol: str) -> dict[str, Any]:
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    market_cap = info.get("marketCap")
    pe_ratio = info.get("trailingPE") or info.get("forwardPE") or info.get("peRatio")
    eps = info.get("epsTrailingTwelveMonths") or info.get("epsCurrentYear") or info.get("forwardEps")
    dividend_yield = info.get("dividendYield")

    return {
        "ticker": normalize_symbol(symbol),
        "price": price,
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "eps": eps,
        "dividend_yield": dividend_yield,
    }


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "MarketMind API is running. Visit /docs for API docs or /api/stock/{ticker} for stock data."
    }


@app.get("/api/stock/{ticker}", response_model=StockResponse)
def get_stock(ticker: str) -> StockResponse:
    try:
        symbol = normalize_symbol(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        quote = yf.Ticker(symbol)
        info = quote.info
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=502, detail="Unable to fetch stock data") from exc

    metrics = extract_stock_metrics(info, symbol)
    if metrics["price"] is None:
        raise HTTPException(status_code=404, detail=f"Ticker '{symbol}' not found")

    return StockResponse(**metrics)
