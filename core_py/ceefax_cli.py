#!/usr/bin/env python3
"""
CeefaxThinUI CLI — Command-line interface for teletext rendering and export

Usage:
  ucode ceefax [COMMAND] [OPTIONS]

Commands:
  parse       Parse text/ANSI file to teletext grid
  render      Render teletext grid in terminal (ANSI output)
  export      Export teletext grid to HTML, ANSI, or JSON
  serve       Start ThinUI API server with Ceefax endpoints
  app         Run the CEETEX Textual teletext app
  feed        Subscribe to feed channels for live teletext updates
  spool       Import/export teletext page collections
  mcp         Send MCP remote control commands to Ceefax
  vdu         Bridge BBC BASIC VDU output to teletext pages
  help        Show help for a command

Examples:
  ucode ceefax parse mygrid.txt
  ucode ceefax render mygrid.txt
  ucode ceefax export mygrid.txt --format html
  ucode ceefax export mygrid.txt --format ansi
  ucode ceefax serve --port 8001
  ucode ceefax app
  ucode ceefax feed subscribe news 101
  ucode ceefax feed poll
  ucode ceefax spool save 101 --title "News"
  ucode ceefax spool export mypages
  ucode ceefax mcp send PAGE 101
  ucode ceefax mcp send NEXT
  ucode ceefax vdu connect
  ucode ceefax vdu write "Hello from BBC BASIC!"
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Optional

# Add core_py to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core_py.ceefax import (
    GameToTeletextBridge,
    TeletextGrid,
    create_bridge,
)


class CeefaxCLI:
    """Command-line interface for CeefaxThinUI teletext operations"""

    def __init__(self):
        self.bridge = create_bridge()

    def main(self, args):
        """Main entry point for ceefax CLI"""
        if len(args) < 1:
            self._print_help()
            return

        command = args[0]

        if command == "parse":
            self._command_parse(args[1:])
        elif command == "render":
            self._command_render(args[1:])
        elif command == "export":
            self._command_export(args[1:])
        elif command == "serve":
            self._command_serve(args[1:])
        elif command == "app":
            self._command_app(args[1:])
        elif command == "feed":
            self._command_feed(args[1:])
        elif command == "spool":
            self._command_spool(args[1:])
        elif command == "mcp":
            self._command_mcp(args[1:])
        elif command == "vdu":
            self._command_vdu(args[1:])
        elif command == "help" or command == "--help" or command == "-h":
            self._print_help()
        else:
            print(f"Unknown command: {command}")
            self._print_help()

    def _print_help(self):
        """Print help message"""
        print(__doc__)

    def _load_file(self, filepath: str) -> Optional[str]:
        """Load content from a file, returning None if not found."""
        path = Path(filepath)
        if not path.exists():
            print(f"❌ File not found: {filepath}")
            return None
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None

    def _detect_format(self, text: str) -> str:
        """Detect whether text is ANSI, ASCII art, or plain text."""
        if "\x1b[" in text:
            return "ansi"
        # Check for box-drawing characters
        box_chars = set("┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬")
        if any(c in text for c in box_chars):
            return "ascii_art"
        return "text"

    def _command_parse(self, args):
        """Parse a text/ANSI file to teletext grid and display summary.

        Usage: ucode ceefax parse [OPTIONS] FILE

        Options:
          --title TEXT    Page title (default: "Teletext Output")
          --json          Output grid data as JSON
        """
        parser = argparse.ArgumentParser(description="Parse text/ANSI file to teletext grid")
        parser.add_argument("file", help="Input file path")
        parser.add_argument("--title", default="Teletext Output", help="Page title")
        parser.add_argument("--json", action="store_true", help="Output grid data as JSON")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        content = self._load_file(parsed.file)
        if content is None:
            return

        fmt = self._detect_format(content)
        self.bridge.clear()
        self.bridge.set_title(parsed.title)

        if fmt == "ansi":
            self.bridge.process_ansi(content)
        elif fmt == "ascii_art":
            self.bridge.process_ascii_art(content)
        else:
            self.bridge.process_text(content)

        if parsed.json:
            data = self.bridge.get_grid_data()
            data["title"] = parsed.title
            print(json.dumps(data, indent=2))
        else:
            print(f"✅ Parsed: {parsed.file}")
            print(f"   Format: {fmt}")
            print(f"   Title:  {parsed.title}")
            print(f"   Grid:   {TeletextGrid.COLS}×{TeletextGrid.ROWS}")
            print()
            # Show a preview of the grid
            ansi_output = self.bridge.to_ansi()
            print(ansi_output)

    def _command_render(self, args):
        """Render a teletext grid in the terminal with ANSI colours.

        Usage: ucode ceefax render [OPTIONS] FILE

        Options:
          --title TEXT    Page title (default: "Teletext Output")
        """
        parser = argparse.ArgumentParser(description="Render teletext grid in terminal")
        parser.add_argument("file", help="Input file path")
        parser.add_argument("--title", default="Teletext Output", help="Page title")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        content = self._load_file(parsed.file)
        if content is None:
            return

        fmt = self._detect_format(content)
        self.bridge.clear()
        self.bridge.set_title(parsed.title)

        if fmt == "ansi":
            self.bridge.process_ansi(content)
        elif fmt == "ascii_art":
            self.bridge.process_ascii_art(content)
        else:
            self.bridge.process_text(content)

        # Render to ANSI for terminal display
        ansi_output = self.bridge.to_ansi()
        print(ansi_output)

    def _command_export(self, args):
        """Export teletext grid to HTML, ANSI, or JSON format.

        Usage: ucode ceefax export [OPTIONS] FILE

        Options:
          --format FORMAT  Export format: html, ansi, json (default: html)
          --title TEXT     Page title (default: "Teletext Output")
          --output FILE    Output file path (default: stdout)
        """
        parser = argparse.ArgumentParser(description="Export teletext grid")
        parser.add_argument("file", help="Input file path")
        parser.add_argument("--format", choices=["html", "ansi", "json"], default="html",
                          help="Export format (default: html)")
        parser.add_argument("--title", default="Teletext Output", help="Page title")
        parser.add_argument("--output", help="Output file path (default: stdout)")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        content = self._load_file(parsed.file)
        if content is None:
            return

        fmt = self._detect_format(content)
        self.bridge.clear()
        self.bridge.set_title(parsed.title)

        if fmt == "ansi":
            self.bridge.process_ansi(content)
        elif fmt == "ascii_art":
            self.bridge.process_ascii_art(content)
        else:
            self.bridge.process_text(content)

        # Generate output in requested format
        if parsed.format == "html":
            output = self.bridge.to_html(parsed.title)
        elif parsed.format == "ansi":
            output = self.bridge.to_ansi()
        elif parsed.format == "json":
            data = self.bridge.get_grid_data()
            data["title"] = parsed.title
            output = json.dumps(data, indent=2)
        else:
            print(f"❌ Unknown format: {parsed.format}")
            return

        # Write to file or stdout
        if parsed.output:
            try:
                Path(parsed.output).write_text(output, encoding="utf-8")
                print(f"✅ Exported to: {parsed.output}")
            except Exception as e:
                print(f"❌ Error writing output: {e}")
        else:
            print(output)

    def _command_serve(self, args):
        """Start the ThinUI API server with Ceefax endpoints.

        Usage: ucode ceefax serve [OPTIONS]

        Options:
          --port PORT     Port to listen on (default: 8001)
          --host HOST     Host to bind to (default: 127.0.0.1)
          --debug         Enable debug mode
        """
        parser = argparse.ArgumentParser(description="Start ThinUI API server")
        parser.add_argument("--port", type=int, default=8001, help="Port (default: 8001)")
        parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        try:
            from core_py.thinui.api import run_api_server
            print(f"🚀 Starting ThinUI API server on {parsed.host}:{parsed.port}")
            print(f"   Ceefax endpoints available at:")
            print(f"   http://{parsed.host}:{parsed.port}/api/thinui/parse")
            print(f"   http://{parsed.host}:{parsed.port}/api/thinui/render")
            print(f"   Press Ctrl+C to stop")
            run_api_server(host=parsed.host, port=parsed.port)
        except ImportError as e:
            print(f"❌ Could not start API server: {e}")
            print("   Make sure Flask is installed: pip install flask")
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
        except Exception as e:
            print(f"❌ Error starting server: {e}")

    def _command_app(self, args):
        """Run the CEETEX Textual teletext app.

        Usage: ucode ceefax app [OPTIONS]

        Options:
          --pages PATH    Path to pages.json config file
        """
        parser = argparse.ArgumentParser(description="Run CEETEX teletext app")
        parser.add_argument("--pages", help="Path to pages.json config file")

        try:
            parsed = parser.parse_args(args)
        except SystemExit:
            return

        try:
            from core_py.ceefax.ceetex_app import run_ceetex
            print("📺 Starting CEETEX Teletext App...")
            run_ceetex(pages_path=parsed.pages)
        except ImportError as e:
            print(f"❌ Could not start CEETEX app: {e}")
            print("   Make sure textual is installed: pip install textual feedparser")
        except KeyboardInterrupt:
            print("\n🛑 CEETEX app stopped")
        except Exception as e:
            print(f"❌ Error starting CEETEX app: {e}")


    # ── Feed Commands ──────────────────────────────────────────────

    def _command_feed(self, args):
        """Subscribe to feed channels for live teletext updates.

        Usage: ucode ceefax feed <subcommand> [OPTIONS]

        Subcommands:
          subscribe CHANNEL PAGE    Subscribe a feed channel to a page number
          unsubscribe CHANNEL      Unsubscribe a feed channel
          list                     List active subscriptions
          poll                     Poll all subscribed feeds once
          start [INTERVAL]         Start background polling
          stop                     Stop background polling
          write CHANNEL DATA       Write a feed entry (JSON string)
        """
        if len(args) < 1:
            print("Usage: ucode ceefax feed <subcommand> [OPTIONS]")
            print("Subcommands: subscribe, unsubscribe, list, poll, start, stop, write")
            return

        from core_py.ceefax.feed_subscriber import create_feed_subscriber
        subscriber = create_feed_subscriber()

        subcommand = args[0]
        sub_args = args[1:]

        if subcommand == "subscribe":
            if len(sub_args) < 2:
                print("Usage: ucode ceefax feed subscribe CHANNEL PAGE [--title TITLE] [--template TEMPLATE]")
                return
            parser = argparse.ArgumentParser(description="Subscribe feed channel")
            parser.add_argument("channel", help="Feed channel name")
            parser.add_argument("page", type=int, help="Teletext page number")
            parser.add_argument("--title", default="", help="Page title")
            parser.add_argument("--template", default="headline", choices=["headline", "weather", "sport", "custom"],
                              help="Render template")
            try:
                parsed = parser.parse_args(sub_args)
            except SystemExit:
                return
            sub = subscriber.subscribe(parsed.channel, parsed.page, parsed.title, parsed.template)
            print(f"✅ Subscribed feed '{sub.channel}' → page {sub.page_number}")

        elif subcommand == "unsubscribe":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax feed unsubscribe CHANNEL")
                return
            channel = sub_args[0]
            if subscriber.unsubscribe(channel):
                print(f"✅ Unsubscribed feed '{channel}'")
            else:
                print(f"❌ No subscription for '{channel}'")

        elif subcommand == "list":
            subs = subscriber.list_subscriptions()
            if not subs:
                print("No active subscriptions")
                return
            print(f"Active subscriptions ({len(subs)}):")
            for s in subs:
                print(f"  {s.channel} → page {s.page_number} [{s.format_template}]")

        elif subcommand == "poll":
            updated = subscriber.poll_once()
            print(f"✅ Polled feeds: {updated} pages updated")

        elif subcommand == "start":
            interval = float(sub_args[0]) if sub_args else 5.0
            subscriber.start(interval)
            print(f"✅ Background polling started (interval={interval}s)")

        elif subcommand == "stop":
            subscriber.stop()
            print("✅ Background polling stopped")

        elif subcommand == "write":
            if len(sub_args) < 2:
                print("Usage: ucode ceefax feed write CHANNEL '{\"key\": \"value\"}'")
                return
            channel = sub_args[0]
            try:
                data = json.loads(sub_args[1])
            except json.JSONDecodeError:
                print("❌ Invalid JSON data")
                return
            subscriber.write_feed_entry(channel, data)
            print(f"✅ Wrote entry to feed '{channel}'")

        else:
            print(f"Unknown feed subcommand: {subcommand}")

    # ── Spool Commands ─────────────────────────────────────────────

    def _command_spool(self, args):
        """Import/export teletext page collections.

        Usage: ucode ceefax spool <subcommand> [OPTIONS]

        Subcommands:
          save PAGE [--title TITLE] [--subtitle SUB]  Save current grid to spool
          remove PAGE              Remove a page from spool
          list                     List pages in current spool
          export FILENAME          Export spool to file
          import FILEPATH          Import spool from file
          merge FILEPATH           Merge spool from another file
          files                    List spool files
          delete FILENAME          Delete a spool file
          clear                    Clear current spool
        """
        if len(args) < 1:
            print("Usage: ucode ceefax spool <subcommand> [OPTIONS]")
            print("Subcommands: save, remove, list, export, import, merge, files, delete, clear")
            return

        from core_py.ceefax.spool import create_ceefax_spool
        spool = create_ceefax_spool()

        subcommand = args[0]
        sub_args = args[1:]

        if subcommand == "save":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax spool save PAGE [--title TITLE] [--subtitle SUB]")
                return
            parser = argparse.ArgumentParser(description="Save grid to spool")
            parser.add_argument("page", type=int, help="Page number")
            parser.add_argument("--title", default="", help="Page title")
            parser.add_argument("--subtitle", default="", help="Page subtitle")
            try:
                parsed = parser.parse_args(sub_args)
            except SystemExit:
                return
            entry = spool.save_page(parsed.page, self.bridge.grid, parsed.title, parsed.subtitle)
            print(f"✅ Saved page {entry.page_number} to spool")

        elif subcommand == "remove":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax spool remove PAGE")
                return
            page = int(sub_args[0])
            if spool.remove_page(page):
                print(f"✅ Removed page {page} from spool")
            else:
                print(f"❌ Page {page} not found in spool")

        elif subcommand == "list":
            pages = spool.list_pages()
            if not pages:
                print("No pages in spool")
                return
            print(f"Pages in spool ({len(pages)}):")
            for p in pages:
                print(f"  Page {p['page_number']}: {p['title'] or '(no title)'}")

        elif subcommand == "export":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax spool export FILENAME")
                return
            filepath = spool.export(sub_args[0])
            print(f"✅ Exported spool to: {filepath}")

        elif subcommand == "import":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax spool import FILEPATH")
                return
            try:
                count = spool.import_file(sub_args[0])
                print(f"✅ Imported {count} pages from: {sub_args[0]}")
            except (FileNotFoundError, ValueError) as e:
                print(f"❌ {e}")

        elif subcommand == "merge":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax spool merge FILEPATH")
                return
            try:
                other = create_ceefax_spool()
                other.import_file(sub_args[0])
                merged = spool.merge(other)
                print(f"✅ Merged {merged} pages from: {sub_args[0]}")
            except (FileNotFoundError, ValueError) as e:
                print(f"❌ {e}")

        elif subcommand == "files":
            files = spool.list_spool_files()
            if not files:
                print("No spool files found")
                return
            print(f"Spool files ({len(files)}):")
            for f in files:
                err = f.get("error", "")
                if err:
                    print(f"  {f['filename']}: {err}")
                else:
                    print(f"  {f['filename']}: {f['page_count']} pages, {f['size']} bytes")

        elif subcommand == "delete":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax spool delete FILENAME")
                return
            if spool.delete_spool_file(sub_args[0]):
                print(f"✅ Deleted spool file: {sub_args[0]}")
            else:
                print(f"❌ Spool file not found: {sub_args[0]}")

        elif subcommand == "clear":
            spool.clear()
            print("✅ Spool cleared")

        else:
            print(f"Unknown spool subcommand: {subcommand}")

    # ── MCP Commands ───────────────────────────────────────────────

    def _command_mcp(self, args):
        """Send MCP remote control commands to Ceefax.

        Usage: ucode ceefax mcp <subcommand> [OPTIONS]

        Subcommands:
          send COMMAND [ARGS]      Send an MCP command
          status                   Show current MCP state
          history                  Show command history
          clear                    Clear pending commands and responses

        Commands:
          NEXT       Next page
          PREV       Previous page
          SUB        Toggle subtitle
          INDEX      Go to index (page 100)
          REVEAL     Toggle reveal
          PAGE <n>   Go to specific page
          HOLD       Toggle hold
          SIZE       Toggle double height
          MIX        Toggle mix mode
          LIST       List pages
          STATUS     Show status
        """
        if len(args) < 1:
            print("Usage: ucode ceefax mcp <subcommand> [OPTIONS]")
            print("Subcommands: send, status, history, clear")
            return

        from core_py.ceefax.mcp_protocol import create_ceefax_mcp
        mcp = create_ceefax_mcp()

        subcommand = args[0]
        sub_args = args[1:]

        if subcommand == "send":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax mcp send COMMAND [ARGS]")
                print("Commands: NEXT, PREV, SUB, INDEX, REVEAL, PAGE <n>, HOLD, SIZE, MIX, LIST, STATUS")
                return
            cmd_str = " ".join(sub_args)
            cmd = mcp.queue_command(cmd_str, source="cli")
            response = mcp.process_command(cmd)
            if response:
                if response.success:
                    print(f"✅ {response.result}")
                else:
                    print(f"❌ {response.error}")
            else:
                print(f"✅ Command queued: {cmd_str}")

        elif subcommand == "status":
            state = mcp.get_state()
            print("Ceefax MCP State:")
            print(f"  Current page:  {state['current_page']}")
            print(f"  Subtitle:      {'on' if state['subtitle'] else 'off'}")
            print(f"  Reveal:        {'on' if state['reveal'] else 'off'}")
            print(f"  Hold:          {'on' if state['hold'] else 'off'}")
            print(f"  Double height: {'on' if state['double_height'] else 'off'}")
            print(f"  Mix mode:      {'on' if state['mix_mode'] else 'off'}")
            print(f"  Pending cmds:  {state['pending_commands']}")
            print(f"  History:       {state['command_history']} commands")

        elif subcommand == "history":
            history = mcp.get_history(limit=20)
            if not history:
                print("No command history")
                return
            print("Command history:")
            for h in history:
                print(f"  {h['command']} ({h['source']})")

        elif subcommand == "clear":
            mcp.clear_commands()
            mcp.clear_responses()
            print("✅ Cleared pending commands and responses")

        else:
            print(f"Unknown mcp subcommand: {subcommand}")

    # ── VDU Commands ───────────────────────────────────────────────

    def _command_vdu(self, args):
        """Bridge BBC BASIC VDU output to teletext pages.

        Usage: ucode ceefax vdu <subcommand> [OPTIONS]

        Subcommands:
          connect                  Connect to VDU driver (simulated)
          write TEXT               Write text to VDU page
          page [NUMBER]            Get/set current VDU page number
          flush                    Flush buffered text to grid
          clear                    Clear VDU page
          grid                     Show current grid as ANSI
          html                     Export current grid as HTML
          pages                    List VDU pages
          title TEXT [PAGE]        Set page title
          subtitle TEXT [PAGE]     Set page subtitle
        """
        if len(args) < 1:
            print("Usage: ucode ceefax vdu <subcommand> [OPTIONS]")
            print("Subcommands: connect, write, page, flush, clear, grid, html, pages, title, subtitle")
            return

        from core_py.ceefax.vdu_bridge import create_vdu_bridge
        vdu = create_vdu_bridge()

        subcommand = args[0]
        sub_args = args[1:]

        if subcommand == "connect":
            print("✅ VDU bridge initialized (page 500)")
            print("   Use 'vdu write TEXT' to send text")
            print("   Use 'vdu page NUMBER' to change page")

        elif subcommand == "write":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax vdu write TEXT")
                return
            text = " ".join(sub_args)
            vdu.write(text)
            vdu.flush()
            print(f"✅ Wrote: {text[:60]}{'...' if len(text) > 60 else ''}")

        elif subcommand == "page":
            if sub_args:
                vdu.set_page_number(int(sub_args[0]))
            print(f"Current VDU page: {vdu.get_page_number()}")

        elif subcommand == "flush":
            grid = vdu.flush()
            if grid:
                print("✅ Flushed buffer to grid")
            else:
                print("No buffered text to flush")

        elif subcommand == "clear":
            vdu.clear()
            print("✅ VDU page cleared")

        elif subcommand == "grid":
            ansi = vdu.to_ansi()
            print(ansi)

        elif subcommand == "html":
            html = vdu.to_html()
            print(html)

        elif subcommand == "pages":
            pages = vdu.list_pages()
            if not pages:
                print("No VDU pages")
                return
            print("VDU pages:")
            for p in pages:
                print(f"  Page {p['page_number']}: {p['title']} ({p['update_count']} updates)")

        elif subcommand == "title":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax vdu title TEXT [PAGE]")
                return
            title = sub_args[0]
            page = int(sub_args[1]) if len(sub_args) > 1 else None
            vdu.set_title(title, page)
            print(f"✅ Title set: {title}")

        elif subcommand == "subtitle":
            if len(sub_args) < 1:
                print("Usage: ucode ceefax vdu subtitle TEXT [PAGE]")
                return
            subtitle = sub_args[0]
            page = int(sub_args[1]) if len(sub_args) > 1 else None
            vdu.set_subtitle(subtitle, page)
            print(f"✅ Subtitle set: {subtitle}")

        else:
            print(f"Unknown vdu subcommand: {subcommand}")


def main():
    """Main entry point for ceefax CLI"""
    cli = CeefaxCLI()
    cli.main(sys.argv[1:])



if __name__ == "__main__":
    main()
