"""
Narrator Engine — Converts feed/snack events into human-readable stories.

Uses the Lexicon to translate technical events into the
dungeon-and-wizard narrative metaphor for Yarnspinner output.
"""

import json
from datetime import datetime
from typing import Optional

from .lexicon import Lexicon, LANE_STORY


class NarratorEngine:
    """Generates story entries from feed events and snack executions."""

    def __init__(self):
        self.lexicon = Lexicon()

    # ── Event Types ─────────────────────────────────────────────────────────

    def vault_init(self, path: str) -> str:
        """Generate a story for vault initialization."""
        return (
            f"The {self.lexicon.translate('vault', LANE_STORY)} awakens. "
            f"A great stone door swings open at {path}, "
            f"revealing a chamber of polished obsidian, ready to receive knowledge."
        )

    def note_create(self, title: str, tags: Optional[list[str]] = None) -> str:
        """Generate a story for note creation."""
        tags_str = ""
        if tags:
            tags_str = f" with the hues: {', '.join(tags)}"
        return (
            f"The Wizard approaches the central pedestal and inscribes "
            f"a new {self.lexicon.translate('note', LANE_STORY).lower()}: "
            f"**{title}**{tags_str}. "
            f"Ancient mechanisms whir to life as it materialises."
        )

    def snack_run(self, snack_id: str, status: str = "completed") -> str:
        """Generate a story for snack execution."""
        if status == "completed":
            return (
                f"The Wizard casts the {self.lexicon.translate('snack', LANE_STORY).lower()} "
                f"**{snack_id}**. Arcane energies swirl and the spell completes successfully."
            )
        elif status == "failed":
            return (
                f"The Wizard attempts **{snack_id}** but the "
                f"{self.lexicon.translate('snack', LANE_STORY).lower()} fizzles. "
                f"The Oracle notes the failure for later study."
            )
        else:
            return (
                f"The Wizard begins the {self.lexicon.translate('snack', LANE_STORY).lower()} "
                f"**{snack_id}**. The outcome is unknown."
            )

    def feed_event(self, event_type: str, detail: str) -> str:
        """Generate a story for a feed event."""
        entry = self.lexicon.get(event_type)
        if entry:
            term = entry.translate(LANE_STORY)
        else:
            term = event_type
        return (
            f"A new entry appears in the {self.lexicon.translate('feed', LANE_STORY).lower()}: "
            f"**{term}** — {detail}"
        )

    def task_create(self, title: str) -> str:
        return (
            f"A new {self.lexicon.translate('task', LANE_STORY).lower()} appears "
            f"in the Wizard's quest log: **{title}**"
        )

    def ok_response(self, query: str) -> str:
        return (
            f"The {self.lexicon.translate('ok', LANE_STORY).lower()} whispers "
            f"in response to the Wizard's inquiry about _{query}_."
        )

    # ── Story Output ────────────────────────────────────────────────────────

    def generate_story(self, event_type: str, **kwargs) -> dict:
        """Generate a structured story entry from any event."""
        generators = {
            "vault_init": lambda **kw: self.vault_init(kw.get("path", kw.get("title", "unknown"))),
            "note_create": lambda **kw: self.note_create(kw.get("title", "Untitled"), kw.get("tags")),
            "snack_run": lambda **kw: self.snack_run(kw.get("snack_id", kw.get("title", "unknown")), kw.get("status", "completed")),
            "feed_event": lambda **kw: self.feed_event(kw.get("event_type", "event"), kw.get("detail", "")),
            "task_create": lambda **kw: self.task_create(kw.get("title", "Untitled")),
            "ok_response": lambda **kw: self.ok_response(kw.get("query", kw.get("detail", "something"))),
        }

        generator = generators.get(event_type)
        if not generator:
            return {
                "type": "story",
                "event": event_type,
                "content": f"An unknown event occurred: {event_type}",
                "timestamp": datetime.now().isoformat(),
            }

        content = generator(**kwargs)
        return {
            "type": "story",
            "event": event_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "lexicon": kwargs,
        }

    def story_to_markdown(self, story: dict) -> str:
        """Render a story entry as markdown."""
        event_labels = {
            "vault_init": "⚔️ The Vault Awakens",
            "note_create": "📜 A New Parchment",
            "snack_run": "✨ A Spell is Cast",
            "feed_event": "📡 Chronicles Updated",
            "task_create": "🎯 A New Quest",
            "ok_response": "🤖 The Oracle Speaks",
        }
        title = event_labels.get(story.get("event", ""), "📖 Story Entry")
        ts = story.get("timestamp", "")[:19].replace("T", " at ")

        return (
            f"## {title}\n\n"
            f"*Week {datetime.now().isocalendar()[1]} of the Wizard's Journey*\n\n"
            f"{story.get('content', '')}\n\n"
            f"— *The Oracle, {ts}*\n"
        )

    def story_to_ceefax(self, story: dict) -> str:
        """Render a story entry as a Ceefax-style teletext page."""
        content = story.get("content", "")
        # Simple teletext frame
        width = 38
        line = f"─" * width
        return (
            f"┌{line}┐\n"
            f"│ {story.get('event', 'STORY').upper().center(width-2)} │\n"
            f"├{line}┤\n"
            f"│ {content.center(width-2)} │\n"
            f"└{line}┘\n"
        )

    # ── Batch Processing ─────────────────────────────────────────────────────

    def process_feed_line(self, line: str) -> Optional[dict]:
        """Process a single JSONL feed line into a story."""
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None

        event_type = data.get("type", "feed_event")
        detail = data.get("detail", data.get("content", str(data)))
        return self.generate_story(event_type, detail=detail)

    def process_feed_file(self, path: str) -> list[dict]:
        """Process an entire feed file into stories."""
        stories = []
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        story = self.process_feed_line(line)
                        if story:
                            stories.append(story)
        except (IOError, FileNotFoundError):
            pass
        return stories
