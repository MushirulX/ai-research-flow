# Claude Agent Instructions
Project: AI Research Intelligence System

You are operating inside a structured automation system using the WAT Framework.

WAT = Workflows + Agent + Tools

This project monitors AI news and research weekly,
analyzes trends,
generates a branded PDF report,
updates Google Sheets,
and emails stakeholders.

------------------------------------------------------------
SYSTEM PURPOSE
------------------------------------------------------------

Automatically:
1. Fetch AI news (past 7 days)
2. Fetch AI research papers (ArXiv)
3. Analyze trends and keywords
4. Generate charts
5. Create branded PDF report
6. Update tracking Google Sheet
7. Email final report

This workflow runs weekly via cron trigger.

------------------------------------------------------------
WAT STRUCTURE
------------------------------------------------------------

Layer 1 — Workflows
Location: /workflows
- Written in Markdown
- Define ordered steps
- Define required tools
- Define expected outputs
- Define failure handling

Primary Workflow:
weekly_ai_report.md

Layer 2 — Agent (You)
- Read workflow fully
- Identify tools required
- Execute tools sequentially
- Pass structured JSON between tools
- Handle failures
- Log progress

Layer 3 — Tools
Location: /tools
- Written in Python
- Perform deterministic actions
- Return structured outputs
- Never contain business logic decisions

------------------------------------------------------------
PROJECT LAYOUT
------------------------------------------------------------

Root:

- claude.md
- PROJECT_OVERVIEW.md
- SYSTEM_ARCHITECTURE.md
- WORKFLOW_SPEC.md
- TOOL_SPEC.md
- DEPLOYMENT_PLAN.md

Folders:

/workflows
    weekly_ai_report.md

/tools
    fetch_news.py
    fetch_research.py
    analyze_trends.py
    generate_charts.py
    generate_pdf.py
    update_sheets.py
    send_email.py

/temp
    charts/
    reports/
    logs/

/.env
    NEWS_API_KEY
    GMAIL_CREDENTIALS
    GOOGLE_SHEETS_CREDENTIALS

------------------------------------------------------------
WORKFLOW EXECUTION PROTOCOL
------------------------------------------------------------

When weekly_ai_report is triggered:

1. Fetch AI news from past 7 days
2. Fetch AI research papers from ArXiv
3. Merge datasets
4. Analyze keyword frequency
5. Identify trending themes
6. Generate summary metrics
7. Create visual charts
8. Build branded PDF report
9. Save PDF in /temp/reports
10. Update Google Sheets
11. Send email with PDF attached
12. Log run summary

Execution must be deterministic.

------------------------------------------------------------
DATA FLOW STANDARD
------------------------------------------------------------

- Tools must pass structured JSON outputs.
- No raw unstructured text between tools.
- Validate data before passing forward.
- Charts saved in /temp/charts.
- Reports saved in /temp/reports.

------------------------------------------------------------
TOOL STANDARDS
------------------------------------------------------------

Each tool must:

- Do only one responsibility
- Accept structured input
- Return structured JSON
- Handle exceptions
- Retry API calls (max 3 times)
- Respect rate limits
- Never expose secrets

------------------------------------------------------------
ERROR HANDLING POLICY
------------------------------------------------------------

If API limit reached:
- Log error
- Stop execution
- Send failure email

If PDF generation fails:
- Log error
- Stop execution

If email fails:
- Retry once
- Log error

------------------------------------------------------------
SECURITY RULES
------------------------------------------------------------

- Secrets must be stored in .env
- Never print API keys
- Never commit .env to repository
- Use environment variables in tools
- Sanitize all external inputs

------------------------------------------------------------
OPTIMIZATION RULES
------------------------------------------------------------

- Batch API requests if possible
- Avoid redundant calls
- Cache intermediate results
- Keep tools modular

------------------------------------------------------------
DEPLOYMENT REQUIREMENTS
------------------------------------------------------------

Before deployment:

- Ensure environment variables externalized
- Ensure file paths are cloud-safe
- Ensure idempotent workflow
- Ensure logs are structured
- Ensure no local-only dependencies

Deployment Target:
Modal

Trigger:
Cron — Monday 6:00 AM

------------------------------------------------------------
LOGGING STANDARD
------------------------------------------------------------

Each run must log:

- Start time
- End time
- Number of news articles processed
- Number of research papers processed
- Top 5 keywords
- PDF file path
- Email status

Logs stored in /temp/logs

------------------------------------------------------------
IMPROVEMENT LOOP
------------------------------------------------------------

If failure occurs:

1. Diagnose
2. Improve tool
3. Retest tool
4. Update workflow documentation
5. Confirm success

Maintain separation of concerns at all times.

Agent reasons.
Workflow defines.
Tools execute.