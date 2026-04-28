#!/usr/bin/env python3
"""
Snack exceptions - Centralized exception definitions
"""

class SnackExecutionError(Exception):
    """Exception raised when Snack execution fails"""
    def __init__(self, message: str, exit_code: int = None):
        super().__init__(message)
        self.exit_code = exit_code


class CircularDependencyError(Exception):
    """Exception raised when circular dependencies are detected"""
    pass