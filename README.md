# 1% Better - Exploit Better

Product engine for the main poker commercial experiment.

The product promise is intentionally narrow:

- one tournament review
- three repeated habits
- one next-session adjustment

This repo contains the analysis engine behind that promise. It should stay grounded in a clear paid-use case, not expand into a broad poker platform before the core loop earns it.

## Features

- **Hand History Parsing**: Full GGPoker `.txt` parsing with preflop and postflop multi-street analysis
- **Exploit Signal Tracking**: VPIP, PFR, 3-bet rates, c-bet frequencies, and barreling patterns
- **Fish Detection**: Identification of weak-player patterns and table dynamics
- **Growth Analytics**: Weekly trends in exploit signals to track improvement
- **Advanced Metrics**: Reckless all-in detection, bad hand selection analysis, and luck-factor scoring
- **Tournament Summary**: P&L tracking and cumulative performance over time

## Repo Role

Use this repo to sharpen product clarity for `Exploit Better`:

- make the single-tournament review feel valuable
- produce insight that a player would pay for
- avoid turning the MVP into a theory-heavy study suite
- keep monetization tied to a believable first report

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
