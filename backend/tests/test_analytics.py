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
from app.analytics import (
    get_tournament_summary, get_positional_stats, get_exploit_signals,
    get_stage_stats, get_fish_report, get_reckless_allin_signals,
    get_bad_hand_selection, get_luck_score, get_non_ideal_range_wins,
)


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


def _add_hand(db, tournament_id, position="BTN", action="raise", result_bb=0.0,
              hero="Hero", facing_limp=False, hero_iso_raised=False, hero_3bet=False,
              facing_open_size_bb=None, flop_action=None, turn_action=None,
              river_action=None, facing_oversize_cbet=False, facing_donk_bet=False,
              opponent_limped=False, stack_bb=100.0, hero_cards=None, showdown_hands=None,
              showdown_winner=None, hero_raise_bb=None, flop_bet_pct=None, turn_bet_pct=None,
              river_bet_pct=None):
    h = models.Hand(
        tournament_id=tournament_id,
        hand_number=f"HN-{id(object())}",
        hero_name=hero,
        position=position,
        stack_bb=stack_bb,
        action_street="preflop",
        action=action,
        result_bb=result_bb,
        facing_limp=facing_limp,
        hero_iso_raised=hero_iso_raised,
        hero_3bet=hero_3bet,
        facing_open_size_bb=facing_open_size_bb,
        flop_action=flop_action,
        turn_action=turn_action,
        river_action=river_action,
        facing_oversize_cbet=facing_oversize_cbet,
        facing_donk_bet=facing_donk_bet,
        opponent_limped=opponent_limped,
        hero_cards=hero_cards,
        showdown_hands=showdown_hands,
        showdown_winner=showdown_winner,
        hero_raise_bb=hero_raise_bb,
        flop_bet_pct=flop_bet_pct,
        turn_bet_pct=turn_bet_pct,
        river_bet_pct=river_bet_pct,
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
    assert list(df["gg_id"]) == ["GG001", "GG002"]
    assert df["cumulative_pnl"].iloc[-1] == pytest.approx(50.0)


def test_tournament_summary_cumulative_pnl(db):
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
    _add_hand(db, t.id, position="BTN", action="raise", result_bb=100.0)
    _add_hand(db, t.id, position="BTN", action="fold", result_bb=0.0)
    _add_hand(db, t.id, position="BB", action="fold", result_bb=0.0)
    db.commit()

    df = get_positional_stats(db)
    assert set(df["position"]) == {"BTN", "BB"}

    btn = df[df["position"] == "BTN"].iloc[0]
    assert btn["hands"] == 2
    assert btn["vpip"] == pytest.approx(50.0)   # percentage, not decimal
    assert btn["pfr"] == pytest.approx(50.0)
    assert btn["fold_rate"] == pytest.approx(50.0)   # fold_rate is also a percentage
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
    assert result["total_hands"] == 0
    assert result["limp_iso_rate"] is None
    assert result["three_bet_rate"] is None
    assert result["cbet_freq"] is None


def test_exploit_signals_vpip_pfr(db):
    t = _add_tournament(db)
    _add_hand(db, t.id, action="raise")   # VPIP + PFR
    _add_hand(db, t.id, action="call")    # VPIP only
    _add_hand(db, t.id, action="fold")    # neither
    _add_hand(db, t.id, action="fold")
    db.commit()

    result = get_exploit_signals(db)
    assert result["total_hands"] == 4
    assert result["vpip_pct"] == pytest.approx(50.0)
    assert result["pfr_pct"] == pytest.approx(25.0)
    assert result["vpip_pfr_gap"] == pytest.approx(25.0)


def test_exploit_signals_three_bet_rate(db):
    t = _add_tournament(db)
    # 4 hands facing a raise: 1 three-bet, 3 did not
    _add_hand(db, t.id, facing_open_size_bb=3.0, hero_3bet=True, action="raise")
    _add_hand(db, t.id, facing_open_size_bb=3.0, hero_3bet=False, action="fold")
    _add_hand(db, t.id, facing_open_size_bb=3.0, hero_3bet=False, action="fold")
    _add_hand(db, t.id, facing_open_size_bb=3.0, hero_3bet=False, action="fold")
    db.commit()

    result = get_exploit_signals(db)
    assert result["three_bet_rate"] == pytest.approx(25.0)
    assert result["facing_raise_situations"] == 4


def test_exploit_signals_cbet_and_barrels(db):
    t = _add_tournament(db)
    # Hand 1: preflop raiser → c-bet flop → bet turn → bet river
    _add_hand(db, t.id, action="raise", flop_action="bet", turn_action="bet", river_action="bet")
    # Hand 2: preflop raiser → c-bet flop → no turn (hand over)
    _add_hand(db, t.id, action="raise", flop_action="bet")
    # Hand 3: preflop raiser → no c-bet (check flop)
    _add_hand(db, t.id, action="raise", flop_action="check")
    # Hand 4: non-raiser → saw flop (not a cbet opportunity)
    _add_hand(db, t.id, action="call", flop_action="call")
    db.commit()

    result = get_exploit_signals(db)
    assert result["cbet_freq"] == pytest.approx(66.7)     # 2/3 cbet opps
    # turn_barrel_opps = cbets where turn_action is not None → only Hand 1
    assert result["turn_barrel_freq"] == pytest.approx(100.0)  # 1/1
    assert result["river_barrel_freq"] == pytest.approx(100.0)  # 1/1


# ── BUG: limp_iso_rate must count hero_iso_raised hands in denominator ─────────

def test_exploit_signals_limp_iso_rate_includes_iso_raised_in_denominator(db):
    """
    Bug: get_exploit_signals used only facing_limp=True as the denominator.
    When hero iso-raises, the parser sets hero_iso_raised=True but facing_limp=False.
    The denominator must be (facing_limp=True OR hero_iso_raised=True).

    Setup: 4 limp situations total
      - 2 where hero faced a limp and did NOT iso (facing_limp=True, hero_iso_raised=False)
      - 2 where hero DID iso (facing_limp=False, hero_iso_raised=True)
    Expected limp_iso_rate: 2/4 = 50.0%
    Bug produces:           0/2 = 0.0%  (ignores iso hands in denominator)
    """
    t = _add_tournament(db)
    # Did not iso
    _add_hand(db, t.id, facing_limp=True, hero_iso_raised=False, action="fold")
    _add_hand(db, t.id, facing_limp=True, hero_iso_raised=False, action="call")
    # Did iso (parser sets hero_iso_raised=True, facing_limp=False)
    _add_hand(db, t.id, facing_limp=False, hero_iso_raised=True, action="raise")
    _add_hand(db, t.id, facing_limp=False, hero_iso_raised=True, action="raise")
    db.commit()

    result = get_exploit_signals(db)
    assert result["limp_iso_rate"] == pytest.approx(50.0)
    assert result["limp_situations"] == 4


# ── get_stage_stats ────────────────────────────────────────────────────────────

def test_stage_stats_empty(db):
    result = get_stage_stats(db)
    assert result == []


def test_stage_stats_groups_by_stack_depth(db):
    t = _add_tournament(db)
    # Early (>30BB): 2 hands, 1 raise 1 fold
    _add_hand(db, t.id, stack_bb=50.0, action="raise")
    _add_hand(db, t.id, stack_bb=35.0, action="fold")
    # Mid (15-30BB): 2 hands, both raises
    _add_hand(db, t.id, stack_bb=20.0, action="raise")
    _add_hand(db, t.id, stack_bb=15.0, action="raise")
    # Late (<15BB): 1 hand, fold
    _add_hand(db, t.id, stack_bb=10.0, action="fold")
    db.commit()

    result = get_stage_stats(db)
    stages = {r["stage"]: r for r in result}

    assert set(stages.keys()) == {"early", "mid", "late"}
    assert stages["early"]["hands"] == 2
    assert stages["mid"]["hands"] == 2
    assert stages["late"]["hands"] == 1


def test_stage_stats_pfr_per_stage(db):
    t = _add_tournament(db)
    _add_hand(db, t.id, stack_bb=100.0, action="raise")
    _add_hand(db, t.id, stack_bb=80.0, action="fold")
    _add_hand(db, t.id, stack_bb=20.0, action="fold")
    db.commit()

    result = get_stage_stats(db)
    stages = {r["stage"]: r for r in result}

    # Early: 1 raise out of 2 hands = 50%
    assert stages["early"]["pfr_pct"] == pytest.approx(50.0)
    # Mid: 0 raises out of 1 hand = 0%
    assert stages["mid"]["pfr_pct"] == pytest.approx(0.0)


def test_stage_stats_filtered_by_hero(db):
    t = _add_tournament(db)
    _add_hand(db, t.id, stack_bb=50.0, hero="HeroA", action="raise")
    _add_hand(db, t.id, stack_bb=50.0, hero="HeroB", action="fold")
    db.commit()

    result = get_stage_stats(db, hero_name="HeroA")
    assert len(result) == 1
    assert result[0]["hands"] == 1


# ── get_fish_report ────────────────────────────────────────────────────────────

def test_fish_report_empty(db):
    result = get_fish_report(db)
    assert result == []


def test_fish_report_per_tournament(db):
    t = _add_tournament(db, "GG001")
    # 4 hands: 2 with limpers, 1 with donk bet, 1 normal
    _add_hand(db, t.id, opponent_limped=True, hero_iso_raised=True, action="raise")
    _add_hand(db, t.id, opponent_limped=True, hero_iso_raised=False, facing_limp=True, action="call")
    _add_hand(db, t.id, facing_donk_bet=True, action="raise", flop_action="call")
    _add_hand(db, t.id, action="fold")
    db.commit()

    result = get_fish_report(db)
    assert len(result) == 1
    row = result[0]
    assert row["gg_id"] == "GG001"
    assert row["total_hands"] == 4
    assert row["limp_pct"] == pytest.approx(50.0)   # 2/4
    assert row["donk_bet_pct"] == pytest.approx(25.0)  # 1/4
    assert "exploit_score" in row
    assert 0 <= row["exploit_score"] <= 100


def test_fish_report_exploit_score_higher_when_exploiting(db):
    """Hero who iso-raises and c-bets scores higher than passive hero."""
    t1 = _add_tournament(db, "GG-Active")
    t2 = _add_tournament(db, "GG-Passive")

    # Active: iso-raised all limps, c-bet when possible
    _add_hand(db, t1.id, opponent_limped=True, hero_iso_raised=True, action="raise",
              flop_action="bet")
    _add_hand(db, t1.id, opponent_limped=True, hero_iso_raised=True, action="raise",
              flop_action="bet")

    # Passive: faced limps and just called/folded, no c-bets
    _add_hand(db, t2.id, opponent_limped=True, facing_limp=True, action="call",
              flop_action="check")
    _add_hand(db, t2.id, opponent_limped=True, facing_limp=True, action="fold")
    db.commit()

    result = get_fish_report(db)
    by_gg = {r["gg_id"]: r for r in result}
    assert by_gg["GG-Active"]["exploit_score"] > by_gg["GG-Passive"]["exploit_score"]


# ── table dynamics (fish% vs reg%) ────────────────────────────────────────────

def test_fish_report_includes_reg_pct(db):
    t = _add_tournament(db, "GG-Mixed")
    # Fish hand: opponent limped
    _add_hand(db, t.id, opponent_limped=True, action="raise")
    # Reg hand: standard open 2.5BB, no fish patterns
    _add_hand(db, t.id, facing_open_size_bb=2.5, action="fold")
    # Unknown: hero folded, no opponent action seen
    _add_hand(db, t.id, action="fold")
    db.commit()

    result = get_fish_report(db)
    row = result[0]
    assert "reg_pct" in row
    assert "fish_pct" in row
    assert "table_dynamic" in row
    # 1/3 fish, 1/3 reg
    assert row["fish_pct"] == pytest.approx(33.3, abs=0.2)


# ── New analytics functions ────────────────────────────────────────────────────

def test_reckless_allin_signals(db):
    t = _add_tournament(db)
    _add_hand(db, t.id, hero_raise_bb=90.0, stack_bb=100.0, action="raise")  # all-in
    _add_hand(db, t.id, flop_bet_pct=85.0, action="raise", flop_action="bet")  # all-in
    _add_hand(db, t.id, action="fold")
    db.commit()

    result = get_reckless_allin_signals(db)
    assert result["total_hands"] == 3
    assert result["reckless_allin_pct"] == pytest.approx(66.7)


def test_bad_hand_selection(db):
    t = _add_tournament(db)
    _add_hand(db, t.id, hero_cards="2s 7h", showdown_hands={"Hero": "2s 7h"}, action="raise")
    _add_hand(db, t.id, hero_cards="As Kd", showdown_hands={"Hero": "As Kd"}, action="raise")
    _add_hand(db, t.id, action="fold")
    db.commit()

    result = get_bad_hand_selection(db)
    assert result["total_showdowns"] == 2
    assert result["bad_selection_pct"] == pytest.approx(50.0)


def test_luck_score(db):
    t = _add_tournament(db)
    _add_hand(db, t.id, hero_cards="2s 7h", result_bb=10.0, action="raise")  # lucky win
    _add_hand(db, t.id, hero_cards="As Kd", result_bb=-5.0, action="raise")  # unlucky loss
    _add_hand(db, t.id, action="fold")
    db.commit()

    result = get_luck_score(db)
    assert result["total_hands"] == 3
    assert result["luck_score"] == pytest.approx(66.7)


def test_non_ideal_range_wins(db):
    t = _add_tournament(db)
    _add_hand(db, t.id, hero_cards="2s 7h", result_bb=10.0, action="raise")  # non-ideal win
    _add_hand(db, t.id, hero_cards="As Kd", result_bb=5.0, action="raise")  # ideal win
    _add_hand(db, t.id, result_bb=-5.0, action="raise")
    db.commit()

    result = get_non_ideal_range_wins(db)
    assert result["total_wins"] == 2
    assert result["non_ideal_win_pct"] == pytest.approx(50.0)


def test_table_dynamic_fishy(db):
    t = _add_tournament(db, "GG-Fish")
    # 4/5 hands have fish patterns
    _add_hand(db, t.id, opponent_limped=True, action="raise")
    _add_hand(db, t.id, opponent_limped=True, action="fold")
    _add_hand(db, t.id, facing_open_size_bb=5.0, action="fold")   # 5x open = fish
    _add_hand(db, t.id, facing_donk_bet=True, action="raise", flop_action="call")
    _add_hand(db, t.id, facing_open_size_bb=2.5, action="fold")   # reg-like
    db.commit()

    result = get_fish_report(db)
    assert result[0]["table_dynamic"] == "fishy"


def test_table_dynamic_reg(db):
    t = _add_tournament(db, "GG-Reg")
    # All standard-sizing hands
    _add_hand(db, t.id, facing_open_size_bb=2.5, action="fold")
    _add_hand(db, t.id, facing_open_size_bb=3.0, action="raise")
    _add_hand(db, t.id, facing_open_size_bb=2.8, action="fold")
    db.commit()

    result = get_fish_report(db)
    assert result[0]["table_dynamic"] == "reg"


def test_table_dynamic_mixed(db):
    t = _add_tournament(db, "GG-Mixed")
    _add_hand(db, t.id, opponent_limped=True, action="raise")      # fish
    _add_hand(db, t.id, facing_open_size_bb=2.5, action="fold")   # reg
    _add_hand(db, t.id, action="fold")                             # unknown
    db.commit()

    result = get_fish_report(db)
    assert result[0]["table_dynamic"] == "mixed"
