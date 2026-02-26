"""
Tool: update_sheets.py
Responsibility: Append a summary row to a Google Sheet for the current run.
Input:  {"run_date": str, "article_count": int, "paper_count": int,
          "top_keywords": [...], "pdf_path": str, "status": str}
Output: {"updated": bool, "sheet_url": str, "rows_added": int}
"""

import json
import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
CREDENTIALS_FILE = os.environ.get("GOOGLE_SHEETS_CREDENTIALS", "credentials.json")
SHEET_NAME = "Run Log"

COLUMN_HEADERS = [
    "Run Date", "Articles", "Papers", "Top Keywords",
    "Trending Theme", "PDF Path", "Status", "Timestamp"
]


def _get_service():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def _ensure_sheet_tab(service):
    """Create the 'Run Log' sheet tab if it doesn't already exist."""
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    existing = [s["properties"]["title"] for s in meta.get("sheets", [])]
    if SHEET_NAME not in existing:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": [{"addSheet": {"properties": {"title": SHEET_NAME}}}]},
        ).execute()
        logger.info(f"update_sheets: created sheet tab '{SHEET_NAME}'")


def _ensure_headers(service):
    """Create header row if the sheet is empty."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1:H1",
    ).execute()
    rows = result.get("values", [])
    if not rows:
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1",
            valueInputOption="RAW",
            body={"values": [COLUMN_HEADERS]},
        ).execute()


def update_sheets(
    run_date: str,
    article_count: int,
    paper_count: int,
    top_keywords: list,
    pdf_path: str,
    status: str = "success",
) -> dict:
    try:
        service = _get_service()
        _ensure_sheet_tab(service)
        _ensure_headers(service)

        top_kw_str = ", ".join(k["keyword"] for k in top_keywords[:5])
        timestamp = datetime.now(timezone.utc).isoformat()

        row = [
            run_date[:10],
            article_count,
            paper_count,
            top_kw_str,
            "",               # Trending theme — populated by caller optionally
            pdf_path,
            status,
            timestamp,
        ]

        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]},
        ).execute()

        sheet_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
        logger.info(f"update_sheets: row appended to {sheet_url}")

        return {
            "updated": True,
            "sheet_url": sheet_url,
            "rows_added": 1,
        }

    except Exception as e:
        logger.error(f"update_sheets failed: {e}")
        return {
            "updated": False,
            "sheet_url": "",
            "rows_added": 0,
            "error": str(e),
        }


if __name__ == "__main__":
    import sys
    payload = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    output = update_sheets(
        run_date=payload.get("run_date", datetime.now().isoformat()),
        article_count=payload.get("article_count", 0),
        paper_count=payload.get("paper_count", 0),
        top_keywords=payload.get("top_keywords", []),
        pdf_path=payload.get("pdf_path", ""),
        status=payload.get("status", "success"),
    )
    print(json.dumps(output, indent=2))
