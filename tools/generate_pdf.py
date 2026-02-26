"""
Tool: generate_pdf.py
Responsibility: Generate a branded PDF report from all collected data + charts.
Input:  Combined dict with articles, papers, analysis, charts
Output: {"pdf_path": str, "page_count": int, "generated_at": str}
"""

import json
import logging
import os
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph,
    Spacer, Image, Table, TableStyle, HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "temp", "reports")

# Brand palette
DARK_BG = colors.HexColor("#1A1A2E")
MID_BG = colors.HexColor("#16213E")
ACCENT = colors.HexColor("#0F3460")
RED = colors.HexColor("#E94560")
WHITE = colors.white
LIGHT_GRAY = colors.HexColor("#CCCCCC")


def _ensure_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _build_styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("ReportTitle", fontSize=28, textColor=WHITE,
                                 fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6),
        "subtitle": ParagraphStyle("Subtitle", fontSize=13, textColor=LIGHT_GRAY,
                                    fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4),
        "section": ParagraphStyle("Section", fontSize=14, textColor=RED,
                                   fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=6),
        "body": ParagraphStyle("Body", fontSize=9, textColor=WHITE,
                                fontName="Helvetica", leading=14, spaceAfter=4),
        "small": ParagraphStyle("Small", fontSize=8, textColor=LIGHT_GRAY,
                                  fontName="Helvetica", leading=12),
        "keyword": ParagraphStyle("Keyword", fontSize=10, textColor=WHITE,
                                   fontName="Helvetica-Bold", alignment=TA_CENTER),
    }
    return styles


def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    # Header bar
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, h - 1.2 * cm, w, 1.2 * cm, fill=1, stroke=0)
    canvas.setFillColor(RED)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(1 * cm, h - 0.8 * cm, "AI Research Intelligence Report")
    canvas.setFillColor(LIGHT_GRAY)
    canvas.drawRightString(w - 1 * cm, h - 0.8 * cm, datetime.now().strftime("%B %d, %Y"))

    # Footer bar
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, w, 1 * cm, fill=1, stroke=0)
    canvas.setFillColor(LIGHT_GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(w / 2, 0.3 * cm, f"Page {doc.page}  |  Confidential — Internal Use Only")
    canvas.restoreState()


def generate_pdf(articles: list, papers: list, analysis: dict, charts: dict) -> dict:
    _ensure_dir()
    datestamp = datetime.now().strftime("%Y%m%d")
    pdf_path = os.path.join(REPORTS_DIR, f"AI_Report_{datestamp}.pdf")

    styles = _build_styles()
    w, h = A4

    doc = BaseDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=1.5 * cm,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="main")
    template = PageTemplate(id="main", frames=[frame], onPage=_header_footer)
    doc.addPageTemplates([template])

    story = []
    run_date = datetime.now().strftime("%B %d, %Y")

    # ── Cover section ──────────────────────────────────────────────
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("AI Research Intelligence", styles["title"]))
    story.append(Paragraph("Weekly Briefing Report", styles["subtitle"]))
    story.append(Paragraph(run_date, styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=RED, spaceAfter=12))

    # ── Executive Summary ──────────────────────────────────────────
    story.append(Paragraph("Executive Summary", styles["section"]))
    top_themes = ", ".join(analysis.get("trending_themes", [])[:3]) or "N/A"
    stats = analysis.get("summary_stats", {})
    summary_text = (
        f"This week's AI intelligence report covers <b>{analysis.get('article_count', 0)} news articles</b> "
        f"and <b>{analysis.get('paper_count', 0)} research papers</b> published between "
        f"{stats.get('date_range', 'N/A')}. "
        f"The most active source was <b>{stats.get('most_active_source', 'N/A')}</b>. "
        f"Top trending themes: <b>{top_themes}</b>."
    )
    story.append(Paragraph(summary_text, styles["body"]))
    story.append(Spacer(1, 0.4 * cm))

    # ── Top Keywords Chart ─────────────────────────────────────────
    story.append(Paragraph("Top Keywords", styles["section"]))
    kw_chart = charts.get("keyword_bar", "")
    if kw_chart and os.path.exists(kw_chart):
        story.append(Image(kw_chart, width=16 * cm, height=9 * cm))
    story.append(Spacer(1, 0.3 * cm))

    # Keywords table
    top_kw = analysis.get("top_keywords", [])[:10]
    if top_kw:
        kw_data = [["Keyword", "Frequency"]] + [[k["keyword"], str(k["count"])] for k in top_kw]
        kw_table = Table(kw_data, colWidths=[10 * cm, 6 * cm])
        kw_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [MID_BG, DARK_BG]),
            ("TEXTCOLOR", (0, 1), (-1, -1), WHITE),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#333355")),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(kw_table)

    story.append(PageBreak())

    # ── Trending Themes ────────────────────────────────────────────
    story.append(Paragraph("Trending Themes", styles["section"]))
    pie_chart = charts.get("theme_pie", "")
    if pie_chart and os.path.exists(pie_chart):
        story.append(Image(pie_chart, width=12 * cm, height=12 * cm))

    vol_chart = charts.get("volume_trend", "")
    if vol_chart and os.path.exists(vol_chart):
        story.append(Paragraph("Content Volume Breakdown", styles["section"]))
        story.append(Image(vol_chart, width=14 * cm, height=8 * cm))

    story.append(PageBreak())

    # ── Top News Articles ──────────────────────────────────────────
    story.append(Paragraph("Top News Articles", styles["section"]))
    for i, article in enumerate(articles[:10], 1):
        title = article.get("title", "Untitled")[:120]
        source = article.get("source", "Unknown")
        pub = article.get("published_at", "")[:10]
        desc = (article.get("description", "") or "")[:200]
        story.append(Paragraph(f"<b>{i}. {title}</b>", styles["body"]))
        story.append(Paragraph(f"Source: {source}  |  Published: {pub}", styles["small"]))
        if desc:
            story.append(Paragraph(desc, styles["small"]))
        story.append(Spacer(1, 0.25 * cm))

    story.append(PageBreak())

    # ── Research Papers ────────────────────────────────────────────
    story.append(Paragraph("AI Research Papers", styles["section"]))
    for i, paper in enumerate(papers[:10], 1):
        title = paper.get("title", "Untitled")[:120]
        authors = ", ".join(paper.get("authors", [])[:3])
        pub = paper.get("published_at", "")[:10]
        abstract = (paper.get("abstract", "") or "")[:250]
        arxiv_id = paper.get("arxiv_id", "")
        story.append(Paragraph(f"<b>{i}. {title}</b>", styles["body"]))
        story.append(Paragraph(f"Authors: {authors}  |  Published: {pub}  |  ArXiv: {arxiv_id}", styles["small"]))
        if abstract:
            story.append(Paragraph(abstract + "...", styles["small"]))
        story.append(Spacer(1, 0.3 * cm))

    doc.build(story)

    page_count = doc.page
    result = {
        "pdf_path": pdf_path,
        "page_count": page_count,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(f"generate_pdf: saved {pdf_path} ({page_count} pages)")
    return result


if __name__ == "__main__":
    import sys
    payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    output = generate_pdf(
        articles=payload.get("articles", []),
        papers=payload.get("papers", []),
        analysis=payload.get("analysis", {}),
        charts=payload.get("charts", {}),
    )
    print(json.dumps(output, indent=2))
