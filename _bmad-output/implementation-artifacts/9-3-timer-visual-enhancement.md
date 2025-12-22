# Story 9.3: Timer Visual Enhancement

Status: done

## Story

As a **player**,
I want **the countdown timer to build tension with visual urgency cues**,
So that **the final seconds feel exciting, not stressful**.

## Acceptance Criteria

1. **Given** timer is counting down
   **When** time > 10 seconds (normal state)
   **Then** timer displays in white text, no special effects

2. **Given** timer reaches 10 seconds
   **When** warning state triggers
   **Then** timer text turns orange (`#ff6600`)
   **And** subtle pulse animation begins (opacity 0.8→1.0)

3. **Given** timer reaches 5 seconds
   **When** critical state triggers
   **Then** timer text turns red (`#ff0040`)
   **And** glow effect activates (`box-shadow: 0 0 30px #ff0040`)
   **And** scale animation adds slight size increase on each second
   **And** pulse animation intensifies

4. **Given** user has `prefers-reduced-motion: reduce`
   **When** timer enters warning/critical states
   **Then** color changes apply but animations are disabled
   **And** glow remains static (no pulse)

5. **Given** timer component
   **When** CSS classes are applied
   **Then** these state classes exist:
   - `.timer` (base styles)
   - `.timer--warning` (orange, subtle pulse)
   - `.timer--critical` (red, glow, intense pulse, scale)

## Tasks / Subtasks

- [x] Task 1: Create timer base styles (AC: #1, #5)
  - [x] Define `.timer` base class with display font, white color
  - [x] Set font-size to `var(--font-size-timer)` (64px)
  - [x] Center alignment, proper spacing

- [x] Task 2: Create warning state (AC: #2, #5)
  - [x] Define `.timer--warning` class
  - [x] Set color to `var(--color-warning)` (#ff6600)
  - [x] Add subtle pulse animation:
    ```css
    @keyframes timer-pulse-subtle {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.8; }
    }
    .timer--warning {
      color: var(--color-warning);
      animation: timer-pulse-subtle 1s ease-in-out infinite;
    }
    ```

- [x] Task 3: Create critical state (AC: #3, #5)
  - [x] Define `.timer--critical` class
  - [x] Set color to `var(--color-error)` (#ff0040)
  - [x] Add glow effect: `box-shadow: 0 0 30px var(--color-error)`
  - [x] Add intense pulse with scale:
    ```css
    @keyframes timer-pulse-intense {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.9; transform: scale(1.05); }
    }
    .timer--critical {
      color: var(--color-error);
      box-shadow: 0 0 30px var(--color-error);
      animation: timer-pulse-intense 0.5s ease-in-out infinite;
    }
    ```

- [x] Task 4: Add reduced motion support (AC: #4)
  - [x] Wrap animations in `@media (prefers-reduced-motion: no-preference)`
  - [x] Or disable via reduced-motion query:
    ```css
    @media (prefers-reduced-motion: reduce) {
      .timer--warning,
      .timer--critical {
        animation: none;
      }
    }
    ```

- [x] Task 5: Update player.js timer logic (AC: #2, #3)
  - [x] Add state class logic in timer update function (already implemented)
  - [x] At 10 seconds: add `.timer--warning`, remove others
  - [x] At 5 seconds: add `.timer--critical`, remove `.timer--warning`
  - [x] Above 10 seconds: remove all state classes

## Dev Notes

### Architecture Patterns
- **CSS State Classes** - Use modifier pattern `--warning`, `--critical`
- **JavaScript** - Use `camelCase` for variables (per project conventions)
- **Animation** - GPU-accelerated properties only (transform, opacity)

### Source Tree Components
- `custom_components/beatify/www/css/styles.css` - Timer CSS classes
- `custom_components/beatify/www/js/player.js` - Timer state logic

### Testing Standards
- Test timer countdown from 30 → 0
- Verify state transitions at 10s and 5s thresholds
- Test with `prefers-reduced-motion: reduce` enabled

### Dependencies
- **Requires Story 9.1** - CSS Custom Properties for color tokens

### References
- [Source: _bmad-output/ux-design-specification.md#Component Strategy - Timer States]
- [Source: _bmad-output/epics.md#Story 9.3]
- [Source: _bmad-output/project-context.md#Frontend Rules]

## Dev Agent Record

### Agent Model Used
Claude claude-opus-4-5-20251101

### Completion Notes List
- Enhanced timer CSS with proper animations per story specs
- Added `timer-pulse-subtle` keyframe animation (opacity 0.8→1.0, 1s duration) for warning state
- Added `timer-pulse-intense` keyframe animation (opacity 0.9→1.0, scale 1→1.05, 0.5s duration) for critical state
- Added box-shadow glow effect to critical state
- Applied matching animations to dark theme overrides with neon text-shadows
- Added `@media (prefers-reduced-motion: reduce)` to disable animations for accessibility
- JavaScript timer logic already implemented correctly (lines 319-335 in player.js)

### File List
- `custom_components/beatify/www/css/styles.css`
- `custom_components/beatify/www/js/player.js`
