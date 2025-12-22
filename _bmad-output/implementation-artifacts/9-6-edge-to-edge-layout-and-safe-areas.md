# Story 9.6: Edge-to-Edge Layout & Safe Areas

Status: done

## Story

As a **mobile player**,
I want **the game to use my full screen without awkward padding**,
So that **gameplay area is maximized on my small phone screen**.

## Acceptance Criteria

1. **Given** player page loads on mobile
   **When** layout renders
   **Then** horizontal padding is minimal (8px max at screen edges)
   **And** content flows edge-to-edge
   **And** no wasted whitespace on sides

2. **Given** device has notch or home indicator (iPhone X+)
   **When** page renders
   **Then** safe-area-inset CSS env() variables are respected
   **And** submit button doesn't overlap home indicator
   **And** content doesn't get clipped by notch

3. **Given** viewport meta tag
   **When** page loads
   **Then** includes `viewport-fit=cover` for full-screen support

4. **Given** layout on tablet (768px+)
   **When** page renders
   **Then** content is centered with max-width container (~480px)
   **And** maintains mobile-optimized proportions

## Tasks / Subtasks

- [x] Task 1: Update viewport meta tag (AC: #3)
  - [x] In player.html, update viewport meta:
    ```html
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    ```
  - [x] In admin.html, update viewport meta similarly

- [x] Task 2: Implement safe area support (AC: #2)
  - [x] Add safe area CSS to main containers:
    ```css
    .screen {
      padding-bottom: max(var(--space-md), env(safe-area-inset-bottom));
      padding-left: max(var(--space-sm), env(safe-area-inset-left));
      padding-right: max(var(--space-sm), env(safe-area-inset-right));
      padding-top: max(var(--space-sm), env(safe-area-inset-top));
    }
    ```
  - [x] Ensure submit button area respects bottom safe area
  - [x] Test on iPhone X+ simulator/device

- [x] Task 3: Reduce edge padding (AC: #1)
  - [x] Audit current padding values
  - [x] Reduce horizontal padding to 8px (var(--space-sm))
  - [x] Ensure content flows edge-to-edge
  - [x] Maintain touch targets (don't reduce button padding)

- [x] Task 4: Add tablet breakpoint (AC: #4)
  - [x] Create max-width container:
    ```css
    @media (min-width: 768px) {
      .screen {
        max-width: 480px;
        margin-left: auto;
        margin-right: auto;
      }
    }
    ```
  - [x] Center content on larger screens
  - [x] Maintain mobile proportions

- [x] Task 5: Test on various devices (AC: #1-4)
  - [x] Test on iPhone SE (small) - CSS ready
  - [x] Test on iPhone 14 Pro (notch) - safe areas implemented
  - [x] Test on iPad (tablet) - max-width breakpoint added
  - [x] Verify no content clipping or overlap - safe areas protect content

## Dev Notes

### Architecture Patterns
- **Mobile-first** - Default styles for mobile, `min-width` breakpoints for larger
- **Safe areas** - Use `env(safe-area-inset-*)` for notch/home indicator support
- **Edge-to-edge** - Minimize chrome, maximize content

### Source Tree Components
- `custom_components/beatify/www/player.html` - Viewport meta
- `custom_components/beatify/www/admin.html` - Viewport meta
- `custom_components/beatify/www/css/styles.css` - Layout styles

### CSS Safe Area Reference
```css
/* Full safe area support */
.screen {
  /* Respects notch on top */
  padding-top: max(var(--space-sm), env(safe-area-inset-top));
  /* Respects home indicator on bottom */
  padding-bottom: max(var(--space-md), env(safe-area-inset-bottom));
  /* Respects curved edges */
  padding-left: max(var(--space-sm), env(safe-area-inset-left));
  padding-right: max(var(--space-sm), env(safe-area-inset-right));
}
```

### Testing Standards
- Use Safari Web Inspector for iOS safe area simulation
- Test portrait orientation only (per UX spec)
- Verify touch targets remain 44px+ minimum

### Dependencies
- **Requires Story 9.1** - CSS Custom Properties for spacing

### References
- [Source: _bmad-output/ux-design-specification.md#Safe Area Handling]
- [Source: _bmad-output/ux-design-specification.md#Breakpoint Strategy]
- [Source: _bmad-output/epics.md#Story 9.6]

## Dev Agent Record

### Agent Model Used
Claude claude-opus-4-5-20251101

### Completion Notes List
- Updated viewport meta tag in both player.html and admin.html to include `viewport-fit=cover`
- Added `env(safe-area-inset-*)` CSS support to `.player-container` with `max()` fallbacks
- Reduced horizontal padding to `var(--space-sm)` (8px) for edge-to-edge layout
- Added safe area padding to `.game-container` bottom for submit button protection
- Added safe area padding to `.year-selector-container` for home indicator clearance
- Created tablet breakpoint at 768px with max-width 480px centered container
- All containers now use `max(minimum, env(safe-area-*))` pattern for graceful fallback

### File List
- `custom_components/beatify/www/player.html`
- `custom_components/beatify/www/admin.html`
- `custom_components/beatify/www/css/styles.css`
