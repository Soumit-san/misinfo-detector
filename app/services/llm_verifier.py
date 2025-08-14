# app/services/llm_verifier.py
import json
import re
import asyncio
from typing import Dict, Any, Union
from app.config import settings
from groq import Groq

# Initialize Groq client
client = Groq(api_key=settings.groq_api_key)

def _build_sources_text(sources: Union[dict, list]) -> str:
    """Convert multiple lists of sources into a readable text block for LLM input."""
    if not sources:
        return "No sources found."

    if isinstance(sources, dict):
        combined = (
            sources.get("wikipedia", []) +
            sources.get("news_sources", []) +
            sources.get("factcheck_sources", [])
        )
    else:
        combined = sources

    if not combined:
        return "No sources found."

    parts = []
    for src in combined[:10]:  # limit to first 10
        title = src.get("title", "No Title")
        url = src.get("url", "No URL")
        snippet = src.get("snippet", "")
        parts.append(f"- {title} ({url}): {snippet}")

    return "\n".join(parts)

def _verify_with_llm_sync(claim: str, sources: Union[dict, list]) -> Dict[str, Any]:
    """Synchronous Groq API call."""
    sources_text = _build_sources_text(sources)
    prompt = f"""
You are a fact-check assistant. Given a claim and supporting sources, decide whether the claim is TRUE, FALSE, PARTIALLY TRUE, or UNVERIFIED.
Return a JSON object with exactly these keys: 
- verdict (one of TRUE/FALSE/PARTIALLY TRUE/UNVERIFIED)
- confidence (0-100 integer)
- explanation (one short paragraph).

Claim:
\"\"\"{claim}\"\"\"

Sources:
{sources_text}

Respond with JSON only.
"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=400
    )

    content = resp.choices[0].message.content.strip()

    # Parse JSON
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", content, re.S)
        if m:
            parsed = json.loads(m.group(0))
        else:
            parsed = {
                "verdict": "UNVERIFIED",
                "confidence": 50,
                "explanation": content
            }

    parsed["verdict"] = str(parsed.get("verdict", "UNVERIFIED")).upper()
    parsed["confidence"] = int(parsed.get("confidence", 50))
    parsed["explanation"] = str(parsed.get("explanation", ""))[:3000]
    return parsed

async def verify_with_llm(claim: str, sources: Union[dict, list]) -> Dict[str, Any]:
    """Async wrapper for LLM verification."""
    try:
        return await asyncio.to_thread(_verify_with_llm_sync, claim, sources)
    except Exception as e:
        return {
            "verdict": "UNVERIFIED",
            "confidence": 40,
            "explanation": f"LLM error: {e}"
        }
