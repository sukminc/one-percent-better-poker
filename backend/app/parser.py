"""
GGPoker hand history parser.
Parses raw .txt files exported from GGPoker into structured dicts
ready for DB insertion.

Covers:
- Preflop: all players (limp detection, open sizes, hero iso/3bet)
- Postflop: hero multi-street actions + bet sizing
- Opponent patterns: oversize cbets, donk bets
- Pot tracking for accurate bet-as-%-of-pot calculations
"""

import re
from datetime import datetime
from typing import Optional
from pathlib import Path


# ── Filename patterns ──────────────────────────────────────────────────────────
FILENAME_RE = re.compile(
    r"(GG\d{8}-\d{4})"           # GG ID
    r"\s*-\s*"
    r"(.+?)(?:\.txt)?$"           # tournament name
)

BUY_IN_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:Buy-?[Ii]n|buy-?in|\$)", re.IGNORECASE)
BOUNTY_RE = re.compile(r"\[Bounty", re.IGNORECASE)

# ── Hand-level patterns ────────────────────────────────────────────────────────
HAND_START_RE = re.compile(r"Poker Hand #([\w-]+):")
LEVEL_RE = re.compile(r"Level\d+\(([\d,]+)/([\d,]+)\)")
SEAT_RE = re.compile(r"Seat (\d+): (\S+) \(([\d,]+) in chips\)")
HERO_DEALT_RE = re.compile(r"Dealt to (\S+) \[")   # hero is the one whose cards are shown
BTN_RE = re.compile(r"Seat #(\d+) is the button")
ANTE_RE = re.compile(r"^(\S+): posts the ante ([\d,]+)", re.MULTILINE)
SB_RE = re.compile(r"^(\S+): posts small blind ([\d,]+)", re.MULTILINE)
BB_RE = re.compile(r"^(\S+): posts big blind ([\d,]+)", re.MULTILINE)
UNCALLED_RE = re.compile(r"Uncalled bet \(([\d,]+)\) returned to (\S+)")

# Street markers
STREET_MARKER_RE = re.compile(
    r"\*\*\* (HOLE CARDS|FLOP|TURN|RIVER|SHOWDOWN|SHOW DOWN|SUMMARY) \*\*\*"
)

# Action line: "PlayerName: action [amount] [to total]"
ACTION_LINE_RE = re.compile(
    r"^(\S+): (folds|checks|calls|raises|bets)(?: ([\d,]+))?(?: to ([\d,]+))?",
    re.MULTILINE,
)

# Result
RESULT_RE = re.compile(r"^(\S+) collected \$?([\d,]+)", re.MULTILINE)
SHOWDOWN_RE = re.compile(r"^(\S+): shows \[([^\]]+)\]", re.MULTILINE)


def _n(s: Optional[str]) -> int:
    """Parse comma-formatted number string to int."""
    return int(s.replace(",", "")) if s else 0


def parse_filename(filename: str) -> dict:
    """Extract GG ID, name, buy-in, format from filename."""
    stem = Path(filename).stem
    m = FILENAME_RE.match(stem)
    if not m:
        return {"gg_id": stem, "name": stem}

    gg_id = m.group(1)
    name = m.group(2).strip()

    date_str = gg_id[2:10]  # "20260102"
    try:
        date = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        date = datetime.utcnow()

    buy_in_m = re.search(r"(?:^|\s)(\d+(?:\.\d+)?)\s", name)
    buy_in = float(buy_in_m.group(1)) if buy_in_m else 0.0
    bounty = buy_in * 0.5 if BOUNTY_RE.search(name) else 0.0

    fmt_tags = []
    for tag in ["Bounty", "Turbo", "6-Max", "7-max", "9-Max", "Mystery Bounty", "Superstack"]:
        if re.search(re.escape(tag), name, re.IGNORECASE):
            fmt_tags.append(tag)
    fmt = ", ".join(fmt_tags) if fmt_tags else "Standard"

    return {
        "gg_id": gg_id,
        "name": name,
        "buy_in": buy_in,
        "bounty": bounty,
        "format": fmt,
        "date": date,
    }


def split_hands(raw_text: str) -> list[str]:
    """Split a full hand history file into individual hand blocks."""
    blocks = re.split(r"(?=Poker Hand #)", raw_text)
    return [b.strip() for b in blocks if b.strip().startswith("Poker Hand #")]


def parse_hand(hand_text: str, hero_name: Optional[str] = None) -> Optional[dict]:
    """
    Parse a single hand block into a structured dict.
    Returns None if the block cannot be parsed.
    """
    hm = HAND_START_RE.search(hand_text)
    if not hm:
        return None
    hand_number = hm.group(1)

    # Blind level
    lm = LEVEL_RE.search(hand_text)
    if not lm:
        return None
    big_blind = _n(lm.group(2))
    if big_blind == 0:
        return None

    # Seats: {seat_num: (player_name, chips)}
    seats_raw = SEAT_RE.findall(hand_text)  # (seat_num, name, chips)
    seat_map = {int(s): (name, _n(chips)) for s, name, chips in seats_raw}
    name_to_chips = {name: _n(chips) for _, name, chips in seats_raw}

    # Hero detection
    hero_m = HERO_DEALT_RE.search(hand_text)
    hero = hero_m.group(1) if hero_m else hero_name
    if not hero or hero not in name_to_chips:
        return None

    # Stack in BBs
    stack_bb = round(name_to_chips[hero] / big_blind, 1)

    # Position
    position = _detect_position(hand_text, hero, seat_map)

    # Split into street sections
    sections = _split_streets(hand_text)

    # ── Preflop parsing ────────────────────────────────────────────────────────
    antes = {m.group(1): _n(m.group(2)) for m in ANTE_RE.finditer(hand_text)}
    sb_m = SB_RE.search(hand_text)
    bb_m = BB_RE.search(hand_text)
    sb_player = sb_m.group(1) if sb_m else None
    bb_player = bb_m.group(1) if bb_m else None
    sb_amount = _n(sb_m.group(2)) if sb_m else 0
    bb_amount = _n(bb_m.group(2)) if bb_m else big_blind

    preflop = _parse_preflop(
        sections.get("hole_cards", ""),  # GGPoker names this section HOLE CARDS
        hero,
        big_blind,
        sb_player,
        sb_amount,
        bb_player,
        bb_amount,
        antes,
    )

    # ── Postflop parsing ───────────────────────────────────────────────────────
    pot = preflop["pot"]
    hero_was_aggressor = preflop["hero_first_action"] == "raise"
    # Is hero IP on flop? Approximation: BTN/CO are IP, blinds are OOP
    hero_ip = position in ("BTN", "CO", "HJ", "BTN/SB")

    flop = _parse_postflop_street(
        sections.get("flop", ""),
        hero,
        pot,
        big_blind,
        hero_was_aggressor=hero_was_aggressor,
        hero_ip=hero_ip,
    )
    pot = flop["pot_after"]

    turn = _parse_postflop_street(
        sections.get("turn", ""),
        hero,
        pot,
        big_blind,
        hero_was_aggressor=(flop["hero_action"] == "bet" or flop["hero_action"] == "raise"),
        hero_ip=hero_ip,
    )
    pot = turn["pot_after"]

    river = _parse_postflop_street(
        sections.get("river", ""),
        hero,
        pot,
        big_blind,
        hero_was_aggressor=(turn["hero_action"] == "bet" or turn["hero_action"] == "raise"),
        hero_ip=hero_ip,
    )

    # ── Result ─────────────────────────────────────────────────────────────────
    total_invested = (
        antes.get(hero, 0)
        + preflop["hero_invested"]
        + flop.get("hero_invested", 0)
        + turn.get("hero_invested", 0)
        + river.get("hero_invested", 0)
    )
    result_bb = _detect_result_bb(hand_text, hero, big_blind, total_invested)

    return {
        "hand_number": hand_number,
        "hero_name": hero,
        "position": position,
        "big_blind": float(big_blind),
        "stack_bb": stack_bb,

        # Preflop
        "action_street": preflop.get("hero_street", "preflop"),
        "action": preflop.get("hero_first_action", "fold"),
        "hero_raise_bb": preflop.get("hero_raise_bb"),
        "opponent_limped": preflop.get("opponent_limped", False),
        "facing_limp": preflop.get("facing_limp", False),
        "hero_iso_raised": preflop.get("hero_iso_raised", False),
        "hero_3bet": preflop.get("hero_3bet", False),
        "facing_open_size_bb": preflop.get("facing_open_size_bb"),

        # Postflop
        "flop_action": flop.get("hero_action"),
        "flop_bet_pct": flop.get("hero_bet_pct"),
        "facing_oversize_cbet": flop.get("facing_oversize_cbet", False),
        "facing_donk_bet": flop.get("facing_donk_bet", False),
        "turn_action": turn.get("hero_action"),
        "turn_bet_pct": turn.get("hero_bet_pct"),
        "river_action": river.get("hero_action"),
        "river_bet_pct": river.get("hero_bet_pct"),

        # Result
        "pot_size_bb": round(preflop["pot"] / big_blind, 1),
        "result_bb": result_bb,
    }


# ── Helpers ────────────────────────────────────────────────────────────────────

def _detect_position(text: str, hero: str, seat_map: dict) -> str:
    """Detect hero's position relative to the button."""
    btn_m = BTN_RE.search(text)
    if not btn_m:
        return "UNKNOWN"

    btn_seat = int(btn_m.group(1))
    seat_nums = sorted(seat_map.keys())
    seat_names = [seat_map[s][0] for s in seat_nums]

    try:
        hero_idx = seat_names.index(hero)
    except ValueError:
        return "UNKNOWN"

    btn_idx = seat_nums.index(btn_seat) if btn_seat in seat_nums else -1
    if btn_idx == -1:
        return "UNKNOWN"

    n = len(seat_names)
    rel = (hero_idx - btn_idx) % n
    pos_map = {0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "MP", 5: "CO"}
    if n == 2:
        pos_map = {0: "BTN/SB", 1: "BB"}
    elif n == 3:
        pos_map = {0: "BTN", 1: "SB", 2: "BB"}
    elif n >= 7:
        pos_map = {0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "UTG+1", 5: "MP", 6: "CO"}

    return pos_map.get(rel, f"MP{rel}")


def _split_streets(hand_text: str) -> dict:
    """Split hand text into per-street sections."""
    markers = list(STREET_MARKER_RE.finditer(hand_text))
    sections = {}
    _normalize = {"show down": "showdown", "show_down": "showdown"}
    for i, m in enumerate(markers):
        street = m.group(1).lower().replace(" ", "_")
        street = _normalize.get(street, street)
        start = m.end()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(hand_text)
        sections[street] = hand_text[start:end]
    return sections


def _parse_preflop(
    preflop_text: str,
    hero: str,
    big_blind: int,
    sb_player: Optional[str],
    sb_amount: int,
    bb_player: Optional[str],
    bb_amount: int,
    antes: dict,
) -> dict:
    """
    Parse the preflop section (after *** HOLE CARDS ***).
    Returns preflop action flags and pot size going into the flop.
    """
    ante_total = sum(antes.values())
    pot = ante_total + sb_amount + bb_amount

    # Track each player's chip commitment this street (excluding antes)
    committed: dict[str, int] = {}
    if sb_player:
        committed[sb_player] = sb_amount
    if bb_player:
        committed[bb_player] = bb_amount

    current_bet = bb_amount   # price to call
    has_raise = False
    has_limp = False          # someone called BB before any raise

    hero_acted = False
    hero_first_action = None
    hero_raise_bb = None
    hero_iso_raised = False
    hero_3bet = False
    opponent_limped = False
    facing_limp = False       # limp(s) exist before hero acts, no raise
    facing_open_size_bb = None
    hero_invested = committed.get(hero, 0)  # already committed (blind/ante-related)
    hero_street = "preflop"

    for m in ACTION_LINE_RE.finditer(preflop_text):
        player = m.group(1)
        action = m.group(2)
        amount = _n(m.group(3)) if m.group(3) else 0
        to_total = _n(m.group(4)) if m.group(4) else 0

        if action == "folds":
            continue

        if player != hero:
            prev = committed.get(player, 0)
            if action == "calls":
                # Amount = additional chips
                if not has_raise and amount == bb_amount:
                    # LIMP: calling the BB when no one has raised
                    has_limp = True
                    opponent_limped = True
                    if not hero_acted:
                        facing_limp = True
                committed[player] = prev + amount
                pot += amount

            elif action == "raises":
                total = to_total if to_total else (prev + amount)
                added = total - prev
                pot += added
                committed[player] = total
                if not has_raise:
                    # Open raise by opponent (before hero acts)
                    has_raise = True
                    if not hero_acted:
                        facing_open_size_bb = round(total / big_blind, 1)
                current_bet = total

            elif action == "bets":
                # Edge case: shouldn't happen preflop but handle
                pot += amount
                committed[player] = prev + amount

        else:
            # Hero's action
            hero_acted = True
            prev = committed.get(hero, 0)

            if action == "raises":
                total = to_total if to_total else (prev + amount)
                added = total - prev
                pot += added
                committed[hero] = total
                hero_invested += added
                if hero_first_action is None:
                    hero_first_action = "raise"
                    hero_raise_bb = round(total / big_blind, 1)
                if has_raise:
                    hero_3bet = True
                elif has_limp:
                    hero_iso_raised = True
                has_raise = True
                current_bet = total

            elif action == "calls":
                pot += amount
                committed[hero] = prev + amount
                hero_invested += amount
                if hero_first_action is None:
                    hero_first_action = "call"

            elif action == "checks":
                if hero_first_action is None:
                    hero_first_action = "check"

            elif action == "folds":
                if hero_first_action is None:
                    hero_first_action = "fold"

    # Subtract uncalled bets
    for um in UNCALLED_RE.finditer(preflop_text):
        pot -= _n(um.group(1))

    return {
        "pot": max(pot, 0),
        "hero_first_action": hero_first_action or "fold",
        "hero_raise_bb": hero_raise_bb,
        "hero_invested": hero_invested,
        "hero_street": "preflop",
        "opponent_limped": opponent_limped,
        "facing_limp": facing_limp and not has_raise,
        "hero_iso_raised": hero_iso_raised,
        "hero_3bet": hero_3bet,
        "facing_open_size_bb": facing_open_size_bb,
    }


def _parse_postflop_street(
    street_text: str,
    hero: str,
    pot_before: int,
    big_blind: int,
    hero_was_aggressor: bool = False,
    hero_ip: bool = False,
) -> dict:
    """
    Parse a single postflop street (flop/turn/river).
    Returns hero action, bet%, and opponent pattern flags.
    """
    if not street_text.strip():
        return {"hero_action": None, "hero_bet_pct": None, "pot_after": pot_before,
                "facing_oversize_cbet": False, "facing_donk_bet": False}

    pot = pot_before
    hero_action = None
    hero_bet_pct = None
    facing_oversize_cbet = False
    facing_donk_bet = False
    first_action_seen = False
    hero_invested = 0
    committed: dict[str, int] = {}

    for m in ACTION_LINE_RE.finditer(street_text):
        player = m.group(1)
        action = m.group(2)
        amount = _n(m.group(3)) if m.group(3) else 0
        to_total = _n(m.group(4)) if m.group(4) else 0

        if player == hero:
            if action == "bets":
                hero_action = "bet"
                hero_bet_pct = round(amount / pot * 100) if pot > 0 else None
                pot += amount
                committed[hero] = committed.get(hero, 0) + amount
                hero_invested += amount

            elif action == "raises":
                total = to_total if to_total else amount
                prev = committed.get(hero, 0)
                added = total - prev
                hero_action = "raise"
                hero_bet_pct = round(total / pot * 100) if pot > 0 else None
                pot += added
                committed[hero] = total
                hero_invested += added

            elif action == "calls":
                hero_action = "call"
                pot += amount
                committed[hero] = committed.get(hero, 0) + amount
                hero_invested += amount

            elif action == "checks":
                if hero_action is None:
                    hero_action = "check"

            elif action == "folds":
                if hero_action is None:
                    hero_action = "fold"

        else:
            # Opponent action
            if action == "bets":
                if not first_action_seen:
                    # First action on this street is an opponent bet
                    bet_pct = round(amount / pot * 100) if pot > 0 else 0
                    if bet_pct > 75:
                        facing_oversize_cbet = True
                    # Donk bet: opponent leads when hero was aggressor (or IP player leads OOP)
                    if hero_was_aggressor or (not hero_ip):
                        facing_donk_bet = True
                pot += amount
                committed[player] = committed.get(player, 0) + amount

            elif action == "raises":
                total = to_total if to_total else amount
                prev = committed.get(player, 0)
                added = total - prev
                pot += added
                committed[player] = total

            elif action == "calls":
                pot += amount
                committed[player] = committed.get(player, 0) + amount

        if action != "folds":
            first_action_seen = True

    # Subtract uncalled bets
    for um in UNCALLED_RE.finditer(street_text):
        pot -= _n(um.group(1))

    return {
        "hero_action": hero_action,
        "hero_bet_pct": hero_bet_pct,
        "pot_after": max(pot, 0),
        "hero_invested": hero_invested,
        "facing_oversize_cbet": facing_oversize_cbet,
        "facing_donk_bet": facing_donk_bet,
    }


def _detect_result_bb(hand_text: str, hero: str, big_blind: int, hero_invested: int) -> float:
    """
    Compute hero's net result in BBs.
    Chips collected minus chips invested.
    """
    collected = 0
    for name, amount in RESULT_RE.findall(hand_text):
        if name == hero:
            collected += _n(amount)
    net_chips = collected - hero_invested
    return round(net_chips / big_blind, 2)


def compute_session_context(hands: list[dict]) -> dict:
    """
    Aggregate opponent patterns across all hands in a tournament.
    Used as anonymous session context for AI hand review.
    """
    total = len(hands)
    if total == 0:
        return {}

    limp_hands = sum(1 for h in hands if h.get("opponent_limped"))
    oversize_open_hands = sum(
        1 for h in hands
        if (h.get("facing_open_size_bb") or 0) >= 4.0
    )
    oversize_cbet_hands = sum(1 for h in hands if h.get("facing_oversize_cbet"))
    donk_bet_hands = sum(1 for h in hands if h.get("facing_donk_bet"))

    return {
        "total_hands": total,
        "opponent_limp_count": limp_hands,
        "opponent_limp_pct": round(limp_hands / total * 100, 1),
        "oversize_open_count": oversize_open_hands,
        "oversize_open_pct": round(oversize_open_hands / total * 100, 1),
        "oversize_cbet_count": oversize_cbet_hands,
        "oversize_cbet_pct": round(oversize_cbet_hands / total * 100, 1),
        "donk_bet_count": donk_bet_hands,
        "donk_bet_pct": round(donk_bet_hands / total * 100, 1),
        # Bingo play: opponents going all-in preflop relative to stack depth
        # Approximated by oversize opens (≥10BB) as chaotic play indicator
        "bingo_play_index": round(
            sum(1 for h in hands if (h.get("facing_open_size_bb") or 0) >= 10) / total * 100, 1
        ),
    }
