#!/usr/bin/env python3
"""
uCode1 CLI Entry Point — delegates to unified ucode CLI.

All commands consolidated under the single `./ucode` entry point.
This stub is kept for backwards compatibility.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Delegate to the unified ucode CLI."""
    from ucode import main as ucode_main
    ucode_main()

if __name__ == '__main__':
    main()
