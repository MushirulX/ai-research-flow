"""
Tool: fetch_research.py
Responsibility: Fetch AI research papers from ArXiv for the past N days.
Input:  {"days_back": int, "query": str, "max_papers": int}
Output: {"papers": [...], "count": int, "fetched_at": str}
"""

import json
import time
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import requests

logger = logging.getLogger(__name__)

ARXIV_API_URL = "http://export.arxiv.org/api/query"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
ARXIV_NS = "http://www.w3.org/2005/Atom"


def fetch_research(days_back: int = 7, query: str = "artificial intelligence", max_papers: int = 30) -> dict:
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_papers,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    papers = []
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(ARXIV_API_URL, params=params, timeout=20)
            response.raise_for_status()

            root = ET.fromstring(response.text)
            entries = root.findall(f"{{{ARXIV_NS}}}entry")

            for entry in entries:
                published_str = entry.findtext(f"{{{ARXIV_NS}}}published", "")
                try:
                    published_dt = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                except ValueError:
                    continue

                if published_dt < cutoff_date:
                    continue

                arxiv_id_raw = entry.findtext(f"{{{ARXIV_NS}}}id", "")
                arxiv_id = arxiv_id_raw.split("/abs/")[-1] if "/abs/" in arxiv_id_raw else arxiv_id_raw

                authors = [
                    author.findtext(f"{{{ARXIV_NS}}}name", "")
                    for author in entry.findall(f"{{{ARXIV_NS}}}author")
                ]

                categories = [
                    tag.get("term", "")
                    for tag in entry.findall("{http://arxiv.org/schemas/atom}primary_category")
                ] + [
                    tag.get("term", "")
                    for tag in entry.findall("{http://www.w3.org/2005/Atom}category")
                ]

                papers.append({
                    "title": entry.findtext(f"{{{ARXIV_NS}}}title", "").strip(),
                    "authors": authors[:5],  # cap at 5
                    "abstract": entry.findtext(f"{{{ARXIV_NS}}}summary", "").strip(),
                    "arxiv_id": arxiv_id,
                    "published_at": published_str,
                    "categories": list(set(filter(None, categories))),
                })
            break

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"fetch_research failed after {MAX_RETRIES} retries: {e}") from e
            time.sleep(RETRY_DELAY)

    result = {
        "papers": papers,
        "count": len(papers),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(f"fetch_research: retrieved {len(papers)} papers")
    return result


if __name__ == "__main__":
    import sys
    payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    output = fetch_research(
        days_back=payload.get("days_back", 7),
        query=payload.get("query", "artificial intelligence large language models deep learning"),
        max_papers=payload.get("max_papers", 30),
    )
    print(json.dumps(output, indent=2))
