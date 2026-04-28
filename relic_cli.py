#!/usr/bin/env python3
"""
uCode1 Relic CLI - Standalone command-line interface for Relic management

This CLI provides full Relic management capabilities without requiring
the complete uCode1 package to be installed.

Usage:
  relic [COMMAND] [OPTIONS]

Commands:
  list        List available relics
  show        Show details of a specific relic
  create      Create a new relic
  validate    Validate a relic file
  unpack      Unpack a relic to directory
  run         Run a relic
  test        Test relic functionality
  help        Show help for a command

Examples:
  relic list
  relic show RELIC_ID
  relic create --id GREET-001 --name "Greeting" --code "print('Hello')"
  relic validate GREET-001.relic
  relic unpack GREET-001.relic --output ./unpacked
"""

import sys
import os
import argparse
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# Add core_py to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from core_py import (
        Relic, RelicMetadata, RelicResource, RelicBinaryFormat, RelicRegistry
    )
    CORE_PY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: core_py not available: {e}")
    print("Relic CLI functionality will be limited.")
    CORE_PY_AVAILABLE = False


class RelicCLI:
    """Command-line interface for Relic management"""
    
    def __init__(self):
        self.registry = RelicRegistry() if CORE_PY_AVAILABLE else None
    
    def main(self, args):
        """Main entry point for relic CLI"""
        if not CORE_PY_AVAILABLE:
            print("Error: core_py module not available. Cannot run Relic CLI.")
            return 1
        
        if len(args) < 1:
            self._print_help()
            return 0
        
        command = args[0]
        
        if command == "list":
            return self._command_list(args[1:])
        elif command == "show":
            return self._command_show(args[1:])
        elif command == "create":
            return self._command_create(args[1:])
        elif command == "validate":
            return self._command_validate(args[1:])
        elif command == "unpack":
            return self._command_unpack(args[1:])
        elif command == "run":
            return self._command_run(args[1:])
        elif command == "test":
            return self._command_test(args[1:])
        elif command == "help" or command == "--help" or command == "-h":
            self._print_help()
            return 0
        else:
            print(f"Unknown command: {command}")
            self._print_help()
            return 1
    
    def _print_help(self):
        """Print help message"""
        print(__doc__)
    
    def _command_list(self, args):
        """List available relics"""
        print("Available Relics:")
        print("-" * 70)
        
        relics = self.registry.list_relics()
        
        if not relics:
            print("No relics found in registry.")
            print(f"Registry location: {self.registry.base_path}")
            return 0
        
        for relic_info in relics:
            if 'error' in relic_info:
                print(f"⚠️  {relic_info['filename']:20} Error: {relic_info['error']}")
            else:
                print(f"{relic_info['filename']:20} {relic_info['id']:15} {relic_info['name']:20} v{relic_info['version']}")
        
        valid_count = sum(1 for r in relics if 'error' not in r)
        print(f"\nTotal: {len(relics)} relics ({valid_count} valid)")
        return 0
    
    def _command_show(self, args):
        """Show details of a specific relic"""
        if len(args) < 1:
            print("Usage: relic show RELIC_FILE.relic")
            return 1
        
        filename = args[0]
        
        try:
            relic = self.registry.load_relic(filename)
            
            print(f"Relic: {relic.metadata.name} ({relic.metadata.id})")
            print(f"Version: {relic.metadata.version}")
            print(f"Runtime: {relic.metadata.runtime}")
            print(f"Description: {relic.metadata.description or 'None'}")
            print(f"Author: {relic.metadata.author or 'None'}")
            print(f"Tags: {', '.join(relic.metadata.tags) if relic.metadata.tags else 'None'}")
            print(f"Dependencies: {', '.join(relic.metadata.dependencies) if relic.metadata.dependencies else 'None'}")
            print(f"Entry Point: {relic.metadata.entry_point or 'None'}")
            print(f"Checksum: {relic.checksum}")
            print(f"Integrity: {'✅ Valid' if relic.verify_integrity() else '❌ Invalid'}")
            print()
            
            if relic.resources:
                print("Resources:")
                for resource in relic.resources:
                    print(f"  {resource.name:15} {resource.type:10} {len(resource.data):8} bytes")
            
            print(f"\nMain Code: {len(relic.main_code)} bytes")
            print("-" * 50)
            
            # Show preview of main code
            preview = relic.main_code[:100]  # First 100 bytes
            try:
                preview_text = preview.decode('utf-8', errors='replace')
                print(f"Preview: {preview_text}")
            except Exception:
                print(f"Preview: {preview.hex()}")
            
            print("-" * 50)
            return 0
        
        except FileNotFoundError:
            print(f"Relic not found: {filename}")
            return 1
        except Exception as e:
            print(f"Error loading relic: {e}")
            return 1
    
    def _command_create(self, args):
        """Create a new relic"""
        parser = argparse.ArgumentParser(description='Create a new relic')
        parser.add_argument('--id', required=True, help='Relic ID')
        parser.add_argument('--name', required=True, help='Relic name')
        parser.add_argument('--version', required=True, help='Relic version')
        parser.add_argument('--runtime', default='python', help='Runtime (python, bash, etc.)')
        parser.add_argument('--code', required=True, help='Main code')
        parser.add_argument('--description', help='Relic description')
        parser.add_argument('--author', help='Author name')
        parser.add_argument('--tag', action='append', help='Add a tag')
        parser.add_argument('--dependency', action='append', help='Add a dependency')
        parser.add_argument('--entry-point', help='Entry point function')
        parser.add_argument('--output', help='Output filename')
        
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return 1
        
        # Create metadata
        metadata = RelicMetadata(
            id=args.id,
            name=args.name,
            version=args.version,
            description=args.description,
            author=args.author,
            tags=args.tag or [],
            dependencies=args.dependency or [],
            runtime=args.runtime,
            entry_point=args.entry_point
        )
        
        # Create relic
        relic = Relic(
            metadata=metadata,
            main_code=args.code.encode('utf-8')
        )
        
        try:
            # Save to registry
            filepath = self.registry.save_relic(relic, args.output)
            print(f"✅ Relic created successfully: {filepath}")
            print(f"ID: {relic.metadata.id}")
            print(f"Name: {relic.metadata.name}")
            print(f"Version: {relic.metadata.version}")
            print(f"Checksum: {relic.checksum}")
            return 0
        except Exception as e:
            print(f"Error creating relic: {e}")
            return 1
    
    def _command_validate(self, args):
        """Validate a relic file"""
        if len(args) < 1:
            print("Usage: relic validate RELIC_FILE.relic")
            return 1
        
        filename = args[0]
        
        try:
            relic = self.registry.load_relic(filename)
            
            if relic.verify_integrity():
                print(f"✅ Relic is valid: {filename}")
                print(f"Checksum: {relic.checksum}")
                return 0
            else:
                print(f"❌ Relic integrity check failed: {filename}")
                return 1
        
        except FileNotFoundError:
            print(f"File not found: {filename}")
            return 1
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return 1
    
    def _command_unpack(self, args):
        """Unpack a relic to directory"""
        parser = argparse.ArgumentParser(description='Unpack a relic')
        parser.add_argument('relic_file', help='Relic file to unpack')
        parser.add_argument('--output', default='./unpacked', help='Output directory')
        
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return 1
        
        try:
            # Load relic
            relic = self.registry.load_relic(args.relic_file)
            
            # Create output directory
            output_dir = Path(args.output)
            output_dir.mkdir(exist_ok=True, parents=True)
            
            # Save metadata
            metadata_file = output_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(relic.to_dict(), f, indent=2)
            
            # Save main code
            main_code_file = output_dir / "main.code"
            with open(main_code_file, 'wb') as f:
                f.write(relic.main_code)
            
            # Save resources
            resources_dir = output_dir / "resources"
            resources_dir.mkdir(exist_ok=True)
            
            for resource in relic.resources:
                resource_file = resources_dir / resource.name
                with open(resource_file, 'wb') as f:
                    f.write(resource.data)
            
            print(f"✅ Relic unpacked successfully to: {output_dir}")
            print(f"Metadata: {metadata_file}")
            print(f"Main Code: {main_code_file}")
            print(f"Resources: {len(relic.resources)} files in {resources_dir}")
            return 0
        
        except Exception as e:
            print(f"❌ Error unpacking relic: {e}")
            return 1
    
    def _command_run(self, args):
        """Run a relic"""
        parser = argparse.ArgumentParser(description='Run a relic')
        parser.add_argument('relic_file', help='Relic file to run')
        parser.add_argument('--input', action='append', help='Input variables (format: NAME=value)')
        
        try:
            args = parser.parse_args(args)
        except SystemExit:
            return 1
        
        try:
            # Load relic
            relic = self.registry.load_relic(args.relic_file)
            
            # Parse inputs
            inputs = {}
            if args.input:
                for input_arg in args.input:
                    if '=' in input_arg:
                        name, value = input_arg.split('=', 1)
                        inputs[name] = value
                    else:
                        print(f"Invalid input format: {input_arg}. Use NAME=value")
                        return 1
            
            # Execute based on runtime
            if relic.metadata.runtime == "python":
                return self._execute_python(relic, inputs)
            elif relic.metadata.runtime == "bash":
                return self._execute_bash(relic, inputs)
            else:
                print(f"Unsupported runtime: {relic.metadata.runtime}")
                return 1
        
        except Exception as e:
            print(f"❌ Error running relic: {e}")
            return 1
    
    def _execute_python(self, relic: Relic, inputs: Dict[str, Any]) -> int:
        """Execute a Python relic"""
        import subprocess
        import sys
        
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write the Python code
            f.write(relic.main_code.decode('utf-8'))
            temp_file = f.name
        
        try:
            # Prepare command
            cmd = [sys.executable, temp_file]
            
            # Add inputs as environment variables
            env = os.environ.copy()
            for name, value in inputs.items():
                env[name] = str(value)
            
            # Execute
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print(f"\nOutput:")
                print(result.stdout)
            if result.stderr:
                print(f"\nErrors:")
                print(result.stderr)
            
            return result.returncode
        
        finally:
            # Clean up temporary file
            os.unlink(temp_file)
    
    def _execute_bash(self, relic: Relic, inputs: Dict[str, Any]) -> int:
        """Execute a Bash relic"""
        import subprocess
        
        try:
            # Create environment variables from inputs
            env = os.environ.copy()
            for name, value in inputs.items():
                env[name] = str(value)
            
            # Execute the bash command
            result = subprocess.run(
                relic.main_code.decode('utf-8'),
                shell=True,
                env=env,
                capture_output=True,
                text=True
            )
            
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print(f"\nOutput:")
                print(result.stdout)
            if result.stderr:
                print(f"\nErrors:")
                print(result.stderr)
            
            return result.returncode
        
        except Exception as e:
            print(f"Error executing bash relic: {e}")
            return 1
    
    def _command_test(self, args):
        """Test relic functionality"""
        print("Testing Relic CLI...")
        
        # Create a test relic
        metadata = RelicMetadata(
            id="TEST-RELIC-001",
            name="Test Relic",
            version="1.0.0",
            runtime="python"
        )
        
        relic = Relic(
            metadata=metadata,
            main_code=b'print("Hello from Relic CLI test!")'
        )
        
        try:
            # Save to registry
            filepath = self.registry.save_relic(relic)
            print(f"✅ Test relic created: {filepath}")
            
            # Load and verify
            loaded_relic = self.registry.load_relic(filepath.name)
            print(f"✅ Test relic loaded: {loaded_relic.metadata.name}")
            print(f"✅ Integrity check: {loaded_relic.verify_integrity()}")
            
            # List relics
            relics = self.registry.list_relics()
            print(f"✅ Registry contains {len(relics)} relics")
            
            return 0
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return 1


def main():
    """Main entry point"""
    cli = RelicCLI()
    try:
        exit_code = cli.main(sys.argv[1:])
        sys.exit(exit_code if exit_code is not None else 0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()