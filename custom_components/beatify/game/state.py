"""Game state management for Beatify."""

from __future__ import annotations

import logging
import secrets
import time
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

_LOGGER = logging.getLogger(__name__)


class GamePhase(Enum):
    """Game phase states."""

    LOBBY = "LOBBY"
    PLAYING = "PLAYING"
    REVEAL = "REVEAL"
    END = "END"
    PAUSED = "PAUSED"


class GameState:
    """Manages game state and phase transitions."""

    def __init__(self, time_fn: Callable[[], float] | None = None) -> None:
        """Initialize game state.

        Args:
            time_fn: Optional time function for testing. Defaults to time.time.
        """
        self._now = time_fn or time.time
        self.game_id: str | None = None
        self.phase: GamePhase = GamePhase.LOBBY
        self.playlists: list[str] = []
        self.songs: list[dict[str, Any]] = []
        self.media_player: str | None = None
        self.join_url: str | None = None
        self.players: dict[str, dict[str, Any]] = {}

    def create_game(
        self,
        playlists: list[str],
        songs: list[dict[str, Any]],
        media_player: str,
        base_url: str,
    ) -> dict[str, Any]:
        """Create a new game session.

        Args:
            playlists: List of playlist file paths
            songs: List of song dicts loaded from playlists
            media_player: Entity ID of media player
            base_url: HA base URL for join URL construction

        Returns:
            dict with game_id, join_url, song_count, phase
        """
        self.game_id = secrets.token_urlsafe(8)
        self.phase = GamePhase.LOBBY
        self.playlists = playlists
        self.songs = songs
        self.media_player = media_player
        self.join_url = f"{base_url}/beatify/play?game={self.game_id}"
        self.players = {}

        _LOGGER.info("Game created: %s with %d songs", self.game_id, len(songs))

        return {
            "game_id": self.game_id,
            "join_url": self.join_url,
            "phase": self.phase.value,
            "song_count": len(songs),
        }

    def get_state(self) -> dict[str, Any] | None:
        """Get current game state for broadcast.

        Returns:
            Game state dict or None if no active game
        """
        if not self.game_id:
            return None

        return {
            "game_id": self.game_id,
            "phase": self.phase.value,
            "player_count": len(self.players),
            "join_url": self.join_url,
        }

    def end_game(self) -> None:
        """End the current game and reset state."""
        _LOGGER.info("Game ended: %s", self.game_id)
        self.game_id = None
        self.phase = GamePhase.LOBBY
        self.playlists = []
        self.songs = []
        self.media_player = None
        self.join_url = None
        self.players = {}
