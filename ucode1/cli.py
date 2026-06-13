"""
uCode1 CLI - Command-line interface for uCode1

Usage:
  ucode1 [OPTIONS] [FILE]
  ucode1 snack [COMMAND] [OPTIONS]  # Snack management

Options:
  --help       Show this help
  --version    Show version
  --repl       Start interactive REPL
  --debug      Enable debug output

Snack Commands:
  ucode1 snack list        List available snacks
  ucode1 snack show ID     Show snack details
  ucode1 snack create     Create a new snack
  ucode1 snack validate    Validate a snack file
  ucode1 snack run FILE    Run a snack
  ucode1 snack test        Test snack functionality
"""

import sys
import argparse


def _get_runtime():
    """Lazy import of UDORuntime from core_py.udo_runtime."""
    try:
        from core_py.udo_runtime import UDORuntime
        return UDORuntime()
    except ImportError:
        return None


def _get_liquid_engine():
    """Lazy import of LiquidEngine from core_py.liquid_engine."""
    try:
        from core_py.liquid_engine import LiquidEngine
        return LiquidEngine()
    except ImportError:
        return None


def _run_bas_file(filepath: str) -> None:
    """Render a .bas file through the Liquid engine.
    
    .bas files are BBC BASIC-style programs. The Liquid engine renders
    any Liquid template syntax within them. Full BASIC execution requires
    a BASIC interpreter (planned for future release).
    """
    engine = _get_liquid_engine()
    if engine is None:
        print("Error: Liquid engine not available")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        source = f.read()
    
    result = engine.render(source, {"file": filepath})
    print(result)


def _run_repl(runtime) -> None:
    """Start an interactive REPL using UDORuntime."""
    import sys as _sys
    
    print("uCode1 REPL (UDO Runtime mode)")
    print("Type 'exit' to quit")
    print("Available: list_skills, list_tasks, list_variables, run_skill <id>")
    
    while True:
        try:
            line = input("> ")
            if line.lower() in ['exit', 'quit']:
                break
            parts = line.strip().split()
            if not parts:
                continue
            cmd = parts[0].lower()
            if cmd == 'list_skills':
                for s in runtime.list_skills():
                    print(f"  {s.id}: {s.name} ({'enabled' if s.enabled else 'disabled'})")
            elif cmd == 'list_tasks':
                for t in runtime.list_tasks():
                    print(f"  {t.id}: {t.type} (priority {t.priority})")
            elif cmd == 'list_variables':
                for v in runtime.list_variables():
                    print(f"  {v.key} = {'***' if v.encrypted else v.value} ({v.scope})")
            elif cmd == 'run_skill' and len(parts) >= 2:
                result = runtime.run_skill(parts[1])
                print(f"Result: {result}")
            else:
                print(f"Unknown command: {cmd}")
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {e}")



def main():
    # Handle snack subcommand
    if len(sys.argv) > 1 and sys.argv[1] == 'snack':
        from .snack_cli import main as snack_main
        snack_main()
        return
    
    parser = argparse.ArgumentParser(
        description='uCode1 - BASIC-inspired scripting language',
        add_help=False
    )
    parser.add_argument('file', nargs='?', help='uCode1 program file (.bas)')
    parser.add_argument('--help', action='store_true', help='Show this help message')
    parser.add_argument('--version', action='version', 
                       version='uCode1 1.0.0',
                       help='Show version')
    parser.add_argument('--repl', action='store_true',
                       help='Start interactive REPL')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    if args.help:
        parser.print_help()
        return
    
    if args.repl:
        runtime = _get_runtime()
        if runtime is None:
            print("Error: uCode1 runtime module not available")
            sys.exit(1)
        _run_repl(runtime)
    elif args.file:
        _run_bas_file(args.file)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

