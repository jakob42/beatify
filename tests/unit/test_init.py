"""Tests for Beatify integration initialization."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_123"
    entry.data = {}
    return entry


@pytest.fixture
def mock_playlist_functions():
    """Mock playlist directory functions to avoid filesystem operations."""
    with patch(
        "custom_components.beatify.async_ensure_playlist_directory",
        new_callable=AsyncMock,
    ) as mock_ensure, patch(
        "custom_components.beatify.async_discover_playlists",
        new_callable=AsyncMock,
    ) as mock_discover:
        mock_ensure.return_value = Path("/config/beatify/playlists")
        mock_discover.return_value = []
        yield mock_ensure, mock_discover


@pytest.fixture
def mock_media_players():
    """Mock media player discovery."""
    with patch(
        "custom_components.beatify.async_get_media_players",
        new_callable=AsyncMock,
    ) as mock_mp:
        mock_mp.return_value = []
        yield mock_mp


@pytest.mark.asyncio
async def test_async_setup_entry_initializes_domain_data(
    mock_hass, mock_config_entry, mock_playlist_functions, mock_media_players
):
    """Test that async_setup_entry initializes hass.data[DOMAIN]."""
    from custom_components.beatify import async_setup_entry
    from custom_components.beatify.const import DOMAIN

    # Mock HTTP app and router
    mock_hass.http = MagicMock()
    mock_hass.http.register_view = MagicMock()
    mock_hass.http.app.router.add_get = MagicMock()

    result = await async_setup_entry(mock_hass, mock_config_entry)

    assert result is True
    assert DOMAIN in mock_hass.data


@pytest.mark.asyncio
async def test_async_setup_entry_returns_true(
    mock_hass, mock_config_entry, mock_playlist_functions, mock_media_players
):
    """Test that async_setup_entry returns True on success."""
    from custom_components.beatify import async_setup_entry

    # Mock HTTP app and router
    mock_hass.http = MagicMock()
    mock_hass.http.register_view = MagicMock()
    mock_hass.http.app.router.add_get = MagicMock()

    result = await async_setup_entry(mock_hass, mock_config_entry)

    assert result is True


@pytest.mark.asyncio
async def test_async_unload_entry_cleans_up_data(
    mock_hass, mock_config_entry, mock_playlist_functions, mock_media_players
):
    """Test that async_unload_entry removes entry data."""
    from custom_components.beatify import async_setup_entry, async_unload_entry
    from custom_components.beatify.const import DOMAIN

    # Mock HTTP app and router
    mock_hass.http = MagicMock()
    mock_hass.http.register_view = MagicMock()
    mock_hass.http.app.router.add_get = MagicMock()

    # Setup first
    await async_setup_entry(mock_hass, mock_config_entry)
    assert DOMAIN in mock_hass.data

    # Unload
    result = await async_unload_entry(mock_hass, mock_config_entry)

    assert result is True
    assert DOMAIN not in mock_hass.data or not mock_hass.data.get(DOMAIN)


@pytest.mark.asyncio
async def test_async_unload_entry_removes_empty_domain(
    mock_hass, mock_config_entry, mock_playlist_functions, mock_media_players
):
    """Test that domain is removed when empty after unload."""
    from custom_components.beatify import async_setup_entry, async_unload_entry
    from custom_components.beatify.const import DOMAIN

    # Mock HTTP app and router
    mock_hass.http = MagicMock()
    mock_hass.http.register_view = MagicMock()
    mock_hass.http.app.router.add_get = MagicMock()

    # Setup and unload
    await async_setup_entry(mock_hass, mock_config_entry)
    await async_unload_entry(mock_hass, mock_config_entry)

    # Domain should be removed when empty
    assert DOMAIN not in mock_hass.data or not mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_async_unload_entry_handles_missing_data(mock_hass, mock_config_entry):
    """Test that unload handles case where data doesn't exist."""
    from custom_components.beatify import async_unload_entry

    # Don't setup, just try to unload
    result = await async_unload_entry(mock_hass, mock_config_entry)

    # Should still return True and not raise
    assert result is True
