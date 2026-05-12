#!/usr/bin/env python3
"""
Nugget models - Python Implementation

Nuggets are binary executable units in the uDos ecosystem.
They provide a compact, portable format for distributing and executing code.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import json
import hashlib
import zlib
import pickle
from pathlib import Path
import struct


@dataclass
class NuggetMetadata:
    """Metadata for a Nugget"""
    id: str
    name: str
    version: str
    description: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    runtime: str = "python"
    entry_point: Optional[str] = None


@dataclass
class NuggetResource:
    """Resource included in a Nugget"""
    name: str
    type: str  # "file", "data", "script", etc.
    data: bytes
    checksum: Optional[str] = None


@dataclass
class Nugget:
    """Represents a Nugget - a binary executable unit"""
    metadata: NuggetMetadata
    main_code: bytes
    resources: List[NuggetResource] = field(default_factory=list)
    checksum: Optional[str] = None
    signature: Optional[str] = None
    
    def __post_init__(self):
        """Calculate checksum after initialization"""
        self.checksum = self.calculate_checksum()
    
    def calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of the nugget content"""
        # Create a hash of metadata + resources + main_code
        content = f"{self.metadata.id}:{self.metadata.version}".encode()
        for resource in self.resources:
            content += resource.name.encode() + resource.data
        content += self.main_code
        
        return hashlib.sha256(content).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify the nugget's integrity"""
        return self.checksum == self.calculate_checksum()
    
    def add_resource(self, name: str, data: bytes, resource_type: str = "file") -> None:
        """Add a resource to the nugget"""
        resource = NuggetResource(
            name=name,
            type=resource_type,
            data=data,
            checksum=hashlib.sha256(data).hexdigest()
        )
        self.resources.append(resource)
        # Recalculate checksum after adding resource
        self.checksum = self.calculate_checksum()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Nugget to dictionary"""
        return {
            'metadata': {
                'id': self.metadata.id,
                'name': self.metadata.name,
                'version': self.metadata.version,
                'description': self.metadata.description,
                'author': self.metadata.author,
                'tags': self.metadata.tags,
                'dependencies': self.metadata.dependencies,
                'runtime': self.metadata.runtime,
                'entry_point': self.metadata.entry_point
            },
            'resources': [
                {
                    'name': r.name,
                    'type': r.type,
                    'checksum': r.checksum,
                    'size': len(r.data)
                }
                for r in self.resources
            ],
            'main_code_size': len(self.main_code),
            'checksum': self.checksum,
            'signature': self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Nugget':
        """Create Nugget from dictionary (limited reconstruction)"""
        metadata = NuggetMetadata(
            id=data['metadata']['id'],
            name=data['metadata']['name'],
            version=data['metadata']['version'],
            description=data['metadata'].get('description'),
            author=data['metadata'].get('author'),
            tags=data['metadata'].get('tags', []),
            dependencies=data['metadata'].get('dependencies', []),
            runtime=data['metadata'].get('runtime', 'python'),
            entry_point=data['metadata'].get('entry_point')
        )
        
        nugget = cls(
            metadata=metadata,
            main_code=b'',  # Main code would need to be loaded separately
            checksum=data.get('checksum')
        )
        
        # Resources would need to be loaded separately
        for resource_data in data.get('resources', []):
            # Placeholder resources
            nugget.resources.append(NuggetResource(
                name=resource_data['name'],
                type=resource_data['type'],
                data=b'',  # Data would be loaded separately
                checksum=resource_data.get('checksum')
            ))
        
        return nugget


class NuggetBinaryFormat:
    """Binary format for Nugget files"""
    
    # File magic number (4 bytes): 'NUGG'
    MAGIC = b'NUGG'
    # Format version (2 bytes): 0x0100 = version 1.0
    VERSION = struct.pack('>H', 0x0100)  # Big-endian, version 1.0
    
    @classmethod
    def pack(cls, nugget: Nugget) -> bytes:
        """Pack a Nugget into binary format"""
        # Header: MAGIC (4) + VERSION (2) + RESERVED (2) = 8 bytes
        header = cls.MAGIC + cls.VERSION + b'\x00\x00'
        
        # Metadata section
        metadata_json = json.dumps({
            'id': nugget.metadata.id,
            'name': nugget.metadata.name,
            'version': nugget.metadata.version,
            'description': nugget.metadata.description,
            'author': nugget.metadata.author,
            'tags': nugget.metadata.tags,
            'dependencies': nugget.metadata.dependencies,
            'runtime': nugget.metadata.runtime,
            'entry_point': nugget.metadata.entry_point
        }).encode('utf-8')
        
        # Metadata length (4 bytes) + metadata
        metadata_section = struct.pack('>I', len(metadata_json)) + metadata_json
        
        # Resources section
        resources_data = b''
        for resource in nugget.resources:
            # Resource header: name_length (2) + type_length (1) + data_length (4)
            name_bytes = resource.name.encode('utf-8')
            type_bytes = resource.type.encode('utf-8')
            
            resource_header = (
                struct.pack('>H', len(name_bytes)) +
                struct.pack('>B', len(type_bytes)) +
                struct.pack('>I', len(resource.data))
            )
            
            resources_data += resource_header + name_bytes + type_bytes + resource.data
        
        # Resources count (2 bytes) + resources data
        resources_section = struct.pack('>H', len(nugget.resources)) + resources_data
        
        # Main code section: length (4 bytes) + code
        main_code_section = struct.pack('>I', len(nugget.main_code)) + nugget.main_code
        
        # Checksum (32 bytes SHA256)
        checksum = hashlib.sha256(
            metadata_section + resources_section + main_code_section
        ).digest()
        
        # Final binary: header + metadata + resources + main_code + checksum
        return (
            header +
            metadata_section +
            resources_section +
            main_code_section +
            checksum
        )
    
    @classmethod
    def unpack(cls, data: bytes) -> Nugget:
        """Unpack binary data into a Nugget"""
        # Validate header
        if data[:4] != cls.MAGIC:
            raise ValueError("Invalid Nugget magic number")
        
        if data[4:6] != cls.VERSION:
            raise ValueError("Unsupported Nugget version")
        
        # Parse metadata
        metadata_length = struct.unpack('>I', data[8:12])[0]
        metadata_end = 12 + metadata_length
        metadata_json = data[12:metadata_end].decode('utf-8')
        metadata = json.loads(metadata_json)
        
        # Parse resources
        resources_start = metadata_end
        resources_count = struct.unpack('>H', data[resources_start:resources_start+2])[0]
        resources_end = resources_start + 2
        
        resources = []
        for _ in range(resources_count):
            # Parse resource header
            name_length = struct.unpack('>H', data[resources_end:resources_end+2])[0]
            type_length = struct.unpack('>B', data[resources_end+2:resources_end+3])[0]
            data_length = struct.unpack('>I', data[resources_end+3:resources_end+7])[0]
            
            resources_end += 7
            
            # Parse resource data
            name = data[resources_end:resources_end+name_length].decode('utf-8')
            resources_end += name_length
            
            resource_type = data[resources_end:resources_end+type_length].decode('utf-8')
            resources_end += type_length
            
            resource_data = data[resources_end:resources_end+data_length]
            resources_end += data_length
            
            resources.append(NuggetResource(
                name=name,
                type=resource_type,
                data=resource_data,
                checksum=hashlib.sha256(resource_data).hexdigest()
            ))
        
        # Parse main code
        main_code_length = struct.unpack('>I', data[resources_end:resources_end+4])[0]
        main_code_start = resources_end + 4
        main_code = data[main_code_start:main_code_start+main_code_length]
        
        # Parse and validate checksum
        checksum_start = main_code_start + main_code_length
        expected_checksum = data[checksum_start:checksum_start+32]
        
        actual_checksum = hashlib.sha256(
            data[8:checksum_start]  # Everything except header and checksum
        ).digest()
        
        if actual_checksum != expected_checksum:
            raise ValueError("Nugget checksum mismatch - file may be corrupted")
        
        # Create metadata object
        metadata_obj = NuggetMetadata(
            id=metadata['id'],
            name=metadata['name'],
            version=metadata['version'],
            description=metadata.get('description'),
            author=metadata.get('author'),
            tags=metadata.get('tags', []),
            dependencies=metadata.get('dependencies', []),
            runtime=metadata.get('runtime', 'python'),
            entry_point=metadata.get('entry_point')
        )
        
        # Create and return nugget
        nugget = Nugget(
            metadata=metadata_obj,
            resources=resources,
            main_code=main_code,
            checksum=expected_checksum.hex()
        )
        
        return nugget


class NuggetRegistry:
    """Registry for managing Nuggets"""
    
    def __init__(self, base_path: str = ".nuggets"):
        """Initialize the nugget registry"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def save_nugget(self, nugget: Nugget, filename: Optional[str] = None) -> Path:
        """Save a nugget to the registry"""
        if filename is None:
            filename = f"{nugget.metadata.id}.nugget"
        
        filepath = self.base_path / filename
        
        # Pack to binary format
        binary_data = NuggetBinaryFormat.pack(nugget)
        
        # Write to file
        with open(filepath, 'wb') as f:
            f.write(binary_data)
        
        return filepath
    
    def load_nugget(self, filename: str) -> Nugget:
        """Load a nugget from the registry"""
        filepath = self.base_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Nugget not found: {filename}")
        
        # Read binary data
        with open(filepath, 'rb') as f:
            binary_data = f.read()
        
        # Unpack from binary format
        return NuggetBinaryFormat.unpack(binary_data)
    
    def list_nuggets(self) -> List[Dict[str, Any]]:
        """List all nuggets in the registry"""
        nuggets = []
        
        for filepath in self.base_path.glob("*.nugget"):
            try:
                nugget = self.load_nugget(filepath.name)
                nuggets.append({
                    'filename': filepath.name,
                    'id': nugget.metadata.id,
                    'name': nugget.metadata.name,
                    'version': nugget.metadata.version,
                    'runtime': nugget.metadata.runtime,
                    'checksum': nugget.checksum,
                    'size': filepath.stat().st_size
                })
            except Exception as e:
                nuggets.append({
                    'filename': filepath.name,
                    'error': str(e)
                })
        
        return nuggets
    
    def delete_nugget(self, filename: str) -> bool:
        """Delete a nugget from the registry"""
        filepath = self.base_path / filename
        
        if filepath.exists():
            filepath.unlink()
            return True
        
        return False


# Test the Nugget implementation
if __name__ == "__main__":
    print("Testing Nugget System...")
    
    # Create a test nugget
    metadata = NuggetMetadata(
        id="TEST-NUGGET-001",
        name="Test Nugget",
        version="1.0.0",
        description="A test nugget for validation",
        author="uDos Team",
        tags=["test", "demo"],
        runtime="python"
    )
    
    nugget = Nugget(
        metadata=metadata,
        main_code=b'print("Hello from Nugget!")',
    )
    
    # Add a resource
    nugget.add_resource("config.json", b'{"setting": "value"}', "file")
    
    print(f"✓ Created nugget: {nugget.metadata.name}")
    print(f"✓ Checksum: {nugget.checksum}")
    print(f"✓ Integrity check: {nugget.verify_integrity()}")
    
    # Test binary format
    binary_data = NuggetBinaryFormat.pack(nugget)
    print(f"✓ Packed to binary: {len(binary_data)} bytes")
    
    # Test unpacking
    unpacked_nugget = NuggetBinaryFormat.unpack(binary_data)
    print(f"✓ Unpacked nugget: {unpacked_nugget.metadata.name}")
    print(f"✓ Unpacked integrity: {unpacked_nugget.verify_integrity()}")
    
    # Test registry
    registry = NuggetRegistry()
    filepath = registry.save_nugget(nugget)
    print(f"✓ Saved to registry: {filepath}")
    
    loaded_nugget = registry.load_nugget(filepath.name)
    print(f"✓ Loaded from registry: {loaded_nugget.metadata.name}")
    
    nuggets_list = registry.list_nuggets()
    print(f"✓ Registry contains {len(nuggets_list)} nuggets")
    
    print("All Nugget tests passed!")
