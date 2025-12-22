# Story 9.7: Accessibility & Reduced Motion

Status: done

## Story

As a **player with accessibility needs**,
I want **the game to be usable with reduced motion preferences and proper contrast**,
So that **I can enjoy the party game like everyone else**.

## Acceptance Criteria

1. **Given** user has `prefers-reduced-motion: reduce` set
   **When** any animation would play
   **Then** animations are disabled
   **And** state changes remain instant (color changes, etc.)
   **And** confetti shows as static celebration icon instead

2. **Given** user has `prefers-color-scheme: light` set
   **When** page renders
   **Then** Day Mode fallback applies:
   - Background: `#ffffff`
   - Surface: `#f5f5f7`
   - Text: `#1a1a1a`
   - Accents remain vibrant (magenta/cyan)

3. **Given** focus is on interactive elements
   **When** using keyboard navigation
   **Then** focus indicator is visible (magenta glow ring, 2px offset)
   **And** focus never gets "lost" on dark backgrounds

4. **Given** timer changes state
   **When** screen reader is active
   **Then** ARIA live region announces time remaining at key moments
   **And** state changes are announced ("10 seconds remaining", "5 seconds!")

5. **Given** all text on dark backgrounds
   **When** contrast is measured
   **Then** all combinations exceed WCAG AA (4.5:1 minimum)
   **And** muted text (`#b3b3c2`) on `#0a0a12` passes ratio check

## Tasks / Subtasks

- [x] Task 1: Implement reduced motion support (AC: #1)
  - [x] Add global reduced motion query:
    ```css
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }
    ```
  - [x] Create static confetti fallback (celebration icon)
  - [x] Ensure color state changes still apply

- [x] Task 2: Implement Day Mode fallback (AC: #2)
  - [x] Add light mode CSS variables:
    ```css
    @media (prefers-color-scheme: light) {
      :root {
        --color-bg-primary: #ffffff;
        --color-bg-surface: #f5f5f7;
        --color-text-primary: #1a1a1a;
        --color-text-muted: #666666;
        /* Accents remain unchanged */
      }
    }
    ```
  - [x] Test all screens in light mode
  - [x] Verify text remains readable

- [x] Task 3: Add focus indicators (AC: #3)
  - [x] Create focus ring style:
    ```css
    :focus-visible {
      outline: 2px solid var(--color-accent-primary);
      outline-offset: 2px;
    }
    ```
  - [x] Ensure all interactive elements receive focus
  - [x] Test keyboard navigation through all screens

- [x] Task 4: Add ARIA live regions for timer (AC: #4)
  - [x] Add `aria-live="polite"` to timer container
  - [x] Add `aria-label` for timer value
  - [x] Announce at 10 seconds: "10 seconds remaining"
  - [x] Announce at 5 seconds: "5 seconds!"
  - [x] Consider `role="timer"` for screen readers

- [x] Task 5: Verify contrast compliance (AC: #5)
  - [x] Check all text/background combinations
  - [x] Verify #b3b3c2 on #0a0a12 (verified: 9.52:1 in Story 9.2)
  - [x] Verify #8b8b9e on #0a0a12 (should be ~5.5:1)
  - [x] Document any adjustments needed (none - all pass)
  - [x] Use WebAIM contrast checker or similar

## Dev Notes

### Architecture Patterns
- **Progressive enhancement** - Animations enhance but aren't required
- **System preferences** - Respect OS-level accessibility settings
- **WCAG 2.1 AA** - Target compliance level

### Source Tree Components
- `custom_components/beatify/www/css/styles.css` - All accessibility CSS
- `custom_components/beatify/www/player.html` - ARIA attributes
- `custom_components/beatify/www/js/player.js` - Timer announcements

### ARIA Implementation for Timer
```html
<div class="timer" role="timer" aria-live="polite" aria-label="Time remaining">
  <span aria-atomic="true">30</span>
</div>
```

```javascript
// In player.js
function updateTimerAria(seconds) {
  if (seconds === 10) {
    timerElement.setAttribute('aria-label', '10 seconds remaining');
  } else if (seconds === 5) {
    timerElement.setAttribute('aria-label', '5 seconds!');
  }
}
```

### Contrast Verification Checklist
| Text Color | Background | Required | Actual |
|------------|------------|----------|--------|
| #ffffff | #0a0a12 | 4.5:1 | 20.1:1 ✓ |
| #b3b3c2 | #0a0a12 | 4.5:1 | 7.5:1 ✓ |
| #8b8b9e | #0a0a12 | 4.5:1 | 5.5:1 ✓ |
| #ff2d6a | #0a0a12 | 4.5:1 | 5.8:1 ✓ |

### Testing Standards
- Test with VoiceOver (iOS) and NVDA/JAWS (desktop)
- Test with prefers-reduced-motion enabled
- Test with prefers-color-scheme: light
- Keyboard-only navigation test

### Dependencies
- **Requires Story 9.1** - CSS Custom Properties
- **Requires Story 9.3** - Timer states (for ARIA integration)

### References
- [Source: _bmad-output/ux-design-specification.md#Accessibility Standards]
- [Source: _bmad-output/ux-design-specification.md#Reduced Motion Support]
- [Source: _bmad-output/epics.md#Story 9.7]

## Dev Agent Record

### Agent Model Used
Claude claude-opus-4-5-20251101

### Completion Notes List
- Added global reduced motion query that disables all animations via `!important`
- Static confetti fallback already implemented in Story 9.4 (showStaticCelebration function)
- Added Day Mode fallback CSS for `prefers-color-scheme: light` users
- Added `:focus-visible` focus ring styles with magenta accent and box-shadow for dark theme
- Added `:focus:not(:focus-visible)` to remove outline for mouse users
- Added `.sr-only` utility class for screen reader only content
- Added `.skip-link` for keyboard navigation (optional use)
- Updated timer in player.html with `role="timer"`, `aria-live="polite"`, and `aria-label`
- Updated JavaScript to announce timer at 10s, 5s, and 0s via aria-label changes
- Contrast verified in Story 9.2: muted text (#b3b3c2) on dark bg (#0a0a12) = 9.52:1 (PASS)

### File List
- `custom_components/beatify/www/css/styles.css`
- `custom_components/beatify/www/player.html`
- `custom_components/beatify/www/js/player.js`
