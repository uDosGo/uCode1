#!/usr/bin/env python3
"""
MCP Server for task management tools.

Provides MCP tools:
  - task_list: List tasks in a lane (returns JSON feed)
  - task_create: Create a new task
  - task_update: Update any field on a task
  - task_kanban_board: Return Kanban board data

Run with: python task_mcp_server.py
Or via stdio: python task_mcp_server.py --stdio
"""

from __future__ import annotations

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Usync.binder.task_models import (
    create_task,
    update_task,
    scan_tasks,
    generate_kanban_board,
    generate_task_feed,
    write_feeds,
)


# ─── MCP Tool Handlers ────────────────────────────────────────────────────────

def handle_task_list(params: dict) -> dict:
    """List tasks in a lane, optionally filtered by status."""
    lane = params.get("lane", "dev")
    status = params.get("status")
    feed = generate_task_feed(lane)
    if status:
        feed["cards"] = [c for c in feed["cards"] if c["status"] == status]
    return {"success": True, "data": feed}


def handle_task_create(params: dict) -> dict:
    """Create a new task."""
    title = params.get("title", "")
    if not title:
        return {"success": False, "error": "title is required"}
    lane = params.get("lane", "dev")
    description = params.get("description", "")
    priority = params.get("priority", "medium")
    assignee = params.get("assignee")
    tags = params.get("tags")

    task = create_task(
        title=title,
        lane=lane,
        description=description,
        priority=priority,
        assignee=assignee,
        tags=tags,
    )
    write_feeds()
    return {"success": True, "data": task.to_card()}


def handle_task_update(params: dict) -> dict:
    """Update a field on an existing task."""
    task_id = params.get("task_id", "")
    field = params.get("field", "")
    value = params.get("value", "")

    if not task_id or not field:
        return {"success": False, "error": "task_id and field are required"}

    task = update_task(task_id, field, value)
    if task:
        write_feeds()
        return {"success": True, "data": task.to_card()}
    return {"success": False, "error": f"Task not found: {task_id}"}


def handle_task_kanban_board(params: dict) -> dict:
    """Return Kanban board data for a lane."""
    lane = params.get("lane", "dev")
    board = generate_kanban_board(lane)
    return {"success": True, "data": board}


# ─── Binder Feed Handlers ─────────────────────────────────────────────────────

# Import task_models module for dynamic FEEDS_DIR access (supports test patching)
import Usync.binder.task_models as _task_models


def _get_feeds_dir():
    """Get the current FEEDS_DIR from task_models (supports test patching)."""
    return _task_models.FEEDS_DIR


def handle_binder_feed(params: dict) -> dict:
    """Get the JSON feed for a binder by name."""
    binder = params.get("binder", "")
    if not binder:
        return {"success": False, "error": "binder name is required"}

    clean_name = binder.lstrip("#")
    feeds_dir = _get_feeds_dir()
    feed_path = feeds_dir / f"{clean_name}.json"

    if not feed_path.exists():
        # List available feeds
        available = [p.stem for p in feeds_dir.glob("*.json")] if feeds_dir.exists() else []
        return {
            "success": False,
            "error": f"Feed for binder '{binder}' not found. Available: {', '.join(available) or '(none)'}",
        }

    try:
        feed = json.loads(feed_path.read_text())
        return {"success": True, "data": feed}
    except Exception as e:
        return {"success": False, "error": f"Error reading feed: {e}"}


def handle_binder_list(params: dict) -> dict:
    """List all available binder feeds."""
    feeds_dir = _get_feeds_dir()
    if not feeds_dir.exists():
        return {"success": True, "data": {"feeds": [], "count": 0}}

    feeds = sorted([p.stem for p in feeds_dir.glob("*.json")])
    return {"success": True, "data": {"feeds": feeds, "count": len(feeds)}}


def handle_binder_feed_update(params: dict) -> dict:
    """Notify that a binder feed has been updated (called by CI/webhook)."""
    binder = params.get("binder", "unknown")
    lane = params.get("lane")
    details = f" (lane: {lane})" if lane else ""
    print(f"[binder_feed_update] Feed updated: {binder}{details}")
    return {
        "success": True,
        "data": {
            "status": "acknowledged",
            "binder": binder,
            "lane": lane,
            "timestamp": datetime.now().isoformat(),
        },
    }


# ─── Webhook Handlers ─────────────────────────────────────────────────────────

def handle_github_webhook(params: dict) -> dict:
    """
    Handle GitHub webhook events for cross-lane sync.

    Supported events:
      - pull_request: closed/merged → update task status
      - push: to main → regenerate feeds
    """
    event = params.get("event", "")
    payload = params.get("payload", {})

    if event == "pull_request":
        action = payload.get("action", "")
        merged = payload.get("pull_request", {}).get("merged", False)

        if action == "closed" and merged:
            # PR merged — find associated task and move to review
            pr_title = payload.get("pull_request", {}).get("title", "")
            pr_body = payload.get("pull_request", {}).get("body", "")

            # Try to find a task ID in the PR body or title
            import re
            task_match = re.search(r"task[_-]?id[=:]\s*(\S+)", pr_body, re.IGNORECASE)
            if not task_match:
                task_match = re.search(r"(\w+-\w+-\w+)", pr_body)

            if task_match:
                task_id = task_match.group(1)
                task = update_task(task_id, "status", "review")
                if task:
                    write_feeds()
                    return {
                        "success": True,
                        "data": {
                            "message": f"Task {task_id} moved to review",
                            "task": task.to_card(),
                        },
                    }

            # If no task found, create a publishing task
            from Usync.binder.task_models import create_task
            pub_task = create_task(
                title=f"Publish: {pr_title}",
                lane="publishing",
                description=f"Auto-created from merged PR. Body: {pr_body[:200]}",
                priority="medium",
                tags=["auto", "publish"],
            )
            write_feeds()
            return {
                "success": True,
                "data": {
                    "message": f"Created publishing task: {pub_task.task_id}",
                    "task": pub_task.to_card(),
                },
            }

    elif event == "push":
        branch = payload.get("ref", "").replace("refs/heads/", "")
        if branch == "main":
            # Regenerate all feeds
            write_feeds()
            return {
                "success": True,
                "data": {"message": "All feeds regenerated on push to main"},
            }

    return {"success": False, "error": f"Unhandled event: {event}"}


# ─── Sync Protocol Handlers ───────────────────────────────────────────────────

def handle_sync_status(params: dict) -> dict:
    """Get sync status: last sync time, task counts per lane, SQLite health."""
    from Usync.binder.task_models import get_sync_status
    return {"success": True, "data": get_sync_status()}


def handle_sync_export(params: dict) -> dict:
    """Export all tasks as a portable JSON payload for cross-machine sync."""
    from Usync.binder.task_models import export_sync_payload
    return {"success": True, "data": export_sync_payload()}


def handle_sync_import(params: dict) -> dict:
    """Import tasks from a sync payload (received from another machine)."""
    payload = params.get("payload", {})
    if not payload:
        return {"success": False, "error": "payload is required"}
    from Usync.binder.task_models import import_sync_payload
    result = import_sync_payload(payload)
    return {"success": True, "data": result}


def handle_query_sqlite(params: dict) -> dict:
    """Query tasks from SQLite with optional filters (faster than markdown scan)."""
    from Usync.binder.task_models import query_sqlite
    results = query_sqlite(
        lane=params.get("lane"),
        status=params.get("status"),
        assignee=params.get("assignee"),
        priority=params.get("priority"),
        limit=params.get("limit", 100),
    )
    return {"success": True, "data": {"cards": results, "count": len(results)}}


# ─── register_tools() — Adapter for Re3Engine Unified MCP Server ──────────────
#
# This function is called by Re3EngineMCPServer.load_tool_module() to register
# all task management tools into the unified server. The existing HTTP/stdio
# server (main(), run_http(), run_stdio()) remains unchanged for backward
# compatibility.
#
# The unified server calls: register_tools(server)
# where server has a register_tool(name, description, input_schema, handler) method.

def register_tools(server):
    """Register all task management tools with a Re3EngineMCPServer instance."""
    for name, info in TOOLS.items():
        server.register_tool(
            name=name,
            description=info["description"],
            input_schema=info["input_schema"],
            handler=info["handler"],
        )


# ─── Tool Registry ────────────────────────────────────────────────────────────

TOOLS = {
    "task_list": {
        "description": "List tasks in a lane (returns JSON feed)",
        "input_schema": {
            "type": "object",
            "properties": {
                "lane": {"type": "string", "enum": ["dev", "publishing", "user"], "description": "Lane to list"},
                "status": {"type": "string", "enum": ["backlog", "in-progress", "review", "done"], "description": "Optional status filter"},
            },
        },
        "handler": handle_task_list,
    },
    "task_create": {
        "description": "Create a new task",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title (required)"},
                "lane": {"type": "string", "enum": ["dev", "publishing", "user"], "description": "Task lane"},
                "description": {"type": "string", "description": "Task description"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Priority"},
                "assignee": {"type": "string", "description": "Assigned agent/user"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"},
            },
            "required": ["title"],
        },
        "handler": handle_task_create,
    },
    "task_update": {
        "description": "Update any field on a task",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
                "field": {"type": "string", "description": "Field to update (title|lane|status|priority|assignee|due_date|description)"},
                "value": {"type": "string", "description": "New value"},
            },
            "required": ["task_id", "field", "value"],
        },
        "handler": handle_task_update,
    },
    "task_kanban_board": {
        "description": "Return Kanban board data (columns + cards)",
        "input_schema": {
            "type": "object",
            "properties": {
                "lane": {"type": "string", "enum": ["dev", "publishing", "user"], "description": "Lane to display"},
            },
        },
        "handler": handle_task_kanban_board,
    },
    "binder_feed": {
        "description": "Get the JSON feed for a binder by name",
        "input_schema": {
            "type": "object",
            "properties": {
                "binder": {"type": "string", "description": "Binder name, e.g. 'tasks-dev', 'standards', or '#udos'"},
            },
            "required": ["binder"],
        },
        "handler": handle_binder_feed,
    },
    "binder_list": {
        "description": "List all available binder feeds",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
        "handler": handle_binder_list,
    },
    "binder_feed_update": {
        "description": "Notify that a binder feed has been updated (called by CI/webhook)",
        "input_schema": {
            "type": "object",
            "properties": {
                "binder": {"type": "string", "description": "Binder name that was updated, or 'all'"},
                "lane": {"type": "string", "description": "Lane name if task feed (dev|publishing|user)"},
            },
            "required": ["binder"],
        },
        "handler": handle_binder_feed_update,
    },
    "github_webhook": {
        "description": "Handle GitHub webhook events for cross-lane sync",
        "input_schema": {
            "type": "object",
            "properties": {
                "event": {"type": "string", "description": "GitHub event type (pull_request, push)"},
                "payload": {"type": "object", "description": "GitHub webhook payload"},
            },
            "required": ["event", "payload"],
        },
        "handler": handle_github_webhook,
    },
    "sync_status": {
        "description": "Get sync status: last sync time, task counts per lane, SQLite health",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
        "handler": handle_sync_status,
    },
    "sync_export": {
        "description": "Export all tasks as a portable JSON payload for cross-machine sync",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
        "handler": handle_sync_export,
    },
    "sync_import": {
        "description": "Import tasks from a sync payload (received from another machine)",
        "input_schema": {
            "type": "object",
            "properties": {
                "payload": {"type": "object", "description": "Sync payload from sync_export"},
            },
            "required": ["payload"],
        },
        "handler": handle_sync_import,
    },
    "query_sqlite": {
        "description": "Query tasks from SQLite with optional filters (faster than markdown scan)",
        "input_schema": {
            "type": "object",
            "properties": {
                "lane": {"type": "string", "enum": ["dev", "publishing", "user"], "description": "Lane filter"},
                "status": {"type": "string", "enum": ["backlog", "in-progress", "review", "done"], "description": "Status filter"},
                "assignee": {"type": "string", "description": "Assignee filter"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Priority filter"},
                "limit": {"type": "integer", "description": "Max results (default 100)"},
            },
        },
        "handler": handle_query_sqlite,
    },
}


# ─── MCP Protocol Handler ─────────────────────────────────────────────────────

def handle_mcp_request(request: dict) -> dict:
    """Handle a JSON-RPC MCP request."""
    method = request.get("method", "")
    params = request.get("params", {})

    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": name,
                    "description": info["description"],
                    "inputSchema": info["input_schema"],
                }
                for name, info in TOOLS.items()
            ]
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        tool = TOOLS.get(tool_name)
        if not tool:
            return {"error": f"Unknown tool: {tool_name}"}
        result = tool["handler"](tool_args)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    return {"error": f"Unknown method: {method}"}


def run_stdio():
    """Run MCP server over stdio (for DevStudio integration)."""
    import sys
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_mcp_request(request)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}))
            sys.stdout.flush()


def run_http(port: int = 30001):
    """Run MCP server over HTTP."""
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class MCPHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                request = json.loads(body)
                response = handle_mcp_request(request)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "tools": list(TOOLS.keys())}).encode())
                return
            self.send_response(404)
            self.end_headers()

        def log_message(self, format, *args):
            pass  # Suppress HTTP logs

    server = HTTPServer(("0.0.0.0", port), MCPHandler)
    print(f"🧠 Task MCP Server running on http://localhost:{port}")
    print(f"   Tools: {', '.join(TOOLS.keys())}")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Task MCP Server")
    parser.add_argument("--stdio", action="store_true", help="Run over stdio")
    parser.add_argument("--port", type=int, default=30001, help="HTTP port (default: 30001)")
    args = parser.parse_args()

    if args.stdio:
        run_stdio()
    else:
        run_http(args.port)


if __name__ == "__main__":
    main()
