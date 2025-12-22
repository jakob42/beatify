# Story 9.1: CSS Custom Properties Foundation

Status: done

## Story

As a **developer**,
I want **all hardcoded colors, spacing, typography, and effects extracted into CSS custom properties**,
So that **the design system is maintainable and theming is possible**.

## Acceptance Criteria

1. **Given** the current `styles.css` (~2400 lines)
   **When** refactored
   **Then** all color values are replaced with semantic custom properties in `:root`

2. **Given** spacing values are scattered throughout CSS
   **When** refactored
   **Then** all spacing uses custom properties (`--space-xs` through `--space-xl`)

3. **Given** typography is inconsistent
   **When** refactored
   **Then** typography uses custom properties for font families and sizes

4. **Given** glow effects are used
   **When** defined
   **Then** effects are reusable via `--glow-primary`, `--glow-success`, etc.

5. **Given** border radius values exist
   **When** refactored
   **Then** all radius values use `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-full`

6. **Given** transitions are used
   **When** refactored
   **Then** all transitions use `--transition-fast` or `--transition-normal`

## Tasks / Subtasks

- [ ] Task 1: Audit current styles.css (AC: #1)
  - [ ] Identify all hardcoded color values
  - [ ] Identify all spacing values (padding, margin, gap)
  - [ ] Identify all typography values (font-family, font-size, font-weight)
  - [ ] Identify all border-radius values
  - [ ] Identify all transition values
  - [ ] Identify all box-shadow/glow values

- [ ] Task 2: Create design tokens in :root (AC: #1-6)
  - [ ] Add color tokens per UX spec:
    ```css
    --color-bg-primary: #0a0a12;
    --color-bg-surface: rgba(255, 255, 255, 0.05);
    --color-accent-primary: #ff2d6a;
    --color-accent-secondary: #00f5ff;
    --color-success: #39ff14;
    --color-warning: #ff6600;
    --color-error: #ff0040;
    --color-text-primary: #ffffff;
    --color-text-muted: #8b8b9e;
    ```
  - [ ] Add spacing tokens:
    ```css
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 32px;
    ```
  - [ ] Add typography tokens:
    ```css
    --font-display: 'Outfit', system-ui, sans-serif;
    --font-body: 'Inter', system-ui, sans-serif;
    --font-size-timer: 64px;
    --font-size-year: 56px;
    ```
  - [ ] Add effect tokens:
    ```css
    --glow-primary: 0 0 20px var(--color-accent-primary);
    --glow-success: 0 0 20px var(--color-success);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-full: 9999px;
    --transition-fast: 150ms ease;
    --transition-normal: 300ms ease;
    ```

- [ ] Task 3: Replace hardcoded values with tokens (AC: #1-6)
  - [ ] Replace all color values with `var(--color-*)`
  - [ ] Replace all spacing values with `var(--space-*)`
  - [ ] Replace all font-family values with `var(--font-*)`
  - [ ] Replace all border-radius values with `var(--radius-*)`
  - [ ] Replace all transition values with `var(--transition-*)`

- [ ] Task 4: Verify no regressions (AC: #1-6)
  - [ ] Test player.html renders correctly
  - [ ] Test admin.html renders correctly
  - [ ] Verify all interactive states work (hover, active, focus)
  - [ ] Verify timer colors still change correctly

## Dev Notes

### Architecture Patterns
- **CSS Custom Properties** at `:root` level for global access
- **Semantic naming** - use purpose-based names (`--color-timer-warning`) not color-based (`--orange`)
- **Fallback values** - include fallbacks for older browsers where critical

### Source Tree Components
- `custom_components/beatify/www/css/styles.css` - Main stylesheet to refactor

### Testing Standards
- Visual regression testing: compare before/after screenshots
- Browser testing: Safari iOS 15+, Chrome 90+, Firefox 90+
- No JavaScript testing required for this story

### Project Structure Notes
- Keep all tokens at top of `styles.css` in `:root` block
- Maintain existing file structure - do not split CSS files

### References
- [Source: _bmad-output/ux-design-specification.md#Design System Foundation]
- [Source: _bmad-output/epics.md#Story 9.1]
- [Source: _bmad-output/project-context.md#Naming Conventions]

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5

### Completion Notes List
- Created comprehensive `:root` design tokens section at top of styles.css (~115 lines)
- Color tokens: 25+ semantic color variables (bg, accent, semantic, text, border)
- Spacing tokens: `--space-xs` (4px) through `--space-2xl` (48px)
- Typography tokens: font families, sizes (xs-hero), weights (normal-extrabold)
- Effect tokens: glow (primary, secondary, success, warning, error), shadows (sm-xl)
- Border radius tokens: `--radius-sm` (4px) through `--radius-full` (9999px)
- Transition tokens: `--transition-fast` (150ms), `--transition-normal` (300ms), `--transition-slow` (500ms)
- Z-index tokens: `--z-control-bar` (100), `--z-modal` (1000), `--z-overlay` (1100)
- Replaced all hardcoded values throughout file with CSS custom properties
- File now uses semantic naming throughout (purpose-based, not color-based)

### File List
- `custom_components/beatify/www/css/styles.css`
