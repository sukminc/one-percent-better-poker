from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from .db import engine, get_db, Base
from . import models, analytics
from .parser import parse_filename, split_hands, parse_hand, compute_session_context

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="onepercentbetter.poker API",
    description="GTO Defends. We Exploit.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://onepercentbetter.poker"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "onepercentbetter.poker"}


# ── Ingest ─────────────────────────────────────────────────────────────────────

@app.post("/ingest", summary="Upload a GGPoker hand history .txt file")
async def ingest_hand_history(
    file: UploadFile = File(...),
    hero_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt hand history files accepted.")

    raw = (await file.read()).decode("utf-8", errors="ignore")
    meta = parse_filename(file.filename)

    # Duplicate detection: same GG ID = same tournament file
    existing = db.query(models.Tournament).filter_by(gg_id=meta["gg_id"]).first()
    if existing:
        hand_count = db.query(models.Hand).filter_by(tournament_id=existing.id).count()
        return {
            "tournament": meta["gg_id"],
            "name": meta["name"],
            "already_exists": True,
            "hands_in_db": hand_count,
            "message": "Tournament already ingested. Delete and re-upload to refresh.",
        }

    # Create tournament record
    tourney = models.Tournament(
        gg_id=meta["gg_id"],
        name=meta["name"],
        buy_in=meta.get("buy_in", 0.0),
        bounty=meta.get("bounty", 0.0),
        format=meta.get("format", "Standard"),
        date=meta.get("date"),
        raw_file=raw,
    )
    db.add(tourney)
    db.flush()

    # Parse all hand blocks
    hand_blocks = split_hands(raw)
    parsed_hands = []
    inserted = 0

    for block in hand_blocks:
        h = parse_hand(block, hero_name)
        if not h:
            continue
        already = db.query(models.Hand).filter_by(hand_number=h["hand_number"]).first()
        if already:
            continue

        hand_row = models.Hand(tournament_id=tourney.id, **h)
        db.add(hand_row)
        parsed_hands.append(h)
        inserted += 1

    # Compute and store session context (opponent pattern aggregates)
    if parsed_hands:
        ctx = compute_session_context(parsed_hands)
        tourney.session_context = ctx

    db.commit()
    return {
        "tournament": meta["gg_id"],
        "name": meta["name"],
        "already_exists": False,
        "hands_inserted": inserted,
        "hands_found": len(hand_blocks),
        "session_context": tourney.session_context,
    }


# ── Tournaments ────────────────────────────────────────────────────────────────

@app.get("/tournaments", summary="List all ingested tournaments")
def list_tournaments(db: Session = Depends(get_db)):
    rows = db.query(models.Tournament).order_by(models.Tournament.date.desc()).all()
    return [
        {
            "id": t.id,
            "gg_id": t.gg_id,
            "name": t.name,
            "date": t.date,
            "buy_in": t.buy_in,
            "format": t.format,
            "net_result": t.net_result,
            "finish_position": t.finish_position,
            "session_context": t.session_context,
        }
        for t in rows
    ]


@app.get("/tournaments/{tournament_id}", summary="Get tournament details with hands")
def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    t = db.query(models.Tournament).filter_by(id=tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tournament not found.")
    hands = db.query(models.Hand).filter_by(tournament_id=tournament_id).all()
    return {
        "id": t.id,
        "gg_id": t.gg_id,
        "name": t.name,
        "date": t.date,
        "buy_in": t.buy_in,
        "format": t.format,
        "net_result": t.net_result,
        "finish_position": t.finish_position,
        "session_context": t.session_context,
        "hands": [_hand_summary(h) for h in hands],
    }


@app.patch("/tournaments/{tournament_id}", summary="Update finish position and result")
def update_tournament(
    tournament_id: int,
    finish_position: Optional[int] = None,
    total_players: Optional[int] = None,
    net_result: Optional[float] = None,
    db: Session = Depends(get_db),
):
    t = db.query(models.Tournament).filter_by(id=tournament_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tournament not found.")
    if finish_position is not None:
        t.finish_position = finish_position
    if total_players is not None:
        t.total_players = total_players
    if net_result is not None:
        t.net_result = net_result
    db.commit()
    return {"updated": tournament_id}


# ── Hands ──────────────────────────────────────────────────────────────────────

@app.get("/hands/{hand_id}", summary="Get a single hand with full detail")
def get_hand(hand_id: int, db: Session = Depends(get_db)):
    h = db.query(models.Hand).filter_by(id=hand_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hand not found.")
    t = db.query(models.Tournament).filter_by(id=h.tournament_id).first()
    return {
        **_hand_detail(h),
        "session_context": t.session_context if t else None,
    }


# ── Analytics ──────────────────────────────────────────────────────────────────

@app.get("/analytics/signals", summary="Exploit edge signals across all hands")
def exploit_signals(hero_name: Optional[str] = None, db: Session = Depends(get_db)):
    return analytics.get_exploit_signals(db, hero_name)


@app.get("/analytics/positional", summary="Win-rate and action stats by position")
def positional_stats(hero_name: Optional[str] = None, db: Session = Depends(get_db)):
    df = analytics.get_positional_stats(db, hero_name)
    if df.empty:
        return []
    return df.to_dict(orient="records")


@app.get("/analytics/pnl", summary="Cumulative P&L over time")
def pnl_over_time(db: Session = Depends(get_db)):
    df = analytics.get_tournament_summary(db)
    if df.empty:
        return []
    return df[["gg_id", "date", "net_result", "cumulative_pnl"]].to_dict(orient="records")


@app.get("/analytics/growth", summary="Exploit signal trends by week")
def growth_timeline(hero_name: Optional[str] = None, db: Session = Depends(get_db)):
    return analytics.get_growth_timeline(db, hero_name)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _hand_summary(h: models.Hand) -> dict:
    return {
        "id": h.id,
        "hand_number": h.hand_number,
        "position": h.position,
        "stack_bb": h.stack_bb,
        "action": h.action,
        "result_bb": h.result_bb,
        "flop_action": h.flop_action,
        "turn_action": h.turn_action,
        "river_action": h.river_action,
        "opponent_limped": h.opponent_limped,
        "hero_iso_raised": h.hero_iso_raised,
        "hero_3bet": h.hero_3bet,
        "facing_oversize_cbet": h.facing_oversize_cbet,
    }


def _hand_detail(h: models.Hand) -> dict:
    return {
        "id": h.id,
        "hand_number": h.hand_number,
        "position": h.position,
        "big_blind": h.big_blind,
        "stack_bb": h.stack_bb,
        "pot_size_bb": h.pot_size_bb,
        # Preflop
        "action": h.action,
        "hero_raise_bb": h.hero_raise_bb,
        "opponent_limped": h.opponent_limped,
        "facing_limp": h.facing_limp,
        "hero_iso_raised": h.hero_iso_raised,
        "hero_3bet": h.hero_3bet,
        "facing_open_size_bb": h.facing_open_size_bb,
        # Postflop
        "flop_action": h.flop_action,
        "flop_bet_pct": h.flop_bet_pct,
        "facing_oversize_cbet": h.facing_oversize_cbet,
        "facing_donk_bet": h.facing_donk_bet,
        "turn_action": h.turn_action,
        "turn_bet_pct": h.turn_bet_pct,
        "river_action": h.river_action,
        "river_bet_pct": h.river_bet_pct,
        # Result
        "result_bb": h.result_bb,
    }
