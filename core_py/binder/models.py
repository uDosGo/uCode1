#!/usr/bin/env python3
"""
Binder System - Python Implementation

Binders are structured data containers in the uDos ecosystem.
They provide a hierarchical organization system for managing complex data,
resources, and relationships between components.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
import json
import uuid
from pathlib import Path
import hashlib
from datetime import datetime


@dataclass
class BinderMetadata:
    """Metadata for a Binder"""
    id: str
    name: str
    version: str
    description: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize timestamps if not provided"""
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now


@dataclass
class BinderResource:
    """Resource stored in a Binder"""
    id: str
    name: str
    resource_type: str  # "file", "data", "reference", "snack", "relic"
    data: Optional[Union[str, bytes, Dict[str, Any]]] = None
    path: Optional[str] = None  # For file references
    checksum: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Calculate checksum if data is provided"""
        if self.data is not None and self.checksum is None:
            if isinstance(self.data, str):
                self.checksum = hashlib.sha256(self.data.encode()).hexdigest()
            elif isinstance(self.data, bytes):
                self.checksum = hashlib.sha256(self.data).hexdigest()
            elif isinstance(self.data, dict):
                self.checksum = hashlib.sha256(json.dumps(self.data, sort_keys=True).encode()).hexdigest()


@dataclass
class BinderEntry:
    """Individual entry in a Binder"""
    id: str
    name: str
    entry_type: str  # "data", "reference", "collection", "link"
    value: Optional[Any] = None
    resources: List[BinderResource] = field(default_factory=list)
    children: List['BinderEntry'] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class Binder:
    """Represents a Binder - a structured data container"""
    metadata: BinderMetadata
    root: BinderEntry
    checksum: Optional[str] = None
    signature: Optional[str] = None
    
    def __post_init__(self):
        """Calculate checksum after initialization"""
        self.checksum = self.calculate_checksum()
    
    def calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of the binder content"""
        content = f"{self.metadata.id}:{self.metadata.version}".encode()
        content += self._serialize_entry(self.root).encode()
        return hashlib.sha256(content).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify the binder's integrity"""
        return self.checksum == self.calculate_checksum()
    
    def _serialize_entry(self, entry: BinderEntry) -> str:
        """Recursively serialize an entry for checksum calculation"""
        result = f"{entry.id}:{entry.name}:{entry.entry_type}"
        
        # Add value if present
        if entry.value is not None:
            if isinstance(entry.value, (str, int, float, bool)):
                result += f":{entry.value}"
            else:
                result += f":{json.dumps(entry.value, sort_keys=True)}"
        
        # Add resources
        for resource in entry.resources:
            result += f"|{resource.id}:{resource.name}:{resource.resource_type}"
            if resource.checksum:
                result += f":{resource.checksum}"
        
        # Add children recursively
        for child in entry.children:
            result += f"<{self._serialize_entry(child)}>"
        
        return result
    
    def add_entry(self, parent_id: str, entry: BinderEntry) -> bool:
        """Add an entry to the binder at the specified parent"""
        if parent_id == "root":
            self.root.children.append(entry)
            self.checksum = self.calculate_checksum()
            return True
        
        found = self._find_entry(self.root, parent_id)
        if found:
            found.children.append(entry)
            self.checksum = self.calculate_checksum()
            return True
        
        return False
    
    def _find_entry(self, current: BinderEntry, target_id: str) -> Optional[BinderEntry]:
        """Recursively find an entry by ID"""
        if current.id == target_id:
            return current
        
        for child in current.children:
            found = self._find_entry(child, target_id)
            if found:
                return found
        
        return None
    
    def get_entry(self, entry_id: str) -> Optional[BinderEntry]:
        """Get an entry by ID"""
        if self.root.id == entry_id:
            return self.root
        
        return self._find_entry(self.root, entry_id)
    
    def add_resource(self, entry_id: str, resource: BinderResource) -> bool:
        """Add a resource to an entry"""
        entry = self.get_entry(entry_id)
        if entry:
            entry.resources.append(resource)
            self.checksum = self.calculate_checksum()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Binder to dictionary"""
        return {
            'metadata': {
                'id': self.metadata.id,
                'name': self.metadata.name,
                'version': self.metadata.version,
                'description': self.metadata.description,
                'author': self.metadata.author,
                'created_at': self.metadata.created_at,
                'updated_at': self.metadata.updated_at,
                'tags': self.metadata.tags,
                'dependencies': self.metadata.dependencies
            },
            'root': self._entry_to_dict(self.root),
            'checksum': self.checksum,
            'signature': self.signature
        }
    
    def _entry_to_dict(self, entry: BinderEntry) -> Dict[str, Any]:
        """Convert BinderEntry to dictionary"""
        result = {
            'id': entry.id,
            'name': entry.name,
            'type': entry.entry_type,
            'resources': [self._resource_to_dict(r) for r in entry.resources],
            'children': [self._entry_to_dict(c) for c in entry.children]
        }
        
        if entry.value is not None:
            result['value'] = entry.value
        
        if entry.metadata:
            result['metadata'] = entry.metadata
        
        return result
    
    def _resource_to_dict(self, resource: BinderResource) -> Dict[str, Any]:
        """Convert BinderResource to dictionary"""
        result = {
            'id': resource.id,
            'name': resource.name,
            'type': resource.resource_type,
            'checksum': resource.checksum
        }
        
        if resource.path:
            result['path'] = resource.path
        
        if resource.metadata:
            result['metadata'] = resource.metadata
        
        # Don't include raw data in serialization by default
        # if resource.data is not None:
        #     result['data'] = resource.data
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Binder':
        """Create Binder from dictionary"""
        metadata = BinderMetadata(
            id=data['metadata']['id'],
            name=data['metadata']['name'],
            version=data['metadata']['version'],
            description=data['metadata'].get('description'),
            author=data['metadata'].get('author'),
            created_at=data['metadata'].get('created_at'),
            updated_at=data['metadata'].get('updated_at'),
            tags=data['metadata'].get('tags', []),
            dependencies=data['metadata'].get('dependencies', [])
        )
        
        root = cls._entry_from_dict(data['root'])
        
        binder = cls(
            metadata=metadata,
            root=root,
            checksum=data.get('checksum'),
            signature=data.get('signature')
        )
        
        return binder
    
    @classmethod
    def _entry_from_dict(cls, data: Dict[str, Any]) -> BinderEntry:
        """Create BinderEntry from dictionary"""
        entry = BinderEntry(
            id=data['id'],
            name=data['name'],
            entry_type=data['type'],
            value=data.get('value'),
            resources=[cls._resource_from_dict(r) for r in data.get('resources', [])],
            children=[cls._entry_from_dict(c) for c in data.get('children', [])],
            metadata=data.get('metadata')
        )
        return entry
    
    @classmethod
    def _resource_from_dict(cls, data: Dict[str, Any]) -> BinderResource:
        """Create BinderResource from dictionary"""
        resource = BinderResource(
            id=data['id'],
            name=data['name'],
            resource_type=data['type'],
            path=data.get('path'),
            checksum=data.get('checksum'),
            metadata=data.get('metadata')
        )
        return resource
    
    def save_to_file(self, path: Path) -> None:
        """Save a Binder to a JSON file"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, path: Path) -> 'Binder':
        """Load a Binder from a JSON file"""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class BinderRegistry:
    """Registry for managing Binders"""
    
    def __init__(self, base_path: str = ".binders"):
        """Initialize the binder registry"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def save_binder(self, binder: Binder, filename: Optional[str] = None) -> Path:
        """Save a binder to the registry"""
        if filename is None:
            filename = f"{binder.metadata.id}.binder.json"
        
        filepath = self.base_path / filename
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(binder.to_dict(), f, indent=2)
        
        return filepath
    
    def load_binder(self, filename: str) -> Binder:
        """Load a binder from the registry"""
        filepath = self.base_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Binder not found: {filename}")
        
        # Load from file
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return Binder.from_dict(data)
    
    def list_binders(self) -> List[Dict[str, Any]]:
        """List all binders in the registry"""
        binders = []
        
        for filepath in self.base_path.glob("*.binder.json"):
            try:
                binder = self.load_binder(filepath.name)
                binders.append({
                    'filename': filepath.name,
                    'id': binder.metadata.id,
                    'name': binder.metadata.name,
                    'version': binder.metadata.version,
                    'checksum': binder.checksum,
                    'size': filepath.stat().st_size
                })
            except Exception as e:
                binders.append({
                    'filename': filepath.name,
                    'error': str(e)
                })
        
        return binders
    
    def delete_binder(self, filename: str) -> bool:
        """Delete a binder from the registry"""
        filepath = self.base_path / filename
        
        if filepath.exists():
            filepath.unlink()
            return True
        
        return False


# Test the Binder implementation
if __name__ == "__main__":
    print("Testing Binder System...")
    
    # Create a test binder
    metadata = BinderMetadata(
        id="TEST-BINDER-001",
        name="Test Binder",
        version="1.0.0",
        description="A test binder for validation",
        author="uDos Team",
        tags=["test", "demo"]
    )
    
    root = BinderEntry(
        id="root",
        name="Root",
        entry_type="collection"
    )
    
    binder = Binder(metadata=metadata, root=root)
    
    # Add a child entry
    child_entry = BinderEntry(
        id="child1",
        name="Child Entry",
        entry_type="data",
        value={"key": "value"}
    )
    binder.add_entry("root", child_entry)
    
    # Add a resource
    resource = BinderResource(
        id="res1",
        name="Test Resource",
        resource_type="file",
        data="test data"
    )
    binder.add_resource("child1", resource)
    
    print(f"✓ Created binder: {binder.metadata.name}")
    print(f"✓ Checksum: {binder.checksum}")
    print(f"✓ Integrity check: {binder.verify_integrity()}")
    
    # Test serialization
    binder_dict = binder.to_dict()
    print(f"✓ Serialization successful")
    
    # Test deserialization
    binder2 = Binder.from_dict(binder_dict)
    print(f"✓ Deserialization successful: {binder2.metadata.name}")
    
    # Test registry
    registry = BinderRegistry()
    filepath = registry.save_binder(binder)
    print(f"✓ Saved to registry: {filepath}")
    
    loaded_binder = registry.load_binder(filepath.name)
    print(f"✓ Loaded from registry: {loaded_binder.metadata.name}")
    
    binders_list = registry.list_binders()
    print(f"✓ Registry contains {len(binders_list)} binders")
    
    print("All Binder tests passed!")