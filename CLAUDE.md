# one-percent-better-poker

GGPoker tournament hand history analyzer. Fish exploitation tracking + player growth scoring.

## Tech Stack

- **Backend:** FastAPI + SQLite (SQLAlchemy ORM) — `backend/`
- **Frontend:** Next.js + Tailwind — `frontend/`
- **Parser:** GGPoker-specific regex — `backend/app/parser.py`

## Development

```bash
# Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Tests (always TDD — write failing tests first)
cd backend && python3 -m pytest tests/ -v
```

## Key Decisions

- **TDD always.** Write failing test → implement → confirm all pass.
- **No Claude AI in MVP** (cost). Analytics only.
- GGPoker Ontario anonymizes usernames — no cross-session opponent tracking.
- Stack depth = tournament stage proxy: early >30BB, mid 15-30BB, late <15BB.

## Completed Work

### Parser (`backend/app/parser.py`)
- Full GGPoker hand history parsing (preflop + postflop multi-street)
- Limp detection, iso-raise, 3-bet, c-bet, turn/river barrels
- Opponent pattern flags: `facing_donk_bet`, `facing_oversize_cbet`, `opponent_limped`
- **Bug fixed:** `facing_donk_bet` was incorrectly set when hero is OOP and opponent c-bets (normal c-bet was mislabeled as donk). Fix: only set `facing_donk_bet=True` when `hero_was_aggressor`.
- **Bug fixed:** `hero_first_action` fallback of `or "fold"` prevented postflop action detection.
- Session context aggregation (`compute_session_context`) for per-tournament opponent patterns.
- **Sizing inconsistency detection**: tracks per-opponent limps and raises within tournament. Players who showed BOTH → `inconsistent_sizer_count` (readable tell — trap limp or limp-then-blast). `_limper_names` / `_opener_name` fields passed through parse pipeline, stripped before DB insertion.
- **Showdown parsing**: Added parsing for showdown sections, hero cards, opponent cards, and winner detection.

### Analytics (`backend/app/analytics.py`)
- `get_exploit_signals()` — VPIP, PFR, limp iso rate, 3-bet rate, c-bet, barrels, oversize cbet response
- `get_positional_stats()` — per-position VPIP/PFR/fold/result breakdown
- `get_tournament_summary()` — P&L + cumulative PnL over time
- `get_growth_timeline()` — weekly trends of exploit signals
- `get_stage_stats()` — exploit signals grouped by stack depth (early/mid/late)
- `get_fish_report()` — per-tournament fish density + hero exploitation score (0-100) + `reg_pct` + `table_dynamic` ("fishy"/"reg"/"mixed")
- **New:** `get_reckless_allin_signals()` — Detects reckless all-in patterns by opponents.
- **New:** `get_bad_hand_selection()` — Analyzes bad hand selection in showdowns (weak hands played).
- **New:** `get_luck_score()` — Measures luck factor (variance from expected results).
- **New:** `get_non_ideal_range_wins()` — Tracks wins with non-ideal (bad) hand ranges.
- **Bug fixed:** `limp_iso_rate` denominator was missing `hero_iso_raised=True` hands.
- **Bug fixed:** `fold_rate` in positional stats was missing `×100` (was 0-1 not 0-100).

### API Endpoints (`backend/app/main.py`)
```
GET  /health
POST /ingest                     — upload .txt hand history (idempotent)
GET  /tournaments                — list all tournaments
GET  /tournaments/{id}           — tournament detail + hands
PATCH /tournaments/{id}          — update net_result, finish_position, date
GET  /hands/{id}                 — single hand detail
GET  /analytics/signals          — exploit signals aggregate
GET  /analytics/positional       — win-rate by position
GET  /analytics/pnl              — cumulative P&L
GET  /analytics/growth           — weekly signal trends
GET  /analytics/stage            — signals by tournament stage (stack depth)
GET  /analytics/fish-report      — per-tournament fish density + exploit score
GET  /analytics/reckless-allin   — reckless all-in patterns detection
GET  /analytics/bad-hand-selection — bad hand selection in showdowns
GET  /analytics/luck-score       — luck factor score
GET  /analytics/non-ideal-wins   — non-ideal range wins
```

### Tests (78 passing)
- `test_api.py` — full API integration tests
- `test_analytics.py` — unit tests for all analytics functions (including new reckless all-in, bad hand selection, luck score, non-ideal wins)
- `test_parser.py` — unit tests for parser (filename, hand splitting, parse_hand, showdown parsing)

## Pending

- Shareable results page (frontend)
- Frontend: drag-and-drop upload UI
- Frontend: tournament list + stage/fish dashboard
- SaaS: auth + Stripe + PostgreSQL migration
