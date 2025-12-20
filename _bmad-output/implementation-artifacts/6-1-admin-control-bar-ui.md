# Story 6.1: Admin Control Bar UI

Status: done

## Story

As a **host playing the game**,
I want **to see admin controls on my player screen**,
so that **I can manage the game without switching devices**.

## Acceptance Criteria

1. **AC1:** Given host has joined as participant (via "Participate" button), When host views player screen during gameplay (PLAYING or REVEAL phase), Then an admin control bar is visible at bottom of screen (FR48) And control bar contains: Stop Song, Next Round, Volume Up, Volume Down, End Game buttons

2. **AC2:** Given regular player views their screen, When game is in progress, Then no admin controls are visible (FR47) And only the admin-flagged player sees controls

3. **AC3:** Given host views admin control bar, When controls are displayed, Then buttons are touch-friendly (44x44px minimum) And controls don't obstruct gameplay elements (year selector, timer)

4. **AC4:** Given game is in different phases, When controls are displayed, Then contextually irrelevant controls are disabled (e.g., "Stop Song" disabled during REVEAL, "Next Round" disabled during PLAYING)

## Tasks / Subtasks

- [x] **Task 1: Add admin control bar HTML to player.html** (AC: #1, #3)
  - [x] 1.1 Create `<div id="admin-control-bar" class="admin-control-bar hidden">` container
  - [x] 1.2 Add Stop Song button: `<button id="stop-song-btn" class="control-btn" type="button"><span class="control-icon">⏹️</span><span class="control-label">Stop</span></button>`
  - [x] 1.3 Add Volume Down button: `<button id="volume-down-btn" class="control-btn" type="button"><span class="control-icon">🔉</span></button>`
  - [x] 1.4 Add Volume Up button: `<button id="volume-up-btn" class="control-btn" type="button"><span class="control-icon">🔊</span></button>`
  - [x] 1.5 Add Next Round button: `<button id="next-round-admin-btn" class="control-btn" type="button"><span class="control-icon">⏭️</span><span class="control-label">Next</span></button>`
  - [x] 1.6 Add End Game button: `<button id="end-game-btn" class="control-btn control-btn--danger" type="button"><span class="control-icon">🛑</span><span class="control-label">End</span></button>`
  - [x] 1.7 Position control bar at bottom of player-container, OUTSIDE game-view div (visible across phases)

- [x] **Task 2: Style admin control bar** (AC: #1, #3)
  - [x] 2.1 Create `.admin-control-bar` styles: fixed/sticky bottom, full width, flex row, gap
  - [x] 2.2 Ensure minimum 44x44px touch targets for all buttons
  - [x] 2.3 Add safe-area padding for notched devices: `padding-bottom: env(safe-area-inset-bottom)`
  - [x] 2.4 Style `.control-btn` with consistent look
  - [x] 2.5 Style `.control-btn--danger` with red/warning color
  - [x] 2.6 Style `.control-btn.is-disabled` with greyed out appearance
  - [x] 2.7 Ensure control bar doesn't overlap year selector or submit button

- [x] **Task 3: Implement control bar visibility logic** (AC: #1, #2)
  - [x] 3.1 Add `showAdminControlBar()` function that checks `isAdmin` flag
  - [x] 3.2 Add `hideAdminControlBar()` function
  - [x] 3.3 Call `showAdminControlBar()` in handleServerMessage when phase is PLAYING or REVEAL AND player is admin
  - [x] 3.4 Call `hideAdminControlBar()` in handleServerMessage when phase is LOBBY or END
  - [x] 3.5 Ensure control bar hidden for non-admin players regardless of phase

- [x] **Task 4: Implement phase-based button state** (AC: #4)
  - [x] 4.1 Add `updateControlBarState(phase)` function
  - [x] 4.2 During PLAYING: Enable Stop Song, Volume controls; Disable Next Round
  - [x] 4.3 During REVEAL: Disable Stop Song; Enable Next Round, Volume controls
  - [x] 4.4 End Game always enabled (both phases)
  - [x] 4.5 Call `updateControlBarState()` whenever phase changes

- [x] **Task 5: Wire button event handlers** (AC: #1)
  - [x] 5.1 Add `setupAdminControlBar()` function called in initAll()
  - [x] 5.2 Wire Stop Song click → `handleStopSong()`
  - [x] 5.3 Wire Volume Up click → `handleVolumeUp()`
  - [x] 5.4 Wire Volume Down click → `handleVolumeDown()`
  - [x] 5.5 Wire Next Round click → `handleNextRoundFromBar()` (reuse existing logic)
  - [x] 5.6 Wire End Game click → `handleEndGame()`

- [x] **Task 6: Implement admin action stubs** (AC: #1)
  - [x] 6.1 `handleStopSong()`: Send `{type: "admin", action: "stop_song"}` via WebSocket
  - [x] 6.2 `handleVolumeUp()`: Send `{type: "admin", action: "set_volume", direction: "up"}` via WebSocket
  - [x] 6.3 `handleVolumeDown()`: Send `{type: "admin", action: "set_volume", direction: "down"}` via WebSocket
  - [x] 6.4 `handleEndGame()`: Show confirmation, then send `{type: "admin", action: "end_game"}` via WebSocket
  - [x] 6.5 Add debouncing (500ms) to prevent rapid repeated clicks

- [x] **Task 7: Handle server responses for admin actions**
  - [x] 7.1 Add handling for `{type: "error", code: "NOT_ADMIN"}` - hide control bar, show error
  - [x] 7.2 Add handling for `{type: "volume_changed", level: number}` - optional visual feedback
  - [x] 7.3 Add handling for `{type: "song_stopped"}` - disable Stop Song button, show "Stopped"

- [x] **Task 8: Verify no regressions**
  - [x] 8.1 Existing reveal-admin-controls still work (Next Round in reveal view)
  - [x] 8.2 Existing lobby admin controls still work (Start Game)
  - [x] 8.3 Non-admin players see NO admin controls anywhere
  - [x] 8.4 Run `ruff check` - no linting issues (N/A - UI only story, Python unchanged)
  - [x] 8.5 Manual test: join as admin, verify control bar visible during game

## Dev Notes

### Current Admin Control Locations

| Location | Current State | This Story |
|----------|---------------|------------|
| `#admin-controls` (lobby-view) | Start Game button, works | Keep as-is |
| `#reveal-admin-controls` (reveal-view) | Next Round button, works | Keep as-is, but control bar adds redundant Next Round |
| `#admin-control-bar` (NEW) | Does not exist | ADD: persistent control bar across PLAYING/REVEAL |

### Control Bar Placement Strategy

The control bar should be positioned OUTSIDE the phase-specific views so it persists across view transitions:

```html
<main class="player-container">
    <!-- ... existing views ... -->

    <!-- NEW: Admin Control Bar (visible across PLAYING/REVEAL for admin) -->
    <div id="admin-control-bar" class="admin-control-bar hidden">
        <button id="stop-song-btn" class="control-btn" type="button">
            <span class="control-icon">⏹️</span>
            <span class="control-label">Stop</span>
        </button>
        <button id="volume-down-btn" class="control-btn" type="button">
            <span class="control-icon">🔉</span>
        </button>
        <button id="volume-up-btn" class="control-btn" type="button">
            <span class="control-icon">🔊</span>
        </button>
        <button id="next-round-admin-btn" class="control-btn" type="button">
            <span class="control-icon">⏭️</span>
            <span class="control-label">Next</span>
        </button>
        <button id="end-game-btn" class="control-btn control-btn--danger" type="button">
            <span class="control-icon">🛑</span>
            <span class="control-label">End</span>
        </button>
    </div>
</main>
```

### CSS Styles (Mobile-First)

```css
/* Admin Control Bar */
.admin-control-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 8px 12px;
    padding-bottom: calc(8px + env(safe-area-inset-bottom));
    background: rgba(0, 0, 0, 0.9);
    border-top: 1px solid #333;
    z-index: 100;
}

.admin-control-bar.hidden {
    display: none;
}

.control-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 44px;
    min-height: 44px;
    padding: 8px 12px;
    background: #2a2a2a;
    border: none;
    border-radius: 8px;
    color: #fff;
    cursor: pointer;
    transition: background 0.2s, opacity 0.2s;
}

.control-btn:hover:not(.is-disabled) {
    background: #3a3a3a;
}

.control-btn:active:not(.is-disabled) {
    background: #4a4a4a;
}

.control-btn.is-disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.control-btn--danger {
    background: #7f1d1d;
}

.control-btn--danger:hover:not(.is-disabled) {
    background: #991b1b;
}

.control-icon {
    font-size: 20px;
    line-height: 1;
}

.control-label {
    font-size: 10px;
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Ensure game-view content doesn't get covered by control bar */
.game-container {
    padding-bottom: 80px; /* Space for control bar */
}

.reveal-container {
    padding-bottom: 80px; /* Space for control bar */
}
```

### JavaScript Implementation

```javascript
// player.js additions

/**
 * Show admin control bar for admin players
 */
function showAdminControlBar() {
    if (!isAdmin) return;
    const bar = document.getElementById('admin-control-bar');
    if (bar) bar.classList.remove('hidden');
}

/**
 * Hide admin control bar
 */
function hideAdminControlBar() {
    const bar = document.getElementById('admin-control-bar');
    if (bar) bar.classList.add('hidden');
}

/**
 * Update control bar button states based on phase
 * @param {string} phase - Current game phase
 */
function updateControlBarState(phase) {
    const stopBtn = document.getElementById('stop-song-btn');
    const nextBtn = document.getElementById('next-round-admin-btn');

    if (phase === 'PLAYING') {
        // Stop Song enabled, Next Round disabled
        if (stopBtn) {
            stopBtn.classList.remove('is-disabled');
            stopBtn.disabled = false;
        }
        if (nextBtn) {
            nextBtn.classList.add('is-disabled');
            nextBtn.disabled = true;
        }
    } else if (phase === 'REVEAL') {
        // Stop Song disabled, Next Round enabled
        if (stopBtn) {
            stopBtn.classList.add('is-disabled');
            stopBtn.disabled = true;
        }
        if (nextBtn) {
            nextBtn.classList.remove('is-disabled');
            nextBtn.disabled = false;
        }
    }
}

// Debounce helper
let adminActionPending = false;
const ADMIN_ACTION_DEBOUNCE_MS = 500;

function debounceAdminAction(action) {
    if (adminActionPending) return false;
    adminActionPending = true;
    setTimeout(() => { adminActionPending = false; }, ADMIN_ACTION_DEBOUNCE_MS);
    return true;
}

/**
 * Handle Stop Song button
 */
function handleStopSong() {
    if (!debounceAdminAction('stop')) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify({
        type: 'admin',
        action: 'stop_song'
    }));
}

/**
 * Handle Volume Up button
 */
function handleVolumeUp() {
    if (!debounceAdminAction('vol_up')) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify({
        type: 'admin',
        action: 'set_volume',
        direction: 'up'
    }));
}

/**
 * Handle Volume Down button
 */
function handleVolumeDown() {
    if (!debounceAdminAction('vol_down')) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify({
        type: 'admin',
        action: 'set_volume',
        direction: 'down'
    }));
}

/**
 * Handle End Game button
 */
function handleEndGame() {
    if (!confirm('End game and show final results?')) return;
    if (!debounceAdminAction('end')) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify({
        type: 'admin',
        action: 'end_game'
    }));
}

/**
 * Handle Next Round from control bar (reuse reveal logic)
 */
function handleNextRoundFromBar() {
    // Reuse existing handleNextRound() logic
    handleNextRound();
}

/**
 * Setup admin control bar event handlers
 */
function setupAdminControlBar() {
    document.getElementById('stop-song-btn')?.addEventListener('click', handleStopSong);
    document.getElementById('volume-up-btn')?.addEventListener('click', handleVolumeUp);
    document.getElementById('volume-down-btn')?.addEventListener('click', handleVolumeDown);
    document.getElementById('next-round-admin-btn')?.addEventListener('click', handleNextRoundFromBar);
    document.getElementById('end-game-btn')?.addEventListener('click', handleEndGame);
}

// Add to initAll():
// setupAdminControlBar();

// Update handleServerMessage() to show/hide control bar:
// if (data.phase === 'PLAYING' || data.phase === 'REVEAL') {
//     showAdminControlBar();
//     updateControlBarState(data.phase);
// } else {
//     hideAdminControlBar();
// }
```

### WebSocket Message Format (Admin Actions)

Per architecture.md, admin actions use this format:

```json
// Client → Server
{"type": "admin", "action": "stop_song"}
{"type": "admin", "action": "set_volume", "direction": "up"}
{"type": "admin", "action": "set_volume", "direction": "down"}
{"type": "admin", "action": "end_game"}

// Server → Client (responses - may need backend implementation in Epic 6.2-6.5)
{"type": "error", "code": "NOT_ADMIN", "message": "Only admin can perform this action"}
{"type": "song_stopped"}
{"type": "volume_changed", "level": 0.8}
```

**NOTE:** The backend handlers for these actions (except `start_game` and `next_round` which exist) will be implemented in Stories 6.2-6.5. This story focuses on the UI only.

### Architecture Compliance

- **CSS Naming:** kebab-case classes with `is-` prefix for states (`.is-disabled`)
- **JS Naming:** camelCase functions (`handleStopSong`, `updateControlBarState`)
- **Touch Targets:** 44x44px minimum per NFR18
- **Mobile-First:** Fixed bottom bar with safe-area padding
- **WebSocket:** snake_case message fields per architecture

### Anti-Patterns to Avoid

- Do NOT add control bar inside game-view or reveal-view (needs to persist across both)
- Do NOT call admin actions for non-admin players
- Do NOT skip debouncing (prevents rapid repeated clicks)
- Do NOT use inline onclick handlers (use addEventListener)
- Do NOT forget safe-area padding (iPhone notch)

### Backend Dependencies

This story is **UI-only**. The actual backend handlers for admin actions:
- `stop_song` → Story 6.2
- `set_volume` → Story 6.4
- `end_game` → Story 6.5

The `next_round` action already exists from Epic 4. The UI can send messages, but backend may not respond until those stories are implemented.

### Testing Considerations

1. **Manual Test:** Join as admin, verify control bar appears during PLAYING
2. **Manual Test:** Join as regular player, verify NO control bar
3. **Manual Test:** Tap buttons, verify WebSocket messages sent (check browser dev tools)
4. **Manual Test:** Verify button states change between PLAYING and REVEAL
5. **Manual Test:** Verify End Game shows confirmation dialog

### References

- [Source: epics.md#Story-6.1] - FR47, FR48 admin control requirements
- [Source: architecture.md#WebSocket-Architecture] - Admin message schema
- [Source: project-context.md#Frontend-Rules] - CSS/JS naming conventions
- [Source: project-context.md#Constants] - Error codes for NOT_ADMIN

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A - UI-only implementation

### Completion Notes List

- Implemented admin control bar HTML with 5 buttons (Stop, Volume Down, Volume Up, Next, End) positioned outside game-view for persistence across phases
- Added CSS styles for fixed-bottom bar with 44x44px touch targets, safe-area padding, and disabled states
- Implemented JS visibility logic: showAdminControlBar() checks isAdmin flag, hideAdminControlBar() hides unconditionally
- Added phase-based button states: Stop Song enabled in PLAYING, Next Round enabled in REVEAL
- Wired all button handlers with 500ms debounce to prevent rapid clicks
- Implemented WebSocket message sending for stop_song, set_volume, end_game, next_round
- Added server response handlers for NOT_ADMIN, song_stopped, volume_changed messages
- Note: Backend handlers for stop_song, set_volume, end_game will be implemented in Stories 6.2-6.5

### File List

- custom_components/beatify/www/player.html (modified - added admin-control-bar div)
- custom_components/beatify/www/css/styles.css (modified - added control bar styles)
- custom_components/beatify/www/js/player.js (modified - added control bar JS functions)
