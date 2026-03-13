# One Percent Better Poker

GGPoker tournament hand history analyzer. Fish exploitation tracking + player growth scoring.

## Features

- **Hand History Parsing**: Full GGPoker .txt file parsing with preflop/postflop multi-street analysis
- **Exploit Signal Tracking**: VPIP, PFR, 3-bet rates, c-bet frequencies, barreling patterns
- **Fish Detection**: Automatic identification of weak players and table dynamics
- **Growth Analytics**: Weekly trends in exploit signals to track improvement
- **Advanced Metrics**: Reckless all-in detection, bad hand selection analysis, luck factor scoring
- **Tournament Summary**: P&L tracking and cumulative performance over time

## Tech Stack

- **Backend**: FastAPI + SQLite (SQLAlchemy ORM)
- **Frontend**: Next.js + Tailwind CSS (in development)
- **Parser**: Custom GGPoker-specific regex parsing
- **Testing**: Pytest with 78 passing tests

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Run Tests

```bash
cd backend
python -m pytest tests/ -v
```

### API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API docs.

## Usage

1. Upload GGPoker hand history .txt files via the `/ingest` endpoint
2. View tournament summaries at `/tournaments`
3. Analyze exploit signals at `/analytics/signals`
4. Track growth over time at `/analytics/growth`

## Key Concepts

- **Fish Exploitation**: Identify and exploit weak player patterns (limps, oversize bets, donk bets)
- **Table Dynamics**: Classify tables as "fishy", "reg", or "mixed"
- **Luck Factor**: Measure variance between expected and actual results
- **Growth Tracking**: Monitor weekly improvements in key poker metrics

## Development

This project follows TDD (Test-Driven Development) principles. Always write failing tests first, then implement the feature.

## License

MIT License