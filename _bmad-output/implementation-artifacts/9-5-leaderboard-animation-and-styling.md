# Story 9.5: Leaderboard Animation & Styling

Status: done

## Story

As a **player**,
I want **the leaderboard to feel alive with rank change animations**,
So that **competition feels dynamic, not like a static spreadsheet**.

## Acceptance Criteria

1. **Given** leaderboard updates after a round
   **When** player's rank changes
   **Then** row animates to new position (slide up or down)
   **And** up arrow (▲) or down arrow (▼) indicator shows briefly
   **And** animation completes in 300-500ms

2. **Given** leaderboard displays
   **When** current player views their row
   **Then** their row is highlighted (accent border or background)
   **And** easy to find at a glance

3. **Given** many players in game (>10)
   **When** leaderboard displays
   **Then** smart compression applies:
   - Top 5 shown fully
   - "..." separator
   - Current player's position (if not in top 5): "**You (#14)**"
   - "..." separator
   - Bottom 3 shown
   **And** list is scrollable for full view

4. **Given** streak indicator displays
   **When** player has active streak
   **Then** streak badge shows (e.g., "🔥3")
   **And** badge has subtle glow if streak ≥5

5. **Given** final leaderboard displays (game end)
   **When** top 3 are shown
   **Then** podium-style treatment with larger text/glow
   **And** 1st place gets gold accent, 2nd silver, 3rd bronze

## Tasks / Subtasks

- [x] Task 1: Create leaderboard row styles (AC: #2)
  - [x] Create `.leaderboard-row` base class (existing as `.leaderboard-entry`)
  - [x] Create `.leaderboard-row--you` for current player highlight (existing as `.is-current`)
  - [x] Add accent border or background for "you" row
  - [x] Ensure row is visually distinct

- [x] Task 2: Implement rank change animations (AC: #1)
  - [x] Track previous rank for each player (server provides rank_change)
  - [x] Add `.leaderboard-entry--climbing` class (slide up)
  - [x] Add `.leaderboard-entry--falling` class (slide down)
  - [x] Add rank change indicator (▲/▼):
    ```css
    .rank-change--up::after { content: '▲'; color: var(--color-success); }
    .rank-change--down::after { content: '▼'; color: var(--color-error); }
    ```
  - [x] Animation duration 300-500ms (400ms)

- [x] Task 3: Implement smart compression (AC: #3)
  - [x] Detect player count > 10
  - [x] Render top 5, separator, current player, separator, bottom 3
  - [x] Add "..." separator styling
  - [x] Make full list scrollable
  - [x] Bold "You (#14)" display for current player

- [x] Task 4: Style streak badges (AC: #4)
  - [x] Create `.streak-indicator` class
  - [x] Add glow for streak ≥5:
    ```css
    .streak-indicator--hot {
      text-shadow: 0 0 10px var(--color-warning);
    }
    ```
  - [x] Format as "🔥3" or similar

- [x] Task 5: Create podium styles for final leaderboard (AC: #5)
  - [x] Create `.is-top-1`, `.is-top-2`, `.is-top-3` classes
  - [x] Gold accent for 1st: `color: #ffd700`
  - [x] Silver accent for 2nd: `color: #c0c0c0`
  - [x] Bronze accent for 3rd: `color: #cd7f32`
  - [x] Larger text/glow for podium positions (dark theme)

- [x] Task 6: Update player.js leaderboard rendering (AC: #1-5)
  - [x] Add rank change detection logic
  - [x] Implement smart compression logic (compressLeaderboard function)
  - [x] Apply appropriate classes on render
  - [x] Handle final leaderboard variant

## Dev Notes

### Architecture Patterns
- **Animation** - CSS transitions for smooth movement
- **State management** - Track previous ranks to detect changes
- **Progressive enhancement** - Basic leaderboard works without animation

### Source Tree Components
- `custom_components/beatify/www/css/styles.css` - Leaderboard styles
- `custom_components/beatify/www/js/player.js` - Leaderboard logic

### Smart Compression Algorithm
```javascript
function compressLeaderboard(players, currentPlayerName) {
  if (players.length <= 10) return players; // No compression needed

  const top5 = players.slice(0, 5);
  const bottom3 = players.slice(-3);
  const currentIdx = players.findIndex(p => p.name === currentPlayerName);

  // If current player in top 5 or bottom 3, no middle section
  if (currentIdx < 5 || currentIdx >= players.length - 3) {
    return [...top5, { separator: true }, ...bottom3];
  }

  // Show current player in middle
  return [
    ...top5,
    { separator: true },
    { ...players[currentIdx], isYou: true },
    { separator: true },
    ...bottom3
  ];
}
```

### Testing Standards
- Test with 5, 10, 15, 20 players
- Verify rank change animations on score updates
- Test final leaderboard podium display

### Dependencies
- **Requires Story 9.1** - CSS Custom Properties
- **Requires Story 9.2** - Theme foundation

### References
- [Source: _bmad-output/ux-design-specification.md#Scalability Patterns]
- [Source: _bmad-output/epics.md#Story 9.5]
- [Source: _bmad-output/epics.md#Story 5.5 - Live Leaderboard]

## Dev Agent Record

### Agent Model Used
Claude claude-opus-4-5-20251101

### Completion Notes List
- Added `.leaderboard-entry--climbing` and `--falling` animation classes with 400ms slide animations
- Created dark theme variants with neon-colored backgrounds (green/magenta)
- Enhanced rank change indicators (▲/▼) with text-shadow glow in dark theme
- Added `.streak-indicator--hot` class with pulsing glow animation for streaks ≥5
- Created `.leaderboard-separator` for smart compression display
- Implemented `compressLeaderboard()` function for >10 players (top 5, separator, you, separator, bottom 3)
- Enhanced dark theme top 3 styling with gold/silver/bronze colors and text shadows
- Added reduced motion support to disable animations
- Updated updateLeaderboard() to apply animation classes based on rank_change

### File List
- `custom_components/beatify/www/css/styles.css`
- `custom_components/beatify/www/js/player.js`
