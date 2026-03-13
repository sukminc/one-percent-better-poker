import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db, Base

TEST_DB = "sqlite:///./test.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Reset DB on every test run so empty-state tests are always consistent
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ── Shared hand history fixture ────────────────────────────────────────────────

HAND_FILE_NAME = "GG20260102-0122 - Test Tourney 26.txt"
HAND_FILE_CONTENT = b"""Poker Hand #RC0001-00001: Tournament #001, Hold'em No Limit - 2026/01/02 01:22:00
Table '001 1' 9-max
Seat #1 is the button
Level1(1/1)
Seat 1: TestHero (5000 in chips)
Seat 2: Villain (4000 in chips)
*** HOLE CARDS ***
Dealt to TestHero [Ah Kd]
Villain: raises 200 to 400
TestHero: folds
*** SUMMARY ***
Villain collected 200
"""


# ── Health ─────────────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── Analytics (empty DB) ───────────────────────────────────────────────────────

def test_signals_empty():
    r = client.get("/analytics/signals")
    assert r.status_code == 200
    data = r.json()
    assert data["total_hands"] == 0


def test_pnl_empty():
    r = client.get("/analytics/pnl")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_positional_stats_empty():
    r = client.get("/analytics/positional")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_tournaments_empty():
    r = client.get("/tournaments")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── Ingest ─────────────────────────────────────────────────────────────────────

def test_ingest_non_txt_rejected():
    r = client.post(
        "/ingest",
        files={"file": ("hands.csv", b"data", "text/csv")},
        params={"hero_name": "TestHero"},
    )
    assert r.status_code == 400


def test_ingest_txt():
    r = client.post(
        "/ingest",
        files={"file": (HAND_FILE_NAME, HAND_FILE_CONTENT, "text/plain")},
        params={"hero_name": "TestHero"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["tournament"] == "GG20260102-0122"
    assert data["hands_found"] == 1
    assert data["hands_inserted"] == 1


def test_ingest_idempotent():
    """Re-uploading the same file should return already_exists=True."""
    r = client.post(
        "/ingest",
        files={"file": (HAND_FILE_NAME, HAND_FILE_CONTENT, "text/plain")},
        params={"hero_name": "TestHero"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["already_exists"] is True


# ── Tournaments (post-ingest) ──────────────────────────────────────────────────

def test_list_tournaments_after_ingest():
    r = client.get("/tournaments")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    gg_ids = [t["gg_id"] for t in data]
    assert "GG20260102-0122" in gg_ids


def test_update_tournament_not_found():
    r = client.patch("/tournaments/99999", params={"net_result": 200.0})
    assert r.status_code == 404


def test_update_tournament():
    # Get the tournament ID first
    tournaments = client.get("/tournaments").json()
    t_id = next(t["id"] for t in tournaments if t["gg_id"] == "GG20260102-0122")

    r = client.patch(
        f"/tournaments/{t_id}",
        params={"net_result": 250.0, "finish_position": 3, "total_players": 100},
    )
    assert r.status_code == 200
    assert r.json()["updated"] == t_id

    # Verify the update persisted
    tournaments = client.get("/tournaments").json()
    updated = next(t for t in tournaments if t["id"] == t_id)
    assert updated["net_result"] == pytest.approx(250.0)
    assert updated["finish_position"] == 3


# ── Analytics (post-ingest) ────────────────────────────────────────────────────

def test_positional_stats_after_ingest():
    r = client.get("/analytics/positional", params={"hero_name": "TestHero"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    positions = {row["position"] for row in data}
    assert len(positions) >= 1


def test_signals_after_ingest():
    r = client.get("/analytics/signals", params={"hero_name": "TestHero"})
    assert r.status_code == 200
    data = r.json()
    assert data["total_hands"] >= 1
    assert "vpip_pct" in data
    assert "limp_iso_rate" in data


def test_pnl_after_ingest():
    r = client.get("/analytics/pnl")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "cumulative_pnl" in data[0]
    assert "net_result" in data[0]


# ── Stage analytics ────────────────────────────────────────────────────────────

def test_stage_returns_list():
    r = client.get("/analytics/stage")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_stage_after_ingest():
    r = client.get("/analytics/stage", params={"hero_name": "TestHero"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Each stage entry has required keys
    if data:
        assert "stage" in data[0]
        assert "hands" in data[0]
        assert "pfr_pct" in data[0]


# ── Fish report ─────────────────────────────────────────────────────────────────

def test_fish_report_empty():
    # Note: db may not be empty at this point (ingest tests ran), just check shape
    r = client.get("/analytics/fish-report")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_fish_report_after_ingest():
    r = client.get("/analytics/fish-report", params={"hero_name": "TestHero"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        row = data[0]
        assert "gg_id" in row
        assert "exploit_score" in row
        assert "limp_pct" in row
