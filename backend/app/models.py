from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
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
    created_at = Column(DateTime, default=datetime.utcnow)

    hands = relationship("Hand", back_populates="tournament", cascade="all, delete-orphan")


class Hand(Base):
    __tablename__ = "hands"

    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), index=True)
    hand_number = Column(String, index=True)
    hero_name = Column(String)
    position = Column(String)                                 # BTN, CO, HJ, MP, UTG, BB, SB
    stack_bb = Column(Float)                                  # hero stack in BBs
    action_street = Column(String)                            # preflop / flop / turn / river
    action = Column(String)                                   # fold / call / raise / check
    pot_size_bb = Column(Float, nullable=True)
    bet_size_bb = Column(Float, nullable=True)
    result_bb = Column(Float, nullable=True)                  # +/- BB outcome for this hand
    created_at = Column(DateTime, default=datetime.utcnow)

    tournament = relationship("Tournament", back_populates="hands")
