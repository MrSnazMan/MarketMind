from __future__ import annotations

import os
from typing import Any

import yfinance as yf
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel


load_dotenv()


class StockResponse(BaseModel):
    ticker: str
    price: float | None
    market_cap: int | None
    pe_ratio: float | None
    eps: float | None
    dividend_yield: float | None


class ChatRequest(BaseModel):
    ticker: str
    question: str


class ChatResponse(BaseModel):
    answer: str


app = FastAPI(title="MarketMind API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception:  # pragma: no cover - defensive
    groq_client = None


SYSTEM_PROMPT = """You are a financial data analyst assistant embedded in a stock research app.
Your job is to help users understand a company's financial position using ONLY the
data provided in the context below — never invent, estimate, or assume values that
aren't given to you.

How to answer:
- Analyze the specific data provided (price, valuation ratios, growth, historical
  trends, etc.) and explain what it suggests, with real reasoning — not vague
generalities.
- If historical data is included, discuss actual trends (direction, magnitude,
  notable highs/lows) rather than ignoring it.
- If the data needed to answer the question isn't present in the context, say
  exactly what's missing — don't guess, and don't pad the answer with unrelated
data just to seem responsive.
- Be specific and quantitative wherever the data allows it (e.g. "a P/E of 30 is
  above the sector norm" rather than "the P/E is high").

Boundaries:
- Do not tell the user to buy, sell, or hold. Analysis and explanation are your
  job; the decision is theirs.
- Do not add a "consult a financial advisor" disclaimer more than once, and only
  if the question is genuinely asking for a recommendation rather than an
  explanation.
- Do not hedge excessively. If the data supports a clear observation, state it
  plainly.

Keep answers concise — a few sentences to a short paragraph, not an essay, unless
the question specifically calls for a longer breakdown."""


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
        "eps": eps,
        "pe_ratio": pe_ratio,
        "dividend_yield": dividend_yield,
    }


def get_stock_metrics(ticker: str) -> dict[str, Any]:
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

    return metrics


def get_history_summary(ticker: str) -> dict[str, Any] | None:
    try:
        symbol = normalize_symbol(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        history = yf.Ticker(symbol).history(period="2y", interval="1d")
    except Exception:
        return None

    if history.empty:
        return None

    closes = history["Close"].dropna()
    if closes.empty:
        return None

    latest_close = float(closes.iloc[-1])

    def compute_change(start_index: int) -> float | None:
        if start_index >= len(closes):
            return None
        start_close = float(closes.iloc[start_index])
        if start_close == 0:
            return None
        return ((latest_close - start_close) / start_close) * 100

    change_30d_pct = compute_change(max(len(closes) - 30, 0))
    change_90d_pct = compute_change(max(len(closes) - 90, 0))
    change_1y_pct = compute_change(max(len(closes) - 252, 0))

    low = float(history["Low"].min())
    high = float(history["High"].max())

    if change_1y_pct is None:
        trend = "unknown"
    elif change_1y_pct > 5:
        trend = "up"
    elif change_1y_pct < -5:
        trend = "down"
    else:
        trend = "flat"

    return {
        "change_30d_pct": change_30d_pct,
        "change_90d_pct": change_90d_pct,
        "change_1y_pct": change_1y_pct,
        "range": {"low": low, "high": high},
        "trend": trend,
    }


def build_chat_prompt(
    metrics: dict[str, Any],
    question: str,
    history_summary: dict[str, Any] | None = None,
) -> str:
    context_lines = [f"{key}: {value}" for key, value in metrics.items() if value is not None]
    context = "\n".join(context_lines)

    history_block = ""
    if history_summary:
        change_30d = history_summary.get("change_30d_pct")
        change_90d = history_summary.get("change_90d_pct")
        change_1y = history_summary.get("change_1y_pct")
        range_data = history_summary.get("range") or {}
        low = range_data.get("low")
        high = range_data.get("high")
        trend = history_summary.get("trend", "unknown")

        history_parts: list[str] = []
        if change_30d is not None:
            history_parts.append(f"last 30 days: {change_30d:+.2f}%")
        if change_90d is not None:
            history_parts.append(f"last 90 days: {change_90d:+.2f}%")
        if change_1y is not None:
            history_parts.append(f"last 1 year: {change_1y:+.2f}%")
        if low is not None and high is not None:
            history_parts.append(f"52-week range: ${low:.2f} - ${high:.2f}")
        if trend:
            history_parts.append(f"overall trend: {trend}")

        if history_parts:
            history_block = "\nHistorical performance summary:\n" f"Recent performance: {'; '.join(history_parts)}."

    return (
        "You are a financial assistant. Use the provided stock data as factual context and answer the user's question. "
        "Do not invent missing values.\n\n"
        f"Stock data:\n{context}{history_block}\n\nUser question: {question}\n\nAnswer clearly and concisely."
    )


def build_fallback_answer(metrics: dict[str, Any], question: str) -> str:
    ticker = metrics.get("ticker", "the stock")
    price = metrics.get("price")
    market_cap = metrics.get("market_cap")
    pe_ratio = metrics.get("pe_ratio")
    eps = metrics.get("eps")

    parts = [f"{ticker} current price is {price}."] if price is not None else [f"I can summarize {ticker} using the available stock data."]

    if market_cap is not None:
        parts.append(f"Market capitalization is {market_cap}.")
    if pe_ratio is not None:
        parts.append(f"The trailing P/E ratio is {pe_ratio}.")
    if eps is not None:
        parts.append(f"EPS is {eps}.")

    if not parts:
        return f"I couldn't retrieve enough data for {ticker} right now."

    return " ".join(parts) + " This is a fallback answer because the AI service is unavailable."


def get_chat_answer(prompt: str) -> str:
    if groq_client is None:
        raise RuntimeError("GROQ_API_KEY is not configured")

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    choices = getattr(response, "choices", None) or []
    if not choices:
        return ""

    message = getattr(choices[0], "message", None)
    if message is None:
        return ""

    return getattr(message, "content", None) or ""


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "MarketMind API is running. Visit /docs for API docs or /api/stock/{ticker} for stock data."
    }


@app.get("/api/stock/{ticker}", response_model=StockResponse)
def get_stock(ticker: str) -> StockResponse:
    return StockResponse(**get_stock_metrics(ticker))


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    metrics = get_stock_metrics(request.ticker)
    history_summary = get_history_summary(request.ticker)
    prompt = build_chat_prompt(metrics, request.question, history_summary=history_summary)

    try:
        answer = get_chat_answer(prompt)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Groq chat error: {exc}")
        answer = build_fallback_answer(metrics, request.question)

    if not answer.strip():
        answer = build_fallback_answer(metrics, request.question)

    return ChatResponse(answer=answer)
