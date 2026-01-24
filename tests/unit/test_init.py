"""Tests for Beatify integration initialization."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_123"
    entry.data = {}
    return entry


@pytest.mark.asyncio
async def test_async_unload_entry_handles_missing_data(mock_hass, mock_config_entry):
    """Test that unload handles case where data doesn't exist."""
    from custom_components.beatify import async_unload_entry

    # Don't setup, just try to unload
    result = await async_unload_entry(mock_hass, mock_config_entry)

    # Should still return True and not raise
    assert result is True


@pytest.mark.asyncio
async def test_async_unload_entry_cleans_up_existing_data(mock_hass, mock_config_entry):
    """Test that unload removes existing domain data."""
    from custom_components.beatify import async_unload_entry
    from custom_components.beatify.const import DOMAIN

    # Manually set up domain data (simulating post-setup state)
    mock_hass.data[DOMAIN] = {
        "entry_id": mock_config_entry.entry_id,
        "game": MagicMock(),
    }

    # Unload
    result = await async_unload_entry(mock_hass, mock_config_entry)

    assert result is True
    assert DOMAIN not in mock_hass.data


def test_module_imports():
    """Test that module can be imported without errors."""
    from custom_components.beatify import async_setup_entry, async_unload_entry

    assert callable(async_setup_entry)
    assert callable(async_unload_entry)


def test_domain_constant():
    """Test that DOMAIN constant is correct."""
    from custom_components.beatify.const import DOMAIN

    assert DOMAIN == "beatify"
