#!/usr/bin/env python3
"""
Snack execution engine - Python Implementation

This module provides the core functionality for executing Snacks,
which are atomic executable units in the uDos ecosystem.
"""

import subprocess
import json
import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
import tempfile
import shlex

from .models import Snack, SnackInput, SnackOutput
from .validator import validate_snack


class SnackExecutionError(Exception):
    """Exception raised when Snack execution fails"""
    def __init__(self, message: str, exit_code: Optional[int] = None):
        super().__init__(message)
        self.exit_code = exit_code


class SnackEngine:
    """Engine for executing Snacks"""
    
    def __init__(self, working_dir: Optional[str] = None):
        """Initialize the Snack engine"""
        self.working_dir = working_dir or os.getcwd()
        
    def execute(self, snack: Snack, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a Snack and return the results"""
        # Validate the snack before execution
        validate_snack(snack)
        
        # Prepare inputs
        input_values = self._prepare_inputs(snack, inputs or {})
        
        # Execute based on runtime
        if snack.runtime == "bash":
            return self._execute_bash(snack, input_values)
        elif snack.runtime == "python":
            return self._execute_python(snack, input_values)
        elif snack.runtime == "node":
            return self._execute_node(snack, input_values)
        elif snack.runtime == "apple-script-osx":
            return self._execute_applescript(snack, input_values)
        else:
            raise SnackExecutionError(f"Unsupported runtime: {snack.runtime}")
    
    def _prepare_inputs(self, snack: Snack, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and validate inputs for execution"""
        prepared_inputs = {}
        
        # Check required inputs
        for input_spec in snack.inputs:
            if input_spec.required and input_spec.name not in inputs:
                raise SnackExecutionError(f"Missing required input: {input_spec.name}")
            
            # Use provided value or default
            value = inputs.get(input_spec.name, input_spec.default)
            prepared_inputs[input_spec.name] = value
        
        return prepared_inputs
    
    def _execute_bash(self, snack: Snack, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a bash Snack"""
        # Create environment variables from inputs
        env = os.environ.copy()
        for name, value in inputs.items():
            # Convert to string and escape properly
            if isinstance(value, (dict, list)):
                env[name] = json.dumps(value)
            else:
                env[name] = str(value)
        
        try:
            # Execute the bash command
            result = subprocess.run(
                shlex.split(snack.code),
                cwd=self.working_dir,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'exit_code': 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'outputs': self._parse_outputs(snack, result.stdout)
            }
        except subprocess.CalledProcessError as e:
            raise SnackExecutionError(
                f"Bash execution failed: {e.stderr}",
                exit_code=e.returncode
            )
    
    def _execute_python(self, snack: Snack, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Python Snack"""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write the Python code
            f.write(snack.code)
            temp_file = f.name
        
        try:
            # Prepare command
            cmd = [sys.executable, temp_file]
            
            # Add inputs as environment variables
            env = os.environ.copy()
            for name, value in inputs.items():
                if isinstance(value, (dict, list)):
                    env[name] = json.dumps(value)
                else:
                    env[name] = str(value)
            
            # Execute
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'exit_code': 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'outputs': self._parse_outputs(snack, result.stdout)
            }
        except subprocess.CalledProcessError as e:
            raise SnackExecutionError(
                f"Python execution failed: {e.stderr}",
                exit_code=e.returncode
            )
        finally:
            # Clean up temporary file
            os.unlink(temp_file)
    
    def _execute_node(self, snack: Snack, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Node.js Snack"""
        # Create a temporary JavaScript file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            # Write the JavaScript code
            f.write(snack.code)
            temp_file = f.name
        
        try:
            # Prepare command
            cmd = ['node', temp_file]
            
            # Add inputs as environment variables
            env = os.environ.copy()
            for name, value in inputs.items():
                if isinstance(value, (dict, list)):
                    env[name] = json.dumps(value)
                else:
                    env[name] = str(value)
            
            # Execute
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'exit_code': 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'outputs': self._parse_outputs(snack, result.stdout)
            }
        except subprocess.CalledProcessError as e:
            raise SnackExecutionError(
                f"Node.js execution failed: {e.stderr}",
                exit_code=e.returncode
            )
        finally:
            # Clean up temporary file
            os.unlink(temp_file)
    
    def _execute_applescript(self, snack: Snack, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an AppleScript Snack"""
        # Create a temporary AppleScript file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scpt', delete=False) as f:
            # Write the AppleScript code
            f.write(snack.code)
            temp_file = f.name
        
        try:
            # Prepare command
            cmd = ['osascript', temp_file]
            
            # Add inputs as environment variables
            env = os.environ.copy()
            for name, value in inputs.items():
                if isinstance(value, (dict, list)):
                    env[name] = json.dumps(value)
                else:
                    env[name] = str(value)
            
            # Execute
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'exit_code': 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'outputs': self._parse_outputs(snack, result.stdout)
            }
        except subprocess.CalledProcessError as e:
            raise SnackExecutionError(
                f"AppleScript execution failed: {e.stderr}",
                exit_code=e.returncode
            )
        finally:
            # Clean up temporary file
            os.unlink(temp_file)
    
    def _parse_outputs(self, snack: Snack, stdout: str) -> Dict[str, Any]:
        """Parse outputs from execution result"""
        outputs = {}
        
        # Try to parse as JSON first
        try:
            parsed = json.loads(stdout.strip())
            if isinstance(parsed, dict):
                # Map to expected outputs
                for output_spec in snack.outputs:
                    if output_spec.name in parsed:
                        outputs[output_spec.name] = parsed[output_spec.name]
            return outputs
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback: simple text output
        if len(snack.outputs) == 1:
            outputs[snack.outputs[0].name] = stdout.strip()
        
        return outputs


def execute_snack(snack: Snack, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to execute a Snack"""
    engine = SnackEngine()
    return engine.execute(snack, inputs)


# Test the execution engine
if __name__ == "__main__":
    print("Testing Snack Execution Engine...")
    
    # Test bash snack
    try:
        bash_snack = Snack.create(
            "TEST-BASH-001",
            "Test Bash Snack",
            "1.0.0",
            'echo "Hello from bash: $NAME"'
        )
        bash_snack.runtime = "bash"
        bash_snack.inputs = [SnackInput(name="NAME", type="string", required=True)]
        bash_snack.outputs = [SnackOutput(name="message", type="string")]
        
        result = execute_snack(bash_snack, {"NAME": "World"})
        print(f"✓ Bash execution result: {result}")
    except Exception as e:
        print(f"✗ Bash execution failed: {e}")
    
    # Test Python snack
    try:
        python_snack = Snack.create(
            "TEST-PY-001",
            "Test Python Snack",
            "1.0.0",
            'import os\nprint("Hello from Python:", os.environ.get("NAME", "Unknown"))'
        )
        python_snack.runtime = "python"
        python_snack.inputs = [SnackInput(name="NAME", type="string", required=True)]
        python_snack.outputs = [SnackOutput(name="message", type="string")]
        
        result = execute_snack(python_snack, {"NAME": "Pythonista"})
        print(f"✓ Python execution result: {result}")
    except Exception as e:
        print(f"✗ Python execution failed: {e}")
    
    print("Snack execution engine tests completed!")