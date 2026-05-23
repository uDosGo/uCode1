"""
ACS Disk Image — Handler for ACS .dsk Disk Images

Supports loading ACS game disk images (.dsk format) into the emulator's
memory. Handles Apple DOS 3.3 disk format (16-sector, 35-track) and
raw binary dumps.

Disk Format (Apple DOS 3.3):
    - 35 tracks, 16 sectors per track
    - 256 bytes per sector
    - Total: 35 * 16 * 256 = 143,360 bytes (140KB)
    - Tracks 0-2: DOS operating system
    - Tracks 2+: File storage
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, BinaryIO
import struct
import os


@dataclass
class ACS_DiskFormat:
    """Describes a disk image format"""
    name: str
    tracks: int
    sectors_per_track: int
    bytes_per_sector: int
    description: str = ""

    @property
    def total_size(self) -> int:
        """Total size of the disk image in bytes"""
        return self.tracks * self.sectors_per_track * self.bytes_per_sector


# Standard disk formats
DISK_FORMATS: Dict[str, ACS_DiskFormat] = {
    "dos33": ACS_DiskFormat(
        "DOS 3.3", 35, 16, 256,
        "Apple DOS 3.3 (140KB, 35 tracks, 16 sectors, 256 bytes/sector)"
    ),
    "raw": ACS_DiskFormat(
        "Raw", 1, 1, 0x8000,
        "Raw binary dump (32KB, loaded at 0x8000)"
    ),
    "nib": ACS_DiskFormat(
        "NIB", 35, 16, 256,
        "Apple NIB format (140KB, with nibble encoding)"
    ),
}


@dataclass
class DiskSector:
    """A single disk sector"""
    track: int
    sector: int
    data: bytes
    valid: bool = True


@dataclass
class DiskTrack:
    """A single disk track"""
    number: int
    sectors: Dict[int, DiskSector] = field(default_factory=dict)


class ACS_DiskImage:
    """
    Handler for ACS disk images (.dsk format).

    Supports loading disk images, reading/writing sectors, and
    loading game data into the emulator's memory.
    """

    def __init__(self, format_name: str = "dos33"):
        """
        Initialize disk image handler.

        Args:
            format_name: Disk format name ("dos33", "raw", "nib")
        """
        self.format = DISK_FORMATS.get(format_name, DISK_FORMATS["dos33"])
        self.tracks: Dict[int, DiskTrack] = {}
        self._loaded_path: Optional[str] = None
        self._dirty: bool = False

    # ── Loading ────────────────────────────────────────────────────

    def load(self, path: str) -> int:
        """Load a disk image from file.

        Args:
            path: Path to .dsk file

        Returns:
            Number of bytes loaded

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file size doesn't match expected format
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Disk image not found: {path}")

        with open(path, 'rb') as f:
            data = f.read()

        expected_size = self.format.total_size
        if len(data) != expected_size:
            raise ValueError(
                f"File size mismatch: got {len(data)} bytes, "
                f"expected {expected_size} for {self.format.name}"
            )

        self._parse_dos33(data)
        self._loaded_path = path
        self._dirty = False
        return len(data)

    def load_raw(self, path: str, load_address: int = 0x8000) -> bytes:
        """Load a raw binary file (not a disk image).

        Args:
            path: Path to binary file
            load_address: Where this would be loaded in memory

        Returns:
            Raw file data
        """
        with open(path, 'rb') as f:
            data = f.read()
        self._loaded_path = path
        return data

    def _parse_dos33(self, data: bytes) -> None:
        """Parse DOS 3.3 format disk image."""
        self.tracks.clear()
        sector_size = self.format.bytes_per_sector
        sectors_per_track = self.format.sectors_per_track

        for track_num in range(self.format.tracks):
            track = DiskTrack(number=track_num)
            for sector_num in range(sectors_per_track):
                offset = (track_num * sectors_per_track + sector_num) * sector_size
                sector_data = data[offset:offset + sector_size]
                track.sectors[sector_num] = DiskSector(
                    track=track_num,
                    sector=sector_num,
                    data=sector_data,
                )
            self.tracks[track_num] = track

    # ── Sector Access ──────────────────────────────────────────────

    def read_sector(self, track: int, sector: int) -> Optional[bytes]:
        """Read a sector from the disk image.

        Args:
            track: Track number (0-34)
            sector: Sector number (0-15)

        Returns:
            Sector data as bytes, or None if not found
        """
        track_data = self.tracks.get(track)
        if track_data is None:
            return None
        sector_data = track_data.sectors.get(sector)
        if sector_data is None:
            return None
        return sector_data.data

    def write_sector(self, track: int, sector: int, data: bytes) -> None:
        """Write data to a sector.

        Args:
            track: Track number
            sector: Sector number
            data: Sector data (must match sector size)
        """
        if len(data) != self.format.bytes_per_sector:
            raise ValueError(
                f"Sector data size mismatch: got {len(data)} bytes, "
                f"expected {self.format.bytes_per_sector}"
            )

        if track not in self.tracks:
            self.tracks[track] = DiskTrack(number=track)

        self.tracks[track].sectors[sector] = DiskSector(
            track=track,
            sector=sector,
            data=data,
        )
        self._dirty = True

    # ── Loading Game Data into Memory ──────────────────────────────

    def load_into_memory(self, memory, start_track: int = 2,
                         start_sector: int = 0, num_sectors: Optional[int] = None,
                         dest_address: int = 0x8000) -> int:
        """Load sectors from disk into emulator memory.

        Args:
            memory: ACS_Memory instance
            start_track: Starting track
            start_sector: Starting sector
            num_sectors: Number of sectors to load (None = all remaining)
            dest_address: Destination memory address

        Returns:
            Number of bytes loaded
        """
        loaded = 0
        sector_count = 0
        max_sectors = num_sectors or (self.format.tracks * self.format.sectors_per_track)

        for track_num in range(start_track, self.format.tracks):
            track = self.tracks.get(track_num)
            if track is None:
                continue

            sector_nums = sorted(track.sectors.keys())
            for sector_num in sector_nums:
                if sector_count >= max_sectors:
                    return loaded

                if sector_num < start_sector and track_num == start_track:
                    continue

                sector = track.sectors[sector_num]
                for i, b in enumerate(sector.data):
                    memory.write_byte(dest_address + loaded + i, b)

                loaded += len(sector.data)
                sector_count += 1

        return loaded

    # ── Save ───────────────────────────────────────────────────────

    def save(self, path: Optional[str] = None) -> None:
        """Save the disk image to a file.

        Args:
            path: Output path (uses loaded path if None)
        """
        output_path = path or self._loaded_path
        if output_path is None:
            raise ValueError("No output path specified")

        data = bytearray()
        sectors_per_track = self.format.sectors_per_track
        sector_size = self.format.bytes_per_sector

        for track_num in range(self.format.tracks):
            track = self.tracks.get(track_num, DiskTrack(number=track_num))
            for sector_num in range(sectors_per_track):
                sector = track.sectors.get(sector_num)
                if sector:
                    data.extend(sector.data)
                else:
                    data.extend(b'\x00' * sector_size)

        with open(output_path, 'wb') as f:
            f.write(data)

        self._dirty = False

    # ── Properties ─────────────────────────────────────────────────

    @property
    def is_loaded(self) -> bool:
        """Check if a disk image is loaded."""
        return len(self.tracks) > 0

    @property
    def is_dirty(self) -> bool:
        """Check if the disk image has unsaved changes."""
        return self._dirty

    @property
    def loaded_path(self) -> Optional[str]:
        """Get the loaded file path."""
        return self._loaded_path

    def get_info(self) -> Dict[str, Any]:
        """Get information about the loaded disk image."""
        total_sectors = sum(
            len(track.sectors) for track in self.tracks.values()
        )
        return {
            "format": self.format.name,
            "tracks": self.format.tracks,
            "sectors_per_track": self.format.sectors_per_track,
            "bytes_per_sector": self.format.bytes_per_sector,
            "total_sectors": total_sectors,
            "loaded_path": self._loaded_path,
            "dirty": self._dirty,
        }
