# MarketMind

AI-powered stock research assistant. Search a ticker to view key financial metrics and ask an AI chat assistant questions about the company, grounded in real financial data — not just the model guessing.

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