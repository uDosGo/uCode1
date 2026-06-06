"""Ceefax MCP Adapter — exposes teletext pages as MCP resources and tools.

This adapter allows AI agents to:
  - Read teletext pages as MCP resources
  - Write teletext pages via MCP tools
  - Search teletext content
  - Subscribe to page updates via WebSocket
"""

from typing import Any, Dict, List, Optional


class CeefaxMCPAdapter:
    """MCP adapter for Ceefax teletext pages."""

    def __init__(self, api_base: str = "http://localhost:8080"):
        self.api_base = api_base

    # ------------------------------------------------------------------
    # MCP Resource definitions
    # ------------------------------------------------------------------

    @property
    def resources(self) -> List[Dict[str, Any]]:
        """MCP resource definitions for Ceefax pages."""
        return [
            {
                "uri": f"ceefax://page/{n}",
                "name": f"Ceefax Page {n}",
                "description": f"Teletext page {n}",
                "mimeType": "text/plain",
            }
            for n in [100, 101, 200, 300, 400, 500, 600, 700]
        ]

    # ------------------------------------------------------------------
    # MCP Tool definitions
    # ------------------------------------------------------------------

    @property
    def tools(self) -> List[Dict[str, Any]]:
        """MCP tool definitions for Ceefax operations."""
        return [
            {
                "name": "ceefax_get_page",
                "description": "Fetch a teletext page by number",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "page_number": {
                            "type": "integer",
                            "description": "Teletext page number (100-899)",
                        }
                    },
                    "required": ["page_number"],
                },
            },
            {
                "name": "ceefax_set_page",
                "description": "Set the content of a teletext page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "page_number": {
                            "type": "integer",
                            "description": "Teletext page number (100-899)",
                        },
                        "rows": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "24 rows of 40 characters each",
                        },
                    },
                    "required": ["page_number", "rows"],
                },
            },
            {
                "name": "ceefax_search",
                "description": "Search teletext pages for a query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query string",
                        }
                    },
                    "required": ["query"],
                },
            },
        ]

    # ------------------------------------------------------------------
    # MCP Tool implementations
    # ------------------------------------------------------------------

    async def get_page(self, page_number: int) -> Dict[str, Any]:
        """Fetch a teletext page."""
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_base}/page/{page_number}")
            resp.raise_for_status()
            return resp.json()

    async def set_page(self, page_number: int, rows: List[str]) -> Dict[str, Any]:
        """Set a teletext page."""
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.api_base}/page/{page_number}",
                json={"number": page_number, "rows": rows},
            )
            resp.raise_for_status()
            return resp.json()

    async def search(self, query: str) -> Dict[str, Any]:
        """Search teletext pages."""
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.api_base}/search",
                params={"q": query},
            )
            resp.raise_for_status()
            return resp.json()
