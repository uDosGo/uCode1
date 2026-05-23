"""
Undo/Redo History for Grid Editing

Provides a generic undo/redo stack that can be used by any editor.
Stores snapshots of grid state for branching and replay.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, TypeVar
from datetime import datetime

T = TypeVar('T')


@dataclass
class EditAction:
    """A single edit action stored in history."""
    description: str
    timestamp: datetime
    snapshot: Any  # The state snapshot
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, description: str, snapshot: Any, **metadata: Any) -> 'EditAction':
        """Create a new edit action with current timestamp."""
        return cls(
            description=description,
            timestamp=datetime.now(),
            snapshot=snapshot,
            metadata=metadata,
        )


class EditHistory(Generic[T]):
    """
    Undo/redo history stack for grid editing.
    
    Stores snapshots of editor state and supports:
    - Undo/redo navigation
    - Branching (saving/restoring named points)
    - History inspection
    - Configurable max depth
    """

    def __init__(self, max_depth: int = 100):
        self._stack: List[EditAction] = []
        self._index: int = -1  # Current position in stack
        self._max_depth: int = max_depth
        self._saved_points: Dict[str, int] = {}  # Named save points

    @property
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._index >= 0

    @property
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._index < len(self._stack) - 1

    @property
    def current(self) -> Optional[EditAction]:
        """Get the current action at the index."""
        if 0 <= self._index < len(self._stack):
            return self._stack[self._index]
        return None

    @property
    def depth(self) -> int:
        """Get the current stack depth."""
        return len(self._stack)

    def push(self, description: str, snapshot: T, **metadata: Any) -> None:
        """
        Push a new state onto the history stack.
        
        This discards any redo states after the current index.
        """
        action = EditAction.create(description, snapshot, **metadata)

        # Discard any redo states
        if self._index < len(self._stack) - 1:
            self._stack = self._stack[:self._index + 1]

        self._stack.append(action)
        self._index = len(self._stack) - 1

        # Enforce max depth
        if len(self._stack) > self._max_depth:
            excess = len(self._stack) - self._max_depth
            self._stack = self._stack[excess:]
            self._index -= excess

    def undo(self) -> Optional[T]:
        """
        Move back one step and return the previous state.
        Returns None if undo is not available.
        """
        if not self.can_undo:
            return None

        snapshot = self._stack[self._index].snapshot
        self._index -= 1
        return snapshot

    def redo(self) -> Optional[T]:
        """
        Move forward one step and return the next state.
        Returns None if redo is not available.
        """
        if not self.can_redo:
            return None

        self._index += 1
        return self._stack[self._index].snapshot

    def peek_undo(self) -> Optional[EditAction]:
        """Preview the action that would be undone."""
        if self.can_undo:
            return self._stack[self._index]
        return None

    def peek_redo(self) -> Optional[EditAction]:
        """Preview the action that would be redone."""
        if self.can_redo:
            return self._stack[self._index + 1]
        return None

    def save_point(self, name: str) -> None:
        """Mark the current position as a named save point."""
        self._saved_points[name] = self._index

    def restore_point(self, name: str) -> Optional[T]:
        """
        Restore to a named save point.
        Returns the snapshot at that point, or None if not found.
        """
        idx = self._saved_points.get(name)
        if idx is None or idx < 0 or idx >= len(self._stack):
            return None
        self._index = idx
        return self._stack[self._index].snapshot

    def get_history(self) -> List[EditAction]:
        """Get the full history list."""
        return list(self._stack)

    def get_recent(self, count: int = 10) -> List[EditAction]:
        """Get the most recent actions."""
        start = max(0, len(self._stack) - count)
        return self._stack[start:]

    def clear(self) -> None:
        """Clear the entire history."""
        self._stack.clear()
        self._index = -1
        self._saved_points.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Export history metadata as a dictionary."""
        return {
            'depth': len(self._stack),
            'index': self._index,
            'can_undo': self.can_undo,
            'can_redo': self.can_redo,
            'saved_points': list(self._saved_points.keys()),
            'recent_actions': [
                {
                    'description': a.description,
                    'timestamp': a.timestamp.isoformat(),
                }
                for a in self.get_recent(5)
            ],
        }
