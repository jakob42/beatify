# Beatify v1.3.0 — Steal the Show 🥷

**Release Date:** January 2026

Get ready to outplay, outsmart, and outsteal your friends! This release introduces game-changing power-ups, end-game awards that celebrate every play style, and rock-solid reliability improvements that keep the party going all night long.

---

## 🥷 Steal Power-Up — Trust No One

The most requested feature is here! Build a streak and steal your way to victory:

**How it works:**
1. Get **3 correct guesses in a row** (within scoring range)
2. A glowing "Steal Available" indicator appears
3. Click the steal button to see who has already submitted
4. Choose your target and copy their answer instantly!

| Scenario | Result |
|----------|--------|
| You steal a perfect guess | You get the same points they would |
| You steal a wrong answer | You share their fate! |
| Someone steals from you | Your answer still counts normally |

**Strategic depth:**
- Use it early when answers cluster, or save it for when you're stumped
- The steal target list shows who submitted (but not their answers!)
- Both stealer and victim see the relationship revealed at the end

Translations included for English and German. The mind games begin! 🎭

---

## 🏆 End-Game Superlatives — Everyone's a Winner

Because first place isn't the only way to shine! After the final round, special awards celebrate unique achievements:

| Award | What It Takes | Badge |
|-------|---------------|-------|
| ⚡ **Speed Demon** | Fastest average submission time | "X.Xs avg" |
| 🔥 **Hot Streak** | Longest scoring streak (min 3) | "X in a row" |
| 🎲 **Risk Taker** | Most bets placed (min 3) | "X bets" |
| 💪 **Clutch Player** | Highest score in final 3 rounds | "X pts in final 3" |
| 🎯 **Close Calls** | Most guesses within 1 year | "X close guesses" |

Awards appear with staggered animations on both player devices and the TV dashboard. Even the slowest guesser might be the ultimate Risk Taker!

---

## ⭐ Song Difficulty Rating — Know What You're Up Against

See how hard each song really is based on how everyone has played it:

| Stars | Accuracy | Meaning |
|-------|----------|---------|
| ⭐⭐⭐⭐ | 75%+ | Easy — Most players nail it |
| ⭐⭐⭐ | 50-75% | Medium — Solid challenge |
| ⭐⭐ | 25-50% | Hard — Only experts score |
| ⭐ | <25% | Extreme — Nearly impossible! |

- Displayed during the REVEAL phase after each round
- Ratings improve as more games are played
- "Not enough data yet" shown for new songs

Finally know if that obscure 1967 B-side was actually guessable!

---

## 🔧 Under the Hood

**Media Player:**
- Pre-flight check wakes sleepy Sonos speakers before each round
- Smart retry (up to 3 attempts) if a song fails to play
- Game pauses gracefully instead of crashing on media errors
- Metadata sync prevents mismatched song info during reveal

**Stability:**
- WebSocket keepalive prevents timeouts during long reveals
- Playlists auto-update when a newer bundled version is available

**Bug Fixes:**
- Fixed runaway retry loop that could exhaust playlist in seconds
- Fixed Safari desktop bet toggle not responding to clicks
- Fixed dark mode button text color on "Join as Player" button

---

## 📋 Technical Notes

### Breaking Changes
None — full backward compatibility with v1.2.x game saves and statistics.

### Minimum Requirements
- Home Assistant 2024.1.0 or later
- A Spotify-connected media player (Sonos, Chromecast, etc.)

---

**Full Changelog:** https://github.com/mholzi/beatify/compare/v1.2.0...v1.3.0

---

*Ready to steal some answers? Update now and let the games begin!* 🎮
