# Beatify v1.2.0 — The Party Just Got Better 🎉

**Release Date:** January 2026

Your favorite music guessing game just leveled up! This release transforms every game night into an unforgettable experience with stunning celebrations, fascinating music trivia, and competitive features that'll keep everyone coming back for more.

---

## 🎯 Difficulty Presets — Your Game, Your Rules

Finally! Tailor the challenge to your crowd:

| Mode | Perfect For | Exact | Close | Near |
|------|-------------|-------|-------|------|
| **🟢 Easy** | Family gatherings, casual parties | 10 pts | ±7 years = 5 pts | ±10 years = 1 pt |
| **🟡 Normal** | Classic Beatify experience | 10 pts | ±3 years = 5 pts | ±5 years = 1 pt |
| **🔴 Hard** | Music nerds, trivia nights | 10 pts | ±2 years = 3 pts | 0 pts |

No more complaints that it's "too hard" or "too easy" — now everyone's happy!

- Select difficulty on the game setup screen before starting
- Current difficulty displayed as a badge during gameplay
- Default remains Normal for the classic experience

---

## 📚 Rich Song Information — Learn While You Play

Turn every reveal into a "wow" moment! After each guess, discover:

- **🏆 Chart History** — Billboard Hot 100 peak position, weeks on chart, UK/German positions
- **💿 Certifications** — Diamond, Multi-Platinum, Gold badges with country indicators
- **🎵 Fun Facts** — Mind-blowing trivia that sparks conversations
- **🏅 Awards** — Grammy wins, Hall of Fame inductions, and more

Your guests will leave knowing more about music than when they arrived. Education disguised as fun!

Information displays in a compact "Fun Fact" box that enhances without overwhelming the score reveal. Missing data? No problem — the UI gracefully shows only what's available.

---

## 📊 Game Statistics — Fuel the Competition

Now the rivalry extends beyond a single game:

- **Track Every Victory** — Persistent stats across all your game nights (date, playlist, rounds, players, winner, scores)
- **All-Time Leaderboard** — Who's the ultimate Beatify champion in your household?
- **Live Motivation** — Real-time feedback during reveal phase:
  - "You're crushing it! 4.2 pts above average!"
  - "NEW RECORD!" when you beat the all-time high
  - "First game! Setting the benchmark" for new installations
- **End Screen Summary** — Compare your game to all-time averages with performance badges

Stats survive Home Assistant restarts, so your legacy lives on forever. 👑

---

## 🎊 Confetti Celebrations — Feel Like a Champion

Because winning should FEEL like winning:

| Moment | Celebration | Duration |
|--------|-------------|----------|
| 🎯 **Nailed It!** | Gold confetti burst when you guess the exact year | 2 seconds |
| 🏆 **Record Breaker!** | Rainbow shower when you set a new all-time high | 3 seconds |
| 👑 **Victory!** | Fireworks from both sides for the game winner | 4 seconds |
| ⭐ **Perfect Game!** | Epic multi-burst celebration extravaganza | 5 seconds |

Every triumph gets the celebration it deserves. On phones AND the big screen!

- Mirrored on TV/Dashboard display for the full party experience
- Respects `prefers-reduced-motion` accessibility setting
- Non-blocking — game controls remain fully clickable during animations

---

## 🎵 New Playlist — Eurovision Winners

**72 winning songs from 1956 to 2025!**

From Lys Assia's "Refrain" to today's champions — every Eurovision winner with rich metadata including country, points scored, and fun facts about each victory.

Perfect for Eurovision watch parties or testing your knowledge of Europe's biggest music competition.

---

## ✨ Polish & Refinements

- **Mystery Mode** — Album covers now blur during guessing phase (no more peeking at release year hints!)
- **Smarter QR Codes** — Now uses actual request URL instead of hardcoded fallback
- **German Chart Support** — Rich song info properly displays German chart positions. Ja, wir sprechen Deutsch! 🇩🇪
- **Buttery Smooth UI** — Fixed horizontal scroll overflow on timer duration selector

---

## 🐛 Squashed Bugs

- Fixed stats service not attaching when GameState created via fallback path
- Fixed `initConfetti()` reference error from legacy code removal
- Fixed timer option buttons not fitting on smaller screens

---

## 📋 Resolved Community Requests

Thanks to everyone who suggested these features!

- ✅ **#2** — Difficulty presets (Easy/Normal/Hard)
- ✅ **#11** — Rich song information cards during reveal
- ✅ **#15** — Game statistics tracking with motivational feedback
- ✅ **#17** — Confetti celebrations for special moments

---

## 🚀 Upgrade Now

**Zero breaking changes** — just update and enjoy!

| What's New | Details |
|------------|---------|
| Stats Storage | `config/beatify/stats.json` — Your game history (auto-created on first game) |
| CDN Dependency | Canvas-confetti library loaded from jsDelivr for celebration animations |

All existing configurations remain fully compatible.

---

## 🔮 Coming Soon in v1.3

We're already cooking up the next batch of features:

- **End Game Superlatives** — "Most Accurate", "Speed Demon", "Comeback King" awards
- **Song Difficulty Ratings** — Know which songs stump players based on historical accuracy
- **Apple Music Support** — More music sources, more fun

---

**Ready to party?** Update now and let the good times roll! 🎶

---

[Download v1.2.0](https://github.com/mholzi/beatify/releases/tag/v1.2.0) | [Full Changelog](https://github.com/mholzi/beatify/compare/v1.1.0...v1.2.0) | [Report Issues](https://github.com/mholzi/beatify/issues)
