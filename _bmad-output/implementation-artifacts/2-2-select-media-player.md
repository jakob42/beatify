# Story 2.2: Select Media Player

Status: done

## Story

As a **host**,
I want **to select which HA media player to use for audio output**,
so that **the music plays through my preferred speakers**.

## Acceptance Criteria

1. **AC1:** Given admin page is loaded with available media players, When host views the media player selection area, Then only available (non-unavailable) HA `media_player` entities are displayed as selectable options (FR8) And each shows friendly name and current state (playing/idle/off)
2. **AC2:** Given no media players are available in HA (all unavailable or none configured), When admin page loads, Then an error displays: "No media players found. Configure a media player in Home Assistant." And troubleshooting guidance is provided (FR56)
3. **AC3:** Given some media players exist but all are unavailable, When admin page loads, Then error displays: "All media players are unavailable. Check your devices are powered on." And troubleshooting guidance is provided (FR56)
4. **AC4:** Given host selects a media player, When selection is made, Then selection is visually confirmed And the player is stored for the game session

## Tasks / Subtasks

- [x] **Task 1: Update media player rendering with radio buttons** (AC: #1, #4)
  - [x] 1.1 Modify `renderMediaPlayers()` in `admin.js` to filter out unavailable players before rendering
  - [x] 1.2 Add radio button input for each available player
  - [x] 1.3 Add `data-entity-id` attribute to radio storing the entity_id
  - [x] 1.4 Add `data-state` attribute for tracking current player state
  - [x] 1.5 Apply CSS class `.media-player-item.is-selectable` for players with radio button
  - [x] 1.6 Display state with visual indicators (green dot for playing, gray for idle/paused/off)

- [x] **Task 2: Implement selection state tracking** (AC: #1, #4)
  - [x] 2.1 Create `selectedMediaPlayer` variable to track selected entity_id
  - [x] 2.2 Add `handleMediaPlayerSelect(entityId, state)` function to update selection state
  - [x] 2.3 Wire radio button change events to `handleMediaPlayerSelect`
  - [x] 2.4 Add `.is-selected` CSS class to visually indicate selected state

- [x] **Task 3: Implement no-media-players and all-unavailable error states** (AC: #2, #3)
  - [x] 3.1 Update `renderMediaPlayers()` to detect if all players filtered out (all unavailable)
  - [x] 3.2 Show "All media players are unavailable" error when players exist but all unavailable
  - [x] 3.3 Show "No media players found" error when no players configured at all
  - [x] 3.4 Add troubleshooting link (HA media player setup docs)
  - [x] 3.5 Add `MEDIA_PLAYER_DOCS_URL = "https://www.home-assistant.io/integrations/#media-player"` to `const.py`
  - [x] 3.6 Update `/beatify/api/status` to include `media_player_docs_url` in response

- [x] **Task 4: Update start game validation** (AC: #4)
  - [x] 4.1 Update `updateStartButtonState()` to check for both playlist AND media player selection
  - [x] 4.2 Add validation message element for media player selection
  - [x] 4.3 Disable start button until both conditions met
  - [x] 4.4 Show appropriate validation message (playlist or media player missing)

- [x] **Task 5: Add CSS for media player selection states** (AC: #1, #4)
  - [x] 5.1 Add `.media-player-item` class extending `.list-item` for selectable items
  - [x] 5.2 Add `.media-player-item.is-selected` with visual highlight (same as playlist selection)
  - [x] 5.3 Add `.media-player-radio` with 44x44px touch target
  - [x] 5.4 Add `.state-indicator` classes for playing/idle states
  - [x] 5.5 Add `.state-dot` indicator styling (colored circle)

- [x] **Task 6: Update admin.html structure** (AC: #1, #2)
  - [x] 6.1 Add validation message element for media player section
  - [x] 6.2 Ensure proper section ordering (MA status, Media Players, Playlists, Game Controls)

- [x] **Task 7: E2E test for media player selection flow** (AC: #1, #2, #3, #4)
  - [x] 7.1 Write Playwright test in `tests/e2e/test_media_player_selection.py` covering:
    - Page loads and displays only available media players with radio buttons
    - Unavailable players are filtered out and not shown
    - Selecting media player updates visual state
    - No media players shows error with documentation link
    - All unavailable shows specific error message
    - Start button disabled until media player selected

- [x] **Task 8: Verify existing tests pass**
  - [x] 8.1 Run `pytest tests/` and verify all existing tests pass (6 pre-existing HA import failures unrelated to story)
  - [x] 8.2 No regressions introduced by changes

## Dev Notes

### Architecture Compliance

- **Frontend:** Vanilla JS only - NO jQuery, NO frameworks
- **Endpoint:** Uses existing `/beatify/api/status` - add `media_player_docs_url` to response
- **Radio buttons:** Must meet 44x44px touch target (NFR18)
- **Naming:** JS uses camelCase, CSS uses kebab-case with `is-` prefix for states
- **XSS Prevention:** Continue using `escapeHtml()` for all user-facing content
- **Single selection:** Use radio buttons (name="media-player"), not checkboxes

### Do NOT (Anti-Patterns)

- Do NOT create new API endpoints - use existing `/beatify/api/status`
- Do NOT use jQuery or any JS framework
- Do NOT allow multiple media player selection - single selection only
- Do NOT store selection state in localStorage - memory only
- Do NOT add backend validation for media player selection (yet) - frontend only for this story
- Do NOT change the media_players array structure from API - just add docs URL to response
- Do NOT show unavailable media players - filter them out before rendering

### Existing Code to Reuse

**From `styles.css` (already exists):**

| Class | Purpose | Lines |
|-------|---------|-------|
| `.list-item` | Base styling for list items | 65-91 |
| `.list-item.is-invalid` | Invalid item styling | 93-96 |
| `.playlist-item.is-selected` | Selected item styling (reuse pattern) | 103-106 |
| `.btn-primary:disabled` | Disabled button state | 167-170 |
| `.hidden` | Hide elements | 211-213 |
| `.status-error` | Error text color | 54-57 |
| `.empty-state` | Empty state container | 192-200 |

**From `admin.js` (already exists):**

| Function | Purpose | Lines |
|----------|---------|-------|
| `renderMediaPlayers(players)` | Render media player list (modify) | 65-84 |
| `escapeHtml(text)` | XSS prevention (reuse) | 247-254 |
| `loadStatus()` | Fetch status from API (reuse) | 18-38 |
| `updateStartButtonState()` | Update button state (modify) | 221-240 |

**From `views.py` (already exists):**

| Endpoint | Returns | Purpose |
|----------|---------|---------|
| `/beatify/api/status` | `{ media_players, playlists, ... }` | Status data (add docs URL) |

### Implementation Reference

**Radio button HTML structure:**

```html
<div class="media-player-item list-item is-selectable">
  <label class="radio-label">
    <input type="radio"
           class="media-player-radio"
           name="media-player"
           data-entity-id="media_player.living_room"
           data-state="idle">
    <span class="player-name">Living Room Speaker</span>
  </label>
  <span class="meta">
    <span class="state-dot state-idle"></span>
    idle
  </span>
</div>
```

**State management pattern (add to existing module state):**

```javascript
// Add to module-level state (existing: selectedPlaylists, playlistData, playlistDocsUrl)
let selectedMediaPlayer = null;  // { entityId: string, state: string } or null
let mediaPlayerDocsUrl = '';

function handleMediaPlayerSelect(radio) {
  const entityId = radio.dataset.entityId;
  const state = radio.dataset.state;

  // Update module state
  selectedMediaPlayer = { entityId, state };

  // Update visual selection
  document.querySelectorAll('.media-player-item').forEach(item => {
    item.classList.remove('is-selected');
  });
  radio.closest('.media-player-item').classList.add('is-selected');

  updateStartButtonState();
}
```

**Updated renderMediaPlayers with filtering:**

```javascript
function renderMediaPlayers(players) {
  const container = document.getElementById('media-players-list');
  const totalPlayers = players ? players.length : 0;

  // Filter out unavailable players
  const availablePlayers = (players || []).filter(p => p.state !== 'unavailable');

  if (totalPlayers === 0) {
    // No players configured at all
    container.innerHTML = `
      <div class="empty-state">
        <p class="status-error">No media players found. Configure a media player in Home Assistant.</p>
        <a href="${escapeHtml(mediaPlayerDocsUrl)}" target="_blank" rel="noopener">Setup Guide</a>
      </div>
    `;
    return;
  }

  if (availablePlayers.length === 0) {
    // Players exist but all unavailable
    container.innerHTML = `
      <div class="empty-state">
        <p class="status-error">All media players are unavailable. Check your devices are powered on.</p>
        <a href="${escapeHtml(mediaPlayerDocsUrl)}" target="_blank" rel="noopener">Troubleshooting</a>
      </div>
    `;
    return;
  }

  // Render only available players with radio buttons
  container.innerHTML = availablePlayers.map(player => `
    <div class="media-player-item list-item is-selectable">
      <label class="radio-label">
        <input type="radio"
               class="media-player-radio"
               name="media-player"
               data-entity-id="${escapeHtml(player.entity_id)}"
               data-state="${escapeHtml(player.state)}">
        <span class="player-name">${escapeHtml(player.friendly_name)}</span>
      </label>
      <span class="meta">
        <span class="state-dot state-${escapeHtml(player.state)}"></span>
        ${escapeHtml(player.state)}
      </span>
    </div>
  `).join('');

  // Attach event listeners
  container.querySelectorAll('.media-player-radio').forEach(radio => {
    radio.addEventListener('change', function() {
      handleMediaPlayerSelect(this);
    });
  });
}
```

**Updated updateStartButtonState():**

```javascript
function updateStartButtonState() {
  const btn = document.getElementById('start-game');
  const playlistMsg = document.getElementById('playlist-validation-msg');
  const mediaPlayerMsg = document.getElementById('media-player-validation-msg');

  if (!btn) return;

  const noPlaylist = selectedPlaylists.length === 0;
  const noMediaPlayer = selectedMediaPlayer === null;

  btn.disabled = noPlaylist || noMediaPlayer;

  // Show/hide playlist validation
  if (playlistMsg) {
    playlistMsg.classList.toggle('hidden', !noPlaylist);
  }

  // Show/hide media player validation
  if (mediaPlayerMsg) {
    mediaPlayerMsg.classList.toggle('hidden', !noMediaPlayer);
  }
}
```

**CSS additions to styles.css:**

```css
/* Media player selection (Story 2.2) */
.media-player-item.is-selectable {
  cursor: pointer;
}

.media-player-item.is-selected {
  background: #eff6ff;
  border-left: 3px solid #3b82f6;
}

.media-player-radio {
  width: 44px;
  height: 44px;
  margin-right: 12px;
  cursor: pointer;
  flex-shrink: 0;
}

.radio-label {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.player-name {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* State indicators */
.state-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.state-dot.state-playing {
  background: #22c55e;
}

.state-dot.state-idle,
.state-dot.state-paused,
.state-dot.state-off {
  background: #9ca3af;
}
```

**Updated admin.html structure:**

```html
<section id="media-players" class="card-section">
    <h2>Media Players</h2>
    <div id="media-players-list">Loading...</div>
    <p id="media-player-validation-msg" class="status-error hidden" style="margin-top: 12px;">
        Select a media player
    </p>
</section>
```

### Testing Approach

- **E2E tests** (`tests/e2e/test_media_player_selection.py`): Playwright tests cover all JS interaction logic
- **No separate JS unit tests** - E2E provides sufficient coverage for this UI-focused story
- **Existing Python tests** must pass - run `pytest tests/` before marking complete

### Error Messages

| Context | Message |
|---------|---------|
| No media players | "No media players found. Configure a media player in Home Assistant." |
| All unavailable | "All media players are unavailable. Check your devices are powered on." |
| Start validation (no player) | "Select a media player" |

### Constants to Add

```python
# const.py
MEDIA_PLAYER_DOCS_URL = "https://www.home-assistant.io/integrations/#media-player"
```

### State Display Mapping

Note: Unavailable players are filtered out and not shown.

| Player State | CSS Class | Visual |
|--------------|-----------|--------|
| `playing` | `.state-playing` | Green dot |
| `idle` | `.state-idle` | Gray dot |
| `paused` | `.state-paused` | Gray dot |
| `off` | `.state-off` | Gray dot |

### Previous Story Learnings (2.1)

From Story 2.1 implementation:
- Use `addEventListener` instead of inline handlers for CSP compatibility
- Add null checks for DOM elements before accessing
- Escape all dynamic content with `escapeHtml()`
- Check for duplicate selections before adding to state
- Test with both valid and invalid items present
- Code review caught: inline handlers, missing null checks, duplicate selection bug

### References

- [Source: epics.md#Story-2.2] - Original acceptance criteria
- [Source: architecture.md#Frontend-Architecture] - Vanilla JS, static files
- [Source: architecture.md#CSS-Classes] - kebab-case, is- prefix for states
- [Source: project-context.md#Frontend-Rules] - Touch targets, naming conventions
- [Source: www/js/admin.js:65-84] - Existing renderMediaPlayers function
- [Source: www/css/styles.css:99-138] - Playlist selection styles (pattern to follow)
- [Source: 2-1-select-playlists-for-game.md] - Previous story learnings

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Tests: 65 passed, 21 skipped, 6 failed (pre-existing HA import errors unrelated to story changes)

### Completion Notes List

- Implemented media player selection with radio buttons (single selection)
- Added filtering of unavailable players before rendering
- Added state dot indicators (green=playing, gray=idle/paused/off)
- Updated start button validation to require both playlist AND media player selection
- Added validation messages for both selection types
- Created comprehensive E2E tests following Story 2.1 pattern

### File List

- `custom_components/beatify/www/js/admin.js` - Modified (added selectedMediaPlayer state, mediaPlayerDocsUrl, renderMediaPlayers with filtering, handleMediaPlayerSelect, updated updateStartButtonState)
- `custom_components/beatify/www/css/styles.css` - Modified (added .media-player-item, .media-player-radio, .radio-label, .player-name, .state-dot classes)
- `custom_components/beatify/www/admin.html` - Modified (added media-player-validation-msg element)
- `custom_components/beatify/const.py` - Modified (added MEDIA_PLAYER_DOCS_URL constant)
- `custom_components/beatify/server/views.py` - Modified (added media_player_docs_url to API response, updated import)
- `tests/e2e/test_media_player_selection.py` - Created (E2E tests covering AC1-AC4)

## Change Log

- 2025-12-18: Code review fixes applied - H1 (redundant validation msg), H2 (test skip conditions), M1 (flexible class assertions), M2 (consolidated CSS).
- 2025-12-18: Story implemented by Dev agent - all tasks complete.
- 2025-12-18: Updated per user request - unavailable players now filtered out instead of shown with validation.
- 2025-12-18: Story created by SM agent, ready for dev.
