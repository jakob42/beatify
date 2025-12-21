# Story 7.2: Admin Reconnection

Status: done

## Story

As a **host who got disconnected**,
I want **to rejoin and resume control of the game**,
so that **the party can continue without starting over**.

## Acceptance Criteria

1. **AC1:** Given game is paused due to admin disconnect, When admin navigates to admin page (`/beatify/admin`), Then admin page shows "Active game paused - Rejoin?" option AND displays current game state (round number, player count)

2. **AC2:** Given admin clicks "Rejoin", When rejoin flow starts, Then admin is prompted to enter their name AND must enter the same name they used before

3. **AC3:** Given admin enters their original name, When name matches the disconnected admin, Then admin reclaims admin status AND admin rejoins as player with admin controls AND game transitions from PAUSED back to previous state

4. **AC4:** Given admin enters a different name, When name doesn't match, Then error displays: "Enter your original name to reclaim admin" AND admin can retry

5. **AC5:** Given admin successfully rejoins, When game resumes, Then all players see "Admin reconnected - Game resuming!" AND timer resumes if in PLAYING phase AND audio restarts if song was playing

## Tasks / Subtasks

- [ ] **Task 1: Detect paused game on admin page load** (AC: #1)
  - [ ] 1.1 Modify `/beatify/api/status` endpoint to include pause info
  - [ ] 1.2 Return `is_paused`, `pause_reason`, `admin_name` in status response
  - [ ] 1.3 Return current game state (round, player_count) for display

- [ ] **Task 2: Add "Rejoin Paused Game" UI to admin.html** (AC: #1, #2)
  - [ ] 2.1 Add `paused-game-view` section to admin.html
  - [ ] 2.2 Display game status: "Game Paused - Waiting for you!"
  - [ ] 2.3 Show current round and player count
  - [ ] 2.4 Add name input field for admin name verification
  - [ ] 2.5 Add "Rejoin Game" button

- [ ] **Task 3: Implement admin name verification** (AC: #2, #3, #4)
  - [ ] 3.1 Store original admin name in GameState when admin disconnects
  - [ ] 3.2 Add `verify_admin_rejoin(name: str)` method to GameState
  - [ ] 3.3 Compare entered name with stored admin name (case-insensitive)
  - [ ] 3.4 Return error if names don't match

- [ ] **Task 4: Implement rejoin WebSocket flow** (AC: #3)
  - [ ] 4.1 Add `rejoin` message type to websocket handler
  - [ ] 4.2 Verify admin name matches disconnected admin
  - [ ] 4.3 Restore admin's PlayerSession with same score/stats
  - [ ] 4.4 Update WebSocket reference on PlayerSession
  - [ ] 4.5 Call `game_state.resume_game()` to exit PAUSED state

- [ ] **Task 5: Resume game state properly** (AC: #5)
  - [ ] 5.1 In `resume_game()`, restore `_previous_phase`
  - [ ] 5.2 If resuming to PLAYING, restart timer with remaining time
  - [ ] 5.3 If resuming to PLAYING, restart song playback (optional)
  - [ ] 5.4 Broadcast "game_resumed" message to all players

- [ ] **Task 6: Show "Game Resuming" notification to players** (AC: #5)
  - [ ] 6.1 Send `type: "game_resumed"` message on resume
  - [ ] 6.2 Handle in player.js - show toast/notification
  - [ ] 6.3 Transition from paused-view back to appropriate view

- [ ] **Task 7: Update admin.js for rejoin flow** (AC: #1-#5)
  - [ ] 7.1 Check for paused game on page load
  - [ ] 7.2 Show paused-game-view if game is paused
  - [ ] 7.3 Handle rejoin form submission
  - [ ] 7.4 Connect WebSocket with rejoin message type
  - [ ] 7.5 Redirect to player page on successful rejoin

- [ ] **Task 8: Verify no regressions**
  - [ ] 8.1 Run `ruff check custom_components/beatify/`
  - [ ] 8.2 Test normal admin join flow still works
  - [ ] 8.3 Test rejoin with correct name
  - [ ] 8.4 Test rejoin with wrong name (should fail)

## Dev Notes

### Pre-flight Check (REQUIRED)

**BEFORE starting implementation, verify Story 7-1 is complete:**

- [ ] `game/state.py` has `async def pause_game(reason: str)` method
- [ ] `game/state.py` has `def resume_game()` method
- [ ] `_previous_phase` is set by `pause_game()`
- [ ] `pause_game()` stops media playback internally
- [ ] PAUSED state broadcasts to all players
- [ ] `paused-view` exists in player.html

**If any check fails, implement Story 7-1 first.**

### Dependencies

**Requires Story 7-1 completed:** This story depends on the PAUSED state implementation from Story 7-1.

### Implementation Details

#### 1. Store Admin Name on Disconnect

In `game/state.py`, add field to track disconnected admin:

```python
class GameState:
    def __init__(self, ...):
        # ... existing fields ...
        self.disconnected_admin_name: str | None = None  # Epic 7

    async def pause_game(self, reason: str) -> bool:
        # ... existing pause logic from Story 7-1 ...

        # ADD: Store admin name for rejoin verification (Story 7-2)
        if reason == "admin_disconnected":
            for player in self.players.values():
                if player.is_admin:
                    self.disconnected_admin_name = player.name
                    break

        return True
```

**Note:** `pause_game()` is async (from Story 7-1) because it stops media playback.

#### 2. Admin Rejoin Verification

```python
def verify_admin_rejoin(self, name: str) -> tuple[bool, str | None]:
    """
    Verify admin can rejoin with given name.

    Args:
        name: Name provided by reconnecting admin

    Returns:
        (success, error_code) - error_code is None on success
    """
    if self.phase != GamePhase.PAUSED:
        return False, "GAME_NOT_PAUSED"

    if not self.disconnected_admin_name:
        return False, "NO_ADMIN_TO_REJOIN"

    # Case-insensitive comparison
    if name.lower().strip() != self.disconnected_admin_name.lower():
        return False, "ADMIN_NAME_MISMATCH"

    return True, None
```

#### 3. Resume Game with Timer Restoration

```python
def resume_game(self, hass: HomeAssistant | None = None) -> bool:
    """
    Resume game from PAUSED state.

    Args:
        hass: Home Assistant instance for timer/media restart

    Returns:
        True if successfully resumed
    """
    if self.phase != GamePhase.PAUSED:
        return False
    if self._previous_phase is None:
        return False

    previous = self._previous_phase
    self.phase = previous
    self.pause_reason = None
    self.disconnected_admin_name = None

    _LOGGER.info("Game resumed to phase: %s", previous.value)

    # Restart timer if resuming to PLAYING
    if previous == GamePhase.PLAYING and self.deadline:
        # Calculate remaining time
        now_ms = int(self._now() * 1000)
        remaining_ms = self.deadline - now_ms

        if remaining_ms > 0:
            # Restart timer with remaining time
            remaining_seconds = remaining_ms / 1000.0
            self._timer_task = asyncio.create_task(
                self._timer_countdown(remaining_seconds)
            )
            _LOGGER.info("Timer restarted with %.1fs remaining", remaining_seconds)
        else:
            # Timer would have expired, trigger reveal
            _LOGGER.info("Timer expired during pause, advancing to reveal")
            # Let caller handle this case

    return True
```

#### 4. WebSocket Rejoin Handler

Add to `_handle_message()` in `server/websocket.py`:

```python
elif msg_type == "rejoin":
    name = data.get("name", "").strip()

    # Verify admin can rejoin
    success, error = game_state.verify_admin_rejoin(name)
    if not success:
        error_messages = {
            "GAME_NOT_PAUSED": "Game is not paused",
            "NO_ADMIN_TO_REJOIN": "No admin session to rejoin",
            "ADMIN_NAME_MISMATCH": "Enter your original name to reclaim admin",
        }
        await ws.send_json({
            "type": "error",
            "code": error,
            "message": error_messages.get(error, "Rejoin failed"),
        })
        return

    # Restore admin session
    if name in game_state.players:
        admin = game_state.players[name]
        admin.ws = ws
        admin.connected = True
    else:
        # Session was removed, recreate with admin status
        game_state.add_player(name, ws)
        game_state.set_admin(name)

    # Resume game
    game_state.resume_game()

    # Restart media if was in PLAYING
    if game_state.phase == GamePhase.PLAYING:
        if game_state._media_player_service and game_state.current_song:
            # Optionally restart song playback
            # await game_state._media_player_service.play_song(...)
            pass

    # Broadcast resumed state
    await self.broadcast({"type": "game_resumed"})
    await self.broadcast_state()

    _LOGGER.info("Admin %s rejoined, game resumed", name)
```

#### 5. Admin Page Status Check

Modify `/beatify/api/status` response in `server/views.py`:

```python
async def get(self, request: web.Request) -> web.Response:
    game_state = self.hass.data.get(DOMAIN, {}).get("game")

    if not game_state or not game_state.game_id:
        return self.json({"exists": False})

    response = {
        "exists": True,
        "phase": game_state.phase.value,
        "player_count": len(game_state.players),
        "round": game_state.round,
        "total_rounds": game_state.total_rounds,
    }

    # Add pause info for admin page
    if game_state.phase == GamePhase.PAUSED:
        response["is_paused"] = True
        response["pause_reason"] = game_state.pause_reason
        response["admin_name"] = game_state.disconnected_admin_name

    return self.json(response)
```

#### 6. Admin Page UI (admin.html)

Add paused game view section:

```html
<!-- Paused Game Rejoin View -->
<div id="paused-game-view" class="view hidden">
    <div class="paused-game-card">
        <div class="paused-game-icon">⏸️</div>
        <h2>Game Paused</h2>
        <p class="paused-game-status">Waiting for you to rejoin!</p>

        <div class="game-info">
            <div class="info-item">
                <span class="info-label">Round</span>
                <span id="paused-round" class="info-value">-</span>
            </div>
            <div class="info-item">
                <span class="info-label">Players</span>
                <span id="paused-players" class="info-value">-</span>
            </div>
        </div>

        <form id="rejoin-form" class="rejoin-form">
            <label for="rejoin-name">Enter your name to rejoin:</label>
            <input type="text" id="rejoin-name" placeholder="Your name"
                   maxlength="20" autocomplete="off" required>
            <p id="rejoin-error" class="error-message hidden"></p>
            <button type="submit" id="rejoin-btn" class="btn btn-primary">
                Rejoin Game
            </button>
        </form>
    </div>
</div>
```

#### 7. Admin.js Rejoin Logic

```javascript
async function checkForPausedGame() {
    const response = await fetch('/beatify/api/status');
    const data = await response.json();

    if (data.exists && data.is_paused) {
        // Show paused game view
        showView('paused-game-view');

        document.getElementById('paused-round').textContent =
            data.round + '/' + data.total_rounds;
        document.getElementById('paused-players').textContent =
            data.player_count;

        // Pre-fill name if known
        if (data.admin_name) {
            document.getElementById('rejoin-name').value = data.admin_name;
        }

        return true;
    }
    return false;
}

function setupRejoinForm() {
    const form = document.getElementById('rejoin-form');
    form?.addEventListener('submit', async function(e) {
        e.preventDefault();

        const name = document.getElementById('rejoin-name').value.trim();
        const btn = document.getElementById('rejoin-btn');
        const errorEl = document.getElementById('rejoin-error');

        btn.disabled = true;
        btn.textContent = 'Rejoining...';
        errorEl.classList.add('hidden');

        // Connect WebSocket and send rejoin
        connectForRejoin(name);
    });
}

function connectForRejoin(name) {
    const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(wsProtocol + '//' + location.host + '/beatify/ws');

    ws.onopen = function() {
        ws.send(JSON.stringify({ type: 'rejoin', name: name }));
    };

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === 'error') {
            showRejoinError(data.message);
            return;
        }

        if (data.type === 'state' || data.type === 'game_resumed') {
            // Success! Store admin info and redirect to player page
            sessionStorage.setItem('beatify_admin_name', name);
            sessionStorage.setItem('beatify_is_admin', 'true');
            window.location.href = '/beatify/play?game=' + data.game_id;
        }
    };

    ws.onerror = function() {
        showRejoinError('Connection failed. Please try again.');
    };
}

function showRejoinError(message) {
    const errorEl = document.getElementById('rejoin-error');
    const btn = document.getElementById('rejoin-btn');

    if (errorEl) {
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
    }
    if (btn) {
        btn.disabled = false;
        btn.textContent = 'Rejoin Game';
    }
}
```

#### 8. Player.js Game Resumed Handler

```javascript
} else if (data.type === 'game_resumed') {
    // Show brief notification
    showToast('Admin reconnected - Game resuming!');

    // State update will follow immediately, triggering view change
}

function showToast(message) {
    var toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';
        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.classList.add('is-visible');

    setTimeout(function() {
        toast.classList.remove('is-visible');
    }, 3000);
}
```

### Architecture Compliance

- **WebSocket:** New `rejoin` message type follows existing patterns
- **State Machine:** PAUSED → previous_phase transition
- **Admin Page:** Uses existing status endpoint pattern
- **Player Page:** Toast notification for resume event

### Anti-Patterns to Avoid

- Do NOT allow rejoin with different name
- Do NOT lose player scores on rejoin
- Do NOT skip name verification
- Do NOT forget to restart timer if resuming to PLAYING

### Testing Considerations

1. **Rejoin with correct name** - Should work, game resumes
2. **Rejoin with wrong name** - Should show error
3. **Rejoin with different case** - Should work (case-insensitive)
4. **Resume to PLAYING** - Timer should continue from where it left off
5. **Resume to REVEAL** - Should show reveal view
6. **Resume to LOBBY** - Should show lobby view

### References

- [Source: epics.md#Story 7.2] - Full acceptance criteria
- [Source: game/state.py:78-79] - _previous_phase field
- [Source: architecture.md#State Machine] - PAUSED state handling
- [Source: server/websocket.py] - Message handler patterns

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

