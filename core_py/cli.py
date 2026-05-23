"""
uCode1 CLI - Command-line interface for uCode1

Usage:
  ucode1 [OPTIONS] [FILE]
  ucode1 snack [COMMAND] [OPTIONS]  # Snack management

Options:
  --help       Show this help
  --version    Show version
  --rust       Enable Rust acceleration (if available)
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
    """Lazy import of Runtime to avoid import errors when module doesn't exist."""
    try:
        from .runtime import Runtime
        return Runtime()
    except ImportError:
        return None


def main():
    # Handle subcommands
    if len(sys.argv) > 1:
        subcommand = sys.argv[1]
        if subcommand == 'snack':
            from .snack_cli import main as snack_main
            snack_main()
            return
        elif subcommand == 'ceefax':
            from .ceefax_cli import main as ceefax_main
            ceefax_main()
            return
    
    parser = argparse.ArgumentParser(
        description='uCode1 - BASIC-inspired scripting language',
        add_help=False
    )
    parser.add_argument('file', nargs='?', help='uCode1 program file')
    parser.add_argument('--help', action='store_true', help='Show this help message')
    parser.add_argument('--version', action='version', 
                       version='uCode1 0.1.0',
                       help='Show version')
    parser.add_argument('--rust', action='store_true',
                       help='Enable Rust acceleration (if available)')
    parser.add_argument('--repl', action='store_true',
                       help='Start interactive REPL')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    if args.help:
        parser.print_help()
        return
    
    runtime = _get_runtime()
    if runtime is None:
        print("Error: uCode1 runtime module not available")
        sys.exit(1)
    
    if args.repl:
        print("uCode1 REPL (Python mode)")
        print("Type 'exit' to quit")
        
        while True:
            try:
                line = input("> ")
                if line.lower() in ['exit', 'quit']:
                    break
                runtime.run_string(line)
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")
    elif args.file:
        try:
            runtime.run_file(args.file)
        except FileNotFoundError:
            print(f"File not found: {args.file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()