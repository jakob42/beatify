# Story 9.4: Celebration-First Reveal Experience

Status: done

## Story

As a **player**,
I want **the reveal to lead with emotion before showing data**,
So that **getting the answer feels theatrical and satisfying**.

## Acceptance Criteria

1. **Given** round ends and reveal displays
   **When** player got exact match (0 years off)
   **Then** "NAILED IT!" text displays prominently in green
   **And** confetti animation triggers (canvas or CSS particles)
   **And** correct year displays with glow effect
   **And** after 1 second, score breakdown fades in

2. **Given** round ends and reveal displays
   **When** player was close (within 2 years)
   **Then** "SO CLOSE!" text displays in orange
   **And** near-miss animation plays (shake or pulse)
   **And** difference shown: "Off by 2 years"

3. **Given** round ends and reveal displays
   **When** player was way off (>5 years)
   **Then** playful "Oops!" text displays in muted gray
   **And** exaggerated distance shown humorously
   **And** no shame messaging—keep it light

4. **Given** player did not submit
   **When** reveal displays
   **Then** "No guess" displays neutrally
   **And** no celebration or commiseration animation

5. **Given** confetti animation exists
   **When** triggered
   **Then** uses canvas or CSS-only implementation (no heavy libraries)
   **And** respects `prefers-reduced-motion` (static icon fallback)
   **And** auto-clears after 2-3 seconds

## Tasks / Subtasks

- [x] Task 1: Create reveal emotion text styles (AC: #1, #2, #3)
  - [x] Create `.reveal-emotion` base class (large, centered)
  - [x] Create `.reveal-emotion--exact` (green, glow)
  - [x] Create `.reveal-emotion--close` (orange)
  - [x] Create `.reveal-emotion--wrong` (muted gray)
  - [x] Create `.reveal-emotion--missed` (neutral gray)

- [x] Task 2: Create confetti system (AC: #1, #5)
  - [x] Implement lightweight CSS/canvas confetti
  - [x] Trigger on exact match only
  - [x] Auto-clear after 2-3 seconds
  - [x] Option 1 - CSS particles:
    ```css
    .confetti-particle {
      position: fixed;
      width: 10px;
      height: 10px;
      animation: confetti-fall 2s ease-out forwards;
    }
    ```
  - [x] Option 2 - Canvas implementation for better performance (selected)

- [x] Task 3: Create reveal animations (AC: #1, #2)
  - [x] Fade-in animation for score breakdown (1s delay)
  - [x] Near-miss shake/pulse animation
  - [x] Year glow effect on exact match:
    ```css
    .reveal-year--exact {
      text-shadow: 0 0 20px var(--color-success);
      animation: reveal-glow 0.5s ease-out;
    }
    ```

- [x] Task 4: Update reveal logic in player.js (AC: #1-4)
  - [x] Determine result category (exact, close, wrong, missed)
  - [x] Apply appropriate emotion class
  - [x] Trigger confetti for exact match
  - [x] Delay score breakdown display by 1s

- [x] Task 5: Add reduced motion support (AC: #5)
  - [x] Replace confetti with static celebration icon
  - [x] Disable shake/pulse animations
  - [x] Keep color changes and text

- [x] Task 6: Update reveal section HTML structure (AC: #1-4)
  - [x] Add emotion text container
  - [x] Add year display with glow capability
  - [x] Add score breakdown with fade-in support

## Dev Notes

### Architecture Patterns
- **Emotion-first reveal** - Show emotion text before data
- **Progressive disclosure** - Fade in details after initial impact
- **Performance** - Use CSS animations, avoid heavy JS libraries

### Source Tree Components
- `custom_components/beatify/www/css/styles.css` - Reveal styles, confetti CSS
- `custom_components/beatify/www/js/player.js` - Reveal logic, confetti trigger
- `custom_components/beatify/www/player.html` - Reveal section structure

### Result Categories
```javascript
// In player.js
const diff = Math.abs(guess - correctYear);
if (diff === 0) return 'exact';      // NAILED IT!
if (diff <= 2) return 'close';       // SO CLOSE!
if (diff > 5) return 'wrong';        // Oops!
return 'close';                       // 3-5 years = still close
```

### Testing Standards
- Test all reveal states: exact, close (1-2), close (3-5), wrong (>5), no guess
- Verify confetti triggers only on exact match
- Test with prefers-reduced-motion enabled

### Dependencies
- **Requires Story 9.1** - CSS Custom Properties for colors
- **Requires Story 9.2** - Theme foundation

### References
- [Source: _bmad-output/ux-design-specification.md#Celebration-First Reveal]
- [Source: _bmad-output/ux-design-specification.md#Emotional Journey Map]
- [Source: _bmad-output/epics.md#Story 9.4]

## Dev Agent Record

### Agent Model Used
Claude claude-opus-4-5-20251101

### Completion Notes List
- Added reveal emotion container and confetti canvas to player.html
- Created `.reveal-emotion` CSS with modifiers for exact/close/wrong/missed states
- Implemented entrance animation with scale and fade
- Added shake animation for near-miss reveals
- Created lightweight canvas-based confetti system (~130 lines JS)
- Confetti uses magenta/cyan/green/yellow/orange party colors
- Auto-clears after 3 seconds
- Added `showRevealEmotion()` function to determine and display emotion category
- Categories: exact (0 off), close (1-5 off), wrong (>5 off), missed (no guess)
- Score breakdown uses `is-delayed` class with 1s fade-in animation
- Reduced motion support: confetti replaced with static celebration icon, animations disabled
- Dark theme styles added for neon glow effects on emotion text

### File List
- `custom_components/beatify/www/css/styles.css`
- `custom_components/beatify/www/js/player.js`
- `custom_components/beatify/www/player.html`
