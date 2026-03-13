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
    # Limp situations: either hero faced a limp (and didn't iso) OR hero did iso.
    # Parser sets facing_limp=True only when hero did NOT raise; hero_iso_raised=True
    # when hero raised over a limper (facing_limp=False in that case).
    limp_situations = [h for h in hands if h.facing_limp or h.hero_iso_raised]
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
    stats["fold_rate"] = (stats["fold_rate"] * 100).round(1)
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
            "raiser_saw_flop": (
                hand.action == "raise" and hand.flop_action is not None
            ),
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


# ── Stage stats ────────────────────────────────────────────────────────────────

def get_stage_stats(db: Session, hero_name: Optional[str] = None) -> list[dict]:
    """
    Exploit signals grouped by tournament stage (stack depth proxy).
    Stages: early (>30BB), mid (15-30BB), late (<15BB).
    """
    q = db.query(models.Hand)
    if hero_name:
        q = q.filter(models.Hand.hero_name == hero_name)
    hands = q.all()
    if not hands:
        return []

    def _stage(stack_bb: float) -> str:
        if stack_bb > 30:
            return "early"
        elif stack_bb >= 15:
            return "mid"
        return "late"

    buckets: dict[str, list] = {"early": [], "mid": [], "late": []}
    for h in hands:
        s = _stage(h.stack_bb or 0.0)
        buckets[s].append(h)

    result = []
    for stage in ("early", "mid", "late"):
        grp = buckets[stage]
        if not grp:
            continue
        n = len(grp)
        vpip = sum(1 for h in grp if h.action != "fold")
        pfr = sum(1 for h in grp if h.action == "raise")
        limp_sit = [h for h in grp if h.facing_limp or h.hero_iso_raised]
        iso = [h for h in limp_sit if h.hero_iso_raised]
        facing_raise = [h for h in grp if h.facing_open_size_bb is not None]
        three_bets = [h for h in facing_raise if h.hero_3bet]
        cbet_opps = [
            h for h in grp if h.action == "raise" and h.flop_action is not None
        ]
        cbets = [h for h in cbet_opps if h.flop_action == "bet"]
        result.append({
            "stage": stage,
            "hands": n,
            "vpip_pct": _pct(vpip, n),
            "pfr_pct": _pct(pfr, n),
            "limp_iso_rate": _pct(len(iso), len(limp_sit)),
            "three_bet_rate": _pct(len(three_bets), len(facing_raise)),
            "cbet_freq": _pct(len(cbets), len(cbet_opps)),
        })
    return result


# ── Fish report ─────────────────────────────────────────────────────────────────

def get_fish_report(db: Session, hero_name: Optional[str] = None) -> list[dict]:
    """
    Per-tournament fish density + hero exploitation score.

    Fish density: how fishy the field was
    (limps, donk bets, oversize opens).
    Exploit score (0-100): how well hero exploited the fish patterns.
      = weighted avg of limp_iso_rate (40%), cbet_freq (35%),
        three_bet_rate (25%).
    """
    tournaments = db.query(models.Tournament).order_by(models.Tournament.date.desc()).all()
    if not tournaments:
        return []

    result = []
    for t in tournaments:
        q = db.query(models.Hand).filter_by(tournament_id=t.id)
        if hero_name:
            q = q.filter(models.Hand.hero_name == hero_name)
        hands = q.all()
        if not hands:
            continue

        n = len(hands)
        limp_count = sum(1 for h in hands if h.opponent_limped)
        donk_count = sum(1 for h in hands if h.facing_donk_bet)
        oversize_count = sum(1 for h in hands if h.facing_oversize_cbet)

        # Table dynamics: classify each hand as fish-signal, reg-signal, or unknown
        # Fish signal: limp, donk bet, oversize cbet, or 4x+ open
        # Reg signal:  standard open (2.0-3.5BB), no fish patterns
        fish_hands = sum(1 for h in hands if _is_fish_hand(h))
        reg_hands = sum(1 for h in hands if _is_reg_hand(h))
        fish_pct = _pct(fish_hands, n) or 0.0
        reg_pct = _pct(reg_hands, n) or 0.0
        table_dynamic = _classify_table(fish_pct, reg_pct)

        # Exploit signals
        limp_sit = [h for h in hands if h.facing_limp or h.hero_iso_raised]
        iso = [h for h in limp_sit if h.hero_iso_raised]
        limp_iso = _pct(len(iso), len(limp_sit)) or 0.0

        facing_raise = [h for h in hands if h.facing_open_size_bb is not None]
        three_bet_r = _pct(
            sum(1 for h in facing_raise if h.hero_3bet), len(facing_raise)
        ) or 0.0

        cbet_opps = [
            h for h in hands if h.action == "raise" and h.flop_action is not None
        ]
        cbet_r = _pct(
            sum(1 for h in cbet_opps if h.flop_action == "bet"), len(cbet_opps)
        ) or 0.0

        exploit_score = round(limp_iso * 0.40 + cbet_r * 0.35 + three_bet_r * 0.25, 1)

        result.append({
            "gg_id": t.gg_id,
            "name": t.name,
            "date": t.date,
            "total_hands": n,
            "limp_pct": _pct(limp_count, n),
            "donk_bet_pct": _pct(donk_count, n),
            "oversize_cbet_pct": _pct(oversize_count, n),
            "fish_pct": fish_pct,
            "reg_pct": reg_pct,
            "table_dynamic": table_dynamic,
            "limp_iso_rate": limp_iso if limp_sit else None,
            "cbet_freq": cbet_r if cbet_opps else None,
            "three_bet_rate": three_bet_r if facing_raise else None,
            "exploit_score": exploit_score,
        })
    return result


# ── Session context ────────────────────────────────────────────────────────────

def get_session_context(db: Session, tournament_id: int) -> dict:
    """Return the pre-computed session context for a tournament."""
    t = db.query(models.Tournament).filter_by(id=tournament_id).first()
    if not t or not t.session_context:
        return {}
    return t.session_context


# ── Helpers ────────────────────────────────────────────────────────────────────

def _is_fish_hand(h) -> bool:
    """Hand contains a fish pattern signal."""
    if h.opponent_limped or h.facing_donk_bet or h.facing_oversize_cbet:
        return True
    open_bb = h.facing_open_size_bb
    if open_bb is not None and open_bb >= 4.0:
        return True
    return False


def _is_reg_hand(h) -> bool:
    """Hand has standard-sizing opponent action, no fish patterns."""
    if _is_fish_hand(h):
        return False
    open_bb = h.facing_open_size_bb
    return open_bb is not None and 2.0 <= open_bb <= 3.5


def _classify_table(fish_pct: float, reg_pct: float) -> str:
    """Label table dynamic based on fish vs reg signal ratios."""
    if fish_pct >= 40.0:
        return "fishy"
    if reg_pct >= 50.0:
        return "reg"
    return "mixed"


def _pct(numerator: int, denominator: int) -> Optional[float]:
    if denominator == 0:
        return None
    return round(numerator / denominator * 100, 1)


def get_reckless_allin_signals(db: Session, hero_name: Optional[str] = None) -> dict:
    """
    Detect reckless all-in patterns by opponents.
    All-in defined as bet/raise >= 80% of pot or stack (approximation).
    """
    q = db.query(models.Hand)
    if hero_name:
        q = q.filter(models.Hand.hero_name == hero_name)
    hands = q.all()

    if not hands:
        return {"total_hands": 0, "reckless_allin_pct": None}

    allin_hands = 0
    for h in hands:
        # Preflop all-in: hero_raise_bb close to stack_bb
        if h.hero_raise_bb and h.stack_bb and h.hero_raise_bb >= h.stack_bb * 0.8:
            allin_hands += 1
        # Postflop: bet_pct close to 100 or facing large bet
        elif h.flop_bet_pct and h.flop_bet_pct >= 80:
            allin_hands += 1
        elif h.turn_bet_pct and h.turn_bet_pct >= 80:
            allin_hands += 1
        elif h.river_bet_pct and h.river_bet_pct >= 80:
            allin_hands += 1
        # Facing all-in: facing_open_size_bb large or oversize
        elif h.facing_open_size_bb and h.facing_open_size_bb >= 10:  # arbitrary threshold
            allin_hands += 1

    return {
        "total_hands": len(hands),
        "reckless_allin_pct": _pct(allin_hands, len(hands)),
    }


def get_bad_hand_selection(db: Session, hero_name: Optional[str] = None) -> dict:
    """
    Detect bad hand selection: showdown with weak hands.
    Weak: no pair, no suited connectors, etc.
    """
    q = db.query(models.Hand)
    if hero_name:
        q = q.filter(models.Hand.hero_name == hero_name)
    hands = q.all()

    showdown_hands = [h for h in hands if h.showdown_hands and h.hero_cards]
    if not showdown_hands:
        return {"total_showdowns": 0, "bad_selection_pct": None}

    bad_count = 0
    for h in showdown_hands:
        if _is_weak_hand(h.hero_cards):
            bad_count += 1

    return {
        "total_showdowns": len(showdown_hands),
        "bad_selection_pct": _pct(bad_count, len(showdown_hands)),
    }


def get_luck_score(db: Session, hero_name: Optional[str] = None) -> dict:
    """
    Luck score: variance between expected and actual results.
    High luck: winning with bad hands or losing with good hands.
    """
    q = db.query(models.Hand)
    if hero_name:
        q = q.filter(models.Hand.hero_name == hero_name)
    hands = q.all()

    luck_events = 0
    total = len(hands)
    for h in hands:
        if h.result_bb and h.result_bb > 0 and h.hero_cards and _is_weak_hand(h.hero_cards):
            luck_events += 1  # lucky win
        elif h.result_bb and h.result_bb < 0 and h.hero_cards and not _is_weak_hand(h.hero_cards):
            luck_events += 1  # unlucky loss

    return {
        "total_hands": total,
        "luck_score": _pct(luck_events, total) if total else None,
    }


def get_non_ideal_range_wins(db: Session, hero_name: Optional[str] = None) -> dict:
    """
    Non-ideal range wins: winning pots with bad hands.
    """
    q = db.query(models.Hand)
    if hero_name:
        q = q.filter(models.Hand.hero_name == hero_name)
    hands = q.all()

    win_hands = [h for h in hands if h.result_bb and h.result_bb > 0 and h.hero_cards]
    if not win_hands:
        return {"total_wins": 0, "non_ideal_win_pct": None}

    non_ideal = sum(1 for h in win_hands if _is_weak_hand(h.hero_cards))

    return {
        "total_wins": len(win_hands),
        "non_ideal_win_pct": _pct(non_ideal, len(win_hands)),
    }


# Helpers
def _is_weak_hand(cards: str) -> bool:
    """Simple weak hand detector: no pair, not suited connectors."""
    if not cards:
        return True
    ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    suits = set()
    card_ranks = []
    for card in cards.split():
        if len(card) == 2:
            r, s = card[0], card[1]
            card_ranks.append(ranks.get(r.upper(), 0))
            suits.add(s)
    if len(set(card_ranks)) == 2 and abs(card_ranks[0] - card_ranks[1]) <= 4:  # connectors
        return False
    if len(suits) == 1:  # suited
        return False
    return True  # weak if not pair/connector/suited


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
