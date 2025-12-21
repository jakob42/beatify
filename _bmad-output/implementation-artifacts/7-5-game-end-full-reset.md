# Story 7.5: Game End Full Reset

Status: done

## Story

As a **host**,
I want **the game to fully reset after ending**,
so that **I can start a fresh game without any stale state**.

## Acceptance Criteria

1. **AC1:** Given game transitions to END phase, When end_game is called, Then all player sessions are cleared from memory AND all WebSocket connections receive final state

2. **AC2:** Given game is ending, When cleanup runs, Then all timers are cancelled (round timer, pause timeout, removal tasks) AND no dangling async tasks remain

3. **AC3:** Given game is ending, When cleanup runs, Then media playback is stopped AND media player service is released

4. **AC4:** Given previous game has ended, When admin starts new game from admin page, Then new game_id is generated AND no state from previous game persists AND playlist is reshuffled

5. **AC5:** Given players are connected when game ends, When players attempt actions after end, Then they receive "Game ended" error AND are guided to rejoin via QR for new game

## Tasks / Subtasks

- [ ] **Task 1: Audit and enhance end_game() cleanup** (AC: #1, #2, #3)
  - [ ] 1.1 Review existing `end_game()` in game/state.py
  - [ ] 1.2 Ensure all state fields are reset to defaults
  - [ ] 1.3 Verify timer cancellation (already exists)
  - [ ] 1.4 Add media player stop call if not present
  - [ ] 1.5 Clear playlist manager reference

- [ ] **Task 2: Clean up WebSocket pending tasks** (AC: #2)
  - [ ] 2.1 Cancel all `_pending_removals` tasks in websocket handler
  - [ ] 2.2 Cancel `_admin_disconnect_task` if exists
  - [ ] 2.3 Add `cleanup_all_tasks()` method to handler

- [ ] **Task 3: Send final state to all players before cleanup** (AC: #1, #5)
  - [ ] 3.1 Broadcast END state before clearing players
  - [ ] 3.2 Players dict cleared after broadcast completes
  - [ ] 3.3 Verify players receive final leaderboard

- [ ] **Task 4: Add end_game API call for admin page** (AC: #4)
  - [ ] 4.1 Verify `/beatify/api/end-game` endpoint exists
  - [ ] 4.2 Ensure it calls full cleanup
  - [ ] 4.3 Stop media player on admin-triggered end

- [ ] **Task 5: Verify new game starts fresh** (AC: #4)
  - [ ] 5.1 Verify `create_game()` generates new game_id
  - [ ] 5.2 Verify playlist is reshuffled on new game
  - [ ] 5.3 Verify no player sessions carry over

- [ ] **Task 6: Handle stale WebSocket connections** (AC: #5)
  - [ ] 6.1 When game ends, set game_id to None
  - [ ] 6.2 Subsequent messages get "No active game" error
  - [ ] 6.3 Players see "Game ended" and can refresh for new game

- [ ] **Task 7: Add game_ended message type** (AC: #5)
  - [ ] 7.1 Broadcast `type: "game_ended"` before cleanup
  - [ ] 7.2 Client handles by showing end view with rejoin hint
  - [ ] 7.3 Client clears session storage

- [ ] **Task 8: Verify no regressions**
  - [ ] 8.1 Run `ruff check custom_components/beatify/`
  - [ ] 8.2 Test game end from reveal phase
  - [ ] 8.3 Test game end from admin control bar
  - [ ] 8.4 Test new game after previous game
  - [ ] 8.5 Verify no memory leaks (players dict empty)

## Dev Notes

### Pre-flight Check (REQUIRED)

**BEFORE starting implementation, verify Story 7-1 is complete:**

- [ ] `_admin_disconnect_task` field exists on WebSocket handler (added in Story 7-1)
- [ ] `pause_game()` method exists (Story 7-1)
- [ ] `PAUSED` phase handling works (Story 7-1)

**If Story 7-1 is not complete, implement it first.**

### Current State Analysis

The codebase already has **comprehensive end_game() cleanup**:

**game/state.py (lines 243-276):**
```python
def end_game(self) -> None:
    """End the current game and reset state."""
    _LOGGER.info("Game ended: %s", self.game_id)
    # Cancel any running timer
    self.cancel_timer()
    self.game_id = None
    self.phase = GamePhase.LOBBY
    self.playlists = []
    self.songs = []
    self.media_player = None
    self.join_url = None
    self.players = {}
    # ... resets all fields ...
```

**websocket.py (lines 283-306):**
- Admin `end_game` action exists
- Cancels timer, stops media, sets phase to END
- Broadcasts final state

**What Might Be Missing:**
- Pending removal tasks not cancelled on game end
- Admin disconnect task not cancelled (introduced in Story 7-1)
- `game_ended` broadcast message for clients
- Media player service cleanup (just set to None, no explicit release method needed)

### Implementation Details

#### 1. Enhanced Cleanup in WebSocket Handler

Add method to cancel all pending tasks:

```python
async def cleanup_game_tasks(self) -> None:
    """Cancel all pending tasks related to the game.

    Note: _admin_disconnect_task is introduced in Story 7-1.
    If Story 7-1 is not yet implemented, only _pending_removals cleanup applies.
    """
    # Cancel all pending player removals (existing infrastructure)
    for task in list(self._pending_removals.values()):
        if not task.done():
            task.cancel()
    self._pending_removals.clear()

    # Cancel admin disconnect task (added by Story 7-1)
    if hasattr(self, '_admin_disconnect_task'):
        task = self._admin_disconnect_task
        if task and not task.done():
            task.cancel()
        self._admin_disconnect_task = None

    _LOGGER.debug("Cleaned up all pending game tasks")
```

#### 2. Modify end_game Action Handler

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

    # Broadcast final state to all players FIRST
    await self.broadcast_state()

    # Send game_ended notification
    await self.broadcast({"type": "game_ended"})

    # Cleanup pending tasks
    await self.cleanup_game_tasks()

    # Note: Don't call game_state.end_game() here
    # Let admin page handle full reset when creating new game
```

#### 3. Handle game_ended on Client

In player.js:

```javascript
} else if (data.type === 'game_ended') {
    // Game has fully ended, clear session
    clearStoredSession();

    // Show end view if not already shown
    if (!document.getElementById('end-view').classList.contains('hidden')) {
        return;  // Already showing end view
    }

    // Update end view with message about new game
    var endMessage = document.getElementById('end-player-message');
    if (endMessage) {
        endMessage.innerHTML =
            '<p>Thanks for playing!</p>' +
            '<p class="rejoin-hint">Scan the QR code again to join the next game.</p>';
    }

    showView('end-view');
}

function clearStoredSession() {
    try {
        localStorage.removeItem(STORAGE_KEY_NAME);
        sessionStorage.removeItem('beatify_admin_name');
        sessionStorage.removeItem('beatify_is_admin');
    } catch (e) {
        // Ignore storage errors
    }
    playerName = null;
    isAdmin = false;

    // Close WebSocket to prevent stale connections
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
    }
    ws = null;
}
```

#### 4. Verify end_game() Completeness

Current `end_game()` already resets:
- `game_id = None`
- `phase = GamePhase.LOBBY`
- `playlists = []`
- `songs = []`
- `media_player = None`
- `join_url = None`
- `players = {}`
- `round = 0`
- `total_rounds = 0`
- `deadline = None`
- `current_song = None`
- `last_round = False`
- `pause_reason = None`
- `_previous_phase = None`
- `_playlist_manager = None`
- `_media_player_service = None`
- `round_start_time = None`
- `round_duration = DEFAULT_ROUND_DURATION`
- `song_stopped = False`
- `volume_level = 0.5`

**Add missing fields (from Epic 7):**

```python
def end_game(self) -> None:
    """End the current game and reset state."""
    _LOGGER.info("Game ended: %s", self.game_id)
    # ... existing cleanup ...

    # Epic 7 additions
    self.disconnected_admin_name = None  # Story 7-2
```

#### 5. New Game Fresh Start Verification

`create_game()` already:
- Generates new `game_id` via `secrets.token_urlsafe(8)`
- Creates new `PlaylistManager` (shuffles songs)
- Resets all round tracking
- Clears `players = {}`

No changes needed for new game creation.

#### 6. Stale Connection Handling

When game_id is None, `_handle_message()` already returns error:

```python
if not game_state or not game_state.game_id:
    await ws.send_json({
        "type": "error",
        "code": ERR_GAME_NOT_STARTED,
        "message": "No active game",
    })
    return
```

### Architecture Compliance

- **State Management:** Uses existing end_game() pattern
- **WebSocket:** Uses existing broadcast pattern
- **Error Handling:** Uses existing error code pattern

### End Game Flow Diagram

```
Admin clicks "End Game"
         │
         ▼
Cancel timer ─────────────────┐
         │                    │
         ▼                    │
Stop media playback           │
         │                    │
         ▼                    │
Set phase = END               │
         │                    │
         ▼                    │
Broadcast final state ────────┼── Players see final leaderboard
         │                    │
         ▼                    │
Broadcast "game_ended" ───────┼── Clients clear session storage
         │                    │
         ▼                    │
Cancel pending tasks          │
         │                    │
         ▼                    │
(Admin page: end_game() ──────┘
 when creating new game)
```

### Anti-Patterns to Avoid

- Do NOT clear players before broadcasting final state
- Do NOT leave dangling async tasks
- Do NOT allow actions after game_id is None
- Do NOT keep stale WebSocket connections

### Testing Considerations

1. **End game from PLAYING** - All cleanup happens, final leaderboard shown
2. **End game from REVEAL** - Same cleanup, players see results
3. **Start new game** - Fresh game_id, empty player list
4. **Player actions after end** - "No active game" error
5. **Memory check** - players dict empty, no task references

### Memory Leak Prevention

Ensure these are cleared on game end:
- `players` dict → `{}`
- `_pending_removals` → cleared (existing dict on websocket handler)
- `_admin_disconnect_task` → None (added by Story 7-1)
- `_timer_task` → cancelled and None (existing field)
- `_playlist_manager` → None (existing field)
- `_media_player_service` → None (no explicit release needed, just clear reference)

### Broadcast Error Handling

When broadcasting final state and game_ended:
- Use existing `broadcast()` method which handles disconnected clients gracefully
- If a client WebSocket fails during broadcast, it's logged but doesn't block cleanup
- No timeout needed - individual send failures are caught in existing broadcast implementation

### References

- [Source: epics.md#Story 7.5] - FR53 requirements
- [Source: game/state.py:243-276] - Existing end_game()
- [Source: websocket.py:283-306] - Admin end_game action
- [Source: game/state.py:99-159] - create_game() fresh start

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

