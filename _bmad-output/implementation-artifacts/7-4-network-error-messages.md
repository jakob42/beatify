# Story 7.4: Network Error Messages

Status: done

## Story

As a **player joining the game**,
I want **clear error messages if something goes wrong**,
so that **I know what to do to fix the problem**.

## Acceptance Criteria

1. **AC1:** Given player scans QR code on wrong WiFi network, When device cannot reach Home Assistant server, Then player sees "Can't reach game server. Are you on the right WiFi?"

2. **AC2:** Given player's connection times out, When fetch or WebSocket connection fails, Then player sees "Connection timed out. Check your WiFi and try again."

3. **AC3:** Given player tries to join with invalid game ID, When game is not found, Then player sees "Game not found. Scan the QR code again." (already exists)

4. **AC4:** Given player tries to join ended game, When game phase is END, Then player sees "This game has ended." (already exists)

5. **AC5:** Given any network error occurs, When error is displayed, Then a "Try Again" button is visible AND tapping it retries the connection

## Tasks / Subtasks

- [ ] **Task 1: Add timeout to initial game status check** (AC: #1, #2)
  - [ ] 1.1 Add 10-second timeout to `checkGameStatus()` fetch call
  - [ ] 1.2 Catch timeout errors and show appropriate message
  - [ ] 1.3 Catch network errors (TypeError) and show WiFi message

- [ ] **Task 2: Enhance not-found-view with better messaging** (AC: #1)
  - [ ] 2.1 Update `not-found-view` to show network-specific errors
  - [ ] 2.2 Add subtext with WiFi troubleshooting hint
  - [ ] 2.3 Show "Try Again" button prominently

- [ ] **Task 3: Add network error view** (AC: #1, #2)
  - [ ] 3.1 Create `network-error-view` section in player.html
  - [ ] 3.2 Display error icon and message
  - [ ] 3.3 Add WiFi troubleshooting tips
  - [ ] 3.4 Add "Try Again" button

- [ ] **Task 4: Handle WebSocket connection failures** (AC: #2)
  - [ ] 4.1 Detect initial WebSocket connection failure
  - [ ] 4.2 Show network error view instead of silent failure
  - [ ] 4.3 Differentiate from reconnection failures

- [ ] **Task 5: Improve existing error views** (AC: #3, #4, #5)
  - [ ] 5.1 Ensure "Try Again" button exists on all error views
  - [ ] 5.2 Verify `not-found-view` has retry functionality
  - [ ] 5.3 Verify `ended-view` messaging is clear

- [ ] **Task 6: Add CSS for error views** (AC: #1-#5)
  - [ ] 6.1 Style network error view consistently
  - [ ] 6.2 Add WiFi icon for network errors
  - [ ] 6.3 Ensure buttons are accessible and visible

- [ ] **Task 7: Verify no regressions**
  - [ ] 7.1 Test normal join flow still works
  - [ ] 7.2 Test invalid game ID shows correct error
  - [ ] 7.3 Test ended game shows correct error
  - [ ] 7.4 Simulate network failure (disable WiFi)

## Dev Notes

### Current State Analysis

The codebase already handles some error cases:

**player.js (lines 56-98):**
- `checkGameStatus()` fetches `/beatify/api/game-status`
- Shows `not-found-view` on missing game or format error
- Shows `ended-view` for phase === 'END'
- Shows `in-progress-view` for REVEAL/PAUSED (can't join)

**player.html:**
- `not-found-view` exists with basic message
- `ended-view` exists with "This game has ended"
- `refresh-btn` and `retry-btn` exist for retry

**What's Missing:**
- No timeout on fetch calls
- No specific network error handling
- No WiFi troubleshooting hints
- Error messages could be clearer

### Implementation Details

#### 1. Add Fetch Timeout

```javascript
async function checkGameStatus() {
    if (!gameId) {
        showView('not-found-view');
        return;
    }

    if (!isValidGameIdFormat(gameId)) {
        showView('not-found-view');
        return;
    }

    try {
        // Add 10-second timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        const response = await fetch(
            `/beatify/api/game-status?game=${encodeURIComponent(gameId)}`,
            { signal: controller.signal }
        );
        clearTimeout(timeoutId);

        const data = await response.json();

        if (!data.exists) {
            showErrorView('not-found', 'Game not found',
                         'Scan the QR code again to get the correct link.');
            return;
        }

        if (data.phase === 'END') {
            showView('ended-view');
            return;
        }

        if (data.can_join) {
            showView('join-view');
        } else {
            showView('in-progress-view');
        }

    } catch (err) {
        console.error('Failed to check game status:', err);

        if (err.name === 'AbortError') {
            // Timeout
            showErrorView('network', 'Connection timed out',
                         'Check your WiFi connection and try again.');
        } else if (err instanceof TypeError) {
            // Network error (fetch failed)
            showErrorView('network', "Can't reach game server",
                         'Are you connected to the right WiFi network?');
        } else {
            // Other errors
            showErrorView('not-found', 'Something went wrong',
                         'Please try again.');
        }
    }
}
```

#### 2. Dynamic Error Display (ENHANCE existing view - DO NOT replace)

**IMPORTANT:** Do NOT create a new `error-view` that replaces `not-found-view`. Instead, enhance the EXISTING `not-found-view` to support dynamic messages. This prevents regression and maintains existing code paths.

```javascript
/**
 * Show error with dynamic message in existing not-found-view
 * @param {string} type - Error type ('network' or 'not-found')
 * @param {string} title - Error title
 * @param {string} message - Error description
 */
function showDynamicError(type, title, message) {
    // Update existing not-found-view elements dynamically
    var iconEl = document.getElementById('error-icon');
    var titleEl = document.getElementById('error-title');
    var msgEl = document.getElementById('error-message');

    if (iconEl) {
        iconEl.textContent = type === 'network' ? '📶' : '🔍';
    }
    if (titleEl) {
        titleEl.textContent = title;
    }
    if (msgEl) {
        msgEl.textContent = message;
    }

    // Use existing not-found-view, NOT a new view
    showView('not-found-view');
}
```

#### 3. Enhance Existing not-found-view (player.html)

**DO NOT replace not-found-view.** Instead, add IDs to existing elements for dynamic updates:

```html
<!-- Enhanced not-found-view (add IDs for dynamic content) -->
<div id="not-found-view" class="view hidden">
    <div class="error-card">
        <div id="error-icon" class="error-icon">🔍</div>
        <h2 id="error-title" class="error-title">Game not found</h2>
        <p id="error-message" class="error-message">
            Scan the QR code again to get the correct link.
        </p>

        <div class="error-tips">
            <p class="tips-title">Troubleshooting:</p>
            <ul>
                <li>Make sure you're on the same WiFi as the game host</li>
                <li>Try scanning the QR code again</li>
                <li>Ask the host if the game is still active</li>
            </ul>
        </div>

        <button id="retry-btn" class="btn btn-primary">
            Try Again
        </button>
    </div>
</div>
```

**Key Changes from Existing:**
- Add `id="error-icon"` for dynamic icon updates
- Add `id="error-title"` for dynamic title updates
- Add `id="error-message"` for dynamic message updates
- Add troubleshooting tips section
- Keep existing `retry-btn` ID (already exists)

#### 4. No View Mapping Needed

Since we're enhancing the existing `not-found-view` rather than creating a new view, no mapping is needed. All existing `showView('not-found-view')` calls continue to work unchanged.

#### 5. WebSocket Connection Error Handling

```javascript
function connectWebSocket(name, isReconnect) {
    // ... existing setup ...

    ws.onerror = function(err) {
        console.error('WebSocket error:', err);

        // Only show error on initial connection (not reconnect)
        if (!isReconnect && reconnectAttempts === 0) {
            showErrorView('network', "Can't connect to game",
                         'Check your WiFi connection and try again.');
        }
    };

    ws.onclose = function() {
        // ... existing reconnect logic ...

        // If this was initial connection failure
        if (!isReconnect && reconnectAttempts === 0) {
            showErrorView('network', 'Connection failed',
                         'Unable to connect to the game server.');
        }
    };
}
```

#### 6. Retry Button Handler

```javascript
function setupErrorRetry() {
    var retryBtn = document.getElementById('error-retry-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', function() {
            showView('loading-view');
            checkGameStatus();
        });
    }
}

// Call in initAll()
```

#### 7. CSS Styles

```css
/* Error View */
.error-view {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 20px;
}

.error-card {
    text-align: center;
    padding: 40px 30px;
    background: var(--card-bg, #1a1a2e);
    border-radius: 16px;
    max-width: 360px;
    width: 100%;
}

.error-icon {
    font-size: 64px;
    margin-bottom: 16px;
    opacity: 0.7;
}

.error-title {
    font-size: 24px;
    margin-bottom: 12px;
    color: var(--text-primary, #fff);
}

.error-message {
    font-size: 16px;
    color: var(--text-secondary, #aaa);
    margin-bottom: 24px;
}

.error-tips {
    text-align: left;
    background: var(--bg-secondary, #252540);
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 24px;
}

.error-tips .tips-title {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--text-primary, #fff);
}

.error-tips ul {
    margin: 0;
    padding-left: 20px;
    font-size: 14px;
    color: var(--text-secondary, #888);
}

.error-tips li {
    margin-bottom: 6px;
}

.error-tips li:last-child {
    margin-bottom: 0;
}

#error-retry-btn {
    width: 100%;
    padding: 14px;
    font-size: 16px;
}
```

### Error Message Matrix

| Condition | Title | Message |
|-----------|-------|---------|
| Fetch timeout (10s) | "Connection timed out" | "Check your WiFi connection and try again." |
| Fetch network error | "Can't reach game server" | "Are you connected to the right WiFi network?" |
| Game not found | "Game not found" | "Scan the QR code again to get the correct link." |
| Invalid game ID format | "Game not found" | "Scan the QR code again to get the correct link." |
| Game ended | "This game has ended" | (use existing ended-view) |
| WebSocket fails | "Can't connect to game" | "Check your WiFi connection and try again." |

### Architecture Compliance

- **Views:** Uses existing view pattern from player.js
- **Error Codes:** No new server error codes needed
- **Styling:** Follows existing card/button patterns

### Anti-Patterns to Avoid

- Do NOT show technical error messages (e.g., "TypeError: Failed to fetch")
- Do NOT leave users without a retry option
- Do NOT blame users (avoid "You did something wrong")
- Do NOT show different messages for same root cause

### Testing Considerations

1. **Disable WiFi** - Should show "Can't reach game server"
2. **Invalid game ID** - Should show "Game not found"
3. **Ended game** - Should show existing "Game ended" view
4. **Slow network** - Should timeout after 10s with clear message
5. **Retry button** - Should attempt connection again

### Accessibility Considerations

- Error messages use clear, non-technical language
- Retry button is prominent and keyboard-accessible
- Troubleshooting tips help users self-serve

### References

- [Source: epics.md#Story 7.4] - FR57, FR58 requirements
- [Source: player.js:56-98] - Existing checkGameStatus()
- [Source: player.html] - Existing error views
- [Source: project-context.md#Error Handling] - Error UX principles

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

