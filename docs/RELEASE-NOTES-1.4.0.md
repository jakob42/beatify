# Beatify v1.4.0 — Fiesta Internacional 🌍

**Release Date:** January 2026

Beatify speaks your language! This release brings full Spanish support, German song trivia, and a polished TV Dashboard experience. Whether you're hosting in Madrid, Munich, or Miami — the party translates perfectly.

---

## 🇪🇸 Spanish Language Support — ¡Vamos!

Play Beatify entirely in Spanish with complete UI translation and localized song content:

**What's included:**
- All buttons, labels, messages, and game text in Spanish
- Automatic language detection for Spanish browsers (es, es-ES, es-MX, es-AR, etc.)
- 370+ songs with Spanish fun facts and awards
- Spanish flag option in the language selector

| Screen | Spanish Example |
|--------|-----------------|
| Lobby | "Sala de espera" / "1 jugador unido" |
| Playing | "Enviar respuesta" / "0/1 enviados" |
| Reveal | Fun facts in Spanish with localized awards |
| End | "Fin del juego!" / "0 puntos" |

The fiesta is officially international! 🎉

---

## 🇩🇪 German Playlist Content — Jetzt mit Fakten!

All bundled playlists now include German translations for song trivia:

| Content | Coverage |
|---------|----------|
| Fun Facts | All 370 songs translated |
| Awards | Grammy, chart achievements, certifications |
| Fallback | English displays if German unavailable |

German players finally get the full experience — no more guessing what that fun fact said!

---

## 📺 TV Dashboard — Front and Center

The spectator dashboard is now easier to find and packed with more info:

**Discoverability:**
- "Open TV Dashboard" button on admin setup screen
- "Cast to TV" hint with URL on player join screen

**Enhanced Display:**
- Round statistics: submissions count and time remaining
- Fun facts display during reveal (in the selected language!)
- Localized labels: "Ronda", "Clasificación", "Respuestas"

| Phase | What's New |
|-------|------------|
| Playing | Submissions counter, countdown timer |
| Reveal | Song fun fact below year, top guesses |
| End | Full leaderboard, superlatives |

Cast it to the big screen and let everyone follow along!

---

## 📲 Invite Late Joiners — The Party Never Stops

Admins can now invite players without leaving the game:

**How it works:**
1. Tap the 📲 invite button on any reveal screen
2. QR code popup appears with join URL
3. Late arrivals scan and join instantly
4. Popup auto-closes when next round starts

| Feature | Detail |
|---------|--------|
| Admin Only | Regular players don't see the button |
| Non-Blocking | Game continues while popup is open |
| Copyable URL | For sharing via text/chat |
| REVEAL Phase Join | Players can now join mid-game during reveals |

No more "wait for the next game" — jump right in!

---

## 🎨 Admin Lobby Makeover

The admin lobby now matches the player experience:

| Improvement | Before | After |
|-------------|--------|-------|
| Background | White (jarring) | Dark (consistent) |
| Player List | Hidden | Visible in real-time |
| Player Count | None | "X players joined" |
| Admin Badge | None | 👑 crown emoji |
| Away Status | None | "(away)" indicator |

Admins can finally see who's in the game without joining as a player!

---

## 🔧 Under the Hood

**Alexa Fix:**
- Spotify playback now works on Alexa devices
- Uses `media_content_type: "spotify"` instead of generic type
- No regression on Sonos or Chromecast

**Stop Button:**
- Admin stop button now actually stops the song
- Visual feedback on tap
- Works on mobile with proper touch targets

**i18n Engine:**
- Dashboard waits for language to load before rendering
- Dynamic content uses translation function instead of hardcoded strings
- Backend validates Spanish as language option

**Bug Fixes:**
- Fixed race condition where UI rendered before translations loaded
- Fixed player count showing "1 player" instead of "1 jugador"
- Fixed "(You)" badge not translating to "(Tu)"

---

## 📋 Technical Notes

### Upgrade Path
1. Restart Home Assistant to load new backend code
2. Clear browser cache if translations don't appear
3. No breaking changes — existing games and settings preserved

### Language Behavior
- Language is set per-game by admin
- All players see the admin's selected language
- Browser detection only affects initial page load

### Playlist Schema
New optional fields in playlist JSON:
```json
{
  "fun_fact": "English fact",
  "fun_fact_de": "German fact",
  "fun_fact_es": "Spanish fact",
  "awards": ["Grammy 2020"],
  "awards_de": ["Grammy 2020"],
  "awards_es": ["Grammy 2020"]
}
```

---

## 📊 By the Numbers

| Metric | Value |
|--------|-------|
| Stories Completed | 8 |
| Languages Supported | 3 (EN, DE, ES) |
| Songs with Full i18n | 370 |
| i18n Bugs Fixed | 12+ |
| Beta Releases | 9 |

---

**Full Changelog:** https://github.com/mholzi/beatify/compare/v1.3.0...v1.4.0

---

*¿Listo para jugar? ¡Actualiza ahora y que empiece la fiesta!* 🎮
