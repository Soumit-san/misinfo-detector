# app/database/queries.py
from typing import Any, Dict, List, Optional
from app.database.db import insert_history, fetch_all_history, fetch_history_by_id, delete_history_by_id

async def save_history(entry: Dict[str, Any]) -> int:
    return await insert_history(
        text=entry.get("text"),
        verdict=entry.get("verdict"),
        confidence=int(entry.get("confidence", 0)),
        explanation=entry.get("explanation", ""),
        sources=entry.get("sources", {})
    )

async def get_history(limit: int = 50) -> List[Dict]:
    return await fetch_all_history(limit)

async def get_history_item(record_id: int) -> Optional[Dict]:
    return await fetch_history_by_id(record_id)

async def delete_history(record_id: int) -> bool:
    return await delete_history_by_id(record_id)
