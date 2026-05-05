#!/usr/bin/env python3
"""
Snack validator implementation - Python version
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import re

from .models import Snack, SnackInput, SnackOutput, SnackResource
from .schema import SnackSchema, SnackInputSchema, SnackOutputSchema, validate_snack_schema


class SnackExecutionError(Exception):
    """Raised when a snack fails during execution."""
    def __init__(self, message: str, snack_id: Optional[str] = None, exit_code: Optional[int] = None):
        self.snack_id = snack_id
        self.exit_code = exit_code
        super().__init__(message)


def validate_snack(snack: Snack) -> None:
    """Validate a Snack instance"""
    # Convert Snack to SnackSchema for validation
    schema = SnackSchema(
        id=snack.id,
        name=snack.name,
        version=snack.version,
        kind=snack.kind,
        runtime=snack.runtime,
        code=snack.code,
        requires=snack.requires,
        inputs=[
            SnackInputSchema(
                name=input.name,
                type=input.type,
                default=input.default,
                required=input.required
            )
            for input in snack.inputs
        ],
        outputs=[
            SnackOutputSchema(
                name=output.name,
                type=output.type
            )
            for output in snack.outputs
        ],
        tags=snack.tags
    )
    
    validate_snack_schema(schema)


def validate_snack_file(path: Path) -> None:
    """Validate a Snack from a YAML file"""
    snack = Snack.load_from_file(path)
    validate_snack(snack)


def is_valid_cell_identifier(identifier: str) -> bool:
    """Check if a cell identifier is valid"""
    # Cell identifier format: L<level>-<gridXY>-<cellXY>-<layer>
    # Example: L100-BB45-1010-2
    parts = identifier.split('-')
    if len(parts) != 4:
        return False
    
    # Check level prefix
    if not parts[0].startswith('L'):
        return False
    
    # Check that all parts are non-empty
    for part in parts:
        if not part:
            return False
    
    return True


def validate_snack_resources(snack: Snack) -> None:
    """Validate resource requirements for a Snack"""
    if snack.resources:
        for resource in snack.resources:
            # Validate resource type
            if resource.type == "cell":
                # Validate cell identifier format
                if not is_valid_cell_identifier(resource.identifier):
                    raise ValueError(f"Invalid cell identifier: {resource.identifier}")
            elif resource.type in ["file", "database", "api"]:
                # Additional validation for other resource types
                if not resource.identifier:
                    raise ValueError(f"Resource identifier cannot be empty for type: {resource.type}")
            else:
                raise ValueError(f"Invalid resource type: {resource.type}")

            # Validate resource mode
            if resource.mode not in ["read", "write", "read_write"]:
                raise ValueError(f"Invalid resource mode: {resource.mode}")


# Test the validator
if __name__ == "__main__":
    # Test valid snack
    try:
        valid_snack = Snack.create("P100-U899", "Postie", "1.0.0", "echo 'Hello'")
        valid_snack.emoji = "📬"
        valid_snack.tags = ["email"]
        
        validate_snack(valid_snack)
        print("✓ Valid snack passed validation")
    except ValueError as e:
        print(f"✗ Valid snack failed: {e}")
    
    # Test invalid snack
    try:
        invalid_snack = Snack.create("", "Postie", "1.0.0", "echo 'Hello'")
        validate_snack(invalid_snack)
        print("✗ Invalid snack should have failed")
    except ValueError as e:
        print(f"✓ Invalid snack correctly failed: {e}")
    
    # Test snack file validation
    try:
        test_snack = Snack.create("P100-U899", "Postie", "1.0.0", "echo 'Hello'")
        test_path = Path("/tmp/test_snack_validation.yaml")
        test_snack.save_to_file(test_path)
        
        validate_snack_file(test_path)
        print("✓ Snack file validation passed")
        
        # Clean up
        test_path.unlink()
    except ValueError as e:
        print(f"✗ Snack file validation failed: {e}")
    
    # Test resource validation
    try:
        snack_with_resources = Snack.create("P100-U899", "Postie", "1.0.0", "echo 'Hello'")
        snack_with_resources.resources = [
            SnackResource(
                type="cell",
                identifier="L100-BB45-1010-2",
                mode="read_write",
                description="VIP email storage"
            )
        ]
        
        validate_snack_resources(snack_with_resources)
        print("✓ Valid snack resources passed validation")
    except ValueError as e:
        print(f"✗ Valid snack resources failed: {e}")
    
    # Test invalid cell identifier
    try:
        snack_with_invalid_cell = Snack.create("P100-U899", "Postie", "1.0.0", "echo 'Hello'")
        snack_with_invalid_cell.resources = [
            SnackResource(
                type="cell",
                identifier="invalid-cell-id",
                mode="read",
                description=None
            )
        ]
        
        validate_snack_resources(snack_with_invalid_cell)
        print("✗ Invalid cell identifier should have failed")
    except ValueError as e:
        print(f"✓ Invalid cell identifier correctly failed: {e}")
    
    print("All validator tests completed!")