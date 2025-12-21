# Story 8.3: Remove Start Game Button from Admin Lobby

Status: done

## Story

As a **host**,
I want **only "Join as Player" shown on the admin lobby page**,
so that **I follow the correct flow: join first, then start game from player view**.

## Context

Per PRD Journey 2 and FR21, the correct admin flow is:
1. Create lobby from admin page
2. Click "Join as Player" to transition to player page
3. Start game from player page (with admin controls)

The current implementation incorrectly shows a "Start Game" button on the admin lobby page, which breaks the intended user journey.

## Acceptance Criteria

1. **Given** admin is on the lobby page (after creating a game) **When** the lobby view displays **Then** only the "Join as Player" button is visible
2. **Given** the admin.html file **When** reviewed **Then** the `#start-game-lobby` button element is removed
3. **Given** the admin.js file **When** reviewed **Then** `startGameplay()` function is removed
4. **Given** the admin.js file **When** reviewed **Then** event listener for `start-game-lobby` is removed
5. **Given** admin clicks "Join as Player" **When** they enter their name and join **Then** they are redirected to the player page with admin controls including "Start Game"

## Tasks / Subtasks

- [x] Task 1: Remove Start Game button from admin.html (AC: 1, 2)
  - [x] Remove `<button id="start-game-lobby">` element (lines 59-62)
  - [x] Promoted "Join as Player" button to btn-primary btn-large

- [x] Task 2: Clean up admin.js (AC: 3, 4)
  - [x] Remove `startGameplay()` function (lines 518-551)
  - [x] Remove event listener `document.getElementById('start-game-lobby')?.addEventListener('click', startGameplay);` (line 25)

## Dev Notes

### Current Code Analysis

**admin.html (lines 58-67):**
```html
<div class="admin-lobby-actions no-print">
    <button id="start-game-lobby" class="btn btn-primary btn-large">
        <span class="btn-icon">▶️</span>
        Start Game
    </button>
    <button id="participate-btn" class="btn btn-secondary">
        <span class="btn-icon">🎮</span>
        Join as Player
    </button>
</div>
```

**After removal (expected):**
```html
<div class="admin-lobby-actions no-print">
    <button id="participate-btn" class="btn btn-primary btn-large">
        <span class="btn-icon">🎮</span>
        Join as Player
    </button>
</div>
```

Note: Consider promoting "Join as Player" to `btn-primary btn-large` since it's now the main action.

**admin.js (line 25):**
```javascript
document.getElementById('start-game-lobby')?.addEventListener('click', startGameplay);
```

**admin.js (lines 518-551):**
```javascript
async function startGameplay() {
    const btn = document.getElementById('start-game-lobby');
    if (!btn) return;
    // ... function body ...
}
```

### Intended User Flow (PRD Journey 2)

1. Admin creates lobby (clicks "Start Game" on setup screen)
2. Admin sees QR code and lobby view
3. Admin clicks "Join as Player" button
4. Admin enters name in modal
5. Admin is redirected to player page (`/beatify/play?game=...`)
6. On player page, admin sees "Start Game" button (Story 3.5 admin controls)
7. Admin clicks "Start Game" to begin gameplay

### File Locations

| File | Path | Lines to Modify |
|------|------|-----------------|
| admin.html | `custom_components/beatify/www/admin.html` | 59-62 (remove button) |
| admin.js | `custom_components/beatify/www/js/admin.js` | 25 (remove listener), 518-551 (remove function) |

### Testing

1. Create a new game from admin page
2. Verify lobby shows only "Join as Player" button (no "Start Game")
3. Click "Join as Player", enter name
4. Verify redirect to player page
5. Verify player page shows "Start Game" button (admin controls)
6. Click "Start Game" on player page
7. Verify game transitions to PLAYING phase

### References

- [Source: epics.md#Story 8.3]
- [Source: project-context.md#WebSocket]
- [Source: PRD Journey 2 and FR21]

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5

### Debug Log References
N/A

### Completion Notes List
- Removed Start Game button from admin.html lobby section
- Promoted "Join as Player" button to primary/large styling (was secondary)
- Removed event listener for start-game-lobby from admin.js
- Removed startGameplay() function from admin.js
- Admin flow now correctly: create lobby → join as player → start game from player view

### File List
- custom_components/beatify/www/admin.html
- custom_components/beatify/www/js/admin.js
