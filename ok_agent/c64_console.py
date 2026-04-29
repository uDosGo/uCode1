"""
C64 BASIC Console — Retro terminal mode for OK Agent.

Provides a Commodore 64 themed interaction surface with:
- Teletext/Mode 7 block graphics
- BBC BASIC-aware REPL
- `/` commands for skills, mood, energy
- Coloured ANSI output
"""

import shutil
import sys
from typing import Optional

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, sys.path[0] + "/..")
    from ok_agent.models import ModelClient
    from ok_agent.orchestrate import OKOrchestrator
    from ok_agent.personality import MoodState
    from ok_agent.skills import SkillsEngine
else:
    from .models import ModelClient
    from .orchestrate import OKOrchestrator
    from .personality import MoodState
    from .skills import SkillsEngine

# ANSI colour codes for C64 theme
C64_BG = "\033[48;2;108;52;148m"    # Purple
C64_FG = "\033[38;2;255;255;255m"   # White text
C64_CYAN = "\033[38;2;0;255;255m"
C64_YELLOW = "\033[38;2;255;255;0m"
C64_GREEN = "\033[38;2;87;200;100m"
C64_RED = "\033[38;2;255;0;0m"
RESET = "\033[0m"
BOLD = "\033[1m"


def c64_header():
    """Render the C64 startup banner."""
    cols = shutil.get_terminal_size().columns
    width = min(cols, 60)

    print(f"{C64_CYAN}{'─' * width}{RESET}")
    print(f"{C64_YELLOW}{BOLD}  ╔══════════════════════════════════════════╗{RESET}")
    print(f"{C64_YELLOW}{BOLD}  ║     OK AGENT  V1.0   64K RAM SYSTEM    ║{RESET}")
    print(f"{C64_YELLOW}{BOLD}  ║  38711 BASIC BYTES FREE                 ║{RESET}")
    print(f"{C64_YELLOW}{BOLD}  ╚══════════════════════════════════════════╝{RESET}")
    print(f"{C64_CYAN}{'─' * width}{RESET}")
    print(f"{C64_GREEN}READY.{RESET}")
    print()


def c64_border():
    """Return a teletext-style separator."""
    cols = shutil.get_terminal_size().columns
    return f"{C64_CYAN}─" * min(cols, 60) + RESET


HELP_TEXT = f"""
{C64_YELLOW}OK Agent — C64 BASIC Console{RESET}

{C64_CYAN}Commands:{RESET}
  /help            Show this help
  /skills          List available skills
  /mood <mode>     Set mood (calm, playful, professional)
  /energy <level>  Set energy (low, normal, high)
  /tone <style>    Set tone (concise, professional, warm)
  /exit            Quit

{C64_CYAN}Examples:{RESET}
  PRINT "HELLO"    → BBC BASIC advice
  help             → General assistance
  search vault     → Vault search skill
  /mood playful    → Playful responses
"""


def run_c64_console():
    """Run the C64 BASIC console interactive mode."""
    orch = OKOrchestrator()
    mood = MoodState()
    mood.mood = "calm"
    mood.tone = "concise"

    # Check availability
    if not ModelClient().is_available:
        print(f"{C64_YELLOW}⚠ Ollama not found. Running in fallback mode.{RESET}")

    c64_header()

    while True:
        try:
            line = input(f"{C64_GREEN}>{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{C64_GREEN}READY.{RESET}")
            print(f"{C64_YELLOW}Bye! 👋{RESET}")
            break

        if not line:
            continue

        # Handle / commands
        if line.startswith("/"):
            parts = line[1:].split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "exit" or cmd == "quit":
                print(f"{C64_GREEN}READY.{RESET}")
                print(f"{C64_YELLOW}Bye! 👋{RESET}")
                break
            elif cmd == "help":
                print(HELP_TEXT)
            elif cmd == "skills":
                engine = SkillsEngine()
                engine.discover()
                print(f"{C64_CYAN}{engine.list_skills()}{RESET}")
            elif cmd == "mood" and arg:
                mood.mood = arg
                print(f"{C64_GREEN}Mood set to: {arg}{RESET}")
            elif cmd == "energy" and arg:
                mood.energy = arg
                print(f"{C64_GREEN}Energy set to: {arg}{RESET}")
            elif cmd == "tone" and arg:
                mood.tone = arg
                print(f"{C64_GREEN}Tone set to: {arg}{RESET}")
            else:
                print(f"{C64_RED}? Unknown command{RESET}")
            continue

        # Process as query
        response = orch.process(line, mood=mood)
        print(f"{C64_CYAN}{response}{RESET}")
        print()


if __name__ == "__main__":
    run_c64_console()
