#!/usr/bin/env python3
"""
uCode1 USXD CLI - Standalone command-line interface for USXD management

This CLI provides full USXD management capabilities including ASCII grid
parsing, component mapping, and rendering.

Usage:
  usxd [COMMAND] [OPTIONS]

Commands:
  list        List available USXD documents
  show        Show details of a specific USXD document
  create      Create a new USXD document
  validate    Validate a USXD document
  parse       Parse ASCII grid text into USXD
  render      Render USXD document or ASCII grid
  map         Map USXD to ThinUI components
  export      Export USXD to other formats
  import      Import content into USXD
  grid        Grid-specific commands
  cell        Cell archiving and linking for USXD documents
  help        Show help for a command

Grid Subcommands (usxd grid):
  parse       Parse ASCII grid text
  render      Render ASCII grid
  to-usxd     Convert ASCII grid to USXD document
  interactive Run interactive grid viewer

Examples:
  usxd list
  usxd show DOCUMENT_ID
  usxd create NEW_DOC --title "My Document"
  usxd validate doc.usxd
  usxd parse --text "┌───┐\n│ A │\n└───┘" --title "My Grid"
  usxd render my_grid.txt
  usxd grid parse "┌───┐\n│ A │\n└───┘"
  usxd grid render my_grid.txt
  usxd grid to-usxd my_grid.txt --output my_doc.usxd
  usxd grid interactive my_grid.txt
"""

import sys
import os
import argparse
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Add core_py to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from core_py import (
        USXDDocument, USXDMetadata, USXDSection, USXDRegistry, USXDFormat,
        Binder, BinderEntry
    )
    CORE_PY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: core_py not available: {e}")
    print("USXD CLI functionality will be limited.")
    CORE_PY_AVAILABLE = False

try:
    from core_py.usxd import (
        ASCIIGridParser, ParsedGrid, GridComponent, GridCell, GridFormat,
        ComponentMapper, ComponentMapping, ComponentType, ThinUIProperties,
        GridRenderer, Style, ColorMode, TerminalUI
    )
    USXD_EXT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: USXD extensions not available: {e}")
    USXD_EXT_AVAILABLE = False
    ASCIIGridParser = None
    ComponentMapper = None
    GridRenderer = None


class USXDCLI:
    """Command-line interface for USXD management"""
    
    def __init__(self):
        self.registry = USXDRegistry() if CORE_PY_AVAILABLE else None
        self.registry_dir = Path(".usxd")
        self.parser = ASCIIGridParser() if USXD_EXT_AVAILABLE else None
        self.mapper = ComponentMapper() if USXD_EXT_AVAILABLE else None
        self.renderer = GridRenderer() if USXD_EXT_AVAILABLE else None
        
        # Ensure registry directory exists
        self.registry_dir.mkdir(exist_ok=True)
    
    def main(self, args):
        """Main entry point for USXD CLI"""
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
            elif command == "parse":
                return self._command_parse(args[1:])
            elif command == "render":
                return self._command_render(args[1:])
            elif command == "map":
                return self._command_map(args[1:])
            elif command == "export":
                return self._command_export(args[1:])
            elif command == "import":
                return self._command_import(args[1:])
            elif command == "grid":
                return self._command_grid(args[1:])
            elif command == "cell":
                return self._command_cell(args[1:])
            elif command == "help" or command == "--help" or command == "-h":
                self._print_help()
                return 0
            else:
                print(f"Unknown command: {command}")
                self._print_help()
                return 1
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    def _print_help(self):
        """Print help message"""
        print(__doc__)
    
    def _command_list(self, args):
        """List available USXD documents"""
        parser = argparse.ArgumentParser(description='List available USXD documents')
        parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
        parser.add_argument('--filter', '-f', type=str, help='Filter by title or ID')
        parser.add_argument('--sort', '-s', choices=['name', 'date', 'size'], default='name', help='Sort order')
        
        args = parser.parse_args(args)
        
        if not CORE_PY_AVAILABLE:
            print("Error: core_py not available")
            return 1
        
        docs = self.registry.list_documents()
        
        print("Available USXD Documents:")
        print("-" * 60)
        
        if not docs:
            print("No documents found.")
            return 0
        
        # Filter
        if args.filter:
            docs = [d for d in docs if 
                    args.filter.lower() in d.get('title', '').lower() or 
                    args.filter.lower() in d.get('id', '').lower()]
        
        # Sort
        if args.sort == 'date':
            docs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif args.sort == 'size':
            docs.sort(key=lambda x: x.get('size', 0), reverse=True)
        else:
            docs.sort(key=lambda x: x.get('title', ''))
        
        for doc in docs:
            doc_id = doc.get('id', 'unknown')
            title = doc.get('title', 'Untitled')
            version = doc.get('version', '1.0')
            size = doc.get('size', 0)
            format_type = doc.get('format', 'json')
            
            if args.verbose:
                print(f"  ID: {doc_id}")
                print(f"  Title: {title}")
                print(f"  Version: {version}")
                print(f"  Format: {format_type}")
                print(f"  Size: {size} bytes")
                print(f"  Checksum: {doc.get('checksum', 'N/A')}")
                print()
            else:
                display_title = title[:40] + "..." if len(title) > 40 else title
                print(f"  {doc_id:20} | {display_title:40} | v{version:5} | {format_type:6} | {size:8} bytes")
        
        print("-" * 60)
        print(f"Total: {len(docs)} documents")
        return 0
    
    def _command_show(self, args):
        """Show details of a specific USXD document"""
        parser = argparse.ArgumentParser(description='Show USXD document details')
        parser.add_argument('doc_id', type=str, nargs='?', help='Document ID or filename')
        parser.add_argument('--section', '-s', type=str, help='Show specific section')
        parser.add_argument('--tree', '-t', action='store_true', help='Show as tree structure')
        parser.add_argument('--raw', '-r', action='store_true', help='Show raw content')
        parser.add_argument('--format', '-f', choices=['json', 'yaml'], default='json', help='Output format')
        
        args = parser.parse_args(args)
        
        if not CORE_PY_AVAILABLE:
            print("Error: core_py not available")
            return 1
        
        if not args.doc_id:
            print("Error: Please specify a document ID or filename")
            return 1
        
        try:
            doc = self.registry.load_document(args.doc_id)
        except FileNotFoundError:
            try:
                doc = USXDDocument.load_from_file(Path(args.doc_id))
            except Exception as e:
                print(f"Error: Document '{args.doc_id}' not found")
                return 1
        
        if args.raw:
            if args.format == 'yaml':
                print(doc.to_yaml())
            else:
                print(doc.to_json())
            return 0
        
        print(f"USXD Document: {doc.metadata.title}")
        print(f"ID: {doc.metadata.id}")
        print(f"Version: {doc.metadata.version}")
        print(f"Description: {doc.metadata.description or 'N/A'}")
        print(f"Author: {doc.metadata.author or 'N/A'}")
        print(f"Created: {doc.metadata.created_at}")
        print(f"Updated: {doc.metadata.updated_at}")
        print(f"Format: {doc.metadata.format.value}")
        print(f"Checksum: {doc.checksum}")
        print(f"Integrity: {'✓ Valid' if doc.verify_integrity() else '✗ Invalid'}")
        print()
        
        if args.section:
            section = doc.get_section(args.section)
            if section:
                print(f"Section: {section.name}")
                print(f"Type: {section.section_type}")
                if section.content is not None:
                    if isinstance(section.content, str):
                        print(f"Content: {section.content}")
                    else:
                        print(f"Content: {json.dumps(section.content, indent=2)}")
            else:
                print(f"Section '{args.section}' not found")
            return 0
        
        if args.tree:
            self._print_tree(doc)
            return 0
        
        print(f"Sections: {len(doc.sections)}")
        for i, section in enumerate(doc.sections):
            print(f"  {i+1}. {section.name} ({section.section_type})")
            if section.content is not None:
                if isinstance(section.content, str):
                    content_preview = section.content[:100] + "..." if len(section.content) > 100 else section.content
                    print(f"      {content_preview}")
        
        return 0
    
    def _command_create(self, args):
        """Create a new USXD document"""
        parser = argparse.ArgumentParser(description='Create a new USXD document')
        parser.add_argument('id', type=str, help='Document ID')
        parser.add_argument('--title', '-t', type=str, default='Untitled', help='Document title')
        parser.add_argument('--version', '-v', type=str, default='1.0.0', help='Version')
        parser.add_argument('--description', '-d', type=str, help='Description')
        parser.add_argument('--author', '-a', type=str, help='Author')
        parser.add_argument('--format', '-f', choices=['json', 'yaml'], default='json', help='File format')
        parser.add_argument('--from-file', type=str, help='Create from file')
        parser.add_argument('--from-grid', type=str, help='Create from ASCII grid file')
        
        args = parser.parse_args(args)
        
        if not CORE_PY_AVAILABLE:
            print("Error: core_py not available")
            return 1
        
        if args.from_file:
            file_path = Path(args.from_file)
            if not file_path.exists():
                print(f"Error: File '{args.from_file}' not found")
                return 1
            
            try:
                content = file_path.read_text()
                try:
                    data = json.loads(content)
                except:
                    try:
                        data = yaml.safe_load(content)
                    except:
                        print("Error: File is not valid JSON or YAML")
                        return 1
                
                doc = USXDDocument.from_dict(data)
                filepath = self.registry.save_document(doc)
                print(f"✓ Created USXD document from '{args.from_file}'")
                print(f"  ID: {doc.metadata.id}")
                print(f"  Title: {doc.metadata.title}")
                return 0
            except Exception as e:
                print(f"Error: {e}")
                return 1
        
        # Create new document
        metadata = USXDMetadata(
            id=args.id,
            title=args.title,
            version=args.version,
            description=args.description,
            author=args.author,
            format=USXDFormat(args.format)
        )
        
        doc = USXDDocument(metadata=metadata)
        
        if args.from_grid:
            grid_text = Path(args.from_grid).read_text()
            parsed_grid = self.parser.parse_grid(grid_text, args.title)
            
            # Add grid as section
            from core_py.usxd.component_mapper import ComponentMapper
            mapper = ComponentMapper()
            layout = mapper.create_grid_layout(parsed_grid)
            
            section = USXDSection(
                id='grid_layout',
                name='Grid Layout',
                section_type='data',
                content=layout,
                format='application/x-usxd-grid-layout'
            )
            doc.add_section(section)
            
            # Add raw grid as section
            grid_section = USXDSection(
                id='raw_grid',
                name='Raw Grid Text',
                section_type='content',
                content=grid_text
            )
            doc.add_section(grid_section)
            
            print(f"✓ Created USXD document with embedded grid from '{args.from_grid}'")
        
        filepath = self.registry.save_document(doc)
        print(f"✓ Created USXD document: {doc.metadata.title}")
        print(f"  ID: {doc.metadata.id}")
        print(f"  Saved to: {filepath}")
        
        return 0
    
    def _command_validate(self, args):
        """Validate a USXD document"""
        parser = argparse.ArgumentParser(description='Validate USXD document')
        parser.add_argument('doc_id', type=str, help='Document ID or filename')
        parser.add_argument('--strict', '-s', action='store_true', help='Strict validation')
        
        args = parser.parse_args(args)
        
        if not CORE_PY_AVAILABLE:
            print("Error: core_py not available")
            return 1
        
        try:
            doc = self.registry.load_document(args.doc_id)
        except:
            try:
                doc = USXDDocument.load_from_file(Path(args.doc_id))
            except Exception as e:
                print(f"Error: {e}")
                return 1
        
        errors = []
        
        if not doc.metadata.id:
            errors.append("Missing ID")
        if not doc.metadata.title:
            errors.append("Missing title")
        if not doc.verify_integrity():
            errors.append("Checksum mismatch - data may be corrupted")
        
        if errors:
            print("❌ Validation Failed:")
            for error in errors:
                print(f"  - {error}")
            return 1
        else:
            print("✅ Validation Passed")
            print(f"  ID: {doc.metadata.id}")
            print(f"  Title: {doc.metadata.title}")
            print(f"  Checksum: {doc.checksum}")
            print(f"  Sections: {len(doc.sections)}")
            return 0
    
    def _command_parse(self, args):
        """Parse ASCII grid text into USXD"""
        if not USXD_EXT_AVAILABLE:
            print("Error: USXD extensions not available")
            return 1
        
        parser = argparse.ArgumentParser(description='Parse ASCII grid')
        parser.add_argument('--text', '-t', type=str, help='ASCII grid text to parse')
        parser.add_argument('--file', '-f', type=str, help='File containing ASCII grid')
        parser.add_argument('--title', type=str, default='Parsed Grid', help='Grid title')
        parser.add_argument('--output', '-o', type=str, help='Output file (USXD format)')
        parser.add_argument('--render', '-r', action='store_true', help='Render parsed grid')
        parser.add_argument('--components', '-c', action='store_true', help='Show detected components')
        
        args = parser.parse_args(args)
        
        if not args.text and not args.file:
            print("Error: Please provide --text or --file")
            return 1
        
        grid_text = args.text or Path(args.file).read_text()
        parsed_grid = self.parser.parse_grid(grid_text, args.title)
        
        print(f"✓ Parsed ASCII grid: {parsed_grid.rows}x{parsed_grid.cols}")
        print(f"  Title: {parsed_grid.title}")
        print(f"  Format: {parsed_grid.format.value}")
        
        if args.components:
            print(f"  Components: {len(parsed_grid.components)}")
            for comp_id, comp in parsed_grid.components.items():
                print(f"    - {comp_id}: {comp.name} ({len(comp.cells)} cells)")
        
        if args.render:
            rendered = self.renderer.render(parsed_grid)
            print("\nRendered:")
            print(rendered)
        
        if args.output:
            # Create USXD document
            metadata = USXDMetadata(
                id=f"grid-{int(time.time())}",
                title=args.title,
                version='1.0.0',
                description='ASCII grid parsed document',
                format=USXDFormat.JSON
            )
            doc = USXDDocument(metadata=metadata)
            
            # Add parsed grid as section
            structured = self.parser.to_structured(parsed_grid)
            section = USXDSection(
                id='parsed_grid',
                name='Parsed Grid',
                section_type='data',
                content=structured,
                format='application/x-usxd-grid'
            )
            doc.add_section(section)
            
            # Add raw text as section
            raw_section = USXDSection(
                id='raw_text',
                name='Raw Text',
                section_type='content',
                content=grid_text
            )
            doc.add_section(raw_section)
            
            filepath = self.registry.save_document(doc, filename=args.output)
            print(f"✓ Saved to USXD: {filepath}")
        
        return 0
    
    def _command_render(self, args):
        """Render USXD document or ASCII grid"""
        if not USXD_EXT_AVAILABLE:
            print("Error: USXD extensions not available")
            return 1
        
        parser = argparse.ArgumentParser(description='Render USXD or grid')
        parser.add_argument('input', type=str, nargs='?', help='USXD document or grid file')
        parser.add_argument('--text', '-t', type=str, help='ASCII grid text to render')
        parser.add_argument('--title', type=str, help='Title override')
        parser.add_argument('--no-color', action='store_true', help='Disable colors')
        parser.add_argument('--interactive', '-i', action='store_true', help='Enable interactive mode')
        
        args = parser.parse_args(args)
        
        if not args.input and not args.text:
            print("Error: Please provide input file or --text")
            return 1
        
        # Try to parse as USXD document first
        parsed_grid = None
        
        if args.input:
            input_path = Path(args.input)
            if input_path.exists():
                content = input_path.read_text()
                
                # Try as USXD
                try:
                    doc = USXDDocument.load_from_file(input_path)
                    # Extract grid from USXD if available
                    for section in doc.sections:
                        if section.section_type == 'data':
                            parsed_grid = self.parser.to_grid(section.content)
                            break
                except:
                    pass
                
                # Try as ASCII grid
                if parsed_grid is None:
                    try:
                        parsed_grid = self.parser.parse_grid(content, args.title)
                    except Exception as e:
                        print(f"Error parsing: {e}")
                        return 1
            else:
                print(f"Error: File '{args.input}' not found")
                return 1
        elif args.text:
            parsed_grid = self.parser.parse_grid(args.text, args.title)
        
        if parsed_grid is None:
            print("Error: Could not parse input as grid")
            return 1
        
        if args.no_color:
            self.renderer.config.color_mode = ColorMode.NONE
        
        if args.interactive:
            self.renderer.run_interactive(parsed_grid, title=args.title or parsed_grid.title)
        else:
            rendered = self.renderer.render(parsed_grid, title=args.title)
            print(rendered)
        
        return 0
    
    def _command_map(self, args):
        """Map USXD to ThinUI components"""
        if not USXD_EXT_AVAILABLE:
            print("Error: USXD extensions not available")
            return 1
        
        parser = argparse.ArgumentParser(description='Map USXD to ThinUI')
        parser.add_argument('input', type=str, nargs='?', help='USXD document or grid file')
        parser.add_argument('--text', '-t', type=str, help='ASCII grid text to map')
        parser.add_argument('--title', type=str, help='Title override')
        parser.add_argument('--format', '-f', choices=['json', 'yaml', 'html'], default='json', help='Output format')
        parser.add_argument('--layout', '-l', choices=['grid', 'teletext', 'flex'], default='grid', help='Layout type')
        parser.add_argument('--output', '-o', type=str, help='Output file')
        
        args = parser.parse_args(args)
        
        if not args.input and not args.text:
            print("Error: Please provide input file or --text")
            return 1
        
        # Parse input
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Error: File '{args.input}' not found")
                return 1
            
            content = input_path.read_text()
            
            # Try as USXD
            try:
                doc = USXDDocument.load_from_file(input_path)
                # Try to find grid data in sections
                parsed_grid = None
                for section in doc.sections:
                    if section.content and isinstance(section.content, dict):
                        if section.content.get('type') == 'grid':
                            parsed_grid = self.parser.to_grid(section.content)
                            break
                
                if parsed_grid is None:
                    # Try to parse as ASCII grid
                    parsed_grid = self.parser.parse_grid(content, args.title)
            except:
                # Try as ASCII grid
                try:
                    parsed_grid = self.parser.parse_grid(content, args.title)
                except Exception as e:
                    print(f"Error: {e}")
                    return 1
        elif args.text:
            parsed_grid = self.parser.parse_grid(args.text, args.title)
        
        if parsed_grid is None:
            print("Error: Could not parse input as grid")
            return 1
        
        # Map to layout
        layout = self.mapper.map_to_layout(parsed_grid, args.layout)
        
        # Output
        if args.format == 'json':
            output = json.dumps(layout, indent=2)
        elif args.format == 'yaml':
            output = yaml.dump(layout, default_flow_style=False)
        elif args.format == 'html':
            output = self.mapper.map_to_html(parsed_grid, args.layout)
        else:
            output = json.dumps(layout, indent=2)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✓ Mapped and saved to {args.output}")
        else:
            print(output)
        
        return 0
    
    def _command_cell(self, args):
        """Convert USXD sections to/from Cells for archiving."""
        parser = argparse.ArgumentParser(description='Cell mapping for USXD documents')
        sub = parser.add_subparsers(dest="cell_cmd")

        ap = sub.add_parser("archive", help="Archive all sections as Cells")
        ap.add_argument("doc_id", help="Document ID or .usxd file path")
        ap.add_argument("--band", type=int, default=100, help="Layer band (default: 100)")

        rp = sub.add_parser("restore", help="Restore sections from Cell references")
        rp.add_argument("doc_id", help="Document ID or .usxd file path")

        lp = sub.add_parser("link", help="Link document metadata as a Cell")
        lp.add_argument("doc_id", help="Document ID or .usxd file path")

        sp = sub.add_parser("show", help="Show cell-referenced sections in a document")
        sp.add_argument("doc_id", help="Document ID or .usxd file path")

        parsed = parser.parse_args(args)

        if not CORE_PY_AVAILABLE:
            print("Error: core_py not available")
            return 1

        # Load document
        try:
            doc = self.registry.load_document(parsed.doc_id)
        except (FileNotFoundError, Exception):
            try:
                doc = USXDDocument.load_from_file(Path(parsed.doc_id))
            except Exception as e:
                print(f"Error: cannot load document '{parsed.doc_id}'")
                return 1

        from core_py.usxd.cell_mapping import (
            archive_document_sections,
            add_cell_references_to_doc,
            restore_sections_from_cells,
            link_doc_to_cell_address,
        )
        from core_py.cell import CellStore

        store = CellStore()

        if parsed.cell_cmd == "archive":
            mapping = archive_document_sections(doc, store, band=parsed.band)
            add_cell_references_to_doc(doc, mapping)

            # Save updated document with cell refs
            filepath = self.registry.save_document(doc)
            print(f"✅ Archived {len(mapping)} sections as Cells")
            print(f"   Updated document: {filepath}")
            for sid, addr in mapping.items():
                print(f"     {sid:30s} → {addr}")

        elif parsed.cell_cmd == "restore":
            cell_ref_section = None
            for s in doc.sections:
                if s.section_type == "cell-reference":
                    cell_ref_section = s
                    break
            if not cell_ref_section:
                print("❌ No cell-reference section found in document.")
                print("   Use 'usxd cell archive' first.")
                return 1

            refs = cell_ref_section.content if isinstance(cell_ref_section.content, list) else []
            if not refs:
                print("No cell references to restore.")
                return 1

            restored = restore_sections_from_cells(refs, store)
            for s in restored:
                doc.add_section(s)
                print(f"   Restored: {s.name} ({s.section_type})")

            filepath = self.registry.save_document(doc)
            print(f"✅ Restored {len(restored)} sections from Cells")
            print(f"   Updated document: {filepath}")

        elif parsed.cell_cmd == "link":
            addr = link_doc_to_cell_address(doc, store, band=100)
            print(f"✅ Document linked to Cell: {addr}")
            print(f"   ucode cell read {addr}")

        elif parsed.cell_cmd == "show":
            cell_count = 0
            for s in doc.sections:
                if s.section_type == "cell-reference":
                    refs = s.content if isinstance(s.content, list) else []
                    cell_count = len(refs)
                    print(f"📎 Cell references ({cell_count}):")
                    for ref in refs:
                        cell = store.read(ref.get("cell_address", ""))
                        status = "✅" if cell else "❌"
                        print(f"   {status} {ref.get('section_id','?'):30s} → {ref.get('cell_address','?')}")
            if cell_count == 0:
                print("No cell references found in this document.")
            doc_addr = link_doc_to_cell_address.__doc__  # not actually linking
            print(f"\nDocument sections: {len(doc.sections)}")

        else:
            parser.print_help()
        return 0

    def _command_grid(self, args):
        """Grid-specific commands"""
        if len(args) < 1:
            self._print_grid_help()
            return 0
        
        subcommand = args[0]
        
        if subcommand == "parse":
            return self._grid_command_parse(args[1:])
        elif subcommand == "render":
            return self._grid_command_render(args[1:])
        elif subcommand == "to-usxd":
            return self._grid_command_to_usxd(args[1:])
        elif subcommand == "interactive":
            return self._grid_command_interactive(args[1:])
        elif subcommand == "help" or subcommand == "--help" or subcommand == "-h":
            self._print_grid_help()
            return 0
        else:
            print(f"Unknown grid subcommand: {subcommand}")
            self._print_grid_help()
            return 1
    
    def _print_grid_help(self):
        """Print grid command help"""
        grid_help = """
Grid Commands (usxd grid):
  parse       Parse ASCII grid text
  render      Render ASCII grid (static)
  to-usxd     Convert ASCII grid to USXD document
  interactive Run interactive grid viewer

Usage:
  usxd grid parse [--text TEXT] [--file FILE] [--title TITLE] [--render]
  usxd grid render FILE [--title TITLE] [--no-color]
  usxd grid to-usxd FILE --output OUTPUT.usxd
  usxd grid interactive FILE
"""
        print(grid_help)
    
    def _grid_command_parse(self, args):
        """Grid parse command"""
        if not USXD_EXT_AVAILABLE:
            print("Error: USXD extensions not available")
            return 1
        
        parser = argparse.ArgumentParser(description='Parse ASCII grid')
        parser.add_argument('--text', '-t', type=str, help='ASCII grid text')
        parser.add_argument('--file', '-f', type=str, help='File containing ASCII grid')
        parser.add_argument('--title', type=str, default='Parsed Grid', help='Title')
        parser.add_argument('--render', '-r', action='store_true', help='Render the parsed grid')
        parser.add_argument('--components', '-c', action='store_true', help='Show components')
        parser.add_argument('--auto-components', '-a', action='store_true', help='Auto-detect components')
        
        args = parser.parse_args(args)
        
        if not args.text and not args.file:
            print("Error: Please provide --text or --file")
            return 1
        
        grid_text = args.text or Path(args.file).read_text()
        parsed_grid = self.parser.parse_grid(grid_text, args.title)
        
        print(f"✓ Parsed grid: {parsed_grid.rows}x{parsed_grid.cols}")
        print(f"  Format: {parsed_grid.format.value}")
        
        if args.auto_components:
            components = self.parser.split_into_components(grid_text)
            print(f"  Auto-detected components: {len(components)}")
            for comp in components:
                print(f"    - {comp['id']}: {comp['name']} ({comp['size']} cells)")
        
        if args.components:
            print(f"  Manual components: {len(parsed_grid.components)}")
            for comp_id, comp in parsed_grid.components.items():
                print(f"    - {comp_id}: {comp.name}")
        
        if args.render:
            rendered = self.renderer.render(parsed_grid, args.title)
            print("\nRendered:")
            print(rendered)
        
        return 0
    
    def _grid_command_render(self, args):
        """Grid render command"""
        if not USXD_EXT_AVAILABLE:
            print("Error: USXD extensions not available")
            return 1
        
        parser = argparse.ArgumentParser(description='Render ASCII grid')
        parser.add_argument('file', type=str, nargs='?', help='File to render')
        parser.add_argument('--text', '-t', type=str, help='ASCII grid text')
        parser.add_argument('--title', type=str, help='Title')
        parser.add_argument('--no-color', action='store_true', help='No colors')
        parser.add_argument('--focus', type=str, help='Focus position (row,col)')
        
        args = parser.parse_args(args)
        
        if not args.file and not args.text:
            print("Error: Please provide file or --text")
            return 1
        
        grid_text = None
        if args.file:
            grid_text = Path(args.file).read_text()
        elif args.text:
            grid_text = args.text
        
        parsed_grid = self.parser.parse_grid(grid_text, args.title)
        
        if args.no_color:
            self.renderer.config.color_mode = ColorMode.NONE
        
        # Parse focus position
        focused_cell = None
        if args.focus:
            try:
                row, col = map(int, args.focus.split(','))
                focused_cell = (row, col)
            except:
                print("Warning: Invalid focus position")
        
        rendered = self.renderer.render(parsed_grid, args.title, focused_cell)
        print(rendered)
        
        return 0
    
    def _grid_command_to_usxd(self, args):
        """Convert ASCII grid to USXD"""
        if not CORE_PY_AVAILABLE or not USXD_EXT_AVAILABLE:
            print("Error: Required modules not available")
            return 1
        
        parser = argparse.ArgumentParser(description='Convert grid to USXD')
        parser.add_argument('file', type=str, help='ASCII grid file')
        parser.add_argument('--title', '-t', type=str, help='USXD document title')
        parser.add_argument('--output', '-o', type=str, required=True, help='Output USXD file')
        parser.add_argument('--with-mapping', '-m', action='store_true', help='Include component mapping')
        
        args = parser.parse_args(args)
        
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found")
            return 1
        
        grid_text = file_path.read_text()
        grid_title = args.title or file_path.stem.replace('_', ' ').title()
        parsed_grid = self.parser.parse_grid(grid_text, grid_title)
        
        # Create USXD document
        metadata = USXDMetadata(
            id=f"doc-{file_path.stem}-{int(time.time())}",
            title=grid_title,
            version='1.0.0',
            description=f'ASCII grid converted to USXD: {file_path.name}',
            format=USXDFormat.JSON
        )
        
        doc = USXDDocument(metadata=metadata)
        
        # Add parsed grid
        structured = self.parser.to_structured(parsed_grid)
        grid_section = USXDSection(
            id='parsed_grid',
            name='Parsed Grid',
            section_type='data',
            content=structured,
            format='application/x-usxd-grid'
        )
        doc.add_section(grid_section)
        
        # Add raw text
        raw_section = USXDSection(
            id='raw_text',
            name='Raw ASCII Text',
            section_type='content',
            content=grid_text
        )
        doc.add_section(raw_section)
        
        # Add component mapping if requested
        if args.with_mapping:
            layout = self.mapper.create_grid_layout(parsed_grid)
            mapping_section = USXDSection(
                id='thinui_mapping',
                name='ThinUI Component Mapping',
                section_type='data',
                content=layout,
                format='application/x-usxd-thinui-layout'
            )
            doc.add_section(mapping_section)
        
        # Save
        output_path = Path(args.output)
        doc.save_to_file(output_path)
        
        print(f"✓ Converted to USXD: {output_path}")
        print(f"  ID: {doc.metadata.id}")
        print(f"  Title: {doc.metadata.title}")
        print(f"  Sections: {len(doc.sections)}")
        
        return 0
    
    def _grid_command_interactive(self, args):
        """Interactive grid viewer"""
        if not USXD_EXT_AVAILABLE:
            print("Error: USXD extensions not available")
            return 1
        
        parser = argparse.ArgumentParser(description='Interactive grid viewer')
        parser.add_argument('file', type=str, nargs='?', help='ASCII grid file')
        parser.add_argument('--text', '-t', type=str, help='ASCII grid text')
        parser.add_argument('--title', type=str, help='Title override')
        
        args = parser.parse_args(args)
        
        if not args.file and not args.text:
            print("Error: Please provide file or --text")
            return 1
        
        grid_text = None
        if args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: File '{args.file}' not found")
                return 1
            grid_text = file_path.read_text()
        elif args.text:
            grid_text = args.text
        
        parsed_grid = self.parser.parse_grid(grid_text, args.title)
        
        # Run interactive
        print("Interactive Grid Viewer - Press ESC to exit, Arrow keys to navigate")
        self.renderer.run_interactive(parsed_grid, title=args.title or parsed_grid.title)
        
        return 0
    
    def _command_export(self, args):
        """Export USXD to other formats"""
        if not CORE_PY_AVAILABLE:
            print("Error: core_py not available")
            return 1
        
        parser = argparse.ArgumentParser(description='Export USXD document')
        parser.add_argument('doc_id', type=str, help='Document ID or filename')
        parser.add_argument('--format', '-f', choices=['json', 'yaml', 'binder', 'html'], default='json', help='Export format')
        parser.add_argument('--output', '-o', type=str, help='Output file')
        
        args = parser.parse_args(args)
        
        try:
            doc = self.registry.load_document(args.doc_id)
        except:
            try:
                doc = USXDDocument.load_from_file(Path(args.doc_id))
            except Exception as e:
                print(f"Error: {e}")
                return 1
        
        if args.format == 'json':
            content = doc.to_json()
        elif args.format == 'yaml':
            content = doc.to_yaml()
        elif args.format == 'binder':
            content = self._usxd_to_binder(doc)
        elif args.format == 'html':
            if not USXD_EXT_AVAILABLE:
                print("Error: USXD extensions not available for HTML export")
                return 1
            # Try to find grid data
            parsed_grid = None
            for section in doc.sections:
                if section.content and isinstance(section.content, dict):
                    if section.content.get('type') == 'grid':
                        parsed_grid = self.parser.to_grid(section.content)
                        break
            
            if parsed_grid:
                content = self.mapper.map_to_html(parsed_grid)
            else:
                print("Warning: No grid data found in USXD, exporting as JSON")
                content = doc.to_json()
        else:
            content = doc.to_json()
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(content)
            print(f"✓ Exported to {args.output}")
        else:
            print(content)
        
        return 0
    
    def _usxd_to_binder(self, doc) -> str:
        """Convert USXD to Binder format"""
        metadata = BinderMetadata(
            id=doc.metadata.id,
            title=doc.metadata.title,
            version=doc.metadata.version,
            description=doc.metadata.description or f"Binder converted from {doc.metadata.title}",
            author=doc.metadata.author,
            created_at=doc.metadata.created_at
        )
        
        binder = Binder(metadata=metadata)
        
        for section in doc.sections:
            entry = BinderEntry(
                name=section.name,
                entry_type=section.section_type,
                description=section.name if not section.name.startswith('#') else None
            )
            
            if section.content is not None:
                entry.data = section.content
            
            binder.add_entry(entry)
        
        return binder.to_json()
    
    def _command_import(self, args):
        """Import content into USXD"""
        if not CORE_PY_AVAILABLE:
            print("Error: core_py not available")
            return 1
        
        parser = argparse.ArgumentParser(description='Import into USXD')
        parser.add_argument('doc_id', type=str, nargs='?', help='Target document ID (create new if not provided)')
        parser.add_argument('--file', '-f', type=str, required=True, help='File to import')
        parser.add_argument('--title', '-t', type=str, help='Document title')
        parser.add_argument('--as-section', '-s', type=str, help='Import as section name')
        parser.add_argument('--type', type=str, default='content', help='Section type')
        
        args = parser.parse_args(args)
        
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File '{args.file}' not found")
            return 1
        
        content = file_path.read_text()
        
        try:
            # Try JSON
            data = json.loads(content)
        except:
            try:
                # Try YAML
                data = yaml.safe_load(content)
            except:
                data = content
        
        # Create or load document
        if args.doc_id:
            try:
                doc = self.registry.load_document(args.doc_id)
            except:
                print(f"Warning: Document '{args.doc_id}' not found, creating new")
                args.doc_id = None
        
        if not args.doc_id:
            metadata = USXDMetadata(
                id=f"doc-{int(time.time())}",
                title=args.title or file_path.stem.replace('_', ' ').title(),
                version='1.0.0',
                description=f'Imported from {file_path.name}'
            )
            doc = USXDDocument(metadata=metadata)
        
        # Add as section
        section_name = args.as_section or file_path.stem.replace('_', ' ').title()
        section = USXDSection(
            id=f"section-{len(doc.sections)}",
            name=section_name,
            section_type=args.type,
            content=data
        )
        doc.add_section(section)
        
        # Save
        filepath = self.registry.save_document(doc)
        print(f"✓ Imported to USXD: {filepath}")
        return 0


# Import time for timestamp generation
import time

# Main entry point
def main():
    """Main entry point"""
    cli = USXDCLI()
    return cli.main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
