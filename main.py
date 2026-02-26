"""
main.py — AI Research Intelligence System
WAT Framework: Workflows + Agent + Tools

Orchestrates the weekly AI research report pipeline.
Runs all tools sequentially, passes structured JSON between steps,
handles errors, and logs the run summary.

Usage:
    python main.py               # Run the full pipeline
    python main.py --dry-run     # Validate config only, skip API calls
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Logging setup ──────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "temp" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
log_filename = LOG_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_filename),
    ],
)
logger = logging.getLogger("main")

# ── Tool imports ───────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / "tools"))

from fetch_news import fetch_news
from fetch_research import fetch_research
from analyze_trends import analyze_trends
from generate_charts import generate_charts
from generate_pdf import generate_pdf
from update_sheets import update_sheets
from send_email import send_email


def send_failure_email(run_date: str, step: str, error: str):
    """Attempt to notify stakeholders of a pipeline failure."""
    try:
        send_email(
            pdf_path="",
            run_date=run_date,
            article_count=0,
            paper_count=0,
            top_keywords=[],
            sheet_url="",
            failure_mode=True,
        )
        logger.info(f"Failure notification sent for step: {step}")
    except Exception as e:
        logger.error(f"Could not send failure email: {e}")


def write_run_log(log_data: dict):
    log_path = LOG_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)
    logger.info(f"Run log saved: {log_path}")


def validate_env():
    required = ["NEWS_API_KEY", "GMAIL_USER", "GMAIL_APP_PASSWORD",
                 "EMAIL_RECIPIENTS", "GOOGLE_SHEET_ID", "GOOGLE_SHEETS_CREDENTIALS"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")


def run_pipeline(dry_run: bool = False):
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time = datetime.now(timezone.utc)
    run_date = start_time.isoformat()

    logger.info(f"{'='*60}")
    logger.info(f"AI Research Intelligence Pipeline — Run ID: {run_id}")
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info(f"{'='*60}")

    validate_env()

    if dry_run:
        logger.info("Dry run complete — environment variables OK.")
        return

    log_data = {
        "run_id": run_id,
        "start_time": run_date,
        "end_time": None,
        "articles_processed": 0,
        "papers_processed": 0,
        "top_5_keywords": [],
        "pdf_path": "",
        "email_status": "not_sent",
        "sheets_status": "not_updated",
    }

    try:
        # ── Step 1: Fetch News ─────────────────────────────────────
        logger.info("[Step 1/8] Fetching AI news...")
        news_result = fetch_news(days_back=7, query="artificial intelligence machine learning", max_articles=50)
        articles = news_result["articles"]
        logger.info(f"  → {news_result['count']} articles fetched")

        # ── Step 2: Fetch Research Papers ─────────────────────────
        logger.info("[Step 2/8] Fetching ArXiv research papers...")
        research_result = fetch_research(
            days_back=7,
            query="artificial intelligence large language models deep learning",
            max_papers=30,
        )
        papers = research_result["papers"]
        logger.info(f"  → {research_result['count']} papers fetched")

        # ── Step 3: Analyze Trends ─────────────────────────────────
        logger.info("[Step 3/8] Analyzing trends and keywords...")
        analysis = analyze_trends(articles=articles, papers=papers, run_date=run_date)
        log_data["articles_processed"] = analysis["article_count"]
        log_data["papers_processed"] = analysis["paper_count"]
        log_data["top_5_keywords"] = [k["keyword"] for k in analysis["top_keywords"][:5]]
        logger.info(f"  → Top theme: {analysis['trending_themes'][0] if analysis['trending_themes'] else 'N/A'}")
        logger.info(f"  → Top keywords: {', '.join(log_data['top_5_keywords'])}")

        # ── Step 4: Generate Charts ────────────────────────────────
        logger.info("[Step 4/8] Generating charts...")
        charts_result = generate_charts(analysis)
        charts = charts_result["charts"]
        logger.info(f"  → Charts: {list(charts.keys())}")

        # ── Step 5: Generate PDF ───────────────────────────────────
        logger.info("[Step 5/8] Generating PDF report...")
        pdf_result = generate_pdf(articles=articles, papers=papers, analysis=analysis, charts=charts)
        pdf_path = pdf_result["pdf_path"]
        log_data["pdf_path"] = pdf_path
        logger.info(f"  → PDF: {pdf_path} ({pdf_result['page_count']} pages)")

        # ── Step 6: Update Google Sheets ──────────────────────────
        logger.info("[Step 6/8] Updating Google Sheets...")
        sheets_result = update_sheets(
            run_date=run_date,
            article_count=analysis["article_count"],
            paper_count=analysis["paper_count"],
            top_keywords=analysis["top_keywords"],
            pdf_path=pdf_path,
            status="success",
        )
        sheet_url = sheets_result.get("sheet_url", "")
        log_data["sheets_status"] = "updated" if sheets_result.get("updated") else "failed"
        logger.info(f"  → Sheets: {'updated' if sheets_result.get('updated') else 'FAILED (non-blocking)'}")

        # ── Step 7: Send Email ─────────────────────────────────────
        logger.info("[Step 7/8] Sending email report...")
        email_result = send_email(
            pdf_path=pdf_path,
            run_date=run_date,
            article_count=analysis["article_count"],
            paper_count=analysis["paper_count"],
            top_keywords=analysis["top_keywords"],
            sheet_url=sheet_url,
        )
        log_data["email_status"] = "sent" if email_result.get("sent") else "failed"
        logger.info(f"  → Email: {'sent' if email_result.get('sent') else 'FAILED'}")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        send_failure_email(run_date=run_date, step="pipeline", error=str(e))
        log_data["email_status"] = "failure_notification_sent"
        log_data["end_time"] = datetime.now(timezone.utc).isoformat()
        write_run_log(log_data)
        sys.exit(1)

    # ── Step 8: Log Summary ────────────────────────────────────────
    logger.info("[Step 8/8] Writing run summary log...")
    end_time = datetime.now(timezone.utc)
    log_data["end_time"] = end_time.isoformat()
    write_run_log(log_data)

    duration = (end_time - start_time).seconds
    logger.info(f"{'='*60}")
    logger.info(f"Pipeline complete in {duration}s")
    logger.info(f"  Articles: {log_data['articles_processed']}")
    logger.info(f"  Papers:   {log_data['papers_processed']}")
    logger.info(f"  Keywords: {', '.join(log_data['top_5_keywords'])}")
    logger.info(f"  PDF:      {log_data['pdf_path']}")
    logger.info(f"  Email:    {log_data['email_status']}")
    logger.info(f"  Sheets:   {log_data['sheets_status']}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Research Intelligence Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Validate config only, skip API calls")
    args = parser.parse_args()
    run_pipeline(dry_run=args.dry_run)
