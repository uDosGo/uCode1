"""
Matrix Brandy Integration for uCode1 BBC BASIC

This module provides integration with Matrix Brandy, a C-based BBC BASIC
interpreter that offers full compatibility with BBC BASIC V.

Matrix Brandy is available at: https://brandy.morningstar.uk/

This module allows uCode1 to use Brandy as the actual interpreter backend
while providing a Python interface.
"""

import os
import sys
import subprocess
import tempfile
import ctypes
import platform
from typing import Optional, Any, List, Dict
from pathlib import Path

try:
    from .vdu import VDUDriver, VDUHandler
    from .memory import BBCMemory
except ImportError:
    VDUDriver = None
    VDUHandler = None
    BBCMemory = None


class BrandyBridge:
    """
    Bridge to Matrix Brandy interpreter.
    
    This class manages communication with the Brandy interpreter,
    either through subprocess execution or through C API binding
    if Brandy is compiled as a shared library.
    """
    
    def __init__(self, brandy_path: Optional[str] = None):
        """
        Initialize Brandy bridge.
        
        Args:
            brandy_path: Path to brandy executable or shared library.
                        If None, will attempt to find brandy automatically.
        """
        self.brandy_path = brandy_path or self._find_brandy()
        self.use_subprocess = True
        self.use_c_api = False
        self._temp_files = []
        
        # Initialize the interpreter
        self._initialize()
    
    def _find_brandy(self) -> Optional[str]:
        """Attempt to find brandy executable"""
        # Common locations
        search_paths = [
            'brandy',
            '/usr/local/bin/brandy',
            '/usr/bin/brandy',
            '/opt/brandy/bin/brandy',
            os.path.expanduser('~/bin/brandy'),
            os.path.expanduser('~/local/bin/brandy'),
        ]
        
        for path in search_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        # Check Windows
        if platform.system() == 'Windows':
            windows_paths = [
                'brandy.exe',
                'C:\\brandy\\brandy.exe',
                'C:\\Program Files\\Brandy\\brandy.exe',
            ]
            for path in windows_paths:
                if os.path.exists(path):
                    return path
        
        return None
    
    def _initialize(self):
        """Initialize the Brandy interpreter"""
        if not self.brandy_path:
            raise FileNotFoundError(
                "Matrix Brandy interpreter not found. "
                "Please install Brandy from https://brandy.morningstar.uk/ "
                "or specify its path."
            )
        
        # Check if it's a shared library
        lib_extensions = {'.so': '.so', '.dll': '.dll', '.dylib': '.dylib'}
        if any(self.brandy_path.endswith(ext) for ext in lib_extensions.values()):
            try:
                self._c_lib = ctypes.CDLL(self.brandy_path)
                self.use_c_api = True
                self.use_subprocess = False
                self._setup_c_api()
            except OSError:
                self.use_c_api = False
    
    def _setup_c_api(self):
        """Setup C API bindings"""
        # Define function prototypes
        pass
    
    def execute(self, code: str, vdu_handler: Optional['VDUHandler'] = None) -> str:
        """
        Execute BBC BASIC code and return output.
        
        Args:
            code: BBC BASIC program to execute
            vdu_handler: Optional VDU handler for output
            
        Returns:
            Text output from the program
        """
        if self.use_c_api:
            return self._execute_c_api(code, vdu_handler)
        else:
            return self._execute_subprocess(code, vdu_handler)
    
    def _execute_c_api(self, code: str, vdu_handler: Optional['VDUHandler'] = None) -> str:
        """Execute using C API (not fully implemented)"""
        raise NotImplementedError("C API execution not yet implemented")
    
    def _execute_subprocess(self, code: str, vdu_handler: Optional['VDUHandler'] = None) -> str:
        """Execute using subprocess"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bbc', delete=False) as f:
            f.write(code)
            temp_file = f.name
            self._temp_files.append(temp_file)
        
        try:
            # Run brandy
            result = subprocess.run(
                [self.brandy_path, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout + result.stderr
            
            # Clean up VDU handling would go here
            if vdu_handler:
                pass  # VDU output would be processed
            
            return output
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
                self._temp_files.remove(temp_file)
            except:
                pass
    
    def run_interactive(self, vdu_handler: Optional['VDUHandler'] = None):
        """Run Brandy in interactive mode"""
        if self.use_c_api:
            raise NotImplementedError("Interactive mode with C API not yet implemented")
        
        # Run brandy interactively
        env = os.environ.copy()
        process = subprocess.Popen(
            [self.brandy_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Would need to proxy I/O through VDU handler
        return process
    
    def compile(self, source_file: str, output_file: str) -> bool:
        """Compile BBC BASIC to Brandy bytecode (if supported)"""
        raise NotImplementedError("Compilation not supported")
    
    def cleanup(self):
        """Clean up temporary files"""
        for temp_file in self._temp_files[:]:
            try:
                os.unlink(temp_file)
                self._temp_files.remove(temp_file)
            except:
                pass
    
    def __del__(self):
        self.cleanup()


class BrandyInterpreter:
    """
    High-level wrapper around Brandy Bridge that provides
    a Python interface similar to BBCBasicInterpreter.
    """
    
    def __init__(self, brandy_path: Optional[str] = None):
        self.bridge = BrandyBridge(brandy_path)
        self.vdu_handler = None
        self.state_dict = {
            'variables': {},
            'arrays': {},
            'functions': {},
            'program': [],
            'line_numbers': [],
            'screen_mode': 7,
            'fg_color': 7,
            'bg_color': 0,
        }
    
    def set_vdu_handler(self, vdu_handler: 'VDUHandler'):
        """Set VDU handler for output"""
        self.vdu_handler = vdu_handler
    
    def run(self, code: str) -> str:
        """Run BBC BASIC code"""
        return self.bridge.execute(code, self.vdu_handler)
    
    def run_file(self, filename: str) -> str:
        """Run BBC BASIC file"""
        with open(filename, 'r') as f:
            code = f.read()
        return self.run(code)
    
    def set_variable(self, name: str, value: Any):
        """Set a variable value (limited support)"""
        self.state_dict['variables'][name] = value
    
    def get_variable(self, name: str) -> Any:
        """Get a variable value (limited support)"""
        return self.state_dict['variables'].get(name, 0)
    
    def reset(self):
        """Reset interpreter state"""
        self.state_dict = {
            'variables': {},
            'arrays': {},
            'functions': {},
            'program': [],
            'line_numbers': [],
            'screen_mode': 7,
            'fg_color': 7,
            'bg_color': 0,
        }
    
    def __del__(self):
        self.bridge.cleanup()


def get_brandy_available() -> bool:
    """Check if Matrix Brandy is available on the system"""
    try:
        bridge = BrandyBridge()
        return True
    except FileNotFoundError:
        return False


def create_brandy_interpreter(vdu_handler=None) -> Optional[BrandyInterpreter]:
    """Create a Brandy interpreter if available"""
    try:
        interpreter = BrandyInterpreter()
        if vdu_handler:
            interpreter.set_vdu_handler(vdu_handler)
        return interpreter
    except FileNotFoundError:
        return None
