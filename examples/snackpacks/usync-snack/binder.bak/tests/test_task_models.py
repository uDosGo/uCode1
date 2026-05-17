"""
Tests for task models (three-lane Kanban system).
"""

import json
import tempfile
from pathlib import Path
from datetime import date

import pytest

from Usync.binder.task_models import (
    TaskLane,
    TaskStatus,
    TaskPriority,
    TaskFrontmatter,
    TaskDocument,
    parse_task_frontmatter,
    build_task_yaml,
    read_task,
    write_task,
    scan_tasks,
    create_task,
    update_task,
    generate_kanban_board,
    generate_task_feed,
    TASKS_DIR,
    FEEDS_DIR,
)


class TestTaskFrontmatter:
    def test_minimal_frontmatter(self):
        fm = TaskFrontmatter(
            title="Test Task",
            lane=TaskLane.DEV,
            status=TaskStatus.BACKLOG,
        )
        errors = fm.validate()
        assert len(errors) == 0

    def test_missing_title(self):
        fm = TaskFrontmatter(
            title="",
            lane=TaskLane.DEV,
            status=TaskStatus.BACKLOG,
        )
        errors = fm.validate()
        assert any("title" in e for e in errors)

    def test_missing_lane(self):
        fm = TaskFrontmatter(
            title="Test",
            lane="",  # type: ignore
            status=TaskStatus.BACKLOG,
        )
        errors = fm.validate()
        assert any("lane" in e for e in errors)

    def test_invalid_date_format(self):
        fm = TaskFrontmatter(
            title="Test",
            lane=TaskLane.DEV,
            status=TaskStatus.BACKLOG,
            created="invalid-date",
        )
        errors = fm.validate()
        assert any("created" in e for e in errors)

    def test_valid_date_format(self):
        fm = TaskFrontmatter(
            title="Test",
            lane=TaskLane.DEV,
            status=TaskStatus.BACKLOG,
            created="2026-05-04",
        )
        errors = fm.validate()
        assert len(errors) == 0

    def test_to_dict(self):
        fm = TaskFrontmatter(
            title="Test Task",
            lane=TaskLane.DEV,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            assignee="cline",
            tags=["mcp", "rust"],
            created="2026-05-04",
        )
        d = fm.to_dict()
        assert d["title"] == "Test Task"
        assert d["lane"] == "dev"
        assert d["status"] == "in-progress"
        assert d["priority"] == "high"
        assert d["assignee"] == "cline"
        assert d["tags"] == ["mcp", "rust"]

    def test_from_dict(self):
        data = {
            "title": "Test Task",
            "lane": "publishing",
            "status": "review",
            "priority": "urgent",
            "assignee": "github-actions",
            "tags": ["ci", "release"],
        }
        fm = TaskFrontmatter.from_dict(data)
        assert fm.title == "Test Task"
        assert fm.lane == TaskLane.PUBLISHING
        assert fm.status == TaskStatus.REVIEW
        assert fm.priority == TaskPriority.URGENT
        assert fm.assignee == "github-actions"

    def test_from_dict_defaults(self):
        data = {"title": "Minimal"}
        fm = TaskFrontmatter.from_dict(data)
        assert fm.title == "Minimal"
        assert fm.lane == TaskLane.DEV
        assert fm.status == TaskStatus.BACKLOG
        assert fm.priority == TaskPriority.MEDIUM


class TestParseTaskFrontmatter:
    def test_parse_valid(self):
        content = """---
title: Test Task
lane: dev
status: in-progress
priority: high
assignee: cline
tags: [mcp, rust]
created: 2026-05-04
---
Task description here.
"""
        fm_data, body = parse_task_frontmatter(content)
        assert fm_data is not None
        assert fm_data["title"] == "Test Task"
        assert fm_data["lane"] == "dev"
        assert fm_data["status"] == "in-progress"
        assert "Task description here" in body

    def test_parse_no_frontmatter(self):
        content = "# Just a task\n\nNo frontmatter."
        fm_data, body = parse_task_frontmatter(content)
        assert fm_data is None
        assert body == content

    def test_parse_empty_frontmatter(self):
        content = """---
---

# Content
"""
        fm_data, body = parse_task_frontmatter(content)
        assert fm_data is not None
        assert "# Content" in body


class TestBuildTaskYaml:
    def test_build_minimal(self):
        fm = TaskFrontmatter(
            title="Test",
            lane=TaskLane.DEV,
            status=TaskStatus.BACKLOG,
        )
        yaml_str = build_task_yaml(fm)
        assert yaml_str.startswith("---")
        assert yaml_str.endswith("---\n")
        assert "title: Test" in yaml_str
        assert "lane: dev" in yaml_str

    def test_build_with_all_fields(self):
        fm = TaskFrontmatter(
            title="Full Task",
            lane=TaskLane.PUBLISHING,
            status=TaskStatus.REVIEW,
            priority=TaskPriority.URGENT,
            assignee="bot",
            tags=["release", "v2"],
            created="2026-05-04",
            workflow="release-rust.yaml",
        )
        yaml_str = build_task_yaml(fm)
        assert "workflow: release-rust.yaml" in yaml_str


class TestReadWriteTask:
    def test_read_task_with_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test-task.md"
            content = """---
title: Test Task
lane: dev
status: backlog
priority: medium
created: 2026-05-04
---
Description here.
"""
            path.write_text(content)
            task = read_task(path)
            assert task.frontmatter.title == "Test Task"
            assert task.frontmatter.lane == TaskLane.DEV
            assert task.frontmatter.status == TaskStatus.BACKLOG
            assert "Description here" in task.content

    def test_read_task_without_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "my-task.md"
            content = "# Just content"
            path.write_text(content)
            task = read_task(path)
            assert task.frontmatter.title == "My Task"  # Auto from filename
            assert task.frontmatter.lane == TaskLane.DEV  # Default

    def test_write_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "write-test.md"
            content = "---\ntitle: Original\nlane: dev\nstatus: backlog\n---\n\nBody\n"
            path.write_text(content)
            task = read_task(path)
            task.frontmatter.title = "Updated"
            task.frontmatter.status = TaskStatus.IN_PROGRESS
            write_task(task)
            task2 = read_task(path)
            assert task2.frontmatter.title == "Updated"
            assert task2.frontmatter.status == TaskStatus.IN_PROGRESS


class TestCreateUpdateTask:
    def test_create_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Override TASKS_DIR for testing
            original_dir = TASKS_DIR
            import Usync.binder.task_models as tm
            tm.TASKS_DIR = Path(tmp)
            
            task = create_task(
                title="Test Create Task",
                lane="dev",
                description="A test task",
                priority="high",
                assignee="cline",
                tags=["test", "demo"],
            )
            assert task.frontmatter.title == "Test Create Task"
            assert task.frontmatter.lane == TaskLane.DEV
            assert task.frontmatter.priority == TaskPriority.HIGH
            assert task.frontmatter.assignee == "cline"
            assert task.path.exists()
            
            # Restore
            tm.TASKS_DIR = original_dir

    def test_update_task_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            import Usync.binder.task_models as tm
            tm.TASKS_DIR = Path(tmp)
            
            task = create_task(title="Update Test", lane="dev")
            task_id = task.task_id
            
            updated = update_task(task_id, "status", "in-progress")
            assert updated is not None
            assert updated.frontmatter.status == TaskStatus.IN_PROGRESS
            
            tm.TASKS_DIR = TASKS_DIR

    def test_update_task_not_found(self):
        result = update_task("nonexistent-task", "status", "done")
        assert result is None


class TestScanTasks:
    def test_scan_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            import Usync.binder.task_models as tm
            tm.TASKS_DIR = Path(tmp)
            
            tasks = scan_tasks()
            assert len(tasks) == 0
            
            tm.TASKS_DIR = TASKS_DIR

    def test_scan_with_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            import Usync.binder.task_models as tm
            tm.TASKS_DIR = Path(tmp)
            
            create_task(title="Dev Task 1", lane="dev")
            create_task(title="Pub Task 1", lane="publishing")
            create_task(title="User Task 1", lane="user")
            
            all_tasks = scan_tasks()
            assert len(all_tasks) == 3
            
            dev_tasks = scan_tasks(lane="dev")
            assert len(dev_tasks) == 1
            assert dev_tasks[0].frontmatter.lane == TaskLane.DEV
            
            tm.TASKS_DIR = TASKS_DIR


class TestKanbanBoard:
    def test_generate_board_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            import Usync.binder.task_models as tm
            tm.TASKS_DIR = Path(tmp)
            
            board = generate_kanban_board("dev")
            assert board["lane"] == "dev"
            assert len(board["columns"]) == 4
            assert all(len(cards) == 0 for cards in board["cards"].values())
            
            tm.TASKS_DIR = TASKS_DIR

    def test_generate_board_with_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            import Usync.binder.task_models as tm
            tm.TASKS_DIR = Path(tmp)
            
            t1 = create_task(title="Backlog Task", lane="dev")
            t2 = create_task(title="In Progress Task", lane="dev")
            update_task(t2.task_id, "status", "in-progress")
            t3 = create_task(title="Done Task", lane="dev")
            update_task(t3.task_id, "status", "done")
            
            board = generate_kanban_board("dev")
            assert len(board["cards"]["backlog"]) == 1
            assert len(board["cards"]["in-progress"]) == 1
            assert len(board["cards"]["done"]) == 1
            assert len(board["cards"]["review"]) == 0
            
            tm.TASKS_DIR = TASKS_DIR


class TestTaskFeed:
    def test_generate_feed(self):
        with tempfile.TemporaryDirectory() as tmp:
            import Usync.binder.task_models as tm
            tm.TASKS_DIR = Path(tmp)
            tm.FEEDS_DIR = Path(tmp) / "feeds"
            
            create_task(title="Feed Task 1", lane="dev")
            create_task(title="Feed Task 2", lane="dev")
            
            feed = generate_task_feed("dev")
            assert feed["lane"] == "dev"
            assert len(feed["cards"]) == 2
            
            tm.TASKS_DIR = TASKS_DIR
            tm.FEEDS_DIR = FEEDS_DIR


class TestTaskDocument:
    def test_to_card(self):
        fm = TaskFrontmatter(
            title="Card Test",
            lane=TaskLane.DEV,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            assignee="cline",
        )
        doc = TaskDocument(
            path=Path("/tmp/test.md"),
            frontmatter=fm,
            content="Body",
            raw_content="---\ntitle: Card Test\n---\nBody",
            task_id="card-test-123",
        )
        card = doc.to_card()
        assert card["id"] == "card-test-123"
        assert card["title"] == "Card Test"
        assert card["status"] == "in-progress"
        assert card["priority"] == "high"
        assert card["assignee"] == "cline"

    def test_to_dict(self):
        fm = TaskFrontmatter(
            title="Dict Test",
            lane=TaskLane.PUBLISHING,
            status=TaskStatus.DONE,
        )
        doc = TaskDocument(
            path=Path("/tmp/test.md"),
            frontmatter=fm,
            content="Body",
            raw_content="---\ntitle: Dict Test\n---\nBody",
            task_id="dict-test",
        )
        d = doc.to_dict()
        assert d["id"] == "dict-test"
        assert d["frontmatter"]["title"] == "Dict Test"
        assert d["frontmatter"]["lane"] == "publishing"
