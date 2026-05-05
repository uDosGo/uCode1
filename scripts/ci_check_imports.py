#!/usr/bin/env python3
"""
CI script: Verify all core uCode1 modules import cleanly.
Exits with code 1 if any module fails to import.
"""
import os
import sys

# Ensure the project root is on sys.path (for running without pip install -e .)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

MODULES = [
    "core_py.bbc.interpreter",
    "core_py.bbc.lens",
    "core_py.bbc.skin",
    "core_py.bbc.mcp_bridge",
    "core_py.bbc.spool_bridge",
    "core_py.bbc.lens_skin_mcp",
    "core_py.snack_container",
    "core_py.snack",
    "core_py.grid",
    "core_py.text",
    "core_py.themes",
    "core_py.thinui",
    "core_py.usxd",
    "core_py.export",
    "core_py.liquid_engine",
    "core_py.mdx",
    "core_py.plugin",
    "core_py.relic",
    "core_py.binder",
    "core_py.cell",
    "core_py.feed",
    "narrator",
    "ok_agent",
    "ucode1",
]

failures = []
for mod in MODULES:
    try:
        __import__(mod)
        print(f"OK: {mod}")
    except ImportError as e:
        failures.append((mod, str(e)))
        print(f"FAIL: {mod}: {e}")

if failures:
    print(f"\n{len(failures)} module(s) failed to import")
    sys.exit(1)
else:
    print(f"\nAll {len(MODULES)} modules imported successfully")
