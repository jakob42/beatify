# Story 6.4: Volume Control

Status: ready-for-dev

## Story

As a **host playing the game**,
I want **to adjust volume up or down from the control bar**,
so that **I can manage music volume without leaving the game**.

## Acceptance Criteria

1. **AC1:** Given host taps "Volume Up" button, When media player is available, Then volume increases by 10% (FR45) And visual feedback shows volume changed

2. **AC2:** Given host taps "Volume Down" button, When media player is available, Then volume decreases by 10% (FR45) And visual feedback shows volume changed

3. **AC3:** Given volume is at maximum (100%), When host taps "Volume Up", Then nothing happens (at limit) And button shows max indicator

4. **AC4:** Given volume is at minimum (0%), When host taps "Volume Down", Then nothing happens (at limit) And button shows min indicator

5. **AC5:** Given media player is unavailable, When host taps volume buttons, Then appropriate error shown And buttons remain functional (for retry)

## Tasks / Subtasks

- [ ] **Task 1: Add volume state tracking to GameState** (AC: #1, #2, #3, #4)
  - [ ] 1.1 Add `self.volume_level: float = 0.5` in `__init__` (default 50%)
  - [ ] 1.2 Add constant `VOLUME_STEP = 0.1` in const.py
  - [ ] 1.3 Add method `adjust_volume(direction: str) -> float` that returns new level
  - [ ] 1.4 Clamp volume between 0.0 and 1.0

- [ ] **Task 2: Add set_volume action handler to websocket.py** (AC: #1, #2, #3, #4, #5)
  - [ ] 2.1 Add `elif action == "set_volume":` branch in admin message handler
  - [ ] 2.2 Extract `direction` from data ("up" or "down")
  - [ ] 2.3 Calculate new volume: `current ± VOLUME_STEP`
  - [ ] 2.4 Call `await game_state._media_player_service.set_volume(new_level)`
  - [ ] 2.5 Update `game_state.volume_level = new_level`
  - [ ] 2.6 Send `{"type": "volume_changed", "level": new_level}` to requester only
  - [ ] 2.7 Handle case where media player unavailable

- [ ] **Task 3: Handle volume_changed message in player.js** (AC: #1, #2, #3, #4)
  - [ ] 3.1 Add `else if (data.type === 'volume_changed')` in `handleServerMessage()`
  - [ ] 3.2 Implement `handleVolumeChanged(level)` function
  - [ ] 3.3 Show brief visual feedback (e.g., volume level indicator)
  - [ ] 3.4 Update button states if at min/max

- [ ] **Task 4: Add volume feedback UI** (AC: #1, #2, #3, #4)
  - [ ] 4.1 Add volume indicator element in control bar HTML
  - [ ] 4.2 Show volume level briefly on change (toast-style fade)
  - [ ] 4.3 Update volume up/down button appearance at limits

- [ ] **Task 5: Style volume feedback** (AC: #1, #2, #3, #4)
  - [ ] 5.1 Add `.volume-indicator` popup styles
  - [ ] 5.2 Add transition/animation for fade in/out
  - [ ] 5.3 Add `.control-btn.is-at-limit` style (greyed when at 0% or 100%)

- [ ] **Task 6: Wire volume button handlers** (AC: #1, #2)
  - [ ] 6.1 Confirm `handleVolumeUp()` and `handleVolumeDown()` from Story 6.1
  - [ ] 6.2 Verify debouncing works (prevent rapid clicks)
  - [ ] 6.3 Test both buttons send correct messages

- [ ] **Task 7: Verify no regressions**
  - [ ] 7.1 Song playback unaffected by volume changes
  - [ ] 7.2 Other admin controls still work
  - [ ] 7.3 Run `ruff check` - no linting issues

## Dev Notes

### Constants (const.py)

Add:
```python
# Volume control step (10%)
VOLUME_STEP = 0.1
```

### GameState Additions (state.py)

In `__init__`:
```python
self.volume_level: float = 0.5  # Default 50%
```

In `end_game()` and `create_game()`:
```python
self.volume_level = 0.5  # Reset to default
```

Add method:
```python
def adjust_volume(self, direction: str) -> float:
    """
    Adjust volume level by step.

    Args:
        direction: "up" to increase, "down" to decrease

    Returns:
        New volume level (clamped 0.0 to 1.0)
    """
    from custom_components.beatify.const import VOLUME_STEP

    if direction == "up":
        self.volume_level = min(1.0, self.volume_level + VOLUME_STEP)
    elif direction == "down":
        self.volume_level = max(0.0, self.volume_level - VOLUME_STEP)

    return self.volume_level
```

### WebSocket Handler (websocket.py)

Add after `stop_song` handler:

```python
elif action == "set_volume":
    direction = data.get("direction")  # "up" or "down"
    if direction not in ("up", "down"):
        await ws.send_json({
            "type": "error",
            "code": ERR_INVALID_ACTION,
            "message": "Invalid volume direction",
        })
        return

    # Calculate new volume
    new_level = game_state.adjust_volume(direction)

    # Apply to media player
    if game_state._media_player_service:
        success = await game_state._media_player_service.set_volume(new_level)
        if not success:
            _LOGGER.warning("Failed to set volume to %.0f%%", new_level * 100)

    _LOGGER.info("Volume adjusted %s to %.0f%%", direction, new_level * 100)

    # Send feedback to requester only (not broadcast)
    await ws.send_json({
        "type": "volume_changed",
        "level": new_level,
    })
```

### JavaScript Handler (player.js)

Add state and handler:
```javascript
let currentVolume = 0.5;  // Track for UI state

/**
 * Handle volume changed response from server
 * @param {number} level - New volume level (0.0 to 1.0)
 */
function handleVolumeChanged(level) {
    currentVolume = level;
    showVolumeIndicator(level);
    updateVolumeLimitStates(level);
}

/**
 * Show brief volume indicator popup
 * @param {number} level - Volume level
 */
function showVolumeIndicator(level) {
    var indicator = document.getElementById('volume-indicator');
    if (!indicator) return;

    var percentage = Math.round(level * 100);
    indicator.textContent = '🔊 ' + percentage + '%';
    indicator.classList.remove('hidden');
    indicator.classList.add('is-visible');

    // Fade out after 1.5s
    setTimeout(function() {
        indicator.classList.remove('is-visible');
        setTimeout(function() {
            indicator.classList.add('hidden');
        }, 300);
    }, 1500);
}

/**
 * Update volume buttons when at limits
 * @param {number} level - Current volume level
 */
function updateVolumeLimitStates(level) {
    var upBtn = document.getElementById('volume-up-btn');
    var downBtn = document.getElementById('volume-down-btn');

    if (upBtn) {
        upBtn.classList.toggle('is-at-limit', level >= 1.0);
    }
    if (downBtn) {
        downBtn.classList.toggle('is-at-limit', level <= 0.0);
    }
}
```

Add to `handleServerMessage()`:
```javascript
} else if (data.type === 'volume_changed') {
    handleVolumeChanged(data.level);
}
```

### HTML Addition (player.html)

Add inside `#admin-control-bar`:
```html
<!-- Volume feedback indicator -->
<div id="volume-indicator" class="volume-indicator hidden">🔊 50%</div>
```

### CSS Styles

```css
/* Volume indicator popup */
.volume-indicator {
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.8);
    color: #fff;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 8px;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.volume-indicator.is-visible {
    opacity: 1;
}

/* Volume button at limit */
.control-btn.is-at-limit {
    opacity: 0.5;
}

.control-btn.is-at-limit:active {
    transform: none;  /* No visual feedback when at limit */
}
```

### Message Flow

```
[Admin taps Volume Up]
      |
      v
Client sends: {"type": "admin", "action": "set_volume", "direction": "up"}
      |
      v
Server: Validates admin
      |
      v
Server: game_state.adjust_volume("up") → 0.6
      |
      v
Server: MediaPlayerService.set_volume(0.6)
      |
      v
Server sends to requester only: {"type": "volume_changed", "level": 0.6}
      |
      v
Client: Shows "🔊 60%" indicator, updates button states
```

### Why Requester-Only Response?

Volume changes don't need to be broadcast to all players:
- Only the admin needs feedback
- Reduces WebSocket traffic
- Other players don't see/care about volume

### Architecture Compliance

- Uses existing `MediaPlayerService.set_volume()` (already implemented)
- Follows snake_case for WebSocket messages
- 10% volume step per FR45

### Anti-Patterns to Avoid

- Do NOT broadcast volume changes (send to requester only)
- Do NOT allow volume outside 0.0-1.0 range
- Do NOT skip debouncing (rapid clicks = multiple changes)
- Do NOT forget to reset volume on game end/create

### Testing Considerations

1. **Manual Test:** Tap Volume Up, verify speaker gets louder + indicator shows
2. **Manual Test:** Tap Volume Down, verify speaker gets quieter
3. **Manual Test:** Keep tapping Volume Up until max, verify button shows limit state
4. **Manual Test:** Verify volume persists across rounds

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
