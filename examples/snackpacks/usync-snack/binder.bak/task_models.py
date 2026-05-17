"""
Task models for the three-lane Kanban system.

Each task is a markdown file in ~/Vault/binder/#tasks/ with YAML frontmatter.
Lanes: dev, publishing, user
Statuses: backlog, in-progress, review, done
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


# ─── Enums ────────────────────────────────────────────────────────────────────

class TaskLane(str, Enum):
    DEV = "dev"
    PUBLISHING = "publishing"
    USER = "user"


class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in-progress"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# ─── Column definitions per lane ──────────────────────────────────────────────

LANE_COLUMNS: Dict[str, List[str]] = {
    "dev": ["backlog", "in-progress", "review", "done"],
    "publishing": ["backlog", "in-progress", "review", "done"],
    "user": ["backlog", "in-progress", "review", "done"],
}


# ─── Task Frontmatter ─────────────────────────────────────────────────────────

@dataclass
class TaskFrontmatter:
    """YAML frontmatter schema for task files."""
    title: str
    lane: TaskLane
    status: TaskStatus
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[str] = None  # YYYY-MM-DD
    tags: List[str] = field(default_factory=list)
    created: str = ""  # YYYY-MM-DD
    updated: str = ""  # YYYY-MM-DD
    mcp_tools: List[str] = field(default_factory=list)
    workflow: Optional[str] = None
    description: str = ""

    def validate(self) -> List[str]:
        """Validate required fields. Returns list of error messages."""
        errors = []
        if not self.title:
            errors.append("title is required")
        if not self.lane:
            errors.append("lane is required (dev|publishing|user)")
        if not self.status:
            errors.append("status is required (backlog|in-progress|review|done)")
        if self.created and not re.match(r"^\d{4}-\d{2}-\d{2}$", self.created):
            errors.append(f"created must be YYYY-MM-DD format, got '{self.created}'")
        if self.updated and not re.match(r"^\d{4}-\d{2}-\d{2}$", self.updated):
            errors.append(f"updated must be YYYY-MM-DD format, got '{self.updated}'")
        if self.due_date and not re.match(r"^\d{4}-\d{2}-\d{2}$", self.due_date):
            errors.append(f"due_date must be YYYY-MM-DD format, got '{self.due_date}'")
        return errors

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "lane": self.lane.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "assignee": self.assignee,
            "due_date": self.due_date,
            "tags": self.tags,
            "created": self.created,
            "updated": self.updated,
            "mcp_tools": self.mcp_tools,
            "workflow": self.workflow,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskFrontmatter":
        created = data.get("created", "")
        if created and not isinstance(created, str):
            created = str(created)
        updated = data.get("updated", "")
        if updated and not isinstance(updated, str):
            updated = str(updated)
        due_date = data.get("due_date")
        if due_date and not isinstance(due_date, str):
            due_date = str(due_date)

        lane_str = data.get("lane", "dev")
        status_str = data.get("status", "backlog")
        priority_str = data.get("priority", "medium")

        try:
            lane = TaskLane(lane_str)
        except ValueError:
            lane = TaskLane.DEV
        try:
            status = TaskStatus(status_str)
        except ValueError:
            status = TaskStatus.BACKLOG
        try:
            priority = TaskPriority(priority_str)
        except ValueError:
            priority = TaskPriority.MEDIUM

        return cls(
            title=data.get("title", ""),
            lane=lane,
            status=status,
            priority=priority,
            assignee=data.get("assignee"),
            due_date=due_date,
            tags=data.get("tags", []),
            created=created,
            updated=updated,
            mcp_tools=data.get("mcp_tools", []),
            workflow=data.get("workflow"),
            description=data.get("description", ""),
        )


# ─── Task Document ────────────────────────────────────────────────────────────

@dataclass
class TaskDocument:
    """A single task markdown file."""
    path: Path
    frontmatter: TaskFrontmatter
    content: str
    raw_content: str
    task_id: str = ""

    def __post_init__(self):
        if not self.task_id:
            # Derive ID from filename or generate
            self.task_id = self.path.stem if self.path else f"task-{uuid.uuid4().hex[:8]}"

    @property
    def filename(self) -> str:
        return self.path.name

    def to_card(self) -> dict:
        """Convert to Kanban card format."""
        return {
            "id": self.task_id,
            "title": self.frontmatter.title,
            "status": self.frontmatter.status.value,
            "lane": self.frontmatter.lane.value,
            "priority": self.frontmatter.priority.value,
            "assignee": self.frontmatter.assignee,
            "due_date": self.frontmatter.due_date,
            "tags": self.frontmatter.tags,
            "created": self.frontmatter.created,
            "updated": self.frontmatter.updated,
            "workflow": self.frontmatter.workflow,
        }

    def to_dict(self) -> dict:
        return {
            "id": self.task_id,
            "path": str(self.path),
            "frontmatter": self.frontmatter.to_dict(),
            "content_preview": self.content[:300] if self.content else "",
        }


# ─── Task Store ───────────────────────────────────────────────────────────────

TASKS_DIR = Path.home() / "Vault" / "binder" / "#tasks"
FEEDS_DIR = Path.home() / "uDos" / "shared" / "feeds"
STATE_DIR = Path.home() / ".local" / "state" / "udos"
SQLITE_DB = STATE_DIR / "tasks.db"


def ensure_dirs():
    """Create required directories."""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    FEEDS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def parse_task_frontmatter(content: str):
    """Parse YAML frontmatter from task markdown content."""
    match = re.match(r"^---\n(.*?)(?:\n---\n?|---)\n?", content, re.DOTALL)
    if not match:
        return None, content
    fm_text = match.group(1)
    body = content[match.end():]
    try:
        import yaml
        fm_data = yaml.safe_load(fm_text) if fm_text.strip() else {}
        if fm_data is None:
            return {}, body
        if not isinstance(fm_data, dict):
            return None, content
        return fm_data, body
    except yaml.YAMLError:
        return None, content


def build_task_yaml(frontmatter: TaskFrontmatter) -> str:
    """Build YAML frontmatter string from a TaskFrontmatter object."""
    import yaml
    data = frontmatter.to_dict()
    data = {k: v for k, v in data.items() if v is not None and v != "" and v != []}
    fm_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False).strip()
    return f"---\n{fm_yaml}\n---\n"


def read_task(filepath: Path) -> TaskDocument:
    """Read a task markdown file and parse its frontmatter."""
    raw_content = filepath.read_text(encoding="utf-8")
    fm_data, body = parse_task_frontmatter(raw_content)
    if fm_data:
        frontmatter = TaskFrontmatter.from_dict(fm_data)
    else:
        title = filepath.stem.replace("-", " ").replace("_", " ").title()
        frontmatter = TaskFrontmatter(
            title=title,
            lane=TaskLane.DEV,
            status=TaskStatus.BACKLOG,
            created=date.today().isoformat(),
            updated=date.today().isoformat(),
        )
    task_id = filepath.stem
    return TaskDocument(
        path=filepath,
        frontmatter=frontmatter,
        content=body,
        raw_content=raw_content,
        task_id=task_id,
    )


def write_task(task: TaskDocument):
    """Write a TaskDocument back to its file with updated frontmatter."""
    fm_yaml = build_task_yaml(task.frontmatter)
    desc = task.frontmatter.description.strip()
    body = task.content.strip()
    if desc and desc not in body:
        new_content = fm_yaml + "\n" + desc + "\n"
    else:
        new_content = fm_yaml + "\n" + body + "\n" if body else fm_yaml + "\n"
    task.path.write_text(new_content, encoding="utf-8")
    task.raw_content = new_content


def scan_tasks(lane: Optional[str] = None, status: Optional[str] = None) -> List[TaskDocument]:
    """Scan #tasks directory for all task files, optionally filtered by lane/status."""
    ensure_dirs()
    tasks = []
    for md_file in sorted(TASKS_DIR.glob("*.md")):
        task = read_task(md_file)
        if lane and task.frontmatter.lane.value != lane:
            continue
        if status and task.frontmatter.status.value != status:
            continue
        tasks.append(task)
    return tasks


def generate_task_id(title: str) -> str:
    """Generate a URL-friendly task ID from a title."""
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    short_hash = uuid.uuid4().hex[:6]
    return f"{slug}-{short_hash}"


def create_task(
    title: str,
    lane: str = "dev",
    description: str = "",
    priority: str = "medium",
    assignee: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> TaskDocument:
    """Create a new task file."""
    ensure_dirs()
    task_id = generate_task_id(title)
    filepath = TASKS_DIR / f"{task_id}.md"
    today = date.today().isoformat()

    try:
        lane_enum = TaskLane(lane)
    except ValueError:
        lane_enum = TaskLane.DEV

    try:
        priority_enum = TaskPriority(priority)
    except ValueError:
        priority_enum = TaskPriority.MEDIUM

    frontmatter = TaskFrontmatter(
        title=title,
        lane=lane_enum,
        status=TaskStatus.BACKLOG,
        priority=priority_enum,
        assignee=assignee,
        tags=tags or [],
        created=today,
        updated=today,
        description=description,
    )

    task = TaskDocument(
        path=filepath,
        frontmatter=frontmatter,
        content=description,
        raw_content="",
        task_id=task_id,
    )
    write_task(task)
    return task


def update_task(task_id: str, field: str, value: str) -> Optional[TaskDocument]:
    """Update a field on an existing task."""
    filepath = TASKS_DIR / f"{task_id}.md"
    if not filepath.exists():
        # Try to find by partial match
        for md_file in TASKS_DIR.glob("*.md"):
            if md_file.stem.startswith(task_id) or task_id in md_file.stem:
                filepath = md_file
                break
        else:
            return None

    task = read_task(filepath)
    fm = task.frontmatter

    # Map field names
    field_map = {
        "title": "title",
        "lane": "lane",
        "status": "status",
        "priority": "priority",
        "assignee": "assignee",
        "due_date": "due_date",
        "workflow": "workflow",
        "description": "description",
    }

    target = field_map.get(field, field)

    if target == "title":
        fm.title = value
    elif target == "lane":
        try:
            fm.lane = TaskLane(value)
        except ValueError:
            pass
    elif target == "status":
        try:
            fm.status = TaskStatus(value)
        except ValueError:
            pass
    elif target == "priority":
        try:
            fm.priority = TaskPriority(value)
        except ValueError:
            pass
    elif target == "assignee":
        fm.assignee = value if value else None
    elif target == "due_date":
        fm.due_date = value if value else None
    elif target == "workflow":
        fm.workflow = value if value else None
    elif target == "description":
        fm.description = value
        task.content = value
    else:
        return None

    fm.updated = date.today().isoformat()
    write_task(task)
    return task


def generate_kanban_board(lane: str) -> dict:
    """Generate Kanban board data for a lane."""
    tasks = scan_tasks(lane=lane)
    columns = LANE_COLUMNS.get(lane, LANE_COLUMNS["dev"])

    cards_by_status: Dict[str, list] = {col: [] for col in columns}
    for task in tasks:
        status = task.frontmatter.status.value
        if status in cards_by_status:
            cards_by_status[status].append(task.to_card())

    return {
        "lane": lane,
        "columns": columns,
        "cards": cards_by_status,
    }


def generate_task_feed(lane: str) -> dict:
    """Generate JSON feed for a lane (Kanban board format)."""
    board = generate_kanban_board(lane)
    # Flatten cards for feed format
    all_cards = []
    for col_cards in board["cards"].values():
        all_cards.extend(col_cards)
    return {
        "lane": lane,
        "columns": board["columns"],
        "cards": all_cards,
    }


def write_feeds():
    """Write JSON feeds for all lanes."""
    ensure_dirs()
    for lane in ["dev", "publishing", "user"]:
        feed = generate_task_feed(lane)
        feed_path = FEEDS_DIR / f"tasks-{lane}.json"
        with open(feed_path, "w") as f:
            json.dump(feed, f, indent=2)
        print(f"  ✅ Wrote feed: {feed_path}")

    # Write combined feed
    combined = {}
    for lane in ["dev", "publishing", "user"]:
        feed_path = FEEDS_DIR / f"tasks-{lane}.json"
        if feed_path.exists():
            with open(feed_path) as f:
                combined[lane] = json.load(f)
    combined_path = FEEDS_DIR / "tasks-all.json"
    with open(combined_path, "w") as f:
        json.dump(combined, f, indent=2)
    print(f"  ✅ Wrote combined feed: {combined_path}")

    # Sync to SQLite for fast cross-machine querying
    sync_to_sqlite()


# ─── SQLite Sync Layer (Cross-Machine Fast Query) ─────────────────────────────

def sync_to_sqlite():
    """
    Sync all tasks to SQLite for fast cross-machine querying.
    This is an optional fast-query layer — the markdown files remain the source of truth.
    """
    import sqlite3
    ensure_dirs()
    conn = sqlite3.connect(str(SQLITE_DB))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # Create table if not exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            lane TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'medium',
            assignee TEXT,
            due_date TEXT,
            tags TEXT,
            created TEXT,
            updated TEXT,
            workflow TEXT,
            description TEXT,
            file_path TEXT,
            synced_at TEXT NOT NULL
        )
    """)

    # Upsert all tasks
    now = datetime.now().isoformat()
    tasks = scan_tasks()
    for task in tasks:
        fm = task.frontmatter
        conn.execute("""
            INSERT OR REPLACE INTO tasks
                (id, title, lane, status, priority, assignee, due_date,
                 tags, created, updated, workflow, description, file_path, synced_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.task_id,
            fm.title,
            fm.lane.value,
            fm.status.value,
            fm.priority.value,
            fm.assignee,
            fm.due_date,
            json.dumps(fm.tags),
            fm.created,
            fm.updated,
            fm.workflow,
            fm.description,
            str(task.path),
            now,
        ))

    conn.commit()
    conn.close()


def query_sqlite(lane: Optional[str] = None,
                 status: Optional[str] = None,
                 assignee: Optional[str] = None,
                 priority: Optional[str] = None,
                 limit: int = 100) -> List[dict]:
    """
    Query tasks from SQLite with optional filters.
    Faster than scanning markdown files for large task sets.
    """
    import sqlite3
    if not SQLITE_DB.exists():
        # Fall back to markdown scan
        tasks = scan_tasks(lane=lane, status=status)
        return [t.to_card() for t in tasks]

    conn = sqlite3.connect(str(SQLITE_DB))
    conn.row_factory = sqlite3.Row

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if lane:
        query += " AND lane = ?"
        params.append(lane)
    if status:
        query += " AND status = ?"
        params.append(status)
    if assignee:
        query += " AND assignee = ?"
        params.append(assignee)
    if priority:
        query += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY updated DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    results = []
    for row in rows:
        card = dict(row)
        card["tags"] = json.loads(card.get("tags", "[]"))
        results.append(card)
    return results


def get_sync_status() -> dict:
    """
    Get sync status: last sync time, task counts per lane, and SQLite health.
    Used by the sync protocol to determine if a full resync is needed.
    """
    import sqlite3
    status = {
        "sqlite_db": str(SQLITE_DB),
        "db_exists": SQLITE_DB.exists(),
        "last_sync": None,
        "task_count": 0,
        "tasks_per_lane": {},
        "markdown_count": 0,
    }

    if SQLITE_DB.exists():
        conn = sqlite3.connect(str(SQLITE_DB))
        try:
            row = conn.execute("SELECT MAX(synced_at) as last_sync FROM tasks").fetchone()
            status["last_sync"] = row[0] if row else None

            row = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
            status["task_count"] = row[0] if row else 0

            for lane in ["dev", "publishing", "user"]:
                row = conn.execute("SELECT COUNT(*) FROM tasks WHERE lane = ?", (lane,)).fetchone()
                status["tasks_per_lane"][lane] = row[0] if row else 0
        finally:
            conn.close()

    status["markdown_count"] = len(list(TASKS_DIR.glob("*.md")))
    return status


def export_sync_payload() -> dict:
    """
    Export all tasks as a portable JSON payload for cross-machine sync.
    This is the format used by the sync protocol between macOS and Ubuntu.
    """
    tasks = scan_tasks()
    return {
        "version": "1.0",
        "protocol": "udos-task-sync",
        "generated": datetime.now().isoformat(),
        "source_host": __import__("socket").gethostname(),
        "task_count": len(tasks),
        "tasks": [t.to_card() for t in tasks],
    }


def import_sync_payload(payload: dict) -> dict:
    """
    Import tasks from a sync payload (received from another machine).
    Returns a report of what was imported.
    """
    imported = 0
    skipped = 0
    errors = []

    for card in payload.get("tasks", []):
        try:
            task_id = card.get("id", "")
            if not task_id:
                skipped += 1
                continue

            # Check if task already exists
            filepath = TASKS_DIR / f"{task_id}.md"
            if filepath.exists():
                skipped += 1
                continue

            # Create the task
            task = create_task(
                title=card.get("title", "Imported Task"),
                lane=card.get("lane", "dev"),
                description=card.get("description", ""),
                priority=card.get("priority", "medium"),
                assignee=card.get("assignee"),
                tags=card.get("tags", []),
            )
            # Override status if provided
            if card.get("status") and card["status"] != "backlog":
                update_task(task.task_id, "status", card["status"])
            imported += 1
        except Exception as e:
            errors.append(str(e))

    if imported > 0:
        write_feeds()

    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
        "error_count": len(errors),
    }
