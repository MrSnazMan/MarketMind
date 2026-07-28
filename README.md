# MarketMind

MarketMind is a stock research app that combines real market data with an AI assistant. The current backend can look up a stock, return core financial metrics from yfinance, and answer questions with context from both current fundamentals and recent price history.

## Current status
MarketMind is in active development. The backend API is now functional and tested. The frontend currently contains a Vite starter shell and is not yet fully wired to the API.

## What the app can do now
- Fetch real stock metadata for a ticker using yfinance
- Return current metrics such as price, market capitalization, P/E, EPS, and dividend yield
- Validate ticker input and return a clear 404-style error for unknown tickers
- Answer chat questions with a Groq-backed assistant using:
  - current stock metrics
  - recent price-history context (30-day, 90-day, and 1-year changes)
  - a 52-week high/low range and overall trend summary
- Expose the functionality through FastAPI endpoints

## Tech stack
- Backend: FastAPI (Python)
- Frontend: React + TypeScript (Vite)
- Financial data: yfinance
- AI: Groq API

## Project structure
- backend/: FastAPI app, stock/chat routes, tests, and environment config
- frontend/: Vite + React frontend scaffold
- README.md: project overview and setup instructions
- CHANGELOG.md: release notes and notable changes

## Local setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- A Groq API key from [Groq Console](https://console.groq.com/)

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Create a `.env` file in the backend folder using the values from `.env.example`, including:

```env
GROQ_API_KEY=your-key-here
```

Then start the API:

```bash
uvicorn main:app --reload
```

The API will be available at:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```

The frontend dev server will usually run at:
- http://localhost:5173

## API endpoints

### Stock data
- GET /api/stock/{ticker}
- Example: http://127.0.0.1:8000/api/stock/AAPL

### Chat
- POST /api/chat
- Example body:

```json
{
  "ticker": "AAPL",
  "question": "why is the P/E high?"
}
```

## Testing

### Backend tests
Run the backend test suite from the project root or the backend folder:

```bash
cd backend
pytest -q
```

Current verification status:
- 10 tests passing
- 1 warning from FastAPI test client dependencies

### Manual API checks
Start the backend, then try the following:

1. Open the Swagger UI:
   - http://127.0.0.1:8000/docs

2. Check the stock endpoint directly:
   - http://127.0.0.1:8000/api/stock/AAPL

3. Test the chat endpoint with curl:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL","question":"why is the P/E high?"}'
```

## Known limitations
- The frontend UI is still in a starter state and is not yet connected to the backend experience end-to-end.
- The chat assistant can provide grounded answers, but it should still be treated as an assistant rather than a financial advisor.
- The current implementation focuses on stock fundamentals and recent price-history context rather than full portfolio analysis.

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for the latest project changes.

## License
TBD