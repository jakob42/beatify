"""Game statistics tracking service for Beatify."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class StatsService:
    """Service for tracking game statistics."""

    def __init__(self, hass: HomeAssistant) -> None:
        """
        Initialize stats service.

        Args:
            hass: Home Assistant instance

        """
        self._hass = hass
        self._stats_file = Path(hass.config.path("beatify/stats.json"))
        self._stats: dict[str, Any] = self._empty_stats()

    def _empty_stats(self) -> dict[str, Any]:
        """Return empty stats structure."""
        return {
            "version": 1,
            "games": [],
            "playlists": {},
            "all_time": {
                "games_played": 0,
                "highest_avg_score": 0.0,
                "highest_avg_game_id": None,
            },
        }

    async def load(self) -> None:
        """Load stats from file or create empty structure."""
        try:
            if self._stats_file.exists():
                content = await self._hass.async_add_executor_job(
                    self._stats_file.read_text
                )
                self._stats = json.loads(content)
                _LOGGER.debug(
                    "Loaded stats: %d games played",
                    self._stats.get("all_time", {}).get("games_played", 0),
                )
            else:
                _LOGGER.debug("No stats file found, starting fresh")
                self._stats = self._empty_stats()
        except (json.JSONDecodeError, KeyError, TypeError) as err:
            _LOGGER.warning("Stats file corrupted, recreating: %s", err)
            self._stats = self._empty_stats()
            await self.save()

    async def save(self) -> None:
        """Persist stats to file."""
        try:
            # Ensure directory exists
            await self._hass.async_add_executor_job(
                self._stats_file.parent.mkdir, 0o755, True, True
            )
            # Write stats
            content = json.dumps(self._stats, indent=2)
            await self._hass.async_add_executor_job(
                self._stats_file.write_text, content
            )
            _LOGGER.debug("Stats saved to %s", self._stats_file)
        except OSError as err:
            _LOGGER.error("Failed to save stats: %s", err)

    async def record_game(self, game_summary: dict) -> dict:
        """
        Record completed game and return comparison data.

        Args:
            game_summary: Dict with playlist, rounds, player_count, winner,
                         winner_score, total_points

        Returns:
            Comparison data dict for frontend display

        """
        # AC8: Don't record games with 0 players
        if game_summary.get("player_count", 0) == 0:
            _LOGGER.debug("Skipping stats recording for game with 0 players")
            return self.get_game_comparison(0.0)

        # Calculate average score per round
        rounds = game_summary.get("rounds", 1)
        player_count = game_summary.get("player_count", 1)
        total_points = game_summary.get("total_points", 0)

        # Avoid division by zero
        if rounds * player_count == 0:
            avg_score_per_round = 0.0
        else:
            avg_score_per_round = total_points / (rounds * player_count)

        # Create game entry
        game_id = str(uuid.uuid4())[:8]
        game_entry = {
            "id": game_id,
            "date": datetime.now(timezone.utc).isoformat(),
            "playlist": game_summary.get("playlist", "unknown"),
            "rounds": rounds,
            "player_count": player_count,
            "winner": game_summary.get("winner", "Unknown"),
            "winner_score": game_summary.get("winner_score", 0),
            "avg_score_per_round": round(avg_score_per_round, 2),
            "total_points": total_points,
        }

        # Store comparison before updating stats
        comparison = self.get_game_comparison(avg_score_per_round)

        # Add to games list
        self._stats["games"].append(game_entry)

        # Update playlist stats
        playlist_key = game_entry["playlist"]
        if playlist_key not in self._stats["playlists"]:
            self._stats["playlists"][playlist_key] = {
                "times_played": 0,
                "total_rounds": 0,
                "avg_score_per_round": 0.0,
            }

        playlist_stats = self._stats["playlists"][playlist_key]
        playlist_stats["times_played"] += 1
        playlist_stats["total_rounds"] += rounds

        # Update all-time stats
        all_time = self._stats["all_time"]
        all_time["games_played"] += 1

        # Check for new high score
        if avg_score_per_round > all_time["highest_avg_score"]:
            all_time["highest_avg_score"] = round(avg_score_per_round, 2)
            all_time["highest_avg_game_id"] = game_id
            comparison["is_new_record"] = True

        # Save to file
        await self.save()

        _LOGGER.info(
            "Recorded game %s: %.2f avg pts/round, %d players, %d rounds",
            game_id,
            avg_score_per_round,
            player_count,
            rounds,
        )

        return comparison

    def get_game_comparison(self, avg_score: float) -> dict:
        """
        Compare current game avg to all-time avg.

        Args:
            avg_score: Current game's average score per round

        Returns:
            Comparison dict with all relevant data

        """
        all_time = self._stats["all_time"]
        games_played = all_time["games_played"]
        all_time_avg = self.all_time_avg
        highest_avg = all_time["highest_avg_score"]

        is_first_game = games_played == 0
        is_new_record = not is_first_game and avg_score > highest_avg
        difference = avg_score - all_time_avg if not is_first_game else 0.0

        return {
            "avg_score": round(avg_score, 2),
            "all_time_avg": round(all_time_avg, 2),
            "difference": round(difference, 2),
            "is_new_record": is_new_record,
            "is_first_game": is_first_game,
            "is_above_average": difference > 0 if not is_first_game else False,
        }

    def get_motivational_message(self, comparison: dict) -> dict | None:
        """
        Generate motivational message based on performance.

        Args:
            comparison: Comparison dict from get_game_comparison

        Returns:
            Dict with type and message, or None for below average

        """
        if comparison.get("is_first_game"):
            return {"type": "first", "message": "First game! Setting the benchmark"}

        if comparison.get("is_new_record"):
            return {"type": "record", "message": "New Record! Highest scoring game ever!"}

        diff = comparison.get("difference", 0)
        if diff > 5:
            return {"type": "strong", "message": f"Excellent! {diff:.1f} pts above average"}
        if diff > 0:
            return {"type": "above", "message": f"Strong game! {diff:.1f} pts above average"}
        if diff > -5:
            return {
                "type": "close",
                "message": f"Close to average! Just {abs(diff):.1f} pts below",
            }

        # No message for significantly below average
        return None

    @property
    def all_time_avg(self) -> float:
        """
        Get all-time weighted average score per round.

        Returns:
            Weighted average across all games, or 0.0 if no games

        """
        games = self._stats.get("games", [])
        if not games:
            return 0.0

        # Weighted average by rounds * players
        total_weighted = 0.0
        total_weight = 0

        for game in games:
            weight = game.get("rounds", 1) * game.get("player_count", 1)
            avg = game.get("avg_score_per_round", 0.0)
            total_weighted += avg * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return total_weighted / total_weight

    @property
    def games_played(self) -> int:
        """Get total games played."""
        return self._stats.get("all_time", {}).get("games_played", 0)

    async def get_summary(self) -> dict:
        """Get stats summary for admin UI."""
        all_time = self._stats.get("all_time", {})
        return {
            "games_played": all_time.get("games_played", 0),
            "highest_avg_score": all_time.get("highest_avg_score", 0.0),
            "all_time_avg": round(self.all_time_avg, 2),
        }

    async def get_history(self, limit: int = 10) -> list[dict]:
        """
        Get recent game history.

        Args:
            limit: Maximum number of games to return

        Returns:
            List of recent game entries, newest first

        """
        games = self._stats.get("games", [])
        # Return newest first
        return list(reversed(games[-limit:]))
