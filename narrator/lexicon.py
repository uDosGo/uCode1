"""
Lexicon — 3-lane term mapping system for uDos.

Defines what things are called across three "lanes":
- Dev Lane: Technical terms used in code and documentation
- Story Lane: Narrative terms (Wizard/Dungeon metaphor)
- Student Lane: Practical terms for tutorials
"""

from dataclasses import dataclass, field
from typing import Optional

LANE_DEV = "dev"
LANE_STORY = "story"
LANE_STUDENT = "student"


@dataclass
class LexiconEntry:
    """A single term mapped across all three lanes."""
    term_id: str                         # e.g. "vault", "note", "tag"
    dev: str = ""                        # Technical term
    story: str = ""                      # Narrative term
    student: str = ""                    # Tutorial term
    emoji: str = ""                      # Optional emoji
    description: str = ""               # Short explanation
    tags: list[str] = field(default_factory=list)

    def translate(self, lane: str) -> str:
        """Get the term for a specific lane."""
        return {
            LANE_DEV: self.dev,
            LANE_STORY: self.story,
            LANE_STUDENT: self.student,
        }.get(lane, self.dev)

    def to_dict(self) -> dict:
        return {
            "term_id": self.term_id,
            "dev": self.dev,
            "story": self.story,
            "student": self.student,
            "emoji": self.emoji,
            "description": self.description,
            "tags": self.tags,
        }


# ── Built-in Lexicon ───────────────────────────────────────────────────────

CORE_LEXICON: dict[str, LexiconEntry] = {
    "vault": LexiconEntry(
        term_id="vault",
        dev="Vault",
        story="Dungeon of Knowledge",
        student="Digital notebook",
        emoji="💾",
        description="Core data storage structure",
        tags=["core", "storage"],
    ),
    "note": LexiconEntry(
        term_id="note",
        dev="Note",
        story="Parchment",
        student="Piece of knowledge",
        emoji="📝",
        description="Markdown document with frontmatter",
        tags=["core", "content"],
    ),
    "tag": LexiconEntry(
        term_id="tag",
        dev="Tag",
        story="Hue/Color",
        student="Category/Label",
        emoji="🏷️",
        description="Metadata category for organization",
        tags=["core", "metadata"],
    ),
    "link": LexiconEntry(
        term_id="link",
        dev="Link",
        story="Invisible thread",
        student="Connection",
        emoji="🔗",
        description="Bidirectional reference between notes",
        tags=["core", "navigation"],
    ),
    "feed": LexiconEntry(
        term_id="feed",
        dev="Feed",
        story="Scroll of Chronicles",
        student="Activity history",
        emoji="📡",
        description="Append-only JSONL activity log",
        tags=["core", "logging"],
    ),
    "snack": LexiconEntry(
        term_id="snack",
        dev="Snack",
        story="Spell",
        student="Automation",
        emoji="🍱",
        description="Executable container",
        tags=["core", "execution"],
    ),
    "ok": LexiconEntry(
        term_id="ok",
        dev="OK Agent",
        story="Oracle",
        student="AI Assistant",
        emoji="🤖",
        description="Local AI assistant for uDos",
        tags=["core", "ai"],
    ),
    "grid": LexiconEntry(
        term_id="grid",
        dev="Grid",
        story="Map of the Realms",
        student="Layout",
        emoji="🧩",
        description="ASCII grid layout system",
        tags=["core", "ui"],
    ),
    "cell": LexiconEntry(
        term_id="cell",
        dev="Cell",
        story="Treasure chest",
        student="Storage slot",
        emoji="🔲",
        description="24×24 pixel atomic storage unit",
        tags=["core", "storage"],
    ),
    "task": LexiconEntry(
        term_id="task",
        dev="Task",
        story="Quest",
        student="To-do item",
        emoji="✅",
        description="Action item with checkbox",
        tags=["core", "productivity"],
    ),
    "spatial": LexiconEntry(
        term_id="spatial",
        dev="Spatial Index",
        story="Map of the Realms",
        student="Location tracking",
        emoji="🗺️",
        description="2D coordinate system for grid-based indexing",
        tags=["core", "spatial"],
    ),
    "skill": LexiconEntry(
        term_id="skill",
        dev="Skill",
        story="Incantation",
        student="Recipe",
        emoji="🎯",
        description="Predictable function-calling template",
        tags=["core", "automation"],
    ),
}


class Lexicon:
    """The uDos Lexicon — maps terms across Dev/Story/Student lanes."""

    def __init__(self):
        self._entries: dict[str, LexiconEntry] = {}
        self.load_defaults()

    def load_defaults(self):
        self._entries.update(CORE_LEXICON)

    def get(self, term_id: str) -> Optional[LexiconEntry]:
        return self._entries.get(term_id)

    def add(self, entry: LexiconEntry):
        self._entries[entry.term_id] = entry

    def remove(self, term_id: str):
        self._entries.pop(term_id, None)

    def search(self, query: str, lane: Optional[str] = None) -> list[LexiconEntry]:
        """Search lexicon entries by keyword across a specific lane or all."""
        q = query.lower()
        results = []
        for entry in self._entries.values():
            if lane:
                text = getattr(entry, lane, "").lower()
                if q in text:
                    results.append(entry)
                    continue
            if q in entry.term_id.lower():
                results.append(entry)
            elif q in entry.dev.lower():
                results.append(entry)
            elif q in entry.story.lower():
                results.append(entry)
            elif q in entry.student.lower():
                results.append(entry)
            elif q in entry.description.lower():
                results.append(entry)
        return results

    def list_terms(self, lane: Optional[str] = None, tag: Optional[str] = None) -> list[LexiconEntry]:
        """List all terms, optionally filtered by lane or tag."""
        results = []
        for entry in self._entries.values():
            if tag and tag not in entry.tags:
                continue
            results.append(entry)
        return sorted(results, key=lambda e: e.term_id)

    def translate(self, term_id: str, lane: str) -> str:
        """Translate a term into a specific lane."""
        entry = self._entries.get(term_id)
        if entry:
            return entry.translate(lane)
        return term_id

    def to_dict(self) -> dict:
        return {tid: entry.to_dict() for tid, entry in self._entries.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "Lexicon":
        lex = cls()
        lex._entries = {}
        for tid, entry_data in data.items():
            lex._entries[tid] = LexiconEntry(**entry_data)
        return lex

    def __len__(self) -> int:
        return len(self._entries)
