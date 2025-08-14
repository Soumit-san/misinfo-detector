# app/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.models.request_models import CheckRequest
from app.models.response_models import ClaimVerification
from app.services.claim_extractor import extract_claims
from app.services.fact_checker import fact_check_claim
from app.services.llm_verifier import verify_with_llm
from app.database.db import init_db, close_db
from app.database.queries import save_history, get_history, get_history_item, delete_history

app = FastAPI(title="Misinfo Detector API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

@app.get("/", tags=["Health"])
async def root():
    return {"message": "Misinfo Detector API is running 🚀"}

@app.post("/check", response_model=List[ClaimVerification], tags=["Verification"])
async def check(req: CheckRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")

    claims = await extract_claims(text)
    results = []

    for c in claims:
        fc = await fact_check_claim(c)                 # news + factchecks + wiki
        llm_out = await verify_with_llm(c, fc)         # verdict, confidence, explanation

        entry = {
            "claim": c,  # ✅ renamed from text → claim
            "verdict": llm_out.get("verdict"),
            "confidence": llm_out.get("confidence"),
            "explanation": llm_out.get("explanation"),
            "news_sources": fc.get("news_sources", []),
            "factcheck_sources": fc.get("factcheck_sources", []),
        }
        record_id = await save_history({
            "text": c,  # still store as text in DB
            "verdict": entry["verdict"],
            "confidence": entry["confidence"],
            "explanation": entry["explanation"],
            "sources": fc
        })
        entry["id"] = record_id
        results.append(entry)

    return results


@app.get("/history", response_model=List[ClaimVerification], tags=["History"])
async def history(limit: int = Query(50, ge=1, le=500)):
    rows = await get_history(limit)
    return [
        {
            "claim": r["text"],
            "verdict": r["verdict"],
            "confidence": r["confidence"],
            "explanation": r["explanation"],

            # Handle if sources is None, list, or dict
            "news_sources": (r.get("sources") or {}).get("news_sources", []) 
                            if isinstance(r.get("sources"), dict)
                            else (r.get("sources") if isinstance(r.get("sources"), list) else []),

            "factcheck_sources": (r.get("sources") or {}).get("factcheck_sources", []) 
                                  if isinstance(r.get("sources"), dict)
                                  else [],

            "id": r["id"],
            "created_at": r["created_at"].isoformat() if r.get("created_at") else None
        }
        for r in rows
    ]


@app.get("/history/{record_id}", response_model=ClaimVerification, tags=["History"])
async def history_item(record_id: int):
    r = await get_history_item(record_id)
    if not r:
        raise HTTPException(status_code=404, detail="Record not found")

    return {
        "claim": r["text"],
        "verdict": r["verdict"],
        "confidence": r["confidence"],
        "explanation": r["explanation"],

        "news_sources": (r.get("sources") or {}).get("news_sources", []) 
                        if isinstance(r.get("sources"), dict)
                        else (r.get("sources") if isinstance(r.get("sources"), list) else []),

        "factcheck_sources": (r.get("sources") or {}).get("factcheck_sources", []) 
                              if isinstance(r.get("sources"), dict)
                              else [],

        "id": r["id"],
        "created_at": r["created_at"].isoformat() if r.get("created_at") else None
    }
