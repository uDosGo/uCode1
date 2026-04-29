"""
Skills — Predictable function-calling engine for OK Agent.

Skills are YAML-defined, executable command templates that map user intents
to real `ucode` CLI commands. No hallucination — every skill executes a real command.
"""

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class SkillParameter:
    name: str
    type: str = "string"
    required: bool = False
    description: str = ""


@dataclass
class Skill:
    name: str
    description: str = ""
    parameters: list[SkillParameter] = field(default_factory=list)
    action: str = ""
    output: str = "text"

    @classmethod
    def from_dict(cls, data: dict) -> "Skill":
        params = []
        for p in data.get("parameters", []):
            params.append(SkillParameter(
                name=p.get("name", ""),
                type=p.get("type", "string"),
                required=p.get("required", False),
                description=p.get("description", ""),
            ))
        return cls(
            name=data.get("name", "unknown"),
            description=data.get("description", ""),
            parameters=params,
            action=data.get("action", ""),
            output=data.get("output", "text"),
        )


class SkillsEngine:
    """Loads, discovers, and executes .skill files."""

    def __init__(self, skills_dir: Optional[str] = None):
        self.skills_dir = skills_dir or str(
            Path(__file__).parent.parent / "skills"
        )
        self._skills: dict[str, Skill] = {}

    def discover(self) -> dict[str, Skill]:
        """Scan skills directory and load all .skill files."""
        skills = {}
        base = Path(self.skills_dir)
        if not base.exists():
            return skills

        for f in base.rglob("*.skill"):
            try:
                data = yaml.safe_load(f.read_text())
                if data and "name" in data:
                    skill = Skill.from_dict(data)
                    skills[skill.name] = skill
            except (yaml.YAMLError, IOError):
                pass

        self._skills = skills
        return skills

    def find_skill(self, query: str) -> Optional[Skill]:
        """Find a skill by exact name or fuzzy match on description."""
        q = query.lower()

        # Exact name match
        if q in self._skills:
            return self._skills[q]

        # Fuzzy: find best matching skill by description
        best_score = 0
        best_skill = None
        for name, skill in self._skills.items():
            score = 0
            if q in name.lower():
                score += 10
            if q in skill.description.lower():
                score += 5
            for p in skill.parameters:
                if q in p.name.lower():
                    score += 2
            if score > best_score:
                best_score = score
                best_skill = skill

        return best_skill if best_score > 0 else None

    def execute(self, skill: Skill, params: dict[str, str]) -> str:
        """Execute a skill's action with given parameters."""
        if not skill.action:
            return f"Skill '{skill.name}' has no action defined."

        # Substitute parameters into the action template
        cmd = skill.action
        for key, value in params.items():
            placeholder = "{{{" + key + "}}}"
            if placeholder in cmd:
                cmd = cmd.replace(placeholder, value)
            placeholder = "{{{" + key + "}}}"
            # Try mustache syntax too
            cmd = cmd.replace(f"{{{{{key}}}}}", value)

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip() or f"✅ '{skill.name}' completed."
            else:
                return f"❌ Error: {result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return "❌ Command timed out."
        except Exception as e:
            return f"❌ Failed to execute: {e}"

    def list_skills(self) -> str:
        """List all discovered skills as formatted text."""
        if not self._skills:
            self.discover()
        if not self._skills:
            return "No skills found."

        lines = ["Available skills:"]
        for name, skill in sorted(self._skills.items()):
            params = " ".join(
                f"[{p.name}]" for p in skill.parameters if p.required
            )
            lines.append(f"  • {name} {params}")
            if skill.description:
                lines.append(f"    {skill.description}")
        return "\n".join(lines)
