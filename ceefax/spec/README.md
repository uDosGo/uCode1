# Ceefax Container — Teletext RSS Reader Service

## Overview

Ceefax is a containerised teletext information service for uCode1. It wraps
the CEETEX engine (from `~/Code/Vendor/ceetex/`) and exposes teletext pages
via a FastAPI service with LENS/SKIN/MCP adapters and GridUI surface mapping.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Ceefax Container                  │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  ENGINE   │  │   LENS   │  │   SKIN   │           │
│  │ teletext  │  │ renderer │  │  themes  │           │
│  │   API     │  │  (HTML,  │  │ (green,  │           │
│  │ (FastAPI) │  │  ANSI,   │  │  amber,  │           │
│  │           │  │  cells)  │  │  white)  │           │
│  └─────┬─────┘  └────┬─────┘  └────┬─────┘           │
│        │              │              │                │
│  ┌─────┴──────────────┴──────────────┴─────┐          │
│  │              MCP Adapter                 │          │
│  │   (Model Context Protocol for AI agents) │          │
│  └─────────────────────┬────────────────────┘          │
│                        │                               │
│  ┌─────────────────────┴────────────────────┐          │
│  │              GridUI Surface               │          │
│  │   (24x40 cell grid for uCode1 display)   │          │
│  └──────────────────────────────────────────┘          │
│                                                      │
│  Vendor: ~/Code/Vendor/ceetex/ (mounted at runtime)  │
└─────────────────────────────────────────────────────┘
```

## Components

### Engine (`engine/`)
- `teletext_api.py` — FastAPI service with REST + WebSocket endpoints
- In-memory page store (24 rows x 40 cols per page)
- Page numbers: 100-899

### LENS (`lens/`)
- `renderer.py` — Transforms teletext frames into HTML, ANSI, raw, or grid cells
- Supports Teletext50 font family

### SKIN (`skin/`)
- `themes.py` — Visual colour schemes (green, amber, white, condensed)
- CSS generation for HTML rendering

### MCP (`mcp/`)
- `adapter.py` — MCP resource/tool definitions for AI agent integration
- Tools: `ceefax_get_page`, `ceefax_set_page`, `ceefax_search`

### GridUI (`gridui/`)
- `surface.py` — 24x40 cell grid mapping for uCode1 display
- Load/save/clear cell operations

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Ceefax index page (HTML) |
| GET | `/page/{number}` | Fetch teletext page (JSON) |
| POST | `/page/{number}` | Set teletext page |
| GET | `/search?q=` | Search pages |
| GET | `/health` | Health check |
| WS | `/ws` | WebSocket for live updates |

## Page Numbering

| Range | Content |
|-------|---------|
| 100 | Index / Welcome |
| 101-199 | News |
| 200-299 | Weather |
| 300-399 | Sports |
| 400-499 | TV Guide |
| 500-599 | uDos System Status |
| 600-699 | BBC BASIC Tutorial |
| 700-799 | m6502 Emulator Status |
| 800-899 | User-defined |

## Running

```bash
# Build
docker build -t ceefax:latest .

# Run with Vendor CEETEX mount
docker run -p 8080:8080 \
  -v ~/Code/Vendor/ceetex:/vendor/ceetex \
  ceefax:latest

# Or run directly (without Docker)
cd ceefax
pip install fastapi uvicorn httpx websockets
uvicorn engine.teletext_api:app --host 0.0.0.0 --port 8080
```

## Vendor Dependency

This container requires the CEETEX engine from `~/Code/Vendor/ceetex/`.
The Vendor repo is mounted at runtime — it is not copied into the container image.
