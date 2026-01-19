"""Playlist discovery and validation for Beatify."""

from __future__ import annotations

import asyncio
import json
import logging
import random
from pathlib import Path
from typing import TYPE_CHECKING, Any

from custom_components.beatify.const import PLAYLIST_DIR

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class PlaylistManager:
    """Manages song selection and played tracking."""

    def __init__(self, songs: list[dict[str, Any]]) -> None:
        """
        Initialize with list of songs from loaded playlists.

        Each song dict must have: year, uri, fun_fact

        Args:
            songs: List of song dictionaries

        """
        self._songs = songs.copy()
        self._played_uris: set[str] = set()

    def get_next_song(self) -> dict[str, Any] | None:
        """
        Get random unplayed song.

        Returns:
            Song dict or None if all songs played

        """
        available = [s for s in self._songs if s["uri"] not in self._played_uris]
        if not available:
            return None
        return random.choice(available)  # noqa: S311

    def mark_played(self, uri: str) -> None:
        """
        Mark a song as played.

        Args:
            uri: Song URI to mark as played

        """
        self._played_uris.add(uri)

    def reset(self) -> None:
        """Reset played tracking for new game."""
        self._played_uris.clear()

    def is_exhausted(self) -> bool:
        """
        Check if all songs have been played.

        Returns:
            True if all songs have been played

        """
        return len(self._played_uris) >= len(self._songs)

    def get_remaining_count(self) -> int:
        """
        Get count of unplayed songs.

        Returns:
            Number of songs not yet played

        """
        return len(self._songs) - len(self._played_uris)

    def get_total_count(self) -> int:
        """
        Get total song count.

        Returns:
            Total number of songs in playlist

        """
        return len(self._songs)

# Validation constants
MIN_YEAR = 1900
MAX_YEAR = 2030


def get_playlist_directory(hass: HomeAssistant) -> Path:
    """Get the playlist directory path."""
    return Path(hass.config.path(PLAYLIST_DIR))


async def async_ensure_playlist_directory(hass: HomeAssistant) -> Path:
    """Ensure playlist directory exists, create if missing."""
    playlist_dir = get_playlist_directory(hass)

    if not playlist_dir.exists():
        playlist_dir.mkdir(parents=True, exist_ok=True)
        _LOGGER.info("Created playlist directory: %s", playlist_dir)

    # Copy bundled playlists if they don't exist in destination
    await _copy_bundled_playlists(playlist_dir)

    return playlist_dir


def _get_playlist_version(path: Path) -> str:
    """Get version from playlist file. Returns '0.0' if no version field."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("version", "0.0")
    except Exception:  # noqa: BLE001
        return "0.0"


def _compare_versions(v1: str, v2: str) -> int:
    """Compare version strings. Returns: -1 if v1<v2, 0 if equal, 1 if v1>v2."""
    def parse(v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in v.split("."))
    try:
        p1, p2 = parse(v1), parse(v2)
        if p1 < p2:
            return -1
        if p1 > p2:
            return 1
        return 0
    except ValueError:
        return 0


async def _copy_bundled_playlists(dest_dir: Path) -> None:
    """Copy bundled playlists to destination, updating if bundled version is newer."""
    # Bundled playlists are in custom_components/beatify/playlists/
    bundled_dir = Path(__file__).parent.parent / "playlists"

    if not bundled_dir.exists():
        return

    def _copy_file(src: Path, dst: Path) -> None:
        """Copy file contents (runs in executor)."""
        content = src.read_text(encoding="utf-8")
        dst.write_text(content, encoding="utf-8")

    def _get_versions(src: Path, dst: Path) -> tuple[str, str]:
        """Get versions from both files (runs in executor)."""
        bundled_ver = _get_playlist_version(src)
        existing_ver = _get_playlist_version(dst) if dst.exists() else "0.0"
        return bundled_ver, existing_ver

    loop = asyncio.get_event_loop()

    for playlist_file in bundled_dir.glob("*.json"):
        dest_file = dest_dir / playlist_file.name
        try:
            # Get versions
            bundled_ver, existing_ver = await loop.run_in_executor(
                None, _get_versions, playlist_file, dest_file
            )

            if not dest_file.exists():
                # New playlist - copy it
                await loop.run_in_executor(
                    None, _copy_file, playlist_file, dest_file
                )
                _LOGGER.info(
                    "Copied bundled playlist %s (v%s)", playlist_file.name, bundled_ver
                )
            elif _compare_versions(bundled_ver, existing_ver) > 0:
                # Bundled version is newer - update
                await loop.run_in_executor(
                    None, _copy_file, playlist_file, dest_file
                )
                _LOGGER.info(
                    "Updated playlist %s: v%s -> v%s",
                    playlist_file.name, existing_ver, bundled_ver
                )
            else:
                _LOGGER.debug(
                    "Playlist %s is up to date (v%s)", playlist_file.name, existing_ver
                )
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Failed to process playlist %s: %s", playlist_file.name, err)


def validate_playlist(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate playlist structure. Returns (is_valid, list_of_errors)."""
    errors: list[str] = []

    # Check required top-level fields
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        errors.append("Missing or empty 'name' field")

    songs = data.get("songs")
    if not isinstance(songs, list):
        errors.append("Missing or invalid 'songs' array")
        return (False, errors)

    if len(songs) == 0:
        errors.append("Playlist has no songs")

    # Validate each song
    for i, song in enumerate(songs):
        if not isinstance(song, dict):
            errors.append(f"Song {i+1}: not a valid object")
            continue

        # Check year
        year = song.get("year")
        if not isinstance(year, int):
            errors.append(f"Song {i+1}: missing or invalid 'year' (must be integer)")
        elif not (MIN_YEAR <= year <= MAX_YEAR):
            errors.append(f"Song {i+1}: year {year} out of range")

        # Check URI
        uri = song.get("uri")
        if not isinstance(uri, str) or not uri.strip():
            errors.append(f"Song {i+1}: missing or invalid 'uri'")

    return (len(errors) == 0, errors)


async def async_discover_playlists(hass: HomeAssistant) -> list[dict]:
    """Discover all playlist files in the playlist directory."""
    playlist_dir = get_playlist_directory(hass)
    playlists: list[dict] = []

    if not playlist_dir.exists():
        _LOGGER.debug("Playlist directory does not exist: %s", playlist_dir)
        return playlists

    def _read_file(path: Path) -> str:
        """Read file contents (runs in executor)."""
        return path.read_text(encoding="utf-8")

    loop = asyncio.get_event_loop()

    for json_file in playlist_dir.glob("*.json"):
        try:
            content = await loop.run_in_executor(None, _read_file, json_file)
            data = json.loads(content)
            is_valid, errors = validate_playlist(data)

            playlists.append({
                "path": str(json_file),
                "filename": json_file.name,
                "name": data.get("name", json_file.stem),
                "song_count": len(data.get("songs", [])),
                "is_valid": is_valid,
                "errors": errors,
            })
        except json.JSONDecodeError as e:
            playlists.append({
                "path": str(json_file),
                "filename": json_file.name,
                "name": json_file.stem,
                "song_count": 0,
                "is_valid": False,
                "errors": [f"Invalid JSON: {e}"],
            })

    _LOGGER.debug("Found %d playlists", len(playlists))
    return playlists


async def async_load_and_validate_playlist(
    path: str | Path,
) -> tuple[dict | None, list[str]]:
    """Load and validate a playlist file."""
    path = Path(path)

    if not path.exists():
        return (None, [f"File not found: {path}"])

    def _read_file(p: Path) -> str:
        """Read file contents (runs in executor)."""
        return p.read_text(encoding="utf-8")

    try:
        content = await asyncio.get_event_loop().run_in_executor(
            None, _read_file, path
        )
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return (None, [f"Invalid JSON: {e}"])

    is_valid, errors = validate_playlist(data)

    if is_valid:
        return (data, [])
    return (None, errors)
