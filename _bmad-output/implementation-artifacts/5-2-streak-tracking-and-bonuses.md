# Story 5.2: Streak Tracking & Bonuses

Status: review

## Story

As a **player**,
I want **to earn bonus points for consecutive scoring rounds**,
so that **consistent performance is rewarded**.

## Acceptance Criteria

1. **AC1:** Given player scores points in a round (>0), When round completes, Then player's streak counter increments (FR34)

2. **AC2:** Given player scores 0 points in a round, When round completes, Then player's streak counter resets to 0

3. **AC3:** Given player reaches streak milestone, When streak bonus is evaluated (FR35), Then bonus points are awarded:
   - 3 consecutive scoring rounds: +20 bonus
   - 5 consecutive scoring rounds: +50 bonus
   - 10 consecutive scoring rounds: +100 bonus

4. **AC4:** Given player earns a streak bonus, When reveal displays, Then streak bonus is shown separately (e.g., "3-streak bonus: +20!")

5. **AC5:** Given player maintains streak across rounds, When leaderboard displays, Then current streak is visible (e.g., "3" indicator with fire icon)

## Tasks / Subtasks

**DEPENDENCY:** Requires Story 5.1 completed (speed bonus foundation).

- [ ] **Task 1: Define streak milestone bonuses** (AC: #3)
  - [ ] 1.1 Add `STREAK_MILESTONES` constant to const.py: `{3: 20, 5: 50, 10: 100}`
  - [ ] 1.2 Document milestone bonus logic in scoring.py docstring

- [ ] **Task 2: Implement streak bonus calculation** (AC: #3, #4)
  - [ ] 2.1 Add `calculate_streak_bonus(streak: int) -> int` to scoring.py
  - [ ] 2.2 Check if streak matches any milestone (3, 5, 10)
  - [ ] 2.3 Return corresponding bonus (20, 50, 100) or 0
  - [ ] 2.4 Handle edge case: streak exactly at milestone vs past it

- [ ] **Task 3: Track streak bonus in PlayerSession** (AC: #4)
  - [ ] 3.1 Add `streak_bonus: int = 0` field to PlayerSession
  - [ ] 3.2 Reset streak_bonus at round start

- [ ] **Task 4: Integrate streak bonus in end_round()** (AC: #1, #2, #3)
  - [ ] 4.1 After calculating round_score, check for streak milestone
  - [ ] 4.2 Calculate streak_bonus using `calculate_streak_bonus(player.streak)`
  - [ ] 4.3 Add streak_bonus to player's total score (separate from round_score)
  - [ ] 4.4 Store streak_bonus on player session for reveal display

- [ ] **Task 5: Update scoring flow** (AC: #1, #2)
  - [ ] 5.1 Verify streak increments BEFORE checking milestone (so 3rd win triggers +20)
  - [ ] 5.2 Verify streak resets to 0 on missed round or 0 points
  - [ ] 5.3 Verify streak persists across rounds when scoring

- [ ] **Task 6: Update state broadcast for reveal** (AC: #4)
  - [ ] 6.1 Include `streak_bonus` in player data from `get_reveal_players_state()`
  - [ ] 6.2 Include `streak` count for display

- [ ] **Task 7: Update reveal UI for streak bonus** (AC: #4)
  - [ ] 7.1 Add streak bonus section to `renderPersonalResult()`
  - [ ] 7.2 Show streak milestone message when bonus earned
  - [ ] 7.3 Style streak bonus with fire icon and celebration

- [ ] **Task 8: Update leaderboard streak indicator** (AC: #5)
  - [ ] 8.1 Display streak count with fire icon next to player name
  - [ ] 8.2 Only show indicator when streak >= 2
  - [ ] 8.3 Style streak indicator prominently

- [ ] **Task 9: Unit tests for streak bonus** (AC: #3)
  - [ ] 9.1 Test: streak 2 → 0 bonus
  - [ ] 9.2 Test: streak 3 → 20 bonus
  - [ ] 9.3 Test: streak 4 → 0 bonus (only at milestone)
  - [ ] 9.4 Test: streak 5 → 50 bonus
  - [ ] 9.5 Test: streak 10 → 100 bonus
  - [ ] 9.6 Test: streak 11 → 0 bonus

- [ ] **Task 10: Integration tests** (AC: #1, #2)
  - [ ] 10.1 Test: consecutive scoring rounds increment streak
  - [ ] 10.2 Test: 0 points resets streak to 0
  - [ ] 10.3 Test: missed round resets streak to 0
  - [ ] 10.4 Test: total score includes streak bonus

- [ ] **Task 11: Verify no regressions**
  - [ ] 11.1 Run `pytest tests/unit/` - all tests pass
  - [ ] 11.2 Run `ruff check` - no new issues
  - [ ] 11.3 Test full game flow with streaks

## Dev Notes

### Existing Codebase Context

| File | Current State | Action |
|------|---------------|--------|
| `game/scoring.py` | Has `calculate_accuracy_score()`, `calculate_speed_multiplier()` from 5.1 | Add streak bonus function |
| `game/state.py` | Has `end_round()` with speed bonus from 5.1 | Add streak bonus integration |
| `game/player.py` | Has `streak` field from Epic 4, `base_score` from 5.1 | Add `streak_bonus` field |
| `const.py` | Has error codes, constants | Add `STREAK_MILESTONES` |

### Current Streak Implementation (Epic 4)

**IMPORTANT:** Streak logic already exists in `end_round()` (lines 546-549):
```python
# Update streak - any points continues streak
if player.round_score > 0:
    player.streak += 1
else:
    player.streak = 0
```

**Streak Definition:** Player earns ANY points (>0) = streak continues. This differs from project-context.md ("within 3 years") but is simpler and already implemented. **Keep this behavior.**

### Streak Milestone Logic

**IMPORTANT:** Bonuses are awarded ONLY at exact milestones, not cumulatively:

```python
# const.py
STREAK_MILESTONES = {3: 20, 5: 50, 10: 100}

# scoring.py
def calculate_streak_bonus(streak: int) -> int:
    """Calculate milestone bonus for streak.

    Bonuses awarded at exact milestones only:
    - 3 consecutive: +20 points
    - 5 consecutive: +50 points
    - 10 consecutive: +100 points

    Args:
        streak: Current streak count (after incrementing for this round)

    Returns:
        Bonus points (0 if not at milestone)
    """
    from .const import STREAK_MILESTONES
    return STREAK_MILESTONES.get(streak, 0)
```

### Streak Flow in end_round()

**CRITICAL SCORING ORDER:**
1. Base accuracy score (Epic 4)
2. Speed multiplier (Story 5.1)
3. Bet multiplier (Story 5.3 - applied to speed-adjusted score)
4. **Streak bonus (this story) - ADDED to total, NOT multiplied**

```python
# game/state.py - Updated end_round()
from .scoring import calculate_accuracy_score, calculate_speed_multiplier, calculate_streak_bonus

for player in self.players.values():
    if player.submitted and correct_year is not None:
        # 1. Calculate base + speed score (from Story 5.1)
        player.base_score = calculate_accuracy_score(player.current_guess, correct_year)
        elapsed = player.submission_time - self.round_start_time if player.submission_time else DEFAULT_ROUND_DURATION
        player.speed_multiplier = calculate_speed_multiplier(elapsed, round_duration)
        player.round_score = int(player.base_score * player.speed_multiplier)
        player.years_off = abs(player.current_guess - correct_year)
        player.missed_round = False

        # 2. Update streak FIRST (before checking milestone)
        if player.round_score > 0:
            player.streak += 1
            # 3. Check for milestone bonus (awarded ONLY at exact milestones)
            player.streak_bonus = calculate_streak_bonus(player.streak)
        else:
            player.streak = 0
            player.streak_bonus = 0

        # 4. Add round score + streak bonus to total
        # NOTE: round_score and streak_bonus are SEPARATE (streak not multiplied by bet)
        player.score += player.round_score + player.streak_bonus
    else:
        # Non-submitter: reset everything
        player.base_score = 0
        player.speed_multiplier = 1.0
        player.round_score = 0
        player.years_off = None
        player.missed_round = True
        player.streak = 0
        player.streak_bonus = 0
```

**IMPORTANT:** The current code (line 552) does `player.score += player.round_score`. This must be changed to `player.score += player.round_score + player.streak_bonus` to include streak bonuses.

### PlayerSession Addition

```python
# game/player.py - Add to PlayerSession dataclass
    streak_bonus: int = 0  # Milestone bonus earned this round
```

**UPDATE reset_round() to include streak_bonus:**
```python
def reset_round(self) -> None:
    # ... existing resets from 5.1 ...
    self.streak_bonus = 0  # Reset streak bonus for new round
```

### State Broadcast Update

```python
# get_reveal_players_state() - Add streak_bonus
player_data = {
    # ... existing fields ...
    "streak": player.streak,
    "streak_bonus": player.streak_bonus,
}
```

### JavaScript Update

```javascript
// player.js - renderPersonalResult()

// After score breakdown, add streak bonus if earned
if (player.streak_bonus > 0) {
    scoreBreakdown += `
        <div class="result-row streak-bonus-row">
            <span class="result-label">Streak bonus!</span>
            <span class="result-value is-streak">+${player.streak_bonus} pts</span>
        </div>
    `;
}

// Update total to include streak bonus
const totalScore = player.round_score + (player.streak_bonus || 0);
```

### CSS Addition

```css
/* Streak bonus styling */
.result-value.is-streak {
    color: #ef4444;
    font-weight: 700;
}

.streak-bonus-row {
    background: linear-gradient(90deg, #fef3c7, #fde68a);
    padding: 8px 12px;
    border-radius: 8px;
    margin: 8px 0;
}

/* Leaderboard streak indicator */
.streak-indicator {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    font-size: 12px;
    color: #f59e0b;
    font-weight: 600;
}

.streak-indicator::before {
    content: "🔥";
}
```

### Architecture Compliance

- **Milestone Bonuses:** Exact values from epics.md (20/50/100)
- **Streak Logic:** Increment before milestone check
- **State Broadcast:** Include streak_bonus for reveal display
- **UI Pattern:** Consistent with reveal breakdown from 5.1

### Anti-Patterns to Avoid

- Do NOT award cumulative bonuses (only at exact milestones)
- Do NOT increment streak before calculating round_score
- Do NOT include streak_bonus in round_score (keep separate)
- Do NOT show streak indicator for streak < 2

### Previous Story Learnings (from 5.1)

- Scoring module extension pattern works well
- PlayerSession field additions straightforward
- Reveal UI breakdown established

### References

- [Source: epics.md#Story-5.2] - FR34, FR35 streak requirements
- [Source: project-context.md#Scoring-Algorithm] - Streak formula reference
- [Source: 5-1-speed-bonus-multiplier.md] - Speed bonus foundation

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
