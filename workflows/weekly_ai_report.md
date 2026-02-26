# Workflow: Weekly AI Research Report

**Trigger:** Cron — Every Monday at 6:00 AM
**Output:** Branded PDF report + Google Sheets update + Email delivery
**Version:** 1.0

---

## Overview

This workflow fetches AI news and research papers from the past 7 days,
analyzes trends, generates a branded PDF report, updates a Google Sheet,
and emails the report to stakeholders.

---

## Preconditions

- Environment variables loaded from `.env`
- Required: `NEWS_API_KEY`, `GMAIL_CREDENTIALS`, `GOOGLE_SHEETS_CREDENTIALS`
- `/temp/charts`, `/temp/reports`, `/temp/logs` directories exist

---

## Steps

### Step 1 — Fetch AI News
**Tool:** `tools/fetch_news.py`
**Input:**
```json
{
  "days_back": 7,
  "query": "artificial intelligence machine learning",
  "max_articles": 50
}
```
**Output:**
```json
{
  "articles": [
    {
      "title": "string",
      "source": "string",
      "url": "string",
      "published_at": "ISO8601",
      "description": "string"
    }
  ],
  "count": "integer",
  "fetched_at": "ISO8601"
}
```
**On Failure:** Log error → Stop execution → Send failure email

---

### Step 2 — Fetch AI Research Papers
**Tool:** `tools/fetch_research.py`
**Input:**
```json
{
  "days_back": 7,
  "query": "artificial intelligence large language models deep learning",
  "max_papers": 30
}
```
**Output:**
```json
{
  "papers": [
    {
      "title": "string",
      "authors": ["string"],
      "abstract": "string",
      "arxiv_id": "string",
      "published_at": "ISO8601",
      "categories": ["string"]
    }
  ],
  "count": "integer",
  "fetched_at": "ISO8601"
}
```
**On Failure:** Log error → Stop execution → Send failure email

---

### Step 3 — Analyze Trends
**Tool:** `tools/analyze_trends.py`
**Input:** Merged output from Step 1 + Step 2
```json
{
  "articles": [...],
  "papers": [...],
  "run_date": "ISO8601"
}
```
**Output:**
```json
{
  "top_keywords": [{"keyword": "string", "count": "integer"}],
  "trending_themes": ["string"],
  "article_count": "integer",
  "paper_count": "integer",
  "summary_stats": {
    "total_sources": "integer",
    "date_range": "string",
    "most_active_source": "string"
  }
}
```
**On Failure:** Log error → Stop execution

---

### Step 4 — Generate Charts
**Tool:** `tools/generate_charts.py`
**Input:** Output from Step 3
**Output:**
```json
{
  "charts": {
    "keyword_bar": "/temp/charts/keyword_bar_YYYYMMDD.png",
    "theme_pie": "/temp/charts/theme_pie_YYYYMMDD.png",
    "volume_trend": "/temp/charts/volume_trend_YYYYMMDD.png"
  }
}
```
**On Failure:** Log error → Stop execution

---

### Step 5 — Generate PDF Report
**Tool:** `tools/generate_pdf.py`
**Input:** Output from Steps 1–4 combined
**Output:**
```json
{
  "pdf_path": "/temp/reports/AI_Report_YYYYMMDD.pdf",
  "page_count": "integer",
  "generated_at": "ISO8601"
}
```
**On Failure:** Log error → Stop execution

---

### Step 6 — Update Google Sheets
**Tool:** `tools/update_sheets.py`
**Input:**
```json
{
  "run_date": "ISO8601",
  "article_count": "integer",
  "paper_count": "integer",
  "top_keywords": [...],
  "pdf_path": "string",
  "status": "success"
}
```
**Output:**
```json
{
  "updated": true,
  "sheet_url": "string",
  "rows_added": "integer"
}
```
**On Failure:** Log error → Continue to Step 7 (non-blocking)

---

### Step 7 — Send Email Report
**Tool:** `tools/send_email.py`
**Input:**
```json
{
  "pdf_path": "string",
  "run_date": "string",
  "article_count": "integer",
  "paper_count": "integer",
  "top_keywords": [...],
  "sheet_url": "string"
}
```
**Output:**
```json
{
  "sent": true,
  "recipients": ["string"],
  "sent_at": "ISO8601"
}
```
**On Failure:** Retry once → Log error → Stop

---

### Step 8 — Log Run Summary
**Output File:** `/temp/logs/run_YYYYMMDD_HHMMSS.json`
```json
{
  "run_id": "string",
  "start_time": "ISO8601",
  "end_time": "ISO8601",
  "articles_processed": "integer",
  "papers_processed": "integer",
  "top_5_keywords": ["string"],
  "pdf_path": "string",
  "email_status": "success|failed",
  "sheets_status": "success|failed"
}
```

---

## Data Flow Diagram

```
NewsAPI ──────────────┐
                      ▼
                  fetch_news.py ──────────────────────┐
                                                      ▼
ArXiv ────────────────┐                       analyze_trends.py
                      ▼                               │
              fetch_research.py ────────────────────┘ │
                                                      ▼
                                             generate_charts.py
                                                      │
                                                      ▼
                                              generate_pdf.py
                                                      │
                                       ┌──────────────┴──────────────┐
                                       ▼                             ▼
                               update_sheets.py               send_email.py
                                       │                             │
                                       └──────────────┬─────────────┘
                                                      ▼
                                                  Log Summary
```

---

## Failure Handling Summary

| Step | Failure Action |
|------|---------------|
| fetch_news | Stop + send failure email |
| fetch_research | Stop + send failure email |
| analyze_trends | Stop |
| generate_charts | Stop |
| generate_pdf | Stop |
| update_sheets | Log + continue |
| send_email | Retry once + log |

---

## Success Criteria

- PDF generated and saved in `/temp/reports`
- Email delivered to all recipients
- Google Sheet updated with new row
- Run log written to `/temp/logs`
