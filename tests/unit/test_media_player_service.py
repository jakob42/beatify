"""
Unit Tests: MediaPlayerService

Tests media player integration for Epic 4 gameplay:
- Song playback via HA services
- Metadata retrieval from entity attributes
- Stop and volume control
- Error handling for unavailable player

Story 4.1 - AC: #2, #6, #7
"""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

# Mock homeassistant before importing beatify modules
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.components"] = MagicMock()
sys.modules["homeassistant.components.http"] = MagicMock()

from custom_components.beatify.services.media_player import MediaPlayerService


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.services = MagicMock()
    hass.services.async_call = AsyncMock()
    hass.states = MagicMock()
    return hass


@pytest.mark.unit
class TestMediaPlayerServicePlayback:
    """Tests for song playback."""

    @pytest.mark.asyncio
    async def test_play_song_calls_ha_service(self, mock_hass):
        """play_song calls the correct HA service."""
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        result = await service.play_song("spotify:track:abc123")

        assert result is True
        mock_hass.services.async_call.assert_called_once_with(
            "media_player",
            "play_media",
            {
                "entity_id": "media_player.living_room",
                "media_content_id": "spotify:track:abc123",
                "media_content_type": "music",
            },
            blocking=True,
        )

    @pytest.mark.asyncio
    async def test_play_song_returns_false_on_error(self, mock_hass):
        """play_song returns False when service call fails."""
        mock_hass.services.async_call = AsyncMock(side_effect=Exception("Service error"))
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        result = await service.play_song("spotify:track:abc123")

        assert result is False

    @pytest.mark.asyncio
    async def test_stop_calls_ha_service(self, mock_hass):
        """stop calls the correct HA service."""
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        result = await service.stop()

        assert result is True
        mock_hass.services.async_call.assert_called_once_with(
            "media_player",
            "media_stop",
            {"entity_id": "media_player.living_room"},
        )

    @pytest.mark.asyncio
    async def test_stop_returns_false_on_error(self, mock_hass):
        """stop returns False when service call fails."""
        mock_hass.services.async_call = AsyncMock(side_effect=Exception("Service error"))
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        result = await service.stop()

        assert result is False


@pytest.mark.unit
class TestMediaPlayerServiceMetadata:
    """Tests for metadata retrieval."""

    @pytest.mark.asyncio
    async def test_get_metadata_returns_entity_attributes(self, mock_hass):
        """get_metadata returns artist, title, album_art from entity."""
        mock_state = MagicMock()
        mock_state.attributes = {
            "media_artist": "Test Artist",
            "media_title": "Test Song",
            "entity_picture": "/local/image.jpg",
        }
        mock_hass.states.get.return_value = mock_state
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        result = await service.get_metadata()

        assert result["artist"] == "Test Artist"
        assert result["title"] == "Test Song"
        assert result["album_art"] == "/local/image.jpg"

    @pytest.mark.asyncio
    async def test_get_metadata_returns_defaults_when_no_state(self, mock_hass):
        """get_metadata returns defaults when entity has no state."""
        mock_hass.states.get.return_value = None
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        result = await service.get_metadata()

        assert result["artist"] == "Unknown Artist"
        assert result["title"] == "Unknown Title"
        assert result["album_art"] == "/beatify/static/img/no-artwork.svg"

    @pytest.mark.asyncio
    async def test_get_metadata_returns_defaults_for_missing_attributes(self, mock_hass):
        """get_metadata uses defaults for missing attributes."""
        mock_state = MagicMock()
        mock_state.attributes = {}  # Empty attributes
        mock_hass.states.get.return_value = mock_state
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        result = await service.get_metadata()

        assert result["artist"] == "Unknown Artist"
        assert result["title"] == "Unknown Title"
        assert result["album_art"] == "/beatify/static/img/no-artwork.svg"


@pytest.mark.unit
class TestMediaPlayerServiceVolume:
    """Tests for volume control."""

    @pytest.mark.asyncio
    async def test_set_volume_calls_ha_service(self, mock_hass):
        """set_volume calls the correct HA service."""
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        result = await service.set_volume(0.75)

        assert result is True
        mock_hass.services.async_call.assert_called_once_with(
            "media_player",
            "volume_set",
            {
                "entity_id": "media_player.living_room",
                "volume_level": 0.75,
            },
        )

    @pytest.mark.asyncio
    async def test_set_volume_clamps_to_valid_range(self, mock_hass):
        """set_volume clamps values to 0.0-1.0 range."""
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        # Test clamping to max
        await service.set_volume(1.5)
        call_args = mock_hass.services.async_call.call_args
        assert call_args[0][2]["volume_level"] == 1.0

        mock_hass.services.async_call.reset_mock()

        # Test clamping to min
        await service.set_volume(-0.5)
        call_args = mock_hass.services.async_call.call_args
        assert call_args[0][2]["volume_level"] == 0.0

    @pytest.mark.asyncio
    async def test_set_volume_returns_false_on_error(self, mock_hass):
        """set_volume returns False when service call fails."""
        mock_hass.services.async_call = AsyncMock(side_effect=Exception("Service error"))
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        result = await service.set_volume(0.5)

        assert result is False


@pytest.mark.unit
class TestMediaPlayerServiceAvailability:
    """Tests for availability checking."""

    def test_is_available_returns_true_when_state_exists(self, mock_hass):
        """is_available returns True when entity has valid state."""
        mock_state = MagicMock()
        mock_state.state = "idle"
        mock_hass.states.get.return_value = mock_state
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        assert service.is_available() is True

    def test_is_available_returns_false_when_no_state(self, mock_hass):
        """is_available returns False when entity has no state."""
        mock_hass.states.get.return_value = None
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        assert service.is_available() is False

    def test_is_available_returns_false_when_unavailable(self, mock_hass):
        """is_available returns False when entity state is 'unavailable'."""
        mock_state = MagicMock()
        mock_state.state = "unavailable"
        mock_hass.states.get.return_value = mock_state
        service = MediaPlayerService(mock_hass, "media_player.living_room")

        assert service.is_available() is False
