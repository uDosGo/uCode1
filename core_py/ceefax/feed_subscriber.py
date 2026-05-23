"""
Ceefax Feed Subscriber — Live teletext page updates from the uDos feed spool

Subscribes to feed events and converts them into teletext page updates.
Pages can subscribe to specific feed channels (e.g., "news", "weather", "sport")
and auto-refresh when new content arrives.

Usage:
    subscriber = CeefaxFeedSubscriber()
    subscriber.subscribe("news", page_number=101)
    subscriber.start()  # Begin polling
    ...
    subscriber.stop()
"""

import json
import logging
import os
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field

from ..feed import archive_feed_entries, search_feed_cells
from .bridge import GameToTeletextBridge, TeletextGrid, TeletextColour

logger = logging.getLogger(__name__)

# Default feed directory
DEFAULT_FEED_DIR = os.path.expanduser("~/.udos/feeds")


@dataclass
class FeedSubscription:
    """A subscription binding a feed channel to a teletext page"""
    channel: str
    page_number: int
    title: str = ""
    last_update: float = 0.0
    update_count: int = 0
    format_template: str = "headline"  # headline, weather, sport, custom


@dataclass
class TeletextPage:
    """A single teletext page with metadata"""
    page_number: int
    title: str = ""
    subtitle: str = ""
    grid: Optional[TeletextGrid] = None
    last_updated: float = 0.0
    source: str = "manual"  # manual, feed, spool, vdu


class CeefaxFeedSubscriber:
    """
    Subscribes to uDos feed channels and updates teletext pages.

    Features:
        - Subscribe feed channels to teletext page numbers
        - Poll feed directory for new JSONL entries
        - Auto-render feed content as teletext pages
        - Callback on page updates
        - Thread-safe polling with configurable interval
    """

    def __init__(self, feed_dir: Optional[str] = None):
        """
        Initialize the feed subscriber.

        Args:
            feed_dir: Directory containing feed JSONL files
        """
        self._feed_dir = feed_dir or DEFAULT_FEED_DIR
        self._subscriptions: Dict[str, FeedSubscription] = {}
        self._pages: Dict[int, TeletextPage] = {}
        self._bridge = GameToTeletextBridge()
        self._polling = False
        self._poll_thread: Optional[threading.Thread] = None
        self._poll_interval: float = 5.0  # seconds
        self._on_update_callbacks: List[Callable[[int, TeletextPage], None]] = []
        self._seen_entries: Set[str] = set()  # Track seen entry IDs

        # Ensure feed directory exists
        os.makedirs(self._feed_dir, exist_ok=True)

    # ── Subscription Management ────────────────────────────────────

    def subscribe(self, channel: str, page_number: int,
                  title: str = "", template: str = "headline") -> FeedSubscription:
        """
        Subscribe a feed channel to a teletext page number.

        Args:
            channel: Feed channel name (e.g., "news", "weather")
            page_number: Teletext page number (e.g., 101)
            title: Optional page title
            template: Render template (headline, weather, sport, custom)

        Returns:
            The FeedSubscription
        """
        sub = FeedSubscription(
            channel=channel,
            page_number=page_number,
            title=title or f"Page {page_number}",
            format_template=template,
        )
        self._subscriptions[channel] = sub

        # Create page entry
        self._pages[page_number] = TeletextPage(
            page_number=page_number,
            title=sub.title,
            source="feed",
        )

        logger.info(f"Subscribed feed '{channel}' → page {page_number}")
        return sub

    def unsubscribe(self, channel: str) -> bool:
        """Unsubscribe a feed channel"""
        if channel in self._subscriptions:
            sub = self._subscriptions.pop(channel)
            if sub.page_number in self._pages:
                del self._pages[sub.page_number]
            logger.info(f"Unsubscribed feed '{channel}'")
            return True
        return False

    def get_subscription(self, channel: str) -> Optional[FeedSubscription]:
        """Get a subscription by channel name"""
        return self._subscriptions.get(channel)

    def list_subscriptions(self) -> List[FeedSubscription]:
        """List all active subscriptions"""
        return list(self._subscriptions.values())

    # ── Page Management ────────────────────────────────────────────

    def get_page(self, page_number: int) -> Optional[TeletextPage]:
        """Get a teletext page by number"""
        return self._pages.get(page_number)

    def list_pages(self) -> List[TeletextPage]:
        """List all managed teletext pages"""
        return list(self._pages.values())

    def set_page(self, page_number: int, grid: TeletextGrid,
                 title: str = "", subtitle: str = "") -> TeletextPage:
        """Manually set a teletext page"""
        page = TeletextPage(
            page_number=page_number,
            title=title,
            subtitle=subtitle,
            grid=grid,
            last_updated=time.time(),
            source="manual",
        )
        self._pages[page_number] = page
        self._notify_update(page_number, page)
        return page

    # ── Feed Polling ───────────────────────────────────────────────

    def start(self, interval: float = 5.0) -> None:
        """
        Start polling feed channels for updates.

        Args:
            interval: Polling interval in seconds
        """
        if self._polling:
            logger.warning("Feed subscriber already polling")
            return

        self._poll_interval = interval
        self._polling = True
        self._poll_thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="ceefax-feed-poll",
        )
        self._poll_thread.start()
        logger.info(f"Feed subscriber started (interval={interval}s)")

    def stop(self) -> None:
        """Stop polling feed channels"""
        self._polling = False
        if self._poll_thread:
            self._poll_thread.join(timeout=10)
            self._poll_thread = None
        logger.info("Feed subscriber stopped")

    @property
    def is_polling(self) -> bool:
        """Whether the subscriber is actively polling"""
        return self._polling

    def poll_once(self) -> int:
        """
        Poll all subscribed feed channels once.

        Returns:
            Number of pages updated
        """
        updated = 0
        for channel, sub in self._subscriptions.items():
            if self._poll_feed_channel(channel, sub):
                updated += 1
        return updated

    def _poll_loop(self) -> None:
        """Background polling loop"""
        while self._polling:
            try:
                self.poll_once()
            except Exception as e:
                logger.error(f"Feed poll error: {e}")
            time.sleep(self._poll_interval)

    def _poll_feed_channel(self, channel: str, sub: FeedSubscription) -> bool:
        """
        Poll a single feed channel for new entries.

        Args:
            channel: Feed channel name
            sub: The subscription

        Returns:
            True if the page was updated
        """
        feed_path = os.path.join(self._feed_dir, f"{channel}.jsonl")
        if not os.path.exists(feed_path):
            return False

        try:
            new_entries = []
            with open(feed_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        entry_id = str(entry.get("id", entry.get("timestamp", line)))
                        if entry_id not in self._seen_entries:
                            self._seen_entries.add(entry_id)
                            new_entries.append(entry)
                    except json.JSONDecodeError:
                        continue

            if not new_entries:
                return False

            # Render new entries to teletext grid
            grid = self._render_feed_to_grid(new_entries, sub)
            page = self._pages.get(sub.page_number)
            if page:
                page.grid = grid
                page.last_updated = time.time()
                page.subtitle = f"Updated: {len(new_entries)} new items"
                sub.update_count += len(new_entries)
                sub.last_update = time.time()
                self._notify_update(sub.page_number, page)
                return True

        except Exception as e:
            logger.error(f"Error polling feed '{channel}': {e}")

        return False

    def _render_feed_to_grid(self, entries: List[Dict[str, Any]],
                             sub: FeedSubscription) -> TeletextGrid:
        """
        Render feed entries to a teletext grid.

        Args:
            entries: New feed entries
            sub: The subscription

        Returns:
            Rendered TeletextGrid
        """
        grid = TeletextGrid()

        # Title bar
        title = sub.title or f"FEED: {sub.channel.upper()}"
        grid.write_text(f"  {title}", row=0, col=0)
        grid.set_cell(0, 39, '╗', TeletextColour.WHITE, TeletextColour.BLACK)

        # Separator
        for col in range(40):
            grid.set_cell(1, col, '═', TeletextColour.WHITE, TeletextColour.BLACK)

        # Render entries based on template
        row = 3
        for entry in entries[-10:]:  # Show last 10 entries
            if row >= 24:
                break

            if sub.format_template == "headline":
                title_text = entry.get("title", entry.get("detail", "Untitled"))
                source_text = entry.get("source", entry.get("type", ""))
                grid.write_text(f"  {title_text[:36]}", row=row, col=0)
                if source_text:
                    grid.write_text(f"({source_text[:10]})", row=row + 1, col=2)
                row += 2

            elif sub.format_template == "weather":
                temp = entry.get("temperature", entry.get("temp", "?"))
                condition = entry.get("condition", entry.get("detail", ""))
                grid.write_text(f"  {condition[:20]}  {temp}", row=row, col=0)
                row += 1

            elif sub.format_template == "sport":
                team1 = entry.get("team1", entry.get("home", ""))
                team2 = entry.get("team2", entry.get("away", ""))
                score = entry.get("score", entry.get("result", ""))
                grid.write_text(f"  {team1[:15]} vs {team2[:15]}", row=row, col=0)
                grid.write_text(f"  {score[:20]}", row=row + 1, col=2)
                row += 2

            else:  # custom / default
                text = entry.get("detail", entry.get("content", str(entry)[:36]))
                grid.write_text(f"  {text[:36]}", row=row, col=0)
                row += 1

        # Bottom status
        grid.write_text(f"  {len(entries)} items  |  {sub.channel}", row=24, col=0)

        return grid

    # ── Callbacks ──────────────────────────────────────────────────

    def on_update(self, callback: Callable[[int, TeletextPage], None]) -> None:
        """
        Register a callback for page updates.

        Args:
            callback: Function(page_number, TeletextPage)
        """
        self._on_update_callbacks.append(callback)

    def _notify_update(self, page_number: int, page: TeletextPage) -> None:
        """Notify all update callbacks"""
        for cb in self._on_update_callbacks:
            try:
                cb(page_number, page)
            except Exception as e:
                logger.error(f"Update callback error: {e}")

    # ── Feed File Management ───────────────────────────────────────

    def write_feed_entry(self, channel: str, entry: Dict[str, Any]) -> None:
        """
        Write a feed entry to a channel's JSONL file.

        Args:
            channel: Feed channel name
            entry: Entry dict (must have 'type' key)
        """
        feed_path = os.path.join(self._feed_dir, f"{channel}.jsonl")
        os.makedirs(os.path.dirname(feed_path), exist_ok=True)

        # Ensure entry has required fields
        if "timestamp" not in entry:
            entry["timestamp"] = time.time()
        if "type" not in entry:
            entry["type"] = channel

        with open(feed_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    def get_feed_file_path(self, channel: str) -> str:
        """Get the path to a feed channel's JSONL file"""
        return os.path.join(self._feed_dir, f"{channel}.jsonl")


# Convenience function
def create_feed_subscriber(feed_dir: Optional[str] = None) -> CeefaxFeedSubscriber:
    """Create and return a CeefaxFeedSubscriber"""
    return CeefaxFeedSubscriber(feed_dir)
