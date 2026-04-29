"""
Orchestrate — Main orchestrator for OK Agent.

Parses intent, dispatches to skills engine, falls back to LLM,
and manages conversation context.
"""

import sys
from typing import Optional

from .knowledge import format_context
from .models import ModelClient
from .personality import MoodState, format_response, inject_system_prompt
from .skills import SkillsEngine


class OKOrchestrator:
    """Main OK Agent orchestrator."""

    def __init__(self, skills_dir: Optional[str] = None):
        self.models = ModelClient()
        self.skills = SkillsEngine(skills_dir)
        self.mood = MoodState()
        self.context: list[dict] = []  # Simple message history

    def process(self, user_input: str, mood: Optional[MoodState] = None) -> str:
        """Process a user request and return a response."""
        if mood:
            self.mood = mood

        user_input = user_input.strip()
        if not user_input:
            return "Hi! Ask me something — I can help with BBC BASIC, vault searches, and more."

        # Add to context
        self.context.append({"role": "user", "content": user_input})

        # 1. Try skill dispatch for actionable requests
        skill = self.skills.find_skill(user_input)
        if skill:
            # Extract parameters from the input
            params = self._extract_params(user_input, skill)
            result = self.skills.execute(skill, params)
            self.context.append({"role": "assistant", "content": result})
            return format_response(result, self.mood)

        # 2. Gather knowledge context
        knowledge_ctx = format_context(user_input)

        # 3. Build system prompt with mood + knowledge
        system = inject_system_prompt(self.mood)
        if knowledge_ctx:
            system += f"\n\nRelevant knowledge:\n{knowledge_ctx}"

        # 4. Generate LLM response
        # Use phi3 if energy is high and available
        model = self.models.DEFAULT_MODEL
        if self.mood.energy == "high" and self.models.is_model_installed(self.models.EXTENDED_MODEL):
            model = self.models.EXTENDED_MODEL

        response = self.models.generate(user_input, system_prompt=system, model=model)
        self.context.append({"role": "assistant", "content": response})
        return format_response(response, self.mood)

    def _extract_params(self, user_input: str, skill) -> dict[str, str]:
        """Simple parameter extraction from user input.
        Looks for --key=value or "key value" patterns.
        """
        params = {}
        parts = user_input.split()
        for i, part in enumerate(parts):
            if "=" in part and not part.startswith("--"):
                key, val = part.split("=", 1)
                params[key] = val
            elif part.startswith("--") and "=" in part:
                _, rest = part.split("--", 1)
                if "=" in rest:
                    key, val = rest.split("=", 1)
                    params[key] = val
            elif part.startswith("--") and i + 1 < len(parts):
                key = part.lstrip("-")
                if not parts[i + 1].startswith("-"):
                    params[key] = parts[i + 1]
        return params


# Convenience function for one-shot use
def ask(query: str, **kwargs) -> str:
    """One-shot question to OK Agent."""
    from .personality import MoodState
    orch = OKOrchestrator()
    mood = MoodState()
    if "mood" in kwargs:
        mood.mood = kwargs["mood"]
    if "energy" in kwargs:
        mood.energy = kwargs["energy"]
    if "tone" in kwargs:
        mood.tone = kwargs["tone"]
    return orch.process(query, mood=mood)
