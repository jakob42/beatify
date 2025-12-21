# Story 7.1: Admin Disconnect & Game Pause

Status: done

## Story

As a **player**,
I want **the game to pause when the host disconnects**,
so that **the game doesn't continue without someone in control**.

## Acceptance Criteria

1. **AC1:** Given game is in progress (LOBBY, PLAYING, or REVEAL), When admin's WebSocket connection closes unexpectedly, Then game transitions to PAUSED state after 5-second grace period

2. **AC2:** Given game transitions to PAUSED, When in PLAYING phase, Then timer stops counting down AND audio playback stops immediately

3. **AC3:** Given game is paused due to admin disconnect, When players view their screens, Then all players see "Waiting for admin..." message AND game UI is dimmed/overlaid AND players cannot submit guesses

4. **AC4:** Given admin closes browser or loses connection, When disconnect is detected, Then system waits 5 seconds (grace period) before pausing AND if admin reconnects within grace period, no pause occurs

5. **AC5:** Given game is paused, When pause duration exceeds 5 minutes (optional), Then game may auto-end with current standings preserved

## Tasks / Subtasks

- [ ] **Task 1: Implement PAUSED state transition in GameState** (AC: #1, #2)
  - [ ] 1.1 Add `pause_game(reason: str)` method to `game/state.py`
  - [ ] 1.2 Store `_previous_phase` before transitioning to PAUSED
  - [ ] 1.3 Cancel timer task when pausing from PLAYING phase
  - [ ] 1.4 Add `resume_game()` method to restore from `_previous_phase`
  - [ ] 1.5 Update `get_state()` to include pause_reason in PAUSED phase

- [ ] **Task 2: Detect admin disconnect in WebSocket handler** (AC: #1, #4)
  - [ ] 2.1 In `_handle_disconnect()`, check if disconnected player is admin
  - [ ] 2.2 Create `_admin_disconnect_timeout` task with 5-second delay
  - [ ] 2.3 If admin reconnects within grace period, cancel timeout task
  - [ ] 2.4 After timeout, call `game_state.pause_game("admin_disconnected")`
  - [ ] 2.5 Broadcast PAUSED state to all players

- [ ] **Task 3: Verify media playback stops on pause** (AC: #2)
  - [ ] 3.1 Verify `pause_game()` calls `await _media_player_service.stop()` (integrated in Task 1)
  - [ ] 3.2 Optionally store remaining time for resume (deferred to Story 7-2)

- [ ] **Task 4: Add PAUSED view to frontend** (AC: #3)
  - [ ] 4.1 Add `paused-view` section to player.html
  - [ ] 4.2 Design "Waiting for admin..." message with dimmed overlay
  - [ ] 4.3 Add CSS styles for `.paused-overlay` and `.paused-message`

- [ ] **Task 5: Handle PAUSED phase in player.js** (AC: #3)
  - [ ] 5.1 Add `paused-view` to `showView()` view list
  - [ ] 5.2 Handle `phase === 'PAUSED'` in `handleServerMessage()`
  - [ ] 5.3 Stop countdown timer when entering PAUSED
  - [ ] 5.4 Show paused overlay/view
  - [ ] 5.5 Disable submission controls

- [ ] **Task 6: Implement pause timeout (optional)** (AC: #5)
  - [ ] 6.1 Start 5-minute timer when entering PAUSED
  - [ ] 6.2 Cancel timer if admin reconnects
  - [ ] 6.3 On timeout, transition to END state

- [ ] **Task 7: Verify no regressions**
  - [ ] 7.1 Run `ruff check custom_components/beatify/`
  - [ ] 7.2 Verify normal player disconnect still works with grace period
  - [ ] 7.3 Manual test: admin disconnect during PLAYING
  - [ ] 7.4 Manual test: admin disconnect during REVEAL
  - [ ] 7.5 Manual test: admin disconnect during LOBBY

## Dev Notes

### Current State Analysis

The codebase already has **partial infrastructure** for PAUSED state:

**game/state.py:**
- `GamePhase.PAUSED` enum exists (line 47)
- `pause_reason: str | None` field exists (line 78)
- `_previous_phase: GamePhase | None` field exists (line 79)
- `get_state()` includes PAUSED handling (lines 226-227)

**What's Missing:**
- No `pause_game()` or `resume_game()` methods
- No admin disconnect detection in websocket.py
- No PAUSED view in frontend
- Timer/playback not stopped on pause

### Implementation Details

#### 1. GameState.pause_game() Implementation

**IMPORTANT:** `pause_game()` must be **async** because it stops media playback.

```python
async def pause_game(self, reason: str) -> bool:
    """
    Pause the game (typically due to admin disconnect).

    Args:
        reason: Pause reason code (e.g., "admin_disconnected")

    Returns:
        True if successfully paused, False if already paused/ended
    """
    if self.phase == GamePhase.PAUSED:
        return False  # Already paused
    if self.phase == GamePhase.END:
        return False  # Can't pause ended game

    # Store current phase for resume
    self._previous_phase = self.phase
    self.pause_reason = reason

    # Stop timer if in PLAYING
    if self.phase == GamePhase.PLAYING:
        self.cancel_timer()
        # Stop media playback (must check for None)
        if self._media_player_service:
            await self._media_player_service.stop()

    # Transition to PAUSED
    self.phase = GamePhase.PAUSED
    _LOGGER.info("Game paused: %s", reason)

    return True

def resume_game(self) -> bool:
    """
    Resume game from PAUSED state.

    Returns:
        True if successfully resumed, False if not paused
    """
    if self.phase != GamePhase.PAUSED:
        return False
    if self._previous_phase is None:
        _LOGGER.error("Cannot resume: no previous phase stored")
        return False

    # Restore previous phase
    self.phase = self._previous_phase
    self.pause_reason = None

    _LOGGER.info("Game resumed to phase: %s", self.phase.value)

    # Note: Timer and song resume handled in Story 7.2
    return True
```

#### 2. WebSocket Admin Disconnect Detection

**IMPORTANT:** Extend the existing `_handle_disconnect()` pattern - do NOT create a completely separate handler. This reuses the existing grace period infrastructure.

Modify `_handle_disconnect()` in `server/websocket.py` (lines 426-466):

```python
async def _handle_disconnect(self, ws: web.WebSocketResponse) -> None:
    """Handle WebSocket disconnection with grace period."""
    game_state = self.hass.data.get(DOMAIN, {}).get("game")
    if not game_state:
        return

    # Find player by WebSocket
    player_name = None
    player = None
    for name, p in game_state.players.items():
        if p.ws == ws:
            player_name = name
            player = p
            player.connected = False
            break

    if not player_name:
        return

    _LOGGER.info("Player disconnected: %s (is_admin: %s)",
                 player_name, player.is_admin)

    # Broadcast disconnect state immediately
    await self.broadcast_state()

    # Admin disconnect: pause game after grace period
    # Regular player: remove after grace period (existing behavior)
    if player.is_admin:
        # Schedule pause after grace period (reuses existing pattern)
        async def pause_after_timeout() -> None:
            await asyncio.sleep(LOBBY_DISCONNECT_GRACE_PERIOD)
            # Check if admin still disconnected
            if player_name in game_state.players:
                admin = game_state.players[player_name]
                if not admin.connected:
                    # pause_game() is async and handles media stop internally
                    if await game_state.pause_game("admin_disconnected"):
                        await self.broadcast_state()
                        _LOGGER.info("Game paused due to admin disconnect")

        # Store task for cancellation on reconnect
        self._admin_disconnect_task = asyncio.create_task(pause_after_timeout())
    else:
        # Existing regular player removal logic (no changes needed)
        # Schedule removal after grace period
        async def remove_after_timeout() -> None:
            await asyncio.sleep(LOBBY_DISCONNECT_GRACE_PERIOD)
            if player_name in game_state.players:
                if not game_state.players[player_name].connected:
                    game_state.remove_player(player_name)
                    await self.broadcast_state()
                    _LOGGER.info("Player removed after timeout: %s", player_name)
            if player_name in self._pending_removals:
                del self._pending_removals[player_name]

        task = asyncio.create_task(remove_after_timeout())
        self._pending_removals[player_name] = task
```

**Key Changes from Existing Code:**
1. Added `is_admin` check to branch logic
2. Admin path calls `await game_state.pause_game()` (async) instead of `remove_player()`
3. Stores task in `_admin_disconnect_task` for cancellation
4. Regular player path UNCHANGED - preserves existing behavior

#### 3. Cancel Admin Timeout on Reconnect

Add logic to handle admin reconnecting before timeout:

```python
# In _handle_message(), when admin rejoins:
if success and is_admin:
    # Cancel pending admin disconnect timeout
    if hasattr(self, '_admin_disconnect_task'):
        task = self._admin_disconnect_task
        if task and not task.done():
            task.cancel()
            _LOGGER.info("Admin reconnected, cancelled pause timeout")
```

#### 4. Frontend PAUSED View (player.html)

Add after `reveal-view` section:

```html
<!-- Paused View -->
<div id="paused-view" class="view paused-view hidden">
    <div class="paused-overlay">
        <div class="paused-content">
            <div class="paused-icon">⏸️</div>
            <h2 class="paused-title">Game Paused</h2>
            <p class="paused-message">Waiting for admin...</p>
            <div class="paused-spinner"></div>
            <p class="paused-hint">The game will resume when the host reconnects</p>
        </div>
    </div>
</div>
```

#### 5. CSS Styles

```css
/* Paused View */
.paused-view {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: rgba(0, 0, 0, 0.7);
}

.paused-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.paused-content {
    text-align: center;
    padding: 40px;
    background: var(--card-bg, #1a1a2e);
    border-radius: 16px;
    max-width: 320px;
}

.paused-icon {
    font-size: 64px;
    margin-bottom: 16px;
}

.paused-title {
    font-size: 24px;
    margin-bottom: 8px;
    color: var(--text-primary, #fff);
}

.paused-message {
    font-size: 18px;
    color: var(--accent-color, #7c3aed);
    margin-bottom: 24px;
}

.paused-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-color, #333);
    border-top-color: var(--accent-color, #7c3aed);
    border-radius: 50%;
    margin: 0 auto 16px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.paused-hint {
    font-size: 14px;
    color: var(--text-secondary, #888);
}
```

#### 6. JavaScript Handler (player.js)

Add to `handleServerMessage()`:

```javascript
} else if (data.phase === 'PAUSED') {
    stopCountdown();
    hideAdminControlBar();
    showView('paused-view');

    // Update pause message if reason provided
    var pauseMsg = document.getElementById('paused-message');
    if (pauseMsg && data.pause_reason === 'admin_disconnected') {
        pauseMsg.textContent = 'Waiting for admin...';
    }
}
```

Also update `showView()` function to include `paused-view` in the view list:

```javascript
const pausedView = document.getElementById('paused-view');

function showView(viewId) {
    [loadingView, notFoundView, endedView, inProgressView, joinView,
     lobbyView, gameView, revealView, endView, pausedView].forEach(function(v) {
        if (v) {
            v.classList.add('hidden');
        }
    });
    // ...
}
```

### Architecture Compliance

- **State Machine:** Follows documented transition: `Any → PAUSED (admin disconnects)`
- **WebSocket:** Uses existing aiohttp handler pattern
- **Constants:** Uses existing `LOBBY_DISCONNECT_GRACE_PERIOD` (5 seconds)
- **Error Codes:** No new error codes needed (PAUSED is a phase, not error)
- **Naming:** snake_case for Python, camelCase for JS, kebab-case for CSS

### Race Condition Considerations

Per Epic 7 note: "Pay careful attention to race conditions during PAUSED state transitions"

**Potential Race Conditions:**

1. **Timer expiry during disconnect detection**
   - Timer callback should check if phase changed before transitioning
   - Already handled: `_timer_countdown()` checks `self.phase == GamePhase.PLAYING`

2. **Admin reconnect during pause transition**
   - Use task cancellation: `_admin_disconnect_task.cancel()`
   - Check `task.done()` before canceling

3. **Multiple players disconnecting simultaneously**
   - Only admin triggers pause; regular disconnects use separate removal task

### Anti-Patterns to Avoid

- Do NOT silently ignore admin disconnects
- Do NOT continue timer while paused
- Do NOT allow submissions during PAUSED phase
- Do NOT forget to broadcast state after pause
- Do NOT create new error codes (PAUSED is a phase)

### Testing Considerations

1. **Manual Test: Admin disconnect during PLAYING**
   - Start game, play a round
   - Close admin's browser tab
   - Verify: Music stops, timer stops, all players see "Waiting for admin..."

2. **Manual Test: Admin quick reconnect**
   - Start game
   - Close admin's browser tab
   - Quickly reconnect within 5 seconds
   - Verify: Game continues without pause

3. **Manual Test: Admin disconnect during REVEAL**
   - Wait for reveal phase
   - Close admin's browser tab
   - Verify: Game pauses, players see pause screen

4. **Manual Test: Admin disconnect during LOBBY**
   - Create game, add some players
   - Close admin's browser tab
   - Verify: Lobby pauses, waiting message shown

### Project Structure Notes

Files to modify:
- `custom_components/beatify/game/state.py` - Add pause_game(), resume_game()
- `custom_components/beatify/server/websocket.py` - Admin disconnect handling
- `custom_components/beatify/www/player.html` - Add paused-view section
- `custom_components/beatify/www/css/styles.css` - Paused view styles
- `custom_components/beatify/www/js/player.js` - Handle PAUSED phase

No new files needed.

### References

- [Source: architecture.md#Game State Machine] - PAUSED state definition
- [Source: epics.md#Story 7.1] - Acceptance criteria and implementation note
- [Source: project-context.md#State Machine] - Valid transitions
- [Source: game/state.py:40-48] - GamePhase enum with PAUSED
- [Source: game/state.py:78-79] - pause_reason and _previous_phase fields
- [Source: server/websocket.py:426-466] - _handle_disconnect implementation
- [Source: const.py:12] - LOBBY_DISCONNECT_GRACE_PERIOD = 5

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

