#!/usr/bin/env python3
"""
USXD System - Python Implementation

USXD (Universal Structured eXchange Document) provides a portable format
for exchanging structured data between different systems and components in the uDos ecosystem.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
import json
import uuid
from pathlib import Path
import hashlib
from datetime import datetime
from enum import Enum


class USXDFormat(Enum):
    """Supported USXD formats"""
    JSON = "json"
    YAML = "yaml"
    BINARY = "binary"
    MARKDOWN = "markdown"
    HTML = "html"


@dataclass
class USXDMetadata:
    """Metadata for a USXD document"""
    id: str
    title: str
    version: str
    description: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    format: USXDFormat = USXDFormat.JSON
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize timestamps if not provided"""
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now


@dataclass
class USXDSection:
    """Section within a USXD document"""
    id: str
    name: str
    section_type: str  # "content", "data", "metadata", "reference"
    content: Optional[Union[str, Dict[str, Any], List[Any]]] = None
    format: Optional[str] = None  # MIME type or format hint
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class USXDDocument:
    """Represents a USXD document - a portable structured exchange format"""
    metadata: USXDMetadata
    sections: List[USXDSection] = field(default_factory=list)
    checksum: Optional[str] = None
    signature: Optional[str] = None
    
    def __post_init__(self):
        """Calculate checksum after initialization"""
        self.checksum = self.calculate_checksum()
    
    def calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of the document content"""
        content = f"{self.metadata.id}:{self.metadata.version}".encode()
        for section in self.sections:
            content += f"{section.id}:{section.name}".encode()
            if section.content is not None:
                if isinstance(section.content, str):
                    content += section.content.encode()
                else:
                    content += json.dumps(section.content, sort_keys=True).encode()
        
        return hashlib.sha256(content).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify the document's integrity"""
        return self.checksum == self.calculate_checksum()
    
    def add_section(self, section: USXDSection) -> None:
        """Add a section to the document"""
        self.sections.append(section)
        self.checksum = self.calculate_checksum()
    
    def get_section(self, section_id: str) -> Optional[USXDSection]:
        """Get a section by ID"""
        for section in self.sections:
            if section.id == section_id:
                return section
        return None
    
    def remove_section(self, section_id: str) -> bool:
        """Remove a section by ID"""
        for i, section in enumerate(self.sections):
            if section.id == section_id:
                del self.sections[i]
                self.checksum = self.calculate_checksum()
                return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert USXD document to dictionary"""
        return {
            'metadata': {
                'id': self.metadata.id,
                'title': self.metadata.title,
                'version': self.metadata.version,
                'description': self.metadata.description,
                'author': self.metadata.author,
                'created_at': self.metadata.created_at,
                'updated_at': self.metadata.updated_at,
                'format': self.metadata.format.value,
                'tags': self.metadata.tags
            },
            'sections': [self._section_to_dict(s) for s in self.sections],
            'checksum': self.checksum,
            'signature': self.signature
        }
    
    def _section_to_dict(self, section: USXDSection) -> Dict[str, Any]:
        """Convert USXDSection to dictionary"""
        result = {
            'id': section.id,
            'name': section.name,
            'type': section.section_type
        }
        
        if section.content is not None:
            result['content'] = section.content
        
        if section.format:
            result['format'] = section.format
        
        if section.metadata:
            result['metadata'] = section.metadata
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'USXDDocument':
        """Create USXD document from dictionary"""
        metadata = USXDMetadata(
            id=data['metadata']['id'],
            title=data['metadata']['title'],
            version=data['metadata']['version'],
            description=data['metadata'].get('description'),
            author=data['metadata'].get('author'),
            created_at=data['metadata'].get('created_at'),
            updated_at=data['metadata'].get('updated_at'),
            format=USXDFormat(data['metadata'].get('format', 'json')),
            tags=data['metadata'].get('tags', [])
        )
        
        sections = [cls._section_from_dict(s) for s in data.get('sections', [])]
        
        document = cls(
            metadata=metadata,
            sections=sections,
            checksum=data.get('checksum'),
            signature=data.get('signature')
        )
        
        return document
    
    @classmethod
    def _section_from_dict(cls, data: Dict[str, Any]) -> USXDSection:
        """Create USXDSection from dictionary"""
        section = USXDSection(
            id=data['id'],
            name=data['name'],
            section_type=data['type'],
            content=data.get('content'),
            format=data.get('format'),
            metadata=data.get('metadata')
        )
        return section
    
    def to_json(self) -> str:
        """Convert document to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'USXDDocument':
        """Create document from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, path: Path, format: USXDFormat = USXDFormat.JSON) -> None:
        """Save document to file"""
        if format == USXDFormat.JSON:
            with open(path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
        elif format == USXDFormat.YAML:
            import yaml
            with open(path, 'w') as f:
                yaml.safe_dump(self.to_dict(), f)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @classmethod
    def load_from_file(cls, path: Path) -> 'USXDDocument':
        """Load document from file"""
        with open(path, 'r') as f:
            # Try JSON first
            try:
                data = json.load(f)
                return cls.from_dict(data)
            except json.JSONDecodeError:
                # Try YAML
                import yaml
                data = yaml.safe_load(f)
                return cls.from_dict(data)


class USXDRegistry:
    """Registry for managing USXD documents"""
    
    def __init__(self, base_path: str = ".usxd"):
        """Initialize the USXD registry"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def save_document(self, document: USXDDocument, filename: Optional[str] = None, 
                     format: USXDFormat = USXDFormat.JSON) -> Path:
        """Save a document to the registry"""
        if filename is None:
            filename = f"{document.metadata.id}.usxd.{format.value}"
        
        filepath = self.base_path / filename
        document.save_to_file(filepath, format)
        
        return filepath
    
    def load_document(self, filename: str) -> USXDDocument:
        """Load a document from the registry"""
        filepath = self.base_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Document not found: {filename}")
        
        return USXDDocument.load_from_file(filepath)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the registry"""
        documents = []
        
        for filepath in self.base_path.glob("*.usxd.*"):
            try:
                doc = self.load_document(filepath.name)
                documents.append({
                    'filename': filepath.name,
                    'id': doc.metadata.id,
                    'title': doc.metadata.title,
                    'version': doc.metadata.version,
                    'format': doc.metadata.format.value,
                    'checksum': doc.checksum,
                    'size': filepath.stat().st_size
                })
            except Exception as e:
                documents.append({
                    'filename': filepath.name,
                    'error': str(e)
                })
        
        return documents
    
    def delete_document(self, filename: str) -> bool:
        """Delete a document from the registry"""
        filepath = self.base_path / filename
        
        if filepath.exists():
            filepath.unlink()
            return True
        
        return False


# Test the USXD implementation
if __name__ == "__main__":
    print("Testing USXD System...")
    
    # Create a test document
    metadata = USXDMetadata(
        id="TEST-USXD-001",
        title="Test Document",
        version="1.0.0",
        description="A test USXD document",
        author="uDos Team",
        tags=["test", "demo"]
    )
    
    document = USXDDocument(metadata=metadata)
    
    # Add sections
    section1 = USXDSection(
        id="section1",
        name="Introduction",
        section_type="content",
        content="This is the introduction section."
    )
    document.add_section(section1)
    
    section2 = USXDSection(
        id="section2",
        name="Data",
        section_type="data",
        content={"key": "value", "array": [1, 2, 3]}
    )
    document.add_section(section2)
    
    print(f"✓ Created document: {document.metadata.title}")
    print(f"✓ Checksum: {document.checksum}")
    print(f"✓ Integrity check: {document.verify_integrity()}")
    
    # Test serialization
    doc_dict = document.to_dict()
    print(f"✓ Serialization successful")
    
    # Test deserialization
    document2 = USXDDocument.from_dict(doc_dict)
    print(f"✓ Deserialization successful: {document2.metadata.title}")
    
    # Test JSON conversion
    json_str = document.to_json()
    print(f"✓ JSON conversion successful")
    
    # Test registry
    registry = USXDRegistry()
    filepath = registry.save_document(document)
    print(f"✓ Saved to registry: {filepath}")
    
    loaded_doc = registry.load_document(filepath.name)
    print(f"✓ Loaded from registry: {loaded_doc.metadata.title}")
    
    docs_list = registry.list_documents()
    print(f"✓ Registry contains {len(docs_list)} documents")
    
    print("All USXD tests passed!")