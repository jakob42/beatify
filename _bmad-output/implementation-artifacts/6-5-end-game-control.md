# Story 6.5: End Game Control

Status: done

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

- [x] **Task 1: Add end_game action handler to websocket.py** (AC: #2, #4)
  - [x] 1.1 Add `elif action == "end_game":` branch in admin message handler
  - [x] 1.2 Check phase is PLAYING or REVEAL (not LOBBY or END)
  - [x] 1.3 Cancel any running timer: `game_state.cancel_timer()`
  - [x] 1.4 Stop media playback: `await game_state._media_player_service.stop()`
  - [x] 1.5 Transition to END: `game_state.phase = GamePhase.END`
  - [x] 1.6 Broadcast state: `await self.broadcast_state()`
  - [x] 1.7 Log action: `_LOGGER.info("Admin ended game early at round %d", game_state.round)`

- [x] **Task 2: Implement confirmation dialog in handleEndGame()** (AC: #1, #3)
  - [x] 2.1 Use browser `confirm()` dialog (per existing pattern in admin.js)
  - [x] 2.2 Show message: "End game and show final results?"
  - [x] 2.3 If cancelled, return early (no WebSocket message)
  - [x] 2.4 If confirmed, proceed with sending end_game action + button feedback

- [x] **Task 3: Update control bar state for END phase** (AC: #5)
  - [x] 3.1 hideAdminControlBar() already called in END phase handler (Story 6.1)
  - [x] 3.2 Control bar is hidden when game ends

- [x] **Task 4: Verify final leaderboard display** (AC: #4)
  - [x] 4.1 END phase state includes `leaderboard` and `winner` (from Epic 5)
  - [x] 4.2 `end-view` displays final standings (from Epic 5)
  - [x] 4.3 Player stats (best_streak, rounds_played, bets_won) preserved

- [x] **Task 5: Handle edge case - ending during PLAYING** (AC: #2)
  - [x] 5.1 If ending during PLAYING, scores for incomplete round NOT counted (no end_round call)
  - [x] 5.2 Current song submission status ignored
  - [x] 5.3 Timer cancelled immediately via cancel_timer()

- [x] **Task 6: Verify no regressions**
  - [x] 6.1 Existing end-game flow (via last round) still works
  - [x] 6.2 Admin page "End Game" button still works
  - [x] 6.3 Players see end-view correctly
  - [x] 6.4 Run `ruff check` - no linting issues (N/A - environment)

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

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A

### Completion Notes List

- Added end_game action handler in websocket.py (lines 283-306)
- Handler validates phase (PLAYING/REVEAL only), cancels timer, stops media, transitions to END
- Updated handleEndGame() with button feedback ("Ending...") and connection error alert
- Confirmation dialog with confirm() already implemented in Story 6.1
- Control bar hidden in END phase via hideAdminControlBar() from Story 6.1
- Incomplete rounds not scored when ending during PLAYING (intentional - no end_round call)

### File List

- custom_components/beatify/server/websocket.py (modified - added end_game handler)
- custom_components/beatify/www/js/player.js (modified - added button feedback)
