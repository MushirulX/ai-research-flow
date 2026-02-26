"""
Tool: fetch_news.py
Responsibility: Fetch AI-related news articles from NewsAPI for the past N days.
Input:  {"days_back": int, "query": str, "max_articles": int}
Output: {"articles": [...], "count": int, "fetched_at": str}
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
NEWS_API_URL = "https://newsapi.org/v2/everything"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def fetch_news(days_back: int = 7, query: str = "artificial intelligence", max_articles: int = 50) -> dict:
    from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
    to_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    params = {
        "q": query,
        "from": from_date,
        "to": to_date,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": min(max_articles, 100),
        "apiKey": NEWS_API_KEY,
    }

    articles = []
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(NEWS_API_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "ok":
                raise ValueError(f"NewsAPI error: {data.get('message', 'Unknown error')}")

            for item in data.get("articles", []):
                articles.append({
                    "title": item.get("title", ""),
                    "source": item.get("source", {}).get("name", ""),
                    "url": item.get("url", ""),
                    "published_at": item.get("publishedAt", ""),
                    "description": item.get("description", "") or "",
                })
            break

        except requests.exceptions.RateLimitError:
            logger.error("NewsAPI rate limit reached.")
            raise
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"fetch_news failed after {MAX_RETRIES} retries: {e}") from e
            time.sleep(RETRY_DELAY)

    result = {
        "articles": articles,
        "count": len(articles),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(f"fetch_news: retrieved {len(articles)} articles")
    return result


if __name__ == "__main__":
    import sys
    payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    output = fetch_news(
        days_back=payload.get("days_back", 7),
        query=payload.get("query", "artificial intelligence machine learning"),
        max_articles=payload.get("max_articles", 50),
    )
    print(json.dumps(output, indent=2))
