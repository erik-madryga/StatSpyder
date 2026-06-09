"""Helpers to ingest parsed PlayerSeason objects into the database (Supabase).

Provides an upsert function that prefers Postgres `ON CONFLICT` for efficient
upserts and falls back to a simple query-update/insert when that isn't
available.
"""
from typing import Iterable

from sqlalchemy.orm import Session

from models import PlayerSeasonDB
from .crawler import PlayerSeason


def create_tables_if_missing(engine) -> None:
    """Create tables for registered models (safe to call repeatedly)."""
    # import here to avoid circular imports at module import time
    from database import Base

    Base.metadata.create_all(bind=engine)


def upsert_player_seasons(db: Session, seasons: Iterable[PlayerSeason]) -> int:
    """Upsert a sequence of `PlayerSeason` Pydantic objects into the DB.

    Uses Postgres `INSERT ... ON CONFLICT DO UPDATE` when available and
    falls back to a read-then-insert/update loop on error. Returns the number
    of rows processed (inserted or updated).
    """
    processed = 0

    for s in seasons:
        data = s.model_dump() if hasattr(s, "model_dump") else s.dict()
        # Remove any pydantic-only keys if present
        data.pop("id", None)

        try:
            # Prefer Postgres upsert for speed/atomicity
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            stmt = pg_insert(PlayerSeasonDB).values(**data)
            update_cols = {k: getattr(stmt.excluded, k) for k in data.keys()}
            stmt = stmt.on_conflict_do_update(index_elements=["year", "team", "pos"], set_=update_cols)
            db.execute(stmt)
            processed += 1
        except Exception:
            # Fallback: simple query-and-update/insert (works for SQLite and others)
            existing = db.query(PlayerSeasonDB).filter_by(year=data.get("year"), team=data.get("team"), pos=data.get("pos")).first()
            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
            else:
                db.add(PlayerSeasonDB(**data))
            processed += 1

    db.commit()
    return processed
