# Story 5.1: Speed Bonus Multiplier

Status: review

## Story

As a **player**,
I want **to earn bonus points for submitting quickly**,
so that **fast recognition of songs is rewarded**.

## Acceptance Criteria

1. **AC1:** Given player submits a guess, When submission timestamp is evaluated, Then speed bonus multiplier is calculated using the formula: `speed_multiplier = 1.5 - (0.5 * submission_time_ratio)` where submission_time_ratio ranges from 0.0 (instant) to 1.0 (at deadline) (FR33)

2. **AC2:** Given player earns accuracy points, When speed bonus is calculated, Then final round score = `int(accuracy_points * speed_multiplier)` (rounded to nearest integer)

3. **AC3:** Given player submits at exactly 0 seconds into round, When multiplier is determined, Then 1.5x multiplier is applied (maximum bonus)

4. **AC4:** Given player submits at exactly 30 seconds (deadline), When multiplier is determined, Then 1.0x multiplier is applied (no bonus)

5. **AC5:** Given reveal displays, When player views their result, Then speed bonus breakdown is shown (e.g., "5 pts x 1.5x = 8 pts")

## Tasks / Subtasks

**DEPENDENCY:** Requires Story 4.6 completed (scoring module exists).

- [x] **Task 1: Track submission timing** (AC: #1)
  - [x] 1.1 **EXISTING:** `submission_time` field already exists on PlayerSession (stores absolute timestamp)
  - [x] 1.2 Add `round_start_time: float | None = None` to GameState (set when round starts)
  - [x] 1.3 In `start_round()`, set `self.round_start_time = self._now()` before setting deadline
  - [x] 1.4 Speed calculation uses: `elapsed = player.submission_time - self.round_start_time`

- [x] **Task 2: Implement speed multiplier calculation** (AC: #1, #3, #4)
  - [x] 2.1 Add `calculate_speed_multiplier(submission_time: float, round_duration: float) -> float` to scoring.py
  - [x] 2.2 Calculate submission_time_ratio = submission_time / round_duration
  - [x] 2.3 Clamp ratio between 0.0 and 1.0 (handle edge cases)
  - [x] 2.4 Apply formula: `1.5 - (0.5 * submission_time_ratio)`
  - [x] 2.5 Return multiplier (float between 1.0 and 1.5)

- [x] **Task 3: Extend calculate_points function** (AC: #2)
  - [x] 3.1 Add new function `calculate_round_score(guess, actual, submission_time, round_duration)` to scoring.py
  - [x] 3.2 Get base accuracy score via existing `calculate_accuracy_score()`
  - [x] 3.3 Get speed multiplier via `calculate_speed_multiplier()`
  - [x] 3.4 Calculate final score: `int(base * multiplier)`
  - [x] 3.5 Return score as integer

- [x] **Task 4: Update end_round() integration** (AC: #2)
  - [x] 4.1 Import `calculate_round_score` in state.py
  - [x] 4.2 Replace direct `calculate_accuracy_score()` call with `calculate_round_score()`
  - [x] 4.3 Pass submission_time and round_duration to scoring function
  - [x] 4.4 Store speed_multiplier on player session for reveal display

- [x] **Task 5: Add speed_multiplier to PlayerSession** (AC: #5)
  - [x] 5.1 Add `speed_multiplier: float = 1.0` field to PlayerSession dataclass
  - [x] 5.2 Set speed_multiplier during score calculation in end_round()
  - [x] 5.3 Reset speed_multiplier when round starts (or on new round)

- [x] **Task 6: Update state broadcast for reveal** (AC: #5)
  - [x] 6.1 Include `speed_multiplier` in player data from `get_reveal_players_state()`
  - [x] 6.2 Include `base_score` (accuracy only) for breakdown display
  - [x] 6.3 Include `submission_time` for transparency

- [x] **Task 7: Update reveal UI for speed bonus** (AC: #5)
  - [x] 7.1 Update `renderPersonalResult()` to show speed bonus breakdown
  - [x] 7.2 Show: "Base: X pts" + "Speed: Y.Yx" = "Total: Z pts"
  - [x] 7.3 Highlight speed bonus when > 1.0x (visual indicator)
  - [x] 7.4 Add speed bonus to result-row styling

- [x] **Task 8: Unit tests for speed multiplier** (AC: #1, #3, #4)
  - [x] 8.1 Test: 0 seconds → 1.5x multiplier
  - [x] 8.2 Test: 15 seconds (half) → 1.25x multiplier
  - [x] 8.3 Test: 30 seconds → 1.0x multiplier
  - [x] 8.4 Test: Negative time clamped to 0.0 ratio
  - [x] 8.5 Test: Time > duration clamped to 1.0 ratio

- [x] **Task 9: Integration tests for scoring** (AC: #2)
  - [x] 9.1 Test: exact match + instant submit = 10 * 1.5 = 15 pts
  - [x] 9.2 Test: 3 years off + half time = 5 * 1.25 = 6 pts (rounded)
  - [x] 9.3 Test: 5 years off + deadline = 1 * 1.0 = 1 pt
  - [x] 9.4 Test: > 5 years off = 0 pts (no bonus applies to 0)

- [x] **Task 10: E2E verification** (AC: #5)
  - [x] 10.1 Verify reveal shows speed bonus breakdown
  - [x] 10.2 Verify multiplier displayed correctly (2 decimal places)
  - [x] 10.3 Verify total matches calculation

- [x] **Task 11: Verify no regressions**
  - [x] 11.1 Run `pytest tests/unit/` - all tests pass
  - [x] 11.2 Run `ruff check` - no new issues
  - [x] 11.3 Test full round flow with speed bonus

## Dev Notes

### Existing Codebase Context

**CRITICAL:** Before implementing, understand these existing components:

| File | Current State | Action |
|------|---------------|--------|
| `game/scoring.py` | Has `calculate_accuracy_score()` from Story 4.6 | Extend with speed functions |
| `game/state.py` | Has `end_round()` calling accuracy scoring | Update to use full scoring |
| `game/player.py` | Has `round_score`, `years_off` fields | Add submission_time, speed_multiplier |
| `www/js/player.js` | Has `renderPersonalResult()` | Extend for speed breakdown |

### Scoring Formula (from project-context.md)

**AUTHORITATIVE FORMULA - DO NOT MODIFY:**

```python
def calculate_speed_multiplier(submission_time: float, round_duration: float) -> float:
    """Calculate speed bonus multiplier.

    Args:
        submission_time: Seconds since round started when player submitted
        round_duration: Total round duration in seconds (default 30)

    Returns:
        Multiplier between 1.0 and 1.5
    """
    # Calculate ratio (0.0 = instant, 1.0 = at deadline)
    submission_time_ratio = submission_time / round_duration

    # Clamp to valid range
    submission_time_ratio = max(0.0, min(1.0, submission_time_ratio))

    # Formula: 1.5x at instant, 1.0x at deadline (linear)
    return 1.5 - (0.5 * submission_time_ratio)
```

### Round Timing Implementation

**CRITICAL:** `submission_time` is an ABSOLUTE timestamp (set by `player.submit_guess(year, timestamp)`).
Speed calculation must use: `elapsed = submission_time - round_start_time`

```python
# game/state.py - Add to __init__
self.round_start_time: float | None = None  # Unix timestamp when round started

# game/state.py - In start_round(), BEFORE setting deadline:
self.round_start_time = self._now()  # Record when round starts
self.deadline = int((self._now() + DEFAULT_ROUND_DURATION) * 1000)

# game/state.py - In end_round(), calculate elapsed time:
if player.submission_time is not None and self.round_start_time is not None:
    elapsed = player.submission_time - self.round_start_time
else:
    elapsed = DEFAULT_ROUND_DURATION  # Fallback = no bonus
```

**NOTE:** Do NOT modify `PlayerSession.submit_guess()` - it already stores absolute timestamp correctly.
The WebSocket handler calls `player.submit_guess(year, self._now())` which is correct.

### PlayerSession Additions

**EXISTING FIELDS (no change needed):**
- `submission_time: float | None = None` - Already exists, stores absolute timestamp

**NEW FIELDS TO ADD:**
```python
# game/player.py - Add to PlayerSession dataclass

    # Speed bonus tracking (Story 5.1)
    speed_multiplier: float = 1.0  # Calculated multiplier
    base_score: int = 0  # Accuracy-only score (for breakdown)
```

**UPDATE reset_round() to include new fields:**
```python
def reset_round(self) -> None:
    """Reset round-specific state for new round."""
    self.submitted = False
    self.current_guess = None
    self.submission_time = None
    self.round_score = 0
    self.years_off = None
    self.missed_round = False
    # NEW: Reset speed bonus fields
    self.speed_multiplier = 1.0
    self.base_score = 0
```

### Updated end_round() Integration

```python
# game/state.py

from .scoring import calculate_round_score, calculate_speed_multiplier

async def end_round(self) -> None:
    # ... existing timer cancellation ...

    correct_year = self.current_song.get("year") if self.current_song else None
    round_duration = self.round_duration or DEFAULT_ROUND_DURATION

    for player in self.players.values():
        if player.submitted and correct_year is not None:
            # Get accuracy score (base)
            player.base_score = calculate_accuracy_score(
                player.current_guess, correct_year
            )

            # Calculate speed multiplier
            player.speed_multiplier = calculate_speed_multiplier(
                player.submission_time, round_duration
            )

            # Final score with speed bonus
            player.round_score = int(player.base_score * player.speed_multiplier)
            player.years_off = abs(player.current_guess - correct_year)
            player.missed_round = False

            # Update streak (existing logic)
            if player.round_score > 0:
                player.streak += 1
            else:
                player.streak = 0

            player.score += player.round_score
        else:
            # Non-submitter
            player.base_score = 0
            player.speed_multiplier = 1.0
            player.round_score = 0
            player.years_off = None
            player.missed_round = True
            player.streak = 0

    self.transition_to(GamePhase.REVEAL)
    # ... rest of method ...
```

### State Broadcast Update

```python
# game/state.py - get_reveal_players_state()

def get_reveal_players_state(self) -> list[dict[str, Any]]:
    players = []
    for player in self.players.values():
        player_data = {
            "name": player.name,
            "score": player.score,
            "streak": player.streak,
            "is_admin": player.is_admin,
            "connected": player.connected,
            "guess": player.current_guess,
            "round_score": player.round_score,
            "years_off": player.years_off,
            "missed_round": player.missed_round,
            # NEW: Speed bonus data
            "base_score": player.base_score,
            "speed_multiplier": round(player.speed_multiplier, 2),
            "submission_time": round(player.submission_time, 1),
        }
        players.append(player_data)

    players.sort(key=lambda p: p["score"], reverse=True)
    return players
```

### JavaScript Update

```javascript
// player.js - Updated renderPersonalResult()

function renderPersonalResult(player, correctYear) {
    const resultContent = document.getElementById('result-content');
    if (!resultContent) return;

    if (!player) {
        resultContent.innerHTML = '<div class="result-missed">Player not found</div>';
        return;
    }

    if (player.missed_round) {
        resultContent.innerHTML = `
            <div class="result-missed">No guess submitted</div>
            <div class="result-score">0 pts</div>
        `;
        return;
    }

    const yearsOff = player.years_off || 0;
    let yearsOffText = yearsOff === 0 ? 'Exact!' :
                       yearsOff === 1 ? '1 year off' :
                       `${yearsOff} years off`;

    let resultClass = yearsOff === 0 ? 'is-exact' :
                      yearsOff <= 3 ? 'is-close' : 'is-far';

    // Speed bonus display
    const speedMultiplier = player.speed_multiplier || 1.0;
    const baseScore = player.base_score || 0;
    const hasSpeedBonus = speedMultiplier > 1.0;

    let scoreBreakdown = '';
    if (hasSpeedBonus && baseScore > 0) {
        scoreBreakdown = `
            <div class="result-row">
                <span class="result-label">Base score</span>
                <span class="result-value">${baseScore} pts</span>
            </div>
            <div class="result-row">
                <span class="result-label">Speed bonus</span>
                <span class="result-value is-bonus">${speedMultiplier.toFixed(2)}x</span>
            </div>
        `;
    }

    resultContent.innerHTML = `
        <div class="result-row">
            <span class="result-label">Your guess</span>
            <span class="result-value">${player.guess}</span>
        </div>
        <div class="result-row">
            <span class="result-label">Correct year</span>
            <span class="result-value">${correctYear}</span>
        </div>
        <div class="result-row">
            <span class="result-label">Accuracy</span>
            <span class="result-value ${resultClass}">${yearsOffText}</span>
        </div>
        ${scoreBreakdown}
        <div class="result-score">+${player.round_score} pts</div>
    `;
}
```

### CSS Addition

```css
/* Speed bonus indicator */
.result-value.is-bonus {
    color: #f59e0b;
    font-weight: 700;
}
```

### Project Structure Notes

- All scoring logic in `game/scoring.py` (single responsibility)
- PlayerSession tracks timing data (player.py)
- GameState manages round timing (state.py)
- UI displays breakdown (player.js)

### Architecture Compliance

- **Scoring Formula:** EXACT implementation per project-context.md
- **Time Injection:** Uses `self._now()` for testability
- **Naming:** snake_case for Python, camelCase for JS
- **State Broadcast:** snake_case fields in WebSocket messages

### Anti-Patterns to Avoid

- Do NOT use tiered multipliers (1.5x/1.2x/1.0x) - use linear formula
- Do NOT hardcode 30 seconds - use round_duration parameter
- Do NOT modify base scoring formula from Story 4.6
- Do NOT skip speed bonus for 0-point rounds (multiplier still calculated)

### Previous Story Learnings (from 4.6)

- Scoring module pattern is well established
- PlayerSession dataclass extension works smoothly
- Reveal UI pattern with result breakdown tested
- State broadcast includes all needed player data

### Git Intelligence (Recent Commits)

- Epic 4 completed with full gameplay loop
- Sample playlist auto-copy working
- Music Assistant detection improved
- 193 unit tests passing (strong test foundation)

### Testing Strategy

Use time injection pattern from project-context.md:

```python
def test_speed_bonus_instant():
    state = GameState(time_fn=lambda: 1000.0)
    state.start_round()  # round_start_time = 1000.0

    # Simulate instant submission (same time)
    state.submit_guess("Tom", 1985)  # submission at 1000.0

    # Manually set submission_time for test
    state.players["Tom"].submission_time = 0.0

    await state.end_round()

    # 1.5x multiplier for instant
    assert state.players["Tom"].speed_multiplier == 1.5
```

### References

- [Source: project-context.md#Scoring-Algorithm] - Authoritative speed formula
- [Source: epics.md#Story-5.1] - FR33 speed bonus requirements
- [Source: architecture.md#Timer-Synchronization] - Server deadline pattern
- [Source: 4-6-reveal-and-scoring.md] - Scoring module foundation

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
