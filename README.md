
## Features
- Accepts a text/article input and extracts candidate claims
- Searches Wikipedia, NewsAPI, and Google Fact Check for evidence
- Uses an LLM (GROQ) to synthesize verdict and explanation
- Stores checks in PostgreSQL

## Workflow
                ┌──────────────────────┐
                │      User (Web)      │
                │  React Frontend UI   │
                └─────────┬────────────┘
                          │ HTTP Request
                          ▼
                ┌──────────────────────┐
                │     FastAPI Backend  │
                │   (API Layer)        │
                └─────────┬────────────┘
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
     ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
     │ Claim        │  │ Fact Checker │  │ LLM Verifier     │
     │ Extractor    │  │ (News/Wiki)  │  │ (Groq/OpenAI)    │
     │ (spaCy NLP)  │  │              │  │                  │
     └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘
       │                  │                  │
       └──────────┬───────┴──────────┬───────┘
                  ▼                  ▼
           ┌──────────────────────────────┐
           │   Response Aggregator        │
           │ (Verdict + Confidence + Exp) │
           └────────────┬─────────────────┘
                        │
                        ▼
              ┌──────────────────────┐
              │ PostgreSQL Database  │
              │ (History Storage)    │
              └────────────┬─────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   Frontend Display   │
                │ (Result + Sources)   │
                └──────────────────────┘
## Pipeline
    User Input (Claim/Text)
        │
        ▼
    [1] Preprocessing Layer
    - Clean text
    - Normalize input

        ▼
    [2] Claim Extraction (spaCy)
    - Identify meaningful claims
    - Split multi-claim text

        ▼
    [3] Fact Retrieval
    - Query News APIs
    - Query Wikipedia
    - Fetch fact-check sources

        ▼
    [4] Semantic Matching (Optional)
    - Sentence Transformers
    - Similarity scoring with known facts

        ▼
    [5] LLM Verification (Core AI)
    - Input: Claim + Retrieved Evidence
    - Output:
        ✔ Verdict (True / False / Misleading)
        ✔ Confidence Score
        ✔ Explanation

        ▼
    [6] Post-processing
    - Format response
    - Attach sources
    - Structure JSON

        ▼
    [7] Database Storage
    - Save claim
    - Save verdict + explanation
    - Save timestamp

        ▼
    [8] API Response
    - Return structured result

        ▼
    [9] Frontend Rendering
    - Show verdict badge
    - Show confidence bar
    - Show explanation
    - Show sources
    
## Run locally
1. Create a Python venv
2. Copy `.env.example` to `.env` and fill keys
3. `pip install -r requirements.txt`
4. Run `uvicorn app.main:app --reload`
