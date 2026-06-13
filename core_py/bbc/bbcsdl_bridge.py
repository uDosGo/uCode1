"""
BBC BASIC for SDL 2.0 (BBCSDL) Python Bridge
=============================================
Replaces the old interpreter.py (2287 lines) with a thin subprocess wrapper
around the BBCSDL binary. BBCSDL is an actively maintained, cross-platform
BBC BASIC V runtime with 40+ built-in libraries.

Usage:
    bridge = BBCSDLBridge()
    bridge.start()
    result = bridge.execute("PRINT 2+2")
    bridge.install_library("gfxlib")
    bridge.call_procedure("PROC_gfx_init", 640, 480, 32)
    bridge.close()

Features:
    - Execute BBC BASIC code via stdin/stdout
    - Get/set variables (LENS integration)
    - Call PROC/FN procedures and functions
    - Install BBCSDL libraries (@lib$)
    - Run .bas files
    - Capture teletext grid (MODE 7)
    - Capture sprite state
"""

import subprocess
import json
import time
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class BBCSDLError(Exception):
    """BBCSDL bridge error"""
    pass


class BBCSDLBridge:
    """Manages embedded BBCSDL runtime with bidirectional data flow"""

    def __init__(self, bbcsdl_path: str = "bbcsdl", vault_path: Optional[Path] = None):
        self.bbcsdl_path = bbcsdl_path
        self.vault_path = vault_path or Path.home() / "Vaults"
        self.process: Optional[subprocess.Popen] = None
        self.libraries_loaded: set = set()
        self._prompt_pattern = re.compile(r'^(> |OK>|Ready\s*)$')

    def start(self) -> None:
        """Launch BBCSDL in console mode (stdin/stdout)"""
        if self.process:
            return

        try:
            self.process = subprocess.Popen(
                [self.bbcsdl_path, "-stdin"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line-buffered
            )
        except FileNotFoundError:
            raise BBCSDLError(
                f"BBCSDL not found at '{self.bbcsdl_path}'. "
                f"Run 'skills/bbcsdl-installer/run.sh' first."
            )

        # Wait for initial prompt
        self._wait_for_prompt()

    def execute(self, code: str) -> str:
        """Execute BBC BASIC code, return output"""
        if not self.process:
            self.start()

        self.process.stdin.write(code + "\n")
        self.process.stdin.flush()
        return self._read_until_prompt()

    def install_library(self, lib_name: str) -> None:
        """INSTALL @lib$ + library (from BBCSDL's library folder)"""
        if lib_name in self.libraries_loaded:
            return
        result = self.execute(f'INSTALL "@lib$/{lib_name}"')
        self.libraries_loaded.add(lib_name)
        return result

    def get_variable(self, name: str) -> Any:
        """Extract variable value (LENS operation)"""
        result = self.execute(f'PRINT {name}')
        return self._parse_value(result.strip())

    def set_variable(self, name: str, value: Any) -> None:
        """Set variable value (SKIN operation)"""
        if isinstance(value, str):
            self.execute(f'{name} = "{value}"')
        elif isinstance(value, bool):
            self.execute(f'{name} = {"TRUE" if value else "FALSE"}')
        else:
            self.execute(f'{name} = {value}')

    def call_function(self, func_name: str, *args) -> Any:
        """Call BBC BASIC FN function and return result"""
        args_str = ", ".join(repr(a) if isinstance(a, str) else str(a) for a in args)
        result = self.execute(f'PRINT FN{func_name}({args_str})')
        return self._parse_value(result.strip())

    def call_procedure(self, proc_name: str, *args) -> str:
        """Call BBC BASIC PROC procedure"""
        args_str = ", ".join(repr(a) if isinstance(a, str) else str(a) for a in args)
        return self.execute(f'PROC{proc_name}({args_str})')

    def run_file(self, path: Union[str, Path]) -> str:
        """Run a BBC BASIC program file"""
        return self.execute(f'RUN "{path}"')

    def chain_file(self, path: Union[str, Path]) -> str:
        """CHAIN a BBC BASIC program file (load and run, sharing variables)"""
        return self.execute(f'CHAIN "{path}"')

    def close(self) -> None:
        """Shutdown BBCSDL"""
        if not self.process:
            return
        try:
            self.execute("QUIT")
        except:
            pass
        self.process.terminate()
        self.process.wait(timeout=5)
        self.process = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # --- LENS Integration ---

    def capture_teletext_grid(self) -> Dict[str, Any]:
        """Extract MODE 7 teletext screen state"""
        self.install_library("mode7lib")
        grid_json = self.call_function("FN_mode7_get_grid")
        return {
            "type": "teletext",
            "data": grid_json,
            "timestamp": time.time()
        }

    def capture_sprites(self, max_sprites: int = 8) -> List[Dict[str, Any]]:
        """Extract sprite positions (max 8 per layer)"""
        sprites = []
        for i in range(max_sprites):
            visible = self.get_variable(f"sprite_visible_{i}")
            if visible:
                sprites.append({
                    "id": i,
                    "x": self.get_variable(f"sprite_x_{i}"),
                    "y": self.get_variable(f"sprite_y_{i}"),
                    "frame": self.get_variable(f"sprite_frame_{i}")
                })
        return sprites

    def capture_full_state(self) -> Dict[str, Any]:
        """Capture everything: teletext + sprites + variables"""
        return {
            "teletext": self.capture_teletext_grid(),
            "sprites": self.capture_sprites(),
            "timestamp": time.time()
        }

    # --- Internal ---

    def _wait_for_prompt(self, timeout: float = 10.0) -> None:
        """Wait for BBCSDL's prompt"""
        start = time.time()
        output = ""
        while time.time() - start < timeout:
            line = self.process.stdout.readline()
            if not line:
                time.sleep(0.05)
                continue
            output += line
            if self._prompt_pattern.match(line.strip()):
                return
        raise BBCSDLError(f"Timeout waiting for BBCSDL prompt. Output so far: {output[:200]}")

    def _read_until_prompt(self, timeout: float = 30.0) -> str:
        """Read output until prompt appears"""
        output = []
        start = time.time()
        while time.time() - start < timeout:
            line = self.process.stdout.readline()
            if not line:
                time.sleep(0.02)
                continue
            if self._prompt_pattern.match(line.strip()):
                break
            output.append(line)
        return "".join(output)

    def _parse_value(self, value_str: str) -> Any:
        """Convert BBC BASIC PRINT output to Python value"""
        if not value_str:
            return None
        # String (quoted)
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]
        # Boolean
        if value_str == "TRUE":
            return True
        if value_str == "FALSE":
            return False
        # Integer
        try:
            return int(value_str)
        except ValueError:
            pass
        # Float
        try:
            return float(value_str)
        except ValueError:
            pass
        # Return as string
        return value_str


# --- Convenience CLI ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python bbcsdl_bridge.py <command> [args...]")
        print("Commands:")
        print("  exec <code>       Execute BBC BASIC code")
        print("  run <file>        Run a .bas file")
        print("  get <var>         Get variable value")
        print("  set <var> <val>   Set variable value")
        print("  lib <name>        Install library")
        print("  teletext          Capture teletext grid")
        print("  sprites           Capture sprite state")
        sys.exit(1)

    command = sys.argv[1]
    bridge = BBCSDLBridge()
    bridge.start()

    try:
        if command == "exec" and len(sys.argv) > 2:
            result = bridge.execute(" ".join(sys.argv[2:]))
            print(result)
        elif command == "run" and len(sys.argv) > 2:
            result = bridge.run_file(sys.argv[2])
            print(result)
        elif command == "get" and len(sys.argv) > 2:
            result = bridge.get_variable(sys.argv[2])
            print(json.dumps(result))
        elif command == "set" and len(sys.argv) > 3:
            val = sys.argv[3]
            if val.isdigit():
                val = int(val)
            elif val.replace(".", "").isdigit():
                val = float(val)
            bridge.set_variable(sys.argv[2], val)
            print(f"OK: {sys.argv[2]} = {val}")
        elif command == "lib" and len(sys.argv) > 2:
            bridge.install_library(sys.argv[2])
            print(f"OK: {sys.argv[2]} loaded")
        elif command == "teletext":
            result = bridge.capture_teletext_grid()
            print(json.dumps(result, indent=2))
        elif command == "sprites":
            result = bridge.capture_sprites()
            print(json.dumps(result, indent=2))
        else:
            print(f"Unknown command: {command}")
    finally:
        bridge.close()
