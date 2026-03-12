"""
Analytics engine: aggregates hand data into session/positional stats
and computes exploit edge signals.
"""

from typing import Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from . import models


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


def get_positional_stats(db: Session, hero_name: Optional[str] = None) -> pd.DataFrame:
    """
    Aggregate hand-level data by position.
    Returns win-rate and action frequency per position.
    """
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
            vpip=("action", lambda x: (x != "folds").mean()),
            fold_rate=("action", lambda x: (x == "folds").mean()),
        )
        .reset_index()
    )
    stats["avg_result_bb"] = stats["avg_result_bb"].round(2)
    return stats


def get_exploit_signals(db: Session, hero_name: Optional[str] = None) -> dict:
    """
    Compute top-level exploit edge signals.
    Returns a dict with key metrics ready for the dashboard.
    """
    pos_stats = get_positional_stats(db, hero_name)
    tourney_df = get_tournament_summary(db)

    if pos_stats.empty or tourney_df.empty:
        return {
            "total_tournaments": 0,
            "total_pnl": 0.0,
            "avg_pnl_per_session": 0.0,
            "best_position": None,
            "worst_position": None,
            "overall_vpip": None,
            "roi_pct": None,
        }

    total_buy_in = tourney_df["buy_in"].sum()
    total_pnl = tourney_df["net_result"].sum()
    roi = (total_pnl / total_buy_in * 100) if total_buy_in > 0 else 0.0

    best = pos_stats.loc[pos_stats["avg_result_bb"].idxmax()]
    worst = pos_stats.loc[pos_stats["avg_result_bb"].idxmin()]

    overall_vpip = pos_stats["vpip"].mean() if not pos_stats.empty else None

    return {
        "total_tournaments": int(len(tourney_df)),
        "total_pnl": round(float(total_pnl), 2),
        "avg_pnl_per_session": round(float(tourney_df["net_result"].mean()), 2),
        "best_position": {"position": best["position"], "avg_bb": float(best["avg_result_bb"])},
        "worst_position": {"position": worst["position"], "avg_bb": float(worst["avg_result_bb"])},
        "overall_vpip": round(float(overall_vpip) * 100, 1) if overall_vpip is not None else None,
        "roi_pct": round(roi, 1),
    }
