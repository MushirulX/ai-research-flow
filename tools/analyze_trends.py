"""
Tool: analyze_trends.py
Responsibility: Analyze keyword frequency and trending themes from merged news + research data.
Input:  {"articles": [...], "papers": [...], "run_date": str}
Output: {"top_keywords": [...], "trending_themes": [...], "article_count": int,
         "paper_count": int, "summary_stats": {...}}
"""

import json
import re
import logging
from collections import Counter
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Common English stop words to exclude from keyword analysis
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "not", "no", "nor", "so",
    "yet", "both", "either", "neither", "each", "few", "more", "most",
    "other", "some", "such", "than", "too", "very", "just", "that", "this",
    "these", "those", "it", "its", "we", "our", "they", "their", "new",
    "also", "using", "based", "show", "shows", "paper", "study", "research",
    "results", "method", "methods", "approach", "proposed", "model", "models",
    "data", "use", "used", "two", "first", "second", "one", "three",
}

AI_THEME_KEYWORDS = {
    "Large Language Models": ["llm", "gpt", "language model", "chatgpt", "gemini", "claude", "llama"],
    "Computer Vision": ["vision", "image", "object detection", "cnn", "visual", "diffusion"],
    "Reinforcement Learning": ["reinforcement", "rl", "reward", "policy", "agent", "drl"],
    "AI Safety & Alignment": ["safety", "alignment", "harmful", "bias", "ethics", "responsible ai"],
    "Multimodal AI": ["multimodal", "text-to-image", "image-to-text", "audio", "video generation"],
    "AI Infrastructure": ["inference", "training", "gpu", "compute", "deployment", "scalability"],
    "Natural Language Processing": ["nlp", "sentiment", "translation", "summarization", "ner"],
    "Generative AI": ["generative", "gen ai", "diffusion model", "stable diffusion", "midjourney"],
    "AI in Healthcare": ["healthcare", "medical", "clinical", "diagnosis", "drug discovery"],
    "Robotics & Automation": ["robot", "robotics", "automation", "autonomous", "drone"],
}


def extract_text(articles: list, papers: list) -> list[str]:
    texts = []
    for article in articles:
        texts.append(f"{article.get('title', '')} {article.get('description', '')}")
    for paper in papers:
        texts.append(f"{paper.get('title', '')} {paper.get('abstract', '')}")
    return texts


def tokenize(text: str) -> list[str]:
    text = text.lower()
    words = re.findall(r'\b[a-z]{3,}\b', text)
    return [w for w in words if w not in STOP_WORDS]


def detect_themes(texts: list[str]) -> list[str]:
    combined = " ".join(texts).lower()
    theme_scores = {}
    for theme, keywords in AI_THEME_KEYWORDS.items():
        score = sum(combined.count(kw) for kw in keywords)
        if score > 0:
            theme_scores[theme] = score
    return [theme for theme, _ in sorted(theme_scores.items(), key=lambda x: -x[1])]


def get_most_active_source(articles: list) -> str:
    sources = [a.get("source", "") for a in articles if a.get("source")]
    if not sources:
        return "N/A"
    return Counter(sources).most_common(1)[0][0]


def analyze_trends(articles: list, papers: list, run_date: str = None) -> dict:
    if run_date is None:
        run_date = datetime.now(timezone.utc).isoformat()

    texts = extract_text(articles, papers)
    all_words = []
    for text in texts:
        all_words.extend(tokenize(text))

    word_counts = Counter(all_words)
    top_keywords = [
        {"keyword": word, "count": count}
        for word, count in word_counts.most_common(20)
    ]

    trending_themes = detect_themes(texts)

    # Date range from article published_at
    all_dates = [
        a.get("published_at", "") for a in articles
        if a.get("published_at")
    ] + [
        p.get("published_at", "") for p in papers
        if p.get("published_at")
    ]
    all_dates_sorted = sorted(filter(None, all_dates))
    date_range = (
        f"{all_dates_sorted[0][:10]} to {all_dates_sorted[-1][:10]}"
        if all_dates_sorted else "N/A"
    )

    result = {
        "top_keywords": top_keywords,
        "trending_themes": trending_themes[:8],
        "article_count": len(articles),
        "paper_count": len(papers),
        "summary_stats": {
            "total_sources": len(articles) + len(papers),
            "date_range": date_range,
            "most_active_source": get_most_active_source(articles),
        },
    }

    logger.info(f"analyze_trends: top theme={trending_themes[0] if trending_themes else 'N/A'}, keywords={len(top_keywords)}")
    return result


if __name__ == "__main__":
    import sys
    payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    output = analyze_trends(
        articles=payload.get("articles", []),
        papers=payload.get("papers", []),
        run_date=payload.get("run_date"),
    )
    print(json.dumps(output, indent=2))
