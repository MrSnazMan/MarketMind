# MarketMind

Research any stock with an AI assistant that’s backed by real financial data. Search a ticker to instantly see key metrics, then ask questions about the company and get answers grounded in its actual financials. Rest assured, no guessing involved.

## Status
*Disclaimer: In development; project scaffold complete, core features in progress.

## Tech stack
- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript (Vite)
- **Financial data**: yfinance
- **AI**: Gemini API

## Planned features
- [ ] Company dashboard (price, market cap, P/E, EPS, etc.)
- [ ] AI chat grounded in real financial data
- [ ] SEC filing summarization
- [ ] Financial health score

## Local setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com)

### Backend
\`\`\`
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
\`\`\`
Create a `.env` file (see `.env.example` for the required variable), then:
\`\`\`
uvicorn main:app --reload
\`\`\`
Runs at `http://localhost:8000`.

### Frontend
\`\`\`
cd frontend
npm install
npm run dev
\`\`\`
Runs at `http://localhost:5173`.

## License
TBD