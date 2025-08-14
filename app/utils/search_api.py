# app/utils/search_api.py
import os
import httpx
from typing import List, Dict

from app.config import settings

NEWSAPI_KEY = settings.newsapi_key
GOOGLE_KEY = settings.google_fact_check_api_key
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"

async def search_newsapi(query: str, limit: int = 5) -> List[Dict]:
    if not NEWSAPI_KEY:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "pageSize": limit, "sortBy": "relevancy", "language": "en", "apiKey": NEWSAPI_KEY}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        if r.status_code != 200:
            return []
        data = r.json()
    return [
        {"title": a.get("title"), "url": a.get("url"), "publisher": a.get("source", {}).get("name"), "date": a.get("publishedAt")}
        for a in data.get("articles", [])
    ]

async def search_google_factcheck(query: str, limit: int = 5) -> List[Dict]:
    if not GOOGLE_KEY:
        return []
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {"query": query, "key": GOOGLE_KEY, "pageSize": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        if r.status_code != 200:
            return []
        data = r.json()
    results = []
    for c in data.get("claims", []):
        review = c.get("claimReview", [])
        if review:
            rv = review[0]
            results.append({
                "title": c.get("text"),
                "url": rv.get("url"),
                "publisher": rv.get("publisher", {}).get("name"),
                "date": rv.get("reviewDate"),
                "rating": rv.get("textualRating")
            })
    return results

async def search_wikipedia(query: str, limit: int = 3) -> List[Dict]:
    params = {"action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": limit}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(WIKIPEDIA_API, params=params)
        if r.status_code != 200:
            return []
        data = r.json()
    res = []
    for it in data.get("query", {}).get("search", []):
        title = it.get("title")
        url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        snippet = it.get("snippet")
        res.append({"title": title, "url": url, "publisher": "Wikipedia", "date": None, "snippet": snippet})
    return res

async def unified_search(query: str) -> Dict[str, List[Dict]]:
    news = await search_newsapi(query)
    factchecks = await search_google_factcheck(query)
    wiki = await search_wikipedia(query)
    return {"news": news, "factchecks": factchecks, "wikipedia": wiki}
