# Changelog

## [Unreleased]
### Added
- FastAPI backend with stock lookup and chat endpoints
- Real stock data retrieval via yfinance
- Groq-backed chat assistant for stock questions
- Prompt context that includes current fundamentals plus recent price-history summary
- Backend tests covering stock lookup, invalid tickers, chat success, and fallback behavior

### Updated
- Switched the AI integration from Gemini to Groq
- Refined prompt construction to include 30-day, 90-day, and 1-year change context
- Improved error handling for unsupported or invalid ticker queries

### Notes
- The frontend remains in a starter state and is not yet fully integrated with the backend experience
