"""
Narrator & Lexicon — Story generation and term mapping for uDos.

Narrator: Converts feed/snack events into human-readable stories
using the Wizard-in-a-Dungeon metaphor.

Lexicon: The 3-lane term mapping system (Dev / Story / Student)
that defines what things are called across the uDos ecosystem.
"""

from .narrator import NarratorEngine
from .lexicon import Lexicon, LexiconEntry, LANE_DEV, LANE_STORY, LANE_STUDENT
from .cli import main as cli_main

__all__ = ["NarratorEngine", "Lexicon", "LexiconEntry", "LANE_DEV", "LANE_STORY", "LANE_STUDENT", "cli_main"]