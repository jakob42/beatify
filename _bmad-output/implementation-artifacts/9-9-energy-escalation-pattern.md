# Story 9.9: Energy Escalation Pattern

Status: done

## Story

As a **party guest**,
I want **visual energy to build from calm join to exciting gameplay**,
So that **the experience matches the emotional journey of the game**.

## Acceptance Criteria

1. **Given** player is on join screen
   **When** page renders
   **Then** energy is **calm**:
   - Minimal elements (logo, name field, button)
   - No animations or glows
   - Clean, focused entry point

2. **Given** player is in lobby
   **When** waiting for game to start
   **Then** energy is **warming up**:
   - Player cards slide in with subtle animation
   - QR code pulses gently
   - Background may have subtle particle effect

3. **Given** player is in active gameplay
   **When** round is in progress
   **Then** energy is **full party**:
   - Timer glows in critical states
   - Submit button has active glow on hover
   - Album art has subtle ambient glow
   - Reveal has full celebration treatment

4. **Given** screen transitions happen
   **When** moving between phases
   **Then** transitions are smooth (fade or slide)
   **And** feel cohesive, not jarring
   **And** respect `prefers-reduced-motion`

## Tasks / Subtasks

- [x] Task 1: Define energy level classes (AC: #1, #2, #3)
  - [x] Create `.energy-calm` class (join screen defaults)
  - [x] Create `.energy-warmup` class (lobby enhancements)
  - [x] Create `.energy-party` class (gameplay full effects)
  - [x] Apply classes to body or main container based on phase

- [x] Task 2: Style calm join screen (AC: #1)
  - [x] Ensure join screen has minimal elements
  - [x] Remove any existing animations on join
  - [x] Clean, focused layout (btn-glow hover disabled in calm mode)

- [x] Task 3: Add lobby warm-up animations (AC: #2)
  - [x] Create player card slide-in animation (energy-slide-in)
  - [x] Add subtle QR code pulse (energy-pulse-subtle)
  - [x] Optional: subtle background particle effect (skipped for performance)

- [x] Task 4: Enable full party mode during gameplay (AC: #3)
  - [x] Enable all glow effects (already in 9.2, 9.3)
  - [x] Add ambient glow to album art (box-shadow on .album-cover)
  - [x] Ensure submit button glow is active
  - [x] Full celebration treatment on reveal (from 9.4)

- [x] Task 5: Add screen transitions (AC: #4)
  - [x] Create transition utility classes (screen-fade-in on .view)
  - [x] Apply transitions when changing screens
  - [x] Respect prefers-reduced-motion (via global reduced-motion query from 9.7)

- [x] Task 6: Update player.js for energy phases (AC: #1-4)
  - [x] Track current energy level
  - [x] Update body class based on game phase via setEnergyLevel()

## Dev Notes

### Architecture Patterns
- **Progressive enhancement** - Effects layer on top of functional base
- **CSS classes** - Energy levels applied via body class
- **Phase-aware** - JS tracks game phase to update energy

### Source Tree Components
- `custom_components/beatify/www/css/styles.css` - Energy level styles
- `custom_components/beatify/www/js/player.js` - Energy level logic

### Energy Level Map
| Game Phase | Energy Level | Key Visual Treatment |
|------------|--------------|---------------------|
| Join | calm | Minimal, logo focus, clean input |
| Lobby | warmup | Cards slide in, QR pulses |
| Playing | party | Timer glows, slider active |
| Reveal | party | Confetti, celebration |
| End | warmup | Final leaderboard, lower energy |

### Screen Transition Timing
- Fade duration: 300ms
- Slide duration: 400ms
- Use `ease-out` for natural feel

### Testing Standards
- Walk through full game flow, verify energy progression
- Test transitions between all phases
- Verify reduced-motion disables animations

### Dependencies
- **Requires Story 9.1** - CSS Custom Properties
- **Requires Story 9.2** - Theme and glow classes
- **Requires Story 9.3** - Timer glow (party mode)
- **Requires Story 9.4** - Reveal celebration (party mode)

### References
- [Source: _bmad-output/ux-design-specification.md#Energy Escalation Pattern]
- [Source: _bmad-output/ux-design-specification.md#Screen Energy Map]
- [Source: _bmad-output/epics.md#Story 9.9]

## Dev Agent Record

### Agent Model Used
Claude claude-opus-4-5-20251101

### Completion Notes List
- Created CSS for three energy levels: calm, warmup, party
- `.energy-calm` disables btn-glow hover effects for minimal distraction
- `.energy-warmup` adds slide-in animations for player cards and pulse for QR container
- `.energy-party` adds ambient glow to album art and active submit button glow
- Added `screen-fade-in` animation applied to all `.view` elements for smooth transitions
- Created `@keyframes energy-slide-in` and `@keyframes energy-pulse-subtle` animations
- Created `setEnergyLevel()` function in player.js to toggle body classes
- Integrated energy level changes with all phase transitions:
  - join/loading/not-found/ended/in-progress/connection-lost → calm
  - lobby → warmup
  - playing/reveal → party
  - paused/end → warmup
- Reduced motion already handled by Story 9.7 global query

### Code Review Fixes (Epic 9 Review)
- Fixed: Added `connection-lost-view` to calm energy list
- Fixed: Corrected CSS variable `--z-index-modal` → `--z-modal` (2 occurrences)
- Fixed: Added `aria-live="polite"` to reveal-emotion container for accessibility
- Fixed: Updated Story 9-8 file list to remove non-existent fonts directory
- Fixed: Synced sprint-status.yaml with all Epic 9 story statuses

### File List
- `custom_components/beatify/www/css/styles.css`
- `custom_components/beatify/www/js/player.js`
