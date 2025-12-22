# Story 9.8: Beatify Brand Identity

Status: done

## Story

As a **host showing off Beatify**,
I want **a recognizable brand identity with wordmark and logo**,
So that **Beatify looks polished and memorable**.

## Acceptance Criteria

1. **Given** join screen loads
   **When** player views the page
   **Then** Beatify wordmark is prominently displayed:
   - "Beat" in white
   - "ify" in magenta-to-cyan gradient
   - Bold geometric font (Outfit or similar)
   - Subtle glow behind for hero usage

2. **Given** admin page loads
   **When** host views the page
   **Then** Beatify wordmark appears in header
   **And** matches player-side branding

3. **Given** fonts are loaded
   **When** page renders
   **Then** custom fonts load with `font-display: swap`
   **And** fonts are preloaded for critical weights only (2 weights max)
   **And** fallback to system-ui ensures no blank text

4. **Given** loading state
   **When** player waits for connection
   **Then** Beatify logo pulses subtly (not spinner)
   **And** feels premium, not generic

## Tasks / Subtasks

- [x] Task 1: Create wordmark CSS (AC: #1)
  - [x] Create `.wordmark` class with display font
  - [x] Create gradient for "ify" portion:
    ```css
    .wordmark-gradient {
      background: linear-gradient(90deg, var(--color-accent-primary), var(--color-accent-secondary));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    ```
  - [x] Add hero glow effect:
    ```css
    .wordmark-hero {
      text-shadow: 0 0 40px rgba(255, 45, 106, 0.5);
    }
    ```

- [x] Task 2: Update HTML with wordmark (AC: #1, #2)
  - [x] Add wordmark to player.html join screen:
    ```html
    <h1 class="wordmark wordmark-hero">
      <span class="wordmark-beat">Beat</span><span class="wordmark-gradient">ify</span>
    </h1>
    ```
  - [x] Add wordmark to admin.html header
  - [x] Ensure consistent sizing across pages

- [x] Task 3: Set up custom fonts (AC: #3)
  - [x] Add font-face declarations for Outfit (display) - using Google Fonts CDN
  - [x] Add font preload in HTML head (preconnect for Google Fonts)
  - [x] Limit to 2 weights maximum (700, 900)
  - [x] Ensure system-ui fallback

- [x] Task 4: Create loading state (AC: #4)
  - [x] Create `.logo-pulse` animation:
    ```css
    @keyframes logo-pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }
    .logo-loading {
      animation: logo-pulse 2s ease-in-out infinite;
    }
    ```
  - [x] Apply during connection/loading states
  - [x] Respect reduced-motion preference

- [x] Task 5: Download and add font files (AC: #3)
  - [x] Download Outfit font (or use Google Fonts) - using Google Fonts CDN
  - [x] Create `/beatify/static/fonts/` directory - not needed with CDN
  - [x] Add WOFF2 files for best compression - handled by CDN
  - [x] Update manifest if needed - not needed

## Dev Notes

### Architecture Patterns
- **Performance** - Preload critical fonts, use font-display: swap
- **Progressive enhancement** - System fonts work as fallback
- **Branding** - Consistent across all pages

### Source Tree Components
- `custom_components/beatify/www/css/styles.css` - Wordmark and font styles
- `custom_components/beatify/www/player.html` - Wordmark markup
- `custom_components/beatify/www/admin.html` - Wordmark markup
- `custom_components/beatify/www/static/fonts/` - Font files (new directory)

### Font Options
**Option 1: Self-hosted (Recommended)**
- Download Outfit from Google Fonts
- Host in /beatify/static/fonts/
- Full control, no external requests

**Option 2: Google Fonts CDN**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@700;900&display=swap" rel="stylesheet">
```
- Easier setup, relies on external CDN

### Wordmark Gradient Technique
```css
/* Gradient text requires these properties together */
.wordmark-gradient {
  background: linear-gradient(90deg, #ff2d6a, #00f5ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent; /* Fallback */
}
```

### Testing Standards
- Test font loading with slow 3G throttling
- Verify no FOIT (Flash of Invisible Text)
- Test gradient in Safari, Chrome, Firefox

### Dependencies
- **Requires Story 9.1** - CSS Custom Properties for colors

### References
- [Source: _bmad-output/ux-design-specification.md#Brand Identity]
- [Source: _bmad-output/ux-design-specification.md#Typography System]
- [Source: _bmad-output/epics.md#Story 9.8]

## Dev Agent Record

### Agent Model Used
Claude claude-opus-4-5-20251101

### Completion Notes List
- Created `.wordmark` class using Outfit font with 900 weight
- Created `.wordmark-beat` (white text) and `.wordmark-gradient` (magenta-to-cyan gradient)
- Added `.wordmark-hero` with glow text-shadow effect
- Created `.logo-loading` with pulse animation for loading state
- Added reduced motion support for logo pulse
- Added light theme override for wordmark-beat (dark text for admin page)
- Updated player.html with Google Fonts CDN preconnect and Outfit font (700, 900 weights)
- Updated admin.html with same font setup
- Added wordmark to loading view, join view in player.html
- Added wordmark to header in admin.html
- Used Google Fonts CDN instead of self-hosted for simplicity

### File List
- `custom_components/beatify/www/css/styles.css`
- `custom_components/beatify/www/player.html`
- `custom_components/beatify/www/admin.html`
- Note: Using Google Fonts CDN - no local fonts directory needed
