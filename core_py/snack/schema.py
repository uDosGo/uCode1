#!/usr/bin/env python3
"""
Snack schema definitions and validation - Python Implementation
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import re


@dataclass
class SnackInputSchema:
    """Input schema for a Snack"""
    name: str
    type: str
    default: Optional[Any] = None
    required: bool = False


@dataclass
class SnackOutputSchema:
    """Output schema for a Snack"""
    name: str
    type: str


@dataclass
class SnackSchema:
    """Snack schema definition"""
    id: str
    name: str
    version: str
    kind: str
    runtime: str
    code: str
    requires: List[str] = field(default_factory=list)
    inputs: List[SnackInputSchema] = field(default_factory=list)
    outputs: List[SnackOutputSchema] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


# Valid snack kinds
VALID_SNACK_KINDS = ["script", "skill", "spark", "wasm", "snackbox", "vibe-skill"]

# Valid snack runtimes
VALID_SNACK_RUNTIMES = [
    "bash",
    "apple-script-osx", 
    "node",
    "python",
    "wasm",
    "spark-runtime",
    "vibe-skill",
    "github-spark",
]


def is_valid_semver(version: str) -> bool:
    """Check if a string is a valid semver version"""
    # Simple semver regex: major.minor.patch
    parts = version.split('.')
    if len(parts) != 3:
        return False
    
    for part in parts:
        if not part.isdigit():
            return False
    
    return True


def validate_snack_schema(schema: SnackSchema) -> None:
    """Validate a snack schema"""
    errors = []
    
    # Validate ID format
    if not schema.id:
        errors.append("Snack ID cannot be empty")

    # Validate name
    if not schema.name:
        errors.append("Snack name cannot be empty")

    # Validate version (basic semver check)
    if not is_valid_semver(schema.version):
        errors.append("Invalid version format. Use semver (e.g., 1.0.0)")

    # Validate kind
    if schema.kind not in VALID_SNACK_KINDS:
        errors.append(f"Invalid snack kind: {schema.kind}. Must be one of: {', '.join(VALID_SNACK_KINDS)}")

    # Validate runtime
    if schema.runtime not in VALID_SNACK_RUNTIMES:
        errors.append(f"Invalid runtime: {schema.runtime}. Must be one of: {', '.join(VALID_SNACK_RUNTIMES)}")

    # Validate code
    if not schema.code:
        errors.append("Snack code cannot be empty")

    # Validate inputs
    input_names = set()
    for input_schema in schema.inputs:
        if not input_schema.name:
            errors.append("Input name cannot be empty")
        if input_schema.name in input_names:
            errors.append(f"Duplicate input name: {input_schema.name}")
        input_names.add(input_schema.name)

    # Validate outputs
    output_names = set()
    for output_schema in schema.outputs:
        if not output_schema.name:
            errors.append("Output name cannot be empty")
        if output_schema.name in output_names:
            errors.append(f"Duplicate output name: {output_schema.name}")
        output_names.add(output_schema.name)

    if errors:
        raise ValueError("; ".join(errors))


# Test the schema validation
if __name__ == "__main__":
    # Test valid schema
    valid_schema = SnackSchema(
        id="P100-U899",
        name="Postie", 
        version="1.0.0",
        kind="script",
        runtime="bash",
        code="echo 'Hello'",
        requires=[],
        inputs=[],
        outputs=[],
        tags=["email"]
    )
    
    try:
        validate_snack_schema(valid_schema)
        print("✓ Valid schema passed validation")
    except ValueError as e:
        print(f"✗ Valid schema failed: {e}")
    
    # Test invalid ID
    try:
        invalid_schema = SnackSchema(
            id="",
            name="Postie",
            version="1.0.0",
            kind="script",
            runtime="bash",
            code="echo 'Hello'",
            requires=[],
            inputs=[],
            outputs=[],
            tags=[]
        )
        validate_snack_schema(invalid_schema)
        print("✗ Invalid ID should have failed")
    except ValueError as e:
        print(f"✓ Invalid ID correctly failed: {e}")
    
    # Test invalid version
    try:
        invalid_schema = SnackSchema(
            id="P100-U899",
            name="Postie",
            version="invalid",
            kind="script",
            runtime="bash",
            code="echo 'Hello'",
            requires=[],
            inputs=[],
            outputs=[],
            tags=[]
        )
        validate_snack_schema(invalid_schema)
        print("✗ Invalid version should have failed")
    except ValueError as e:
        print(f"✓ Invalid version correctly failed: {e}")
    
    # Test duplicate inputs
    try:
        input_schema = SnackInputSchema(name="mailbox", type="string", required=False)
        invalid_schema = SnackSchema(
            id="P100-U899",
            name="Postie",
            version="1.0.0",
            kind="script",
            runtime="bash",
            code="echo 'Hello'",
            requires=[],
            inputs=[input_schema, input_schema],  # Duplicate
            outputs=[],
            tags=[]
        )
        validate_snack_schema(invalid_schema)
        print("✗ Duplicate inputs should have failed")
    except ValueError as e:
        print(f"✓ Duplicate inputs correctly failed: {e}")
    
    print("All schema validation tests completed!")