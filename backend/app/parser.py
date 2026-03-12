"""
GGPoker hand history parser.
Parses raw .txt files exported from GGPoker into structured dicts
ready for DB insertion.
"""

import re
from datetime import datetime
from typing import Optional
from pathlib import Path


# ── Filename patterns ──────────────────────────────────────────────────────────
# "GG20260102-0122 - #19 26 The Year Begins.txt"
FILENAME_RE = re.compile(
    r"(GG\d{8}-\d{4})"           # GG ID
    r"\s*-\s*"
    r"(.+?)(?:\.txt)?$"           # tournament name
)

BUY_IN_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:Buy-?[Ii]n|buy-?in|\$)", re.IGNORECASE)
BOUNTY_RE = re.compile(r"\[Bounty", re.IGNORECASE)

# ── Hand-level patterns ────────────────────────────────────────────────────────
HAND_START_RE = re.compile(
    r"Poker Hand #([\w-]+):\s+Tournament[^,]+,\s+\$[\d.]+/\$[\d.]+.*?-\s+(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"
)
SEAT_RE = re.compile(r"Seat \d+: (\S+) \((\d+) in chips\)")
HERO_RE = re.compile(r"Dealt to (\S+)")
POSITION_RE = re.compile(r"(\S+): posts (small|big) blind")
BTN_RE = re.compile(r"#(\d+) is the button")

# Action patterns per street
STREET_RE = re.compile(r"\*\*\* (HOLE CARDS|FLOP|TURN|RIVER|SHOW DOWN|SUMMARY) \*\*\*")
ACTION_RE = re.compile(
    r"(\S+): (folds|checks|calls|raises|bets)(?: \$?([\d.]+))?"
)
RESULT_RE = re.compile(r"(\S+) collected \$?([\d.]+)")


def parse_filename(filename: str) -> dict:
    """Extract GG ID, name, buy-in, format from filename."""
    stem = Path(filename).stem
    m = FILENAME_RE.match(stem)
    if not m:
        return {"gg_id": stem, "name": stem}

    gg_id = m.group(1)
    name = m.group(2).strip()

    # Parse date from GG ID: GG20260102-0122
    date_str = gg_id[2:10]  # "20260102"
    try:
        date = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        date = datetime.utcnow()

    # Rough buy-in extraction from name
    buy_in_m = re.search(r"(?:^|\s)(\d+(?:\.\d+)?)\s", name)
    buy_in = float(buy_in_m.group(1)) if buy_in_m else 0.0

    bounty = buy_in * 0.5 if BOUNTY_RE.search(name) else 0.0

    # Format tags
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


def parse_hand(hand_text: str, hero_name: Optional[str] = None) -> Optional[dict]:
    """
    Parse a single hand block into a dict.
    Returns None if the block can't be parsed.
    """
    hm = HAND_START_RE.search(hand_text)
    if not hm:
        return None

    hand_number = hm.group(1)

    # Detect hero
    hero_m = HERO_RE.search(hand_text)
    hero = hero_m.group(1) if hero_m else hero_name

    if not hero:
        return None

    # Position detection (simplified: BTN/SB/BB from blind posts)
    position = _detect_position(hand_text, hero)

    # Stack
    stack_bb = _detect_stack(hand_text, hero)

    # Primary action (preflop)
    action, street = _detect_primary_action(hand_text, hero)

    # Result
    result_bb = _detect_result(hand_text, hero)

    return {
        "hand_number": hand_number,
        "hero_name": hero,
        "position": position,
        "stack_bb": stack_bb,
        "action_street": street,
        "action": action,
        "result_bb": result_bb,
    }


def split_hands(raw_text: str) -> list[str]:
    """Split a full hand history file into individual hand blocks."""
    blocks = re.split(r"(?=Poker Hand #)", raw_text)
    return [b.strip() for b in blocks if b.strip().startswith("Poker Hand #")]


# ── Helpers ────────────────────────────────────────────────────────────────────

def _detect_position(text: str, hero: str) -> str:
    """Rough positional detection."""
    btn_m = BTN_RE.search(text)
    seats = SEAT_RE.findall(text)
    if not seats:
        return "UNKNOWN"

    seat_names = [s[0] for s in seats]
    try:
        hero_idx = seat_names.index(hero)
    except ValueError:
        return "UNKNOWN"

    n = len(seat_names)
    if btn_m:
        btn_seat = int(btn_m.group(1)) - 1  # 0-indexed
        rel = (hero_idx - btn_seat) % n
        pos_map = {0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "MP", 5: "CO"}
        if n == 2:
            pos_map = {0: "BTN/SB", 1: "BB"}
        return pos_map.get(rel, f"MP{rel}")

    return "UNKNOWN"


def _detect_stack(text: str, hero: str) -> float:
    """Return hero starting stack. We approximate in chips (not BBs without blind info)."""
    for name, chips in SEAT_RE.findall(text):
        if name == hero:
            return float(chips)
    return 0.0


def _detect_primary_action(text: str, hero: str) -> tuple[str, str]:
    """Return (action, street) for hero's first significant action."""
    current_street = "preflop"
    for line in text.splitlines():
        sm = STREET_RE.search(line)
        if sm:
            s = sm.group(1).lower()
            if s == "flop":
                current_street = "flop"
            elif s == "turn":
                current_street = "turn"
            elif s == "river":
                current_street = "river"
            elif s in ("show down", "summary"):
                break

        am = ACTION_RE.match(line.strip())
        if am and am.group(1) == hero:
            return am.group(2), current_street

    return "fold", "preflop"


def _detect_result(text: str, hero: str) -> float:
    """Return net chips won/lost by hero from SUMMARY block."""
    for name, amount in RESULT_RE.findall(text):
        if name == hero:
            return float(amount)
    return 0.0
