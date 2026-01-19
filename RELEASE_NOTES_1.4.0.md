# Beatify v1.4.0 — World Party Edition

**Release Date:** January 2026

Take your music trivia global! This release brings Spanish language support, Alexa compatibility, and polish across the board. Whether you're hosting in Berlin, Barcelona, or Buenos Aires — Beatify now speaks your language.

---

## Spanish Language Support

Beatify now speaks Spanish! All 268 UI strings have been professionally translated:

- **Automatic detection** — Spanish browsers (es, es-ES, es-MX, es-AR) auto-select Spanish
- **Complete coverage** — Every screen, button, and message translated
- **Playlist localization ready** — Add `fun_fact_es` and `awards_es` to your playlists for Spanish fun facts

Supported languages: English, German, Spanish.

---

## Alexa Device Compatibility

Finally! Spotify playback now works on Alexa-powered devices:

**The problem:** Alexa devices returned "Sorry, direct music streaming isn't supported" when Beatify tried to play Spotify tracks.

**The fix:** We now send the correct `media_content_type: "spotify"` instead of generic `"music"` for Spotify URIs. This matches what Alexa expects for linked Spotify accounts.

| Device Type | Status |
|-------------|--------|
| Echo / Echo Dot | Now working |
| Echo Show | Now working |
| Sonos | Still working |
| Chromecast | Still working |

Future-proofed for Apple Music and Tidal URIs too!

---

## German Playlist Localization

Curators can now add German translations to playlist content:

```json
{
  "year": 1984,
  "uri": "spotify:track:xxx",
  "fun_fact": "Written in just 10 minutes",
  "fun_fact_de": "In nur 10 Minuten geschrieben",
  "awards": ["Grammy Winner"],
  "awards_de": ["Grammy-Gewinner"]
}
```

- Game language German + German content available = German shown
- Missing translation = English fallback (seamless)

---

## TV Dashboard Improvements

The spectator dashboard is now easier to find and more informative:

**Discoverability:**
- New "Open TV Dashboard" button in admin lobby (right next to Print QR)
- Subtle "Cast to TV: /beatify/dashboard" hint on player join screen

**Enhanced Display:**
- **Round statistics** below leaderboard: submission count (3/5) and time remaining
- **Fun facts** now display below the year during reveal phase
- **TV-optimized styling** for 1400px+ screens

---

## QR Code Invite During Game

Late arrivals? No problem! Admins can now invite players mid-game:

1. During the **REVEAL** phase, an "Invite" button appears for admins
2. Tap to open a modal with the QR code and join URL
3. Share with latecomers — they can join immediately
4. Modal auto-closes when the next round starts

The URL is copyable for easy sharing via messaging apps.

---

## Admin Stop Button Fix

The Stop button in the admin control bar now works properly:

**Before:** Button appeared to do nothing (no feedback, silent failures)

**After:**
- Immediate visual feedback ("Stopping...")
- Proper disabled state while processing
- Error recovery if stop fails

---

## Technical Notes

### Files Changed
- 18 files modified across Python, JavaScript, HTML, CSS
- 1 new file: `es.json` (Spanish translations)
- 1 new test file: `test_admin_stop_song.py`
- 35 new unit tests added

### Breaking Changes
None — full backward compatibility with v1.3.x.

### Minimum Requirements
- Home Assistant 2024.1.0 or later
- Python 3.11+ (for HA)
- A Spotify-connected media player

---

**Full Changelog:** https://github.com/mholzi/beatify/compare/v1.3.0...v1.4.0

---

*Your party, your language. Update now and invite the world!*
