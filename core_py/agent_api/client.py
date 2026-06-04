"""
BYO Agent Client Library for uCode1

Client library for external agents (LLMs, automation tools) to interact
with the uCode1 Agent API. Provides a clean Python interface for MCP
commands, teletext page streaming, and spool operations.

Usage:
    from ucode1.agent_api.client import UCode1AgentClient

    client = UCode1AgentClient()
    status = await client.health()
    result = await client.mcp_command("ceetex", "PAGE", page="101")
    page = await client.get_teletext_page("ceetex")
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

import httpx
import websockets


class UCode1AgentClient:
    """
    Client library for the uCode1 Agent API.
    
    Provides methods for all API endpoints including MCP commands,
    teletext feed access, WebSocket streaming, and spool operations.
    
    Args:
        base_url: Base URL of the Agent API server
        timeout: HTTP request timeout in seconds
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self._http = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def close(self) -> None:
        """Close the HTTP client session"""
        await self._http.aclose()

    async def __aenter__(self) -> "UCode1AgentClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    # ── Health ─────────────────────────────────────────────────────

    async def health(self) -> Dict[str, Any]:
        """
        Check the Agent API health.
        
        Returns:
            Health status dict
        """
        response = await self._http.get("/health")
        response.raise_for_status()
        return response.json()

    # ── Snack Management ───────────────────────────────────────────

    async def list_snacks(self) -> List[Dict[str, Any]]:
        """
        List all registered snacks.
        
        Returns:
            List of snack info dicts
        """
        response = await self._http.get("/snacks")
        response.raise_for_status()
        return response.json().get("snacks", [])

    async def snack_status(self, snack_id: str) -> Dict[str, Any]:
        """
        Get status of a running snack.
        
        Args:
            snack_id: Snack identifier
            
        Returns:
            Snack status dict
        """
        response = await self._http.get(f"/snacks/{snack_id}/status")
        response.raise_for_status()
        return response.json()

    # ── MCP Commands ───────────────────────────────────────────────

    async def mcp_command(self, snack_id: str, command: str, **args) -> Dict[str, Any]:
        """
        Send an MCP command to a running snack.
        
        Args:
            snack_id: Snack identifier
            command: MCP command name (PAGE, NEXT, PREV, REVEAL, SAVE, LOAD, etc.)
            **args: Command arguments
            
        Returns:
            Command response dict
        """
        response = await self._http.post(
            f"/mcp/{snack_id}",
            json={"command": command, "args": args},
        )
        response.raise_for_status()
        return response.json()

    async def page(self, snack_id: str, page_number: int) -> Dict[str, Any]:
        """
        Convenience: Navigate to a teletext page.
        
        Args:
            snack_id: Snack identifier
            page_number: Page number (100-899)
            
        Returns:
            Command response
        """
        return await self.mcp_command(snack_id, "PAGE", page=str(page_number))

    async def next_page(self, snack_id: str) -> Dict[str, Any]:
        """Go to the next page in sequence"""
        return await self.mcp_command(snack_id, "NEXT")

    async def prev_page(self, snack_id: str) -> Dict[str, Any]:
        """Go to the previous page in sequence"""
        return await self.mcp_command(snack_id, "PREV")

    async def reveal(self, snack_id: str) -> Dict[str, Any]:
        """Toggle concealed text reveal"""
        return await self.mcp_command(snack_id, "REVEAL")

    # ── Teletext Feed ──────────────────────────────────────────────

    async def get_teletext_page(self, snack_id: str) -> Dict[str, Any]:
        """
        Get the current teletext page as structured data.
        
        Args:
            snack_id: Snack identifier
            
        Returns:
            Teletext page data with grid, attributes, and metadata
        """
        response = await self._http.get(f"/feed/{snack_id}/teletext")
        response.raise_for_status()
        return response.json()

    # ── WebSocket Feed ─────────────────────────────────────────────

    async def stream_teletext(
        self, snack_id: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream teletext updates via WebSocket.
        
        Yields teletext update dicts as they arrive from the server.
        Also accepts incoming MCP commands sent as JSON.
        
        Args:
            snack_id: Snack identifier
            
        Yields:
            Teletext update dicts
        """
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/ws/{snack_id}"

        async with websockets.connect(ws_url) as ws:
            while True:
                try:
                    message = await ws.recv()
                    if isinstance(message, str):
                        yield json.loads(message)
                except websockets.exceptions.ConnectionClosed:
                    break

    async def send_command_via_websocket(
        self, snack_id: str, command: str, **args
    ) -> None:
        """
        Send an MCP command via the WebSocket connection.
        
        Note: This requires an active stream_teletext() connection.
        Use the HTTP mcp_command() method for standalone commands.
        
        Args:
            snack_id: Snack identifier
            command: MCP command name
            **args: Command arguments
        """
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/ws/{snack_id}"

        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"command": command, "args": args}))

    # ── Spool Operations ───────────────────────────────────────────

    async def save_game(self, snack_id: str, slot: str = "auto") -> Dict[str, Any]:
        """
        Save current teletext state to spool.
        
        Args:
            snack_id: Snack identifier
            slot: Save slot name (default: "auto")
            
        Returns:
            Spool save response with spool_id
        """
        response = await self._http.post(
            f"/spool/{snack_id}/save",
            params={"slot": slot},
        )
        response.raise_for_status()
        return response.json()

    async def load_game(self, snack_id: str, spool_id: str) -> Dict[str, Any]:
        """
        Load teletext state from spool.
        
        Args:
            snack_id: Snack identifier
            spool_id: Spool file identifier
            
        Returns:
            Spool load response
        """
        response = await self._http.post(
            f"/spool/{snack_id}/load",
            params={"spool_id": spool_id},
        )
        response.raise_for_status()
        return response.json()

    # ── Skin Management ────────────────────────────────────────────

    async def list_skins(self, snack_id: str) -> Dict[str, Any]:
        """
        List available skins for a snack.
        
        Args:
            snack_id: Snack identifier
            
        Returns:
            Dict with active and available skins
        """
        response = await self._http.get(f"/snacks/{snack_id}/skins")
        response.raise_for_status()
        return response.json()

    async def apply_skin(self, snack_id: str, skin_name: str) -> Dict[str, Any]:
        """
        Apply a skin to a running snack.
        
        Args:
            snack_id: Snack identifier
            skin_name: Name of the skin to apply
            
        Returns:
            Response dict
        """
        response = await self._http.post(f"/snacks/{snack_id}/skins/{skin_name}")
        response.raise_for_status()
        return response.json()

    # ── Agent Convenience Methods ──────────────────────────────────

    async def get_screen_text(self, snack_id: str) -> str:
        """
        Get the current teletext screen as plain text.
        
        Useful for LLM agents that need to read the screen content.
        
        Args:
            snack_id: Snack identifier
            
        Returns:
            Plain text representation of the teletext screen
        """
        page = await self.get_teletext_page(snack_id)
        grid = page.get("grid", [])
        lines = []
        for row in grid:
            line = "".join(cell.get("char", " ") for cell in row)
            lines.append(line)
        return "\n".join(lines)

    async def get_status_summary(self, snack_id: str) -> str:
        """
        Get a human-readable status summary for an agent.
        
        Args:
            snack_id: Snack identifier
            
        Returns:
            Formatted status string
        """
        status = await self.snack_status(snack_id)
        return (
            f"Snack: {snack_id}\n"
            f"Running: {status.get('running', False)}\n"
            f"Current Page: {status.get('current_page', 'N/A')}\n"
            f"View Mode: {status.get('view_mode', 'N/A')}\n"
            f"Active Skin: {status.get('active_skin', 'N/A')}\n"
            f"Available Skins: {', '.join(status.get('available_skins', []))}"
        )


# ── Convenience Functions ──────────────────────────────────────────

async def quick_command(snack_id: str, command: str, **args) -> Dict[str, Any]:
    """
    Quick one-shot MCP command.
    
    Creates a temporary client, sends the command, and closes.
    
    Args:
        snack_id: Snack identifier
        command: MCP command name
        **args: Command arguments
        
    Returns:
        Command response
    """
    async with UCode1AgentClient() as client:
        return await client.mcp_command(snack_id, command, **args)


async def quick_page(snack_id: str, page_number: int) -> Dict[str, Any]:
    """Quick one-shot page navigation"""
    return await quick_command(snack_id, "PAGE", page=str(page_number))


async def quick_status(snack_id: str) -> str:
    """Quick one-shot status summary"""
    async with UCode1AgentClient() as client:
        return await client.get_status_summary(snack_id)
