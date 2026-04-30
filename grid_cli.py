#!/usr/bin/env python3
"""
Grid CLI — ASCII grid operations with Monodraw visual editing.

Usage:
  ucode grid parse [--text <ascii> | --file <path>] [--title <title>]
  ucode grid render <file> [--title <title>]
  ucode grid interactive <file>
  ucode grid to-usxd <file> --output <path>
  ucode grid edit [<file>] [--title <title>]
  ucode grid monodraw import <file.monopic> [--output <path>]
  ucode grid monodraw export <file> [--output <path.monopic>]
  ucode grid monodraw install
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core_py.usxd import ASCIIGridParser, GridFormat
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

try:
    from core_py.grid.monodraw import (
        edit_grid_interactive,
        export_grid_to_monopic,
        install_symlink,
        is_monopic_file,
        monopic_to_ascii,
        open_in_monodraw,
    )
    from core_py.grid.monodraw import (
        is_available as monodraw_available,
    )
    MONODRAW_AVAILABLE = True
except ImportError:
    MONODRAW_AVAILABLE = False


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ucode grid", description="ASCII grid operations")
    sub = p.add_subparsers(dest="command")

    gp = sub.add_parser("parse", help="Parse ASCII grid text")
    gp.add_argument("--text", help="ASCII grid text to parse")
    gp.add_argument("--file", help="Read grid from file")
    gp.add_argument("--title", default="Untitled", help="Grid title")
    gp.add_argument("--format", choices=["simple", "box", "markdown", "csv", "teletext"],
                    help="Force grid format (auto-detected if omitted)")

    gr = sub.add_parser("render", help="Render grid to terminal")
    gr.add_argument("file", help="Grid file to render")
    gr.add_argument("--title", default="Grid", help="Grid title")

    gi = sub.add_parser("interactive", help="Run interactive grid viewer (TUI)")
    gi.add_argument("file", nargs="?", help="Grid file to load")

    gu = sub.add_parser("to-usxd", help="Convert grid to USXD document")
    gu.add_argument("file", help="Grid file")
    gu.add_argument("--output", "-o", required=True, help="Output USXD file")

    # ── Monodraw visual editing ──────────────────────────────────────────
    ge = sub.add_parser("edit", help="Edit grid visually in Monodraw.app")
    ge.add_argument("file", nargs="?", help="Grid file to edit (creates new if omitted)")
    ge.add_argument("--title", default="Untitled Grid", help="Grid title")

    gm = sub.add_parser("monodraw", help="Monodraw format conversion tools")
    gm_sub = gm.add_subparsers(dest="monodraw_cmd")

    gmi = gm_sub.add_parser("import", help="Import .monopic file to grid text")
    gmi.add_argument("file", help="Path to .monopic file")
    gmi.add_argument("--output", "-o", help="Output file (stdout if omitted)")

    gme = gm_sub.add_parser("export", help="Export grid text as .monopic file")
    gme.add_argument("file", help="Grid text file to export")
    gme.add_argument("--output", "-o", help="Output .monopic path")

    gms = gm_sub.add_parser("install", help="Install monodraw CLI symlink")

    return p


def cmd_edit(args, parser):
    """Open a grid file in Monodraw for visual editing."""
    if not MONODRAW_AVAILABLE:
        print("Error: monodraw module not available in core_py.grid")
        sys.exit(1)
    if not monodraw_available():
        print("❌ Monodraw not found. Install from https://monodraw.helftone.com/")
        print("   Then run: sudo ln -sf /Applications/Monodraw.app/Contents/Resources/monodraw /usr/local/bin/monodraw")
        sys.exit(1)

    text = None
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: file not found: {args.file}")
            sys.exit(1)
        with open(args.file) as f:
            text = f.read()
        print(f"📄 Loaded {args.file}")

    edited_text, mono_path = edit_grid_interactive(
        text=text, file_path=args.file, title=args.title
    )

    # Parse and display the result
    parsed = parser.parse_grid(edited_text, title=args.title)
    print(f"\n✅ Grid edited — {parsed.rows}×{parsed.cols}")
    print(parsed.to_ascii())

    # Save result alongside original or to temp
    out_path = args.file
    if out_path:
        base, ext = os.path.splitext(out_path)
        out_path = f"{base}_edited{ext}"
        with open(out_path, "w") as f:
            f.write(edited_text)
        print(f"💾 Saved edited grid to: {out_path}")
    else:
        print(f"\n--- Grid Content ---")
        print(edited_text)

    # Cleanup temp monopic
    try:
        os.unlink(mono_path)
        os.rmdir(os.path.dirname(mono_path))
    except OSError:
        pass


def cmd_monodraw_import(args, parser):
    """Import a .monopic file to ASCII grid text."""
    if not os.path.exists(args.file):
        print(f"Error: file not found: {args.file}")
        sys.exit(1)
    if not is_monopic_file(args.file):
        print(f"Warning: {args.file} does not appear to be a valid .monopic file")
        proceed = input("Proceed anyway? [y/N] ").lower()
        if proceed != "y":
            sys.exit(1)

    try:
        ascii_text = monopic_to_ascii(args.file, unicode=True, trim=True)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Parse to validate
    parsed = parser.parse_grid(ascii_text, title=os.path.basename(args.file))

    if args.output:
        with open(args.output, "w") as f:
            f.write(ascii_text)
        print(f"✅ Imported {parsed.rows}×{parsed.cols} grid → {args.output}")
    else:
        print(ascii_text)
        print(f"\n--- {parsed.title} ({parsed.rows}×{parsed.cols}) ---")


def cmd_monodraw_export(args):
    """Export a grid text file as plain text for Monodraw GUI editing."""
    if not os.path.exists(args.file):
        print(f"Error: file not found: {args.file}")
        sys.exit(1)

    with open(args.file) as f:
        text = f.read()

    out = args.output or f"{os.path.splitext(args.file)[0]}_monodraw.txt"
    mono_path = export_grid_to_monopic(text, out)

    print(f"✅ Exported to: {mono_path}")
    print(f"")
    print(f"   📐 Edit workflow:")
    print(f"      1. Open in Monodraw: open -a Monodraw {mono_path}")
    print(f"      2. Edit visually, then File > Save As... → save as .monopic")
    print(f"      3. Import back: ucode grid monodraw import <saved.monopic>")


def main():
    p = build_arg_parser()
    args = p.parse_args()

    if not CORE_AVAILABLE:
        print("Error: core_py modules not available")
        sys.exit(1)

    parser = ASCIIGridParser()

    if args.command == "parse":
        text = args.text
        if args.file:
            with open(args.file) as f:
                text = f.read()
        if not text:
            print("Error: provide --text or --file")
            sys.exit(1)
        parsed = parser.parse_grid(text, title=args.title)
        print(f"Parsed grid: {parsed.rows}×{parsed.cols}")
        print(f"Format: {parsed.format or 'auto-detected'}")
        print(f"Cells: {parsed.rows * parsed.cols}")
        print(parsed.to_ascii())

    elif args.command == "render":
        if not os.path.exists(args.file):
            print(f"Error: file not found: {args.file}")
            sys.exit(1)
        with open(args.file) as f:
            text = f.read()
        parsed = parser.parse_grid(text, title=args.title)
        print(parsed.to_ascii())
        print(f"\n--- {parsed.title} ({parsed.rows}×{parsed.cols}) ---")

    elif args.command == "interactive":
        from core_py.usxd import GridRenderer
        renderer = GridRenderer()
        text = ""
        if args.file and os.path.exists(args.file):
            with open(args.file) as f:
                text = f.read()
        if text:
            parsed = parser.parse_grid(text)
        else:
            parsed = parser.parse_grid("Hello\nWorld", title="Interactive")
        print("Grid interactive mode (basic display)")
        print(renderer.render_simple(parsed))

    elif args.command == "to-usxd":
        from core_py.usxd import USXDDocument, USXDMetadata
        with open(args.file) as f:
            text = f.read()
        parsed = parser.parse_grid(text)
        doc = USXDDocument(
            metadata=USXDMetadata(
                id=f"grid-{os.path.basename(args.file)}",
                title=parsed.title,
                version="1.0.0",
            ),
            sections=[],
        )
        from core_py.usxd import USXDSection
        doc.add_section(USXDSection(
            name="grid",
            section_type="grid",
            content=parsed.to_dict(),
        ))
        doc.save_to_file(args.output)
        print(f"Saved USXD document to {args.output}")

    elif args.command == "edit":
        cmd_edit(args, parser)

    elif args.command == "monodraw":
        if not MONODRAW_AVAILABLE:
            print("Error: monodraw module not available")
            sys.exit(1)
        if args.monodraw_cmd == "import":
            cmd_monodraw_import(args, parser)
        elif args.monodraw_cmd == "export":
            cmd_monodraw_export(args)
        elif args.monodraw_cmd == "install":
            ok = install_symlink()
            sys.exit(0 if ok else 1)
        else:
            p.print_help()

    else:
        p.print_help()


if __name__ == "__main__":
    main()
