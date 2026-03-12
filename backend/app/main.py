from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from .db import engine, get_db, Base
from . import models, analytics
from .parser import parse_filename, split_hands, parse_hand

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="onepercentbetter.poker API",
    description="GTO Defends. We Exploit.",
    version="0.1.0",
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

    # Upsert tournament
    existing = db.query(models.Tournament).filter_by(gg_id=meta["gg_id"]).first()
    if existing:
        tourney = existing
    else:
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

    # Parse hands
    hand_blocks = split_hands(raw)
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
        inserted += 1

    db.commit()
    return {
        "tournament": meta["gg_id"],
        "name": meta["name"],
        "hands_inserted": inserted,
        "hands_found": len(hand_blocks),
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
        }
        for t in rows
    ]


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


# ── Analytics ──────────────────────────────────────────────────────────────────

@app.get("/analytics/signals", summary="Top-level exploit edge signals")
def exploit_signals(hero_name: Optional[str] = None, db: Session = Depends(get_db)):
    return analytics.get_exploit_signals(db, hero_name)


@app.get("/analytics/positional", summary="Win-rate and action stats by position")
def positional_stats(hero_name: Optional[str] = None, db: Session = Depends(get_db)):
    df = analytics.get_positional_stats(db, hero_name)
    return df.to_dict(orient="records")


@app.get("/analytics/pnl", summary="Cumulative P&L over time")
def pnl_over_time(db: Session = Depends(get_db)):
    df = analytics.get_tournament_summary(db)
    if df.empty:
        return []
    return df[["gg_id", "date", "net_result", "cumulative_pnl"]].to_dict(orient="records")
