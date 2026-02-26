# AI Research Intelligence System

An automated weekly pipeline that monitors AI news and research, analyzes trends, generates a branded PDF report, updates a Google Sheet, and emails stakeholders — all on a cron schedule via [Modal](https://modal.com).

Built on the **WAT Framework**: Workflows + Agent + Tools.

---

## How It Works

Every Monday at 6:00 AM, the pipeline runs automatically:

```
NewsAPI ──► fetch_news ──────────────────────► analyze_trends ──► generate_charts ──► generate_pdf
                                                     ▲                                       │
ArXiv ───► fetch_research ───────────────────────────┘                          ┌────────────┘
                                                                                 ▼
                                                                        update_sheets + send_email
                                                                                 │
                                                                                 ▼
                                                                            Log Summary
```

1. **Fetch AI news** — pulls the past 7 days from NewsAPI (up to 50 articles)
2. **Fetch research papers** — pulls from ArXiv (up to 30 papers)
3. **Analyze trends** — extracts top keywords and trending themes
4. **Generate charts** — keyword bar chart, theme pie chart, volume trend
5. **Generate PDF** — branded report with articles, papers, and charts
6. **Update Google Sheets** — appends a new row for each run
7. **Send email** — delivers PDF report to all stakeholders
8. **Log summary** — structured JSON log saved to `/temp/logs`

---

## Project Structure

```
AI_RESEARCH_FLOW/
├── main.py                        # Pipeline orchestrator
├── generate_flowchart.py          # System architecture diagram generator
├── requirements.txt
├── .env.example                   # Environment variable template
├── .gitignore
├── Claude.md                      # Agent instructions (WAT framework)
│
├── workflows/
│   └── weekly_ai_report.md        # Full workflow spec with I/O contracts
│
├── tools/
│   ├── fetch_news.py              # NewsAPI integration
│   ├── fetch_research.py          # ArXiv API integration
│   ├── analyze_trends.py          # Keyword & theme analysis
│   ├── generate_charts.py         # Matplotlib chart generation
│   ├── generate_pdf.py            # ReportLab PDF builder
│   ├── update_sheets.py           # Google Sheets API integration
│   └── send_email.py              # Gmail SMTP delivery
│
└── temp/                          # Runtime outputs (git-ignored)
    ├── charts/                    # Generated PNG charts
    ├── reports/                   # Generated PDF reports
    └── logs/                      # JSON run logs
```

---

## Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/MushirulX/ai-research-flow.git
cd ai-research-flow
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
NEWS_API_KEY=your_newsapi_key
GMAIL_USER=you@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json
```

### 3. Add Google credentials

Place your Google service account JSON file at the path specified in `GOOGLE_SHEETS_CREDENTIALS`.

---

## Usage

### Run the full pipeline

```bash
python main.py
```

### Validate config only (no API calls)

```bash
python main.py --dry-run
```

---

## Deployment (Modal)

This pipeline is designed to deploy on [Modal](https://modal.com) with a Monday 6:00 AM cron trigger.

```bash
pip install modal
modal deploy main.py
```

Ensure all environment variables are set as Modal secrets before deploying.

---

## Requirements

| Package | Purpose |
|---|---|
| `requests` | NewsAPI & ArXiv HTTP calls |
| `python-dotenv` | Environment variable loading |
| `matplotlib` | Chart generation |
| `reportlab` | PDF report building |
| `google-auth` + `google-api-python-client` | Google Sheets integration |
| `modal` | Cloud deployment & cron scheduling |

---

## Error Handling

| Step | On Failure |
|---|---|
| fetch_news | Stop pipeline + send failure email |
| fetch_research | Stop pipeline + send failure email |
| analyze_trends | Stop pipeline |
| generate_charts | Stop pipeline |
| generate_pdf | Stop pipeline |
| update_sheets | Log error + continue (non-blocking) |
| send_email | Retry once, then log error |

All runs produce a structured JSON log in `/temp/logs/run_YYYYMMDD_HHMMSS.json`.

---

## Security

- All secrets are stored in `.env` — never committed to version control
- `.env` and `credentials.json` are listed in `.gitignore`
- API keys are loaded via environment variables, never hardcoded
