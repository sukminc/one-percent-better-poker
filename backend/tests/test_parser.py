from app.parser import parse_filename, split_hands, parse_hand


# ── parse_filename ─────────────────────────────────────────────────────────────

def test_parse_filename_basic():
    result = parse_filename("GG20260102-0122 - #19 26 The Year Begins.txt")
    assert result["gg_id"] == "GG20260102-0122"
    assert "Year Begins" in result["name"]
    assert result["date"].year == 2026


def test_parse_filename_bounty():
    result = parse_filename("GG20260103-0233 - Mini Friday Night Fight 25 [Bounty 6-Max].txt")
    assert result["gg_id"] == "GG20260103-0233"
    assert result["bounty"] > 0
    assert "Bounty" in result["format"]


def test_parse_filename_no_match_returns_fallback():
    result = parse_filename("notavalidfile.txt")
    assert result["gg_id"] == "notavalidfile"
    assert result["name"] == "notavalidfile"


def test_parse_filename_standard_format():
    result = parse_filename("GG20260115-1800 - Regular 50.txt")
    assert result["format"] == "Standard"
    assert result["bounty"] == 0.0


def test_parse_filename_turbo_format():
    result = parse_filename("GG20260115-1800 - Turbo 50.txt")
    assert "Turbo" in result["format"]


def test_parse_filename_6max_format():
    result = parse_filename("GG20260115-1800 - Sprint 50 [6-Max].txt")
    assert "6-Max" in result["format"]


# ── split_hands ────────────────────────────────────────────────────────────────

def test_split_hands_empty():
    assert split_hands("") == []


def test_split_hands_single():
    text = """Poker Hand #RC1234-56789: Tournament #999, $1/$2 No Limit Hold'em - 2026/01/02 01:22:00
Seat 1: Hero (5000 in chips)
*** HOLE CARDS ***
Dealt to Hero [Ah Kd]
Hero: folds
*** SUMMARY ***
"""
    blocks = split_hands(text)
    assert len(blocks) == 1


def test_split_hands_multiple():
    hand = """Poker Hand #RC1234-00001: Tournament #999, $1/$2 No Limit Hold'em - 2026/01/02 01:22:00
Seat 1: Hero (5000 in chips)
*** HOLE CARDS ***
Dealt to Hero [Ah Kd]
Hero: folds
*** SUMMARY ***
"""
    hand2 = """Poker Hand #RC1234-00002: Tournament #999, $1/$2 No Limit Hold'em - 2026/01/02 01:23:00
Seat 1: Hero (4800 in chips)
*** HOLE CARDS ***
Dealt to Hero [Th Td]
Hero: raises $200 to $400
*** SUMMARY ***
Hero collected $400
"""
    blocks = split_hands(hand + "\n" + hand2)
    assert len(blocks) == 2


def test_split_hands_ignores_leading_garbage():
    text = "some preamble text\nPoker Hand #RC99-001: Tournament #1, $1/$2 No Limit Hold'em - 2026/01/01 00:00:00\nSeat 1: Hero (1000 in chips)\n*** SUMMARY ***\n"
    blocks = split_hands(text)
    assert len(blocks) == 1
    assert blocks[0].startswith("Poker Hand #")


# ── parse_hand ─────────────────────────────────────────────────────────────────

HAND_TEMPLATE = """Poker Hand #RC1234-{num}: Tournament #999, Hold'em No Limit - 2026/01/02 01:22:00
Table '999 1' {seats}-max
Seat #1 is the button
Level1(1/1)
{seat_lines}
*** HOLE CARDS ***
Dealt to {hero} [Ah Kd]
{actions}
*** SUMMARY ***
{summary}
"""


def _make_hand(num="56789", seats=2, seat_names=None, hero="Hero",
               actions="Villain: raises 200 to 400\nHero: folds",
               summary="Villain collected 200"):
    if seat_names is None:
        seat_names = ["Hero", "Villain"][:seats]
    seat_lines = "\n".join(
        f"Seat {i+1}: {name} ({5000 - i*500} in chips)"
        for i, name in enumerate(seat_names)
    )
    return HAND_TEMPLATE.format(
        num=num, seats=seats, seat_lines=seat_lines,
        hero=hero, actions=actions, summary=summary,
    )


def test_parse_hand_basic():
    text = _make_hand()
    hand = parse_hand(text, hero_name="Hero")
    assert hand is not None
    assert hand["hero_name"] == "Hero"
    assert hand["action"] == "fold"
    assert hand["action_street"] == "preflop"


def test_parse_hand_returns_none_without_hero():
    text = """Poker Hand #RC9999-00001: Tournament #999, $1/$2 No Limit Hold'em - 2026/01/02 00:00:00
Seat 1: Villain (5000 in chips)
*** HOLE CARDS ***
Villain: folds
*** SUMMARY ***
"""
    # No "Dealt to" and no hero_name provided
    hand = parse_hand(text, hero_name=None)
    assert hand is None


def test_parse_hand_returns_none_for_invalid_block():
    hand = parse_hand("not a hand history at all", hero_name="Hero")
    assert hand is None


def test_parse_hand_call_action():
    actions = "Villain: raises 200 to 400\nHero: calls 400"
    hand = parse_hand(_make_hand(actions=actions), hero_name="Hero")
    assert hand["action"] == "call"


def test_parse_hand_raise_action():
    actions = "Hero: raises 200 to 400"
    hand = parse_hand(_make_hand(actions=actions), hero_name="Hero")
    assert hand["action"] == "raise"


def test_parse_hand_check_action():
    actions = "Hero: checks"
    hand = parse_hand(_make_hand(actions=actions), hero_name="Hero")
    assert hand["action"] == "check"


def test_parse_hand_flop_action():
    actions = (
        "Villain: raises 200 to 400\n"
        "Hero: calls 400\n"
        "*** FLOP *** [Ac 2d 7h]\n"
        "Hero: checks\n"
        "Villain: bets 300\n"
        "Hero: folds"
    )
    hand = parse_hand(_make_hand(actions=actions), hero_name="Hero")
    # Hero's first action is preflop call
    assert hand["action"] == "call"
    assert hand["action_street"] == "preflop"


def test_parse_hand_hero_first_action_is_postflop():
    # Hero never acts preflop (e.g. checks BB option) → first action is on flop
    actions = (
        "Villain: raises 200 to 400\n"
        "*** FLOP *** [Ac 2d 7h]\n"
        "Hero: bets 300"
    )
    hand = parse_hand(_make_hand(actions=actions), hero_name="Hero")
    assert hand["action"] == "bet"
    assert hand["action_street"] == "flop"


def test_parse_hand_hero_wins():
    actions = "Villain: folds"
    summary = "Hero collected $400"
    hand = parse_hand(_make_hand(actions=actions, summary=summary), hero_name="Hero")
    assert hand["result_bb"] == 400.0


def test_parse_hand_hero_loses():
    # Hero folds; villain collects — hero result is 0 (no collect line for hero)
    hand = parse_hand(_make_hand(), hero_name="Hero")
    assert hand["result_bb"] == 0.0


def test_parse_hand_stack_detected():
    hand = parse_hand(_make_hand(), hero_name="Hero")
    assert hand["stack_bb"] == 5000.0


def test_parse_hand_number_captured():
    hand = parse_hand(_make_hand(num="ABCD-12345"), hero_name="Hero")
    assert hand["hand_number"] == "RC1234-ABCD-12345"


def test_parse_hand_position_btn_headsup():
    # 2-player, button is #1, Hero is seat 1 → BTN/SB
    hand = parse_hand(_make_hand(seats=2, seat_names=["Hero", "Villain"]), hero_name="Hero")
    assert hand["position"] == "BTN/SB"


def test_parse_hand_position_bb_headsup():
    # 2-player, button is #1, Hero is seat 2 → BB
    hand = parse_hand(_make_hand(seats=2, seat_names=["Villain", "Hero"]), hero_name="Hero")
    assert hand["position"] == "BB"


def test_parse_hand_position_sb():
    # 3-player, button is #1 (seat 1), Hero is seat 2 → SB (rel=1)
    hand = parse_hand(
        _make_hand(seats=3, seat_names=["Btn", "Hero", "Villain"]),
        hero_name="Hero",
    )
    assert hand["position"] == "SB"


def test_parse_hand_position_bb():
    # 3-player, button is #1 (seat 1), Hero is seat 3 → BB (rel=2)
    hand = parse_hand(
        _make_hand(seats=3, seat_names=["Btn", "SbPlayer", "Hero"]),
        hero_name="Hero",
    )
    assert hand["position"] == "BB"


# ── Donk bet detection ─────────────────────────────────────────────────────────

def test_donk_bet_true_when_hero_raised_preflop_and_opponent_leads_flop():
    """Opponent leads into hero who was preflop aggressor = donk bet."""
    # Hero is BTN (IP), raises preflop. BB calls. BB donks the flop.
    actions = (
        "Hero: raises 200 to 400\n"
        "Villain: calls 400\n"
        "*** FLOP *** [Ac 2d 7h]\n"
        "Villain: bets 300\n"
        "Hero: folds"
    )
    hand = parse_hand(_make_hand(actions=actions), hero_name="Hero")
    assert hand["facing_donk_bet"] is True


def test_donk_bet_false_when_hero_called_preflop_and_opponent_cbets():
    """Opponent c-bets after being the preflop raiser = NOT a donk bet."""
    # 3-seat: Btn(seat1), Villain(seat2/SB), Hero(seat3/BB)
    # Hero is BB (OOP), calls Villain's raise. Villain (IP) c-bets flop.
    actions = (
        "Villain: raises 200 to 400\n"
        "Hero: calls 400\n"
        "*** FLOP *** [Ac 2d 7h]\n"
        "Villain: bets 300\n"
        "Hero: folds"
    )
    hand = parse_hand(
        _make_hand(seats=3, seat_names=["Btn", "Villain", "Hero"], actions=actions,
                   summary="Villain collected 700"),
        hero_name="Hero",
    )
    assert hand["facing_donk_bet"] is False


def test_donk_bet_flop_action_captured():
    """When facing a real donk bet, hero's flop response is recorded."""
    actions = (
        "Hero: raises 200 to 400\n"
        "Villain: calls 400\n"
        "*** FLOP *** [Ac 2d 7h]\n"
        "Villain: bets 300\n"
        "Hero: calls 300"
    )
    hand = parse_hand(_make_hand(actions=actions), hero_name="Hero")
    assert hand["facing_donk_bet"] is True
    assert hand["flop_action"] == "call"


def test_parse_hand_position_utg():
    # 4-player, button is #1, Hero is seat 4 → UTG (rel=3)
    hand = parse_hand(
        _make_hand(seats=4, seat_names=["Btn", "SbPlayer", "BbPlayer", "Hero"]),
        hero_name="Hero",
    )
    assert hand["position"] == "UTG"


# ── Opponent sizing inconsistency (limp vs raise tell) ─────────────────────────

from app.parser import compute_session_context


def _make_parsed_hand(opener_name=None, opener_size_bb=None, limper_names=None):
    """Minimal parsed hand dict for compute_session_context tests."""
    return {
        "hand_number": f"HN-{id(object())}",
        "opponent_limped": bool(limper_names),
        "facing_open_size_bb": opener_size_bb,
        "facing_oversize_cbet": False,
        "facing_donk_bet": False,
        "_limper_names": limper_names or [],
        "_opener_name": opener_name,
    }


def test_session_context_inconsistent_sizer_limp_then_raise():
    """PlayerA limps in hand 1, raises big in hand 2 → flagged as inconsistent."""
    hands = [
        _make_parsed_hand(limper_names=["PlayerA"]),           # hand 1: PlayerA limps
        _make_parsed_hand(opener_name="PlayerA", opener_size_bb=6.0),  # hand 2: PlayerA raises 6x
    ]
    ctx = compute_session_context(hands)
    assert ctx["inconsistent_sizer_count"] >= 1
    assert ctx["inconsistent_sizer_pct"] > 0


def test_session_context_inconsistent_sizer_raise_then_limp():
    """PlayerB raises consistently, then suddenly limps → flagged."""
    hands = [
        _make_parsed_hand(opener_name="PlayerB", opener_size_bb=4.0),
        _make_parsed_hand(opener_name="PlayerB", opener_size_bb=4.0),
        _make_parsed_hand(limper_names=["PlayerB"]),  # suddenly limps
    ]
    ctx = compute_session_context(hands)
    assert ctx["inconsistent_sizer_count"] >= 1


def test_session_context_consistent_raiser_not_flagged():
    """PlayerC always raises 3BB → NOT flagged as inconsistent."""
    hands = [
        _make_parsed_hand(opener_name="PlayerC", opener_size_bb=3.0),
        _make_parsed_hand(opener_name="PlayerC", opener_size_bb=3.0),
        _make_parsed_hand(opener_name="PlayerC", opener_size_bb=3.5),
    ]
    ctx = compute_session_context(hands)
    assert ctx["inconsistent_sizer_count"] == 0


def test_session_context_consistent_limper_not_flagged():
    """PlayerD always limps → NOT flagged (that's just their style, readable but consistent)."""
    hands = [
        _make_parsed_hand(limper_names=["PlayerD"]),
        _make_parsed_hand(limper_names=["PlayerD"]),
    ]
    ctx = compute_session_context(hands)
    assert ctx["inconsistent_sizer_count"] == 0
