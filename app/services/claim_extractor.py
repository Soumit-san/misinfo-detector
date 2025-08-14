# app/services/claim_extractor.py
from typing import List
import asyncio
from app.utils.text_cleaner import clean_text

# spaCy loaded lazily to avoid heavy import during tests/startup
_spacy_nlp = None

def _load_spacy():
    global _spacy_nlp
    if _spacy_nlp is None:
        import spacy
        try:
            _spacy_nlp = spacy.load("en_core_web_sm")
        except Exception:
            # If model missing, raise helpful message
            raise RuntimeError("spaCy model 'en_core_web_sm' not installed. Run: python -m spacy download en_core_web_sm")
    return _spacy_nlp

def _extract_claims_sync(text: str) -> List[str]:
    nlp = _load_spacy()
    doc = nlp(text)
    claims = []
    for sent in doc.sents:
        # heuristic: sentence longer than 6 words and contains a verb and a subject
        tokens = list(sent)
        if len(tokens) < 6:
            continue
        has_verb = any(tok.pos_ == "VERB" for tok in sent)
        has_nsubj = any(tok.dep_ in ("nsubj", "nsubjpass") for tok in sent)
        if has_verb and has_nsubj:
            claims.append(sent.text.strip())
    return claims

async def extract_claims(text: str) -> List[str]:
    text = clean_text(text)
    # run spaCy in thread to avoid blocking
    claims = await asyncio.to_thread(_extract_claims_sync, text)
    # fallback: if none found, return whole text as single claim
    return claims or [text]
