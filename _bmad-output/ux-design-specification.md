---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
inputDocuments:
  - '_bmad-output/prd.md'
  - '_bmad-output/epics.md'
  - '_bmad-output/research/music-assistant-media-player-research.md'
workflowType: 'ux-design'
lastStep: 14
completedAt: '2025-12-21'
project_name: 'Beatify'
user_name: 'Markusholzhaeuser'
date: '2025-12-21'
---

# UX Design Specification Beatify

**Author:** Markusholzhaeuser
**Date:** 2025-12-21

---

## Executive Summary

### Project Vision

Beatify transforms Home Assistant into a party game venue where guests guess song release years. The core promise is **frictionless fun** — scan a QR code, type your name, play. No app, no account, no friction.

The UX must feel like a **party game show**, not a developer prototype. Every moment should build excitement: the countdown creates tension, the reveal delivers payoff, the leaderboard sparks competition.

### Target Users

| User | Context | UX Priority |
|------|---------|-------------|
| **Party guests** | Phone in one hand, drink in the other, low light, loud music | One-handed use, large touch targets, instant legibility |
| **Host** | Playing alongside guests while managing game flow | Admin controls that don't break immersion |
| **HA enthusiast** | Setting up before party, showing off tech | Confidence-inspiring setup, "just works" feeling |

### Key Design Challenges

1. **Party conditions** — Low attention, dim lighting, competing noise, one-handed use
2. **Emotional arc** — The game needs drama: tension during countdown, excitement at reveal
3. **20+ players, one leaderboard** — Rankings must feel alive, not like a spreadsheet
4. **Edge-to-edge on mobile** — Current excessive padding wastes precious screen space
5. **Brand identity** — Beatify needs a recognizable visual language and wordmark

### Design Opportunities

1. **The countdown** — Prime real estate for drama: pulsing glow, scale on critical
2. **Celebration-First Reveal** — Lead with emotion, follow with information:
   - Exact match: Confetti burst, "NAILED IT!"
   - Close: "SO CLOSE!" with near-miss animation
   - Way off: Playful "Oops!" with exaggerated distance
3. **Streak celebrations** — Particles/confetti for milestone moments
4. **Leaderboard animation** — Show rank changes with motion, not just numbers
5. **Neon party aesthetic** — Dark background with vibrant neons creates instant party atmosphere

### Design Direction

**Aesthetic:** Neon Party Mode — dark backgrounds (`#0a0a12` or `#121218`) with vibrant magenta/cyan accents, glass surfaces, and glow effects on key interactions only.

**Energy Escalation Pattern:**

| Screen | Energy Level | Treatment |
|--------|--------------|-----------|
| **Join** | Calm | Minimal, clean, just logo + name field + button |
| **Lobby** | Warming up | Subtle animations, player cards slide in, QR pulses gently |
| **Game** | Full party | Glows, dramatic countdown, theatrical reveals |

**Glow Budget (Performance-Safe):**
- Timer (critical states only)
- Submit button (hover/active)
- Reveal year (the big moment)
- Streak milestone celebrations

**Adaptive Theming:**

| Condition | Treatment |
|-----------|-----------|
| **Default (Party Mode)** | Dark background with neon accents — optimized for evening/indoor |
| **Daylight Fallback** | High-contrast mode via `prefers-color-scheme: light` — bold black on white, accents preserved |

**Scalability Patterns (20+ Players):**

| Element | Threshold | Behavior |
|---------|-----------|----------|
| **"Who submitted" tracker** | >15 players | Switch to count mode: "18/25 submitted" |
| **Leaderboard** | >10 players | Smart compression: Top 5 → ... → **You (#14)** → ... → Bottom 3 |
| **Player list (lobby)** | >20 players | Virtualized scroll, count header |

**Technical Prerequisites:**
- Introduce CSS custom properties before redesign
- Handle iOS safe areas for edge-to-edge layout
- Load custom fonts async (don't block render)

**Brand Identity:**
- Beatify wordmark: Bold geometric font with gradient treatment
- **Beat** (white) + **ify** (magenta-to-cyan gradient)
- Subtle glow behind for hero usage

---

## Core User Experience

### Defining Experience

Beatify's core experience is **competitive music nostalgia** — players race against the clock to guess when songs were released, competing for bragging rights among friends.

The defining interaction is the **guess-submit loop**: hear a song, drag a slider to select a year, tap submit before time runs out. This loop repeats 10-20 times per game, making it the most frequent and critical interaction to perfect.

Success means this loop feels:
- **Responsive** — slider moves with zero lag
- **Urgent** — countdown creates genuine tension
- **Satisfying** — submit provides immediate tactile feedback
- **Rewarding** — reveal delivers emotional payoff

### Platform Strategy

| Dimension | Decision |
|-----------|----------|
| **Platform** | Mobile web (progressive web app capable) |
| **Input** | Touch-first, one-handed operation |
| **Orientation** | Portrait only |
| **Minimum viewport** | 320px width |
| **Offline support** | Not required (real-time multiplayer) |
| **Browser targets** | iOS Safari 15+, Chrome 90+, Firefox 90+ |

The mobile web approach eliminates app store friction — guests scan a QR code and play within seconds, no download required.

### Effortless Interactions

| Interaction | Target Experience |
|-------------|-------------------|
| **Join flow** | QR scan → name entry → playing in <10 seconds |
| **Year selection** | Single thumb gesture, no precision required |
| **Submit action** | Large tap target, instant visual confirmation |
| **Result comprehension** | Emotion first, numbers second, no reading required |
| **Leaderboard navigation** | Instantly find yourself, understand rank |

### Critical Success Moments

1. **First Scan Success** — New player goes from QR to lobby without confusion
2. **First Guess Submitted** — Player understands the mechanic without explanation
3. **First Reveal Reaction** — Player laughs, groans, or cheers — emotional engagement
4. **First Leaderboard Check** — Player finds their position and cares about it
5. **First Streak Achieved** — Player feels rewarded and wants to protect it

### Experience Principles

1. **Thumb-Zone Everything** — All critical actions reachable by right thumb in portrait mode
2. **Emotion Before Information** — Lead with celebration/commiseration, follow with data
3. **Zero Learning Curve** — First-time users succeed without instruction or tutorial
4. **The Room Is The Game** — Phone supplements the shared audio/social experience
5. **Speed Is Respect** — Every millisecond of latency erodes trust; use optimistic UI
6. **Drama Beats Accuracy** — A theatrical wrong answer is more fun than a boring right one

---

## Desired Emotional Response

### Primary Emotional Goals

| Emotion | Priority | Expression |
|---------|----------|------------|
| **Excitement** | Primary | High-energy countdown, celebration animations, dramatic reveals |
| **Competition** | Primary | Visible rankings, streak rewards, rank change animations |
| **Nostalgia** | Secondary | Music triggers memories; album art and song info support this |
| **Belonging** | Secondary | Social proof (who's playing, who submitted), shared experience |
| **Fun Failure** | Essential | Wrong answers are funny, not shameful; playful "Oops!" reactions |

### Emotional Journey Map

| Phase | Emotion | Design Support |
|-------|---------|----------------|
| **Join** | Curiosity → Ease | Clean entry, instant success, "that was easy" |
| **Lobby** | Anticipation → Social energy | See others joining, feel the crowd building |
| **Song start** | Recognition → Engagement | "I know this!" moment, lean in |
| **Guessing** | Confidence → Tension | Slider feels responsive, timer builds pressure |
| **Final seconds** | Excitement → Urgency | Pulsing timer, heightened visuals, heart racing |
| **Submit** | Relief → Anticipation | Instant confirmation, waiting for reveal |
| **Reveal** | Triumph OR Playful defeat | Emotion-first feedback, celebration or commiseration |
| **Leaderboard** | Pride OR Determination | See your position, motivated for next round |

### Micro-Emotion Targets

**At submission:** "Locked in!" not "Did it work?"
**At wrong answer:** "Ha! Way off" not "I suck at this"
**At streak break:** "Noooo!" (dramatic) not silence
**At timer critical:** "Come on!" (thrill) not "I'm gonna miss it" (panic)

### Emotions to Prevent

| Emotion | Prevention Strategy |
|---------|---------------------|
| **Confusion** | Zero learning curve, obvious affordances |
| **Anxiety** | Timer excites, doesn't punish |
| **Shame** | Celebrate everyone, make misses funny |
| **Frustration** | Instant feedback, forgiving timing |
| **Boredom** | Quick transitions, always something happening |
| **Isolation** | Social proof, encourage looking up |

### Emotional Design Principles

1. **Celebrate Everything** — Every action deserves acknowledgment
2. **Make Failure Fun** — Wrong answers get playful reactions
3. **Build Social Energy** — Never feel like you're playing alone
4. **Urgency, Not Anxiety** — Timer excites, doesn't stress
5. **Momentum Matters** — Always a sense of forward progress
6. **The Room Wins** — If players are laughing together, we've succeeded

---

## UX Pattern Analysis & Inspiration

### Inspiring Products Analysis

#### Jackbox Games
- **Phone as controller:** Minimal phone UI, rich shared display
- **One task at a time:** Never multiple choices simultaneously
- **TV timing language:** Pacing feels like a game show
- **Failure is funny:** Wrong answers become entertainment content

#### Kahoot
- **Color = meaning:** Shapes and colors over text
- **Leaderboard drama:** Podium reveals, animated rank changes
- **Instant feedback:** Immediate right/wrong indication
- **High energy:** Music and motion reinforce excitement

#### SongPop / Heardle
- **Album art as memory trigger:** Visual aids recognition
- **Social sharing:** Results designed for screenshots
- **Music-first:** Audio is the star, UI supports it

#### Neon/Arcade UI Trends
- **Glow restraint:** Effects on interactions, not everywhere
- **Dark foundations:** Near-black lets colors pop
- **Glass surfaces:** Subtle transparency for depth
- **High contrast:** White text on dark for legibility

### Transferable UX Patterns

| Category | Pattern | Application |
|----------|---------|-------------|
| **Interaction** | One task at a time | Slider + Submit, nothing else |
| **Interaction** | Large touch targets | 56px minimum for primary actions |
| **Feedback** | Celebration-first | Emotion before score breakdown |
| **Feedback** | Instant confirmation | Optimistic UI, no spinners |
| **Visual** | Glow budget | Timer, submit, reveal only |
| **Visual** | Dark mode default | Party atmosphere |
| **Navigation** | Single-screen flows | No deep navigation |
| **Social** | Visible participation | Who's playing, who submitted |

### Anti-Patterns to Avoid

| Anti-Pattern | Risk | Prevention |
|--------------|------|------------|
| Tutorial overlays | Ignored at parties | Self-explanatory UI |
| Tiny touch targets | Missed taps | 44-56px minimums |
| Loading spinners | Momentum killer | Optimistic UI |
| Complex navigation | Users lost | Flat structure |
| White backgrounds | Harsh, generic | Dark mode |
| Flat feedback | Boring reveals | Theatrical reactions |
| Persistent leaderboard | Space hog | Show after reveal |

### Design Inspiration Strategy

**Adopt:**
- Phone as simple controller (Jackbox)
- One task at a time (Jackbox)
- Color-coded states (Kahoot)
- Celebration-first feedback (Kahoot)
- Glow restraint (Neon UI)

**Adapt:**
- Podium reveal → End-game leaderboard
- Album art → Smaller during guess, prominent at reveal
- Glass surfaces → Subtle, not overdone

**Avoid:**
- Tutorials, spinners, white backgrounds, persistent UI elements

---

## Design System Foundation

### Design System Choice

**Approach:** CSS Custom Properties + Semantic Utility Classes

Given Beatify's vanilla HTML/CSS/JS stack, custom "Neon Party Mode" aesthetic, and performance requirements, a lightweight custom design system built on CSS custom properties is the optimal choice.

### Rationale for Selection

| Factor | Decision Driver |
|--------|-----------------|
| **No framework** | Framework-based systems (MUI, Chakra) require React/Vue |
| **Custom aesthetic** | Pre-built systems fight the neon party vision |
| **Performance** | Zero library overhead, minimal CSS |
| **Scope** | 6 screens don't justify a full design system |
| **Theming** | CSS variables enable party/day mode switching |

### Implementation Approach

**Phase 1: Token Extraction**
- Audit current `styles.css` (2400+ lines)
- Extract all colors, spacing, typography, shadows into `:root` variables
- Create semantic naming (`--color-timer-warning` not `--orange`)

**Phase 2: Component Patterns**
- Define reusable component classes (`.btn-primary`, `.btn-glow`, `.card`, `.card-glass`)
- Create animation utilities (`.animate-pulse`, `.animate-pop`)
- Build glow effect mixins

**Phase 3: Theme System**
- Default: Party Mode (dark + neon)
- Alternative: Day Mode (light + high contrast)
- Switch via `<body class="theme-day">` override

### Customization Strategy

**Design Tokens:**

```css
:root {
  /* Colors - Semantic */
  --color-bg-primary: #0a0a12;
  --color-bg-surface: rgba(255, 255, 255, 0.05);
  --color-accent-primary: #ff2d6a;
  --color-accent-secondary: #00f5ff;
  --color-success: #39ff14;
  --color-warning: #ff6600;
  --color-error: #ff0040;
  --color-text-primary: #ffffff;
  --color-text-muted: #8b8b9e;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* Typography */
  --font-display: 'Outfit', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-size-timer: 64px;
  --font-size-year: 56px;

  /* Effects */
  --glow-primary: 0 0 20px var(--color-accent-primary);
  --glow-success: 0 0 20px var(--color-success);

  /* Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
}
```

**Component Classes:**

| Component | Class | Purpose |
|-----------|-------|---------|
| Primary button | `.btn-primary` | Main actions (Submit, Join) |
| Glow button | `.btn-glow` | Adds glow on hover/active |
| Card | `.card` | Container with surface bg |
| Glass card | `.card-glass` | Subtle transparency |
| Timer | `.timer`, `.timer--warning`, `.timer--critical` | Countdown states |
| Glow text | `.text-glow` | Neon text effect |

---

## Defining Experience

### The Core Interaction

**One-liner:** "Race against the clock to guess when songs were released"

**User description:** "You hear a song, drag a slider to pick the year, and try to beat everyone else before time runs out"

This guess-submit-reveal loop is Beatify's defining interaction — the experience that makes it addictive and shareable.

### User Mental Model

Users approach Beatify with existing mental models:
- Sliders select from a range
- Big buttons are primary actions
- Red timers mean urgency
- Checkmarks confirm completion
- Names in lists mean competition

**Alignment:** Beatify leverages these models without requiring learning.

### Success Criteria

| Criterion | Target |
|-----------|--------|
| Slider responsiveness | <16ms (60fps feel) |
| Year always visible | Above slider, large text |
| Submit confirmation | <100ms visual feedback |
| Timer urgency | 90%+ submit before timeout |
| Reveal satisfaction | Emotional reaction rate |
| Retention | 80%+ play multiple rounds |

### Novel UX Patterns

| Pattern | Innovation |
|---------|------------|
| **Celebration-first reveal** | Emotion before score breakdown |
| **Streak mechanics** | Consecutive correct bonus |
| **Multiplier betting** | Risk/reward for confident players |
| **Admin-player hybrid** | Host plays while controlling game |

### Experience Mechanics

**The Loop:**
1. **Song starts** → Audio plays, timer begins, slider resets
2. **Guessing** → Drag slider, see year, feel time pressure
3. **Submit** → Tap button, instant confirmation, wait for others
4. **Reveal** → Emotion first, then year, then points
5. **Leaderboard** → Animated rankings, find yourself, next round

**Timing:**
- Song plays: 30 seconds (configurable)
- Reveal: 3-5 seconds
- Leaderboard: 3-5 seconds
- Round total: ~40 seconds

---

## Visual Design Foundation

### Color System

**Primary Palette:**

| Role | Hex | Usage |
|------|-----|-------|
| Background | `#0a0a12` | All screens base |
| Surface | `rgba(255,255,255,0.05)` | Cards, containers |
| Accent Primary | `#ff2d6a` | Brand, buttons, CTA |
| Accent Secondary | `#00f5ff` | Highlights, gradients |
| Success | `#39ff14` | Correct, streaks |
| Warning | `#ff6600` | Timer warning |
| Error | `#ff0040` | Timer critical |
| Text Primary | `#ffffff` | Headlines |
| Text Secondary | `#b3b3c2` | Body text |

**Semantic States:**
- Timer: normal (white) → warning (orange) → critical (red + pulse)
- Reveal: success (green + confetti) / close (orange) / wrong (gray + playful)

**Theming:** Party Mode (default) with Day Mode fallback via `prefers-color-scheme`

### Typography System

| Role | Font | Size | Weight |
|------|------|------|--------|
| Display (timer, year) | Outfit | 56-64px | 800-900 |
| Headlines | Outfit | 24-32px | 600-700 |
| Body | Inter | 14-16px | 400-600 |

**Loading:** `font-display: swap`, preload critical, 2 weights max per font

### Spacing & Layout

**Base unit:** 8px

**Scale:** xs(4) / sm(8) / md(16) / lg(24) / xl(32)

**Principles:**
- Edge-to-edge on mobile (8px screen padding)
- Thumb zone priority (actions in bottom 60%)
- Single column, vertical stacking
- No horizontal scroll

### Accessibility

**Contrast:** All combinations exceed WCAG AA (4.5:1+)
**Touch:** 44px minimum, 56px recommended
**Motion:** Respect `prefers-reduced-motion`
**Color independence:** Icons + animation + text, never color alone

---

## Design Direction Decision

### Chosen Direction

**Neon Party Mode** — Dark, immersive backgrounds with electric magenta and neon cyan accents. Glow effects reserved for key moments. Edge-to-edge layouts that maximize gameplay area.

### Design Rationale

| Decision | Rationale |
|----------|-----------|
| Dark backgrounds | Works in party lighting, creates immersion |
| Neon accents | Instantly says "party," not "business app" |
| Glow budget | Performance-safe, makes moments special |
| Edge-to-edge | Maximizes limited mobile real estate |
| Bold typography | Readable from arm's length, one-handed |
| Energy escalation | Matches emotional journey through game |

### Screen Energy Map

| Screen | Energy | Key Visual Treatment |
|--------|--------|---------------------|
| Join | Calm | Minimal, logo focus, clean input |
| Lobby | Building | Cards slide in, QR pulses |
| Guessing | Focused | Timer dominates, slider responsive |
| Reveal | Explosive | Confetti, glow burst, big year |
| Leaderboard | Competitive | Animated ranks, you highlighted |

### Implementation Approach

1. **Phase 1:** Introduce CSS custom properties for all tokens
2. **Phase 2:** Refactor existing screens to use new tokens
3. **Phase 3:** Add glow effects and animations
4. **Phase 4:** Implement reveal celebration (confetti, emotion text)
5. **Phase 5:** Polish leaderboard animations

---

## User Journey Flows

### Guest Journey (Tom)

**Path:** QR Scan → Join → Play → Celebrate

```
QR Scan → Name Entry → Lobby → Guessing → Submit → Reveal → Leaderboard → Repeat
```

**Critical moments:**
- QR must open browser directly (no app prompt)
- Name validation inline, not blocking
- First guess must be intuitive (no tutorial needed)
- Reveal creates emotional reaction

### Host Journey (Sarah)

**Path:** Configure → Start → Play + Manage → End

```
Admin Panel → Settings → QR Display → Start → Play (with controls) → End
```

**Critical moments:**
- Admin controls integrated into play view
- Start only enabled with 2+ players
- Can pause/resume if needed
- Sees same experience as guests

### Late Joiner Journey (Lisa)

**Path:** Arrive → Scan → Join In Progress

```
QR Scan → Name → Join Active Game → Wait for Next Round → Play
```

**Critical moments:**
- No disruption to ongoing round
- Starts at 0 points (fair)
- No shame messaging about missed rounds

### Setup Journey (Marcus)

**Path:** Install → Configure → Test → Ready

```
Install → HA Config → Media Player → Playlist → Solo Test → QR Test → Ready
```

**Critical moments:**
- Solo mode for testing
- Audio feedback confirms setup
- Clear error messages

### Journey Patterns

- **Instant feedback:** Every action has visible response
- **Progressive disclosure:** Only show what's needed now
- **Social proof:** See other players' status
- **Error recovery:** Clear hints, no dead-ends
- **State persistence:** Reconnection is seamless

---

## Component Strategy

### Foundation Components

| Component | Purpose | Key States |
|-----------|---------|------------|
| Button Primary | Main actions | default, hover, active, disabled, loading |
| Button Secondary | Secondary actions | default, hover, active, disabled |
| Input Text | Text entry | default, focus, error, disabled |
| Card | Content container | default, highlighted |

### Game Components

| Component | Purpose | Key States |
|-----------|---------|------------|
| Timer | Countdown | normal, warning (<10s), critical (<5s) |
| Year Slider | Year selection | default, dragging, disabled |
| Submit Button | Lock in guess | default, loading, submitted |
| Player Card | Player identity | waiting, submitted, you |
| Leaderboard Row | Ranking display | default, you, climbing, falling |
| Reveal Celebration | Answer feedback | exact, close, wrong |

### Component States

**Timer States:**
- Normal: White text
- Warning (10-5s): Orange + pulse
- Critical (<5s): Red + pulse + glow + scale

**Reveal Variants:**
- Exact match: "NAILED IT!" + confetti + green
- Close (within 2 years): "SO CLOSE!" + near-miss
- Wrong: "Oops!" + playful + distance

### Implementation Roadmap

| Phase | Components | Dependency |
|-------|------------|------------|
| 1 | Button, Input, Card | Foundation |
| 2 | Timer, Slider, Submit | Core loop |
| 3 | Player Card, Leaderboard | Social |
| 4 | Reveal, Confetti | Emotion |
| 5 | Progress, Streak, Toast | Polish |

---

## UX Consistency Patterns

### Feedback Patterns

| Type | Trigger | Treatment |
|------|---------|-----------|
| **Micro success** | Submit confirmed | Checkmark, button → "Waiting..." |
| **Standard success** | Close guess | "SO CLOSE!" + orange |
| **Major success** | Exact guess | "NAILED IT!" + confetti + green |
| **Warning** | Timer <10s | Orange text + pulse |
| **Critical** | Timer <5s | Red text + pulse + glow + scale |
| **Error** | Validation fail | Inline hint, red border |
| **Info** | Waiting | Progress text, no blocking |

### Button Patterns

| Level | Visual | Usage |
|-------|--------|-------|
| Primary | Magenta fill + glow | One per screen (Join, Submit) |
| Secondary | Magenta border | Supporting actions |
| Admin | Subtle, icon + text | Host controls |

**States:** default → hover (glow) → active (scale down) → disabled (gray)
**Sizing:** 56px primary, 48px secondary, 44px minimum touch target

### Loading States

- **Full screen:** Logo pulse, no spinner
- **Inline:** Spinner in button, dimensions stable
- **Waiting:** Progress text ("12/20 submitted")

### Form Patterns

- Validate on blur, not keystroke
- Inline hints, never modal errors
- Focus: magenta glow, Error: red border

### Animation Principles

- Ease-out timing, 150-500ms duration
- Transform + opacity only (GPU-accelerated)
- Respect prefers-reduced-motion

---

## Responsive Design & Accessibility

### Breakpoint Strategy

| Breakpoint | Width | Treatment |
|------------|-------|-----------|
| **Mobile (default)** | 320px+ | Single column, full-width controls |
| **Large Mobile** | 390px+ | Larger touch targets, more breathing room |
| **Tablet** | 768px+ | Centered content, max-width container |

**Approach:** Mobile-first, min-width queries, single-column gameplay on all sizes.

### Touch Target Standards

| Element | Minimum | Recommended |
|---------|---------|-------------|
| Primary buttons | 48px | 56px |
| Secondary actions | 44px | 48px |
| Slider thumb | 44px | 48px |
| List items | 44px | 48px |

### Safe Area Handling

```css
.screen {
  padding-bottom: max(var(--space-md), env(safe-area-inset-bottom));
  padding-left: max(var(--space-sm), env(safe-area-inset-left));
  padding-right: max(var(--space-sm), env(safe-area-inset-right));
}
```

### Accessibility Standards

**Target:** WCAG 2.1 AA

| Requirement | Implementation |
|-------------|----------------|
| **Color contrast** | 4.5:1 minimum (all text passes) |
| **Focus indicators** | Magenta glow ring, 2px offset |
| **Motion** | `prefers-reduced-motion` disables animations |
| **Screen readers** | ARIA labels, live regions for timer |
| **Color independence** | Icons + text + animation, never color alone |

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Fallbacks:** Static confetti icon, instant state changes, no glow pulses.

### Day Mode Fallback

```css
@media (prefers-color-scheme: light) {
  :root {
    --color-bg-primary: #ffffff;
    --color-bg-surface: #f5f5f7;
    --color-text-primary: #1a1a1a;
    --color-text-muted: #666666;
    /* Accents remain vibrant */
  }
}
```

### Performance Considerations

- **GPU-only animations:** transform, opacity
- **Glow budget:** Maximum 3 glowing elements per screen
- **Font loading:** `font-display: swap`, preload critical weights
- **Image optimization:** WebP with SVG fallback for artwork

---

## Implementation Guidance

### CSS Custom Properties Migration

**Priority 1:** Extract all hardcoded values to `:root` variables
**Priority 2:** Create semantic component classes
**Priority 3:** Add state variants (hover, active, disabled)
**Priority 4:** Implement animation utilities

### Component Build Order

1. Foundation: Buttons, Inputs, Cards
2. Core Loop: Timer, Slider, Submit
3. Social: Player Cards, Leaderboard
4. Celebration: Reveal, Confetti
5. Polish: Toasts, Streaks, Progress

### Testing Checklist

- [ ] Touch targets pass 44px minimum
- [ ] All text passes 4.5:1 contrast
- [ ] Reduced motion eliminates all animation
- [ ] Screen reader announces timer changes
- [ ] Day mode remains usable
- [ ] Edge-to-edge works with notch/home bar

---

*UX Design Specification Complete — Ready for Implementation*
