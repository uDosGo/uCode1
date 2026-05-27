"""
ACS CLI — Command-line interface for the ACS Emulator

Usage:
  ucode acs [COMMAND] [OPTIONS]

Commands:
  run          Run an ACS game from a disk image
  step         Single-step through execution
  state        Show current emulator state
  reset        Reset the emulator
  load-rom     Load a ROM file
  load-disk    Load a disk image
  debug        Start interactive debugger
  mcp          Send MCP commands to the emulator
  info         Show emulator information
  save-state   Save emulator state to file
  load-state   Load emulator state from file
  key          Send a key press to the emulator
  type         Type text into the emulator
  export       Export display to HTML/ANSI/JSON
  help         Show help for a command

Examples:
  ucode acs load-rom apple2.rom
  ucode acs load-disk mygame.dsk
  ucode acs run --max-instructions 10000
  ucode acs step
  ucode acs state
  ucode acs key 65          # Press 'A'
  ucode acs type "HELLO"
  ucode acs export --format html
  ucode acs mcp send PAUSE
  ucode acs debug
"""

import sys
import os
import json
import argparse
import time
from pathlib import Path
from typing import Optional, Dict, Any

# Add core_py to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core_py.bbc.acs import (
    ACS_Emulator,
    ACS_EmulatorConfig,
    ACS_DisplayMode,
)


class ACS_CLI:
    """Command-line interface for the ACS Emulator"""

    def __init__(self):
        self.config = ACS_EmulatorConfig()
        self.emulator: Optional[ACS_Emulator] = None
        self._init_emulator()

    def _init_emulator(self):
        """Initialize the emulator with default config."""
        self.emulator = ACS_Emulator(self.config)

    def main(self, args):
        """Main entry point for ACS CLI"""
        if len(args) < 1:
            self._print_help()
            return

        command = args[0]

        if command == "run":
            self._command_run(args[1:])
        elif command == "step":
            self._command_step(args[1:])
        elif command == "state":
            self._command_state(args[1:])
        elif command == "reset":
            self._command_reset(args[1:])
        elif command == "load-rom":
            self._command_load_rom(args[1:])
        elif command == "load-disk":
            self._command_load_disk(args[1:])
        elif command == "debug":
            self._command_debug(args[1:])
        elif command == "mcp":
            self._command_mcp(args[1:])
        elif command == "info":
            self._command_info(args[1:])
        elif command == "save-state":
            self._command_save_state(args[1:])
        elif command == "load-state":
            self._command_load_state(args[1:])
        elif command == "key":
            self._command_key(args[1:])
        elif command == "type":
            self._command_type(args[1:])
        elif command == "export":
            self._command_export(args[1:])
        elif command == "help" or command == "--help" or command == "-h":
            self._print_help()
        else:
            print(f"Unknown command: {command}")
            self._print_help()

    def _print_help(self):
        """Print help message"""
        print(__doc__)

    # ── Run ─────────────────────────────────────────────────────────

    def _command_run(self, args):
        """Run the emulator.

        Usage: ucode acs run [OPTIONS]

        Options:
          --max-instructions N    Maximum instructions to execute (0 = unlimited)
          --frequency HZ          CPU frequency in Hz (default: 1000000)
          --trace                 Enable execution tracing
          --log-memory            Enable memory access logging
        """
        parser = argparse.ArgumentParser(description="Run the ACS emulator")
        parser.add_argument("--max-instructions", type=int, default=0,
                          help="Maximum instructions (0 = unlimited)")
        parser.add_argument("--frequency", type=int, default=1_000_000,
                          help="CPU frequency in Hz")
        parser.add_argument("--trace", action="store_true",
                          help="Enable execution tracing")
        parser.add_argument("--log-memory", action="store_true",
                          help="Enable memory access logging")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        # Update config
        self.emulator.config.max_instructions = parsed.max_instructions
        self.emulator.config.cpu_frequency = parsed.frequency
        self.emulator.config.trace_enabled = parsed.trace
        self.emulator.config.log_memory = parsed.log_memory

        if parsed.trace:
            self.emulator.debugger.enable_tracing()
        if parsed.log_memory:
            self.emulator.memory.enable_logging()

        print(f"🚀 Running ACS emulator...")
        print(f"   CPU: {parsed.frequency} Hz")
        print(f"   Max instructions: {parsed.max_instructions or 'unlimited'}")
        print(f"   Trace: {'on' if parsed.trace else 'off'}")
        print(f"   Press Ctrl+C to stop\n")

        try:
            start = time.time()
            executed = self.emulator.run(parsed.max_instructions)
            elapsed = time.time() - start
            ips = executed / elapsed if elapsed > 0 else 0

            print(f"\n✅ Execution complete")
            print(f"   Instructions: {executed}")
            print(f"   Elapsed: {elapsed:.2f}s")
            print(f"   IPS: {ips:.0f}")
        except KeyboardInterrupt:
            print(f"\n⏹️  Execution stopped")
            print(f"   Instructions: {self.emulator.instruction_count}")
        except Exception as e:
            print(f"❌ Execution error: {e}")

    # ── Step ────────────────────────────────────────────────────────

    def _command_step(self, args):
        """Single-step through execution.

        Usage: ucode acs step [OPTIONS]

        Options:
          --count N    Number of steps to execute (default: 1)
        """
        parser = argparse.ArgumentParser(description="Single-step through execution")
        parser.add_argument("--count", type=int, default=1,
                          help="Number of steps (default: 1)")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        for i in range(parsed.count):
            state = self.emulator.step()
            self._print_cpu_state(state)
            if i < parsed.count - 1:
                print()

        print(f"\n✅ Stepped {parsed.count} instruction(s)")

    # ── State ───────────────────────────────────────────────────────

    def _command_state(self, args):
        """Show current emulator state.

        Usage: ucode acs state [OPTIONS]

        Options:
          --json    Output as JSON
        """
        parser = argparse.ArgumentParser(description="Show emulator state")
        parser.add_argument("--json", action="store_true",
                          help="Output as JSON")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        state = self.emulator.get_cpu_state()
        info = self.emulator.get_info()

        if parsed.json:
            print(json.dumps({"cpu": state, "info": info}, indent=2))
            return

        print("CPU State:")
        self._print_cpu_state(state)
        print()
        print(f"Running: {info['running']}")
        print(f"Paused: {info['paused']}")
        print(f"Instructions: {info['instructions']}")
        print(f"Elapsed: {info['elapsed']:.2f}s")
        print(f"IPS: {info['ips']:.0f}")

    def _print_cpu_state(self, state: Dict[str, Any]):
        """Print CPU register state."""
        flags = state.get("flags", {})
        print(f"  PC=0x{state.get('pc', 0):04X}  SP=0x{state.get('sp', 0):04X}")
        print(f"  A=0x{state.get('a', 0):02X}  X=0x{state.get('x', 0):02X}  Y=0x{state.get('y', 0):02X}")
        print(f"  Flags: {' '.join(f'{k}={v}' for k, v in flags.items())}")
        print(f"  Cycles: {state.get('cycles', 0)}")

    # ── Reset ───────────────────────────────────────────────────────

    def _command_reset(self, args):
        """Reset the emulator.

        Usage: ucode acs reset
        """
        self.emulator.reset()
        print("✅ Emulator reset")

    # ── Load ROM ────────────────────────────────────────────────────

    def _command_load_rom(self, args):
        """Load a ROM file.

        Usage: ucode acs load-rom [OPTIONS] FILE

        Options:
          --offset ADDR    Memory offset to load at (default: 0x8000)
        """
        parser = argparse.ArgumentParser(description="Load a ROM file")
        parser.add_argument("file", help="Path to ROM file")
        parser.add_argument("--offset", type=lambda x: int(x, 0), default=0x8000,
                          help="Memory offset (default: 0x8000)")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        path = Path(parsed.file)
        if not path.exists():
            print(f"❌ ROM file not found: {parsed.file}")
            return

        try:
            bytes_loaded = self.emulator.load_rom_from_file(str(path), parsed.offset)
            print(f"✅ Loaded {bytes_loaded} bytes from {parsed.file}")
            print(f"   Offset: 0x{parsed.offset:04X}")
        except Exception as e:
            print(f"❌ Error loading ROM: {e}")

    # ── Load Disk ───────────────────────────────────────────────────

    def _command_load_disk(self, args):
        """Load a disk image.

        Usage: ucode acs load-disk [OPTIONS] FILE

        Options:
          --format FORMAT    Disk format: dos33, raw, nib (default: dos33)
        """
        parser = argparse.ArgumentParser(description="Load a disk image")
        parser.add_argument("file", help="Path to .dsk file")
        parser.add_argument("--format", choices=["dos33", "raw", "nib"],
                          default="dos33", help="Disk format (default: dos33)")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        path = Path(parsed.file)
        if not path.exists():
            print(f"❌ Disk image not found: {parsed.file}")
            return

        try:
            bytes_loaded = self.emulator.load_disk(str(path))
            print(f"✅ Loaded disk image: {parsed.file}")
            print(f"   Format: {parsed.format}")
            print(f"   Bytes: {bytes_loaded}")
        except Exception as e:
            print(f"❌ Error loading disk: {e}")

    # ── Debug ───────────────────────────────────────────────────────

    def _command_debug(self, args):
        """Start interactive debugger.

        Usage: ucode acs debug [OPTIONS]

        Options:
          --breakpoint ADDR    Set breakpoint at address (can be repeated)
        """
        parser = argparse.ArgumentParser(description="Start interactive debugger")
        parser.add_argument("--breakpoint", "-b", type=lambda x: int(x, 0),
                          action="append", default=[],
                          help="Set breakpoint at address")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        # Set breakpoints
        for addr in parsed.breakpoint:
            self.emulator.debugger.set_breakpoint(addr, f"CLI breakpoint @ 0x{addr:04X}")
            print(f"🔴 Breakpoint set at 0x{addr:04X}")

        print("\n🔧 ACS Debugger (interactive)")
        print("   Commands: step, continue, state, break <addr>, clear, quit")
        print()

        while True:
            try:
                cmd = input("(acs) ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not cmd:
                continue

            parts = cmd.split()
            action = parts[0].lower()

            if action in ("q", "quit", "exit"):
                print("Exiting debugger")
                break

            elif action in ("s", "step"):
                state = self.emulator.step()
                self._print_cpu_state(state)

            elif action in ("c", "cont", "continue"):
                self.emulator.debugger.continue_execution()
                print("Continuing execution...")
                try:
                    self.emulator.run(max_instructions=1000)
                except KeyboardInterrupt:
                    print("\nExecution paused")

            elif action in ("st", "state"):
                state = self.emulator.get_cpu_state()
                self._print_cpu_state(state)

            elif action in ("b", "break", "breakpoint"):
                if len(parts) < 2:
                    print("Usage: break <address>")
                    continue
                try:
                    addr = int(parts[1], 0)
                    self.emulator.debugger.set_breakpoint(addr, f"BP @ 0x{addr:04X}")
                    print(f"🔴 Breakpoint set at 0x{addr:04X}")
                except ValueError:
                    print(f"Invalid address: {parts[1]}")

            elif action in ("cl", "clear"):
                self.emulator.debugger.clear_breakpoints()
                print("✅ All breakpoints cleared")

            elif action in ("bp", "breakpoints"):
                bps = self.emulator.debugger.get_breakpoints()
                if not bps:
                    print("No breakpoints set")
                else:
                    print("Breakpoints:")
                    for addr, bp in bps.items():
                        print(f"  0x{addr:04X}: {bp.description} (hits: {bp.hit_count})")

            elif action in ("r", "reset"):
                self.emulator.reset()
                print("✅ Emulator reset")

            elif action in ("h", "help"):
                print("Commands:")
                print("  s, step          Step one instruction")
                print("  c, continue      Continue execution")
                print("  st, state        Show CPU state")
                print("  b, break <addr>  Set breakpoint")
                print("  cl, clear        Clear all breakpoints")
                print("  bp, breakpoints  List breakpoints")
                print("  r, reset         Reset emulator")
                print("  q, quit          Exit debugger")

            else:
                print(f"Unknown command: {action}")

    # ── MCP ─────────────────────────────────────────────────────────

    def _command_mcp(self, args):
        """Send MCP commands to the emulator.

        Usage: ucode acs mcp <subcommand> [OPTIONS]

        Subcommands:
          send COMMAND [ARGS]    Send an MCP command
          status                 Show MCP state
          history                Show command history
          clear                  Clear pending commands

        Commands:
          PAUSE       Pause execution
          RESUME      Resume execution
          SAVE        Save state
          RESTORE     Restore state
          INSPECT var Inspect a variable
          EVAL expr   Evaluate an expression
          QUIT        Quit the emulator
          STEP        Single step
          RESET       Reset the emulator
          STATE       Show CPU state
        """
        if len(args) < 1:
            print("Usage: ucode acs mcp <subcommand> [OPTIONS]")
            print("Subcommands: send, status, history, clear")
            return

        from core_py.bbc.mcp_bridge import create_mcp_bridge
        mcp = create_mcp_bridge()

        subcommand = args[0]
        sub_args = args[1:]

        if subcommand == "send":
            if len(sub_args) < 1:
                print("Usage: ucode acs mcp send COMMAND [ARGS]")
                print("Commands: PAUSE, RESUME, SAVE, RESTORE, INSPECT, EVAL, QUIT, STEP, RESET, STATE")
                return
            cmd_str = " ".join(sub_args)
            cmd = mcp.queue_command(cmd_str, source="cli")
            response = mcp.process_command(cmd)
            if response:
                print(f"✅ {response}")
            else:
                print(f"✅ Command queued: {cmd_str}")

        elif subcommand == "status":
            state = mcp.get_state() if hasattr(mcp, 'get_state') else {}
            print("MCP State:")
            print(f"  Enabled: {mcp._enabled}")
            print(f"  Pending commands: {len(mcp._pending_commands)}")
            print(f"  Pending responses: {len(mcp._responses)}")

        elif subcommand == "history":
            print("Command history not available in basic mode")

        elif subcommand == "clear":
            mcp.clear_commands()
            mcp.clear_responses()
            print("✅ Cleared pending commands and responses")

        else:
            print(f"Unknown mcp subcommand: {subcommand}")

    # ── Info ────────────────────────────────────────────────────────

    def _command_info(self, args):
        """Show emulator information.

        Usage: ucode acs info [OPTIONS]

        Options:
          --json    Output as JSON
        """
        parser = argparse.ArgumentParser(description="Show emulator info")
        parser.add_argument("--json", action="store_true",
                          help="Output as JSON")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        info = self.emulator.get_info()

        if parsed.json:
            print(json.dumps(info, indent=2))
            return

        print("ACS Emulator Info:")
        print(f"  Running: {info['running']}")
        print(f"  Paused: {info['paused']}")
        print(f"  Instructions: {info['instructions']}")
        print(f"  Elapsed: {info['elapsed']:.2f}s")
        print(f"  IPS: {info['ips']:.0f}")
        print(f"  CPU: PC=0x{info['cpu']['pc']:04X}")
        print(f"  Disk loaded: {info['disk'] is not None}")
        print(f"  Debugger: {info['debugger']}")

    # ── Save/Load State ─────────────────────────────────────────────

    def _command_save_state(self, args):
        """Save emulator state to file.

        Usage: ucode acs save-state [OPTIONS] FILE
        """
        parser = argparse.ArgumentParser(description="Save emulator state")
        parser.add_argument("file", help="Output file path")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        state = self.emulator.save_state()
        try:
            with open(parsed.file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            print(f"✅ State saved to: {parsed.file}")
        except Exception as e:
            print(f"❌ Error saving state: {e}")

    def _command_load_state(self, args):
        """Load emulator state from file.

        Usage: ucode acs load-state [OPTIONS] FILE
        """
        parser = argparse.ArgumentParser(description="Load emulator state")
        parser.add_argument("file", help="Input file path")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        path = Path(parsed.file)
        if not path.exists():
            print(f"❌ State file not found: {parsed.file}")
            return

        try:
            with open(path, 'r') as f:
                state = json.load(f)
            self.emulator.restore_state(state)
            print(f"✅ State loaded from: {parsed.file}")
        except Exception as e:
            print(f"❌ Error loading state: {e}")

    # ── Key / Type ──────────────────────────────────────────────────

    def _command_key(self, args):
        """Send a key press to the emulator.

        Usage: ucode acs key [OPTIONS] KEYCODE

        Options:
          --char    Interpret argument as a character instead of keycode
        """
        parser = argparse.ArgumentParser(description="Send a key press")
        parser.add_argument("key", help="Key code (numeric) or character (with --char)")
        parser.add_argument("--char", action="store_true",
                          help="Interpret as character")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        if parsed.char:
            key = ord(parsed.key.upper())
        else:
            try:
                key = int(parsed.key, 0)
            except ValueError:
                print(f"❌ Invalid key code: {parsed.key}")
                return

        self.emulator.io.key_press(key)
        char = chr(key) if 32 <= key <= 126 else f"0x{key:02X}"
        print(f"✅ Key pressed: {char}")

    def _command_type(self, args):
        """Type text into the emulator.

        Usage: ucode acs type [OPTIONS] TEXT
        """
        parser = argparse.ArgumentParser(description="Type text into emulator")
        parser.add_argument("text", nargs="+", help="Text to type")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        text = " ".join(parsed.text)
        self.emulator.io.type_string(text)
        print(f"✅ Typed: {text}")

    # ── Export ──────────────────────────────────────────────────────

    def _command_export(self, args):
        """Export display to HTML, ANSI, or JSON.

        Usage: ucode acs export [OPTIONS]

        Options:
          --format FORMAT    Export format: html, ansi, json (default: html)
          --output FILE      Output file path (default: stdout)
        """
        parser = argparse.ArgumentParser(description="Export display")
        parser.add_argument("--format", choices=["html", "ansi", "json"],
                          default="html", help="Export format (default: html)")
        parser.add_argument("--output", help="Output file path")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        display_text = self.emulator.io.get_display_text()

        if parsed.format == "json":
            output = json.dumps({
                "display": display_text,
                "mode": self.emulator.io.display.mode.name,
                "cpu": self.emulator.get_cpu_state(),
            }, indent=2)
        elif parsed.format == "ansi":
            # Simple ANSI rendering
            output = display_text
        else:
            # HTML
            escaped = display_text.replace("&", "&").replace("<", "<").replace(">", ">")
            output = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ACS Display</title>
    <style>
        body {{ background: #000; color: #0f0; font-family: monospace; padding: 2rem; }}
        pre {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <pre>{escaped}</pre>
</body>
</html>"""

        if parsed.output:
            try:
                Path(parsed.output).write_text(output, encoding="utf-8")
                print(f"✅ Exported to: {parsed.output}")
            except Exception as e:
                print(f"❌ Error writing output: {e}")
        else:
            print(output)


def main():
    """Main entry point for ACS CLI"""
    cli = ACS_CLI()
    cli.main(sys.argv[1:])


if __name__ == "__main__":
    main()
