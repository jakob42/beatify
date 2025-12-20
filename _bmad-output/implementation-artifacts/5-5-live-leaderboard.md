# Story 5.5: Live Leaderboard

Status: ready-for-dev

## Story

As a **player**,
I want **to see a live leaderboard with everyone's scores**,
so that **I know my standing throughout the game**.

## Acceptance Criteria

1. **AC1:** Given game is in progress, When player views game screen, Then leaderboard is visible showing all players (FR39) And players are ranked by total score (highest first)

2. **AC2:** Given round completes (after reveal), When scores are calculated, Then leaderboard updates in real-time (FR40) And update occurs within 1 second (NFR5)

3. **AC3:** Given leaderboard displays, When player views rankings, Then each entry shows: rank position, player name, total score, current streak indicator (FR42)

4. **AC4:** Given player's rank changes, When leaderboard updates, Then movement is visually indicated (up/down arrow or animation)

5. **AC5:** Given many players in game (>10), When leaderboard displays, Then list is scrollable And current player's position is highlighted/visible

## Tasks / Subtasks

**DEPENDENCY:** Requires Story 5.4 completed (scoring complete).

- [ ] **Task 1: Design leaderboard data structure** (AC: #1, #3)
  - [ ] 1.1 Define leaderboard entry format in state broadcast
  - [ ] 1.2 Include: rank, name, score, streak, is_current_player
  - [ ] 1.3 Track previous rank for movement detection

- [ ] **Task 2: Implement get_leaderboard() in GameState** (AC: #1)
  - [ ] 2.1 Create `get_leaderboard() -> list[dict]` method
  - [ ] 2.2 Sort players by score descending
  - [ ] 2.3 Assign rank numbers (handle ties)
  - [ ] 2.4 Return formatted leaderboard data

- [ ] **Task 3: Track rank changes** (AC: #4)
  - [ ] 3.1 Add `previous_rank: int | None` to PlayerSession
  - [ ] 3.2 Store current rank before recalculating
  - [ ] 3.3 Calculate rank_change (positive = moved up)

- [ ] **Task 4: Update state broadcast** (AC: #1, #2)
  - [ ] 4.1 Include leaderboard in all state broadcasts
  - [ ] 4.2 Include rank_change for movement indicators
  - [ ] 4.3 Ensure real-time updates after scoring

- [ ] **Task 5: Create leaderboard HTML structure** (AC: #1, #3)
  - [ ] 5.1 Add leaderboard section to player.html
  - [ ] 5.2 Design compact layout for game view
  - [ ] 5.3 Design expanded layout for reveal view

- [ ] **Task 6: Implement updateLeaderboard() JavaScript** (AC: #1, #2, #3)
  - [ ] 6.1 Parse leaderboard data from state
  - [ ] 6.2 Render ranked player list
  - [ ] 6.3 Highlight current player
  - [ ] 6.4 Show streak indicators

- [ ] **Task 7: Implement rank change animations** (AC: #4)
  - [ ] 7.1 Add up/down arrow indicators
  - [ ] 7.2 Animate position changes
  - [ ] 7.3 Highlight significant moves

- [ ] **Task 8: Handle large player counts** (AC: #5)
  - [ ] 8.1 Make leaderboard scrollable
  - [ ] 8.2 Auto-scroll to current player
  - [ ] 8.3 Show "You: #X" quick indicator

- [ ] **Task 9: Style leaderboard** (AC: #1, #3, #4, #5)
  - [ ] 9.1 Create `.leaderboard` container styles
  - [ ] 9.2 Create `.leaderboard-entry` styles
  - [ ] 9.3 Create `.leaderboard-entry.is-current` styles
  - [ ] 9.4 Create rank change indicator styles
  - [ ] 9.5 Create streak indicator styles
  - [ ] 9.6 Add podium styling for top 3

- [ ] **Task 10: Leaderboard visibility states** (AC: #1)
  - [ ] 10.1 Compact view during PLAYING (sidebar or bottom)
  - [ ] 10.2 Prominent view during REVEAL
  - [ ] 10.3 Toggle to expand/collapse

- [ ] **Task 11: Unit tests** (AC: #1, #4)
  - [ ] 11.1 Test: players sorted by score descending
  - [ ] 11.2 Test: tied scores get same rank (e.g., two players with 50 pts both get #1)
  - [ ] 11.3 Test: rank_change calculated correctly (previous_rank - current_rank)
  - [ ] 11.4 Test: leaderboard includes all players including disconnected
  - [ ] 11.5 Test: ties don't skip ranks (e.g., #1, #1, #3 not #1, #1, #2)

- [ ] **Task 12: Integration tests** (AC: #2)
  - [ ] 12.1 Test: leaderboard updates after round
  - [ ] 12.2 Test: current player highlighted
  - [ ] 12.3 Test: streak indicators shown

- [ ] **Task 13: Verify no regressions**
  - [ ] 13.1 Run `pytest tests/unit/` - all tests pass
  - [ ] 13.2 Run `ruff check` - no new issues
  - [ ] 13.3 Test leaderboard with multiple players

## Dev Notes

### Existing Codebase Context

| File | Current State | Action |
|------|---------------|--------|
| `game/state.py` | Has `get_reveal_players_state()` | Add `get_leaderboard()` method |
| `game/player.py` | Has score, streak fields | Add `previous_rank` field |
| `www/player.html` | Has game-view, reveal-view | Add leaderboard sections |
| `www/js/player.js` | Has state handling | Add `updateLeaderboard()` |

### Leaderboard Data Structure

```python
# game/state.py

def get_leaderboard(self) -> list[dict]:
    """Get leaderboard sorted by score.

    Returns:
        List of player data with rank and movement info.
        Note: is_current is set client-side based on playerName.
    """
    # Sort by score descending, then by name for tie-breaking display order
    sorted_players = sorted(
        self.players.values(),
        key=lambda p: (-p.score, p.name)
    )

    leaderboard = []
    current_rank = 0
    previous_score = None

    for i, player in enumerate(sorted_players):
        # Handle ties (same score = same rank)
        # Example: scores [100, 80, 80, 50] -> ranks [1, 2, 2, 4]
        if player.score != previous_score:
            current_rank = i + 1  # Rank jumps to position (skips tied ranks)
        previous_score = player.score

        # Calculate rank change (positive = moved up)
        rank_change = 0
        if player.previous_rank is not None:
            rank_change = player.previous_rank - current_rank

        entry = {
            "rank": current_rank,
            "name": player.name,
            "score": player.score,
            "streak": player.streak,
            "is_admin": player.is_admin,
            "rank_change": rank_change,
            "connected": player.connected,
            # NOTE: is_current set client-side
        }
        leaderboard.append(entry)

    return leaderboard
```

**Tie Handling:** Same score = same rank, next rank skips. Example:
- Player A: 100 pts → Rank #1
- Player B: 80 pts → Rank #2
- Player C: 80 pts → Rank #2 (same as B)
- Player D: 50 pts → Rank #4 (skips #3)

### PlayerSession Addition

```python
# game/player.py
@dataclass
class PlayerSession:
    # ... existing fields ...
    previous_rank: int | None = None  # Rank before last update
```

### Update Ranks in end_round()

```python
# game/state.py - end_round()

# Before calculating new scores, store current ranks
sorted_by_score = sorted(self.players.values(), key=lambda p: -p.score)
for i, player in enumerate(sorted_by_score):
    player.previous_rank = i + 1

# ... calculate new scores ...

# After scoring, new ranks will be different
```

### State Broadcast with Leaderboard

**IMPORTANT:** The current `get_state()` method has NO parameters. To support `is_current` highlighting, we have two options:

**Option A (Recommended): Calculate is_current in JavaScript**
```python
# game/state.py - get_state() - NO CHANGES to signature
def get_state(self) -> dict:
    state = {
        # ... existing fields ...
        "leaderboard": self.get_leaderboard(),  # No player_name needed
    }
    return state
```

```javascript
// player.js - Set is_current client-side
leaderboard.forEach(entry => {
    entry.is_current = (entry.name === playerName);  // playerName is global
});
```

**Option B: Pass player_name through WebSocket handler**
```python
# This requires modifying WebSocket broadcast logic significantly
# NOT recommended for this story
```

**Use Option A** - client-side highlighting is simpler and doesn't require backend changes.

### HTML Structure

```html
<!-- Leaderboard section - can be placed in game-view or as overlay -->
<div id="leaderboard" class="leaderboard">
    <div class="leaderboard-header">
        <span class="leaderboard-title">Leaderboard</span>
        <button id="leaderboard-toggle" class="leaderboard-toggle">
            <span class="toggle-icon">▼</span>
        </button>
    </div>
    <div id="leaderboard-list" class="leaderboard-list">
        <!-- Populated by JavaScript -->
    </div>
    <div id="leaderboard-you" class="leaderboard-you hidden">
        <!-- Quick "You: #X" indicator when scrolled -->
    </div>
</div>
```

### JavaScript Implementation

```javascript
// player.js

function updateLeaderboard(data) {
    const leaderboard = data.leaderboard || [];
    const listEl = document.getElementById('leaderboard-list');
    if (!listEl) return;

    let html = '';
    leaderboard.forEach((entry, index) => {
        const rankClass = entry.rank <= 3 ? `is-top-${entry.rank}` : '';
        const currentClass = entry.is_current ? 'is-current' : '';
        const adminBadge = entry.is_admin ? '<span class="admin-badge">👑</span>' : '';

        // Rank change indicator
        let changeIndicator = '';
        if (entry.rank_change > 0) {
            changeIndicator = `<span class="rank-up">▲${entry.rank_change}</span>`;
        } else if (entry.rank_change < 0) {
            changeIndicator = `<span class="rank-down">▼${Math.abs(entry.rank_change)}</span>`;
        }

        // Streak indicator
        const streakIndicator = entry.streak >= 2
            ? `<span class="streak-indicator">🔥${entry.streak}</span>`
            : '';

        html += `
            <div class="leaderboard-entry ${rankClass} ${currentClass}" data-rank="${entry.rank}">
                <span class="entry-rank">#${entry.rank}</span>
                <span class="entry-name">${entry.name}${adminBadge}</span>
                <span class="entry-meta">
                    ${streakIndicator}
                    ${changeIndicator}
                </span>
                <span class="entry-score">${entry.score}</span>
            </div>
        `;
    });

    listEl.innerHTML = html;

    // Scroll to current player if many players
    if (leaderboard.length > 8) {
        scrollToCurrentPlayer();
    }

    // Update quick indicator
    updateYouIndicator(leaderboard);
}

function scrollToCurrentPlayer() {
    const currentEntry = document.querySelector('.leaderboard-entry.is-current');
    if (currentEntry) {
        currentEntry.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function updateYouIndicator(leaderboard) {
    const youEl = document.getElementById('leaderboard-you');
    const currentPlayer = leaderboard.find(e => e.is_current);
    if (youEl && currentPlayer) {
        youEl.textContent = `You: #${currentPlayer.rank}`;
        youEl.classList.remove('hidden');
    }
}
```

### CSS Styles

```css
/* Leaderboard container */
.leaderboard {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    max-width: 320px;
}

.leaderboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #f3f4f6;
    border-bottom: 1px solid #e5e7eb;
}

.leaderboard-title {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
}

.leaderboard-toggle {
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px;
}

.leaderboard-list {
    max-height: 300px;
    overflow-y: auto;
}

/* Leaderboard entries */
.leaderboard-entry {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    border-bottom: 1px solid #f3f4f6;
    transition: background 0.2s ease;
}

.leaderboard-entry:last-child {
    border-bottom: none;
}

.leaderboard-entry.is-current {
    background: #eff6ff;
    border-left: 3px solid #3b82f6;
}

/* Top 3 styling */
.leaderboard-entry.is-top-1 {
    background: linear-gradient(90deg, #fef3c7, #fde68a);
}

.leaderboard-entry.is-top-1 .entry-rank {
    color: #b45309;
    font-weight: 700;
}

.leaderboard-entry.is-top-2 {
    background: linear-gradient(90deg, #f3f4f6, #e5e7eb);
}

.leaderboard-entry.is-top-3 {
    background: linear-gradient(90deg, #fed7aa, #fdba74);
}

.entry-rank {
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    min-width: 28px;
}

.entry-name {
    flex: 1;
    font-size: 14px;
    font-weight: 500;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 4px;
}

.entry-meta {
    display: flex;
    align-items: center;
    gap: 4px;
}

.entry-score {
    font-size: 14px;
    font-weight: 700;
    color: #6366f1;
    min-width: 48px;
    text-align: right;
}

/* Rank change indicators */
.rank-up {
    font-size: 10px;
    color: #10b981;
    font-weight: 600;
}

.rank-down {
    font-size: 10px;
    color: #ef4444;
    font-weight: 600;
}

/* Streak indicator */
.streak-indicator {
    font-size: 11px;
    color: #f59e0b;
    font-weight: 600;
}

/* Quick you indicator */
.leaderboard-you {
    position: sticky;
    bottom: 0;
    padding: 8px 16px;
    background: #3b82f6;
    color: white;
    font-size: 12px;
    font-weight: 600;
    text-align: center;
}

/* Admin badge */
.admin-badge {
    font-size: 12px;
}
```

### Leaderboard Visibility by Phase

```javascript
// Show different views based on phase
function updateLeaderboardVisibility(phase) {
    const leaderboard = document.getElementById('leaderboard');
    if (!leaderboard) return;

    switch (phase) {
        case 'LOBBY':
            leaderboard.classList.add('is-compact');
            break;
        case 'PLAYING':
            leaderboard.classList.add('is-compact');
            break;
        case 'REVEAL':
            leaderboard.classList.remove('is-compact');
            leaderboard.classList.add('is-prominent');
            break;
        case 'END':
            leaderboard.classList.remove('is-compact');
            leaderboard.classList.add('is-final');
            break;
    }
}
```

### Architecture Compliance

- **Sorting:** Score descending, name for ties
- **Real-time:** Updates within 1 second (NFR5)
- **Ties:** Same score = same rank
- **Highlighting:** Current player always visible

### Anti-Patterns to Avoid

- Do NOT re-sort on every render (cache sorted list)
- Do NOT hide current player when scrolled
- Do NOT animate every update (only rank changes)
- Do NOT block UI for large player counts

### References

- [Source: epics.md#Story-5.5] - FR39, FR40, FR42 leaderboard requirements
- [Source: architecture.md] - NFR5 update latency
- [Source: 5-2-streak-tracking-and-bonuses.md] - Streak indicator pattern

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
