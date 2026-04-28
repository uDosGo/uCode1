#!/usr/bin/env python3
"""
Snack module for uDos - Python Implementation

This module provides the core functionality for managing and executing Snacks,
which are atomic executable units in the uDos ecosystem.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import json
import yaml
from pathlib import Path
import re


@dataclass
class SnackInput:
    """Input parameter for a Snack"""
    name: str
    type: str
    default: Optional[Any] = None
    required: bool = False


@dataclass
class SnackOutput:
    """Output parameter for a Snack"""
    name: str
    type: str


@dataclass
class SnackLexicon:
    """Lexicon translations for a Snack"""
    terms: List[str]
    emoji: Optional[str] = None
    short: str = ""
    long: str = ""


@dataclass
class SnackVisuals:
    """Visual representation for a Snack"""
    ascii: Optional[str] = None
    teletext: Optional[str] = None
    color: Optional[str] = None


@dataclass
class SnackChain:
    """Chaining rules for a Snack"""
    can_be_before: List[str] = field(default_factory=list)
    can_be_after: List[str] = field(default_factory=list)
    can_be_parallel: bool = False


@dataclass
class SnackResource:
    """Resource requirement for a Snack"""
    type: str  # "cell", "file", "database", etc.
    identifier: str  # e.g., "L100-BB45-1010-2" for cells
    mode: str  # "read", "write", "read_write"
    description: Optional[str] = None


@dataclass
class Snack:
    """Represents a Snack - an atomic executable unit"""
    id: str
    name: str
    version: str
    emoji: Optional[str] = None
    glyph: Optional[str] = None
    ascii: Optional[str] = None
    kind: str = "script"
    runtime: str = "bash"
    code: str = ""
    requires: List[str] = field(default_factory=list)
    inputs: List[SnackInput] = field(default_factory=list)
    outputs: List[SnackOutput] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    lexicon: Optional[SnackLexicon] = None
    visuals: Optional[SnackVisuals] = None
    chain: Optional[SnackChain] = None
    resources: Optional[List[SnackResource]] = None

    @classmethod
    def create(cls, id: str, name: str, version: str, code: str) -> 'Snack':
        """Create a new Snack instance"""
        return cls(
            id=id,
            name=name,
            version=version,
            code=code
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Snack to dictionary"""
        result = {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'kind': self.kind,
            'runtime': self.runtime,
            'code': self.code,
            'requires': self.requires,
            'inputs': [input.to_dict() for input in self.inputs],
            'outputs': [output.to_dict() for output in self.outputs],
            'tags': self.tags,
        }
        
        if self.emoji:
            result['emoji'] = self.emoji
        if self.glyph:
            result['glyph'] = self.glyph
        if self.ascii:
            result['ascii'] = self.ascii
        if self.lexicon:
            result['lexicon'] = self.lexicon.to_dict()
        if self.visuals:
            result['visuals'] = self.visuals.to_dict()
        if self.chain:
            result['chain'] = self.chain.to_dict()
        if self.resources:
            result['resources'] = [resource.to_dict() for resource in self.resources]
            
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Snack':
        """Create Snack from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            version=data['version'],
            emoji=data.get('emoji'),
            glyph=data.get('glyph'),
            ascii=data.get('ascii'),
            kind=data.get('kind', 'script'),
            runtime=data.get('runtime', 'bash'),
            code=data['code'],
            requires=data.get('requires', []),
            inputs=[SnackInput(**input_data) for input_data in data.get('inputs', [])],
            outputs=[SnackOutput(**output_data) for output_data in data.get('outputs', [])],
            tags=data.get('tags', []),
            lexicon=SnackLexicon(**data['lexicon']) if data.get('lexicon') else None,
            visuals=SnackVisuals(**data['visuals']) if data.get('visuals') else None,
            chain=SnackChain(**data['chain']) if data.get('chain') else None,
            resources=[SnackResource(**resource_data) for resource_data in data.get('resources', [])] if data.get('resources') else None
        )

    def save_to_file(self, path: Path) -> None:
        """Save a Snack to a YAML file"""
        with open(path, 'w') as f:
            yaml.safe_dump(self.to_dict(), f)

    @classmethod
    def load_from_file(cls, path: Path) -> 'Snack':
        """Load a Snack from a YAML file"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)


# Helper methods for data classes

def _to_dict_helper(obj):
    """Helper to convert dataclass to dict"""
    if hasattr(obj, 'to_dict') and callable(obj.to_dict):
        return obj.to_dict()
    elif hasattr(obj, '__dict__'):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    else:
        return obj


# Add to_dict methods to nested classes
for cls in [SnackInput, SnackOutput, SnackLexicon, SnackVisuals, SnackChain, SnackResource]:
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                    result[key] = value.to_dict()
                else:
                    result[key] = value
        return result
    cls.to_dict = to_dict


# Test the implementation
if __name__ == "__main__":
    # Create a test snack
    snack = Snack.create("P100-U899", "Postie", "1.0.0", "echo 'Hello'")
    snack.emoji = "📬"
    snack.tags = ["email", "ingest"]
    
    # Test serialization
    snack_dict = snack.to_dict()
    print("Snack as dict:", snack_dict)
    
    # Test deserialization
    snack2 = Snack.from_dict(snack_dict)
    print("Reconstructed snack:", snack2)
    
    # Test file operations
    test_path = Path("/tmp/test_snack.yaml")
    snack.save_to_file(test_path)
    loaded_snack = Snack.load_from_file(test_path)
    print("Loaded from file:", loaded_snack)
    
    print("All tests passed!")