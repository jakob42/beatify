# Story 7.3: Player Auto-Reconnect

Status: done

## Story

As a **player who lost connection**,
I want **to automatically reconnect and resume playing**,
so that **I don't lose my score or miss rounds**.

## Acceptance Criteria

1. **AC1:** Given player's WebSocket connection drops, When connection is lost, Then client automatically attempts reconnection every 2 seconds AND player sees "Reconnecting..." indicator

2. **AC2:** Given player reconnects within 60 seconds, When connection is restored, Then player's session is recovered (score, streak preserved) AND player rejoins current game state (LOBBY/PLAYING/REVEAL)

3. **AC3:** Given player reconnects during PLAYING phase, When session is restored, Then player sees current round state AND can submit guess if timer hasn't expired AND if they already submitted, sees "Already submitted" state

4. **AC4:** Given player reconnects after 60 seconds, When grace period has expired, Then player's session has ended AND player must re-enter name to rejoin as new player AND previous score is lost

5. **AC5:** Given player is reconnecting, When reconnection fails repeatedly (5 attempts), Then player sees "Connection lost. Check your WiFi and refresh."

## Tasks / Subtasks

- [ ] **Task 1: Implement reconnection WebSocket message** (AC: #2, #3)
  - [ ] 1.1 Add `reconnect` message type to websocket handler
  - [ ] 1.2 Check if player session exists with matching name
  - [ ] 1.3 Verify session is within 60-second grace period
  - [ ] 1.4 Restore WebSocket reference on existing PlayerSession
  - [ ] 1.5 Mark player as connected again
  - [ ] 1.6 Cancel pending removal task if exists

- [ ] **Task 2: Enhance client WebSocket reconnection logic** (AC: #1)
  - [ ] 2.1 Already has exponential backoff (1s, 2s, 4s...)
  - [ ] 2.2 Change to fixed 2-second intervals per AC
  - [ ] 2.3 Add visual "Reconnecting..." indicator
  - [ ] 2.4 Store player name in localStorage for reconnect

- [ ] **Task 3: Send reconnect message instead of join** (AC: #2)
  - [ ] 3.1 On WebSocket reconnect, check if we have stored name
  - [ ] 3.2 Send `type: "reconnect"` with stored name
  - [ ] 3.3 Handle success: restore UI state
  - [ ] 3.4 Handle failure (session expired): show join form

- [ ] **Task 4: Handle session restoration on server** (AC: #2, #3)
  - [ ] 4.1 On reconnect, find player by name
  - [ ] 4.2 Check if session still valid (not removed)
  - [ ] 4.3 Update ws reference, set connected = True
  - [ ] 4.4 Send current game state to reconnected player
  - [ ] 4.5 Broadcast updated player list to others

- [ ] **Task 5: Handle expired session gracefully** (AC: #4)
  - [ ] 5.1 If player not found on reconnect, return error
  - [ ] 5.2 Clear stored name on client
  - [ ] 5.3 Redirect to join view

- [ ] **Task 6: Implement max retry limit** (AC: #5)
  - [ ] 6.1 Track reconnection attempts (already exists)
  - [ ] 6.2 After 5 failures, stop retrying
  - [ ] 6.3 Show "Connection lost" message with refresh hint

- [ ] **Task 7: Add reconnecting indicator UI** (AC: #1)
  - [ ] 7.1 Add reconnecting overlay to player.html
  - [ ] 7.2 Show spinner and "Reconnecting..." text
  - [ ] 7.3 Show/hide based on connection state

- [ ] **Task 8: Verify no regressions**
  - [ ] 8.1 Run `ruff check custom_components/beatify/`
  - [ ] 8.2 Test normal join flow still works
  - [ ] 8.3 Test reconnect within grace period
  - [ ] 8.4 Test reconnect after grace period expired

## Dev Notes

### Current State Analysis

The codebase already has **significant reconnection infrastructure**:

**player.js (lines 1466-1530):**
- `reconnectAttempts` counter exists
- Exponential backoff implemented (1s, 2s, 4s, 8s, 16s, max 30s)
- `localStorage` stores player name for reconnection
- Max 5 reconnection attempts before giving up

**websocket.py (lines 426-479):**
- `_handle_disconnect()` with grace period
- `_pending_removals` dict tracks scheduled removals
- `cancel_pending_removal()` exists but unused
- Players marked `connected = False` on disconnect

**const.py:**
- `RECONNECT_TIMEOUT = 60` seconds (grace period)
- `LOBBY_DISCONNECT_GRACE_PERIOD = 5` seconds (removal delay)

**What's Missing:**
- No `reconnect` message type (only `join`)
- No reconnecting indicator UI
- Exponential backoff should be fixed 2s interval
- No differentiation between join and reconnect on client

### Implementation Details

#### 1. Add Reconnect Message Handler

In `server/websocket.py`, add to `_handle_message()`:

```python
elif msg_type == "reconnect":
    name = data.get("name", "").strip()

    if not name:
        await ws.send_json({
            "type": "error",
            "code": "NAME_INVALID",
            "message": "No name provided for reconnection",
        })
        return

    # Check if player session exists
    if name not in game_state.players:
        await ws.send_json({
            "type": "error",
            "code": "SESSION_EXPIRED",
            "message": "Session expired. Please rejoin with your name.",
        })
        return

    player = game_state.players[name]

    # Cancel any pending removal
    self.cancel_pending_removal(name)

    # Restore connection
    player.ws = ws
    player.connected = True

    _LOGGER.info("Player reconnected: %s", name)

    # Send current state
    state_msg = {"type": "state", **game_state.get_state()}
    await ws.send_json(state_msg)

    # Broadcast updated state to all (connected status changed)
    await self.broadcast_state()
```

#### 2. Add SESSION_EXPIRED Error Code

In `const.py`:

```python
ERR_SESSION_EXPIRED = "SESSION_EXPIRED"
```

#### 3. Client Reconnect Logic Enhancement

In `player.js`, modify WebSocket reconnection:

```javascript
// Change reconnection strategy to fixed 2-second intervals
const RECONNECT_INTERVAL_MS = 2000;
const MAX_RECONNECT_ATTEMPTS = 5;

function getReconnectDelay() {
    // Fixed 2-second intervals per FR58 spec
    return RECONNECT_INTERVAL_MS;
}

// Show/hide reconnecting indicator
function showReconnectingIndicator() {
    var indicator = document.getElementById('reconnecting-indicator');
    if (indicator) {
        indicator.classList.remove('hidden');
    }
}

function hideReconnectingIndicator() {
    var indicator = document.getElementById('reconnecting-indicator');
    if (indicator) {
        indicator.classList.add('hidden');
    }
}

// Enhanced WebSocket connection
function connectWebSocket(name, isReconnect) {
    playerName = name;
    isReconnect = isReconnect || false;

    // Store name for reconnection
    try {
        localStorage.setItem(STORAGE_KEY_NAME, name);
    } catch (e) {
        // Ignore
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = wsProtocol + '//' + window.location.host + '/beatify/ws';

    ws = new WebSocket(wsUrl);

    ws.onopen = function() {
        reconnectAttempts = 0;
        hideReconnectingIndicator();

        if (isReconnect) {
            // Send reconnect message
            ws.send(JSON.stringify({ type: 'reconnect', name: name }));
        } else {
            // Normal join
            var joinMsg = { type: 'join', name: name };
            if (isAdmin) {
                joinMsg.is_admin = true;
            }
            ws.send(JSON.stringify(joinMsg));
        }
    };

    ws.onclose = function() {
        if (playerName && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            reconnectAttempts++;
            showReconnectingIndicator();

            var delay = getReconnectDelay();
            console.log('Reconnecting in ' + delay + 'ms (attempt ' +
                        reconnectAttempts + '/' + MAX_RECONNECT_ATTEMPTS + ')');

            setTimeout(function() {
                connectWebSocket(playerName, true);  // true = reconnect
            }, delay);
        } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            // Show connection lost message
            showConnectionLostView();
        }
    };

    // ... rest of handlers
}
```

#### 4. Handle SESSION_EXPIRED Error

```javascript
// In handleServerMessage():
if (data.type === 'error') {
    if (data.code === 'SESSION_EXPIRED') {
        // Session expired, need to rejoin as new player
        hideReconnectingIndicator();
        clearStoredSession();
        showView('join-view');
        showJoinError('Session expired. Please enter your name to rejoin.');
        return;
    }
    // ... other error handling
}

function clearStoredSession() {
    try {
        localStorage.removeItem(STORAGE_KEY_NAME);
        sessionStorage.removeItem('beatify_admin_name');
        sessionStorage.removeItem('beatify_is_admin');
    } catch (e) {
        // Ignore
    }
    playerName = null;
    isAdmin = false;
}
```

#### 5. Connection Lost View

Add to player.html:

```html
<!-- Reconnecting Indicator -->
<div id="reconnecting-indicator" class="reconnecting-indicator hidden">
    <div class="reconnecting-content">
        <div class="reconnecting-spinner"></div>
        <span>Reconnecting...</span>
    </div>
</div>

<!-- Connection Lost View -->
<div id="connection-lost-view" class="view connection-lost-view hidden">
    <div class="connection-lost-card">
        <div class="connection-lost-icon">📶</div>
        <h2>Connection Lost</h2>
        <p>Unable to reconnect to the game.</p>
        <p class="hint">Check your WiFi and refresh the page.</p>
        <button id="refresh-page-btn" class="btn btn-primary" onclick="location.reload()">
            Refresh Page
        </button>
    </div>
</div>
```

#### 6. CSS Styles

```css
/* Reconnecting Indicator */
.reconnecting-indicator {
    position: fixed;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--warning-bg, #fbbf24);
    color: var(--warning-text, #1a1a1a);
    padding: 8px 16px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.reconnecting-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

/* Connection Lost View */
.connection-lost-view {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}

.connection-lost-card {
    text-align: center;
    padding: 40px;
    background: var(--card-bg, #1a1a2e);
    border-radius: 16px;
    max-width: 320px;
}

.connection-lost-icon {
    font-size: 64px;
    margin-bottom: 16px;
    opacity: 0.5;
}

.connection-lost-card h2 {
    margin-bottom: 16px;
}

.connection-lost-card .hint {
    color: var(--text-secondary, #888);
    margin-bottom: 24px;
}
```

#### 7. Show Connection Lost View

```javascript
function showConnectionLostView() {
    hideReconnectingIndicator();
    showView('connection-lost-view');
}
```

### Architecture Compliance

- **Constants:** Uses existing `RECONNECT_TIMEOUT` (60s) from const.py
- **WebSocket:** Follows existing message handling patterns
- **Error Codes:** Adds `SESSION_EXPIRED` to const.py
- **Grace Period:** Leverages existing `_pending_removals` mechanism

### Existing Code to Leverage

The current implementation already:
1. Stores `playerName` in `localStorage` (line 1488)
2. Tracks `reconnectAttempts` (line 1468)
3. Has max reconnect attempts = 5 (line 1518)
4. Cancels pending removals via `cancel_pending_removal()` (lines 468-479)

### Anti-Patterns to Avoid

- Do NOT lose player score on reconnect
- Do NOT allow reconnect after 60 seconds (use join instead)
- Do NOT spam reconnection attempts (use 2s interval)
- Do NOT show stale UI state on reconnect

### Testing Considerations

1. **Reconnect within grace period** - Score preserved, rejoins current phase
2. **Reconnect after 60 seconds** - Session expired, must rejoin
3. **Reconnect during PLAYING** - Can submit if timer not expired
4. **Reconnect during REVEAL** - Sees reveal results
5. **5 failed attempts** - Shows connection lost view
6. **Admin reconnect** - Should use Story 7-2 flow instead

### Race Condition Considerations

- Reconnect may race with pending removal task
- Solution: Always call `cancel_pending_removal()` on reconnect
- Check `player.connected` state when processing reconnect

### References

- [Source: epics.md#Story 7.3] - Acceptance criteria
- [Source: const.py:8] - RECONNECT_TIMEOUT = 60
- [Source: player.js:1466-1530] - Existing reconnect logic
- [Source: websocket.py:468-479] - cancel_pending_removal()
- [Source: project-context.md#Player Session Management] - 60-second grace period

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

