#!/usr/bin/env python3
"""
uCode1 Binder CLI - Standalone command-line interface for Binder management

This CLI provides full Binder management capabilities without requiring
the complete uCode1 package to be installed.

Usage:
  binder [COMMAND] [OPTIONS]

Commands:
  list        List available binders
  show        Show details of a specific binder
  create      Create a new binder
  validate    Validate a binder file
  extract     Extract content from a binder
  pack        Pack content into a binder
  search      Search within binders
  tree        Show hierarchical structure
  info        Show metadata and information
  export      Export binder to other formats
  import      Import content into binder
  help        Show help for a command

Examples:
  binder list
  binder show BINDER_ID
  binder create NEW_BINDER --title "My Binder"
  binder validate binder.yaml
  binder tree BINDER_ID
  binder export BINDER_ID --format json
"""

import sys
import os
import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add core_py to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from core_py import (
        Binder, BinderMetadata, BinderEntry, BinderResource, BinderRegistry,
        USXDDocument, USXDMetadata, USXDSection
    )
    CORE_PY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: core_py not available: {e}")
    print("Binder CLI functionality will be limited.")
    CORE_PY_AVAILABLE = False


class BinderCLI:
    """Command-line interface for Binder management"""
    
    def __init__(self):
        self.registry = BinderRegistry() if CORE_PY_AVAILABLE else None
        self.registry_dir = Path(".binders")
        
        # Ensure registry directory exists
        self.registry_dir.mkdir(exist_ok=True)
    
    def main(self, args):
        """Main entry point for binder CLI"""
        if not CORE_PY_AVAILABLE:
            print("Error: core_py module not available. Cannot run Binder CLI.")
            return 1
        
        if len(args) < 1:
            self._print_help()
            return 0
        
        command = args[0]
        
        try:
            if command == "list":
                return self._command_list(args[1:])
            elif command == "show":
                return self._command_show(args[1:])
            elif command == "create":
                return self._command_create(args[1:])
            elif command == "validate":
                return self._command_validate(args[1:])
            elif command == "extract":
                return self._command_extract(args[1:])
            elif command == "pack":
                return self._command_pack(args[1:])
            elif command == "search":
                return self._command_search(args[1:])
            elif command == "tree":
                return self._command_tree(args[1:])
            elif command == "info":
                return self._command_info(args[1:])
            elif command == "export":
                return self._command_export(args[1:])
            elif command == "import":
                return self._command_import(args[1:])
            elif command == "help" or command == "--help" or command == "-h":
                self._print_help()
                return 0
            else:
                print(f"Unknown command: {command}")
                self._print_help()
                return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def _print_help(self):
        """Print help message"""
        print(__doc__)
    
    def _command_list(self, args):
        """List available binders"""
        parser = argparse.ArgumentParser(description='List available binders')
        parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
        parser.add_argument('--filter', '-f', type=str, help='Filter by title or ID')
        parser.add_argument('--sort', '-s', choices=['name', 'date', 'size'], default='name', help='Sort order')
        
        args = parser.parse_args(args)
        
        binders = self.registry.list_binders() if CORE_PY_AVAILABLE else []
        
        print("Available Binders:")
        print("-" * 60)
        
        if not binders:
            print("No binders found.")
            return 0
        
        # Filter
        if args.filter:
            binders = [b for b in binders if 
                      args.filter.lower() in b.get('title', '').lower() or 
                      args.filter.lower() in b.get('id', '').lower()]
        
        # Sort
        if args.sort == 'date':
            binders.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif args.sort == 'size':
            binders.sort(key=lambda x: x.get('size', 0), reverse=True)
        else:
            binders.sort(key=lambda x: x.get('title', ''))
        
        for binder in binders:
            info = binder.get('id', 'unknown')
            title = binder.get('title', 'Untitled')
            version = binder.get('version', '1.0')
            size = binder.get('size', 0)
            
            if args.verbose:
                print(f"  ID: {info}")
                print(f"  Title: {title}")
                print(f"  Version: {version}")
                print(f"  Size: {size} bytes")
                print(f"  Checksum: {binder.get('checksum', 'N/A')}")
                print()
            else:
                # Truncate long titles
                display_title = title[:40] + "..." if len(title) > 40 else title
                print(f"  {info:20} | {display_title:40} | v{version:5} | {size:8} bytes")
        
        print("-" * 60)
        print(f"Total: {len(binders)} binders")
        return 0
    
    def _command_show(self, args):
        """Show details of a specific binder"""
        parser = argparse.ArgumentParser(description='Show binder details')
        parser.add_argument('binder_id', type=str, nargs='?', help='Binder ID or filename')
        parser.add_argument('--section', '-s', type=str, help='Show specific section')
        parser.add_argument('--tree', '-t', action='store_true', help='Show as tree structure')
        parser.add_argument('--raw', '-r', action='store_true', help='Show raw YAML')
        
        args = parser.parse_args(args)
        
        if not args.binder_id:
            print("Error: Please specify a binder ID or filename")
            return 1
        
        # Try to find binder
        binder = None
        try:
            binder = self.registry.load_binder(args.binder_id)
        except FileNotFoundError:
            # Try as direct file
            try:
                binder = self.registry.load_binder_from_file(Path(args.binder_id))
            except:
                print(f"Error: Binder '{args.binder_id}' not found")
                return 1
        
        if args.raw:
            print(binder.to_yaml())
            return 0
        
        print(f"Binder: {binder.metadata.name}")
        print(f"ID: {binder.metadata.id}")
        print(f"Version: {binder.metadata.version}")
        print(f"Description: {binder.metadata.description or 'N/A'}")
        print(f"Author: {binder.metadata.author or 'N/A'}")
        print(f"Created: {binder.metadata.created_at}")
        print(f"Updated: {binder.metadata.updated_at}")
        print(f"Checksum: {binder.checksum}")
        print(f"Integrity: {'✓ Valid' if binder.verify_integrity() else '✗ Invalid'}")
        print()
        
        if args.tree:
            self._print_tree(binder)
        else:
            # Show root entry and children
            root = binder.root
            print(f"Root Entry: {root.name} ({root.entry_type})")
            if root.children:
                print("Children:")
                for i, entry in enumerate(root.children):
                    print(f"  {i+1}. {entry.name} ({entry.entry_type})")
                    if entry.value:
                        print(f"      Value: {entry.value}")
                    if entry.resources:
                        print(f"      Resources: {len(entry.resources)}")
                        for j, res in enumerate(entry.resources):
                            print(f"        {j+1}. {res.name} ({res.resource_type})")
            
            if args.section and root.children:
                # Find section
                for entry in root.children:
                    if entry.name == args.section or entry.id == args.section:
                        print(f"\nSection Details: {entry.name}")
                        print(f"  Type: {entry.entry_type}")
                        if entry.value:
                            print(f"  Value: {entry.value}")
                        if entry.children:
                            print(f"  Children: {len(entry.children)}")
        
        return 0
    
    def _command_create(self, args):
        """Create a new binder"""
        parser = argparse.ArgumentParser(description='Create a new binder')
        parser.add_argument('id', type=str, help='Binder ID')
        parser.add_argument('--title', '-t', type=str, default='Untitled', help='Binder title')
        parser.add_argument('--version', '-v', type=str, default='1.0.0', help='Version')
        parser.add_argument('--description', '-d', type=str, help='Description')
        parser.add_argument('--author', '-a', type=str, help='Author')
        parser.add_argument('--from-file', '-f', type=str, help='Create from YAML/JSON file')
        
        args = parser.parse_args(args)
        
        if args.from_file:
            # Load from file
            file_path = Path(args.from_file)
            if not file_path.exists():
                print(f"Error: File '{args.from_file}' not found")
                return 1
            
            try:
                file_binder = self.registry.load_binder_from_file(file_path)
                # Save to registry
                self.registry.save_binder(file_binder)
                print(f"✓ Imported binder from '{args.from_file}'")
                print(f"  ID: {file_binder.metadata.id}")
                print(f"  Title: {file_binder.metadata.title}")
                return 0
            except Exception as e:
                print(f"Error loading file: {e}")
                return 1
        
        # Create new binder
        metadata = BinderMetadata(
            id=args.id,
            name=args.title,
            version=args.version,
            description=args.description,
            author=args.author
        )
        
        # Create root entry
        from core_py import BinderEntry
        root_entry = BinderEntry(
            id="root",
            name="Root",
            entry_type="collection"
        )
        
        binder = Binder(metadata=metadata, root=root_entry)
        
        # Save to registry
        filepath = self.registry.save_binder(binder)
        print(f"✓ Created binder: {binder.metadata.title}")
        print(f"  ID: {binder.metadata.id}")
        print(f"  Saved to: {filepath}")
        
        return 0
    
    def _command_validate(self, args):
        """Validate a binder file"""
        parser = argparse.ArgumentParser(description='Validate binder')
        parser.add_argument('binder_id', type=str, help='Binder ID or filename')
        parser.add_argument('--strict', '-s', action='store_true', help='Strict validation')
        
        args = parser.parse_args(args)
        
        try:
            binder = self.registry.load_binder(args.binder_id)
            
            # Validate
            errors = []
            
            # Check metadata
            if not binder.metadata.id:
                errors.append("Missing ID")
            if not binder.metadata.title:
                errors.append("Missing title")
            
            # Check integrity
            if not binder.verify_integrity():
                errors.append("Checksum mismatch - data may be corrupted")
            
            if errors:
                print("❌ Validation Failed:")
                for error in errors:
                    print(f"  - {error}")
                return 1
            else:
                print("✅ Validation Passed")
                print(f"  ID: {binder.metadata.id}")
                print(f"  Title: {binder.metadata.title}")
                print(f"  Checksum: {binder.checksum}")
                return 0
        
        except Exception as e:
            print(f"❌ Validation Error: {e}")
            return 1
    
    def _command_extract(self, args):
        """Extract content from a binder"""
        parser = argparse.ArgumentParser(description='Extract from binder')
        parser.add_argument('binder_id', type=str, help='Binder ID or filename')
        parser.add_argument('--entry', '-e', type=str, help='Extract specific entry')
        parser.add_argument('--resource', '-r', type=str, help='Extract specific resource')
        parser.add_argument('--output', '-o', type=str, help='Output file')
        parser.add_argument('--list', '-l', action='store_true', help='List extractable items')
        
        args = parser.parse_args(args)
        
        try:
            binder = self.registry.load_binder(args.binder_id)
        except Exception as e:
            print(f"Error: {e}")
            return 1
        
        if args.list:
            print("Extractable Items:")
            if binder.entries:
                for i, entry in enumerate(binder.entries):
                    print(f"  Entry {i+1}: {entry.name} ({entry.entry_type})")
                    for j, res in enumerate(entry.resources):
                        print(f"    Resource {j+1}: {res.resource_type} - {res.source}")
            if binder.resources:
                for i, res in enumerate(binder.resources):
                    print(f"  Resource {i+1}: {res.resource_type} - {res.source}")
            return 0
        
        # Extract specific entry or all
        if args.entry:
            # Find entry by name or index
            entry = None
            try:
                index = int(args.entry) - 1
                if 0 <= index < len(binder.entries):
                    entry = binder.entries[index]
            except ValueError:
                for e in binder.entries:
                    if e.name == args.entry:
                        entry = e
                        break
            
            if entry:
                content = self._entry_to_text(entry)
                if args.output:
                    with open(args.output, 'w') as f:
                        f.write(content)
                    print(f"✓ Extracted to {args.output}")
                else:
                    print(content)
                return 0
            else:
                print(f"Entry '{args.entry}' not found")
                return 1
        
        # Extract all
        all_content = []
        if binder.entries:
            for entry in binder.entries:
                all_content.append(f"# {entry.name}\n")
                all_content.append(self._entry_to_text(entry))
                all_content.append("\n")
        
        if binder.resources:
            for res in binder.resources:
                all_content.append(f"# Resource: {res.resource_type}\n")
                all_content.append(f"Source: {res.source}\n")
                all_content.append(f"Data: {res.data}\n\n")
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(''.join(all_content))
            print(f"✓ Extracted all content to {args.output}")
        else:
            print(''.join(all_content))
        
        return 0
    
    def _entry_to_text(self, entry) -> str:
        """Convert entry to text representation"""
        lines = []
        lines.append(f"Name: {entry.name}")
        lines.append(f"Type: {entry.entry_type}")
        if entry.description:
            lines.append(f"Description: {entry.description}")
        if entry.data:
            lines.append(f"Data: {json.dumps(entry.data, indent=2)}")
        if entry.entries:
            lines.append(f"Sub-entries: {len(entry.entries)}")
            for sub in entry.entries:
                lines.append(f"  - {sub.name}")
        if entry.resources:
            lines.append(f"Resources: {len(entry.resources)}")
            for res in entry.resources:
                lines.append(f"  - {res.resource_type}: {res.source}")
        return '\n'.join(lines)
    
    def _command_pack(self, args):
        """Pack content into a binder"""
        parser = argparse.ArgumentParser(description='Pack content into binder')
        parser.add_argument('binder_id', type=str, help='Target binder ID')
        parser.add_argument('--name', '-n', type=str, required=True, help='Entry name')
        parser.add_argument('--type', '-t', type=str, default='content', help='Entry type')
        parser.add_argument('--description', '-d', type=str, help='Description')
        parser.add_argument('--file', '-f', type=str, help='File to pack')
        parser.add_argument('--data', type=str, help='Data to pack (JSON)')
        parser.add_argument('--text', type=str, help='Text content to pack')
        
        args = parser.parse_args(args)
        
        try:
            binder = self.registry.load_binder(args.binder_id)
        except:
            # Create new binder if doesn't exist
            metadata = BinderMetadata(
                id=args.binder_id,
                title=args.binder_id.replace('_', ' ').title(),
                version='1.0.0'
            )
            binder = Binder(metadata=metadata)
        
        # Create entry
        entry = BinderEntry(
            name=args.name,
            entry_type=args.type,
            description=args.description
        )
        
        # Add data (Binder uses value, not data)
        if args.file:
            file_path = Path(args.file)
            if file_path.exists():
                from core_py import BinderResource
                resource = BinderResource(
                    id=f"res-{len(entry.resources)}",
                    name=file_path.stem,
                    resource_type='file',
                    data=file_path.read_text(),
                    path=str(file_path)
                )
                entry.resources.append(resource)
        
        if args.data:
            try:
                entry.value = json.loads(args.data)
            except:
                entry.value = args.data
        
        if args.text:
            entry.value = args.text
        
        # Add to root entry
        binder.add_entry("root", entry)
        
        # Save
        self.registry.save_binder(binder)
        print(f"✓ Packed '{args.name}' into binder '{args.binder_id}'")
        return 0
    
    def _command_search(self, args):
        """Search within binders"""
        parser = argparse.ArgumentParser(description='Search binders')
        parser.add_argument('query', type=str, help='Search query')
        parser.add_argument('--binder', '-b', type=str, help='Search in specific binder')
        parser.add_argument('--case-sensitive', '-c', action='store_true', help='Case sensitive search')
        parser.add_argument('--name-only', '-n', action='store_true', help='Search in names only')
        
        args = parser.parse_args(args)
        
        if not args.query:
            print("Error: Please provide a search query")
            return 1
        
        binders = self.registry.list_binders() if CORE_PY_AVAILABLE else []
        
        if args.binder:
            binders = [b for b in binders if b.get('id') == args.binder]
        
        results = []
        query = args.query if args.case_sensitive else args.query.lower()
        
        for binder_info in binders:
            try:
                binder = self.registry.load_binder(binder_info['filename'])
                
                # Search in metadata
                if not args.name_only:
                    if query in (binder.metadata.title or '').lower():
                        results.append((binder, f"Title: {binder.metadata.title}"))
                    if query in (binder.metadata.description or '').lower():
                        results.append((binder, f"Description: {binder.metadata.description}"))
                
                # Search in entries
                for entry in binder.entries:
                    if query in entry.name.lower():
                        results.append((binder, f"Entry: {entry.name}"))
                    if not args.name_only and entry.description:
                        if query in entry.description.lower():
                            results.append((binder, f"Entry description: {entry.name}"))
                    
                    # Search in entry data
                    if not args.name_only and entry.data:
                        data_str = json.dumps(entry.data).lower()
                        if query in data_str:
                            results.append((binder, f"Entry data: {entry.name}"))
                
                # Search in resources
                for res in binder.resources:
                    if query in res.resource_type.lower():
                        results.append((binder, f"Resource type: {res.resource_type}"))
                    if not args.name_only and query in (res.source or '').lower():
                        results.append((binder, f"Resource: {res.source}"))
                        
            except Exception as e:
                print(f"Warning: Error loading {binder_info['filename']}: {e}")
        
        if results:
            print(f"Found {len(results)} matches:")
            for binder, match in results:
                print(f"  [{binder.metadata.id}] {match}")
        else:
            print("No matches found.")
        
        return 0
    
    def _command_tree(self, args):
        """Show hierarchical structure"""
        parser = argparse.ArgumentParser(description='Show binder tree')
        parser.add_argument('binder_id', type=str, help='Binder ID or filename')
        parser.add_argument('--depth', '-d', type=int, default=10, help='Maximum depth')
        parser.add_argument('--compact', '-c', action='store_true', help='Compact display')
        
        args = parser.parse_args(args)
        
        try:
            binder = self.registry.load_binder(args.binder_id)
        except Exception as e:
            print(f"Error: {e}")
            return 1
        
        if args.compact:
            self._print_tree_compact(binder, depth=0, max_depth=args.depth)
        else:
            self._print_tree(binder)
        
        return 0
    
    def _print_tree(self, binder, indent=0, prefix=""):
        """Print binder tree structure"""
        print(f"{prefix}{binder.metadata.name} (v{binder.metadata.version})")
        print(f"{prefix}  ID: {binder.metadata.id}")
        print(f"{prefix}  Checksum: {binder.checksum}")
        
        root = binder.root
        print(f"{prefix}  Root Entry: {root.name} [{root.entry_type}]")
        
        if root.children:
            print(f"{prefix}  Children: {len(root.children)}")
            for i, child in enumerate(root.children):
                entry_prefix = f"{prefix}  {i+1}. " if indent == 0 else f"{prefix}  "
                print(f"{entry_prefix}{child.name} [{child.entry_type}]")
                if child.value:
                    value_preview = str(child.value)[:50] + "..." if len(str(child.value)) > 50 else str(child.value)
                    print(f"{entry_prefix}    Value: {value_preview}")
                if child.resources:
                    print(f"{entry_prefix}    Resources: {len(child.resources)}")
                    for j, res in enumerate(child.resources):
                        print(f"{entry_prefix}      {j+1}. {res.name} ({res.resource_type})")
                if child.children:
                    for j, sub_child in enumerate(child.children):
                        sub_prefix = f"{entry_prefix}    {j+1}. "
                        print(f"{sub_prefix}{sub_child.name} [{sub_child.entry_type}]")
    
    def _print_tree_compact(self, binder, depth=0, max_depth=10, prefix=""):
        """Print compact tree structure"""
        if depth > max_depth:
            return
        
        indent = "  " * depth
        print(f"{indent}{binder.metadata.name}")
        
        root = binder.root
        for i, child in enumerate(root.children):
            is_last = i == len(root.children) - 1
            connector = "└── " if is_last else "├── "
            print(f"{indent}{connector}{child.name} ({child.entry_type})")
            
            if child.children:
                for j, sub_child in enumerate(child.children):
                    is_last_child = j == len(child.children) - 1
                    sub_connector = "└── " if is_last_child else "├── "
                    spacing = "    " if is_last else "│   "
                    print(f"{indent}{spacing}{sub_connector}{sub_child.name}")
        
        if root.resources:
            print(f"{indent}└── Resources: {len(root.resources)}")
    
    def _command_info(self, args):
        """Show binder information"""
        parser = argparse.ArgumentParser(description='Show binder info')
        parser.add_argument('binder_id', type=str, help='Binder ID or filename')
        parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
        parser.add_argument('--yaml', '-y', action='store_true', help='Output as YAML')
        
        args = parser.parse_args(args)
        
        try:
            binder = self.registry.load_binder(args.binder_id)
        except Exception as e:
            print(f"Error: {e}")
            return 1
        
        info = {
            'id': binder.metadata.id,
            'title': binder.metadata.title,
            'version': binder.metadata.version,
            'description': binder.metadata.description,
            'author': binder.metadata.author,
            'created_at': binder.metadata.created_at,
            'updated_at': binder.metadata.updated_at,
            'checksum': binder.checksum,
            'integrity': binder.verify_integrity(),
            'entries': len(binder.entries),
            'resources': len(binder.resources),
            'size': binder.calculate_size()
        }
        
        if args.json:
            print(json.dumps(info, indent=2))
        elif args.yaml:
            print(yaml.dump(info, default_flow_style=False))
        else:
            print(f"Binder Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        
        return 0
    
    def _command_export(self, args):
        """Export binder to other formats"""
        parser = argparse.ArgumentParser(description='Export binder')
        parser.add_argument('binder_id', type=str, help='Binder ID or filename')
        parser.add_argument('--format', '-f', choices=['json', 'yaml', 'usxd'], default='json', help='Export format')
        parser.add_argument('--output', '-o', type=str, help='Output file path')
        
        args = parser.parse_args(args)
        
        try:
            binder = self.registry.load_binder(args.binder_id)
        except Exception as e:
            print(f"Error: {e}")
            return 1
        
        # Export based on format
        if args.format == 'json':
            content = binder.to_json()
        elif args.format == 'yaml':
            content = binder.to_yaml()
        elif args.format == 'usxd':
            # Convert to USXD
            content = self._binder_to_usxd(binder)
        else:
            print(f"Unsupported format: {args.format}")
            return 1
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(content)
            print(f"✓ Exported to {args.output}")
        else:
            print(content)
        
        return 0
    
    def _binder_to_usxd(self, binder) -> str:
        """Convert binder to USXD format"""
        metadata = USXDMetadata(
            id=binder.metadata.id,
            title=binder.metadata.title,
            version=binder.metadata.version,
            description=binder.metadata.description or f"USXD export of {binder.metadata.title}",
            author=binder.metadata.author,
            created_at=binder.metadata.created_at
        )
        
        doc = USXDDocument(metadata=metadata)
        
        # Add metadata section
        metadata_section = USXDSection(
            id='binder_metadata',
            name='Binder Metadata',
            section_type='metadata',
            content={
                'original_type': 'binder',
                'checksum': binder.checksum,
                'integrity': binder.verify_integrity()
            }
        )
        doc.add_section(metadata_section)
        
        # Add entries as sections
        for i, entry in enumerate(binder.entries):
            entry_section = USXDSection(
                id=f'entry_{i}',
                name=entry.name,
                section_type='content',
                content={
                    'type': entry.entry_type,
                    'description': entry.description,
                    'data': entry.data,
                    'resources': len(entry.resources)
                }
            )
            doc.add_section(entry_section)
        
        return doc.to_json()
    
    def _command_import(self, args):
        """Import content into binder"""
        parser = argparse.ArgumentParser(description='Import into binder')
        parser.add_argument('binder_id', type=str, help='Target binder ID')
        parser.add_argument('--file', '-f', type=str, required=True, help='File to import (JSON, YAML, USXD)')
        parser.add_argument('--as-entry', '-e', type=str, help='Import as entry name')
        parser.add_argument('--replace', '-r', action='store_true', help='Replace existing content')
        
        args = parser.parse_args(args)
        
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found")
            return 1
        
        try:
            # Try to load as binder first
            try:
                import_binder = self.registry.load_binder_from_file(file_path)
                # This is a binder - merge or import entries
                if args.binder_id == import_binder.metadata.id:
                    print("Error: Cannot import binder into itself")
                    return 1
                
                target_binder = self.registry.load_binder(args.binder_id)
                
                # Import entries
                for entry in import_binder.entries:
                    if args.as_entry:
                        entry.name = args.as_entry
                    target_binder.add_entry(entry)
                
                self.registry.save_binder(target_binder)
                print(f"✓ Imported {len(import_binder.entries)} entries from '{args.file}'")
                return 0
                
            except:
                # Try as USXD
                try:
                    from core_py import USXDDocument
                    content = file_path.read_text()
                    doc = USXDDocument.from_json(content)
                    
                    # Convert USXD to binder entry
                    binder = self.registry.load_binder(args.binder_id)
                    
                    entry = BinderEntry(
                        name=args.as_entry or doc.metadata.title,
                        entry_type='usxd',
                        description=doc.metadata.description,
                        data={'usxd_document': doc.to_dict()}
                    )
                    
                    binder.add_entry(entry)
                    self.registry.save_binder(binder)
                    print(f"✓ Imported USXD document as entry '{entry.name}'")
                    return 0
                    
                except:
                    # Try as generic data
                    content = file_path.read_text()
                    
                    try:
                        # Try JSON
                        data = json.loads(content)
                    except:
                        # Use raw text
                        data = {'text': content}
                    
                    binder = self.registry.load_binder(args.binder_id)
                    entry = BinderEntry(
                        name=args.as_entry or file_path.stem,
                        entry_type='data',
                        data=data
                    )
                    
                    binder.add_entry(entry)
                    self.registry.save_binder(binder)
                    print(f"✓ Imported file as entry '{entry.name}'")
                    return 0
                    
        except Exception as e:
            print(f"Error: {e}")
            return 1


# Main entry point
def main():
    """Main entry point"""
    cli = BinderCLI()
    return cli.main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
