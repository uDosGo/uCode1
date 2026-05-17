"""
Integration tests for the full binder workflow pipeline.

Tests the complete flow:
  1. Create a task → file written to ~/Vault/binder/#tasks/
  2. Update task status → file updated
  3. Generate feeds → JSON written to ~/uDos/shared/feeds/
  4. MCP server serves feeds → binder_feed tool returns correct data
  5. Cross-lane webhook → GitHub PR merge triggers task status change

These tests use temporary directories to avoid touching real data.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from datetime import date
from unittest.mock import patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from Usync.binder.task_models import (
    TaskLane,
    TaskStatus,
    TaskPriority,
    create_task,
    update_task,
    scan_tasks,
    generate_kanban_board,
    generate_task_feed,
    write_feeds,
    TASKS_DIR,
    FEEDS_DIR,
    STATE_DIR,
)
from Usync.binder.task_mcp_server import (
    handle_task_list,
    handle_task_create,
    handle_task_update,
    handle_task_kanban_board,
    handle_binder_feed,
    handle_binder_list,
    handle_binder_feed_update,
    handle_github_webhook,
    handle_mcp_request,
)


# ─── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_dirs():
    """Create temporary directories for tasks and feeds."""
    with tempfile.TemporaryDirectory() as tmp_tasks, \
         tempfile.TemporaryDirectory() as tmp_feeds:
        # Save originals
        orig_tasks = TASKS_DIR
        orig_feeds = FEEDS_DIR

        # Patch
        import Usync.binder.task_models as tm
        tm.TASKS_DIR = Path(tmp_tasks)
        tm.FEEDS_DIR = Path(tmp_feeds)
        tm.STATE_DIR = Path(tmp_tasks).parent / "state"
        tm.STATE_DIR.mkdir(exist_ok=True)

        yield {
            "tasks_dir": Path(tmp_tasks),
            "feeds_dir": Path(tmp_feeds),
        }

        # Restore
        tm.TASKS_DIR = orig_tasks
        tm.FEEDS_DIR = orig_feeds


# ─── Test 1: Full Task Lifecycle ──────────────────────────────────────────────

class TestFullTaskLifecycle:
    """Create → update → scan → board → feed → verify."""

    def test_create_task_creates_file(self, temp_dirs):
        """Creating a task should write a .md file to the tasks directory."""
        task = create_task(
            title="Integration Test Task",
            lane="dev",
            description="Testing the full pipeline",
            priority="high",
            assignee="cline",
            tags=["test", "integration"],
        )

        # Verify file exists
        assert task.path.exists()
        assert task.path.suffix == ".md"

        # Verify file content has frontmatter
        content = task.path.read_text()
        assert "title: Integration Test Task" in content
        assert "lane: dev" in content
        assert "status: backlog" in content
        assert "priority: high" in content
        assert "assignee: cline" in content

    def test_update_task_modifies_file(self, temp_dirs):
        """Updating a task should modify the file on disk."""
        task = create_task(title="Update Test", lane="dev")

        # Update status
        updated = update_task(task.task_id, "status", "in-progress")
        assert updated is not None
        assert updated.frontmatter.status == TaskStatus.IN_PROGRESS

        # Verify file was updated
        content = task.path.read_text()
        assert "status: in-progress" in content

        # Update assignee
        updated = update_task(task.task_id, "assignee", "fred")
        assert updated is not None
        assert updated.frontmatter.assignee == "fred"

        content = task.path.read_text()
        assert "assignee: fred" in content

    def test_scan_tasks_filters_by_lane(self, temp_dirs):
        """Scanning tasks should filter by lane correctly."""
        create_task(title="Dev Task", lane="dev")
        create_task(title="Pub Task", lane="publishing")
        create_task(title="User Task", lane="user")

        dev_tasks = scan_tasks(lane="dev")
        assert len(dev_tasks) == 1
        assert dev_tasks[0].frontmatter.title == "Dev Task"

        pub_tasks = scan_tasks(lane="publishing")
        assert len(pub_tasks) == 1

        user_tasks = scan_tasks(lane="user")
        assert len(user_tasks) == 1

    def test_kanban_board_generation(self, temp_dirs):
        """Kanban board should group tasks by status."""
        t1 = create_task(title="Backlog Item", lane="dev")
        t2 = create_task(title="In Progress Item", lane="dev")
        update_task(t2.task_id, "status", "in-progress")
        t3 = create_task(title="Done Item", lane="dev")
        update_task(t3.task_id, "status", "done")

        board = generate_kanban_board("dev")

        assert board["lane"] == "dev"
        assert len(board["columns"]) == 4
        assert len(board["cards"]["backlog"]) == 1
        assert len(board["cards"]["in-progress"]) == 1
        assert len(board["cards"]["done"]) == 1
        assert len(board["cards"]["review"]) == 0

    def test_feed_generation(self, temp_dirs):
        """Feed should contain all tasks for a lane."""
        create_task(title="Feed Task 1", lane="dev")
        create_task(title="Feed Task 2", lane="dev")

        feed = generate_task_feed("dev")
        assert feed["lane"] == "dev"
        assert len(feed["cards"]) == 2

    def test_write_feeds_creates_files(self, temp_dirs):
        """write_feeds() should create JSON files on disk."""
        create_task(title="Feed File Task", lane="dev")
        create_task(title="Pub Feed Task", lane="publishing")

        write_feeds()

        feeds_dir = temp_dirs["feeds_dir"]
        assert (feeds_dir / "tasks-dev.json").exists()
        assert (feeds_dir / "tasks-publishing.json").exists()
        assert (feeds_dir / "tasks-user.json").exists()
        assert (feeds_dir / "tasks-all.json").exists()

        # Verify content
        dev_feed = json.loads((feeds_dir / "tasks-dev.json").read_text())
        assert len(dev_feed["cards"]) == 1
        assert dev_feed["cards"][0]["title"] == "Feed File Task"


# ─── Test 2: MCP Server Tools ─────────────────────────────────────────────────

class TestMCPServerTools:
    """Test the MCP tool handlers directly."""

    def test_task_list_tool(self, temp_dirs):
        """task_list should return feed data."""
        create_task(title="MCP List Task", lane="dev")

        result = handle_task_list({"lane": "dev"})
        assert result["success"] is True
        assert len(result["data"]["cards"]) == 1

    def test_task_create_tool(self, temp_dirs):
        """task_create should create a task and return its card."""
        result = handle_task_create({
            "title": "MCP Created Task",
            "lane": "publishing",
            "priority": "urgent",
        })
        assert result["success"] is True
        assert result["data"]["title"] == "MCP Created Task"
        assert result["data"]["status"] == "backlog"
        assert result["data"]["priority"] == "urgent"

    def test_task_create_missing_title(self, temp_dirs):
        """task_create should fail gracefully without a title."""
        result = handle_task_create({"lane": "dev"})
        assert result["success"] is False
        assert "title" in result["error"]

    def test_task_update_tool(self, temp_dirs):
        """task_update should modify a task field."""
        task = create_task(title="MCP Update Task", lane="dev")

        result = handle_task_update({
            "task_id": task.task_id,
            "field": "status",
            "value": "review",
        })
        assert result["success"] is True
        assert result["data"]["status"] == "review"

    def test_task_update_not_found(self, temp_dirs):
        """task_update should fail gracefully for unknown tasks."""
        result = handle_task_update({
            "task_id": "nonexistent-task",
            "field": "status",
            "value": "done",
        })
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_kanban_board_tool(self, temp_dirs):
        """task_kanban_board should return board structure."""
        create_task(title="Board Task", lane="dev")

        result = handle_task_kanban_board({"lane": "dev"})
        assert result["success"] is True
        assert result["data"]["lane"] == "dev"
        assert len(result["data"]["columns"]) == 4

    def test_binder_feed_tool(self, temp_dirs):
        """binder_feed should return feed data from disk."""
        # First write some feeds
        create_task(title="Binder Feed Task", lane="dev")
        write_feeds()

        result = handle_binder_feed({"binder": "tasks-dev"})
        assert result["success"] is True
        assert result["data"]["lane"] == "dev"
        assert len(result["data"]["cards"]) == 1

    def test_binder_feed_not_found(self, temp_dirs):
        """binder_feed should fail gracefully for missing feeds."""
        result = handle_binder_feed({"binder": "nonexistent"})
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_binder_feed_with_hash(self, temp_dirs):
        """binder_feed should handle # prefix."""
        create_task(title="Hash Task", lane="dev")
        write_feeds()

        result = handle_binder_feed({"binder": "#tasks-dev"})
        assert result["success"] is True

    def test_binder_list_tool(self, temp_dirs):
        """binder_list should return available feeds."""
        create_task(title="List Test", lane="dev")
        write_feeds()

        result = handle_binder_list({})
        assert result["success"] is True
        assert "tasks-dev" in result["data"]["feeds"]

    def test_binder_feed_update_tool(self, temp_dirs):
        """binder_feed_update should acknowledge the update."""
        result = handle_binder_feed_update({"binder": "tasks-dev", "lane": "dev"})
        assert result["success"] is True
        assert result["data"]["status"] == "acknowledged"
        assert result["data"]["binder"] == "tasks-dev"


# ─── Test 3: Cross-Lane Webhook ───────────────────────────────────────────────

class TestCrossLaneWebhook:
    """Test the GitHub webhook handler for cross-lane sync."""

    def test_pr_merge_creates_publishing_task(self, temp_dirs):
        """Merged PR should create a publishing task."""
        result = handle_github_webhook({
            "event": "pull_request",
            "payload": {
                "action": "closed",
                "pull_request": {
                    "merged": True,
                    "title": "Add new feature",
                    "body": "This PR adds a new feature",
                },
            },
        })
        assert result["success"] is True
        assert "Created publishing task:" in result["data"]["message"]
        assert result["data"]["task"]["lane"] == "publishing"

    def test_pr_with_task_id_moves_to_review(self, temp_dirs):
        """PR with task_id in body should move that task to review."""
        task = create_task(title="Webhook Task", lane="dev")

        result = handle_github_webhook({
            "event": "pull_request",
            "payload": {
                "action": "closed",
                "pull_request": {
                    "merged": True,
                    "title": "Implement feature",
                    "body": f"task_id={task.task_id}\nThis implements the feature",
                },
            },
        })
        assert result["success"] is True
        assert "moved to review" in result["data"]["message"]
        assert result["data"]["task"]["status"] == "review"

    def test_push_to_main_regenerates_feeds(self, temp_dirs):
        """Push to main should regenerate all feeds."""
        create_task(title="Push Test Task", lane="dev")

        result = handle_github_webhook({
            "event": "push",
            "payload": {
                "ref": "refs/heads/main",
            },
        })
        assert result["success"] is True
        assert "regenerated" in result["data"]["message"]

    def test_unhandled_event(self, temp_dirs):
        """Unhandled events should return an error."""
        result = handle_github_webhook({
            "event": "issues",
            "payload": {"action": "opened"},
        })
        assert result["success"] is False
        assert "Unhandled" in result["error"]


# ─── Test 4: MCP Protocol ─────────────────────────────────────────────────────

class TestMCPProtocol:
    """Test the JSON-RPC MCP protocol handler."""

    def test_tools_list(self, temp_dirs):
        """tools/list should return all registered tools."""
        response = handle_mcp_request({"method": "tools/list"})
        assert "tools" in response
        tool_names = [t["name"] for t in response["tools"]]
        assert "task_list" in tool_names
        assert "task_create" in tool_names
        assert "task_update" in tool_names
        assert "task_kanban_board" in tool_names
        assert "binder_feed" in tool_names
        assert "binder_list" in tool_names
        assert "binder_feed_update" in tool_names
        assert "github_webhook" in tool_names

    def test_tools_call(self, temp_dirs):
        """tools/call should invoke the correct tool."""
        response = handle_mcp_request({
            "method": "tools/call",
            "params": {
                "name": "binder_list",
                "arguments": {},
            },
        })
        assert "content" in response
        content = json.loads(response["content"][0]["text"])
        assert content["success"] is True

    def test_unknown_tool(self, temp_dirs):
        """Unknown tools should return an error."""
        response = handle_mcp_request({
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {},
            },
        })
        assert "error" in response

    def test_unknown_method(self, temp_dirs):
        """Unknown methods should return an error."""
        response = handle_mcp_request({"method": "unknown/method"})
        assert "error" in response


# ─── Test 5: End-to-End Pipeline ──────────────────────────────────────────────

# ─── Sync Protocol Tests ──────────────────────────────────────────────────────

class TestSyncProtocol:
    """Tests for the cross-machine sync protocol (Phase D)."""

    def test_sync_to_sqlite_creates_db(self, temp_dirs):
        """sync_to_sqlite() should create a SQLite database."""
        from Usync.binder.task_models import sync_to_sqlite, SQLITE_DB
        create_task(title="Sync Test Task", lane="dev")
        sync_to_sqlite()
        assert SQLITE_DB.exists()
        # Verify data in SQLite
        import sqlite3
        conn = sqlite3.connect(str(SQLITE_DB))
        row = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
        conn.close()
        assert row[0] >= 1

    def test_query_sqlite_returns_results(self, temp_dirs):
        """query_sqlite() should return tasks from SQLite."""
        from Usync.binder.task_models import sync_to_sqlite, query_sqlite
        create_task(title="SQLite Query Test", lane="dev", priority="high")
        sync_to_sqlite()
        results = query_sqlite(lane="dev")
        assert len(results) >= 1
        assert any(r["title"] == "SQLite Query Test" for r in results)

    def test_query_sqlite_filters_by_status(self, temp_dirs):
        """query_sqlite() should filter by status."""
        from Usync.binder.task_models import sync_to_sqlite, query_sqlite
        t1 = create_task(title="Status Filter A", lane="dev")
        t2 = create_task(title="Status Filter B", lane="dev")
        update_task(t1.task_id, "status", "in-progress")
        sync_to_sqlite()
        backlog = query_sqlite(status="backlog")
        in_progress = query_sqlite(status="in-progress")
        assert len(backlog) >= 1
        assert len(in_progress) >= 1

    def test_get_sync_status(self, temp_dirs):
        """get_sync_status() should return sync metadata."""
        from Usync.binder.task_models import sync_to_sqlite, get_sync_status
        create_task(title="Sync Status Test", lane="dev")
        sync_to_sqlite()
        status = get_sync_status()
        assert status["db_exists"] is True
        assert status["task_count"] >= 1
        assert "dev" in status["tasks_per_lane"]

    def test_export_sync_payload(self, temp_dirs):
        """export_sync_payload() should return all tasks as portable JSON."""
        from Usync.binder.task_models import export_sync_payload
        create_task(title="Export Test Task", lane="dev", priority="urgent")
        payload = export_sync_payload()
        assert payload["version"] == "1.0"
        assert payload["protocol"] == "udos-task-sync"
        assert payload["task_count"] >= 1
        assert any(t["title"] == "Export Test Task" for t in payload["tasks"])

    def test_import_sync_payload(self, temp_dirs):
        """import_sync_payload() should create tasks from a payload."""
        from Usync.binder.task_models import import_sync_payload
        payload = {
            "version": "1.0",
            "protocol": "udos-task-sync",
            "task_count": 2,
            "tasks": [
                {"id": "imported-task-1", "title": "Imported Task 1", "lane": "dev", "status": "in-progress", "priority": "high"},
                {"id": "imported-task-2", "title": "Imported Task 2", "lane": "publishing", "status": "backlog", "priority": "medium"},
            ],
        }
        result = import_sync_payload(payload)
        assert result["imported"] == 2
        assert result["skipped"] == 0
        assert result["error_count"] == 0

    def test_import_skips_existing(self, temp_dirs):
        """import_sync_payload() should skip tasks that already exist."""
        from Usync.binder.task_models import import_sync_payload, create_task
        task = create_task(title="Existing Task", lane="dev")
        # Use the actual task ID so the file exists
        payload = {
            "version": "1.0",
            "protocol": "udos-task-sync",
            "task_count": 1,
            "tasks": [
                {"id": task.task_id, "title": "Existing Task", "lane": "dev", "status": "backlog"},
            ],
        }
        result = import_sync_payload(payload)
        assert result["imported"] == 0
        assert result["skipped"] == 1

    def test_sync_mcp_tools(self, temp_dirs):
        """MCP sync tools should work end-to-end."""
        from Usync.binder.task_mcp_server import (
            handle_sync_status,
            handle_sync_export,
            handle_sync_import,
            handle_query_sqlite,
        )
        from Usync.binder.task_models import sync_to_sqlite

        # Create a task and sync to SQLite
        create_task(title="MCP Sync Test", lane="dev", priority="high")
        sync_to_sqlite()

        # Test sync_status
        status_result = handle_sync_status({})
        assert status_result["success"] is True
        assert status_result["data"]["task_count"] >= 1

        # Test sync_export
        export_result = handle_sync_export({})
        assert export_result["success"] is True
        assert export_result["data"]["task_count"] >= 1

        # Test query_sqlite
        query_result = handle_query_sqlite({"lane": "dev"})
        assert query_result["success"] is True
        assert query_result["data"]["count"] >= 1

        # Test sync_import
        import_result = handle_sync_import({
            "payload": {
                "tasks": [
                    {"id": "mcp-import-test", "title": "MCP Imported", "lane": "user", "status": "backlog"},
                ],
            },
        })
        assert import_result["success"] is True
        assert import_result["data"]["imported"] == 1


class TestEndToEndPipeline:
    """Full end-to-end test: create → update → feed → MCP serve."""

    def test_full_pipeline(self, temp_dirs):
        """
        Complete workflow test:
          1. Create a dev task
          2. Move it to in-progress
          3. Move it to review
          4. Generate feeds
          5. Read feed via MCP tool
          6. Verify all steps
        """
        # Step 1: Create
        task = create_task(
            title="E2E Pipeline Test",
            lane="dev",
            description="End-to-end test task",
            priority="high",
            assignee="cline",
            tags=["e2e", "pipeline"],
        )
        assert task.path.exists()
        task_id = task.task_id

        # Step 2: Move to in-progress
        updated = update_task(task_id, "status", "in-progress")
        assert updated.frontmatter.status == TaskStatus.IN_PROGRESS

        # Step 3: Move to review
        updated = update_task(task_id, "status", "review")
        assert updated.frontmatter.status == TaskStatus.REVIEW

        # Step 4: Generate feeds
        write_feeds()
        feed_path = temp_dirs["feeds_dir"] / "tasks-dev.json"
        assert feed_path.exists()

        # Step 5: Read feed via MCP tool
        result = handle_binder_feed({"binder": "tasks-dev"})
        assert result["success"] is True
        assert len(result["data"]["cards"]) == 1
        card = result["data"]["cards"][0]
        assert card["title"] == "E2E Pipeline Test"
        assert card["status"] == "review"
        assert card["priority"] == "high"
        assert card["assignee"] == "cline"

        # Step 6: Verify Kanban board
        board = handle_task_kanban_board({"lane": "dev"})
        assert board["success"] is True
        assert len(board["data"]["cards"]["review"]) == 1
        assert len(board["data"]["cards"]["backlog"]) == 0
        assert len(board["data"]["cards"]["in-progress"]) == 0
        assert len(board["data"]["cards"]["done"]) == 0
