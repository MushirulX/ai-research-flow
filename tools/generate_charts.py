"""
Tool: generate_charts.py
Responsibility: Generate visualisation charts from trend analysis data.
Input:  analyze_trends output dict
Output: {"charts": {"keyword_bar": str, "theme_pie": str, "volume_trend": str}}
"""

import json
import logging
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — safe for servers
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

logger = logging.getLogger(__name__)

CHARTS_DIR = os.path.join(os.path.dirname(__file__), "..", "temp", "charts")
BRAND_COLOR = "#1A1A2E"
ACCENT_COLOR = "#16213E"
HIGHLIGHT_COLOR = "#0F3460"
TEXT_COLOR = "#E94560"


def _ensure_dir():
    os.makedirs(CHARTS_DIR, exist_ok=True)


def _datestamp() -> str:
    return datetime.now().strftime("%Y%m%d")


def generate_keyword_bar(top_keywords: list) -> str:
    _ensure_dir()
    keywords = [k["keyword"] for k in top_keywords[:10]]
    counts = [k["count"] for k in top_keywords[:10]]

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BRAND_COLOR)
    ax.set_facecolor(ACCENT_COLOR)

    bars = ax.barh(keywords[::-1], counts[::-1], color=TEXT_COLOR, height=0.6)
    ax.set_xlabel("Frequency", color="white", fontsize=11)
    ax.set_title("Top AI Keywords This Week", color="white", fontsize=14, fontweight="bold", pad=15)
    ax.tick_params(colors="white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#444")
    ax.spines["bottom"].set_color("#444")

    for bar, count in zip(bars, counts[::-1]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                str(count), va="center", color="white", fontsize=9)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, f"keyword_bar_{_datestamp()}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BRAND_COLOR)
    plt.close(fig)
    logger.info(f"Saved keyword_bar chart: {path}")
    return path


def generate_theme_pie(trending_themes: list, top_keywords: list) -> str:
    _ensure_dir()
    themes = trending_themes[:6]
    if not themes:
        themes = ["General AI"]

    # Approximate sizes from keyword frequency distribution
    total = sum(k["count"] for k in top_keywords[:6]) or 1
    sizes = []
    for i, _ in enumerate(themes):
        sizes.append(top_keywords[i]["count"] if i < len(top_keywords) else 1)

    colors = ["#E94560", "#0F3460", "#533483", "#2B9348", "#F4A261", "#E76F51"]

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor(BRAND_COLOR)
    ax.set_facecolor(BRAND_COLOR)

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        autopct="%1.0f%%",
        colors=colors[:len(themes)],
        startangle=140,
        pctdistance=0.75,
        wedgeprops={"edgecolor": BRAND_COLOR, "linewidth": 2},
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(9)

    ax.set_title("Trending AI Themes", color="white", fontsize=14, fontweight="bold", pad=20)
    legend_patches = [mpatches.Patch(color=colors[i], label=t) for i, t in enumerate(themes)]
    ax.legend(handles=legend_patches, loc="lower center", bbox_to_anchor=(0.5, -0.1),
              ncol=2, frameon=False, labelcolor="white", fontsize=9)

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, f"theme_pie_{_datestamp()}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BRAND_COLOR)
    plt.close(fig)
    logger.info(f"Saved theme_pie chart: {path}")
    return path


def generate_volume_trend(article_count: int, paper_count: int) -> str:
    _ensure_dir()
    categories = ["News Articles", "Research Papers", "Total Sources"]
    values = [article_count, paper_count, article_count + paper_count]

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(BRAND_COLOR)
    ax.set_facecolor(ACCENT_COLOR)

    bar_colors = [TEXT_COLOR, "#0F3460", "#533483"]
    bars = ax.bar(categories, values, color=bar_colors, width=0.5, edgecolor=BRAND_COLOR)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha="center", va="bottom", color="white", fontsize=12, fontweight="bold")

    ax.set_ylabel("Count", color="white", fontsize=11)
    ax.set_title("Weekly Content Volume", color="white", fontsize=14, fontweight="bold", pad=15)
    ax.tick_params(colors="white")
    ax.set_ylim(0, max(values) * 1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#444")
    ax.spines["bottom"].set_color("#444")

    plt.tight_layout()
    path = os.path.join(CHARTS_DIR, f"volume_trend_{_datestamp()}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BRAND_COLOR)
    plt.close(fig)
    logger.info(f"Saved volume_trend chart: {path}")
    return path


def generate_charts(analysis: dict) -> dict:
    top_keywords = analysis.get("top_keywords", [])
    trending_themes = analysis.get("trending_themes", [])
    article_count = analysis.get("article_count", 0)
    paper_count = analysis.get("paper_count", 0)

    charts = {
        "keyword_bar": generate_keyword_bar(top_keywords),
        "theme_pie": generate_theme_pie(trending_themes, top_keywords),
        "volume_trend": generate_volume_trend(article_count, paper_count),
    }

    return {"charts": charts}


if __name__ == "__main__":
    import sys
    payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    output = generate_charts(payload)
    print(json.dumps(output, indent=2))
