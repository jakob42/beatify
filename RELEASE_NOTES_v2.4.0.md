**Release Date:** February 2026

Beatify v2.4.0 brings **Tidal as a fourth streaming provider**, an exciting **Movie Quiz Bonus mode**, **French language support**, and **two new playlists** — now featuring 18 playlists with over 2,000 songs.

---

## 🌊 New Streaming Provider: Tidal

Tidal joins Spotify, Apple Music, and YouTube Music as the fourth supported music platform. All 18 playlists have been enriched with Tidal URIs, giving you more flexibility in how you play.

- **Backend:** New `PROVIDER_TIDAL` with URI pattern `tidal://track/{id}`
- **Frontend:** Tidal chip button in Admin UI with enable/disable based on speaker capability
- **Platform support:** Music Assistant (Tidal via URI) — Sonos and Alexa do not support Tidal
- **Enrichment:** 90%+ of songs enriched with Tidal URIs via Odesli API

---

## 🎬 New Feature: Movie Quiz Bonus

Playing the Movie's Greatest Themes playlist? Now you can earn bonus points by guessing which movie the song is from! After guessing the release year, three movie options appear — pick the right film for tiered bonus points:

| Speed | Points |
|-------|--------|
| Fast answer (≤3s) | +30 points |
| Quick answer (≤6s) | +20 points |
| Correct answer | +10 points |

- **Film Buff superlative:** Awarded to the player with the most movie bonus points
- **Server-side timing:** Fastest correct guesses rank highest
- **41 new unit tests** across 9 test classes

---

## 🇫🇷 New Language: French

French joins English, German, and Spanish as the fourth UI language. All game text, playlist descriptions, and song fun facts are now available in French — *Bienvenue!*

---

## 🎸 New Playlist: British Invasion & Britpop

100 tracks spanning the 1960s British Invasion through 90s Britpop. From The Beatles and The Kinks to Oasis and Blur — the best of British rock in one playlist. Every track includes chart positions, certifications, alternative artists, and fun facts in four languages.

---

## ☀️ New Playlist: Summer Party Anthems

112 feel-good summer tracks perfect for parties. Features The Beach Boys, Wham!, Daft Punk, and decades of sunshine hits from 1957–2020 to keep the energy high. Complete with comprehensive metadata and cross-platform streaming URIs.

---

## 📊 By The Numbers

**18 Playlists** | **2,008 Songs** | **4 Music Platforms** | **4 Languages**

---

*Your speakers, your music service, your party!* 🎉
