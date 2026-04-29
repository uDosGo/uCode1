"""
Models — Ollama client for TinyLlama/phi3:mini.

Manages local LLM inference via Ollama. Falls back gracefully if models
are not installed.
"""

import json
import subprocess
import sys
from typing import Optional


class ModelClient:
    """Client for running local LLM inference via Ollama."""

    DEFAULT_MODEL = "tinyllama:1.1b"
    EXTENDED_MODEL = "phi3:mini"

    def __init__(self, model: Optional[str] = None):
        self.model = model or self.DEFAULT_MODEL
        self._available = None

    @property
    def is_available(self) -> bool:
        if self._available is None:
            self._available = self._check_ollama()
        return self._available

    def _check_ollama(self) -> bool:
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def is_model_installed(self, model: Optional[str] = None) -> bool:
        model = model or self.model
        if not self.is_available:
            return False
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True, text=True, timeout=10
            )
            return model in result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 model: Optional[str] = None) -> str:
        """Generate a response from the LLM."""
        model = model or self.model
        if not self.is_available:
            return self._fallback_response(prompt)

        cmd = ["ollama", "run", model]
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"

        try:
            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return self._fallback_response(prompt)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Fallback when no LLM is available — rule-based replies."""
        prompt_lower = prompt.lower()

        if "hello" in prompt_lower or "hi " in prompt_lower:
            return "Hello! I'm OK Agent, your local assistant. How can I help?"
        if "help" in prompt_lower:
            return (
                "I can help with:\n"
                "  • uCode1 / BBC BASIC questions\n"
                "  • Vault searches (ucode vault search <query>)\n"
                "  • Snack management (ucode snack list)\n"
                "  • Grid parsing (ucode grid parse --text ...)\n"
                "Try: ok 'How do I print in BASIC?'"
            )
        if "print" in prompt_lower and "basic" in prompt_lower:
            return (
                "In BBC BASIC, use the PRINT statement:\n\n"
                "    10 PRINT \"Hello, World!\"\n"
                "    20 PRINT \"The answer is \"; 42\n"
            )
        if "for loop" in prompt_lower or ("for" in prompt_lower and "loop" in prompt_lower):
            return (
                "In BBC BASIC, use FOR...NEXT for loops:\n\n"
                "    10 FOR I = 1 TO 10\n"
                "    20   PRINT I\n"
                "    30 NEXT I\n\n"
                "You can also use STEP: FOR I = 1 TO 10 STEP 2\n"
            )
        if "if" in prompt_lower and "statement" in prompt_lower:
            return (
                "In BBC BASIC, use IF...THEN for conditionals:\n\n"
                "    10 IF score > 100 THEN PRINT \"Winner!\"\n"
                "    20 IF name$ = \"Fred\" THEN GOTO 100\n"
            )
        if "input" in prompt_lower and "basic" in prompt_lower:
            return "INPUT reads from keyboard:\n    10 INPUT \"Name: \", name$\n    20 PRINT \"Hello, \"; name$\n"
        if "mode 7" in prompt_lower or "mode7" in prompt_lower or "teletext" in prompt_lower:
            return (
                "MODE 7 is BBC BASIC's teletext mode:\n"
                "  • 40x25 character grid\n"
                "  • 64 colours with block graphics\n"
                "  • VDU 23,0,12,0;0;0;0; clears the screen\n"
                "  • COLOUR 1-7 sets text colour\n\n"
                "Example:\n"
                "    10 MODE 7\n"
                "    20 COLOUR 3\n"
                "    30 PRINT \"Hello from Ceefax!\"\n"
            )
        if "ok agent" in prompt_lower or "what can you do" in prompt_lower:
            return (
                "I'm OK Agent, your local AI assistant. I can:\n"
                "  • Answer BBC BASIC / uCode1 questions\n"
                "  • Search your vault (try: ok 'search vault for recipes')\n"
                "  • Run skills (ok skills)\n"
                "  • Switch moods (ok --mood playful)\n"
                "  • Run in C64 console mode (ok --c64)\n"
            )
        if "skill" in prompt_lower:
            return (
                "Available skills:\n"
                "  binder/search   — Search binder content\n"
                "  code/explain    — Explain code snippets\n"
                "  vault/list      — List vault contents\n"
                "  device/status   — Check device status\n"
                "Run `ok skills list` to see all skills."
            )

        return (
            "I'm not sure about that yet. I can help with BBC BASIC, "
            "uCode1 commands, vault searches, and device info. "
            "Try `ok --help` or ask me a specific question."
        )

    def stream_generate(self, prompt: str, system_prompt: Optional[str] = None):
        """Stream tokens from the LLM (generator)."""
        if not self.is_available:
            yield self._fallback_response(prompt)
            return

        cmd = ["ollama", "run", self.model]
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, _ = proc.communicate(input=full_prompt, timeout=120)
            yield stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            yield self._fallback_response(prompt)
