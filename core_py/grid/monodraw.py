#!/usr/bin/env python3
"""
Monodraw Integration — Visual grid editing via Monodraw.app

Provides bidirectional format conversion between uCode grid data and
Monodraw's .monopic format, plus CLI integration for launching Monodraw
as a visual grid editor.

Monodraw.app: https://monodraw.helftone.com/
CLI tool: /Applications/Monodraw.app/Contents/Resources/monodraw
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple

MONODRAW_BUNDLE = "/Applications/Monodraw.app"
MONODRAW_CLI = f"{MONODRAW_BUNDLE}/Contents/Resources/monodraw"
MONODRAW_LINK = "/usr/local/bin/monodraw"
MONOPIC_HEADER = b"\xffMONOPIC\x01"  # Magic bytes for .monopic files


def is_available() -> bool:
    """Check if Monodraw CLI is installed and accessible."""
    return os.path.isfile(MONODRAW_CLI) or shutil.which("monodraw") is not None


def get_cli_path() -> Optional[str]:
    """Get the monodraw CLI path, or None if unavailable."""
    if os.path.isfile(MONODRAW_CLI):
        return MONODRAW_CLI
    path = shutil.which("monodraw")
    if path:
        return path
    # Try the symlink path
    if os.path.isfile(MONODRAW_LINK):
        return MONODRAW_LINK
    return None


def is_monopic_file(path: str) -> bool:
    """Check if a file is in .monopic format by examining magic bytes."""
    try:
        with open(path, "rb") as f:
            header = f.read(len(MONOPIC_HEADER))
            return header == MONOPIC_HEADER
    except (IOError, OSError):
        return False


def monopic_to_ascii(path: str, unicode: bool = False, trim: bool = True) -> str:
    """Convert a .monopic file to plain ASCII grid text via monodraw CLI.

    Args:
        path: Path to .monopic file.
        unicode: Use Unicode box-drawing characters instead of ASCII.
        trim: Trim trailing whitespace from each line.

    Returns:
        ASCII grid text as a string.
    """
    cli = get_cli_path()
    if not cli:
        raise RuntimeError(
            "Monodraw CLI not found. Install Monodraw from https://monodraw.helftone.com/"
        )

    cmd = [cli]
    if unicode:
        cmd.append("--unicode")
    if trim:
        cmd.append("--trim-whitespace")
    cmd.append(path)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(
            f"Monodraw CLI failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    return result.stdout


def monopic_to_json(path: str) -> dict:
    """Convert a .monopic file to structured JSON via monodraw CLI.

    Returns a dict with an 'output' key containing the ASCII text.
    """
    cli = get_cli_path()
    if not cli:
        raise RuntimeError("Monodraw CLI not found")

    result = subprocess.run(
        [cli, "-j", "-w", path], capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Monodraw CLI failed (exit {result.returncode}): {result.stderr.strip()}"
        )
    return json.loads(result.stdout)


def export_grid_to_monopic(
    ascii_text: str,
    output_path: str,
    title: str = "uDos Grid",
) -> str:
    """Export ASCII grid text for editing in Monodraw.

    Since Monodraw's native .monopic format is proprietary (binary + gzip),
    this saves as plain text. The Monodraw GUI can open plain text files.

    Workflow for Monodraw round-trip:
        1. ucode grid export → saves as .txt
        2. open -a Monodraw file.txt  (edit visually)
        3. In Monodraw: File > Save As... > saves as .monopic
        4. ucode grid monodraw import saved.monopic  (read back)

    Args:
        ascii_text: The ASCII grid content.
        output_path: Desired output path.
        title: Title for the document (unused for plain text).

    Returns:
        The actual path the file was saved to.
    """
    # Save as plain text — Monodraw GUI opens text natively.
    # User then does File > Save As... to create a native .monopic.
    with open(output_path, "w") as f:
        f.write(ascii_text)

    return output_path


def open_in_monodraw(path: str) -> None:
    """Open a file in Monodraw.app for visual editing.

    Uses macOS 'open' command to launch Monodraw with the specified file.
    Monodraw GUI can open both plain text and .monopic files.

    Args:
        path: Path to the file to open.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    subprocess.run(
        ["open", "-a", "Monodraw", path],
        capture_output=True,
        text=True,
        timeout=10,
    )


def edit_grid_interactive(
    text: Optional[str] = None,
    file_path: Optional[str] = None,
    title: str = "Untitled Grid",
) -> Tuple[str, str]:
    """Launch a visual grid editing session using Monodraw.

    Workflow:
        1. Save grid as plain text.
        2. Open in Monodraw GUI for visual editing.
        3. User edits and does File > Save As... (creates .monopic).
        4. We ask the user for the saved .monopic path.
        5. Read it back via monodraw CLI.

    Args:
        text: ASCII grid text to start with.
        file_path: Path to existing grid file.
        title: Grid title for the temp file.

    Returns:
        Tuple of (edited_text, saved_monopic_path).
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="udox_mono_"))
    txt_path = tmp_dir / f"{title.lower().replace(' ', '_')}.txt"

    # Write initial grid content as plain text
    if text:
        with open(txt_path, "w") as f:
            f.write(text)
    elif file_path:
        shutil.copy2(file_path, txt_path)
    else:
        with open(txt_path, "w") as f:
            f.write("")

    print(f"📐 Opening grid in Monodraw for editing...")
    print(f"   Temp file: {txt_path}")
    print(f"   Instructions:")
    print(f"     1. Edit grid visually in Monodraw")
    print(f"     2. File > Save As... to save as .monopic")
    print(f"     3. Copy the .monopic file path")
    open_in_monodraw(str(txt_path))

    # Ask user for the path to their saved .monopic
    mono_path = input("   Paste the path to your saved .monopic file: ").strip()
    mono_path = mono_path.strip("'\"")

    if not os.path.isfile(mono_path):
        print(f"⚠️  File not found: {mono_path}")
        print(f"   Falling back to reading: {txt_path}")
        with open(txt_path) as f:
            edited_text = f.read()
        return edited_text, str(txt_path)

    # Read back via monodraw CLI
    if is_monopic_file(mono_path):
        edited_text = monopic_to_ascii(mono_path, unicode=True, trim=True)
    else:
        with open(mono_path) as f:
            edited_text = f.read()

    return edited_text, mono_path


def install_symlink() -> bool:
    """Install the monodraw CLI symlink if not present.

    Returns True if the symlink was installed or already exists.
    """
    if shutil.which("monodraw"):
        return True
    if not os.path.isfile(MONODRAW_CLI):
        print("❌ Monodraw is not installed. Install from https://monodraw.helftone.com/")
        return False
    try:
        os.symlink(MONODRAW_CLI, MONODRAW_LINK)
        print(f"✅ Created symlink: {MONODRAW_LINK} → {MONODRAW_CLI}")
        return True
    except PermissionError:
        # Try with sudo
        print("ℹ️  Need admin to install symlink. Run:")
        print(f"   sudo ln -sf {MONODRAW_CLI} {MONODRAW_LINK}")
        return False
    except FileExistsError:
        return True
