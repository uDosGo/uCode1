"""
uCode1 CLI - Command-line interface for uCode1

Usage:
  ucode1 [OPTIONS] [FILE]

Options:
  --help       Show this help
  --version    Show version
  --rust       Enable Rust acceleration (if available)
  --repl       Start interactive REPL
  --debug      Enable debug output
"""

import sys
import argparse
from .runtime import Runtime


def main():
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
    
    runtime = Runtime()
    
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