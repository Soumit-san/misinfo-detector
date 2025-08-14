# app/models/request_models.py
from pydantic import BaseModel

class CheckRequest(BaseModel):
    text: str
