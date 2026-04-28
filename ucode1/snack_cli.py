#!/usr/bin/env python3
"""
uCode1 Snack CLI - Command-line interface for Snack management

Usage:
  ucode1 snack [COMMAND] [OPTIONS]

Commands:
  list        List available snacks
  show        Show details of a specific snack
  create      Create a new snack
  validate    Validate a snack file
  run         Run a snack
  test        Test snack execution
  help        Show help for a command

Examples:
  ucode1 snack list
  ucode1 snack show SNACK_ID
  ucode1 snack run SNACK_FILE.yaml --input NAME=value
  ucode1 snack validate SNACK_FILE.yaml
"""

import sys
import os
import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Add core_py to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core_py import (
    Snack, SnackInput, SnackOutput, SnackEngine, execute_snack,
    validate_snack, validate_snack_file, resolve_snack_dependencies
)
from core_py.snack.validator import SnackExecutionError


class SnackCLI:
    """Command-line interface for Snack management"""
    
    def __init__(self):
        self.engine = SnackEngine()
        self.registry_dir = Path(".snacks")
        
        # Ensure registry directory exists
        self.registry_dir.mkdir(exist_ok=True)
    
    def main(self, args):
        """Main entry point for snack CLI"""
        if len(args) < 2:
            self._print_help()
            return
        
        command = args[1]
        
        if command == "list":
            self._command_list(args[2:])
        elif command == "show":
            self._command_show(args[2:])
        elif command == "create":
            self._command_create(args[2:])
        elif command == "validate":
            self._command_validate(args[2:])
        elif command == "run":
            self._command_run(args[2:])
        elif command == "test":
            self._command_test(args[2:])
        elif command == "help" or command == "--help" or command == "-h":
            self._print_help()
        else:
            print(f"Unknown command: {command}")
            self._print_help()
    
    def _print_help(self):
        """Print help message"""
        print(__doc__)
    
    def _command_list(self, args):
        """List available snacks"""
        print("Available Snacks:")
        print("-" * 50)
        
        # Look for YAML files in registry
        yaml_files = list(self.registry_dir.glob("*.yaml")) + list(self.registry_dir.glob("*.yml"))
        
        if not yaml_files:
            print("No snacks found in registry.")
            print(f"Registry location: {self.registry_dir}")
            return
        
        for yaml_file in sorted(yaml_files):
            try:
                snack = Snack.load_from_file(yaml_file)
                print(f"{snack.id:15} {snack.name:20} v{snack.version}")
            except Exception as e:
                print(f"⚠️  {yaml_file.name:15} Error: {e}")
        
        print(f"\nTotal: {len(yaml_files)} snacks")
    
    def _command_show(self, args):
        """Show details of a specific snack"""
        if len(args) < 1:
            print("Usage: ucode1 snack show SNACK_ID")
            return
        
        snack_id = args[0]
        
        # Look for the snack in registry
        yaml_files = list(self.registry_dir.glob("*.yaml")) + list(self.registry_dir.glob("*.yml"))
        
        found = None
        for yaml_file in yaml_files:
            try:
                snack = Snack.load_from_file(yaml_file)
                if snack.id == snack_id:
                    found = snack
                    break
            except Exception:
                continue
        
        if not found:
            print(f"Snack not found: {snack_id}")
            return
        
        print(f"Snack: {found.name} ({found.id})")
        print(f"Version: {found.version}")
        print(f"Kind: {found.kind}")
        print(f"Runtime: {found.runtime}")
        print(f"Emoji: {found.emoji or 'None'}")
        print(f"Tags: {', '.join(found.tags) if found.tags else 'None'}")
        print(f"Requires: {', '.join(found.requires) if found.requires else 'None'}")
        print()
        
        if found.inputs:
            print("Inputs:")
            for input_spec in found.inputs:
                required = "[required]" if input_spec.required else "[optional]"
                default = f" (default: {input_spec.default})" if input_spec.default else ""
                print(f"  {input_spec.name:15} {input_spec.type:10} {required}{default}")
        
        if found.outputs:
            print("\nOutputs:")
            for output_spec in found.outputs:
                print(f"  {output_spec.name:15} {output_spec.type}")
        
        print(f"\nCode:")
        print("-" * 50)
        print(found.code)
        print("-" * 50)
    
    def _command_create(self, args):
        """Create a new snack"""
        parser = argparse.ArgumentParser(description='Create a new snack')
        parser.add_argument('snack_id', help='Snack ID')
        parser.add_argument('name', help='Snack name')
        parser.add_argument('version', help='Snack version')
        parser.add_argument('--kind', default='script', help='Snack kind')
        parser.add_argument('--runtime', default='bash', help='Runtime (bash, python, node, applescript)')
        parser.add_argument('--code', required=True, help='Snack code')
        parser.add_argument('--emoji', help='Snack emoji')
        parser.add_argument('--tag', action='append', help='Add a tag')
        parser.add_argument('--require', action='append', help='Add a dependency')
        
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        
        # Create the snack
        snack = Snack.create(
            id=args.snack_id,
            name=args.name,
            version=args.version,
            code=args.code
        )
        
        snack.kind = args.kind
        snack.runtime = args.runtime
        
        if args.emoji:
            snack.emoji = args.emoji
        
        if args.tag:
            snack.tags = args.tag
        
        if args.require:
            snack.requires = args.require
        
        # Validate
        try:
            validate_snack(snack)
        except ValueError as e:
            print(f"Validation error: {e}")
            return
        
        # Save to file
        filename = f"{snack.id}.yaml"
        filepath = self.registry_dir / filename
        
        try:
            snack.save_to_file(filepath)
            print(f"✅ Snack created successfully: {filepath}")
            print(f"ID: {snack.id}")
            print(f"Name: {snack.name}")
            print(f"Version: {snack.version}")
        except Exception as e:
            print(f"Error saving snack: {e}")
    
    def _command_validate(self, args):
        """Validate a snack file"""
        if len(args) < 1:
            print("Usage: ucode1 snack validate SNACK_FILE.yaml")
            return
        
        filepath = Path(args[0])
        if not filepath.exists():
            print(f"File not found: {filepath}")
            return
        
        try:
            validate_snack_file(filepath)
            print(f"✅ Snack is valid: {filepath}")
        except ValueError as e:
            print(f"❌ Validation failed: {e}")
        except Exception as e:
            print(f"❌ Error validating snack: {e}")
    
    def _command_run(self, args):
        """Run a snack"""
        parser = argparse.ArgumentParser(description='Run a snack')
        parser.add_argument('snack_file', help='Snack YAML file')
        parser.add_argument('--input', action='append', help='Input variables (format: NAME=value)')
        parser.add_argument('--json', action='store_true', help='Output results as JSON')
        
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return
        
        filepath = Path(args.snack_file)
        if not filepath.exists():
            print(f"File not found: {filepath}")
            return
        
        # Parse inputs
        inputs = {}
        if args.input:
            for input_arg in args.input:
                if '=' in input_arg:
                    name, value = input_arg.split('=', 1)
                    inputs[name] = value
                else:
                    print(f"Invalid input format: {input_arg}. Use NAME=value")
                    return
        
        try:
            # Load and run the snack
            snack = Snack.load_from_file(filepath)
            result = execute_snack(snack, inputs)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"✅ Snack executed successfully: {snack.name}")
                print(f"Exit code: {result['exit_code']}")
                if result['stdout']:
                    print(f"\nOutput:")
                    print(result['stdout'])
                if result['stderr']:
                    print(f"\nErrors:")
                    print(result['stderr'])
                if result['outputs']:
                    print(f"\nParsed outputs:")
                    for name, value in result['outputs'].items():
                        print(f"  {name}: {value}")
        
        except SnackExecutionError as e:
            print(f"❌ Snack execution failed: {e}")
            if hasattr(e, 'exit_code'):
                print(f"Exit code: {e.exit_code}")
        except Exception as e:
            print(f"❌ Error running snack: {e}")
    
    def _command_test(self, args):
        """Test snack functionality"""
        print("Testing Snack CLI...")
        
        # Create a test snack
        test_snack = Snack.create(
            "TEST-CLI-001",
            "Test CLI Snack",
            "1.0.0",
            "echo 'Hello from CLI test'"
        )
        test_snack.runtime = "bash"
        
        try:
            result = execute_snack(test_snack)
            print(f"✅ Test snack executed: {result['exit_code'] == 0}")
            print(f"Output: {result['stdout'].strip()}")
        except Exception as e:
            print(f"❌ Test failed: {e}")


def main():
    """Main entry point"""
    cli = SnackCLI()
    cli.main(sys.argv[1:])  # Skip 'snack' command


if __name__ == '__main__':
    main()