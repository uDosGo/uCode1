#!/usr/bin/env python3
"""
Task CLI — `binder task` commands for the three-lane Kanban system.

Usage:
  binder task list --lane <lane> [--status <status>] [--format json|table]
  binder task create --title <title> --lane <lane> [--priority <p>] [--assignee <a>]
  binder task update <task_id> --field <field> --value <value>
  binder task board --lane <lane> [--format json|table]
  binder task feed [--lane <lane>]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

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
    ensure_dirs,
    TASKS_DIR,
)


def cmd_list(args: argparse.Namespace):
    """List tasks, optionally filtered by lane/status."""
    lane = args.lane
    status = args.status

    tasks = scan_tasks(lane=lane, status=status)

    if args.format == "json":
        output = [t.to_dict() for t in tasks]
        print(json.dumps(output, indent=2))
        return

    # Table format
    if not tasks:
        print(f"📭 No tasks found" + (f" in lane '{lane}'" if lane else "") + (f" with status '{status}'" if status else ""))
        return

    print(f"\n📋 Tasks" + (f" — Lane: {lane}" if lane else "") + (f" — Status: {status}" if status else ""))
    print(f"{'=' * 80}")
    print(f"{'ID':<30} {'Title':<30} {'Status':<15} {'Priority':<10}")
    print(f"{'-' * 80}")
    for t in tasks:
        fm = t.frontmatter
        print(f"{t.task_id:<30} {fm.title[:28]:<30} {fm.status.value:<15} {fm.priority.value:<10}")
    print(f"{'=' * 80}")
    print(f"Total: {len(tasks)} tasks")


def cmd_create(args: argparse.Namespace):
    """Create a new task."""
    task = create_task(
        title=args.title,
        lane=args.lane,
        description=args.description or "",
        priority=args.priority,
        assignee=args.assignee,
        tags=args.tags.split(",") if args.tags else None,
    )
    print(f"✅ Created task: {task.task_id}")
    print(f"   Title: {task.frontmatter.title}")
    print(f"   Lane: {task.frontmatter.lane.value}")
    print(f"   Status: {task.frontmatter.status.value}")
    print(f"   File: {task.path}")


def cmd_update(args: argparse.Namespace):
    """Update a task field."""
    task = update_task(args.task_id, args.field, args.value)
    if task:
        print(f"✅ Updated task '{task.task_id}': {args.field} = {args.value}")
    else:
        print(f"❌ Task not found: {args.task_id}")
        sys.exit(1)


def cmd_board(args: argparse.Namespace):
    """Show Kanban board for a lane."""
    lane = args.lane
    board = generate_kanban_board(lane)

    if args.format == "json":
        print(json.dumps(board, indent=2))
        return

    # Table format
    print(f"\n📊 Kanban Board — Lane: {lane}")
    print(f"{'=' * 80}")

    for col in board["columns"]:
        cards = board["cards"].get(col, [])
        print(f"\n  [{col.upper()}] ({len(cards)} cards)")
        if cards:
            for card in cards:
                assignee = f" @{card['assignee']}" if card.get("assignee") else ""
                priority = f" [{card['priority']}]" if card.get("priority") else ""
                print(f"    • {card['title']}{priority}{assignee}")
        else:
            print(f"    (empty)")

    total = sum(len(c) for c in board["cards"].values())
    print(f"\n{'=' * 80}")
    print(f"Total: {total} cards")


def cmd_feed(args: argparse.Namespace):
    """Generate and optionally write feeds."""
    if args.lane:
        feed = generate_task_feed(args.lane)
        print(json.dumps(feed, indent=2))
    else:
        write_feeds()


def main():
    parser = argparse.ArgumentParser(
        description="uDos Task Manager — Three-Lane Kanban System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  binder task list --lane dev
  binder task list --lane dev --status in-progress --format json
  binder task create --title "Add MCP tool" --lane dev --priority high --assignee cline
  binder task update my-task-abc123 --field status --value in-progress
  binder task board --lane dev
  binder task feed --lane dev > feed.json
  binder task feed  (writes all feeds to ~/uDos/shared/feeds/)
        """,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--lane", help="Filter by lane (dev|publishing|user)")
    list_parser.add_argument("--status", help="Filter by status (backlog|in-progress|review|done)")
    list_parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")

    # create
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("--title", required=True, help="Task title")
    create_parser.add_argument("--lane", default="dev", choices=["dev", "publishing", "user"], help="Task lane")
    create_parser.add_argument("--description", help="Task description")
    create_parser.add_argument("--priority", default="medium", choices=["low", "medium", "high", "urgent"], help="Priority")
    create_parser.add_argument("--assignee", help="Assigned agent/user")
    create_parser.add_argument("--tags", help="Comma-separated tags")

    # update
    update_parser = subparsers.add_parser("update", help="Update a task field")
    update_parser.add_argument("task_id", help="Task ID (filename stem)")
    update_parser.add_argument("--field", required=True, help="Field to update (title|lane|status|priority|assignee|due_date|description)")
    update_parser.add_argument("--value", required=True, help="New value")

    # board
    board_parser = subparsers.add_parser("board", help="Show Kanban board")
    board_parser.add_argument("--lane", default="dev", choices=["dev", "publishing", "user"], help="Lane to display")
    board_parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")

    # feed
    feed_parser = subparsers.add_parser("feed", help="Generate task feeds")
    feed_parser.add_argument("--lane", choices=["dev", "publishing", "user"], help="Single lane feed (omit for all)")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "create": cmd_create,
        "update": cmd_update,
        "board": cmd_board,
        "feed": cmd_feed,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
