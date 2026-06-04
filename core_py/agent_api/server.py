"""
BYO Agent API for uCode1 — FastAPI + WebSocket endpoints

Provides HTTP and WebSocket endpoints for external agents (LLMs, automation tools)
to interact with uCode1 teletext snacks. Supports MCP commands, teletext page
streaming, and spool save/load operations.

Usage:
    # Start the API server
    python -m ucode1.agent_api.server

    # Or programmatically
    from ucode1.agent_api.server import create_app
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..ceefax.ceetex_app import CeetexUCodeApp
from ..ceefax.mcp_protocol import CeefaxMCPProtocol, CeefaxCommandType
from ..ceefax.spool import CeefaxSpool
from ..ceefax.bridge import TeletextGrid

logger = logging.getLogger(__name__)

# ── Pydantic Models ────────────────────────────────────────────────

class MCPCommandRequest(BaseModel):
    """MCP command request from an agent"""
    command: str
    args: Dict[str, Any] = {}

class MCPCommandResponse(BaseModel):
    """Response to an MCP command"""
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TeletextPageResponse(BaseModel):
    """Teletext page data"""
    page_number: int
    title: str
    subtitle: str
    grid: List[List[Dict[str, Any]]]
    timestamp: str

class SpoolSaveResponse(BaseModel):
    """Response to a spool save operation"""
    spool_id: str
    slot: str
    page_count: int

class SpoolLoadResponse(BaseModel):
    """Response to a spool load operation"""
    status: str
    pages_loaded: int

class SnackStatus(BaseModel):
    """Status of a running snack"""
    snack_id: str
    running: bool
    current_page: int
    view_mode: str
    active_skin: str
    available_skins: List[str]

# ── Snack Manager ──────────────────────────────────────────────────

class SnackManager:
    """
    Manages running uCode1 snack instances for the Agent API.
    
    Each snack gets its own CeetexUCodeApp instance and MCP protocol handler.
    """

    def __init__(self):
        self._snacks: Dict[str, Dict[str, Any]] = {}
        self._spool = CeefaxSpool()

    def register_snack(self, snack_id: str, app: CeetexUCodeApp) -> None:
        """Register a running snack instance"""
        self._snacks[snack_id] = {
            "app": app,
            "mcp": CeefaxMCPProtocol(),
            "started": datetime.now().isoformat(),
        }
        logger.info(f"Snack registered: {snack_id}")

    def unregister_snack(self, snack_id: str) -> bool:
        """Unregister a snack instance"""
        if snack_id in self._snacks:
            del self._snacks[snack_id]
            logger.info(f"Snack unregistered: {snack_id}")
            return True
        return False

    def get_snack(self, snack_id: str) -> Optional[Dict[str, Any]]:
        """Get a registered snack instance"""
        return self._snacks.get(snack_id)

    def list_snacks(self) -> List[Dict[str, Any]]:
        """List all registered snacks"""
        return [
            {
                "snack_id": sid,
                "running": True,
                "started": info["started"],
            }
            for sid, info in self._snacks.items()
        ]

    def get_mcp(self, snack_id: str) -> Optional[CeefaxMCPProtocol]:
        """Get the MCP protocol handler for a snack"""
        snack = self._snacks.get(snack_id)
        return snack["mcp"] if snack else None

    def get_app(self, snack_id: str) -> Optional[CeetexUCodeApp]:
        """Get the CeetexUCodeApp for a snack"""
        snack = self._snacks.get(snack_id)
        return snack["app"] if snack else None

    @property
    def spool(self) -> CeefaxSpool:
        """Get the shared spool manager"""
        return self._spool


# ── FastAPI App Factory ────────────────────────────────────────────

def create_app(snack_manager: Optional[SnackManager] = None) -> FastAPI:
    """
    Create the FastAPI application with all routes.
    
    Args:
        snack_manager: Optional SnackManager instance (creates one if omitted)
    
    Returns:
        Configured FastAPI app
    """
    manager = snack_manager or SnackManager()

    app = FastAPI(
        title="uCode1 Agent API",
        description="BYO Agent interface for uCode1 teletext snacks",
        version="1.0.0",
    )

    # CORS — allow any origin for agent integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Health ─────────────────────────────────────────────────────

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "ok",
            "service": "uCode1 Agent API",
            "version": "1.0.0",
            "snacks_running": len(manager.list_snacks()),
            "timestamp": datetime.now().isoformat(),
        }

    # ── Snack Management ───────────────────────────────────────────

    @app.get("/snacks")
    async def list_snacks():
        """List all registered snacks"""
        return {"snacks": manager.list_snacks()}

    @app.get("/snacks/{snack_id}/status")
    async def snack_status(snack_id: str):
        """Get status of a running snack"""
        app_instance = manager.get_app(snack_id)
        if not app_instance:
            raise HTTPException(status_code=404, detail=f"Snack not found: {snack_id}")

        return SnackStatus(
            snack_id=snack_id,
            running=app_instance.is_mounted,
            current_page=int(app_instance.current_page_id),
            view_mode=app_instance.view_mode,
            active_skin=app_instance.skin_adapter.active_skin_name,
            available_skins=app_instance.skin_adapter.available_skins,
        )

    # ── MCP Commands ───────────────────────────────────────────────

    @app.post("/mcp/{snack_id}")
    async def send_mcp_command(snack_id: str, request: MCPCommandRequest):
        """Send an MCP command to a running snack"""
        mcp = manager.get_mcp(snack_id)
        if not mcp:
            raise HTTPException(status_code=404, detail=f"Snack not found: {snack_id}")

        # Queue the command
        cmd = mcp.queue_command(f"{request.command} {json.dumps(request.args)}")

        # Process it
        response = mcp.process_command(cmd)

        if response and response.success:
            return MCPCommandResponse(
                status="ok",
                result={
                    "result": response.result,
                    "page_number": response.page_number,
                },
            )
        elif response:
            return MCPCommandResponse(
                status="error",
                error=response.error or "Command failed",
            )
        else:
            return MCPCommandResponse(
                status="ok",
                result={"message": f"Command queued: {request.command}"},
            )

    # ── Teletext Feed ──────────────────────────────────────────────

    @app.get("/feed/{snack_id}/teletext")
    async def get_teletext_feed(snack_id: str):
        """Get current teletext page as structured data"""
        app_instance = manager.get_app(snack_id)
        if not app_instance:
            raise HTTPException(status_code=404, detail=f"Snack not found: {snack_id}")

        state = app_instance.get_lens_state()
        grid = state.get("headlines", [])

        return TeletextPageResponse(
            page_number=int(app_instance.current_page_id),
            title=f"Page {app_instance.current_page_id}",
            subtitle=state.get("page_category", ""),
            grid=[[{"char": " ", "fg": 7, "bg": 0}]],  # Simplified grid
            timestamp=state.get("timestamp", datetime.now().isoformat()),
        )

    # ── WebSocket Feed ─────────────────────────────────────────────

    @app.websocket("/ws/{snack_id}")
    async def websocket_feed(websocket: WebSocket, snack_id: str):
        """Real-time teletext stream via WebSocket"""
        app_instance = manager.get_app(snack_id)
        if not app_instance:
            await websocket.close(code=4004, reason=f"Snack not found: {snack_id}")
            return

        await websocket.accept()

        try:
            while True:
                # Send current state
                state = app_instance.get_lens_state()
                await websocket.send_json({
                    "type": "teletext_update",
                    "page": app_instance.current_page_id,
                    "state": state,
                    "timestamp": datetime.now().isoformat(),
                })

                # Wait for next update or client message
                try:
                    data = await asyncio.wait_for(
                        websocket.receive_text(),
                        timeout=5.0,
                    )
                    # Handle incoming MCP command from agent
                    try:
                        msg = json.loads(data)
                        if "command" in msg:
                            mcp = manager.get_mcp(snack_id)
                            if mcp:
                                cmd = mcp.queue_command(
                                    f"{msg['command']} {json.dumps(msg.get('args', {}))}"
                                )
                                response = mcp.process_command(cmd)
                                await websocket.send_json({
                                    "type": "mcp_response",
                                    "command": msg["command"],
                                    "response": {
                                        "result": response.result if response else "queued",
                                        "success": response.success if response else True,
                                    },
                                })
                    except json.JSONDecodeError:
                        pass
                except asyncio.TimeoutError:
                    continue

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {snack_id}")

    # ── Spool Operations ───────────────────────────────────────────

    @app.post("/spool/{snack_id}/save")
    async def save_spool(snack_id: str, slot: str = "auto"):
        """Save current teletext state to spool"""
        app_instance = manager.get_app(snack_id)
        if not app_instance:
            raise HTTPException(status_code=404, detail=f"Snack not found: {snack_id}")

        state = app_instance.get_lens_state()
        spool = manager.spool

        # Create a grid from current state
        grid = TeletextGrid()
        spool.save_page(
            page_number=int(app_instance.current_page_id),
            grid=grid,
            title=f"Snack {snack_id} - Page {app_instance.current_page_id}",
            metadata={"snack_id": snack_id, "slot": slot},
        )

        filename = f"{snack_id}_{slot}" if slot != "auto" else snack_id
        filepath = spool.export(filename)

        return SpoolSaveResponse(
            spool_id=filepath,
            slot=slot,
            page_count=spool.page_count,
        )

    @app.post("/spool/{snack_id}/load")
    async def load_spool(snack_id: str, spool_id: str):
        """Load teletext state from spool"""
        spool = manager.spool
        try:
            count = spool.import_file(spool_id)
            return SpoolLoadResponse(
                status="ok",
                pages_loaded=count,
            )
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"Spool not found: {spool_id}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # ── Skin Management ────────────────────────────────────────────

    @app.get("/snacks/{snack_id}/skins")
    async def list_skins(snack_id: str):
        """List available skins for a snack"""
        app_instance = manager.get_app(snack_id)
        if not app_instance:
            raise HTTPException(status_code=404, detail=f"Snack not found: {snack_id}")

        return {
            "active": app_instance.skin_adapter.active_skin_name,
            "available": app_instance.skin_adapter.available_skins,
        }

    @app.post("/snacks/{snack_id}/skins/{skin_name}")
    async def apply_skin(snack_id: str, skin_name: str):
        """Apply a skin to a running snack"""
        app_instance = manager.get_app(snack_id)
        if not app_instance:
            raise HTTPException(status_code=404, detail=f"Snack not found: {snack_id}")

        success = app_instance.apply_skin(skin_name)
        if not success:
            raise HTTPException(status_code=400, detail=f"Unknown skin: {skin_name}")

        return {"status": "ok", "skin": skin_name}

    return app


# ── Standalone Entry Point ─────────────────────────────────────────

def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Run the Agent API server standalone.
    
    Args:
        host: Host to bind to
        port: Port to listen on
    """
    import uvicorn

    app = create_app()
    logger.info(f"Starting uCode1 Agent API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    run_server()
