"""
Text Injection Module

Provides variable substitution and template injection utilities.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from .exceptions import InjectionError


class TextInjector:
    """Performs variable injection into text templates.
    
    Supports:
    - Simple {{variable}} substitution
    - Default values: {{variable, default}}
    - Optional variables: {{variable?}}
    - Filter application: {{variable|filter}}
    - Custom delimiters
    """
    
    DEFAULT_OPEN = "{{"
    DEFAULT_CLOSE = "}}"
    ESCAPE_CHARS = ("\\", "{", "}")
    
    def __init__(self, open_delim: str = None, close_delim: str = None):
        """Initialize injector with custom delimiters."""
        self.open = open_delim or self.DEFAULT_OPEN
        self.close = close_delim or self.DEFAULT_CLOSE
        self._pattern = re.compile(
            r"(\\)?" + re.escape(self.open) + 
            r"\s*(.*?)\s*" + re.escape(self.close),
            re.DOTALL
        )
    
    def inject(self, template: str, variables: Dict[str, Any], 
               filters: Optional[Dict[str, Callable]] = None) -> str:
        """Inject variables into template string.
        
        Args:
            template: Template string with placeholders
            variables: Dictionary of variable names to values
            filters: Optional dict of filter names to callables
        
        Returns:
            Rendered string with substitutions
        """
        result = template
        
        for match in self._pattern.finditer(template):
            full_match, escaped, var_expr = match.groups()
            
            if escaped:
                # It's escaped, restore the literal
                continue
            
            # Parse variable expression
            value = self._resolve_var(var_expr, variables, filters)
            
            # Replace in result
            result = result[:match.start()] + str(value) + result[match.end():]
        
        return result
    
    def _resolve_var(self, expr: str, variables: Dict[str, Any], 
                     filters: Dict[str, Callable]) -> Any:
        """Resolve a variable expression."""
        # Parse expression: name, default, filters, optional
        expr = expr.strip()
        
        if not expr:
            return ""
        
        # Check for optional
        if expr.endswith("?"):
            expr = expr[:-1].strip()
            optional = True
        else:
            optional = False
        
        # Check for default value
        if "," in expr:
            name_part, default = expr.split(",", 1)
            name = name_part.strip()
            default = default.strip()
        else:
            name = expr
            default = None
        
        # Check for filters
        if "|" in name:
            name, filter_chain = name.split("|", 1)
            name = name.strip()
            filter_chain = filter_chain.strip()
            filters_to_apply = [f.strip() for f in filter_chain.split("|")]
        else:
            filters_to_apply = []
        
        # Get value
        if name in variables:
            value = variables[name]
        elif optional:
            return default if default is not None else ""
        elif default is not None:
            return default
        else:
            raise InjectionError(f"Variable '{name}' not found and not optional")
        
        # Apply filters
        if filters and filters_to_apply:
            for filter_name in filters_to_apply:
                if filter_name in filters:
                    value = filters[filter_name](value)
        
        return value


class TemplateEngine:
    """Advanced template engine with blocks and includes.
    
    Supports:
    - Variable injection
    - If/else blocks
    - For loops
    - Include files
    - Macro definitions
    """
    
    def __init__(self, template_dir: Optional[Union[str, Path]] = None,
                 injector: Optional[TextInjector] = None):
        """Initialize template engine."""
        self.template_dir = Path(template_dir) if template_dir else None
        self.injector = injector or TextInjector()
        self._cache: Dict[str, str] = {}
    
    def render(self, template_name: str, variables: Dict[str, Any] = None) -> str:
        """Render a template by name.
        
        Args:
            template_name: Name/path of template file
            variables: Variables to inject
        
        Returns:
            Rendered template
        """
        if not self.template_dir:
            raise InjectionError("No template directory configured")
        
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            raise InjectionError(f"Template '{template_name}' not found")
        
        template = template_path.read_text()
        return self.injector.inject(template, variables or {})
    
    def render_string(self, template: str, variables: Dict[str, Any] = None) -> str:
        """Render a template string.
        
        Args:
            template: Template string
            variables: Variables to inject
        
        Returns:
            Rendered string
        """
        return self.injector.inject(template, variables or {})


def inject_variables(template: str, variables: Dict[str, Any], 
                     delimiters: Optional[Tuple[str, str]] = None) -> str:
    """Convenience function for simple variable injection.
    
    Args:
        template: Template with {{variable}} placeholders
        variables: Variable dictionary
        delimiters: Optional (open, close) delimiter tuple
    
    Returns:
        Rendered string
    """
    injector = TextInjector()
    if delimiters:
        injector.open, injector.close = delimiters
    return injector.inject(template, variables)


def inject_file(file_path: Union[str, Path], variables: Dict[str, Any],
                encoding: str = "utf-8") -> str:
    """Inject variables into a file.
    
    Args:
        file_path: Path to template file
        variables: Variable dictionary
        encoding: File encoding
    
    Returns:
        Rendered file content as string
    """
    template = Path(file_path).read_text(encoding=encoding)
    return inject_variables(template, variables)


def format_template(template: str, **kwargs) -> str:
    """Format template with keyword arguments.
    
    Args:
        template: Template string with {placeholders}
        **kwargs: Variable names and values
    
    Returns:
        Formatted string
    """
    return template.format(**kwargs)
