# Beatify v1.6.0 — React & Connect 🎉📲

**Release Date:** January 2026

Beatify brings the party energy to a new level! This release introduces live emoji reactions during reveals, a cleaner lobby experience, and a brand new One-Hit Wonders playlist. Share those "wow" moments together and keep the good vibes flowing!

---

## 🎉 Live Emoji Reactions — Share the Moment

React in real-time when songs are revealed! Send emoji reactions that float across everyone's screens:

**How it works:**
1. During the REVEAL phase, a reaction bar appears at the bottom
2. Tap one of 5 emojis: 🔥 😂 😱 👏 🤔
3. Your reaction floats up on the TV dashboard AND all player screens
4. Everyone sees who reacted: "Sarah 🔥"

| Emoji | When to Use |
|-------|-------------|
| 🔥 | That song is fire / Great guess! |
| 😂 | Hilarious year reveal |
| 😱 | Shocked by the answer |
| 👏 | Applause for a perfect guess |
| 🤔 | Never heard of that song |

**Details:**
- One reaction per player per reveal (no spam!)
- Glassmorphism container with subtle button styling
- Positioned above admin controls for hosts
- Respects reduced motion preferences

The party just got more interactive! 🎮

---

## 📲 Improved Lobby Experience — Less Clutter, More Fun

The player lobby has been streamlined for a cleaner look:

**Collapsible Sections:**
| Section | Default State | Why |
|---------|---------------|-----|
| How to Play | Collapsed | Returning players don't need instructions |
| Invite Friends (QR) | Collapsed | Less visual clutter once everyone's joined |

**How to Play Instructions:**
- Expandable 4-step guide for new players
- Clean numbered list with proper formatting
- Tap to expand/collapse anytime

**Sticky Leave Game Footer:**
- "Leave Game" button always visible at bottom
- No more scrolling to find the exit
- Safe area support for notched phones

First-time players get guidance, regulars get a clean screen!

---

## 🎵 New Playlists

### One-Hit Wonders — 98 Songs

A brand new playlist celebrating the artists who made one unforgettable hit:

| Decade | Sample Songs |
|--------|--------------|
| 1960s | "Eve Of Destruction", "96 Tears" |
| 1970s | "Spirit In The Sky", "Kung Fu Fighting" |
| 1980s | "Take On Me", "Come On Eileen" |
| 1990s | "Macarena", "Mambo No. 5" |
| 2000s | "Crazy Town - Butterfly", "Chamillionaire - Ridin'" |

**Features:**
- 98 songs spanning 6 decades
- Full trilingual fun facts (EN, DE, ES)
- Chart history and certifications included
- Perfect for "I know this song but who sang it?" moments

### Kölner Karneval — 291 Songs 🎭

The ultimate Cologne carnival playlist! From classic Kölsch dialect hits to modern party anthems:

| Era | Sample Songs |
|-----|--------------|
| Classics | "Drink doch eine met" (Bläck Fööss), "Viva Colonia" (Höhner) |
| Modern | "Pirate" (Kasalla), "Echte Fründe" (Höhner) |
| Party | "Polka, Polka, Polka" (Brings), "Superjeile Zick" (Brings) |

**Features:**
- 291 songs celebrating Kölner Karneval tradition
- Full trilingual fun facts (EN, DE, ES)
- Spans 50+ years of carnival history
- Perfect for Karneval parties or German music lovers

Kölle Alaaf! 🎉

---

## 🎨 UI Polish

- 📊 Analytics icon in admin header for quick access
- Dark mode consistency across admin and analytics pages
- Cleaner how-to-play list formatting
- Reaction bar with frosted glass effect

---

## 🔧 Upgrade Notes

1. Restart Home Assistant to load new code
2. Hard refresh browser (Cmd+Shift+R) for new assets
3. No breaking changes — existing games preserved

---

**Full Changelog:** https://github.com/mholzi/beatify/compare/v1.5.0...v1.6.0

*Ready to react? Update now and let the emojis fly!* 🎉🔥😂
