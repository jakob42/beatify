# Story 5.4: No Submission Penalty

Status: ready-for-dev

## Story

As a **game system**,
I want **to award 0 points when players don't submit**,
so that **there's incentive to participate in every round**.

## Acceptance Criteria

1. **AC1:** Given timer expires, When player has not submitted a guess, Then player receives 0 points for the round (FR38) And streak is broken (reset to 0)

2. **AC2:** Given player did not submit, When reveal displays, Then player sees "No guess submitted - 0 points" And streak indicator shows broken streak if applicable

3. **AC3:** Given player had an active bet but didn't submit, When round completes, Then bet is forfeited (no effect, just 0 points)

## Tasks / Subtasks

**DEPENDENCY:** Requires Story 5.3 completed (betting mechanic).

- [ ] **Task 1: Verify missed round handling in end_round()** (AC: #1)
  - [ ] 1.1 Confirm non-submitters get `round_score = 0`
  - [ ] 1.2 Confirm non-submitters get `streak = 0` (reset)
  - [ ] 1.3 Confirm `missed_round = True` is set
  - [ ] 1.4 Confirm `bet` is ignored for non-submitters

- [ ] **Task 2: Track previous streak for display** (AC: #2)
  - [ ] 2.1 Add `previous_streak: int = 0` field to PlayerSession
  - [ ] 2.2 Store streak value before resetting on missed round
  - [ ] 2.3 Use for "lost X streak" display

- [ ] **Task 3: Update state broadcast** (AC: #2)
  - [ ] 3.1 Include `previous_streak` in reveal player data (when missed)
  - [ ] 3.2 Include `missed_round` flag

- [ ] **Task 4: Update reveal UI for missed rounds** (AC: #2)
  - [ ] 4.1 Show "No guess submitted" message prominently
  - [ ] 4.2 Show "Lost X-streak!" if previous_streak >= 2
  - [ ] 4.3 Style missed round distinctively (red/gray theme)

- [ ] **Task 5: Handle bet forfeiture** (AC: #3)
  - [ ] 5.1 Verify bet is ignored when missed_round = True
  - [ ] 5.2 Clear bet_outcome to None for missed rounds
  - [ ] 5.3 No special messaging needed (just 0 points)

- [ ] **Task 6: Unit tests for no submission** (AC: #1)
  - [ ] 6.1 Test: non-submitter gets 0 points
  - [ ] 6.2 Test: non-submitter streak resets to 0
  - [ ] 6.3 Test: non-submitter with bet gets 0 points

- [ ] **Task 7: Integration tests** (AC: #1, #2)
  - [ ] 7.1 Test: missed round shows correct reveal message
  - [ ] 7.2 Test: streak broken message when previous streak > 0
  - [ ] 7.3 Test: score doesn't change for non-submitter

- [ ] **Task 8: Verify no regressions**
  - [ ] 8.1 Run `pytest tests/unit/` - all tests pass
  - [ ] 8.2 Run `ruff check` - no new issues
  - [ ] 8.3 Test round with mix of submitters and non-submitters

## Dev Notes

### This Story is Mostly Implemented

**IMPORTANT:** Most of Story 5.4 is already implemented in Epic 4. This story is primarily:
1. **Verification** that existing logic works correctly
2. **Enhancement** to add `previous_streak` tracking for better UX

### Existing Codebase Context

| File | Current State | Action |
|------|---------------|--------|
| `game/state.py` | **ALREADY HAS** missed_round handling (lines 553-558) | Add previous_streak tracking |
| `game/player.py` | **ALREADY HAS** `missed_round: bool = False` field | Add `previous_streak: int = 0` field |
| `www/js/player.js` | Has renderPersonalResult() with missed handling | Enhance with "lost X-streak" display |

### Existing Implementation (lines 553-558 in state.py)

```python
else:
    # Non-submitter
    player.round_score = 0
    player.years_off = None
    player.missed_round = True
    player.streak = 0  # Break streak
```

**This already does:**
- Sets round_score to 0
- Sets missed_round to True
- Resets streak to 0

**What's NEW in this story:**
- Track `previous_streak` before resetting (for "lost 5-streak!" display)
- Enhanced UI messaging

### Existing Implementation Check

Most of this story is already implemented from Epic 4. Key verification points:

```python
# game/state.py - end_round() already handles this:

for player in self.players.values():
    if player.submitted and correct_year is not None:
        # ... scoring logic ...
    else:
        # Non-submitter - THIS IS THE KEY SECTION
        player.base_score = 0
        player.speed_multiplier = 1.0
        player.round_score = 0
        player.years_off = None
        player.missed_round = True
        player.streak = 0  # Streak broken
        player.streak_bonus = 0
        player.bet_outcome = None  # Bet forfeited
```

### New: Track Previous Streak

```python
# game/player.py
@dataclass
class PlayerSession:
    # ... existing fields ...
    previous_streak: int = 0  # Streak before reset (for "lost X-streak" display)
```

### Updated end_round() Logic

```python
# game/state.py - end_round()

for player in self.players.values():
    if player.submitted and correct_year is not None:
        # ... existing scoring logic ...
        player.previous_streak = 0  # Not relevant for submitters
    else:
        # Non-submitter
        player.previous_streak = player.streak  # Store before reset
        player.base_score = 0
        player.speed_multiplier = 1.0
        player.round_score = 0
        player.years_off = None
        player.missed_round = True
        player.streak = 0  # Break streak
        player.streak_bonus = 0
        player.bet_outcome = None  # Bet forfeited silently
```

### State Broadcast Update

```python
# get_reveal_players_state()
player_data = {
    # ... existing fields ...
    "missed_round": player.missed_round,
    "previous_streak": player.previous_streak,  # For "lost X-streak" display
}
```

### JavaScript Reveal Update

```javascript
// player.js - renderPersonalResult()

if (player.missed_round) {
    let missedMessage = `
        <div class="result-missed-container">
            <div class="result-missed-icon">⏰</div>
            <div class="result-missed-text">No guess submitted</div>
        </div>
    `;

    // Show broken streak if they had one
    if (player.previous_streak >= 2) {
        missedMessage += `
            <div class="streak-broken">
                <span class="streak-broken-icon">💔</span>
                <span class="streak-broken-text">Lost ${player.previous_streak}-streak!</span>
            </div>
        `;
    }

    resultContent.innerHTML = `
        ${missedMessage}
        <div class="result-score is-zero">0 pts</div>
    `;
    return;
}
```

### CSS Styles

```css
/* Missed round styling */
.result-missed-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 16px;
}

.result-missed-icon {
    font-size: 48px;
}

.result-missed-text {
    font-size: 18px;
    font-weight: 600;
    color: #6b7280;
}

.streak-broken {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    padding: 8px 16px;
    background: #fee2e2;
    border-radius: 8px;
}

.streak-broken-icon {
    font-size: 20px;
}

.streak-broken-text {
    font-size: 14px;
    font-weight: 600;
    color: #dc2626;
}

.result-score.is-zero {
    color: #9ca3af;
    font-size: 24px;
}
```

### Architecture Compliance

- **0 Points:** Already implemented in Epic 4
- **Streak Reset:** Already implemented in Epic 4
- **Bet Forfeiture:** Silent (no special message)
- **Display:** Enhanced with previous streak info

### What's Actually New in This Story

This story is largely a verification + enhancement story:

1. **Verify** existing missed round logic works correctly
2. **Add** previous_streak tracking for better UX
3. **Enhance** reveal display with streak-broken message
4. **Add** tests to ensure behavior is correct

### Anti-Patterns to Avoid

- Do NOT add penalty beyond 0 points (that's the only penalty)
- Do NOT show bet outcome for missed rounds
- Do NOT keep streak on missed round

### References

- [Source: epics.md#Story-5.4] - FR38 no submission penalty
- [Source: 4-6-reveal-and-scoring.md] - Original missed round handling
- [Source: 5-2-streak-tracking-and-bonuses.md] - Streak reset logic

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
