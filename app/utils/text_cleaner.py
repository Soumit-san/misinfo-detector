# app/utils/text_cleaner.py
import re

def clean_text(text: str) -> str:
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text
