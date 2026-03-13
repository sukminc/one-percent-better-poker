from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from .db import Base


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    gg_id = Column(String, unique=True, index=True)          # e.g. "GG20260102-0122"
    name = Column(String)
    buy_in = Column(Float, default=0.0)
    bounty = Column(Float, default=0.0)
    format = Column(String)                                   # e.g. "Bounty Turbo", "6-Max"
    date = Column(DateTime)
    finish_position = Column(Integer, nullable=True)
    total_players = Column(Integer, nullable=True)
    net_result = Column(Float, default=0.0)                   # USD P&L after buy-in
    raw_file = Column(Text, nullable=True)                    # raw hand history text
    session_context = Column(JSON, nullable=True)             # opponent pattern aggregates
    created_at = Column(DateTime, default=datetime.utcnow)

    hands = relationship("Hand", back_populates="tournament", cascade="all, delete-orphan")


class Hand(Base):
    __tablename__ = "hands"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), index=True)
    hand_number = Column(String, index=True)
    hero_name = Column(String)
    position = Column(String)                                 # BTN, CO, HJ, MP, UTG, BB, SB
    big_blind = Column(Float, nullable=True)                  # big blind chip value for this hand
    stack_bb = Column(Float)                                  # hero stack in BBs (properly computed)

    # ── Preflop ─────────────────────────────────────────────────────────────────
    action_street = Column(String)                            # street of hero's first action
    action = Column(String)                                   # hero's first action: fold/call/raise
    hero_raise_bb = Column(Float, nullable=True)              # hero's raise size in BBs
    opponent_limped = Column(Boolean, default=False)          # any opponent limped this hand
    facing_limp = Column(Boolean, default=False)              # hero faced a limp before acting
    hero_iso_raised = Column(Boolean, default=False)          # hero iso-raised vs a limp
    hero_3bet = Column(Boolean, default=False)                # hero 3-bet preflop
    facing_open_size_bb = Column(Float, nullable=True)        # open raise size hero faced (in BBs)

    # ── Postflop ─────────────────────────────────────────────────────────────────
    flop_action = Column(String, nullable=True)               # hero flop action
    flop_bet_pct = Column(Float, nullable=True)               # hero bet as % of pot (flop)
    facing_oversize_cbet = Column(Boolean, default=False)     # opponent c-bet > 75% pot (flop)
    facing_donk_bet = Column(Boolean, default=False)          # opponent led flop OOP
    turn_action = Column(String, nullable=True)               # hero turn action
    turn_bet_pct = Column(Float, nullable=True)
    river_action = Column(String, nullable=True)              # hero river action
    river_bet_pct = Column(Float, nullable=True)

    # ── Result ───────────────────────────────────────────────────────────────────
    pot_size_bb = Column(Float, nullable=True)                # pot at start of hand in BBs
    result_bb = Column(Float, nullable=True)                  # net +/- BBs for this hand
    created_at = Column(DateTime, default=datetime.utcnow)

    tournament = relationship("Tournament", back_populates="hands")
