# app/database/db.py
import databases
from sqlalchemy import (
    MetaData, Table, Column, Integer, String, Text, DateTime
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import create_async_engine
from datetime import datetime, timezone
from typing import List, Optional
from app.config import settings
from sqlalchemy.sql import func

DATABASE_URL = settings.database_url

database = databases.Database(DATABASE_URL)
metadata = MetaData()

history = Table(
    "history",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("text", Text, nullable=False),
    Column("verdict", String(50)),
    Column("confidence", Integer),
    Column("explanation", Text),
    Column("sources", JSONB),
    Column("created_at", DateTime(timezone=True),  server_default=func.now())
)

async def init_db() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    await database.connect()

async def close_db() -> None:
    if database.is_connected:
        await database.disconnect()

async def insert_history(text: str, verdict: str, confidence: int, explanation: str, sources: Optional[dict] = None) -> int:
    query = history.insert().values(
        text=text,
        verdict=verdict,
        confidence=int(confidence),
        explanation=explanation,
        sources=sources or {},
       
    )
    record_id = await database.execute(query)
    return record_id

async def fetch_all_history(limit: int = 50) -> List[dict]:
    query = history.select().order_by(history.c.created_at.desc()).limit(limit)
    rows = await database.fetch_all(query)
    return [dict(r) for r in rows]

async def fetch_history_by_id(record_id: int) -> Optional[dict]:
    query = history.select().where(history.c.id == record_id)
    row = await database.fetch_one(query)
    return dict(row) if row else None

async def delete_history_by_id(record_id: int) -> bool:
    query = history.delete().where(history.c.id == record_id).returning(history.c.id)
    row = await database.execute(query)
    return bool(row)
