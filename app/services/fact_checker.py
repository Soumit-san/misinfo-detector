import httpx
from app.config import settings
from typing import List

WIKIPEDIA_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
NEWSAPI_URL = "https://newsapi.org/v2/everything"
GOOGLE_FACTCHECK_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

async def search_wikipedia(claim: str) -> List[dict]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": claim,
        "format": "json",
        "srlimit": 5,
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(WIKIPEDIA_SEARCH_URL, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        print(f"[Wikipedia Search Error] {e}")
        return []

    results = []
    for it in data.get("query", {}).get("search", []):
        title = it.get("title")
        snippet = it.get("snippet")
        url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        results.append({"title": title, "url": url, "snippet": snippet})
    return results


async def search_newsapi(claim: str) -> List[dict]:
    if not settings.newsapi_key:
        return []
    params = {"q": claim, "apiKey": settings.newsapi_key, "pageSize": 5}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(NEWSAPI_URL, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        print(f"[NewsAPI Error] {e}")
        return []

    results = []
    for a in data.get("articles", []):
        results.append({
            "title": a.get("title"),
            "url": a.get("url"),
            "snippet": a.get("description")
        })
    return results


async def search_google_factcheck(claim: str) -> List[dict]:
    if not settings.google_fact_check_api_key:
        return []

    params = {"query": claim, "key": settings.google_fact_check_api_key}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(GOOGLE_FACTCHECK_URL, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        print(f"[Google Fact Check API Error] {e}")
        return []

    results = []
    for item in data.get("claims", []):
        review = item.get("claimReview", [])
        for rev in review:
            results.append({
                "title": rev.get("publisher", {}).get("name"),
                "url": rev.get("url"),
                "snippet": rev.get("title")
            })
    return results


async def fact_check_claim(claim: str) -> dict:
    wiki = await search_wikipedia(claim)
    news = await search_newsapi(claim)
    gfc = await search_google_factcheck(claim)

    return {
        "wikipedia": wiki,
        "news_sources": news,
        "factcheck_sources": gfc
    }
