# Story 6.3: Next Round Control

Status: ready-for-dev

## Story

As a **host playing the game**,
I want **to skip to the next round from the control bar**,
so that **I can advance the game when ready, or skip problematic songs**.

## Acceptance Criteria

1. **AC1:** Given host taps "Next Round" button during REVEAL phase, When there are more rounds remaining, Then game transitions to next round (FR44) And new song starts playing

2. **AC2:** Given host taps "Next Round" button during PLAYING phase, When round is in progress, Then current round ends early (timer cancelled) And game transitions to REVEAL first (show results before next round)

3. **AC3:** Given host taps "Next Round" on the last round's REVEAL, When it's the final round, Then game transitions to END phase And final leaderboard is shown

4. **AC4:** Given game is in LOBBY or END phase, When viewing admin control bar, Then "Next Round" button is disabled

## Tasks / Subtasks

- [ ] **Task 1: Verify existing next_round action in websocket.py** (AC: #1, #2, #3)
  - [ ] 1.1 Confirm `action == "next_round"` handler exists (it does from Epic 4)
  - [ ] 1.2 Confirm PLAYING phase handling ends round first, then reveals
  - [ ] 1.3 Confirm REVEAL phase handling starts next round or ends game
  - [ ] 1.4 Confirm last_round flag triggers END phase correctly

- [ ] **Task 2: Wire control bar Next Round button** (AC: #1, #2, #3)
  - [ ] 2.1 Confirm `handleNextRoundFromBar()` calls existing `handleNextRound()`
  - [ ] 2.2 Verify debouncing works (from Story 6.1)
  - [ ] 2.3 Button sends `{type: "admin", action: "next_round"}` message

- [ ] **Task 3: Update button state management** (AC: #4)
  - [ ] 3.1 Confirm `updateControlBarState()` disables Next Round during PLAYING
  - [ ] 3.2 Confirm `updateControlBarState()` enables Next Round during REVEAL
  - [ ] 3.3 Verify button text changes to "Final Results" on last round (reuse reveal logic)

- [ ] **Task 4: Handle early round advancement feedback** (AC: #2)
  - [ ] 4.1 Add visual feedback when skipping (button shows "Ending...")
  - [ ] 4.2 Wait for state broadcast to confirm transition
  - [ ] 4.3 Reset button state when REVEAL phase received

- [ ] **Task 5: Verify no regressions**
  - [ ] 5.1 Existing reveal-view "Next Round" button still works
  - [ ] 5.2 Timer expiry still triggers REVEAL correctly
  - [ ] 5.3 End of game flow still works
  - [ ] 5.4 Run `ruff check` - no linting issues

## Dev Notes

### Existing Implementation Analysis

The `next_round` action is **already implemented** in `websocket.py:200-225`:

```python
elif action == "next_round":
    if game_state.phase == GamePhase.PLAYING:
        # Early advance - end current round first
        await game_state.end_round()
        # Broadcast handled by round_end_callback
    elif game_state.phase == GamePhase.REVEAL:
        # Start next round or end game
        if game_state.last_round:
            # No more rounds, end game
            game_state.phase = GamePhase.END
            await self.broadcast_state()
        else:
            # Start next round
            success = await game_state.start_round(self.hass)
            if success:
                await self.broadcast_state()
            else:
                # No more songs
                game_state.phase = GamePhase.END
                await self.broadcast_state()
```

**This story is primarily about wiring the control bar button to this existing action.**

### JavaScript Updates (player.js)

The control bar's Next Round button should reuse the existing `handleNextRound()`:

```javascript
/**
 * Handle Next Round from control bar (reuse reveal logic)
 */
function handleNextRoundFromBar() {
    handleNextRound();  // Already implemented for reveal view
}
```

Add loading state for early advancement:
```javascript
function handleNextRound() {
    if (nextRoundPending) return;

    if (ws && ws.readyState === WebSocket.OPEN) {
        nextRoundPending = true;

        // Update both buttons (reveal-view and control bar)
        var revealBtn = document.getElementById('next-round-btn');
        var barBtn = document.getElementById('next-round-admin-btn');

        if (revealBtn) {
            revealBtn.disabled = true;
            revealBtn.textContent = 'Loading...';
        }
        if (barBtn) {
            barBtn.disabled = true;
            var labelEl = barBtn.querySelector('.control-label');
            if (labelEl) labelEl.textContent = 'Wait...';
        }

        ws.send(JSON.stringify({
            type: 'admin',
            action: 'next_round'
        }));

        setTimeout(function() {
            nextRoundPending = false;
            if (revealBtn) revealBtn.disabled = false;
            if (barBtn) barBtn.disabled = false;
        }, NEXT_ROUND_DEBOUNCE_MS);
    }
}
```

### Phase State Updates

Ensure `updateControlBarState()` handles button states correctly:

```javascript
function updateControlBarState(phase) {
    var stopBtn = document.getElementById('stop-song-btn');
    var nextBtn = document.getElementById('next-round-admin-btn');

    if (phase === 'PLAYING') {
        // During PLAYING: Next Round enabled (for early skip)
        // Note: This differs from reveal-view where Next isn't shown during playing
        if (nextBtn) {
            nextBtn.classList.remove('is-disabled');
            nextBtn.disabled = false;
            var labelEl = nextBtn.querySelector('.control-label');
            if (labelEl) labelEl.textContent = 'Skip';
        }
    } else if (phase === 'REVEAL') {
        if (nextBtn) {
            nextBtn.classList.remove('is-disabled');
            nextBtn.disabled = false;
            var labelEl = nextBtn.querySelector('.control-label');
            if (labelEl) labelEl.textContent = 'Next';
        }
    } else {
        // LOBBY or END: disable
        if (nextBtn) {
            nextBtn.classList.add('is-disabled');
            nextBtn.disabled = true;
        }
    }
}
```

### Message Flow (Early Skip)

```
[Admin taps Next during PLAYING]
      |
      v
Client sends: {"type": "admin", "action": "next_round"}
      |
      v
Server: game_state.phase == PLAYING
      |
      v
Server: await game_state.end_round()
        - Stops media playback
        - Calculates scores
        - Transitions to REVEAL
        - Calls round_end_callback
      |
      v
Server broadcasts: {"type": "state", "phase": "REVEAL", ...}
      |
      v
All clients: showView('reveal-view'), show results
```

### Architecture Compliance

- Reuses existing `next_round` backend handler
- No duplicate code - single `handleNextRound()` function
- Button states managed via `updateControlBarState()`

### Key Difference from Reveal View

| Reveal View Button | Control Bar Button |
|--------------------|-------------------|
| Only visible in REVEAL phase | Visible in PLAYING + REVEAL |
| Text: "Next Round" or "Final Results" | Text: "Skip" (PLAYING) or "Next" (REVEAL) |
| Large prominent button | Compact control bar button |

### Anti-Patterns to Avoid

- Do NOT create separate handler for control bar (reuse existing)
- Do NOT enable button during LOBBY/END phases
- Do NOT skip the REVEAL phase (always show results before next round)

### Testing Considerations

1. **Manual Test:** During REVEAL, tap Next Round, verify next song plays
2. **Manual Test:** During PLAYING, tap Skip, verify round ends + REVEAL shown
3. **Manual Test:** On last round REVEAL, tap Final Results, verify END phase
4. **Manual Test:** Verify both buttons sync (reveal-view + control bar)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
