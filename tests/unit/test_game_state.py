"""
Unit Tests: Game State Machine

Tests the game state transitions and invariants:
- LOBBY → PLAYING → REVEAL → END lifecycle
- Player management (join, reconnect, disconnect)
- Round progression
- Timer mechanics with time injection

State Machine (from architecture):
    LOBBY ─[start_game]─► PLAYING ─[reveal]─► REVEAL ─[next_round]─┐
      ▲                                          │                 │
      │                                          ▼                 │
      └────────────────────[end_game]──────────END◄────────────────┘
"""

from __future__ import annotations

import pytest

from tests.support.factories import create_player


# =============================================================================
# STATE TRANSITION TESTS
# =============================================================================


@pytest.mark.unit
class TestStateTransitions:
    """Tests for valid state machine transitions."""

    def test_initial_state_is_lobby(self, game_state):
        """New game should start in LOBBY phase."""
        assert game_state.phase == "LOBBY"
        assert game_state.round == 0

    def test_cannot_start_without_players(self, game_state):
        """Starting game with no players should raise error."""
        with pytest.raises(ValueError, match="at least 2 players"):
            game_state.start_game()

    def test_cannot_start_with_one_player(self, game_state):
        """Starting game with 1 player should raise error."""
        game_state.add_player("Alice", "session-1")
        with pytest.raises(ValueError, match="at least 2 players"):
            game_state.start_game()

    def test_start_game_with_two_players(self, game_state):
        """Game should start with 2+ players."""
        game_state.add_player("Alice", "session-1")
        game_state.add_player("Bob", "session-2")
        game_state.start_game()

        assert game_state.phase == "PLAYING"
        assert game_state.round == 1

    def test_cannot_start_twice(self, game_state):
        """Starting an already-started game should raise error."""
        game_state.add_player("Alice", "session-1")
        game_state.add_player("Bob", "session-2")
        game_state.start_game()

        with pytest.raises(ValueError, match="Cannot start game from phase"):
            game_state.start_game()


# =============================================================================
# PLAYER MANAGEMENT TESTS
# =============================================================================


@pytest.mark.unit
class TestPlayerManagement:
    """Tests for player join/leave/reconnect."""

    def test_add_player(self, game_state):
        """Adding a player should create player entry."""
        player = game_state.add_player("Alice", "session-1")

        assert player["name"] == "Alice"
        assert player["session_id"] == "session-1"
        assert player["score"] == 0
        assert player["connected"] is True

    def test_add_multiple_players(self, game_state):
        """Multiple players should be tracked."""
        game_state.add_player("Alice", "session-1")
        game_state.add_player("Bob", "session-2")
        game_state.add_player("Charlie", "session-3")

        assert len(game_state.players) == 3
        names = [p["name"] for p in game_state.players]
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names


# =============================================================================
# SERIALIZATION TESTS
# =============================================================================


@pytest.mark.unit
class TestStateSerialization:
    """Tests for state → dict conversion (WebSocket broadcast)."""

    def test_to_dict_basic(self, game_state):
        """Basic serialization should include core fields."""
        state_dict = game_state.to_dict()

        assert "phase" in state_dict
        assert "round" in state_dict
        assert "total_rounds" in state_dict
        assert "players" in state_dict

    def test_to_dict_with_players(self, game_state):
        """Serialization should include player data."""
        game_state.add_player("Alice", "session-1")
        game_state.add_player("Bob", "session-2")

        state_dict = game_state.to_dict()

        assert len(state_dict["players"]) == 2
        assert state_dict["players"][0]["name"] == "Alice"


# =============================================================================
# TIME INJECTION TESTS
# =============================================================================


@pytest.mark.unit
class TestTimeInjection:
    """Tests for deterministic time control."""

    def test_frozen_time(self, game_state, frozen_time):
        """Game state should use injected time function."""
        assert game_state._now() == frozen_time
        assert game_state._now() == 1000.0

    def test_time_does_not_advance(self, game_state):
        """Frozen time should remain constant (no real time passing)."""
        time1 = game_state._now()
        # Simulate some operations
        game_state.add_player("Alice", "session-1")
        game_state.add_player("Bob", "session-2")
        time2 = game_state._now()

        assert time1 == time2  # Time didn't advance


# =============================================================================
# FACTORY INTEGRATION TESTS
# =============================================================================


@pytest.mark.unit
class TestFactoryIntegration:
    """Tests demonstrating factory usage with game state."""

    def test_factory_players_unique(self):
        """Factory should generate unique players."""
        player1 = create_player()
        player2 = create_player()

        assert player1.session_id != player2.session_id
        assert player1.name != player2.name

    def test_factory_with_overrides(self):
        """Factory overrides should be applied."""
        player = create_player(name="Custom", score=100)

        assert player.name == "Custom"
        assert player.score == 100

    def test_add_factory_player_to_game(self, game_state):
        """Factory-created players should integrate with game state."""
        player = create_player(name="TestPlayer")
        game_state.add_player(player.name, player.session_id)

        assert len(game_state.players) == 1
        assert game_state.players[0]["name"] == "TestPlayer"


# =============================================================================
# GAME SESSION TESTS (Story 2.3)
# =============================================================================


@pytest.mark.unit
class TestGameSessionCreation:
    """Tests for game session creation (Story 2.3)."""

    def test_create_game_returns_valid_game_id(self):
        """Game creation returns URL-safe game_id."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        result = state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://192.168.1.100:8123",
        )

        # Game ID should be 11 characters (8 bytes base64url encoded)
        assert len(result["game_id"]) == 11
        # URL-safe characters only
        assert all(c.isalnum() or c in "-_" for c in result["game_id"])

    def test_create_game_sets_lobby_phase(self):
        """Initial phase is LOBBY after create_game."""
        from custom_components.beatify.game.state import GamePhase, GameState

        state = GameState()
        result = state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://192.168.1.100:8123",
        )

        assert result["phase"] == "LOBBY"
        assert state.phase == GamePhase.LOBBY

    def test_create_game_unique_ids(self):
        """Game_id is unique across multiple creations."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        ids = set()

        for _ in range(100):
            result = state.create_game(
                playlists=["playlist1.json"],
                songs=[{"year": 1985, "uri": "spotify:track:test"}],
                media_player="media_player.test",
                base_url="http://test.local:8123",
            )
            ids.add(result["game_id"])

        # All 100 game IDs should be unique
        assert len(ids) == 100

    def test_create_game_stores_playlists(self):
        """Playlists are stored correctly."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        playlists = ["playlist1.json", "playlist2.json"]

        state.create_game(
            playlists=playlists,
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        assert state.playlists == playlists

    def test_create_game_stores_media_player(self):
        """Media_player is stored correctly."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        media_player = "media_player.living_room"

        state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player=media_player,
            base_url="http://test.local:8123",
        )

        assert state.media_player == media_player

    def test_create_game_constructs_join_url(self):
        """Join_url is constructed correctly."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        base_url = "http://192.168.1.100:8123"

        result = state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url=base_url,
        )

        expected_url = f"{base_url}/beatify/play?game={result['game_id']}"
        assert result["join_url"] == expected_url
        assert state.join_url == expected_url

    def test_create_game_returns_song_count(self):
        """Song_count is returned correctly."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        songs = [
            {"year": 1985, "uri": "spotify:track:1"},
            {"year": 1990, "uri": "spotify:track:2"},
            {"year": 1995, "uri": "spotify:track:3"},
        ]

        result = state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        assert result["song_count"] == 3


@pytest.mark.unit
class TestGameSessionState:
    """Tests for get_state method (Story 2.3)."""

    def test_get_state_returns_none_when_no_game(self):
        """get_state returns None when no game is active."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        assert state.get_state() is None

    def test_get_state_returns_game_data(self):
        """get_state returns correct game data."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        result = state.get_state()

        assert result is not None
        assert "game_id" in result
        assert result["phase"] == "LOBBY"
        assert result["player_count"] == 0
        assert "join_url" in result

    def test_get_state_player_count(self):
        """get_state returns correct player count."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        # Add some players
        state.players = {
            "player1": {"score": 0},
            "player2": {"score": 0},
            "player3": {"score": 0},
        }

        result = state.get_state()
        assert result["player_count"] == 3


@pytest.mark.unit
class TestGameSessionEnd:
    """Tests for end_game method (Story 2.3)."""

    def test_end_game_clears_game_id(self):
        """end_game clears the game_id."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.end_game()

        assert state.game_id is None

    def test_end_game_resets_all_state(self):
        """end_game resets all state."""
        from custom_components.beatify.game.state import GamePhase, GameState

        state = GameState()
        state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )
        state.players = {"player1": {"score": 100}}

        state.end_game()

        assert state.game_id is None
        assert state.phase == GamePhase.LOBBY
        assert state.playlists == []
        assert state.songs == []
        assert state.media_player is None
        assert state.join_url is None
        assert state.players == {}

    def test_end_game_get_state_returns_none(self):
        """get_state returns None after end_game."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.end_game()

        assert state.get_state() is None


# =============================================================================
# WEBSOCKET BROADCAST STATE TESTS (Story 2.3 Task 11.6)
# =============================================================================


@pytest.mark.unit
class TestWebSocketBroadcastState:
    """Tests for WebSocket state broadcast format."""

    def test_get_state_returns_websocket_broadcast_format(self):
        """get_state returns format suitable for WebSocket broadcast."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://192.168.1.100:8123",
        )

        result = state.get_state()

        # Verify all required fields for WebSocket broadcast
        assert "game_id" in result
        assert "phase" in result
        assert "player_count" in result
        assert "join_url" in result

        # Verify phase is string (not enum) for JSON serialization
        assert isinstance(result["phase"], str)
        assert result["phase"] == "LOBBY"

    def test_get_state_phase_is_serializable(self):
        """Phase value should be JSON-serializable string."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        result = state.get_state()

        # Should be able to serialize to JSON without error
        import json

        json_str = json.dumps(result)
        assert '"phase": "LOBBY"' in json_str

    def test_broadcast_state_includes_join_url_for_qr(self):
        """Broadcast state includes join_url for QR code generation."""
        from custom_components.beatify.game.state import GameState

        state = GameState()
        result = state.create_game(
            playlists=["playlist1.json"],
            songs=[{"year": 1985, "uri": "spotify:track:test"}],
            media_player="media_player.test",
            base_url="http://192.168.1.100:8123",
        )

        broadcast_state = state.get_state()

        # join_url should match what was returned from create_game
        assert broadcast_state["join_url"] == result["join_url"]
        assert "/beatify/play?game=" in broadcast_state["join_url"]
