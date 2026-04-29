"""
Personality — Mood/tone/energy injection for OK Agent.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MoodState:
    """Current mood/energy/tone settings for a conversation."""
    mood: str = "calm"         # calm, playful, professional
    energy: str = "normal"     # low, normal, high
    tone: str = "concise"      # concise, professional, warm
    verbosity: str = "normal"  # low, normal, high


DEFAULT_MOOD = MoodState()


def parse_flags(args: list[str]) -> tuple[MoodState, list[str]]:
    """Extract --mood, --energy, --tone flags from arg list.
    Returns (mood_state, remaining_args).
    """
    mood = MoodState()
    remaining = []
    skip_next = False

    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg == "--mood" and i + 1 < len(args):
            mood.mood = args[i + 1]
            skip_next = True
        elif arg == "--energy" and i + 1 < len(args):
            mood.energy = args[i + 1]
            skip_next = True
        elif arg == "--tone" and i + 1 < len(args):
            mood.tone = args[i + 1]
            skip_next = True
        elif arg.startswith("--mood="):
            mood.mood = arg.split("=", 1)[1]
        elif arg.startswith("--energy="):
            mood.energy = arg.split("=", 1)[1]
        elif arg.startswith("--tone="):
            mood.tone = arg.split("=", 1)[1]
        else:
            remaining.append(arg)

    return mood, remaining


def inject_system_prompt(mood: MoodState) -> str:
    """Generate system prompt based on mood state."""
    parts = [
        "You are OK Agent, the friendly local AI assistant for uDos.",
        "You run entirely offline. No cloud. No telemetry.",
        "You help with: BBC BASIC, uCode1, vault, and device info only.",
    ]

    # Mood
    if mood.mood == "playful":
        parts.append("Be playful, use emojis, be enthusiastic and fun.")
    elif mood.mood == "calm":
        parts.append("Be gentle, measured, reassuring. Keep it simple.")
    elif mood.mood == "professional":
        parts.append("Be formal, precise, and thorough. No fluff.")

    # Tone
    if mood.tone == "concise":
        parts.append("Keep answers short and direct. One sentence when possible.")
    elif mood.tone == "warm":
        parts.append("Be warm and friendly. Use the user's name if known.")

    # Energy
    if mood.energy == "low":
        parts.append("Use minimal model. Shortest possible helpful answers.")

    return " ".join(parts)


def format_response(text: str, mood: MoodState) -> str:
    """Apply mood-based formatting to a response."""
    if mood.mood == "playful":
        if not any(e in text for e in ["😊", "✨", "🎮", "💾"]):
            text = text + " 😊"
    return text
