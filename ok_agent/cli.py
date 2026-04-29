"""
CLI — `ok` command for OK Agent.

Usage:
  ok [--mood <mood>] [--energy <energy>] [--tone <tone>] [<question>]
  ok skills list
  ok skill show <name>
  ok set preference <key> <value>
  ok upgrade --extended

Examples:
  ok "How do I print in BASIC?"
  ok --mood playful "Hello!"
  ok skills list
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Allow running as `python3 ok_agent/cli.py` directly
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from ok_agent.models import ModelClient
    from ok_agent.orchestrate import OKOrchestrator
    from ok_agent.personality import MoodState, parse_flags
    from ok_agent.skills import SkillsEngine
else:
    from .models import ModelClient
    from .orchestrate import OKOrchestrator
    from .personality import MoodState, parse_flags
    from .skills import SkillsEngine


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ok",
        description="OK Agent — Local AI assistant for uDos",
    )
    p.add_argument("question", nargs="*", help="Question to ask")
    p.add_argument("--mood", choices=["calm", "playful", "professional"],
                   help="Set response mood")
    p.add_argument("--energy", choices=["low", "normal", "high"],
                   help="Set energy level")
    p.add_argument("--tone", choices=["concise", "professional", "warm"],
                   help="Set response tone")
    p.add_argument("--model", help="Override LLM model")
    p.add_argument("--c64", action="store_true",
                   help="C64 BASIC console mode (retro terminal)")

    sub = p.add_subparsers(dest="command", metavar="")

    # `ok skills`
    skills_p = sub.add_parser("skills", help="List available skills")

    # `ok skill show <name>`
    skill_show = sub.add_parser("skill", help="Show skill details")
    skill_show.add_argument("name", help="Skill name")

    # `ok set preference <key> <value>`
    set_p = sub.add_parser("set", help="Set user preference")
    set_p.add_argument("preference", nargs="+", help="preference key value")

    # `ok upgrade --extended`
    upgrade_p = sub.add_parser("upgrade", help="Upgrade OK Agent")
    upgrade_p.add_argument("--extended", action="store_true",
                           help="Install phi3:mini extended model")

    return p


def main():
    # Check for --c64 flag before parsing
    if "--c64" in sys.argv:
        from ok_agent.c64_console import run_c64_console
        run_c64_console()
        return

    # Detect if we have a subcommand vs a free-form question
    known = {"skills", "skill", "set", "upgrade"}
    has_sub = len(sys.argv) > 1 and sys.argv[1] in known

    if has_sub:
        parser = build_parser()
        args = parser.parse_args()
    else:
        # Free-form question: everything is the question
        question = " ".join(sys.argv[1:]).strip()

        # Parse --mood/--energy/--tone flags manually
        mood = MoodState()
        q_parts = []
        skip = False
        for i, arg in enumerate(sys.argv[1:]):
            if skip:
                skip = False
                continue
            if arg == "--mood" and i + 1 < len(sys.argv[1:]):
                mood.mood = sys.argv[1:][i + 1]
                skip = True
            elif arg == "--energy" and i + 1 < len(sys.argv[1:]):
                mood.energy = sys.argv[1:][i + 1]
                skip = True
            elif arg == "--tone" and i + 1 < len(sys.argv[1:]):
                mood.tone = sys.argv[1:][i + 1]
                skip = True
            elif arg.startswith(("--mood=", "--energy=", "--tone=")):
                continue
            else:
                q_parts.append(arg)

        question = " ".join(q_parts).strip()

        if question:
            orch = OKOrchestrator()
            response = orch.process(question, mood=mood)
            print(response)
        else:
            # Interactive REPL
            print("OK Agent — Local AI assistant. Type 'exit' to quit.")
            if not ModelClient().is_available:
                print("⚠️  Ollama not found. Running in fallback mode (rule-based).")
            print()
            orch = OKOrchestrator()
            while True:
                try:
                    q = input("> ").strip()
                    if q.lower() in ("exit", "quit", "q"):
                        print("Bye! 👋")
                        break
                    if not q:
                        continue
                    response = orch.process(q, mood=mood)
                    print(f"< {response}")
                except (KeyboardInterrupt, EOFError):
                    print("\nBye! 👋")
                    break
        return

    # Handle subcommands
    if args.command == "skills":
        engine = SkillsEngine()
        engine.discover()
        print(engine.list_skills())
        return

    if args.command == "skill":
        engine = SkillsEngine()
        engine.discover()
        if not engine._skills:
            engine.discover()
        if args.name and args.name in engine._skills:
            s = engine._skills[args.name]
            print(f"Name:        {s.name}")
            print(f"Description: {s.description}")
            print(f"Action:      {s.action}")
            print("Parameters:")
            for p in s.parameters:
                req = "(required)" if p.required else "(optional)"
                print(f"  {p.name}: {p.type} {req}")
        else:
            print("Skill not found. Use `ok skills list` to see available skills.")
        return

    if args.command == "set":
        prefs_file = Path.home() / "uDos" / "memory" / "user" / "profile.json"
        prefs_file.parent.mkdir(parents=True, exist_ok=True)
        prefs = {}
        if prefs_file.exists():
            try:
                prefs = json.loads(prefs_file.read_text())
            except json.JSONDecodeError:
                pass
        if len(args.preference) >= 2:
            key = args.preference[0]
            value = " ".join(args.preference[1:])
            prefs[key] = value
            prefs_file.write_text(json.dumps(prefs, indent=2))
            print(f"✅ Set {key} = {value}")
        else:
            print("Usage: ok set <key> <value>")
        return

    if args.command == "upgrade":
        if args.extended:
            print("Installing phi3:mini extended model...")
            import subprocess
            try:
                subprocess.run(["ollama", "pull", "phi3:mini"], check=True)
                print("✅ phi3:mini installed!")
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("❌ Failed to install phi3:mini. Is Ollama installed?")
        else:
            print("Usage: ok upgrade --extended")
        return

    # Interactive or one-shot mode
    orch = OKOrchestrator()
    mood = MoodState()

    # Apply flags from subcommand mode
    if hasattr(args, 'mood') and args.mood:
        mood.mood = args.mood
    if hasattr(args, 'energy') and args.energy:
        mood.energy = args.energy
    if hasattr(args, 'tone') and args.tone:
        mood.tone = args.tone

    question = " ".join(getattr(args, 'question', []) or [])

    if question:
        response = orch.process(question, mood=mood)
        print(response)
    else:
        print("OK Agent — Local AI assistant. Type 'exit' to quit.")
        if not ModelClient().is_available:
            print("⚠️  Ollama not found. Running in fallback mode (rule-based).")
        print()
        while True:
            try:
                q = input("> ").strip()
                if q.lower() in ("exit", "quit", "q"):
                    print("Bye! 👋")
                    break
                if not q:
                    continue
                response = orch.process(q, mood=mood)
                print(f"< {response}")
            except (KeyboardInterrupt, EOFError):
                print("\nBye! 👋")
                break


if __name__ == "__main__":
    main()
