# Story 6.5: End Game Control

Status: ready-for-dev

## Story

As a **host playing the game**,
I want **to end the game immediately from the control bar**,
so that **I can wrap up the session when needed (time constraints, issues, etc.)**.

## Acceptance Criteria

1. **AC1:** Given host taps "End Game" button, When game is in any phase (PLAYING/REVEAL), Then confirmation dialog appears (FR46) And user can confirm or cancel

2. **AC2:** Given host confirms "End Game", When confirmation is accepted, Then game transitions to END phase And final leaderboard is shown to all players

3. **AC3:** Given host cancels "End Game", When confirmation is rejected, Then game continues normally And no state changes

4. **AC4:** Given game ends via End Game button, When final leaderboard is shown, Then all player stats are preserved And winner is highlighted

5. **AC5:** Given game has ended, When admin control bar is displayed, Then "End Game" button is disabled (game already ended)

## Tasks / Subtasks

- [ ] **Task 1: Add end_game action handler to websocket.py** (AC: #2, #4)
  - [ ] 1.1 Add `elif action == "end_game":` branch in admin message handler
  - [ ] 1.2 Check phase is PLAYING or REVEAL (not LOBBY or END)
  - [ ] 1.3 Cancel any running timer: `game_state.cancel_timer()`
  - [ ] 1.4 Stop media playback: `await game_state._media_player_service.stop()`
  - [ ] 1.5 Transition to END: `game_state.phase = GamePhase.END`
  - [ ] 1.6 Broadcast state: `await self.broadcast_state()`
  - [ ] 1.7 Log action: `_LOGGER.info("Admin ended game early at round %d", game_state.round)`

- [ ] **Task 2: Implement confirmation dialog in handleEndGame()** (AC: #1, #3)
  - [ ] 2.1 Use browser `confirm()` dialog (per existing pattern in admin.js)
  - [ ] 2.2 Show message: "End game and show final results?"
  - [ ] 2.3 If cancelled, return early (no WebSocket message)
  - [ ] 2.4 If confirmed, proceed with sending end_game action

- [ ] **Task 3: Update control bar state for END phase** (AC: #5)
  - [ ] 3.1 In `updateControlBarState()`: hide entire control bar during END phase
  - [ ] 3.2 Alternatively: disable all buttons and show "Game Ended" state

- [ ] **Task 4: Verify final leaderboard display** (AC: #4)
  - [ ] 4.1 Confirm END phase state includes `leaderboard` and `winner`
  - [ ] 4.2 Confirm `end-view` displays final standings (from Epic 5)
  - [ ] 4.3 Ensure player stats (best_streak, rounds_played, bets_won) preserved

- [ ] **Task 5: Handle edge case - ending during PLAYING** (AC: #2)
  - [ ] 5.1 If ending during PLAYING, scores for incomplete round NOT counted
  - [ ] 5.2 Current song submission status ignored
  - [ ] 5.3 Timer cancelled immediately

- [ ] **Task 6: Verify no regressions**
  - [ ] 6.1 Existing end-game flow (via last round) still works
  - [ ] 6.2 Admin page "End Game" button still works
  - [ ] 6.3 Players see end-view correctly
  - [ ] 6.4 Run `ruff check` - no linting issues

## Dev Notes

### WebSocket Handler (websocket.py)

Add after `set_volume` handler:

```python
elif action == "end_game":
    if game_state.phase not in (GamePhase.PLAYING, GamePhase.REVEAL):
        await ws.send_json({
            "type": "error",
            "code": ERR_INVALID_ACTION,
            "message": "Cannot end game in current phase",
        })
        return

    # Cancel timer if running
    game_state.cancel_timer()

    # Stop media playback
    if game_state._media_player_service:
        await game_state._media_player_service.stop()

    # Transition to END
    game_state.phase = GamePhase.END
    _LOGGER.info("Admin ended game early at round %d", game_state.round)

    # Broadcast final state to all players
    await self.broadcast_state()
```

### JavaScript Handler (player.js)

Update `handleEndGame()`:
```javascript
/**
 * Handle End Game button click
 */
function handleEndGame() {
    // Confirmation dialog
    if (!confirm('End game and show final results?')) {
        return;
    }

    // Debounce check
    if (!debounceAdminAction('end')) return;

    // Check WebSocket connection
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('Connection lost. Please refresh.');
        return;
    }

    // Update button state
    var endBtn = document.getElementById('end-game-btn');
    if (endBtn) {
        endBtn.disabled = true;
        var labelEl = endBtn.querySelector('.control-label');
        if (labelEl) labelEl.textContent = 'Ending...';
    }

    // Send end game request
    ws.send(JSON.stringify({
        type: 'admin',
        action: 'end_game'
    }));
}
```

### Control Bar in END Phase

Update `handleServerMessage()` to hide control bar during END:
```javascript
if (data.type === 'state') {
    // ... existing phase handling ...

    if (data.phase === 'END') {
        stopCountdown();
        showView('end-view');
        hideAdminControlBar();  // Hide control bar on game end
        // ... render final leaderboard ...
    }
}
```

### Message Flow

```
[Admin taps End Game]
      |
      v
Browser: confirm("End game and show final results?")
      |
      v (User confirms)
Client sends: {"type": "admin", "action": "end_game"}
      |
      v
Server: Validates admin + phase (PLAYING or REVEAL)
      |
      v
Server: game_state.cancel_timer()
      |
      v
Server: MediaPlayerService.stop()
      |
      v
Server: game_state.phase = GamePhase.END
      |
      v
Server broadcasts: {"type": "state", "phase": "END", "leaderboard": [...], "winner": {...}}
      |
      v
All clients: showView('end-view'), hideAdminControlBar()
```

### What Happens When Ending During PLAYING

When admin ends game during PLAYING phase:
1. Timer is cancelled immediately
2. Media playback stops
3. **Current round submissions are NOT scored** (incomplete round)
4. Scores remain as they were after last completed round
5. Game transitions directly to END (skips REVEAL for incomplete round)

This is intentional - partial rounds shouldn't count.

### End-View Content (already implemented in Epic 5)

The END phase state from `get_state()` includes:
```python
elif self.phase == GamePhase.END:
    state["leaderboard"] = self.get_final_leaderboard()
    state["game_stats"] = {
        "total_rounds": self.round,
        "total_players": len(self.players),
    }
    if self.players:
        winner = max(self.players.values(), key=lambda p: p.score)
        state["winner"] = {"name": winner.name, "score": winner.score}
```

### Architecture Compliance

- Uses existing `cancel_timer()` and `MediaPlayerService.stop()`
- Uses browser `confirm()` for confirmation (matches admin.js pattern)
- Follows WebSocket message pattern

### Anti-Patterns to Avoid

- Do NOT score the incomplete round when ending during PLAYING
- Do NOT allow ending during LOBBY phase (game hasn't started)
- Do NOT skip confirmation dialog (prevents accidental game end)
- Do NOT forget to hide control bar when game ends

### Testing Considerations

1. **Manual Test:** During PLAYING, tap End Game, cancel, verify game continues
2. **Manual Test:** During PLAYING, tap End Game, confirm, verify END phase shown
3. **Manual Test:** During REVEAL, tap End Game, confirm, verify END phase shown
4. **Manual Test:** Verify final leaderboard shows all players with correct scores
5. **Manual Test:** Verify music stops when game ends

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
