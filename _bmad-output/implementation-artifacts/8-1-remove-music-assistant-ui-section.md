# Story 8.1: Remove Music Assistant UI Section

Status: done

## Story

As a **user**,
I want **the obsolete Music Assistant section removed from the admin page**,
so that **the UI is clean and doesn't show irrelevant configuration options**.

## Acceptance Criteria

1. **Given** the admin page loads **When** the page renders **Then** no "Music Assistant" section is displayed
2. **Given** the admin.js code **When** reviewed **Then** `'ma-status'` is removed from `setupSections` array
3. **Given** the admin.js code **When** reviewed **Then** `renderMAStatus()` function is removed
4. **Given** the admin.js code **When** reviewed **Then** call to `renderMAStatus()` in `loadStatus()` is removed
5. **Given** the backend status API **When** called **Then** MA-related fields are no longer needed (optional cleanup)

## Tasks / Subtasks

- [x] Task 1: Remove MA section from HTML (AC: 1)
  - [x] Remove `<section id="ma-status">...</section>` from admin.html (lines 15-18)

- [x] Task 2: Clean up admin.js (AC: 2, 3, 4)
  - [x] Remove `'ma-status'` from `setupSections` array (line 19)
  - [x] Remove `renderMAStatus()` function definition (lines 75-89)
  - [x] Remove `renderMAStatus(status.ma_configured, status.ma_setup_url);` call in `loadStatus()` (line 52)

- [x] Task 3: Optional backend cleanup (AC: 5)
  - [x] Verified: Status API already doesn't return ma_configured/ma_setup_url (no changes needed)

## Dev Notes

### Current Code Analysis

**admin.html (lines 15-18):**
```html
<section id="ma-status" class="status-section">
    <h2>Music Assistant</h2>
    <div id="ma-status-content">Loading...</div>
</section>
```

**admin.js (line 19):**
```javascript
const setupSections = ['ma-status', 'media-players', 'playlists', 'game-controls'];
```

**admin.js (line 52 in loadStatus):**
```javascript
renderMAStatus(status.ma_configured, status.ma_setup_url);
```

**admin.js (lines 75-89):**
```javascript
function renderMAStatus(isConfigured, setupUrl) {
    const container = document.getElementById('ma-status-content');
    if (isConfigured) {
        container.innerHTML = '<span class="status-connected">✓ Connected</span>';
    } else {
        container.innerHTML = `...setup guide HTML...`;
    }
}
```

**views.py StatusView - Note:** The status API doesn't currently return `ma_configured` or `ma_setup_url`. The admin.js references these but they appear to be legacy/unused.

### File Locations

| File | Path | Lines to Modify |
|------|------|-----------------|
| admin.html | `custom_components/beatify/www/admin.html` | 15-18 (remove section) |
| admin.js | `custom_components/beatify/www/js/admin.js` | 19, 52, 75-89 |

### Testing

- Load admin page and verify no "Music Assistant" section appears
- Verify page still functions correctly (media players, playlists, game creation)
- Check browser console for no JS errors

### References

- [Source: epics.md#Story 8.1]
- [Source: project-context.md#Frontend Rules]

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5

### Debug Log References
N/A

### Completion Notes List
- Removed MA section from admin.html (lines 15-18)
- Removed 'ma-status' from setupSections array in admin.js
- Removed renderMAStatus() function definition from admin.js
- Removed renderMAStatus() call from loadStatus() in admin.js
- Updated error message container to media-players-list instead of ma-status-content
- Verified backend StatusView doesn't return MA-related fields

### File List
- custom_components/beatify/www/admin.html
- custom_components/beatify/www/js/admin.js
