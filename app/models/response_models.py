# app/models/response_models.py
from pydantic import BaseModel
from typing import List, Optional

class Source(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None
    publisher: Optional[str] = None
    date: Optional[str] = None
    rating: Optional[str] = None

class ClaimVerification(BaseModel):
    claim: str
    verdict: str
    confidence: int
    explanation: str
    news_sources: List[Source] = []
    factcheck_sources: List[Source] = []
    id: Optional[int] = None
    created_at: Optional[str] = None
