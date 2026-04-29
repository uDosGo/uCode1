"""
Knowledge — Domain-restricted RAG for OK Agent.

Indexes and searches the four allowed knowledge domains:
1. General Library (Ceefax, BBC BASIC, uDos basics)
2. User Vault (projects, private notes)
3. BBC BASIC / uCode1 Reference
4. Sonic Device Library
"""

import json
import os
from pathlib import Path
from typing import Optional

# ── Path helpers ────────────────────────────────────────────────────────────

def _udos_home() -> Path:
    return Path.home() / "uDos" / "core" / "ucode1"


def _vault_path() -> Path:
    return Path.home() / "Code" / "Vault"


# ── Domain 1: General Knowledge Library ─────────────────────────────────────

GENERAL_KNOWLEDGE: dict[str, str] = {
    "ceefax": (
        "Ceefax is the BBC's teletext service. Pages are 40x25 characters. "
        "Mode 7 uses 64 colours with block graphics (0x00-0x1F). "
        "Pages are navigated via 3-digit codes (100-899)."
    ),
    "mode7": (
        "MODE 7 is BBC BASIC's teletext mode. It provides a 40x25 character grid "
        "with 64 colours, block graphics, and flash/reveal effects. "
        "Use VDU 23,0,12,0;0;0;0; to clear the screen."
    ),
    "bbc_basic_print": (
        "In BBC BASIC, PRINT displays text: PRINT \"Hello\""
    ),
    "bbc_basic_for": (
        "FOR loop: FOR I = 1 TO 10 : PRINT I : NEXT I. "
        "You can use STEP for non-unit increments: FOR I = 1 TO 10 STEP 2"
    ),
    "bbc_basic_if": (
        "IF condition THEN statements. Example: IF score > 100 THEN PRINT \"Winner!\""
    ),
    "bbc_basic_input": (
        "INPUT reads from the keyboard: INPUT \"Name: \", name$"
    ),
    "bbc_basic_mode": (
        "MODE 7 selects teletext mode (40x25, block graphics). "
        "MODE 0 is 640x256 2-colour. MODE 1 is 320x256 4-colour."
    ),
    "udos_vault": (
        "The vault is at ~/Code/Vault. Use `ucode vault list /` to browse. "
        "Notes are markdown files with YAML frontmatter."
    ),
    "udos_snack": (
        "Snacks are executable units. List with `ucode snack list`. "
        "Run with `ucode snack run <id>`."
    ),
    "udos_grid": (
        "ASCII grids use box-drawing characters. Parse with `ucode grid parse`."
    ),
    "udos_ok": (
        "OK Agent is the local AI assistant. Use `ok <question>` or `ucode ok <question>`. "
        "Flags: --mood (calm/playful/professional), --energy (low/normal/high). "
        "Use `ok --c64` for retro C64 console mode."
    ),
}


def search_general(query: str) -> list[str]:
    """Search general knowledge library."""
    results = []
    q = query.lower()
    for key, value in GENERAL_KNOWLEDGE.items():
        if q in key.lower() or q in value.lower():
            results.append(value)
    return results


# ── Domain 2: User Vault ────────────────────────────────────────────────────

def search_vault(query: str, max_results: int = 5) -> list[dict]:
    """Search vault files locally."""
    vault = _vault_path()
    if not vault.exists():
        return []

    results = []
    q = query.lower()
    for f in vault.rglob("*.md"):
        if q in f.stem.lower():
            results.append({
                "path": str(f.relative_to(vault)),
                "title": f.stem,
            })
        if len(results) >= max_results:
            break
    return results


# ── Domain 3: BBC BASIC Reference ───────────────────────────────────────────

BBC_BASIC_KEYWORDS = {
    "PRINT": "Output text or numbers to the screen.",
    "INPUT": "Read input from the keyboard.",
    "IF": "Conditional execution: IF condition THEN ...",
    "FOR": "Loop: FOR var = start TO end ... NEXT var",
    "WHILE": "Loop while condition is true: WHILE condition ... ENDWHILE",
    "REPEAT": "Loop until condition: REPEAT ... UNTIL condition",
    "DIM": "Dimension an array: DIM array(10)",
    "PROC": "Define a procedure: DEF PROCname ... ENDPROC",
    "FN": "Define a function: DEF FNname(x) = x * 2",
    "REM": "Comment: REM This is a comment",
    "MODE": "Set screen mode: MODE 7 (teletext), MODE 0 (high-res)",
    "VDU": "Send command to VDU driver: VDU 23,0,12,0;0;0;0;",
    "COLOUR": "Set text colour: COLOUR 1 (red), 2 (green), 3 (yellow)",
    "GOTO": "Jump to line number: GOTO 100",
    "GOSUB": "Call subroutine: GOSUB 1000 ... RETURN",
    "PLOT": "Plot a point: PLOT 69, x, y",
    "DRAW": "Draw a line: DRAW x, y",
    "MOVE": "Move cursor: MOVE x, y",
}


def search_basic(query: str) -> list[str]:
    """Search BBC BASIC reference."""
    q = query.upper()
    results = []
    for kw, desc in BBC_BASIC_KEYWORDS.items():
        if q in kw or q in desc.upper():
            results.append(f"{kw}: {desc}")
    return results


# ── Domain 4: Sonic Device Library ──────────────────────────────────────────

def get_device_info() -> list[dict]:
    """Read Sonic device inventory from disk."""
    devices_path = _udos_home() / "knowledge" / "devices"
    if not devices_path.exists():
        return []
    devices = []
    for f in devices_path.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            devices.append(data)
        except (json.JSONDecodeError, IOError):
            pass
    return devices


# ── Unified Search ──────────────────────────────────────────────────────────

def search_all(query: str) -> dict[str, list]:
    """Search all knowledge domains for a query."""
    return {
        "general": search_general(query),
        "basic": search_basic(query),
        "vault": search_vault(query),
        "devices": get_device_info(),
    }


def format_context(query: str) -> str:
    """Build a context string from all knowledge domains."""
    ctx = search_all(query)
    parts = []

    if ctx["general"]:
        parts.append("General: " + " ".join(ctx["general"]))
    if ctx["basic"]:
        parts.append("BBC BASIC: " + " ".join(ctx["basic"]))
    if ctx["vault"]:
        vault_items = "; ".join(
            f"{r['path']} ({r['title']})" for r in ctx["vault"]
        )
        parts.append(f"Vault matches: {vault_items}")

    return "\n".join(parts) if parts else ""
