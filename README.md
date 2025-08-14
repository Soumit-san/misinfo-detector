# Misinfo Detector Backend (MVP)

This repository contains a FastAPI backend scaffold for an AI-powered misinformation detection tool.

## Features
- Accepts a text/article input and extracts candidate claims
- Searches Wikipedia, NewsAPI, and Google Fact Check for evidence
- Uses an LLM (GROQ) to synthesize verdict and explanation
- Stores checks in PostgreSQL

## Run locally
1. Create a Python venv
2. Copy `.env.example` to `.env` and fill keys
3. `pip install -r requirements.txt`
4. Run `uvicorn app.main:app --reload`