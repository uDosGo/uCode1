"""Ceefax Teletext API — FastAPI service for teletext page rendering.

This is the primary API surface for the Ceefax container. It wraps the
CEETEX engine (from ~/Code/Vendor/ceetex/) and exposes teletext pages
as JSON, HTML, or raw teletext frames.

Endpoints:
  GET  /                    — Ceefax index page (teletext-style)
  GET  /page/{number}       — Fetch a teletext page by number
  GET  /rss/{feed}          — Render an RSS feed as teletext pages
  GET  /search?q=           — Search teletext pages
  GET  /health              — Health check
  WS   /ws                  — WebSocket for live teletext updates
"""

import os
import json
from typing import Optional, Dict, List
from fastapi import FastAPI, Query, WebSocket, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Ceefax Teletext API",
    description="Teletext page rendering service for uCode1",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# In-memory page store (teletext pages are 24 rows × 40 cols)
# ---------------------------------------------------------------------------

PAGES: Dict[int, List[str]] = {}

# Default welcome page
PAGES[100] = [
    "╔══════════════════════════════════════════╗",
    "║                                          ║",
    "║          ██████╗███████╗███████╗         ║",
    "║         ██╔════╝██╔════╝██╔════╝         ║",
    "║         ██║     █████╗  █████╗           ║",
    "║         ██║     ██╔══╝  ██╔══╝           ║",
    "║         ╚██████╗███████╗██║              ║",
    "║          ╚═════╝╚══════╝╚═╝              ║",
    "║                                          ║",
    "║           C E E F A X                    ║",
    "║     Teletext Information Service         ║",
    "║                                          ║",
    "║   Page 100  —  Welcome                   ║",
    "║                                          ║",
    "║   Enter a page number to begin:          ║",
    "║                                          ║",
    "║   101  News Headlines                    ║",
    "║   200  Weather                           ║",
    "║   300  Sports                            ║",
    "║   400  TV Guide                          ║",
    "║   500  uDos System Status                ║",
    "║   600  BBC BASIC Tutorial                ║",
    "║   700  m6502 Emulator Status             ║",
    "║                                          ║",
    "╚══════════════════════════════════════════╝",
]


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class TeletextPage(BaseModel):
    number: int
    rows: list[str]
    subtitle: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index():
    """Render the Ceefax welcome page as HTML."""
    rows = PAGES.get(100, [])
    html_rows = "\n".join(
        f"<div class='tt-row'>{row}</div>"
        for row in rows
    )
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Ceefax — Teletext Service</title>
    <link rel="stylesheet" href="/teletext-spec.css">
</head>
<body class="tt-theme-green">
    <div class="tt-frame">
        <div class="tt-header-row">═══ CEEFAX ═══</div>
        <div class="tt-body">
            {html_rows}
        </div>
        <div class="tt-footer-row">
            <a href="/page/100" class="tt-cyan">Page 100</a> ·
            <a href="/page/101" class="tt-cyan">News</a> ·
            <a href="/page/200" class="tt-cyan">Weather</a> ·
            <a href="/page/500" class="tt-cyan">uDos</a>
        </div>
    </div>
</body>
</html>"""


@app.get("/page/{page_number}", response_model=TeletextPage)
async def get_page(page_number: int):
    """Fetch a teletext page by number."""
    if page_number not in PAGES:
        raise HTTPException(status_code=404, detail=f"Page {page_number} not found")
    return TeletextPage(
        number=page_number,
        rows=PAGES[page_number],
        subtitle=f"Ceefax Page {page_number}",
    )


@app.post("/page/{page_number}")
async def set_page(page_number: int, page: TeletextPage):
    """Set a teletext page (for programmatic updates)."""
    PAGES[page_number] = page.rows
    return {"status": "ok", "page": page_number}


@app.get("/search")
async def search_pages(q: str = Query("", min_length=1)):
    """Search teletext pages for a query string."""
    results = []
    for num, rows in PAGES.items():
        for i, row in enumerate(rows):
            if q.lower() in row.lower():
                results.append({
                    "page": num,
                    "row": i,
                    "content": row.strip(),
                })
    return {"query": q, "results": results}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "pages": len(PAGES),
        "vendor_ceetex": os.path.isdir("/vendor/ceetex"),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for live teletext page updates."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "get_page":
                page_num = data.get("page", 100)
                page = PAGES.get(page_num, ["Page not found"])
                await websocket.send_json({
                    "page": page_num,
                    "rows": page,
                })
            elif data.get("action") == "set_page":
                page_num = data.get("page", 0)
                rows = data.get("rows", [])
                if page_num and rows:
                    PAGES[page_num] = rows
                    await websocket.send_json({"status": "ok", "page": page_num})
    except Exception:
        pass
