"""
E2E Tests: QR Code & Player Flow (Story 2.4)

Tests the complete QR code and player page workflow:
- QR code display in lobby
- Print button functionality
- Player page game validation
- Error states for invalid/ended games
"""

from __future__ import annotations

import pytest
from playwright.async_api import Page, expect


@pytest.mark.e2e
class TestQRCodeDisplay:
    """Tests for QR code display in lobby."""

    async def test_qr_code_visible_in_lobby(
        self, page: Page, admin_page_url: str, mock_start_game: dict
    ) -> None:
        """QR code should be visible in lobby view."""
        await page.goto(admin_page_url)
        await page.wait_for_load_state("networkidle")

        # Start a game
        await page.locator(".playlist-checkbox").first.click()
        await page.locator(".media-player-radio").first.click()
        await page.locator("#start-game").click()

        # QR code should be visible
        qr_code = page.locator("#qr-code")
        await expect(qr_code).to_be_visible()

    async def test_qr_code_has_content(
        self, page: Page, admin_page_url: str, mock_start_game: dict
    ) -> None:
        """QR code container should have generated content."""
        await page.goto(admin_page_url)
        await page.wait_for_load_state("networkidle")

        # Start a game
        await page.locator(".playlist-checkbox").first.click()
        await page.locator(".media-player-radio").first.click()
        await page.locator("#start-game").click()

        # QR code should contain canvas or img element
        qr_code = page.locator("#qr-code")
        await expect(qr_code.locator("canvas, img")).to_be_attached()

    async def test_join_url_displayed(
        self, page: Page, admin_page_url: str, mock_start_game: dict
    ) -> None:
        """Join URL should be displayed below QR code."""
        await page.goto(admin_page_url)
        await page.wait_for_load_state("networkidle")

        # Start a game
        await page.locator(".playlist-checkbox").first.click()
        await page.locator(".media-player-radio").first.click()
        await page.locator("#start-game").click()

        # Join URL should contain the game path
        join_url = page.locator("#join-url")
        await expect(join_url).to_be_visible()
        await expect(join_url).to_contain_text("/beatify/play?game=")

    async def test_qr_code_has_aria_label(
        self, page: Page, admin_page_url: str, mock_start_game: dict
    ) -> None:
        """QR code should have accessibility label."""
        await page.goto(admin_page_url)
        await page.wait_for_load_state("networkidle")

        # Start a game
        await page.locator(".playlist-checkbox").first.click()
        await page.locator(".media-player-radio").first.click()
        await page.locator("#start-game").click()

        # Check aria-label
        qr_code = page.locator("#qr-code")
        aria_label = await qr_code.get_attribute("aria-label")
        assert aria_label is not None
        assert "QR" in aria_label or "qr" in aria_label.lower()


@pytest.mark.e2e
class TestPrintQRCode:
    """Tests for print QR code functionality."""

    async def test_print_button_visible(
        self, page: Page, admin_page_url: str, mock_start_game: dict
    ) -> None:
        """Print button should be visible in lobby."""
        await page.goto(admin_page_url)
        await page.wait_for_load_state("networkidle")

        # Start a game
        await page.locator(".playlist-checkbox").first.click()
        await page.locator(".media-player-radio").first.click()
        await page.locator("#start-game").click()

        # Print button should be visible
        print_btn = page.locator("#print-qr")
        await expect(print_btn).to_be_visible()

    async def test_print_button_enabled(
        self, page: Page, admin_page_url: str, mock_start_game: dict
    ) -> None:
        """Print button should be enabled."""
        await page.goto(admin_page_url)
        await page.wait_for_load_state("networkidle")

        # Start a game
        await page.locator(".playlist-checkbox").first.click()
        await page.locator(".media-player-radio").first.click()
        await page.locator("#start-game").click()

        # Print button should be enabled
        print_btn = page.locator("#print-qr")
        await expect(print_btn).to_be_enabled()


@pytest.mark.e2e
class TestPlayerPage:
    """Tests for player page game validation."""

    async def test_player_page_loads(
        self, page: Page, player_page_url: str
    ) -> None:
        """Player page should load."""
        await page.goto(player_page_url)
        await page.wait_for_load_state("networkidle")

        # Main container should be present
        container = page.locator(".player-container")
        await expect(container).to_be_visible()

    async def test_invalid_game_id_shows_not_found(
        self, page: Page, player_page_url_invalid: str
    ) -> None:
        """Invalid game ID should show not found view."""
        await page.goto(player_page_url_invalid)
        await page.wait_for_load_state("networkidle")

        # Not found view should be visible
        not_found = page.locator("#not-found-view")
        await expect(not_found).to_be_visible()

    async def test_no_game_id_shows_not_found(
        self, page: Page, player_page_url_no_game: str
    ) -> None:
        """No game ID in URL should show not found view."""
        await page.goto(player_page_url_no_game)
        await page.wait_for_load_state("networkidle")

        # Not found view should be visible
        not_found = page.locator("#not-found-view")
        await expect(not_found).to_be_visible()

    async def test_valid_game_shows_join_view(
        self, page: Page, player_page_url_valid: str, mock_game_status_valid: dict
    ) -> None:
        """Valid game ID should show join view."""
        await page.goto(player_page_url_valid)
        await page.wait_for_load_state("networkidle")

        # Join view should be visible
        join_view = page.locator("#join-view")
        await expect(join_view).to_be_visible()

    async def test_ended_game_shows_ended_view(
        self, page: Page, player_page_url_ended: str, mock_game_status_ended: dict
    ) -> None:
        """Ended game should show ended view."""
        await page.goto(player_page_url_ended)
        await page.wait_for_load_state("networkidle")

        # Ended view should be visible
        ended_view = page.locator("#ended-view")
        await expect(ended_view).to_be_visible()

    async def test_refresh_button_exists(
        self, page: Page, player_page_url_invalid: str
    ) -> None:
        """Refresh button should exist on not found view."""
        await page.goto(player_page_url_invalid)
        await page.wait_for_load_state("networkidle")

        # Refresh button should be present
        refresh_btn = page.locator("#refresh-btn")
        await expect(refresh_btn).to_be_visible()

    async def test_refresh_button_clickable(
        self, page: Page, player_page_url_invalid: str
    ) -> None:
        """Refresh button should be clickable."""
        await page.goto(player_page_url_invalid)
        await page.wait_for_load_state("networkidle")

        # Refresh button should be enabled and clickable
        refresh_btn = page.locator("#refresh-btn")
        await expect(refresh_btn).to_be_enabled()


@pytest.mark.e2e
class TestResponsiveQRCode:
    """Tests for responsive QR code sizing."""

    async def test_qr_visible_on_mobile(
        self, page: Page, admin_page_url: str, mock_start_game: dict
    ) -> None:
        """QR code should be visible on mobile viewport."""
        # Set mobile viewport
        await page.set_viewport_size({"width": 375, "height": 667})

        await page.goto(admin_page_url)
        await page.wait_for_load_state("networkidle")

        # Start a game
        await page.locator(".playlist-checkbox").first.click()
        await page.locator(".media-player-radio").first.click()
        await page.locator("#start-game").click()

        # QR code should still be visible
        qr_code = page.locator("#qr-code")
        await expect(qr_code).to_be_visible()

    async def test_qr_visible_on_tablet(
        self, page: Page, admin_page_url: str, mock_start_game: dict
    ) -> None:
        """QR code should be visible on tablet viewport."""
        # Set tablet viewport
        await page.set_viewport_size({"width": 768, "height": 1024})

        await page.goto(admin_page_url)
        await page.wait_for_load_state("networkidle")

        # Start a game
        await page.locator(".playlist-checkbox").first.click()
        await page.locator(".media-player-radio").first.click()
        await page.locator("#start-game").click()

        # QR code should be visible
        qr_code = page.locator("#qr-code")
        await expect(qr_code).to_be_visible()

    async def test_qr_visible_on_desktop(
        self, page: Page, admin_page_url: str, mock_start_game: dict
    ) -> None:
        """QR code should be visible on desktop viewport."""
        # Set desktop viewport
        await page.set_viewport_size({"width": 1920, "height": 1080})

        await page.goto(admin_page_url)
        await page.wait_for_load_state("networkidle")

        # Start a game
        await page.locator(".playlist-checkbox").first.click()
        await page.locator(".media-player-radio").first.click()
        await page.locator("#start-game").click()

        # QR code should be visible
        qr_code = page.locator("#qr-code")
        await expect(qr_code).to_be_visible()
