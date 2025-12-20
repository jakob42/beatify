# Story 5.3: Betting Mechanic

Status: ready-for-dev

## Story

As a **player**,
I want **to bet double-or-nothing on my guess**,
so that **I can take risks for bigger rewards**.

## Acceptance Criteria

1. **AC1:** Given round is in progress (PLAYING phase), When player views the game screen, Then a "Bet" toggle or button is visible (FR36) And betting can be activated before submitting

2. **AC2:** Given player activates bet, When they submit their guess, Then bet flag is sent with submission

3. **AC3:** Given player bet and scored points (>0), When score is calculated (FR37), Then points are doubled (after speed bonus, before streak bonus) And reveal shows "Bet paid off! Double points!"

4. **AC4:** Given player bet but scored 0 points, When score is calculated, Then no additional penalty (0 × 2 = 0) And reveal shows "Bet lost - no points"

5. **AC5:** Given player activates bet, When bet is confirmed, Then visual indicator shows bet is active And player can deactivate before submitting

## Tasks / Subtasks

**DEPENDENCY:** Requires Story 5.2 completed (streak bonus integration).

- [ ] **Task 1: Add bet field to PlayerSession** (AC: #2)
  - [ ] 1.1 Add `bet: bool = False` field to PlayerSession dataclass
  - [ ] 1.2 Add `bet_outcome: str | None = None` field ("won", "lost", or None)
  - [ ] 1.3 Reset both to defaults in `reset_round()`: `self.bet = False; self.bet_outcome = None`

- [ ] **Task 2: Update WebSocket handler for bet** (AC: #2)
  - [ ] 2.1 Parse `bet` from submit message: `bet = data.get("bet", False)`
  - [ ] 2.2 Store bet on player before submit: `player.bet = bet`
  - [ ] 2.3 **Do NOT modify** PlayerSession.submit_guess() signature

- [ ] **Task 3: Update WebSocket message handling** (AC: #2)
  - [ ] 3.1 Parse `bet` field from submit message
  - [ ] 3.2 Pass bet to `submit_guess()` call

- [ ] **Task 4: Implement bet multiplier in scoring** (AC: #3, #4)
  - [ ] 4.1 Add `calculate_bet_multiplier(bet: bool, scored_points: bool) -> int` to scoring.py
  - [ ] 4.2 Return 2 if bet and scored_points > 0
  - [ ] 4.3 Return 0 if bet and scored_points == 0 (effectively 0 × anything = 0)
  - [ ] 4.4 Return 1 if no bet (no change)

- [ ] **Task 5: Integrate bet in end_round()** (AC: #3, #4)
  - [ ] 5.1 Calculate round_score with speed bonus first
  - [ ] 5.2 Apply bet multiplier: `round_score *= bet_multiplier`
  - [ ] 5.3 Then add streak bonus (streak bonus NOT doubled by bet)
  - [ ] 5.4 Store bet outcome for reveal display

- [ ] **Task 6: Track bet outcome in PlayerSession** (AC: #3, #4)
  - [ ] 6.1 Add `bet_outcome: str | None = None` field ("won", "lost", None)
  - [ ] 6.2 Set outcome based on bet result in end_round()

- [ ] **Task 7: Update state broadcast** (AC: #3, #4)
  - [ ] 7.1 Include `bet` and `bet_outcome` in reveal player data

- [ ] **Task 8: Add bet toggle to game UI** (AC: #1, #5)
  - [ ] 8.1 Add bet toggle button in game-view HTML
  - [ ] 8.2 Position near submit button but distinct
  - [ ] 8.3 Style as toggle (on/off state)

- [ ] **Task 9: Implement bet toggle JavaScript** (AC: #1, #5)
  - [ ] 9.1 Track `betActive` state variable
  - [ ] 9.2 Toggle bet state on click
  - [ ] 9.3 Update visual indicator
  - [ ] 9.4 Include bet in submit message

- [ ] **Task 10: Update reveal UI for bet outcome** (AC: #3, #4)
  - [ ] 10.1 Show bet outcome message in renderPersonalResult()
  - [ ] 10.2 "Bet paid off! Double points!" for won
  - [ ] 10.3 "Bet lost - no points" for lost
  - [ ] 10.4 Style bet outcomes distinctively

- [ ] **Task 11: Style bet UI components** (AC: #1, #5)
  - [ ] 11.1 Create `.bet-toggle` styles
  - [ ] 11.2 Create `.bet-toggle.is-active` styles
  - [ ] 11.3 Create `.bet-outcome` styles (won/lost variants)

- [ ] **Task 12: Unit tests for bet multiplier** (AC: #3, #4)
  - [ ] 12.1 Test: no bet → multiplier 1
  - [ ] 12.2 Test: bet + scored → multiplier 2
  - [ ] 12.3 Test: bet + 0 points → result 0

- [ ] **Task 13: Integration tests** (AC: #3, #4)
  - [ ] 13.1 Test: bet doubles round score
  - [ ] 13.2 Test: bet does NOT double streak bonus
  - [ ] 13.3 Test: bet with 0 points = 0 total
  - [ ] 13.4 Test: bet flag stored correctly

- [ ] **Task 14: Verify no regressions**
  - [ ] 14.1 Run `pytest tests/unit/` - all tests pass
  - [ ] 14.2 Run `ruff check` - no new issues
  - [ ] 14.3 Test full game with betting

## Dev Notes

### Existing Codebase Context

| File | Current State | Action |
|------|---------------|--------|
| `game/scoring.py` | Has accuracy, speed, streak functions | Add bet multiplier |
| `game/state.py` | Has end_round() with speed + streak | Add bet integration |
| `game/player.py` | Has streak_bonus from 5.2 | Add bet, bet_outcome fields |
| `server/websocket.py` | Handles submit message | Parse bet field |
| `www/js/player.js` | Has submit handling | Add bet toggle logic |

### Current Submission Flow (Epic 4)

**IMPORTANT:** Understand how submissions currently work:

1. WebSocket handler receives `{"type": "submit", "year": 1985}` message
2. Handler calls `player.submit_guess(year, self._now())` on PlayerSession
3. PlayerSession stores: `submitted=True`, `current_guess=year`, `submission_time=timestamp`

**For betting, add `bet` to the WebSocket message and player session:**

### Bet Multiplier Implementation

```python
# scoring.py

def apply_bet_multiplier(round_score: int, bet: bool) -> tuple[int, str | None]:
    """Apply bet multiplier to round score.

    Betting is double-or-nothing:
    - If bet and scored points (>0): double the score, outcome="won"
    - If bet and 0 points: score stays 0, outcome="lost"
    - If no bet: score unchanged, outcome=None

    Args:
        round_score: Points earned before bet (accuracy × speed)
        bet: Whether player placed a bet

    Returns:
        Tuple of (final_score, bet_outcome)
        bet_outcome is "won", "lost", or None
    """
    if not bet:
        return round_score, None

    if round_score > 0:
        return round_score * 2, "won"
    else:
        return 0, "lost"
```

**NOTE:** Function returns tuple with outcome for reveal display. Do NOT use separate multiplier function.

### Scoring Order (CRITICAL)

The order of score calculation matters:

```python
# end_round() scoring flow

# 1. Base accuracy score
base_score = calculate_accuracy_score(guess, actual)

# 2. Speed bonus multiplier
speed_multiplier = calculate_speed_multiplier(submission_time, duration)
speed_adjusted = int(base_score * speed_multiplier)

# 3. Bet multiplier (on speed-adjusted score)
bet_multiplier = calculate_bet_multiplier(player.bet, speed_adjusted)
round_score = speed_adjusted * bet_multiplier

# 4. Streak bonus (added AFTER bet, NOT multiplied)
streak_bonus = calculate_streak_bonus(player.streak)

# 5. Total for round
total_round = round_score + streak_bonus
player.score += total_round
```

### PlayerSession Additions

```python
# game/player.py
@dataclass
class PlayerSession:
    # ... existing fields ...
    bet: bool = False  # Whether player bet this round
    bet_outcome: str | None = None  # "won", "lost", or None
```

### WebSocket Submit Handler

**CURRENT FLOW:** The WebSocket handler calls `player.submit_guess(year, timestamp)` directly on PlayerSession.

**UPDATED FLOW:**
```python
# server/websocket.py - In submit message handler

async def handle_submit(self, ws, data: dict) -> None:
    guess = data.get("year")
    bet = data.get("bet", False)  # NEW: Parse bet flag

    if guess is None:
        await self.send_error(ws, "INVALID_SUBMISSION", "Year required")
        return

    player = self.get_player_for_ws(ws)
    if not player:
        return

    # Store bet flag on player BEFORE calling submit_guess
    player.bet = bet  # NEW

    # Existing call - no change needed
    player.submit_guess(guess, self._now())

    # ... rest of handler (broadcast, etc.)
```

**NOTE:** We store `bet` separately rather than modifying `submit_guess()` signature. This keeps changes minimal.

### HTML Bet Toggle

```html
<!-- In game-view, near submit button -->
<div class="bet-container">
    <button id="bet-toggle" class="bet-toggle" type="button">
        <span class="bet-icon">🎲</span>
        <span class="bet-label">Double or Nothing</span>
    </button>
</div>

<button id="submit-btn" class="submit-btn">Submit Guess</button>
```

### JavaScript Bet Logic

```javascript
// player.js

let betActive = false;

function setupBetToggle() {
    const betToggle = document.getElementById('bet-toggle');
    if (!betToggle) return;

    betToggle.addEventListener('click', () => {
        // Can't toggle after submitted
        if (hasSubmitted) return;

        betActive = !betActive;
        betToggle.classList.toggle('is-active', betActive);
    });
}

function handleSubmit() {
    if (hasSubmitted) return;

    const year = parseInt(document.getElementById('year-slider').value);

    ws.send(JSON.stringify({
        type: 'submit',
        year: year,
        bet: betActive  // Include bet flag
    }));

    hasSubmitted = true;
    // ... rest of submit handling
}

// Reset bet on new round
function resetForNewRound() {
    betActive = false;
    const betToggle = document.getElementById('bet-toggle');
    if (betToggle) betToggle.classList.remove('is-active');
    // ... other resets
}
```

### Reveal UI Update

```javascript
// renderPersonalResult() - Add bet outcome

if (player.bet_outcome === 'won') {
    scoreBreakdown += `
        <div class="result-row bet-won-row">
            <span class="result-label">🎲 Bet paid off!</span>
            <span class="result-value is-bet-won">2x</span>
        </div>
    `;
} else if (player.bet_outcome === 'lost') {
    scoreBreakdown += `
        <div class="result-row bet-lost-row">
            <span class="result-label">🎲 Bet lost</span>
            <span class="result-value is-bet-lost">No bonus</span>
        </div>
    `;
}
```

### CSS Styles

```css
/* Bet toggle */
.bet-container {
    margin-bottom: 16px;
}

.bet-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: #f3f4f6;
    border: 2px solid #d1d5db;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
    font-weight: 600;
    color: #6b7280;
}

.bet-toggle:hover {
    border-color: #9ca3af;
}

.bet-toggle.is-active {
    background: #fef3c7;
    border-color: #f59e0b;
    color: #92400e;
}

.bet-toggle.is-active .bet-icon {
    animation: dice-shake 0.5s ease;
}

@keyframes dice-shake {
    0%, 100% { transform: rotate(0deg); }
    25% { transform: rotate(-10deg); }
    75% { transform: rotate(10deg); }
}

/* Bet outcomes */
.bet-won-row {
    background: linear-gradient(90deg, #d1fae5, #a7f3d0);
    padding: 8px 12px;
    border-radius: 8px;
}

.result-value.is-bet-won {
    color: #059669;
    font-weight: 700;
}

.bet-lost-row {
    background: linear-gradient(90deg, #fee2e2, #fecaca);
    padding: 8px 12px;
    border-radius: 8px;
}

.result-value.is-bet-lost {
    color: #dc2626;
    font-weight: 700;
}
```

### Architecture Compliance

- **Bet Logic:** Double-or-nothing per epics.md
- **Scoring Order:** Speed → Bet → Streak (streak NOT doubled)
- **WebSocket:** Parse bet from submit message
- **UI Pattern:** Toggle before submit, outcome in reveal

### Anti-Patterns to Avoid

- Do NOT double streak bonus (only round_score)
- Do NOT allow bet change after submission
- Do NOT show bet toggle after player has submitted
- Do NOT apply bet to missed rounds

### References

- [Source: epics.md#Story-5.3] - FR36, FR37 betting requirements
- [Source: project-context.md#Scoring-Algorithm] - Bet multiplier formula
- [Source: 5-2-streak-tracking-and-bonuses.md] - Scoring integration pattern

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
