#!/usr/bin/env python3
"""
uCode1 CLI Entry Point

This is the main entry point for uCode1 command-line interface.
It handles both the main uCode1 commands and snack subcommands.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))


def main():
    """Main CLI entry point"""
    # Handle snack subcommand
    if len(sys.argv) > 1 and sys.argv[1] == 'snack':
        try:
            from ucode1.snack_cli import main as snack_main
            snack_main()
            return
        except ImportError as e:
            print(f"Error loading snack CLI: {e}")
            print("Please ensure uCode1 is properly installed.")
            sys.exit(1)
    
    # Handle main uCode1 commands
    try:
        from ucode1.cli import main as ucode_main
        ucode_main()
    except ImportError as e:
        print(f"Error loading uCode1 CLI: {e}")
        print("Please ensure uCode1 is properly installed.")
        sys.exit(1)


if __name__ == '__main__':
    main()