# Story 5.6: Final Leaderboard

Status: ready-for-dev

## Story

As a **player**,
I want **to see the final standings when the game ends**,
so that **there's a celebratory conclusion to the competition**.

## Acceptance Criteria

1. **AC1:** Given game transitions to END state, When final leaderboard displays, Then all players see the complete final standings (FR41) And leaderboard remains visible until dismissed

2. **AC2:** Given final leaderboard displays, When player views results, Then top 3 players are highlighted (podium style) And each player sees their final rank and total score

3. **AC3:** Given final leaderboard displays, When player views their own entry, Then their entry is visually highlighted And shows their final stats (score, best streak, etc.)

4. **AC4:** Given game has ended, When final leaderboard is shown, Then admin sees option to "Start New Game" And players see "Thanks for playing!" message

## Tasks / Subtasks

**DEPENDENCY:** Requires Story 5.5 completed (live leaderboard).

- [ ] **Task 1: Track game stats for final display** (AC: #3)
  - [ ] 1.1 Add `best_streak: int = 0` to PlayerSession
  - [ ] 1.2 Update best_streak when streak exceeds it
  - [ ] 1.3 Track `rounds_played: int = 0`
  - [ ] 1.4 Track `total_bets_won: int = 0`

- [ ] **Task 2: Create end-view HTML** (AC: #1, #2, #4)
  - [ ] 2.1 Add `#end-view` section to player.html
  - [ ] 2.2 Create podium layout for top 3
  - [ ] 2.3 Add full leaderboard below podium
  - [ ] 2.4 Add player stats section
  - [ ] 2.5 Add admin "Start New Game" button
  - [ ] 2.6 Add "Thanks for playing!" message

- [ ] **Task 3: Implement updateEndView() JavaScript** (AC: #1, #2, #3)
  - [ ] 3.1 Render podium with top 3 players
  - [ ] 3.2 Render full ranked list
  - [ ] 3.3 Highlight current player's entry
  - [ ] 3.4 Show player's personal stats

- [ ] **Task 4: Create podium component** (AC: #2)
  - [ ] 4.1 Design 1st/2nd/3rd place layout
  - [ ] 4.2 Show player names prominently
  - [ ] 4.3 Show final scores
  - [ ] 4.4 Add trophy/medal icons

- [ ] **Task 5: Display personal stats** (AC: #3)
  - [ ] 5.1 Show final rank ("You placed #X!")
  - [ ] 5.2 Show total score
  - [ ] 5.3 Show best streak achieved
  - [ ] 5.4 Show rounds participated

- [ ] **Task 6: Admin controls for end state** (AC: #4)
  - [ ] 6.1 Show "Start New Game" button for admin only
  - [ ] 6.2 Wire button to admin action: `{"type": "admin", "action": "new_game"}`
  - [ ] 6.3 Add `new_game` handler in WebSocket (calls `game_state.end_game()` then redirects)
  - [ ] 6.4 Server responds with redirect URL to admin setup page

- [ ] **Task 7: Player end message** (AC: #4)
  - [ ] 7.1 Show "Thanks for playing!" for non-admin
  - [ ] 7.2 Show celebratory animation
  - [ ] 7.3 Optional: Show QR code for next game

- [ ] **Task 8: Update state broadcast for END** (AC: #1, #3)
  - [ ] 8.1 Include final leaderboard in END state
  - [ ] 8.2 Include player stats (best_streak, rounds_played)
  - [ ] 8.3 Include game summary data

- [ ] **Task 9: Style final leaderboard** (AC: #1, #2, #3)
  - [ ] 9.1 Create `.end-view` container styles
  - [ ] 9.2 Create `.podium` styles with 1st/2nd/3rd heights
  - [ ] 9.3 Create `.final-stats` styles
  - [ ] 9.4 Add celebration animations (confetti optional)
  - [ ] 9.5 Style "Start New Game" button

- [ ] **Task 10: Handle view transition** (AC: #1)
  - [ ] 10.1 Transition from reveal-view to end-view
  - [ ] 10.2 Auto-show end-view when END state received
  - [ ] 10.3 Prevent navigation away (lock to end view)

- [ ] **Task 11: Integration tests** (AC: #1, #2)
  - [ ] 11.1 Test: END state shows final leaderboard
  - [ ] 11.2 Test: top 3 in podium
  - [ ] 11.3 Test: current player highlighted
  - [ ] 11.4 Test: admin sees new game button

- [ ] **Task 12: Verify no regressions**
  - [ ] 12.1 Run `pytest tests/unit/` - all tests pass
  - [ ] 12.2 Run `ruff check` - no new issues
  - [ ] 12.3 Test complete game flow to END

## Dev Notes

### Existing Codebase Context

| File | Current State | Action |
|------|---------------|--------|
| `game/player.py` | Has score, streak | Add best_streak, rounds_played |
| `game/state.py` | Has END phase | Add get_final_state() |
| `www/player.html` | Has views | Add end-view section |
| `www/js/player.js` | Has view handling | Add updateEndView() |

### PlayerSession Additions

```python
# game/player.py - Add to PlayerSession dataclass

    # Final stats tracking (Story 5.6)
    best_streak: int = 0  # Highest streak achieved during game
    rounds_played: int = 0  # Rounds where player submitted
    bets_won: int = 0  # Successful bets
```

**NOTE:** These fields track CUMULATIVE stats across the entire game. Do NOT reset in `reset_round()`.

### Update Stats in end_round() - EVERY ROUND

**CRITICAL:** Stats must be updated in `end_round()` EVERY round, not just at game end.

```python
# game/state.py - In end_round(), INSIDE the player loop for submitters:

for player in self.players.values():
    if player.submitted and correct_year is not None:
        # ... existing scoring logic from 5.1, 5.2, 5.3 ...

        # Track cumulative stats (Story 5.6)
        player.rounds_played += 1

        # Update best streak (AFTER streak increment)
        if player.streak > player.best_streak:
            player.best_streak = player.streak

        # Track bet wins (AFTER bet outcome calculated)
        if player.bet_outcome == "won":
            player.bets_won += 1
```

**Place this AFTER streak calculation (5.2) and bet outcome calculation (5.3).**

### State Broadcast for END

```python
# game/state.py - get_state()

def get_state(self, player_name: str | None = None) -> dict:
    state = {
        "type": "state",
        "phase": self.phase.value,
        # ... other fields ...
    }

    if self.phase == GamePhase.END:
        state["final_leaderboard"] = self.get_leaderboard(player_name)
        state["game_stats"] = {
            "total_rounds": self.current_round,
            "total_players": len(self.players),
        }
        # Include personal stats for the requesting player
        if player_name and player_name in self.players:
            p = self.players[player_name]
            state["your_stats"] = {
                "rank": self._get_player_rank(player_name),
                "score": p.score,
                "best_streak": p.best_streak,
                "rounds_played": p.rounds_played,
                "bets_won": p.bets_won,
            }

    return state
```

### HTML End View

```html
<!-- End view -->
<div id="end-view" class="view hidden">
    <div class="end-container">
        <!-- Header -->
        <div class="end-header">
            <h1 class="end-title">Game Over!</h1>
            <p class="end-subtitle">Thanks for playing Beatify</p>
        </div>

        <!-- Podium for top 3 -->
        <div class="podium">
            <div class="podium-place podium-2">
                <div class="podium-medal">🥈</div>
                <div class="podium-name" id="podium-2-name">---</div>
                <div class="podium-score" id="podium-2-score">0</div>
                <div class="podium-stand">2</div>
            </div>
            <div class="podium-place podium-1">
                <div class="podium-medal">🥇</div>
                <div class="podium-name" id="podium-1-name">---</div>
                <div class="podium-score" id="podium-1-score">0</div>
                <div class="podium-stand">1</div>
            </div>
            <div class="podium-place podium-3">
                <div class="podium-medal">🥉</div>
                <div class="podium-name" id="podium-3-name">---</div>
                <div class="podium-score" id="podium-3-score">0</div>
                <div class="podium-stand">3</div>
            </div>
        </div>

        <!-- Your result -->
        <div class="your-result">
            <div class="your-result-header">Your Result</div>
            <div class="your-result-rank" id="your-final-rank">#1</div>
            <div class="your-result-score" id="your-final-score">0 points</div>
            <div class="your-result-stats">
                <div class="stat">
                    <span class="stat-value" id="stat-best-streak">0</span>
                    <span class="stat-label">Best Streak</span>
                </div>
                <div class="stat">
                    <span class="stat-value" id="stat-rounds">0</span>
                    <span class="stat-label">Rounds Played</span>
                </div>
                <div class="stat">
                    <span class="stat-value" id="stat-bets">0</span>
                    <span class="stat-label">Bets Won</span>
                </div>
            </div>
        </div>

        <!-- Full leaderboard -->
        <div class="final-leaderboard">
            <div class="final-leaderboard-header">Full Rankings</div>
            <div id="final-leaderboard-list" class="final-leaderboard-list">
                <!-- Populated by JavaScript -->
            </div>
        </div>

        <!-- Admin controls -->
        <div id="end-admin-controls" class="end-admin-controls hidden">
            <button id="new-game-btn" class="new-game-btn">
                Start New Game
            </button>
        </div>

        <!-- Player message -->
        <div id="end-player-message" class="end-player-message hidden">
            <p>Thanks for playing! 🎉</p>
            <p class="end-hint">Wait for the host to start a new game</p>
        </div>
    </div>
</div>
```

### JavaScript Implementation

```javascript
// player.js

function updateEndView(data) {
    const leaderboard = data.final_leaderboard || [];
    const yourStats = data.your_stats || {};

    // Update podium
    const top3 = leaderboard.slice(0, 3);
    [1, 2, 3].forEach(place => {
        const player = top3.find(p => p.rank === place);
        const nameEl = document.getElementById(`podium-${place}-name`);
        const scoreEl = document.getElementById(`podium-${place}-score`);
        if (nameEl) nameEl.textContent = player ? player.name : '---';
        if (scoreEl) scoreEl.textContent = player ? player.score : '0';
    });

    // Update your result
    document.getElementById('your-final-rank').textContent = `#${yourStats.rank || '?'}`;
    document.getElementById('your-final-score').textContent = `${yourStats.score || 0} points`;
    document.getElementById('stat-best-streak').textContent = yourStats.best_streak || 0;
    document.getElementById('stat-rounds').textContent = yourStats.rounds_played || 0;
    document.getElementById('stat-bets').textContent = yourStats.bets_won || 0;

    // Update full leaderboard
    const listEl = document.getElementById('final-leaderboard-list');
    if (listEl) {
        listEl.innerHTML = leaderboard.map(entry => `
            <div class="final-entry ${entry.is_current ? 'is-current' : ''}">
                <span class="final-rank">#${entry.rank}</span>
                <span class="final-name">${entry.name}${entry.is_admin ? ' 👑' : ''}</span>
                <span class="final-score">${entry.score}</span>
            </div>
        `).join('');
    }

    // Show admin or player controls
    const currentPlayer = leaderboard.find(p => p.is_current);
    const adminControls = document.getElementById('end-admin-controls');
    const playerMessage = document.getElementById('end-player-message');

    if (currentPlayer && currentPlayer.is_admin) {
        adminControls.classList.remove('hidden');
        playerMessage.classList.add('hidden');
    } else {
        adminControls.classList.add('hidden');
        playerMessage.classList.remove('hidden');
    }
}

// Wire up new game button
document.addEventListener('DOMContentLoaded', () => {
    const newGameBtn = document.getElementById('new-game-btn');
    if (newGameBtn) {
        newGameBtn.addEventListener('click', handleNewGame);
    }
});

function handleNewGame() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'admin',
            action: 'new_game'
        }));
    }
}
```

### CSS Styles

```css
/* End view container */
.end-container {
    padding: 24px;
    max-width: 480px;
    margin: 0 auto;
    text-align: center;
}

.end-header {
    margin-bottom: 24px;
}

.end-title {
    font-size: 32px;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 8px;
}

.end-subtitle {
    font-size: 16px;
    color: #6b7280;
}

/* Podium */
.podium {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: 8px;
    margin-bottom: 32px;
}

.podium-place {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100px;
}

.podium-medal {
    font-size: 32px;
    margin-bottom: 8px;
}

.podium-name {
    font-size: 14px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 4px;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.podium-score {
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 8px;
}

.podium-stand {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: 800;
    color: white;
    border-radius: 8px 8px 0 0;
}

.podium-1 .podium-stand {
    height: 80px;
    background: linear-gradient(180deg, #fbbf24, #d97706);
}

.podium-2 .podium-stand {
    height: 60px;
    background: linear-gradient(180deg, #9ca3af, #6b7280);
}

.podium-3 .podium-stand {
    height: 40px;
    background: linear-gradient(180deg, #fb923c, #c2410c);
}

/* Your result */
.your-result {
    background: #eff6ff;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
}

.your-result-header {
    font-size: 14px;
    font-weight: 600;
    color: #3b82f6;
    margin-bottom: 8px;
}

.your-result-rank {
    font-size: 48px;
    font-weight: 800;
    color: #1f2937;
}

.your-result-score {
    font-size: 18px;
    color: #6b7280;
    margin-bottom: 16px;
}

.your-result-stats {
    display: flex;
    justify-content: center;
    gap: 24px;
}

.stat {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-value {
    font-size: 24px;
    font-weight: 700;
    color: #6366f1;
}

.stat-label {
    font-size: 12px;
    color: #6b7280;
}

/* Final leaderboard */
.final-leaderboard {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 24px;
}

.final-leaderboard-header {
    padding: 12px 16px;
    background: #f3f4f6;
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    text-align: left;
}

.final-leaderboard-list {
    max-height: 200px;
    overflow-y: auto;
}

.final-entry {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    border-bottom: 1px solid #f3f4f6;
}

.final-entry.is-current {
    background: #eff6ff;
}

.final-rank {
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    width: 32px;
}

.final-name {
    flex: 1;
    font-size: 14px;
    color: #1f2937;
}

.final-score {
    font-size: 14px;
    font-weight: 600;
    color: #6366f1;
}

/* Admin controls */
.end-admin-controls {
    margin-bottom: 16px;
}

.new-game-btn {
    padding: 16px 32px;
    font-size: 18px;
    font-weight: 600;
    color: white;
    background: #10b981;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: background 0.2s ease;
}

.new-game-btn:hover {
    background: #059669;
}

/* Player message */
.end-player-message {
    color: #6b7280;
}

.end-hint {
    font-size: 14px;
    margin-top: 8px;
}
```

### New Admin Action: new_game

**Add to WebSocket handler:**
```python
# server/websocket.py - In admin action handler

elif action == "new_game":
    if not player.is_admin:
        await self.send_error(ws, "NOT_ADMIN", "Only admin can start new game")
        return

    # End current game
    self.game_state.end_game()

    # Send redirect to all clients
    await self.broadcast({
        "type": "redirect",
        "url": "/beatify/admin"  # Admin goes to setup, players see "game ended"
    })
```

**Add to architecture WebSocket schema (const.py or documentation):**
```python
# Admin actions: start_game, stop_song, next_round, end_game, set_volume, new_game
```

### Architecture Compliance

- **Final Leaderboard:** All players visible (FR41)
- **Podium:** Top 3 highlighted
- **Stats:** Best streak, rounds played, bets won
- **Admin Control:** "Start New Game" button with `new_game` action
- **NEW:** `new_game` admin action defined

### Anti-Patterns to Avoid

- Do NOT allow game restart without admin
- Do NOT hide any players from final leaderboard
- Do NOT navigate away from end view until new game
- Do NOT forget to track best_streak DURING game (not just at end)
- Do NOT reset best_streak/rounds_played/bets_won in reset_round()

### References

- [Source: epics.md#Story-5.6] - FR41 final leaderboard
- [Source: 5-5-live-leaderboard.md] - Leaderboard component base
- [Source: architecture.md] - END state handling

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
