"""
CEETEX Teletext App — uCode1 Textual App Subclass

Wraps the CEETEX teletext RSS reader as a uCode1-compatible Textual app.
Integrates with LENS (state capture), SKIN (runtime CSS patching),
and MCP (remote control) via the uCode1 bridge system.

Usage:
    from ucode1.ceefax.ceetex_app import CeetexUCodeApp
    
    app = CeetexUCodeApp()
    app.run()

Or via Snack:
    ucode1 snack run snacks/ceetex/snack.yaml
"""

import os
import sys
import json
import html
import textwrap
import re
import webbrowser
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

import feedparser
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Static, Input, ListView, ListItem, Label
from textual.containers import Container
from textual.binding import Binding
# ── uCode1 Integration Imports ──────────────────────────────────────

from ..bbc.lens import LENSEngine, LENSEvent
from ..bbc.skin import SkinEngine, SkinDefinition
from ..bbc.mcp_bridge import MCPBridge, MCPCommand, MCPCommandType


# ── CEETEX Logo ─────────────────────────────────────────────────────

CEETEX_LOGO = """
 [b white]█▀▀ █▀▀ █▀▀ ▀█▀ █▀▀ █ █[/b white]
 [b white]█   █▀▀ █▀▀  █  █▀▀ ▄▀▄[/b white]
 [b white]▀▀▀ ▀▀▀ ▀▀▀  ▀  ▀▀▀ ▀ ▀[/b white]
 [reverse][b yellow]  B R O A D C A S T   S E R V I C E  [/b yellow][/reverse]
"""


# ── uCode1 Skin Definitions for CEETEX ──────────────────────────────

CEETEX_SKINS: Dict[str, Dict[str, str]] = {
    "teletext_classic": {
        "screen_bg": "#000000",
        "screen_fg": "#ffffff",
        "header_bg": "#0000ff",
        "header_fg": "#ffffff",
        "subheader_bg": "#000000",
        "subheader_fg": "#00ff00",
        "list_bg": "#000000",
        "list_fg": "#ffffff",
        "highlight_bg": "#0000ff",
        "highlight_fg": "#ffff00",
        "ticker_bg": "#0000ff",
        "ticker_fg": "#ffffff",
        "fasttext_bg": "#000000",
        "fasttext_fg": "#ffffff",
        "loading_fg": "#ffff00",
        "article_fg": "#ffffff",
    },
    "paper_retro": {
        "screen_bg": "#F5E6C8",
        "screen_fg": "#4A3728",
        "header_bg": "#8B4513",
        "header_fg": "#F5E6C8",
        "subheader_bg": "#F5E6C8",
        "subheader_fg": "#4A3728",
        "list_bg": "#F5E6C8",
        "list_fg": "#4A3728",
        "highlight_bg": "#D2B48C",
        "highlight_fg": "#3E2723",
        "ticker_bg": "#8B4513",
        "ticker_fg": "#F5E6C8",
        "fasttext_bg": "#F5E6C8",
        "fasttext_fg": "#4A3728",
        "loading_fg": "#8B4513",
        "article_fg": "#4A3728",
    },
    "dark_mode": {
        "screen_bg": "#1E1E1E",
        "screen_fg": "#E0E0E0",
        "header_bg": "#2D2D2D",
        "header_fg": "#E0E0E0",
        "subheader_bg": "#1E1E1E",
        "subheader_fg": "#66BB6A",
        "list_bg": "#1E1E1E",
        "list_fg": "#E0E0E0",
        "highlight_bg": "#333333",
        "highlight_fg": "#FFEE58",
        "ticker_bg": "#2D2D2D",
        "ticker_fg": "#E0E0E0",
        "fasttext_bg": "#1E1E1E",
        "fasttext_fg": "#E0E0E0",
        "loading_fg": "#FFEE58",
        "article_fg": "#E0E0E0",
    },
    "high_vis": {
        "screen_bg": "#000000",
        "screen_fg": "#FFFF00",
        "header_bg": "#000080",
        "header_fg": "#FFFF00",
        "subheader_bg": "#000000",
        "subheader_fg": "#FFFF00",
        "list_bg": "#000000",
        "list_fg": "#FFFF00",
        "highlight_bg": "#000080",
        "highlight_fg": "#FFFFFF",
        "ticker_bg": "#000080",
        "ticker_fg": "#FFFF00",
        "fasttext_bg": "#000000",
        "fasttext_fg": "#FFFF00",
        "loading_fg": "#FFFF00",
        "article_fg": "#FFFF00",
    },
    "amiga_workbench": {
        "screen_bg": "#0050A0",
        "screen_fg": "#FFFFFF",
        "header_bg": "#003070",
        "header_fg": "#FFFFFF",
        "subheader_bg": "#0050A0",
        "subheader_fg": "#FFFFFF",
        "list_bg": "#0050A0",
        "list_fg": "#FFFFFF",
        "highlight_bg": "#0080FF",
        "highlight_fg": "#FFFF00",
        "ticker_bg": "#003070",
        "ticker_fg": "#FFFFFF",
        "fasttext_bg": "#0050A0",
        "fasttext_fg": "#FFFFFF",
        "loading_fg": "#FFFF00",
        "article_fg": "#FFFFFF",
    },
}


def _generate_ceetex_css(skin: Dict[str, str]) -> str:
    """Generate Textual CSS from a CEETEX skin definition."""
    return f"""
    Screen {{ background: {skin['screen_bg']}; color: {skin['screen_fg']}; }}
    #page_header {{ background: {skin['header_bg']}; color: {skin['header_fg']}; height: 7; width: 100%; content-align: center top; }}
    #sub_header {{ background: {skin['subheader_bg']}; color: {skin['subheader_fg']}; height: 1; margin: 0 2; text-style: bold; }}
    #teletext_container {{ width: 100%; height: 1fr; background: {skin['screen_bg']}; }}
    ListView {{ background: {skin['list_bg']}; height: 1fr; border: none; overflow-y: scroll; }}
    ListItem {{ padding: 0 1; background: {skin['list_bg']}; color: {skin['list_fg']}; }}
    ListItem.--highlight {{ background: {skin['highlight_bg']}; color: {skin['highlight_fg']}; text-style: bold; }}
    #ticker_tape {{ background: {skin['ticker_bg']}; color: {skin['ticker_fg']}; height: 1; width: 100%; text-style: bold; }}
    #fasttext_bar {{ height: 1; width: 100%; background: {skin['fasttext_bg']}; }}
    Input {{ width: 100%; height: 1; background: {skin['screen_bg']}; color: {skin['screen_fg']}; border: none; padding: 0 2; }}
    .hidden {{ display: none; }}
    #loading_msg {{ color: {skin['loading_fg']}; text-style: blink; margin: 2; }}
    #article_view {{ padding: 1 2; }}
    """


# ── LENS Adapter for CEETEX ─────────────────────────────────────────

class CeetexLENSAdapter:
    """
    LENS adapter that captures CEETEX teletext state.
    
    Captures:
        - Current page ID and title
        - Headline list (up to 15 entries)
        - Cursor position and view mode
        - Ticker tape text
        - Timestamp of last update
    """

    def __init__(self, app: "CeetexUCodeApp"):
        self.app = app
        self._last_state: Dict[str, Any] = {}

    def capture(self) -> Dict[str, Any]:
        """Capture current CEETEX state for LENS export."""
        state = {
            "current_page": self.app.current_page_id,
            "view_mode": self.app.view_mode,
            "headline_count": len(self.app.entries),
            "headlines": [
                {
                    "title": html.unescape(e.get("title", "UNTITLED")).upper(),
                    "link": e.get("link", ""),
                }
                for e in self.app.entries[:15]
            ],
            "ticker": str(self.app.query_one("#ticker_tape").renderable)
                       if self.app.is_mounted else "",
            "timestamp": datetime.now().isoformat(),
        }

        # Add page metadata if available
        if self.app.current_page_id in self.app.pages:
            cat, url = self.app.pages[self.app.current_page_id]
            state["page_category"] = cat
            state["page_url"] = url

        self._last_state = state
        return state

    def detect_changes(self) -> Dict[str, Any]:
        """Detect what changed since last capture."""
        current = self.capture()
        changes = {}

        if current["current_page"] != self._last_state.get("current_page"):
            changes["page_changed"] = {
                "from": self._last_state.get("current_page"),
                "to": current["current_page"],
            }
        if current["headline_count"] != self._last_state.get("headline_count"):
            changes["headline_count"] = {
                "from": self._last_state.get("headline_count"),
                "to": current["headline_count"],
            }
        if current["view_mode"] != self._last_state.get("view_mode"):
            changes["view_mode"] = {
                "from": self._last_state.get("view_mode"),
                "to": current["view_mode"],
            }

        return changes


# ── SKIN Adapter for CEETEX ─────────────────────────────────────────

class CeetexSKINAdapter:
    """
    SKIN adapter that patches CEETEX's Textual CSS at runtime.
    
    Maps uCode1 SkinEngine skins to CEETEX CSS variables and
    hot-reloads the Textual theme without restarting the app.
    """

    def __init__(self, app: "CeetexUCodeApp"):
        self.app = app
        self._active_skin_name: str = "teletext_classic"

    @property
    def active_skin_name(self) -> str:
        return self._active_skin_name

    @property
    def available_skins(self) -> List[str]:
        return list(CEETEX_SKINS.keys())

    def apply(self, skin_name: str) -> bool:
        """
        Apply a named skin to the CEETEX app.
        
        Hot-reloads the Textual CSS without restarting.
        
        Args:
            skin_name: Name of the skin to apply
            
        Returns:
            True if applied, False if skin not found
        """
        if skin_name not in CEETEX_SKINS:
            return False

        self._active_skin_name = skin_name
        skin = CEETEX_SKINS[skin_name]
        css = _generate_ceetex_css(skin)

        # Hot-reload CSS on the running Textual app
        if self.app.is_mounted:
            try:
                self.app.stylesheet.update(css)
                self.app.refresh()
            except Exception:
                # Fallback: set CSS directly
                self.app.css = css

        return True

    def get_skin_colors(self) -> Dict[str, str]:
        """Get the current skin's colour palette."""
        return dict(CEETEX_SKINS.get(self._active_skin_name, CEETEX_SKINS["teletext_classic"]))


# ── MCP Controller for CEETEX ───────────────────────────────────────

class CeetexMCPController:
    """
    MCP controller for remote CEETEX control.
    
    MCP Commands:
        PAGE <id>       — Navigate to a teletext page
        NEXT            — Next page in sequence
        PREV            — Previous page in sequence
        REVEAL          — Toggle concealed text
        SUBTITLE        — Toggle subtitle mode
        SKIN <name>     — Change visual skin
        STATUS          — Get current CEETEX state
    """

    def __init__(self, app: "CeetexUCodeApp"):
        self.app = app

    def handle_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle an MCP command for CEETEX.
        
        Args:
            command: Command name (PAGE, NEXT, PREV, REVEAL, SUBTITLE, SKIN, STATUS)
            args: Optional command arguments
            
        Returns:
            Response dict with result or error
        """
        args = args or {}

        if command == "PAGE":
            page_id = args.get("page", "100")
            return self._handle_page(str(page_id))

        elif command == "NEXT":
            return self._handle_next()

        elif command == "PREV":
            return self._handle_prev()

        elif command == "REVEAL":
            return self._handle_reveal()

        elif command == "SUBTITLE":
            return self._handle_subtitle()

        elif command == "SKIN":
            skin_name = args.get("name", "teletext_classic")
            return self._handle_skin(skin_name)

        elif command == "STATUS":
            return self._handle_status()

        else:
            return {"error": f"Unknown CEETEX MCP command: {command}"}

    def _handle_page(self, page_id: str) -> Dict[str, Any]:
        """Navigate to a teletext page."""
        if not self.app.is_mounted:
            return {"error": "CEETEX app not running"}

        self.app.call_from_thread(self.app.load_page, page_id)
        page_info = self.app.pages.get(page_id, ["UNKNOWN"])
        page_title = page_info[0] if isinstance(page_info, list) else page_info
        return {
            "command": "PAGE",
            "page": page_id,
            "title": page_title,
        }

    def _handle_next(self) -> Dict[str, Any]:
        """Go to the next page in sequence."""
        if not self.app.is_mounted:
            return {"error": "CEETEX app not running"}

        pages = sorted(
            [int(k) for k in self.app.pages.keys() if k != "100"],
        )
        current = int(self.app.current_page_id)
        next_page = "100"

        for p in pages:
            if p > current:
                next_page = str(p)
                break

        self.app.call_from_thread(self.app.load_page, next_page)
        return {"command": "NEXT", "page": next_page}

    def _handle_prev(self) -> Dict[str, Any]:
        """Go to the previous page in sequence."""
        if not self.app.is_mounted:
            return {"error": "CEETEX app not running"}

        pages = sorted(
            [int(k) for k in self.app.pages.keys() if k != "100"],
            reverse=True,
        )
        current = int(self.app.current_page_id)
        prev_page = "100"

        for p in pages:
            if p < current:
                prev_page = str(p)
                break

        self.app.call_from_thread(self.app.load_page, prev_page)
        return {"command": "PREV", "page": prev_page}

    def _handle_reveal(self) -> Dict[str, Any]:
        """Toggle concealed text reveal."""
        # CEETEX doesn't natively support conceal/reveal,
        # but we can toggle a CSS class for effect
        if not self.app.is_mounted:
            return {"error": "CEETEX app not running"}

        # Toggle a reveal state on the app
        self.app._reveal_active = not getattr(self.app, "_reveal_active", False)
        return {
            "command": "REVEAL",
            "active": self.app._reveal_active,
        }

    def _handle_subtitle(self) -> Dict[str, Any]:
        """Toggle subtitle mode."""
        if not self.app.is_mounted:
            return {"error": "CEETEX app not running"}

        self.app._subtitle_active = not getattr(self.app, "_subtitle_active", False)
        return {
            "command": "SUBTITLE",
            "active": self.app._subtitle_active,
        }

    def _handle_skin(self, skin_name: str) -> Dict[str, Any]:
        """Change the visual skin."""
        success = self.app.skin_adapter.apply(skin_name)
        if success:
            return {"command": "SKIN", "skin": skin_name}
        return {"error": f"Unknown skin: {skin_name}"}

    def _handle_status(self) -> Dict[str, Any]:
        """Get current CEETEX status."""
        if not self.app.is_mounted:
            return {"error": "CEETEX app not running"}

        state = self.app.lens_adapter.capture()
        state["active_skin"] = self.app.skin_adapter.active_skin_name
        state["available_skins"] = self.app.skin_adapter.available_skins
        return {"command": "STATUS", "state": state}


# ── Main CEETEX uCode1 App ──────────────────────────────────────────

class CeetexUCodeApp(App):
    """
    CEETEX Teletext App — uCode1 Textual App Subclass.
    
    Integrates CEETEX RSS teletext reader with uCode1's LENS/SKIN/MCP
    ecosystem. Can be run standalone or as a uCode1 Snack.
    
    Features:
        - RSS feed teletext pages (3-digit navigation)
        - LENS state capture (current page, headlines, ticker)
        - SKIN hot-reload (5 built-in themes)
        - MCP remote control (PAGE, NEXT, PREV, SKIN, STATUS)
        - uCode1 bridge integration (VDU stream, ThinUI output)
    """

    BINDINGS = [
        Binding("escape", "back_to_list", "Index/Back"),
        Binding("home", "go_home", "Home"),
        Binding("o", "open_browser", "Open Link"),
        Binding("q", "quit", "Quit"),
        Binding("s", "cycle_skin", "Cycle Skin"),
    ]

    CSS = _generate_ceetex_css(CEETEX_SKINS["teletext_classic"])

    def __init__(self, pages_path: Optional[str] = None):
        """
        Initialize the CEETEX uCode1 app.
        
        Args:
            pages_path: Optional path to pages.json config.
                        Defaults to the CEETEX repo's pages.json.
        """
        super().__init__()
        self.pages = self._load_config(pages_path)
        self.entries: List[Dict] = []
        self.current_page_id = "100"
        self.view_mode = "index"
        self.index_mapping: List[str] = []

        # uCode1 integration adapters
        self.lens_adapter = CeetexLENSAdapter(self)
        self.skin_adapter = CeetexSKINAdapter(self)
        self.mcp_controller = CeetexMCPController(self)

        # Internal state
        self._reveal_active = False
        self._subtitle_active = False
        self._on_page_change_callbacks: List[Callable[[str], None]] = []
        self._on_headline_change_callbacks: List[Callable[[List[Dict]], None]] = []

    # ── Configuration ───────────────────────────────────────────────

    def _load_config(self, pages_path: Optional[str] = None) -> Dict:
        """Load pages.json configuration."""
        if pages_path and os.path.exists(pages_path):
            try:
                with open(pages_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"CEETEX config error: {e}")

        # Fallback: look in ~/Code/Vendor/ceetex/ (external clone)
        vendor_path = os.path.expanduser("~/Code/Vendor/ceetex/pages.json")
        if os.path.exists(vendor_path):
            try:
                with open(vendor_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass

        return {"100": ["INDEX", ""]}

    # ── Textual App Lifecycle ───────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("", id="page_header", markup=True)
        yield Static(" P100  CEETEX 1  [white]1/1[/white]  LONDON", id="sub_header", markup=True)

        with Container(id="teletext_container"):
            yield ListView(id="main_list")
            yield Static(" [blink]LOADING DATA...[/blink]", id="loading_msg", markup=True, classes="hidden")
            yield Static("", id="article_view", classes="hidden", markup=True)

        yield Static(" LATEST: WAITING FOR CEETEX DATA...", id="ticker_tape", markup=True)
        yield Static(
            " [b red] NEWS [/b red] [b green] SPORT [/b green]"
            " [b yellow] WEATHER [/b yellow] [b cyan] TRAVEL [/b cyan]",
            id="fasttext_bar",
            markup=True,
        )
        yield Input(placeholder="P100", id="dialer")

    def on_mount(self) -> None:
        self.query_one("#dialer").focus()
        self.load_page("100")

    # ── Page Navigation ─────────────────────────────────────────────

    def update_header(self, page_id: str) -> None:
        """Update the header with logo (P100) or page info."""
        time_str = datetime.now().strftime('%a %d %b %H:%M/%S')
        meta = f"[yellow]Ceetex {page_id}[/yellow] [white]CEETEX 1[/white] [yellow]{time_str}[/yellow]"
        header_widget = self.query_one("#page_header")

        if page_id == "100":
            header_widget.update(f"{meta}\n{CEETEX_LOGO}")
            header_widget.styles.height = 7
        else:
            header_widget.update(meta)
            header_widget.styles.height = 1

    def action_go_home(self) -> None:
        """Return to the index page (P100)."""
        self.load_page("100")
        self.query_one("#dialer").value = ""
        self.query_one("#dialer").focus()

    def action_cycle_skin(self) -> None:
        """Cycle through available skins."""
        skins = self.skin_adapter.available_skins
        current = self.skin_adapter.active_skin_name
        idx = skins.index(current) if current in skins else 0
        next_idx = (idx + 1) % len(skins)
        self.skin_adapter.apply(skins[next_idx])
        self.notify(f"Skin: {skins[next_idx]}", timeout=2)

    def display_index(self) -> None:
        """Render the main index page (P100)."""
        self.view_mode = "index"
        self.current_page_id = "100"
        self.index_mapping = []

        lst = self.query_one("#main_list")
        lst.clear()
        self._toggle_views(show_list=True)

        lst.append(ListItem(Label("[b yellow] DIRECTORY                  [/b yellow]", markup=True)))

        sorted_keys = sorted([k for k in self.pages.keys() if k != "100"], key=int)
        mid = (len(sorted_keys) + 1) // 2
        col1 = sorted_keys[:mid]
        col2 = sorted_keys[mid:]

        for i in range(mid):
            p1 = col1[i]
            n1 = self.pages[p1][0].upper()
            left_dots = "." * max(2, 22 - len(n1))
            line = f" [white]{n1}[/white] {left_dots} [cyan]{p1}[/cyan]"

            if i < len(col2):
                p2 = col2[i]
                n2 = self.pages[p2][0].upper()
                right_dots = "." * max(2, 22 - len(n2))
                line += f"     [white]{n2}[/white] {right_dots} [cyan]{p2}[/cyan]"

            lst.append(ListItem(Label(line, markup=True)))
            self.index_mapping.append(p1)

        lst.append(ListItem(Label("")))
        lst.append(ListItem(Label(
            "[reverse][b yellow] FINANCE: GET THE FACTS ON PAGE 200 [/b yellow][/reverse]",
            markup=True,
        )))

        self.update_header("100")
        self.query_one("#sub_header").update(" P100  CEETEX 1  [white]1/1[/white]  MAIN INDEX")

        # Notify LENS
        self._notify_page_change("100")

    def load_page(self, page_id: str) -> None:
        """Load a teletext page by ID."""
        if page_id == "100":
            self.display_index()
            return

        if page_id not in self.pages:
            self.show_error(page_id, "PAGE DOES NOT EXIST")
            return

        self.current_page_id = page_id
        cat, url = self.pages[page_id]

        self.update_header(page_id)
        self.query_one("#sub_header").update(
            f" P{page_id}  CEETEX 1  [white]1/1[/white]  {cat}"
        )

        self._toggle_views(show_loading=True)
        self.fetch_feed(page_id, url)

    @work(thread=True)
    def fetch_feed(self, page_id: str, url: str) -> None:
        """Fetch an RSS feed in a background thread."""
        try:
            feed = feedparser.parse(url)
            self.call_from_thread(self.render_feed, page_id, feed)
        except Exception as e:
            self.call_from_thread(self.show_error, page_id, f"CONNECTION ERROR: {str(e)}")

    def render_feed(self, page_id: str, feed) -> None:
        """Render an RSS feed as a teletext page."""
        if self.current_page_id != page_id:
            return

        if not feed.entries:
            self.show_error(page_id, "NO DATA RECEIVED ON THIS CHANNEL")
            return

        self.entries = feed.entries
        lst = self.query_one("#main_list")
        lst.clear()

        safe_ticker_title = html.unescape(
            self.entries[0].get("title", "UNTITLED").upper()
        )
        self.query_one("#ticker_tape").update(
            f" [b yellow]LATEST:[/b yellow] {safe_ticker_title}"
        )

        for entry in self.entries[:15]:
            clean_title = html.unescape(entry.get("title", "UNTITLED")).upper()
            title = textwrap.shorten(clean_title, width=self.size.width - 10, placeholder="...")
            lst.append(ListItem(Label(f" [cyan]█[/cyan] [white]{title}[/white]", markup=True)))

        self.view_mode = "list"
        self._toggle_views(show_list=True)
        lst.focus()

        # Notify LENS and callbacks
        self._notify_page_change(page_id)
        self._notify_headline_change(self.entries[:15])

    def show_error(self, page_id: str, message: str) -> None:
        """Display an error page."""
        self.view_mode = "error"
        view = self.query_one("#article_view")
        content = (
            f"\n\n[b red] {message} [/b red]\n\n"
            f"[white] PLEASE CHECK SIGNAL AND TRY AGAIN[/white]\n\n"
            f"[b yellow] ESC FOR INDEX[/b yellow]"
        )
        view.update(content)
        self._toggle_views(show_article=True)

    def _toggle_views(self, show_list=False, show_article=False, show_loading=False):
        """Toggle visibility of list, article, and loading views."""
        self.query_one("#main_list").set_class(not show_list, "hidden")
        self.query_one("#article_view").set_class(not show_article, "hidden")
        self.query_one("#loading_msg").set_class(not show_loading, "hidden")

    # ── Event Handlers ──────────────────────────────────────────────

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection."""
        idx = self.query_one("#main_list").index
        if idx is None:
            return

        if self.view_mode == "index":
            adjusted_idx = idx - 1
            if 0 <= adjusted_idx < len(self.index_mapping):
                self.load_page(self.index_mapping[adjusted_idx])
        elif self.view_mode == "list":
            self.display_article(self.entries[idx])

    def display_article(self, entry) -> None:
        """Display a full article view."""
        self.view_mode = "article"
        view = self.query_one("#article_view")

        raw_summary = entry.get('summary', entry.get('description', 'NO DETAILS PROVIDED.'))
        clean_summary = html.unescape(re.sub('<[^<]+?>', '', raw_summary))
        clean_title = html.unescape(entry.get('title', 'UNTITLED')).upper()

        content = (
            f"[b cyan]{clean_title}[/b cyan]\n\n"
            f"[white]{textwrap.fill(clean_summary, width=self.size.width - 10)}[/white]\n\n"
            f"[b yellow]PRESS 'O' FOR FULL STORY | ESC FOR INDEX[/b yellow]"
        )
        view.update(content)
        self._toggle_views(show_article=True)

    def action_back_to_list(self) -> None:
        """Go back to the list or index."""
        if self.view_mode in ("article", "error"):
            self.load_page(self.current_page_id)
        else:
            self.load_page("100")
        self.query_one("#dialer").value = ""
        self.query_one("#dialer").focus()

    def action_open_browser(self) -> None:
        """Open the current article link in a browser."""
        if self.view_mode == "article":
            idx = self.query_one("#main_list").index
            link = self.entries[idx].get("link")
            if link:
                webbrowser.open(link)

    def on_key(self, event) -> None:
        """Route digit keys to the dialer input."""
        if event.character and event.character.isdigit():
            dialer = self.query_one("#dialer")
            if not dialer.has_focus:
                dialer.focus()
                dialer.value += event.character
                event.stop()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle 3-digit page dialing."""
        val = event.value
        if len(val) == 3:
            if val.isdigit():
                self.load_page(val)
                self.call_after_refresh(self._clear_dialer)
            else:
                self._clear_dialer()

    def _clear_dialer(self) -> None:
        """Clear the dialer input and refocus."""
        dialer = self.query_one("#dialer")
        dialer.value = ""
        dialer.focus()

    # ── uCode1 Integration Callbacks ────────────────────────────────

    def add_page_change_callback(self, callback: Callable[[str], None]) -> None:
        """Register a callback for page changes."""
        self._on_page_change_callbacks.append(callback)

    def add_headline_change_callback(self, callback: Callable[[List[Dict]], None]) -> None:
        """Register a callback for headline changes."""
        self._on_headline_change_callbacks.append(callback)

    def _notify_page_change(self, page_id: str) -> None:
        """Notify page change callbacks."""
        for cb in self._on_page_change_callbacks:
            try:
                cb(page_id)
            except Exception:
                pass

    def _notify_headline_change(self, headlines: List[Dict]) -> None:
        """Notify headline change callbacks."""
        for cb in self._on_headline_change_callbacks:
            try:
                cb(headlines)
            except Exception:
                pass

    # ── LENS Integration ────────────────────────────────────────────

    def get_lens_state(self) -> Dict[str, Any]:
        """Get current state for LENS capture."""
        return self.lens_adapter.capture()

    def get_lens_changes(self) -> Dict[str, Any]:
        """Get detected changes since last capture."""
        return self.lens_adapter.detect_changes()

    # ── SKIN Integration ────────────────────────────────────────────

    def apply_skin(self, skin_name: str) -> bool:
        """Apply a named skin (public API for SKIN engine)."""
        return self.skin_adapter.apply(skin_name)

    def get_skin_colors(self) -> Dict[str, str]:
        """Get current skin colours."""
        return self.skin_adapter.get_skin_colors()

    # ── MCP Integration ─────────────────────────────────────────────

    def handle_mcp_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle an MCP command (public API for MCP bridge)."""
        return self.mcp_controller.handle_command(command, args)


# ── Standalone Entry Point ──────────────────────────────────────────

def run_ceetex(pages_path: Optional[str] = None) -> None:
    """Run CEETEX as a standalone uCode1 app."""
    app = CeetexUCodeApp(pages_path)
    app.run()


if __name__ == "__main__":
    run_ceetex()
