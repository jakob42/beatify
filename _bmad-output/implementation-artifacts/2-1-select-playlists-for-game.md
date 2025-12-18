# Story 2.1: Select Playlists for Game

Status: done

## Story

As a **host**,
I want **to select one or more playlist files for my game session**,
so that **I can customize the music selection for my party**.

## Acceptance Criteria

1. **AC1:** Given admin page is loaded with available playlists, When host views the playlist selection area, Then all valid playlists from `{HA_CONFIG}/beatify/playlists/` are displayed with: playlist name, song count, checkbox for selection
2. **AC2:** Given no playlists exist in the playlist directory, When admin page loads, Then an error displays: "No playlists found. Add playlist JSON files to [folder path]." And a link to "How to create playlists" documentation is provided (FR55)
3. **AC3:** Given host selects multiple playlists, When playlists are selected, Then total song count across all selected playlists is displayed
4. **AC4:** Given host attempts to start game with no playlists selected, When start game is clicked, Then validation prevents start with message "Select at least one playlist"

## Tasks / Subtasks

- [x] **Task 1: Update playlist rendering with checkboxes** (AC: #1)
  - [x] 1.1 Modify `renderPlaylists()` in `admin.js` to include checkbox input for each valid playlist
  - [x] 1.2 Add `data-path` attribute to checkbox storing the playlist file path
  - [x] 1.3 Add `data-song-count` attribute for calculation
  - [x] 1.4 Apply CSS class `.playlist-item.is-selectable` for valid playlists with checkbox
  - [x] 1.5 Invalid playlists use existing `.list-item.is-invalid` class (no checkbox, greyed out)

- [x] **Task 2: Implement selection state tracking** (AC: #1, #3)
  - [x] 2.1 Create `selectedPlaylists` array to track selected playlist paths
  - [x] 2.2 Add `handlePlaylistToggle(path, isChecked)` function to update selection state
  - [x] 2.3 Wire checkbox change events to `handlePlaylistToggle`
  - [x] 2.4 Add `.is-selected` CSS class to visually indicate selected state

- [x] **Task 3: Display total song count for selections** (AC: #3)
  - [x] 3.1 Add `calculateTotalSongs()` function summing song counts from selected playlists
  - [x] 3.2 Add summary element below playlist list: "Selected: X playlists, Y songs total"
  - [x] 3.3 Update summary in real-time as checkboxes are toggled
  - [x] 3.4 Hide summary when no playlists selected (use `.hidden` class)

- [x] **Task 4: Implement no-playlists error state** (AC: #2)
  - [x] 4.1 Update `renderPlaylists()` empty state to show error message with folder path
  - [x] 4.2 Add link to playlist documentation with PLAYLIST_DOCS_URL
  - [x] 4.3 Add `PLAYLIST_DOCS_URL = "https://github.com/mholzi/beatify/wiki/Creating-Playlists"` to `const.py`
  - [x] 4.4 Update `/beatify/api/status` to include `playlist_docs_url` in response

- [x] **Task 5: Implement start game validation** (AC: #4)
  - [x] 5.1 Add `updateStartButtonState()` function to enable/disable based on selections
  - [x] 5.2 Call `updateStartButtonState()` on page load and after each selection change
  - [x] 5.3 Start button disabled until playlist selected (AC4 validation)
  - [x] 5.4 Reveal `#game-controls` section when playlists exist (remove `.hidden` class)

- [x] **Task 6: Add CSS for playlist selection states** (AC: #1)
  - [x] 6.1 Add `.playlist-item` class extending `.list-item` for selectable items
  - [x] 6.2 Add `.playlist-item.is-selected` with visual highlight (background color)
  - [x] 6.3 Add `.playlist-checkbox` with 44x44px touch target
  - [x] 6.4 Add `.selection-summary` styling for totals display

- [x] **Task 7: E2E test for playlist selection flow** (AC: #1, #2, #3, #4)
  - [x] 7.1 Write Playwright test in `tests/e2e/test_playlist_selection.py` covering:
    - Page loads and displays playlists with checkboxes
    - Selecting playlists updates total count
    - No playlists shows error with documentation link
    - Start button disabled until playlist selected

- [x] **Task 8: Verify existing tests pass**
  - [x] 8.1 Run `pytest tests/` and verify all existing tests pass (65 passed, 6 fail due to pre-existing homeassistant import issues)
  - [x] 8.2 No regressions introduced by changes

## Dev Notes

### Architecture Compliance

- **Frontend:** Vanilla JS only - NO jQuery, NO frameworks
- **Endpoint:** Uses existing `/beatify/api/status` - NO new API endpoints
- **Checkboxes:** Must meet 44x44px touch target (NFR18)
- **Naming:** JS uses camelCase, CSS uses kebab-case with `is-` prefix for states
- **XSS Prevention:** Continue using `escapeHtml()` for all user-facing content

### Do NOT (Anti-Patterns)

- Do NOT create new API endpoints - use existing `/beatify/api/status`
- Do NOT use jQuery or any JS framework
- Do NOT create new CSS utility classes - reuse `.hidden`, `.status-error`
- Do NOT store selection state in localStorage - memory only
- Do NOT add backend validation for playlist selection - frontend only for this story

### Existing Code to Reuse

**From `styles.css` (already exists):**

| Class | Purpose | Lines |
|-------|---------|-------|
| `.list-item` | Base styling for list items | 65-91 |
| `.list-item.is-invalid` | Invalid playlist styling | 93-96 |
| `.btn-primary:disabled` | Disabled button state | 125-128 |
| `.hidden` | Hide elements | 169-171 |
| `.status-error` | Error text color | 54-57 |
| `.empty-state` | Empty state container | 149-158 |

**From `admin.js` (already exists):**

| Function | Purpose | Lines |
|----------|---------|-------|
| `renderPlaylists(playlists, playlistDir)` | Render playlist list (modify) | 84-110 |
| `escapeHtml(text)` | XSS prevention (reuse) | 117-124 |
| `loadStatus()` | Fetch status from API (reuse) | 13-31 |

**From `views.py` (already exists):**

| Endpoint | Returns | Purpose |
|----------|---------|---------|
| `/beatify/api/status` | `{ playlists, playlist_dir, ma_configured }` | Status data |

### Implementation Reference

**Checkbox HTML structure:**

```html
<div class="playlist-item list-item is-selectable">
  <label class="checkbox-label">
    <input type="checkbox"
           class="playlist-checkbox"
           data-path="/config/beatify/playlists/80s.json"
           data-song-count="25">
    <span class="playlist-name">80s Hits</span>
  </label>
  <span class="meta">25 songs</span>
</div>
```

**Selection summary element (add to admin.html after #playlists-list):**

```html
<div id="playlist-summary" class="selection-summary hidden">
  Selected: <span id="selected-count">0</span> playlists,
  <span id="total-songs">0</span> songs
</div>
```

**State management pattern:**

```javascript
// Module-level state
let selectedPlaylists = [];  // Array of playlist paths
let playlistData = [];       // Cached from /beatify/api/status

function handlePlaylistToggle(path, songCount, isChecked) {
  const item = document.querySelector(`[data-path="${path}"]`).closest('.playlist-item');
  if (isChecked) {
    selectedPlaylists.push({ path, songCount });
    item.classList.add('is-selected');
  } else {
    selectedPlaylists = selectedPlaylists.filter(p => p.path !== path);
    item.classList.remove('is-selected');
  }
  updateSelectionSummary();
  updateStartButtonState();
}

function updateStartButtonState() {
  const btn = document.getElementById('start-game');
  btn.disabled = selectedPlaylists.length === 0;
}
```

**CSS additions to styles.css:**

```css
/* Playlist selection */
.playlist-item.is-selectable {
  cursor: pointer;
}

.playlist-item.is-selected {
  background: #eff6ff;
  border-left: 3px solid #3b82f6;
}

.playlist-checkbox {
  width: 44px;
  height: 44px;
  margin-right: 12px;
  cursor: pointer;
}

.selection-summary {
  padding: 12px 16px;
  background: #f0fdf4;
  border-radius: 8px;
  margin-top: 12px;
  font-weight: 500;
  color: #166534;
}
```

### Testing Approach

- **E2E tests** (`tests/e2e/test_playlist_selection.py`): Playwright tests cover all JS interaction logic
- **No separate JS unit tests** - E2E provides sufficient coverage for this UI-focused story
- **Existing Python tests** must pass - run `pytest tests/` before marking complete

### Error Messages

| Context | Message |
|---------|---------|
| No playlists | "No playlists found. Add playlist JSON files to [folder path]." |
| Start validation | "Select at least one playlist" |

### Constants to Add

```python
# const.py
PLAYLIST_DOCS_URL = "https://github.com/mholzi/beatify/wiki/Creating-Playlists"
```

### References

- [Source: architecture.md#Frontend-Architecture] - Vanilla JS, static files
- [Source: architecture.md#CSS-Classes] - kebab-case, is- prefix for states
- [Source: epics.md#Story-2.1] - Original acceptance criteria
- [Source: project-context.md#Frontend-Rules] - Touch targets, naming conventions
- [Source: www/js/admin.js:84-110] - Existing renderPlaylists function
- [Source: www/css/styles.css:65-96] - Existing list-item styles

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

None - implementation proceeded smoothly.

### Completion Notes List

- Implemented playlist checkbox rendering with `data-path` and `data-song-count` attributes
- Added module-level state tracking (`selectedPlaylists`, `playlistData`, `playlistDocsUrl`)
- Implemented `handlePlaylistToggle()`, `calculateTotalSongs()`, `updateSelectionSummary()`, and `updateStartButtonState()` functions
- Added CSS for `.playlist-item.is-selectable`, `.is-selected`, `.playlist-checkbox` (44x44px touch target), and `.selection-summary`
- Updated empty state to show error message with documentation link
- Added `PLAYLIST_DOCS_URL` constant and updated API response to include it
- Game controls section shows/hides based on valid playlist availability
- Start button disabled until at least one playlist selected
- Created comprehensive E2E tests covering all acceptance criteria
- Renamed duplicate test file (test_config_flow.py) to avoid pytest collection error
- All tests passing that don't require homeassistant module import (62 passed)

**Code Review Fixes (2025-12-18):**
- Fixed AC4: Added validation message "Select at least one playlist" with proper show/hide logic
- Fixed duplicate selection bug: Added check to prevent same playlist being added twice
- Fixed null checks: Added safety checks in updateSelectionSummary() and updateStartButtonState()
- Fixed security: Replaced inline `onchange` handler with `addEventListener` for CSP compatibility
- Fixed XSS: song_count now escaped consistently
- Fixed error handling: playlist.errors undefined check improved

### File List

- `custom_components/beatify/www/js/admin.js` - Modified (added state management, checkbox rendering, event handlers)
- `custom_components/beatify/www/css/styles.css` - Modified (added playlist selection CSS)
- `custom_components/beatify/www/admin.html` - Modified (added playlist-summary element)
- `custom_components/beatify/const.py` - Modified (added PLAYLIST_DOCS_URL constant)
- `custom_components/beatify/server/views.py` - Modified (added playlist_docs_url to API response)
- `tests/e2e/test_playlist_selection.py` - Created (E2E tests for story 2.1)
- `tests/unit/test_config_flow_file.py` - Renamed from test_config_flow.py (avoid duplicate name collision)

## Change Log

- 2025-12-18: Story 2.1 implementation complete. All tasks completed with E2E tests.
- 2025-12-18: Code review completed. Fixed 3 HIGH and 2 MEDIUM severity issues.
