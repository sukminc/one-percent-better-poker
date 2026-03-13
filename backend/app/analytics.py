"""
Analytics engine: exploit signal computation + growth tracking.

Core philosophy: track YOUR exploit frequency over time.
Growth = specific exploit actions happening more often.
"""

from typing import Optional
import pandas as pd
from sqlalchemy.orm import Session
from . import models


# ── Tournament Summary ─────────────────────────────────────────────────────────

def get_tournament_summary(db: Session) -> pd.DataFrame:
    """Return a DataFrame of all tournaments with P&L."""
    rows = db.query(models.Tournament).all()
    if not rows:
        return pd.DataFrame()

    data = [
        {
            "id": t.id,
            "gg_id": t.gg_id,
            "name": t.name,
            "date": t.date,
            "buy_in": t.buy_in,
            "bounty": t.bounty,
            "format": t.format,
            "finish_position": t.finish_position,
            "total_players": t.total_players,
            "net_result": t.net_result,
        }
        for t in rows
    ]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)
    df["cumulative_pnl"] = df["net_result"].cumsum()
    return df


# ── Exploit Signals ────────────────────────────────────────────────────────────

def get_exploit_signals(db: Session, hero_name: Optional[str] = None) -> dict:
    """
    Compute exploit frequency signals across all hands.

    Signals:
    - limp_iso_rate: % of limp situations where hero iso-raised
    - three_bet_rate: % of facing-a-raise situations where hero 3-bet
    - cbet_freq: % of flop opportunities where hero c-bet (was aggressor + saw flop)
    - turn_barrel_freq: % of c-bet flops where hero also bet turn
    - river_barrel_freq: % of turn bets where hero also bet river
    - vpip_pfr_gap: VPIP - PFR (lower = better, fewer calling stations)
    - fold_to_oversize_cbet_rate: % of oversize cbets hero folded to
    """
    q = db.query(models.Hand)
    if hero_name:
        q = q.filter(models.Hand.hero_name == hero_name)
    hands = q.all()

    if not hands:
        return _empty_signals()

    total = len(hands)

    # ── Preflop signals ────────────────────────────────────────────────────────
    limp_situations = [h for h in hands if h.facing_limp]
    iso_raises = [h for h in limp_situations if h.hero_iso_raised]
    limp_iso_rate = _pct(len(iso_raises), len(limp_situations))

    facing_raise = [h for h in hands if h.facing_open_size_bb is not None]
    hero_3bets = [h for h in facing_raise if h.hero_3bet]
    three_bet_rate = _pct(len(hero_3bets), len(facing_raise))

    vpip = sum(1 for h in hands if h.action != "fold")
    pfr = sum(1 for h in hands if h.action == "raise")
    vpip_pct = _pct(vpip, total)
    pfr_pct = _pct(pfr, total)
    vpip_pfr_gap = round(vpip_pct - pfr_pct, 1)

    # ── Postflop signals ───────────────────────────────────────────────────────
    # Hands where hero reached the flop
    saw_flop = [h for h in hands if h.flop_action is not None]

    # C-bet opportunities: hero was raiser preflop AND saw the flop
    cbet_opportunities = [h for h in saw_flop if h.action == "raise"]
    cbets = [h for h in cbet_opportunities if h.flop_action == "bet"]
    cbet_freq = _pct(len(cbets), len(cbet_opportunities))

    # Turn barrel: c-betted the flop AND saw the turn
    turn_barrel_opps = [h for h in cbets if h.turn_action is not None]
    turn_barrels = [h for h in turn_barrel_opps if h.turn_action == "bet"]
    turn_barrel_freq = _pct(len(turn_barrels), len(turn_barrel_opps))

    # River barrel: bet turn AND saw the river
    river_barrel_opps = [h for h in turn_barrels if h.river_action is not None]
    river_barrels = [h for h in river_barrel_opps if h.river_action == "bet"]
    river_barrel_freq = _pct(len(river_barrels), len(river_barrel_opps))

    # Response to oversize cbets
    facing_oversize = [h for h in saw_flop if h.facing_oversize_cbet]
    fold_vs_oversize = [h for h in facing_oversize if h.flop_action == "fold"]
    call_vs_oversize = [h for h in facing_oversize if h.flop_action == "call"]
    raise_vs_oversize = [h for h in facing_oversize if h.flop_action == "raise"]
    oversize_cbet_response = {
        "fold_pct": _pct(len(fold_vs_oversize), len(facing_oversize)),
        "call_pct": _pct(len(call_vs_oversize), len(facing_oversize)),
        "raise_pct": _pct(len(raise_vs_oversize), len(facing_oversize)),
        "total_situations": len(facing_oversize),
    }

    return {
        "total_hands": total,
        # Preflop
        "vpip_pct": vpip_pct,
        "pfr_pct": pfr_pct,
        "vpip_pfr_gap": vpip_pfr_gap,
        "limp_iso_rate": limp_iso_rate,
        "limp_situations": len(limp_situations),
        "three_bet_rate": three_bet_rate,
        "facing_raise_situations": len(facing_raise),
        # Postflop
        "cbet_freq": cbet_freq,
        "cbet_opportunities": len(cbet_opportunities),
        "turn_barrel_freq": turn_barrel_freq,
        "river_barrel_freq": river_barrel_freq,
        "oversize_cbet_response": oversize_cbet_response,
    }


def get_positional_stats(db: Session, hero_name: Optional[str] = None) -> pd.DataFrame:
    """Win-rate and action frequency by position."""
    q = db.query(models.Hand)
    if hero_name:
        q = q.filter(models.Hand.hero_name == hero_name)
    rows = q.all()
    if not rows:
        return pd.DataFrame()

    data = [
        {
            "position": h.position,
            "action": h.action,
            "result_bb": h.result_bb or 0.0,
            "stack_bb": h.stack_bb or 0.0,
        }
        for h in rows
    ]
    df = pd.DataFrame(data)

    stats = (
        df.groupby("position")
        .agg(
            hands=("result_bb", "count"),
            avg_result_bb=("result_bb", "mean"),
            total_result_bb=("result_bb", "sum"),
            vpip=("action", lambda x: (x != "fold").mean()),
            pfr=("action", lambda x: (x == "raise").mean()),
            fold_rate=("action", lambda x: (x == "fold").mean()),
        )
        .reset_index()
    )
    stats["avg_result_bb"] = stats["avg_result_bb"].round(2)
    stats["vpip"] = (stats["vpip"] * 100).round(1)
    stats["pfr"] = (stats["pfr"] * 100).round(1)
    stats["vpip_pfr_gap"] = (stats["vpip"] - stats["pfr"]).round(1)
    return stats


def get_growth_timeline(db: Session, hero_name: Optional[str] = None) -> list[dict]:
    """
    Compute exploit signal trends grouped by week.
    Returns a list of {week, limp_iso_rate, cbet_freq, three_bet_rate, ...}
    sorted chronologically for chart rendering.
    """
    q = db.query(models.Hand, models.Tournament.date).join(
        models.Tournament, models.Hand.tournament_id == models.Tournament.id
    )
    if hero_name:
        q = q.filter(models.Hand.hero_name == hero_name)

    rows = q.all()
    if not rows:
        return []

    records = []
    for hand, date in rows:
        records.append({
            "week": date.strftime("%Y-W%W") if date else "unknown",
            "action": hand.action,
            "facing_limp": hand.facing_limp or False,
            "hero_iso_raised": hand.hero_iso_raised or False,
            "facing_open": hand.facing_open_size_bb is not None,
            "hero_3bet": hand.hero_3bet or False,
            "raiser_saw_flop": hand.action == "raise" and hand.flop_action is not None,
            "cbet": hand.flop_action == "bet" if hand.action == "raise" else False,
            "turn_barrel": hand.turn_action == "bet" if hand.flop_action == "bet" else False,
        })

    df = pd.DataFrame(records)
    result = []

    for week, grp in df.groupby("week"):
        n = len(grp)
        limp_sit = grp["facing_limp"].sum()
        iso = grp["hero_iso_raised"].sum()
        open_sit = grp["facing_open"].sum()
        threebet = grp["hero_3bet"].sum()
        cbet_opp = grp["raiser_saw_flop"].sum()
        cbet = grp["cbet"].sum()
        barrel_opp = grp["cbet"].sum()
        barrel = grp["turn_barrel"].sum()

        result.append({
            "week": week,
            "hands": n,
            "limp_iso_rate": _pct(iso, limp_sit),
            "three_bet_rate": _pct(threebet, open_sit),
            "cbet_freq": _pct(cbet, cbet_opp),
            "turn_barrel_freq": _pct(barrel, barrel_opp),
            "vpip_pct": _pct((grp["action"] != "fold").sum(), n),
            "pfr_pct": _pct((grp["action"] == "raise").sum(), n),
        })

    return sorted(result, key=lambda x: x["week"])


# ── Session context ────────────────────────────────────────────────────────────

def get_session_context(db: Session, tournament_id: int) -> dict:
    """Return the pre-computed session context for a tournament."""
    t = db.query(models.Tournament).filter_by(id=tournament_id).first()
    if not t or not t.session_context:
        return {}
    return t.session_context


# ── Helpers ────────────────────────────────────────────────────────────────────

def _pct(numerator: int, denominator: int) -> Optional[float]:
    if denominator == 0:
        return None
    return round(numerator / denominator * 100, 1)


def _empty_signals() -> dict:
    return {
        "total_hands": 0,
        "vpip_pct": None,
        "pfr_pct": None,
        "vpip_pfr_gap": None,
        "limp_iso_rate": None,
        "limp_situations": 0,
        "three_bet_rate": None,
        "facing_raise_situations": 0,
        "cbet_freq": None,
        "cbet_opportunities": 0,
        "turn_barrel_freq": None,
        "river_barrel_freq": None,
        "oversize_cbet_response": {
            "fold_pct": None, "call_pct": None, "raise_pct": None, "total_situations": 0
        },
    }
