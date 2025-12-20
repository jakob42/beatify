# Story 6.6: Start New Game Reset

Status: done

## Story

As a **host who just finished a game**,
I want **a clear option to start a new game**,
so that **I can easily run another session without navigating back to the admin page**.

## Acceptance Criteria

1. **AC1:** Given game has ended (END phase), When final leaderboard is displayed, Then "New Game" button is visible to admin player only

2. **AC2:** Given admin taps "New Game" button, When confirmed, Then admin is redirected to admin page And game state is reset for new setup

3. **AC3:** Given regular player views end screen, When game has ended, Then they see "Thanks for playing" message And no "New Game" button (admin-only)

4. **AC4:** Given admin starts new game from admin page, When new game is created, Then previous game is fully cleaned up And new game_id is generated

## Tasks / Subtasks

- [x] **Task 1: Add New Game button to end-view for admin** (AC: #1, #3)
  - [x] 1.1 HTML already exists: `<div id="end-admin-controls" class="end-admin-controls hidden">`
  - [x] 1.2 Button exists: `<button id="new-game-btn" class="new-game-btn">Start New Game</button>`
  - [x] 1.3 Styled with green primary button

- [x] **Task 2: Show/hide New Game button based on admin status** (AC: #1, #3)
  - [x] 2.1 updateEndView() checks currentPlayer.is_admin
  - [x] 2.2 Shows `end-admin-controls` only for admin
  - [x] 2.3 Shows `end-player-message` for regular players

- [x] **Task 3: Implement New Game button handler** (AC: #2)
  - [x] 3.1 handleNewGame() function implemented
  - [x] 3.2 Shows confirmation: "Start a new game?"
  - [x] 3.3 On confirm, redirects to `/beatify/admin`
  - [x] 3.4 Clears session storage (beatify_admin_name, beatify_is_admin)

- [x] **Task 4: Ensure clean game reset on admin page** (AC: #4)
  - [x] 4.1 Admin page handles existing game state
  - [x] 4.2 game_state.end_game() clears all state (verified in Epic 4/5)
  - [x] 4.3 create_game() generates fresh game_id via secrets.token_urlsafe(8)

- [x] **Task 5: Style end-view admin controls** (AC: #1)
  - [x] 5.1 .end-admin-controls styles exist
  - [x] 5.2 Positioned after final leaderboard
  - [x] 5.3 .new-game-btn styled as green primary button

- [x] **Task 6: Verify no regressions**
  - [x] 6.1 End-view displays correctly for all players
  - [x] 6.2 Admin page start-game flow works
  - [x] 6.3 Run `ruff check` - no linting issues (N/A - JS only changes)

## Dev Notes

### HTML Addition (player.html)

Add inside `#end-view .end-container`, after existing content:

```html
<!-- Admin controls for end view -->
<div id="end-admin-controls" class="end-admin-controls hidden">
    <button id="new-game-btn" class="btn btn-primary btn-large">
        <span class="btn-icon">🎮</span>
        New Game
    </button>
    <p class="admin-hint">Return to setup for a new session</p>
</div>
```

### CSS Styles

```css
.end-admin-controls {
    margin-top: 32px;
    text-align: center;
}

.end-admin-controls .btn-large {
    padding: 16px 32px;
    font-size: 18px;
}

.end-admin-controls .admin-hint {
    margin-top: 12px;
    font-size: 14px;
    color: #888;
}
```

### JavaScript Implementation (player.js)

Add handler:
```javascript
/**
 * Handle New Game button click
 */
function handleNewGame() {
    if (!confirm('Start a new game?')) {
        return;
    }

    // Clear admin session storage
    try {
        sessionStorage.removeItem('beatify_admin_name');
        sessionStorage.removeItem('beatify_is_admin');
    } catch (e) {
        // Ignore storage errors
    }

    // Redirect to admin page
    window.location.href = '/beatify/admin';
}

/**
 * Setup end view controls
 */
function setupEndViewControls() {
    document.getElementById('new-game-btn')?.addEventListener('click', handleNewGame);
}

// Add to initAll()
// setupEndViewControls();
```

Update end-view handling in `handleServerMessage()`:
```javascript
if (data.phase === 'END') {
    stopCountdown();
    showView('end-view');
    hideAdminControlBar();

    // Show final leaderboard
    if (data.leaderboard) {
        renderFinalLeaderboard(data);
    }

    // Show admin controls if current player is admin
    var endAdminControls = document.getElementById('end-admin-controls');
    if (endAdminControls) {
        // Check if current player is admin
        var currentPlayer = data.leaderboard?.find(function(p) {
            return p.name === playerName;
        });
        if (currentPlayer && currentPlayer.is_admin) {
            endAdminControls.classList.remove('hidden');
        } else {
            endAdminControls.classList.add('hidden');
        }
    }

    // Show winner
    if (data.winner) {
        updateWinnerDisplay(data.winner);
    }
}
```

### Final Leaderboard Rendering (player.js)

If not already implemented from Epic 5:
```javascript
/**
 * Render final leaderboard in end view
 * @param {Object} data - State data with leaderboard
 */
function renderFinalLeaderboard(data) {
    var listEl = document.getElementById('final-leaderboard-list');
    if (!listEl) return;

    var leaderboard = data.leaderboard || [];

    var html = '';
    leaderboard.forEach(function(entry) {
        var rankClass = entry.rank === 1 ? 'is-winner' : '';
        var isCurrentPlayer = entry.name === playerName;
        var currentClass = isCurrentPlayer ? 'is-current' : '';
        var adminBadge = entry.is_admin ? '<span class="admin-badge">👑</span>' : '';

        html += '<div class="leaderboard-entry final-entry ' + rankClass + ' ' + currentClass + '">' +
            '<span class="entry-rank">#' + entry.rank + '</span>' +
            '<span class="entry-name">' + escapeHtml(entry.name) + adminBadge + '</span>' +
            '<span class="entry-stats">' +
                '<span class="stat">🔥' + (entry.best_streak || 0) + '</span>' +
                '<span class="stat">🎯' + (entry.rounds_played || 0) + '</span>' +
            '</span>' +
            '<span class="entry-score">' + entry.score + '</span>' +
        '</div>';
    });

    listEl.innerHTML = html;
}

/**
 * Update winner display
 * @param {Object} winner - Winner info {name, score}
 */
function updateWinnerDisplay(winner) {
    var winnerEl = document.getElementById('winner-name');
    var scoreEl = document.getElementById('winner-score');

    if (winnerEl) winnerEl.textContent = winner.name;
    if (scoreEl) scoreEl.textContent = winner.score + ' pts';
}
```

### What Happens on Admin Page Return

When admin clicks "New Game" and returns to admin page:

1. `window.location.href = '/beatify/admin'` triggers page load
2. Admin page's `loadStatus()` checks for active game
3. If game exists (even in END phase), shows "existing game" view
4. Admin can "End Game" to clear, then start fresh
5. New game creation generates new `game_id` via `secrets.token_urlsafe(8)`

### Alternative: Clear Game on New Game Click

Could also call end-game API before redirect:
```javascript
async function handleNewGame() {
    if (!confirm('Start a new game?')) return;

    // End current game first
    try {
        await fetch('/beatify/api/end-game', { method: 'POST' });
    } catch (e) {
        // Continue anyway
    }

    // Clear storage and redirect
    sessionStorage.clear();
    window.location.href = '/beatify/admin';
}
```

This ensures clean state, but may cause race conditions with WebSocket. Simpler to let admin page handle it.

### Architecture Compliance

- Uses existing admin page for game setup
- Follows redirect pattern from admin join flow
- Clears session storage to prevent stale admin state

### Anti-Patterns to Avoid

- Do NOT show "New Game" to regular players
- Do NOT skip confirmation dialog
- Do NOT create game directly from player page (use admin page)
- Do NOT forget to clear session storage

### Testing Considerations

1. **Manual Test:** End game, verify admin sees "New Game" button
2. **Manual Test:** End game, verify regular player does NOT see "New Game" button
3. **Manual Test:** Click "New Game", confirm, verify redirect to admin page
4. **Manual Test:** Start new game from admin, verify fresh game_id
5. **Manual Test:** Verify old players are disconnected/cleared

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A

### Completion Notes List

- HTML and CSS for New Game button already existed from prior Epic 5 implementation
- Updated handleNewGame() to use redirect approach per story AC:
  - Shows confirmation dialog
  - Clears sessionStorage (beatify_admin_name, beatify_is_admin)
  - Redirects to /beatify/admin for new game setup
- Existing updateEndView() correctly shows button only for admin players
- Regular players see "Thanks for playing" message instead

### File List

- custom_components/beatify/www/js/player.js (modified - updated handleNewGame for redirect)
