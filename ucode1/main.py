#!/usr/bin/env python3
"""
uCode1 main entry point
"""

import sys
import os

# Add the parent directory to path so we can import ucode1
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ucode1.cli import main

if __name__ == '__main__':
    main()