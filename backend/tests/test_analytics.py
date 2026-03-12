"""
Unit tests for analytics.py.
Uses an in-memory SQLite DB seeded with known fixtures.
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app import models
from app.analytics import get_tournament_summary, get_positional_stats, get_exploit_signals


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def _add_tournament(db, gg_id="GG001", buy_in=50.0, net_result=100.0, date=None):
    t = models.Tournament(
        gg_id=gg_id,
        name=f"Test Tourney {gg_id}",
        buy_in=buy_in,
        bounty=0.0,
        format="Standard",
        date=date or datetime(2026, 1, 1),
        net_result=net_result,
    )
    db.add(t)
    db.flush()
    return t


def _add_hand(db, tournament_id, position="BTN", action="raises", result_bb=50.0, hero="Hero"):
    h = models.Hand(
        tournament_id=tournament_id,
        hand_number=f"HN-{position}-{result_bb}-{id(h := object())}",
        hero_name=hero,
        position=position,
        stack_bb=100.0,
        action_street="preflop",
        action=action,
        result_bb=result_bb,
    )
    db.add(h)
    db.flush()
    return h


# ── get_tournament_summary ─────────────────────────────────────────────────────

def test_tournament_summary_empty(db):
    df = get_tournament_summary(db)
    assert df.empty


def test_tournament_summary_with_data(db):
    _add_tournament(db, "GG001", buy_in=50.0, net_result=100.0, date=datetime(2026, 1, 1))
    _add_tournament(db, "GG002", buy_in=50.0, net_result=-50.0, date=datetime(2026, 1, 2))
    db.commit()

    df = get_tournament_summary(db)
    assert len(df) == 2
    assert "cumulative_pnl" in df.columns
    # Sorted by date: GG001 then GG002
    assert list(df["gg_id"]) == ["GG001", "GG002"]
    assert df["cumulative_pnl"].iloc[-1] == pytest.approx(50.0)


def test_tournament_summary_cumulative_pnl_runs_correctly(db):
    _add_tournament(db, "GG-A", net_result=30.0, date=datetime(2026, 1, 1))
    _add_tournament(db, "GG-B", net_result=-10.0, date=datetime(2026, 1, 2))
    _add_tournament(db, "GG-C", net_result=20.0, date=datetime(2026, 1, 3))
    db.commit()

    df = get_tournament_summary(db)
    assert list(df["cumulative_pnl"]) == pytest.approx([30.0, 20.0, 40.0])


# ── get_positional_stats ───────────────────────────────────────────────────────

def test_positional_stats_empty(db):
    df = get_positional_stats(db)
    assert df.empty


def test_positional_stats_with_data(db):
    t = _add_tournament(db)
    _add_hand(db, t.id, position="BTN", action="raises", result_bb=100.0)
    _add_hand(db, t.id, position="BTN", action="folds", result_bb=0.0)
    _add_hand(db, t.id, position="BB", action="folds", result_bb=0.0)
    db.commit()

    df = get_positional_stats(db)
    assert set(df["position"]) == {"BTN", "BB"}

    btn = df[df["position"] == "BTN"].iloc[0]
    assert btn["hands"] == 2
    assert btn["vpip"] == pytest.approx(0.5)
    assert btn["fold_rate"] == pytest.approx(0.5)
    assert btn["avg_result_bb"] == pytest.approx(50.0)

    bb = df[df["position"] == "BB"].iloc[0]
    assert bb["vpip"] == pytest.approx(0.0)


def test_positional_stats_filtered_by_hero(db):
    t = _add_tournament(db)
    _add_hand(db, t.id, position="BTN", hero="HeroA", result_bb=100.0)
    _add_hand(db, t.id, position="CO", hero="HeroB", result_bb=200.0)
    db.commit()

    df = get_positional_stats(db, hero_name="HeroA")
    assert len(df) == 1
    assert df.iloc[0]["position"] == "BTN"


# ── get_exploit_signals ────────────────────────────────────────────────────────

def test_exploit_signals_empty(db):
    result = get_exploit_signals(db)
    assert result["total_tournaments"] == 0
    assert result["total_pnl"] == 0.0
    assert result["best_position"] is None
    assert result["worst_position"] is None
    assert result["overall_vpip"] is None
    assert result["roi_pct"] is None


def test_exploit_signals_with_data(db):
    t = _add_tournament(db, buy_in=50.0, net_result=150.0)
    _add_hand(db, t.id, position="BTN", action="raises", result_bb=200.0)
    _add_hand(db, t.id, position="BB", action="folds", result_bb=0.0)
    db.commit()

    result = get_exploit_signals(db)
    assert result["total_tournaments"] == 1
    assert result["total_pnl"] == pytest.approx(150.0)
    assert result["roi_pct"] == pytest.approx(300.0)
    assert result["best_position"]["position"] == "BTN"
    assert result["worst_position"]["position"] == "BB"


def test_exploit_signals_overall_vpip(db):
    t = _add_tournament(db)
    # 3 hands: 2 non-fold (vpip=1), 1 fold (vpip=0)
    _add_hand(db, t.id, position="BTN", action="raises", result_bb=0.0)
    _add_hand(db, t.id, position="BTN", action="calls", result_bb=0.0)
    _add_hand(db, t.id, position="BB", action="folds", result_bb=0.0)
    db.commit()

    result = get_exploit_signals(db)
    # BTN vpip=1.0, BB vpip=0.0 → mean=0.5 → 50.0%
    assert result["overall_vpip"] == pytest.approx(50.0)
