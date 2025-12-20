"""
Unit Tests: Scoring Logic (Story 4.6)

Tests the MVP accuracy-based scoring system:
- Exact match: 10 points
- Within ±3 years: 5 points
- Within ±5 years: 1 point
- More than 5 years off: 0 points

NOTE: Advanced scoring (speed bonus, streaks, betting) is in Epic 5.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

# Mock homeassistant before importing beatify modules
sys.modules["homeassistant"] = MagicMock()
sys.modules["homeassistant.core"] = MagicMock()
sys.modules["homeassistant.components"] = MagicMock()
sys.modules["homeassistant.components.http"] = MagicMock()

from custom_components.beatify.game.scoring import (
    apply_bet_multiplier,
    calculate_accuracy_score,
    calculate_round_score,
    calculate_speed_multiplier,
    calculate_streak_bonus,
    calculate_years_off_text,
)


# =============================================================================
# EXACT MATCH TESTS (10 points)
# =============================================================================


@pytest.mark.unit
class TestExactMatch:
    """Tests for exact year matches (10 base points)."""

    def test_exact_match_returns_10(self):
        """Exact match (0 years off) returns 10 points."""
        assert calculate_accuracy_score(1985, 1985) == 10

    def test_exact_match_various_years(self):
        """Exact match works for any year."""
        assert calculate_accuracy_score(1950, 1950) == 10
        assert calculate_accuracy_score(2000, 2000) == 10
        assert calculate_accuracy_score(2025, 2025) == 10


# =============================================================================
# CLOSE MATCH TESTS (±3 years = 5 points)
# =============================================================================


@pytest.mark.unit
class TestCloseMatch:
    """Tests for ±3 year matches (5 base points)."""

    def test_1_year_off_returns_5(self):
        """1 year off returns 5 points."""
        assert calculate_accuracy_score(1986, 1985) == 5
        assert calculate_accuracy_score(1984, 1985) == 5

    def test_2_years_off_returns_5(self):
        """2 years off returns 5 points."""
        assert calculate_accuracy_score(1987, 1985) == 5
        assert calculate_accuracy_score(1983, 1985) == 5

    def test_3_years_off_returns_5(self):
        """3 years off returns 5 points (boundary of ±3)."""
        assert calculate_accuracy_score(1988, 1985) == 5
        assert calculate_accuracy_score(1982, 1985) == 5


# =============================================================================
# NEAR MATCH TESTS (±5 years = 1 point)
# =============================================================================


@pytest.mark.unit
class TestNearMatch:
    """Tests for ±4-5 year matches (1 base point)."""

    def test_4_years_off_returns_1(self):
        """4 years off returns 1 point."""
        assert calculate_accuracy_score(1989, 1985) == 1
        assert calculate_accuracy_score(1981, 1985) == 1

    def test_5_years_off_returns_1(self):
        """5 years off returns 1 point (boundary of ±5)."""
        assert calculate_accuracy_score(1990, 1985) == 1
        assert calculate_accuracy_score(1980, 1985) == 1


# =============================================================================
# WRONG GUESS TESTS (>5 years = 0 points)
# =============================================================================


@pytest.mark.unit
class TestWrongGuess:
    """Tests for wrong guesses (>5 years off)."""

    def test_6_years_off_returns_0(self):
        """6 years off returns 0 points."""
        assert calculate_accuracy_score(1991, 1985) == 0
        assert calculate_accuracy_score(1979, 1985) == 0

    def test_10_years_off_returns_0(self):
        """10 years off returns 0 points."""
        assert calculate_accuracy_score(1995, 1985) == 0
        assert calculate_accuracy_score(1975, 1985) == 0

    def test_100_years_off_returns_0(self):
        """100 years off returns 0 points."""
        assert calculate_accuracy_score(2085, 1985) == 0
        assert calculate_accuracy_score(1885, 1985) == 0


# =============================================================================
# BOUNDARY TESTS
# =============================================================================


@pytest.mark.unit
class TestScoringBoundaries:
    """Tests for scoring boundary conditions."""

    def test_boundary_3_to_4_years(self):
        """Test transition from 5 points (3 years) to 1 point (4 years)."""
        # 3 years off = 5 points
        assert calculate_accuracy_score(1988, 1985) == 5
        # 4 years off = 1 point
        assert calculate_accuracy_score(1989, 1985) == 1

    def test_boundary_5_to_6_years(self):
        """Test transition from 1 point (5 years) to 0 points (6 years)."""
        # 5 years off = 1 point
        assert calculate_accuracy_score(1990, 1985) == 1
        # 6 years off = 0 points
        assert calculate_accuracy_score(1991, 1985) == 0


# =============================================================================
# YEARS OFF TEXT TESTS
# =============================================================================


@pytest.mark.unit
class TestYearsOffText:
    """Tests for calculate_years_off_text function."""

    def test_exact_returns_exact_text(self):
        """0 years off returns 'Exact!'."""
        assert calculate_years_off_text(0) == "Exact!"

    def test_1_year_singular(self):
        """1 year off uses singular form."""
        assert calculate_years_off_text(1) == "1 year off"

    def test_2_years_plural(self):
        """2+ years off uses plural form."""
        assert calculate_years_off_text(2) == "2 years off"

    def test_10_years_plural(self):
        """10 years off uses plural form."""
        assert calculate_years_off_text(10) == "10 years off"

    def test_100_years_plural(self):
        """Large values use plural form."""
        assert calculate_years_off_text(100) == "100 years off"


# =============================================================================
# INTEGRATION TESTS: SCORING WITH GAMESTATE
# =============================================================================


@pytest.mark.unit
class TestScoringIntegration:
    """Tests for scoring integration with GameState."""

    @pytest.mark.asyncio
    async def test_end_round_calculates_scores(self):
        """end_round calculates accuracy scores for submitted players."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        # Add player and simulate submission
        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].submit_guess(year=1985, timestamp=1000.0)

        # Set current song (normally done by start_round)
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        await state.end_round()

        # Check exact match score
        player = state.players["TestPlayer"]
        assert player.round_score == 10
        assert player.years_off == 0
        assert player.missed_round is False

    @pytest.mark.asyncio
    async def test_end_round_calculates_close_match(self):
        """end_round calculates close match (5 points)."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].submit_guess(year=1988, timestamp=1000.0)  # 3 years off
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        await state.end_round()

        player = state.players["TestPlayer"]
        assert player.round_score == 5
        assert player.years_off == 3

    @pytest.mark.asyncio
    async def test_end_round_updates_total_score(self):
        """end_round adds round_score to total score."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].score = 50  # Pre-existing score
        state.players["TestPlayer"].submit_guess(year=1985, timestamp=1000.0)
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        await state.end_round()

        # Total should be previous (50) + round (10) = 60
        assert state.players["TestPlayer"].score == 60

    @pytest.mark.asyncio
    async def test_end_round_increments_streak_on_points(self):
        """end_round increments streak when player earns points."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].streak = 2
        state.players["TestPlayer"].submit_guess(year=1988, timestamp=1000.0)  # 3 years off
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        await state.end_round()

        # Streak should increment (earned 5 points)
        assert state.players["TestPlayer"].streak == 3

    @pytest.mark.asyncio
    async def test_end_round_breaks_streak_on_zero_points(self):
        """end_round resets streak when player earns 0 points."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].streak = 5
        state.players["TestPlayer"].submit_guess(year=1970, timestamp=1000.0)  # 15 years off
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        await state.end_round()

        # Streak should reset (earned 0 points)
        assert state.players["TestPlayer"].streak == 0

    @pytest.mark.asyncio
    async def test_end_round_non_submitter_gets_zero(self):
        """end_round gives non-submitters 0 points and breaks streak."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].streak = 3
        state.players["TestPlayer"].score = 50
        # No submission
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        await state.end_round()

        player = state.players["TestPlayer"]
        assert player.round_score == 0
        assert player.years_off is None
        assert player.missed_round is True
        assert player.streak == 0
        assert player.score == 50  # Total unchanged


# =============================================================================
# REVEAL STATE TESTS
# =============================================================================


@pytest.mark.unit
class TestRevealState:
    """Tests for reveal state including scoring data."""

    @pytest.mark.asyncio
    async def test_reveal_state_includes_years_off(self):
        """Reveal state includes years_off for each player."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].submit_guess(year=1988, timestamp=1000.0)
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        await state.end_round()

        reveal_state = state.get_reveal_players_state()
        player_data = reveal_state[0]

        assert player_data["years_off"] == 3

    @pytest.mark.asyncio
    async def test_reveal_players_sorted_by_score(self):
        """Reveal state sorts players by total score descending."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        # Add players with different scores
        mock_ws = MagicMock()
        state.add_player("Low", mock_ws)
        state.add_player("High", mock_ws)
        state.add_player("Mid", mock_ws)

        state.players["Low"].score = 10
        state.players["High"].score = 100
        state.players["Mid"].score = 50

        reveal_state = state.get_reveal_players_state()

        # Should be sorted high to low
        assert reveal_state[0]["name"] == "High"
        assert reveal_state[1]["name"] == "Mid"
        assert reveal_state[2]["name"] == "Low"


# =============================================================================
# SPEED MULTIPLIER TESTS (Story 5.1)
# =============================================================================


@pytest.mark.unit
class TestSpeedMultiplier:
    """Tests for speed bonus multiplier calculation (Story 5.1)."""

    def test_instant_submission_returns_1_5x(self):
        """0 seconds elapsed → 1.5x multiplier (maximum bonus)."""
        assert calculate_speed_multiplier(0.0, 30.0) == 1.5

    def test_half_time_returns_1_25x(self):
        """15 seconds elapsed → 1.25x multiplier."""
        result = calculate_speed_multiplier(15.0, 30.0)
        assert abs(result - 1.25) < 0.001  # Float comparison

    def test_deadline_returns_1_0x(self):
        """30 seconds elapsed (deadline) → 1.0x multiplier (no bonus)."""
        assert calculate_speed_multiplier(30.0, 30.0) == 1.0

    def test_negative_time_clamped_to_0(self):
        """Negative elapsed time is clamped to 0 ratio (1.5x)."""
        assert calculate_speed_multiplier(-5.0, 30.0) == 1.5

    def test_time_exceeds_duration_clamped_to_1(self):
        """Elapsed > duration is clamped to 1.0 ratio (1.0x)."""
        assert calculate_speed_multiplier(45.0, 30.0) == 1.0

    def test_zero_duration_returns_1_0x(self):
        """Zero round duration returns 1.0x (avoid division by zero)."""
        assert calculate_speed_multiplier(10.0, 0.0) == 1.0

    def test_linear_interpolation(self):
        """Verify linear interpolation between 1.5 and 1.0."""
        # 10 seconds = 1/3 of 30 → ratio = 0.333 → mult = 1.5 - 0.5*0.333 = 1.333
        result = calculate_speed_multiplier(10.0, 30.0)
        expected = 1.5 - (0.5 * (10.0 / 30.0))
        assert abs(result - expected) < 0.001


# =============================================================================
# ROUND SCORE TESTS (Story 5.1)
# =============================================================================


@pytest.mark.unit
class TestRoundScore:
    """Tests for combined scoring with speed bonus (Story 5.1)."""

    def test_exact_match_instant_submit(self):
        """Exact match + instant submit = 10 * 1.5 = 15 pts."""
        final, base, mult = calculate_round_score(1985, 1985, 0.0, 30.0)
        assert base == 10
        assert mult == 1.5
        assert final == 15

    def test_close_match_half_time(self):
        """3 years off + 15s = 5 * 1.25 = 6.25 → 6 pts (rounded down)."""
        final, base, mult = calculate_round_score(1988, 1985, 15.0, 30.0)
        assert base == 5
        assert abs(mult - 1.25) < 0.001
        assert final == 6  # int(5 * 1.25) = 6

    def test_near_match_at_deadline(self):
        """5 years off + deadline = 1 * 1.0 = 1 pt."""
        final, base, mult = calculate_round_score(1990, 1985, 30.0, 30.0)
        assert base == 1
        assert mult == 1.0
        assert final == 1

    def test_wrong_guess_no_bonus_applies(self):
        """>5 years off = 0 pts (no bonus on 0)."""
        final, base, mult = calculate_round_score(1970, 1985, 0.0, 30.0)
        assert base == 0
        assert mult == 1.5  # Multiplier still calculated
        assert final == 0  # 0 * 1.5 = 0

    def test_2_years_off_quick_submit(self):
        """2 years off + 5s = 5 * 1.417 = 7.08 → 7 pts."""
        final, base, mult = calculate_round_score(1987, 1985, 5.0, 30.0)
        assert base == 5
        expected_mult = 1.5 - (0.5 * (5.0 / 30.0))
        assert abs(mult - expected_mult) < 0.001
        assert final == int(5 * expected_mult)


# =============================================================================
# SPEED BONUS INTEGRATION TESTS (Story 5.1)
# =============================================================================


@pytest.mark.unit
class TestSpeedBonusIntegration:
    """Tests for speed bonus integration with GameState (Story 5.1)."""

    @pytest.mark.asyncio
    async def test_end_round_calculates_speed_multiplier(self):
        """end_round calculates speed multiplier based on submission timing."""
        from custom_components.beatify.game.state import GameState

        time_counter = [1000.0]

        def mock_time():
            return time_counter[0]

        state = GameState(time_fn=mock_time)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        # Simulate round start
        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("FastPlayer", mock_ws)
        # Submit at 1005.0 (5 seconds elapsed)
        state.players["FastPlayer"].submit_guess(year=1985, timestamp=1005.0)

        await state.end_round()

        player = state.players["FastPlayer"]
        # Speed multiplier = 1.5 - 0.5 * (5/30) = 1.5 - 0.083 = 1.417
        expected_mult = 1.5 - (0.5 * (5.0 / 30.0))
        assert abs(player.speed_multiplier - expected_mult) < 0.01
        assert player.base_score == 10  # Exact match
        assert player.round_score == int(10 * expected_mult)

    @pytest.mark.asyncio
    async def test_end_round_instant_submit_gets_max_bonus(self):
        """Player submitting instantly gets 1.5x multiplier."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("InstantPlayer", mock_ws)
        state.players["InstantPlayer"].submit_guess(year=1985, timestamp=1000.0)

        await state.end_round()

        player = state.players["InstantPlayer"]
        assert player.speed_multiplier == 1.5
        assert player.base_score == 10
        assert player.round_score == 15  # 10 * 1.5

    @pytest.mark.asyncio
    async def test_end_round_deadline_submit_gets_no_bonus(self):
        """Player submitting at deadline gets 1.0x multiplier."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1030.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("SlowPlayer", mock_ws)
        state.players["SlowPlayer"].submit_guess(year=1985, timestamp=1030.0)

        await state.end_round()

        player = state.players["SlowPlayer"]
        assert player.speed_multiplier == 1.0
        assert player.base_score == 10
        assert player.round_score == 10  # 10 * 1.0

    @pytest.mark.asyncio
    async def test_reveal_state_includes_speed_bonus_data(self):
        """Reveal state includes base_score and speed_multiplier."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].submit_guess(year=1988, timestamp=1010.0)

        await state.end_round()

        reveal_state = state.get_reveal_players_state()
        player_data = reveal_state[0]

        assert "base_score" in player_data
        assert "speed_multiplier" in player_data
        assert player_data["base_score"] == 5  # 3 years off
        # speed_multiplier rounded to 2 decimals in reveal state
        expected_mult = round(1.5 - (0.5 * (10.0 / 30.0)), 2)
        assert player_data["speed_multiplier"] == expected_mult

    @pytest.mark.asyncio
    async def test_non_submitter_gets_default_speed_values(self):
        """Non-submitters get base_score=0 and speed_multiplier=1.0."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("NoSubmit", mock_ws)
        # Don't submit

        await state.end_round()

        player = state.players["NoSubmit"]
        assert player.base_score == 0
        assert player.speed_multiplier == 1.0
        assert player.round_score == 0
        assert player.missed_round is True


# =============================================================================
# STREAK BONUS TESTS (Story 5.2)
# =============================================================================


@pytest.mark.unit
class TestStreakBonus:
    """Tests for streak milestone bonus calculation (Story 5.2)."""

    def test_streak_2_no_bonus(self):
        """Streak 2 → 0 bonus (not at milestone)."""
        assert calculate_streak_bonus(2) == 0

    def test_streak_3_gives_20_bonus(self):
        """Streak 3 → 20 bonus (first milestone)."""
        assert calculate_streak_bonus(3) == 20

    def test_streak_4_no_bonus(self):
        """Streak 4 → 0 bonus (only at exact milestones)."""
        assert calculate_streak_bonus(4) == 0

    def test_streak_5_gives_50_bonus(self):
        """Streak 5 → 50 bonus (second milestone)."""
        assert calculate_streak_bonus(5) == 50

    def test_streak_6_no_bonus(self):
        """Streak 6 → 0 bonus (between milestones)."""
        assert calculate_streak_bonus(6) == 0

    def test_streak_10_gives_100_bonus(self):
        """Streak 10 → 100 bonus (third milestone)."""
        assert calculate_streak_bonus(10) == 100

    def test_streak_11_no_bonus(self):
        """Streak 11 → 0 bonus (past all milestones)."""
        assert calculate_streak_bonus(11) == 0

    def test_streak_0_no_bonus(self):
        """Streak 0 → 0 bonus (no streak)."""
        assert calculate_streak_bonus(0) == 0

    def test_streak_1_no_bonus(self):
        """Streak 1 → 0 bonus (too early)."""
        assert calculate_streak_bonus(1) == 0


# =============================================================================
# STREAK INTEGRATION TESTS (Story 5.2)
# =============================================================================


@pytest.mark.unit
class TestStreakIntegration:
    """Tests for streak bonus integration with GameState (Story 5.2)."""

    @pytest.mark.asyncio
    async def test_end_round_awards_streak_bonus_at_milestone(self):
        """Player reaching streak 3 gets +20 bonus."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("StreakPlayer", mock_ws)
        # Set streak to 2 (about to reach 3)
        state.players["StreakPlayer"].streak = 2
        state.players["StreakPlayer"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        player = state.players["StreakPlayer"]
        assert player.streak == 3  # Incremented
        assert player.streak_bonus == 20  # Milestone bonus
        # Total should include streak bonus
        assert player.score == player.round_score + 20

    @pytest.mark.asyncio
    async def test_end_round_no_bonus_between_milestones(self):
        """Player at streak 4 (between milestones) gets no bonus."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].streak = 3  # Will become 4
        state.players["TestPlayer"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        player = state.players["TestPlayer"]
        assert player.streak == 4
        assert player.streak_bonus == 0  # No bonus at 4

    @pytest.mark.asyncio
    async def test_end_round_resets_streak_on_zero_points(self):
        """Player scoring 0 points has streak reset and no bonus."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].streak = 5
        # Guess way off → 0 points
        state.players["TestPlayer"].submit_guess(year=1900, timestamp=1015.0)

        await state.end_round()

        player = state.players["TestPlayer"]
        assert player.streak == 0  # Reset
        assert player.streak_bonus == 0

    @pytest.mark.asyncio
    async def test_end_round_missed_round_resets_streak(self):
        """Non-submitter has streak reset and no bonus."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("NoSubmit", mock_ws)
        state.players["NoSubmit"].streak = 4
        # Don't submit

        await state.end_round()

        player = state.players["NoSubmit"]
        assert player.streak == 0
        assert player.streak_bonus == 0
        assert player.missed_round is True

    @pytest.mark.asyncio
    async def test_reveal_state_includes_streak_bonus(self):
        """Reveal state includes streak_bonus field."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].streak = 2
        state.players["TestPlayer"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        reveal_state = state.get_reveal_players_state()
        player_data = reveal_state[0]

        assert "streak_bonus" in player_data
        assert player_data["streak_bonus"] == 20  # Reached streak 3

    @pytest.mark.asyncio
    async def test_streak_5_gives_50_bonus_integration(self):
        """Player reaching streak 5 gets +50 bonus."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("StreakPlayer", mock_ws)
        state.players["StreakPlayer"].streak = 4  # About to reach 5
        state.players["StreakPlayer"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        player = state.players["StreakPlayer"]
        assert player.streak == 5
        assert player.streak_bonus == 50


# =============================================================================
# BET MULTIPLIER TESTS (Story 5.3)
# =============================================================================


@pytest.mark.unit
class TestBetMultiplier:
    """Tests for bet multiplier calculation (Story 5.3)."""

    def test_no_bet_returns_original_score(self):
        """No bet → score unchanged, outcome None."""
        score, outcome = apply_bet_multiplier(10, False)
        assert score == 10
        assert outcome is None

    def test_bet_with_points_doubles_score(self):
        """Bet + scored → score doubled, outcome 'won'."""
        score, outcome = apply_bet_multiplier(10, True)
        assert score == 20
        assert outcome == "won"

    def test_bet_with_zero_returns_zero(self):
        """Bet + 0 points → 0, outcome 'lost'."""
        score, outcome = apply_bet_multiplier(0, True)
        assert score == 0
        assert outcome == "lost"

    def test_bet_with_one_point_doubles(self):
        """Bet + 1 point → 2 points, outcome 'won'."""
        score, outcome = apply_bet_multiplier(1, True)
        assert score == 2
        assert outcome == "won"

    def test_no_bet_with_zero_returns_zero(self):
        """No bet + 0 points → 0, outcome None."""
        score, outcome = apply_bet_multiplier(0, False)
        assert score == 0
        assert outcome is None


# =============================================================================
# BET INTEGRATION TESTS (Story 5.3)
# =============================================================================


@pytest.mark.unit
class TestBetIntegration:
    """Tests for bet integration with GameState (Story 5.3)."""

    @pytest.mark.asyncio
    async def test_bet_doubles_round_score(self):
        """Player with bet gets double round score."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("BetPlayer", mock_ws)
        state.players["BetPlayer"].bet = True  # Place bet
        state.players["BetPlayer"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        player = state.players["BetPlayer"]
        # Without bet: ~12 pts (10 base * 1.25 speed)
        # With bet: should be doubled (~24 pts)
        assert player.bet_outcome == "won"
        # Verify it's roughly double the expected speed score
        expected_speed_mult = 1.5 - (0.5 * (15.0 / 30.0))  # 1.25
        expected_speed_score = int(10 * expected_speed_mult)
        assert player.round_score == expected_speed_score * 2

    @pytest.mark.asyncio
    async def test_bet_lost_on_zero_points(self):
        """Player betting with 0 points has outcome 'lost'."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("BetLoser", mock_ws)
        state.players["BetLoser"].bet = True
        # Guess way off → 0 points
        state.players["BetLoser"].submit_guess(year=1900, timestamp=1015.0)

        await state.end_round()

        player = state.players["BetLoser"]
        assert player.round_score == 0
        assert player.bet_outcome == "lost"

    @pytest.mark.asyncio
    async def test_bet_does_not_double_streak_bonus(self):
        """Bet doubles round score but NOT streak bonus."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("BetStreak", mock_ws)
        state.players["BetStreak"].bet = True
        state.players["BetStreak"].streak = 2  # Will reach 3 → +20 bonus
        state.players["BetStreak"].submit_guess(year=1985, timestamp=1030.0)  # At deadline

        await state.end_round()

        player = state.players["BetStreak"]
        # At deadline: speed_mult = 1.0, base = 10, speed_score = 10
        # With bet: round_score = 20
        # Streak bonus = 20 (NOT doubled by bet)
        assert player.round_score == 20  # 10 * 2
        assert player.streak_bonus == 20  # Not affected by bet
        assert player.score == 40  # 20 + 20

    @pytest.mark.asyncio
    async def test_no_bet_outcome_when_not_betting(self):
        """Player not betting has bet_outcome = None."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("NoBetPlayer", mock_ws)
        state.players["NoBetPlayer"].bet = False  # No bet
        state.players["NoBetPlayer"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        player = state.players["NoBetPlayer"]
        assert player.bet_outcome is None

    @pytest.mark.asyncio
    async def test_reveal_includes_bet_data(self):
        """Reveal state includes bet and bet_outcome."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("BetPlayer", mock_ws)
        state.players["BetPlayer"].bet = True
        state.players["BetPlayer"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        reveal_state = state.get_reveal_players_state()
        player_data = reveal_state[0]

        assert "bet" in player_data
        assert "bet_outcome" in player_data
        assert player_data["bet"] is True
        assert player_data["bet_outcome"] == "won"


# =============================================================================
# NO-SUBMISSION PENALTY TESTS (Story 5.4)
# =============================================================================


@pytest.mark.unit
class TestNoSubmissionPenalty:
    """Tests for no-submission penalty (Story 5.4)."""

    @pytest.mark.asyncio
    async def test_missed_round_stores_previous_streak(self):
        """Non-submitter has previous_streak stored before reset."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("NoSubmit", mock_ws)
        state.players["NoSubmit"].streak = 5  # Had a 5-streak
        # Don't submit

        await state.end_round()

        player = state.players["NoSubmit"]
        assert player.previous_streak == 5  # Stored before reset
        assert player.streak == 0  # Reset
        assert player.missed_round is True

    @pytest.mark.asyncio
    async def test_zero_points_stores_previous_streak(self):
        """Submitter with 0 points has previous_streak stored."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("ZeroPoints", mock_ws)
        state.players["ZeroPoints"].streak = 4
        # Guess way off → 0 points
        state.players["ZeroPoints"].submit_guess(year=1900, timestamp=1015.0)

        await state.end_round()

        player = state.players["ZeroPoints"]
        assert player.previous_streak == 4  # Stored before reset
        assert player.streak == 0

    @pytest.mark.asyncio
    async def test_scored_points_clears_previous_streak(self):
        """Submitter with points has previous_streak = 0."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("Scorer", mock_ws)
        state.players["Scorer"].streak = 3
        state.players["Scorer"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        player = state.players["Scorer"]
        assert player.previous_streak == 0  # Not relevant for scorers
        assert player.streak == 4  # Incremented

    @pytest.mark.asyncio
    async def test_reveal_state_includes_previous_streak(self):
        """Reveal state includes previous_streak field."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("NoSubmit", mock_ws)
        state.players["NoSubmit"].streak = 7

        await state.end_round()

        reveal_state = state.get_reveal_players_state()
        player_data = reveal_state[0]

        assert "previous_streak" in player_data
        assert player_data["previous_streak"] == 7

    @pytest.mark.asyncio
    async def test_missed_round_with_bet_forfeits_bet(self):
        """Non-submitter with bet gets bet_outcome = None (forfeited)."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("BetNoSubmit", mock_ws)
        state.players["BetNoSubmit"].bet = True  # Had bet active
        state.players["BetNoSubmit"].streak = 3

        await state.end_round()

        player = state.players["BetNoSubmit"]
        assert player.round_score == 0
        assert player.bet_outcome is None  # Bet forfeited (not lost)
        assert player.missed_round is True

    @pytest.mark.asyncio
    async def test_reset_round_clears_previous_streak(self):
        """reset_round() clears previous_streak for new round."""
        from custom_components.beatify.game.player import PlayerSession

        mock_ws = MagicMock()
        player = PlayerSession(name="Test", ws=mock_ws)
        player.previous_streak = 5
        player.streak = 0

        player.reset_round()

        assert player.previous_streak == 0


# =============================================================================
# LEADERBOARD TESTS (Story 5.5)
# =============================================================================


@pytest.mark.unit
class TestLeaderboard:
    """Tests for leaderboard functionality (Story 5.5)."""

    def test_leaderboard_sorted_by_score_descending(self):
        """Leaderboard is sorted by score descending."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("Low", mock_ws)
        state.add_player("High", mock_ws)
        state.add_player("Mid", mock_ws)

        state.players["Low"].score = 10
        state.players["High"].score = 100
        state.players["Mid"].score = 50

        leaderboard = state.get_leaderboard()

        assert leaderboard[0]["name"] == "High"
        assert leaderboard[1]["name"] == "Mid"
        assert leaderboard[2]["name"] == "Low"

    def test_leaderboard_ties_get_same_rank(self):
        """Players with same score get same rank."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("Alice", mock_ws)
        state.add_player("Bob", mock_ws)
        state.add_player("Carol", mock_ws)

        state.players["Alice"].score = 100
        state.players["Bob"].score = 80
        state.players["Carol"].score = 80  # Same as Bob

        leaderboard = state.get_leaderboard()

        assert leaderboard[0]["rank"] == 1
        assert leaderboard[1]["rank"] == 2
        assert leaderboard[2]["rank"] == 2  # Same rank as Bob

    def test_leaderboard_ties_skip_ranks(self):
        """After ties, next rank skips (1, 2, 2, 4 not 1, 2, 2, 3)."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("A", mock_ws)
        state.add_player("B", mock_ws)
        state.add_player("C", mock_ws)
        state.add_player("D", mock_ws)

        state.players["A"].score = 100
        state.players["B"].score = 80
        state.players["C"].score = 80  # Tie with B
        state.players["D"].score = 50

        leaderboard = state.get_leaderboard()

        ranks = [e["rank"] for e in leaderboard]
        assert ranks == [1, 2, 2, 4]  # Skips 3

    def test_leaderboard_includes_all_fields(self):
        """Leaderboard entries include all required fields."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.players["TestPlayer"].score = 50
        state.players["TestPlayer"].streak = 3

        leaderboard = state.get_leaderboard()
        entry = leaderboard[0]

        assert "rank" in entry
        assert "name" in entry
        assert "score" in entry
        assert "streak" in entry
        assert "is_admin" in entry
        assert "rank_change" in entry
        assert "connected" in entry

    def test_leaderboard_rank_change_calculated(self):
        """Rank change is calculated from previous_rank."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("Mover", mock_ws)
        state.players["Mover"].score = 100
        state.players["Mover"].previous_rank = 3  # Was rank 3

        leaderboard = state.get_leaderboard()
        entry = leaderboard[0]

        # Now rank 1, was rank 3 → moved up 2
        assert entry["rank_change"] == 2

    def test_leaderboard_no_previous_rank_zero_change(self):
        """No previous_rank means rank_change is 0."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("NewPlayer", mock_ws)
        state.players["NewPlayer"].score = 50
        # previous_rank is None (default)

        leaderboard = state.get_leaderboard()
        entry = leaderboard[0]

        assert entry["rank_change"] == 0

    @pytest.mark.asyncio
    async def test_end_round_stores_previous_ranks(self):
        """end_round stores previous ranks before scoring."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("Leader", mock_ws)
        state.add_player("Follower", mock_ws)

        state.players["Leader"].score = 100
        state.players["Follower"].score = 50

        await state.end_round()

        # Previous ranks should be stored
        assert state.players["Leader"].previous_rank == 1
        assert state.players["Follower"].previous_rank == 2

    def test_state_includes_leaderboard_in_playing(self):
        """get_state includes leaderboard during PLAYING phase."""
        from custom_components.beatify.game.state import GamePhase, GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.phase = GamePhase.PLAYING
        state.current_song = {"year": 1985}

        game_state = state.get_state()

        assert "leaderboard" in game_state
        assert len(game_state["leaderboard"]) == 1

    def test_state_includes_leaderboard_in_reveal(self):
        """get_state includes leaderboard during REVEAL phase."""
        from custom_components.beatify.game.state import GamePhase, GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.phase = GamePhase.REVEAL
        state.current_song = {"year": 1985}

        game_state = state.get_state()

        assert "leaderboard" in game_state


# =============================================================================
# FINAL LEADERBOARD TESTS (Story 5.6)
# =============================================================================


@pytest.mark.unit
class TestFinalLeaderboard:
    """Tests for final leaderboard functionality (Story 5.6)."""

    @pytest.mark.asyncio
    async def test_end_round_tracks_rounds_played(self):
        """rounds_played increments for submitters each round."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("Player1", mock_ws)
        state.players["Player1"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        assert state.players["Player1"].rounds_played == 1

    @pytest.mark.asyncio
    async def test_end_round_tracks_best_streak(self):
        """best_streak updates when streak exceeds it."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("Player1", mock_ws)
        state.players["Player1"].streak = 4
        state.players["Player1"].best_streak = 3
        state.players["Player1"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        # Streak went from 4 to 5, best_streak updated
        assert state.players["Player1"].streak == 5
        assert state.players["Player1"].best_streak == 5

    @pytest.mark.asyncio
    async def test_end_round_tracks_bets_won(self):
        """bets_won increments when bet wins."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("Player1", mock_ws)
        state.players["Player1"].bet = True
        state.players["Player1"].submit_guess(year=1985, timestamp=1015.0)

        await state.end_round()

        assert state.players["Player1"].bet_outcome == "won"
        assert state.players["Player1"].bets_won == 1

    @pytest.mark.asyncio
    async def test_missed_round_no_stats_update(self):
        """Non-submitter doesn't get stats updated."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        state.round_start_time = 1000.0
        state.round_duration = 30.0
        state.current_song = {"year": 1985, "uri": "spotify:track:1"}

        mock_ws = MagicMock()
        state.add_player("NoSubmit", mock_ws)
        # Don't submit

        await state.end_round()

        assert state.players["NoSubmit"].rounds_played == 0

    def test_final_leaderboard_includes_stats(self):
        """get_final_leaderboard includes all final stats."""
        from custom_components.beatify.game.state import GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("Player1", mock_ws)
        state.players["Player1"].score = 100
        state.players["Player1"].best_streak = 5
        state.players["Player1"].rounds_played = 10
        state.players["Player1"].bets_won = 3

        leaderboard = state.get_final_leaderboard()
        entry = leaderboard[0]

        assert "best_streak" in entry
        assert "rounds_played" in entry
        assert "bets_won" in entry
        assert entry["best_streak"] == 5
        assert entry["rounds_played"] == 10
        assert entry["bets_won"] == 3

    def test_state_includes_final_leaderboard_in_end(self):
        """get_state includes final leaderboard during END phase."""
        from custom_components.beatify.game.state import GamePhase, GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("TestPlayer", mock_ws)
        state.phase = GamePhase.END

        game_state = state.get_state()

        assert "leaderboard" in game_state
        assert "game_stats" in game_state
        assert "winner" in game_state

    def test_state_end_includes_game_stats(self):
        """END state includes game_stats with total_rounds and total_players."""
        from custom_components.beatify.game.state import GamePhase, GameState

        state = GameState(time_fn=lambda: 1000.0)
        songs = [{"year": 1985, "uri": "spotify:track:1", "fun_fact": "Fact 1"}]
        state.create_game(
            playlists=["playlist1.json"],
            songs=songs,
            media_player="media_player.test",
            base_url="http://test.local:8123",
        )

        mock_ws = MagicMock()
        state.add_player("Player1", mock_ws)
        state.add_player("Player2", mock_ws)
        state.round = 5
        state.phase = GamePhase.END

        game_state = state.get_state()

        assert game_state["game_stats"]["total_rounds"] == 5
        assert game_state["game_stats"]["total_players"] == 2

    def test_cumulative_stats_not_reset_in_reset_round(self):
        """Cumulative stats are NOT reset in reset_round()."""
        from custom_components.beatify.game.player import PlayerSession

        mock_ws = MagicMock()
        player = PlayerSession(name="Test", ws=mock_ws)
        player.best_streak = 5
        player.rounds_played = 10
        player.bets_won = 3

        player.reset_round()

        # These should NOT be reset
        assert player.best_streak == 5
        assert player.rounds_played == 10
        assert player.bets_won == 3
