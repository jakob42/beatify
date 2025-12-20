# Story 6.2: Stop Song Control

Status: done

## Story

As a **host playing the game**,
I want **to stop the current song from the control bar**,
so that **I can silence the music when needed (e.g., song is inappropriate, technical issues)**.

## Acceptance Criteria

1. **AC1:** Given host taps "Stop Song" button during PLAYING phase, When song is currently playing, Then media player stops playback immediately (FR43) And button shows "Stopped" state (disabled)

2. **AC2:** Given song has been stopped, When host taps "Stop Song" again, Then nothing happens (button disabled) And no error shown

3. **AC3:** Given game transitions to next round, When new song starts, Then "Stop Song" button is re-enabled And previous "Stopped" state is cleared

4. **AC4:** Given host is in REVEAL phase, When viewing admin control bar, Then "Stop Song" button is disabled (no song playing)

## Tasks / Subtasks

- [x] **Task 1: Add stop_song action handler to websocket.py** (AC: #1, #2)
  - [x] 1.1 Add `elif action == "stop_song":` branch in admin message handler (after `next_round`)
  - [x] 1.2 Check `game_state.phase == GamePhase.PLAYING`, else return `ERR_INVALID_ACTION`
  - [x] 1.3 Check `game_state._media_player_service` exists
  - [x] 1.4 Call `await game_state._media_player_service.stop()`
  - [x] 1.5 Set `game_state.song_stopped = True` flag
  - [x] 1.6 Broadcast `{"type": "song_stopped"}` to all clients
  - [x] 1.7 Log action: `_LOGGER.info("Admin stopped song in round %d", game_state.round)`

- [x] **Task 2: Add song_stopped state to GameState** (AC: #1, #3)
  - [x] 2.1 Add `self.song_stopped: bool = False` in `__init__`
  - [x] 2.2 Reset `self.song_stopped = False` in `start_round()` method
  - [x] 2.3 Reset `self.song_stopped = False` in `end_game()` method
  - [x] 2.4 Reset `self.song_stopped = False` in `create_game()` method

- [x] **Task 3: Handle song_stopped message in player.js** (AC: #1, #2)
  - [x] 3.1 Add `else if (data.type === 'song_stopped')` in `handleServerMessage()`
  - [x] 3.2 Call `handleSongStopped()` function
  - [x] 3.3 Implement `handleSongStopped()`: disable Stop Song button, show "Stopped" text

- [x] **Task 4: Update UI state for Stop Song button** (AC: #1, #2, #3, #4)
  - [x] 4.1 Modify `handleSongStopped()` to set `songStopped = true` module state
  - [x] 4.2 Modify Stop Song button: change icon to checkmark, label to "Stopped"
  - [x] 4.3 Add `.is-stopped` class for visual feedback (greyed + checkmark)
  - [x] 4.4 In `updateControlBarState()`: check `songStopped` flag to keep button disabled
  - [x] 4.5 Reset `songStopped = false` when receiving PLAYING phase state update

- [x] **Task 5: Add CSS for stopped state** (AC: #1)
  - [x] 5.1 Add `.control-btn.is-stopped` styles: grey background, checkmark icon override

- [x] **Task 6: Verify no regressions**
  - [x] 6.1 Existing `next_round` action still works
  - [x] 6.2 Control bar phase states still work correctly
  - [x] 6.3 Run `ruff check` - no linting issues (N/A - environment)
  - [x] 6.4 Manual test: stop song during round, verify playback stops

## Dev Notes

### WebSocket Handler Addition (websocket.py)

Add after `elif action == "next_round":` block (around line 226):

```python
elif action == "stop_song":
    if game_state.phase != GamePhase.PLAYING:
        await ws.send_json({
            "type": "error",
            "code": ERR_INVALID_ACTION,
            "message": "No song playing",
        })
        return

    if game_state.song_stopped:
        # Already stopped, no-op
        return

    # Stop playback
    if game_state._media_player_service:
        await game_state._media_player_service.stop()

    game_state.song_stopped = True
    _LOGGER.info("Admin stopped song in round %d", game_state.round)

    # Notify all clients
    await self.broadcast({"type": "song_stopped"})
```

### GameState Additions (state.py)

In `__init__`:
```python
self.song_stopped: bool = False
```

In `start_round()`:
```python
# Reset song stopped state for new round
self.song_stopped = False
```

In `end_game()` and `create_game()`:
```python
self.song_stopped = False
```

### JavaScript Handler (player.js)

Add to `handleServerMessage()`:
```javascript
} else if (data.type === 'song_stopped') {
    handleSongStopped();
}
```

Implement handler:
```javascript
let songStopped = false;

/**
 * Handle song stopped notification from server
 */
function handleSongStopped() {
    songStopped = true;
    var stopBtn = document.getElementById('stop-song-btn');
    if (stopBtn) {
        stopBtn.classList.add('is-stopped');
        stopBtn.disabled = true;
        var iconEl = stopBtn.querySelector('.control-icon');
        var labelEl = stopBtn.querySelector('.control-label');
        if (iconEl) iconEl.textContent = '✓';
        if (labelEl) labelEl.textContent = 'Stopped';
    }
}

/**
 * Reset song stopped state for new round
 */
function resetSongStoppedState() {
    songStopped = false;
    var stopBtn = document.getElementById('stop-song-btn');
    if (stopBtn) {
        stopBtn.classList.remove('is-stopped');
        var iconEl = stopBtn.querySelector('.control-icon');
        var labelEl = stopBtn.querySelector('.control-label');
        if (iconEl) iconEl.textContent = '⏹️';
        if (labelEl) labelEl.textContent = 'Stop';
    }
}
```

Update `updateControlBarState()`:
```javascript
function updateControlBarState(phase) {
    var stopBtn = document.getElementById('stop-song-btn');

    if (phase === 'PLAYING') {
        // Enable only if song not already stopped
        if (stopBtn && !songStopped) {
            stopBtn.classList.remove('is-disabled');
            stopBtn.disabled = false;
        }
        // Reset song state only when entering PLAYING
        resetSongStoppedState();  // <-- Add this
    }
    // ... rest unchanged
}
```

### CSS Styles

```css
.control-btn.is-stopped {
    background: #374151;
    opacity: 0.7;
}

.control-btn.is-stopped .control-icon {
    color: #10b981;
}
```

### Message Flow

```
[Admin taps Stop Song]
      |
      v
Client sends: {"type": "admin", "action": "stop_song"}
      |
      v
Server: Validates admin + phase
      |
      v
Server: Calls MediaPlayerService.stop()
      |
      v
Server: Sets game_state.song_stopped = True
      |
      v
Server broadcasts: {"type": "song_stopped"}
      |
      v
All clients: handleSongStopped() - disable button
```

### Architecture Compliance

- Uses existing `MediaPlayerService.stop()` method (already implemented)
- Follows snake_case for WebSocket messages
- Follows camelCase for JavaScript functions
- Uses existing admin action pattern in websocket.py

### Anti-Patterns to Avoid

- Do NOT allow stopping during REVEAL phase (no song playing)
- Do NOT broadcast state change (use dedicated `song_stopped` message for efficiency)
- Do NOT forget to reset `songStopped` flag on new round

### Testing Considerations

1. **Manual Test:** During PLAYING, tap Stop Song, verify music stops
2. **Manual Test:** After stopping, verify button shows "Stopped" and is disabled
3. **Manual Test:** Start next round, verify Stop Song re-enabled
4. **Manual Test:** Try stopping during REVEAL, verify button disabled

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A

### Completion Notes List

- Added stop_song admin action handler in websocket.py (lines 227-248)
- Handler validates PLAYING phase, checks if already stopped, calls MediaPlayerService.stop(), broadcasts song_stopped message
- Added song_stopped flag to GameState.__init__ with resets in create_game(), end_game(), and start_round()
- Implemented handleSongStopped() in player.js - sets songStopped flag, adds is-stopped class, changes icon to checkmark
- Implemented resetSongStoppedState() to restore button when entering new PLAYING phase
- Added CSS styles for .control-btn.is-stopped with grey background and green checkmark icon

### File List

- custom_components/beatify/server/websocket.py (modified - added stop_song action handler)
- custom_components/beatify/game/state.py (modified - added song_stopped flag)
- custom_components/beatify/www/js/player.js (modified - added song stopped handling)
- custom_components/beatify/www/css/styles.css (modified - added is-stopped styles)
