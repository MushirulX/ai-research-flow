"""
generate_flowchart.py
Generates a professional leadership-ready flowchart of the AI Research Intelligence System.
Output: temp/charts/AI_Research_Flow_Architecture.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "temp", "charts", "AI_Research_Flow_Architecture.png")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ── Colour palette ──────────────────────────────────────────────────────────
C_BG        = "#0D1117"   # page background
C_PANEL     = "#161B22"   # card fill
C_BORDER    = "#30363D"   # card border
C_ACCENT    = "#E94560"   # red accent
C_BLUE      = "#1F6FEB"   # blue accent
C_GREEN     = "#3FB950"   # success green
C_PURPLE    = "#8957E5"   # purple
C_ORANGE    = "#D29922"   # orange
C_TEAL      = "#39D0CF"   # teal
C_WHITE     = "#FFFFFF"
C_LGRAY     = "#8B949E"
C_DGRAY     = "#21262D"

fig = plt.figure(figsize=(22, 30), facecolor=C_BG)
ax  = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 22)
ax.set_ylim(0, 30)
ax.axis("off")
ax.set_facecolor(C_BG)


# ── Helper functions ────────────────────────────────────────────────────────

def rounded_box(ax, x, y, w, h, fill, border, radius=0.35, alpha=1.0, lw=1.5):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad=0,rounding_size={radius}",
                         linewidth=lw, edgecolor=border,
                         facecolor=fill, alpha=alpha, zorder=3)
    ax.add_patch(box)
    return box


def label(ax, x, y, text, size=10, color=C_WHITE, bold=False, ha="center", va="center", zorder=5):
    weight = "bold" if bold else "normal"
    ax.text(x, y, text, fontsize=size, color=color, fontweight=weight,
            ha=ha, va=va, zorder=zorder, fontfamily="monospace")


def arrow(ax, x1, y1, x2, y2, color=C_LGRAY, lw=1.8):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=lw, mutation_scale=14),
                zorder=4)


def tag_pill(ax, x, y, text, bg, fg=C_WHITE, size=7.5):
    tw = len(text) * 0.072 + 0.25
    rounded_box(ax, x - tw/2, y - 0.145, tw, 0.29, bg, bg, radius=0.12, lw=0)
    label(ax, x, y, text, size=size, color=fg, bold=True)


def step_card(ax, x, y, w, h,
              step_num, title, subtitle,
              accent, tech_tags=None, io_label=None):
    # Card shadow
    rounded_box(ax, x+0.06, y-0.06, w, h, "#000000", "#000000", alpha=0.35, lw=0)
    # Card body
    rounded_box(ax, x, y, w, h, C_PANEL, accent, radius=0.3, lw=2)
    # Left accent bar
    rounded_box(ax, x, y, 0.22, h, accent, accent, radius=0.15, lw=0)

    # Step badge
    rounded_box(ax, x+0.35, y+h-0.52, 0.52, 0.38, accent, accent, radius=0.12, lw=0)
    label(ax, x+0.61, y+h-0.335, f"0{step_num}", size=8, color=C_WHITE, bold=True)

    # Title
    label(ax, x+1.05, y+h-0.34, title, size=11.5, color=C_WHITE, bold=True, ha="left")
    # Subtitle
    label(ax, x+1.05, y+h-0.66, subtitle, size=8, color=C_LGRAY, ha="left")

    # Tech tags
    if tech_tags:
        tx = x + 1.05
        for tag, bg in tech_tags:
            tw = len(tag)*0.072 + 0.25
            tag_pill(ax, tx + tw/2, y+0.32, tag, bg)
            tx += tw + 0.18

    # IO label
    if io_label:
        label(ax, x + w - 0.25, y + h/2, io_label, size=7, color=C_LGRAY, ha="right", va="center")


# ══════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 0.6, 27.8, 20.8, 1.85, C_PANEL, C_ACCENT, radius=0.4, lw=2)
rounded_box(ax, 0.6, 27.8, 20.8, 1.85, C_ACCENT, C_ACCENT, radius=0.4, lw=0, alpha=0.08)

label(ax, 11, 29.05, "AI RESEARCH INTELLIGENCE SYSTEM", size=20, color=C_WHITE, bold=True)
label(ax, 11, 28.42, "End-to-End Automated Pipeline  ·  WAT Framework (Workflows + Agent + Tools)",
      size=10, color=C_LGRAY)

# Version + date badge
tag_pill(ax, 19.8, 29.38, "v1.0", C_DGRAY, C_LGRAY, size=8)
tag_pill(ax, 19.8, 28.82, "Feb 2026", C_DGRAY, C_LGRAY, size=8)


# ══════════════════════════════════════════════════════════════════════════
# TRIGGER BOX
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 7.5, 26.5, 7, 0.92, C_DGRAY, C_ORANGE, radius=0.3, lw=2)
label(ax, 11, 27.12, "[ TRIGGER ]", size=9.5, color=C_ORANGE, bold=True)
label(ax, 11, 26.76, "Manual Run  ·  python3 main.py", size=8.5, color=C_LGRAY)
arrow(ax, 11, 26.5, 11, 26.08, color=C_ORANGE, lw=2)


# ══════════════════════════════════════════════════════════════════════════
# LAYER LABEL — DATA INGESTION
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 0.6, 23.55, 2.8, 2.25, C_DGRAY, C_BORDER, radius=0.25, lw=1, alpha=0.7)
ax.text(2.0, 24.68, "DATA\nINGESTION", fontsize=8, color=C_LGRAY, ha="center", va="center",
        fontweight="bold", fontfamily="monospace", rotation=0)

CARD_W = 17.4
CX = 2.2   # left edge of cards

# ── STEP 1 — Fetch News ───────────────────────────────────────────────────
step_card(ax, CX, 24.35, CARD_W, 1.28,
          step_num=1,
          title="Fetch AI News",
          subtitle="Retrieve top AI & ML headlines from the past 7 days",
          accent=C_BLUE,
          tech_tags=[("NewsAPI", C_BLUE), ("REST", C_DGRAY), ("JSON", C_DGRAY)],
          io_label="→ 49 articles")

arrow(ax, 11, 24.35, 11, 24.0, color=C_BLUE, lw=2)

# ── STEP 2 — Fetch Research ───────────────────────────────────────────────
step_card(ax, CX, 22.72, CARD_W, 1.28,
          step_num=2,
          title="Fetch Research Papers",
          subtitle="Query ArXiv API for latest AI research publications",
          accent=C_BLUE,
          tech_tags=[("ArXiv API", C_BLUE), ("XML Parsing", C_DGRAY), ("JSON", C_DGRAY)],
          io_label="→ 30 papers")

arrow(ax, 11, 22.72, 11, 22.37, color=C_BLUE, lw=2)


# ══════════════════════════════════════════════════════════════════════════
# LAYER LABEL — INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 0.6, 19.62, 2.8, 2.45, C_DGRAY, C_BORDER, radius=0.25, lw=1, alpha=0.7)
ax.text(2.0, 20.85, "INTEL\nPROCESSING", fontsize=8, color=C_LGRAY, ha="center", va="center",
        fontweight="bold", fontfamily="monospace")

# ── STEP 3 — Analyze Trends ───────────────────────────────────────────────
step_card(ax, CX, 21.09, CARD_W, 1.28,
          step_num=3,
          title="Analyze Trends & Keywords",
          subtitle="NLP keyword extraction · Theme detection · Summary statistics",
          accent=C_PURPLE,
          tech_tags=[("NLP", C_PURPLE), ("Counter", C_DGRAY), ("Regex", C_DGRAY),
                     ("Theme Engine", C_PURPLE)],
          io_label="→ Top 20 keywords")

arrow(ax, 11, 21.09, 11, 20.74, color=C_PURPLE, lw=2)

# ── STEP 4 — Generate Charts ──────────────────────────────────────────────
step_card(ax, CX, 19.46, CARD_W, 1.28,
          step_num=4,
          title="Generate Visual Charts",
          subtitle="Keyword frequency bar  ·  Theme distribution pie  ·  Volume trend chart",
          accent=C_PURPLE,
          tech_tags=[("Matplotlib", C_PURPLE), ("PNG 150dpi", C_DGRAY), ("3 Charts", C_DGRAY)],
          io_label="→ /temp/charts/")

arrow(ax, 11, 19.46, 11, 19.11, color=C_PURPLE, lw=2)


# ══════════════════════════════════════════════════════════════════════════
# LAYER LABEL — REPORTING
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 0.6, 17.82, 2.8, 1.0, C_DGRAY, C_BORDER, radius=0.25, lw=1, alpha=0.7)
ax.text(2.0, 18.32, "REPORTING", fontsize=8, color=C_LGRAY, ha="center", va="center",
        fontweight="bold", fontfamily="monospace")

# ── STEP 5 — Generate PDF ─────────────────────────────────────────────────
step_card(ax, CX, 17.83, CARD_W, 1.28,
          step_num=5,
          title="Generate Branded PDF Report",
          subtitle="4-page branded report: Executive summary · Keywords · Articles · Papers",
          accent=C_ACCENT,
          tech_tags=[("ReportLab", C_ACCENT), ("4 Pages", C_DGRAY), ("Branded", C_DGRAY)],
          io_label="→ /temp/reports/")

# ── FORK arrow ────────────────────────────────────────────────────────────
arrow(ax, 11, 17.83, 11, 17.56, color=C_ACCENT, lw=2)
# horizontal fork line
ax.plot([6.2, 15.8], [17.3, 17.3], color=C_LGRAY, lw=1.8, zorder=4)
arrow(ax, 6.2, 17.3, 6.2, 17.07, color=C_GREEN, lw=2)
arrow(ax, 15.8, 17.3, 15.8, 17.07, color=C_TEAL, lw=2)


# ══════════════════════════════════════════════════════════════════════════
# LAYER LABEL — DELIVERY
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 0.6, 14.6, 2.8, 2.2, C_DGRAY, C_BORDER, radius=0.25, lw=1, alpha=0.7)
ax.text(2.0, 15.7, "DELIVERY\n& AUDIT", fontsize=8, color=C_LGRAY, ha="center", va="center",
        fontweight="bold", fontfamily="monospace")

# ── STEP 6 — Google Sheets (left) ────────────────────────────────────────
step_card(ax, CX, 15.79, 8.1, 1.28,
          step_num=6,
          title="Update Google Sheets",
          subtitle="Append run summary row · Auto-create 'Run Log' tab",
          accent=C_GREEN,
          tech_tags=[("Sheets API v4", C_GREEN), ("Service Account", C_DGRAY)])

# ── STEP 7 — Send Email (right) ──────────────────────────────────────────
step_card(ax, 11.5, 15.79, 8.1, 1.28,
          step_num=7,
          title="Send Email Report",
          subtitle="HTML email + PDF attachment → all recipients",
          accent=C_TEAL,
          tech_tags=[("Gmail SMTP", C_TEAL), ("App Password", C_DGRAY)])

# ── Merge arrows → Step 8 ────────────────────────────────────────────────
arrow(ax, 6.2, 15.79, 6.2, 15.52, color=C_GREEN, lw=2)
arrow(ax, 15.8, 15.79, 15.8, 15.52, color=C_TEAL, lw=2)
ax.plot([6.2, 15.8], [15.52, 15.52], color=C_LGRAY, lw=1.8, zorder=4)
arrow(ax, 11, 15.52, 11, 15.3, color=C_LGRAY, lw=2)


# ── STEP 8 — Log Summary ─────────────────────────────────────────────────
step_card(ax, CX, 14.02, CARD_W, 1.28,
          step_num=8,
          title="Write Run Log",
          subtitle="JSON structured log: Run ID · Timings · Article count · Keywords · Status",
          accent=C_ORANGE,
          tech_tags=[("JSON", C_ORANGE), ("/temp/logs/", C_DGRAY)],
          io_label="→ run_YYYYMMDD.json")


# ══════════════════════════════════════════════════════════════════════════
# OUTPUT SUMMARY ROW
# ══════════════════════════════════════════════════════════════════════════
arrow(ax, 11, 14.02, 11, 13.6, color=C_ORANGE, lw=2)

outputs = [
    ("PDF Report",      "/temp/reports/",   C_ACCENT),
    ("3 Charts",        "/temp/charts/",    C_PURPLE),
    ("Google Sheet Row","Run Log tab",      C_GREEN),
    ("Email Delivered", "2 recipients",     C_TEAL),
    ("Run Log JSON",    "/temp/logs/",      C_ORANGE),
]
ow = 3.6
ox_start = 1.5
oy = 12.6

for i, (title, sub, color) in enumerate(outputs):
    ox = ox_start + i * (ow + 0.25)
    rounded_box(ax, ox, oy, ow, 0.85, C_DGRAY, color, radius=0.2, lw=1.5)
    rounded_box(ax, ox, oy + 0.6, ow, 0.25, color, color, radius=0.12, lw=0, alpha=0.3)
    label(ax, ox + ow/2, oy + 0.71, title, size=8.5, color=color, bold=True)
    label(ax, ox + ow/2, oy + 0.26, sub, size=7.5, color=C_LGRAY)

label(ax, 11, 13.35, "PIPELINE OUTPUTS", size=9, color=C_LGRAY, bold=True)


# ══════════════════════════════════════════════════════════════════════════
# WAT FRAMEWORK LEGEND (bottom left)
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 0.6, 9.3, 6.8, 2.95, C_PANEL, C_BORDER, radius=0.3, lw=1.5)
label(ax, 4.0, 12.0, "WAT FRAMEWORK", size=9, color=C_LGRAY, bold=True)

wat = [
    ("W", "WORKFLOWS",  "weekly_ai_report.md defines step order & I/O contracts", C_ACCENT),
    ("A", "AGENT",      "main.py orchestrates, passes JSON, handles failures",     C_BLUE),
    ("T", "TOOLS",      "7 Python modules — one responsibility each",              C_GREEN),
]
for i, (letter, name, desc, color) in enumerate(wat):
    wy = 11.35 - i * 0.82
    rounded_box(ax, 0.9, wy - 0.2, 0.48, 0.48, color, color, radius=0.1, lw=0)
    label(ax, 1.14, wy + 0.04, letter, size=11, color=C_WHITE, bold=True)
    label(ax, 2.0, wy + 0.12, name, size=8.5, color=C_WHITE, bold=True, ha="left")
    label(ax, 2.0, wy - 0.12, desc, size=7, color=C_LGRAY, ha="left")


# ══════════════════════════════════════════════════════════════════════════
# DATA FLOW STANDARD (bottom centre)
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 8.1, 9.3, 6.0, 2.95, C_PANEL, C_BORDER, radius=0.3, lw=1.5)
label(ax, 11.1, 12.0, "DATA FLOW STANDARD", size=9, color=C_LGRAY, bold=True)

standards = [
    ("Structured JSON between every tool",  C_WHITE),
    ("Max 3 API retries with backoff",       C_WHITE),
    ("Secrets via .env — never hardcoded",  C_WHITE),
    ("Non-blocking: Sheets failure ≠ stop", C_WHITE),
    ("All outputs timestamped & logged",    C_WHITE),
]
for i, (txt, color) in enumerate(standards):
    sy = 11.45 - i * 0.48
    ax.plot([8.35, 8.6], [sy, sy], color=C_ACCENT, lw=1.5, zorder=5)
    label(ax, 8.75, sy, txt, size=7.8, color=color, ha="left")


# ══════════════════════════════════════════════════════════════════════════
# TECH STACK (bottom right)
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 14.8, 9.3, 6.6, 2.95, C_PANEL, C_BORDER, radius=0.3, lw=1.5)
label(ax, 18.1, 12.0, "TECHNOLOGY STACK", size=9, color=C_LGRAY, bold=True)

techs = [
    ("Python 3.14",      C_BLUE),
    ("NewsAPI",          C_BLUE),
    ("ArXiv API",        C_BLUE),
    ("Matplotlib",       C_PURPLE),
    ("ReportLab",        C_ACCENT),
    ("Google Sheets API",C_GREEN),
    ("Gmail SMTP SSL",   C_TEAL),
    ("python-dotenv",    C_ORANGE),
]
cols = 2
for i, (name, color) in enumerate(techs):
    col = i % cols
    row = i // cols
    tx = 15.1 + col * 3.1
    ty = 11.45 - row * 0.54
    tw = len(name)*0.068 + 0.3
    rounded_box(ax, tx, ty-0.16, tw, 0.35, C_DGRAY, color, radius=0.1, lw=1)
    label(ax, tx + tw/2, ty + 0.015, name, size=7.5, color=color, bold=True)


# ══════════════════════════════════════════════════════════════════════════
# ERROR HANDLING CALLOUT (right side of main flow)
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 19.85, 17.5, 1.85, 7.2, C_PANEL, C_BORDER, radius=0.3, lw=1.5)
ax.text(20.775, 24.45, "ERROR\nHANDLING", fontsize=7.5, color=C_LGRAY, ha="center", va="center",
        fontweight="bold", fontfamily="monospace")

errors = [
    ("API fail", "Stop + alert", C_ACCENT),
    ("PDF fail", "Stop",         C_ACCENT),
    ("Sheets",   "Continue",     C_ORANGE),
    ("Email",    "Retry ×1",     C_ORANGE),
]
for i, (trigger, action, color) in enumerate(errors):
    ey = 23.6 - i * 1.45
    rounded_box(ax, 20.0, ey - 0.35, 1.55, 1.1, C_DGRAY, color, radius=0.15, lw=1.2)
    label(ax, 20.775, ey + 0.38, trigger, size=7, color=color, bold=True)
    label(ax, 20.775, ey + 0.02, "↓", size=8, color=C_LGRAY)
    label(ax, 20.775, ey - 0.24, action, size=7, color=C_LGRAY)


# ══════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════
rounded_box(ax, 0.6, 8.85, 20.8, 0.5, C_DGRAY, C_BORDER, radius=0.2, lw=1)
label(ax, 4.0,  9.12, "AI Research Intelligence System  ·  Architecture v1.0", size=8, color=C_LGRAY)
label(ax, 11.0, 9.12, "Confidential — Internal Use Only", size=8, color=C_LGRAY)
label(ax, 18.5, 9.12, "February 2026", size=8, color=C_LGRAY)

# ══════════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════════
fig.savefig(OUTPUT_PATH, dpi=180, bbox_inches="tight",
            facecolor=C_BG, edgecolor="none")
plt.close(fig)
print(f"Flowchart saved → {OUTPUT_PATH}")
