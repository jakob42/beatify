# Beatify Architecture

System architecture overview for developers building on or contributing to Beatify.

## System Overview

Beatify is a Home Assistant custom integration that turns smart speakers into an interactive music quiz game. It consists of a Python backend running inside Home Assistant and vanilla JavaScript frontends served over HTTP.

```
# Backend (Python)
+-----------------------------------------------------------+
|                    Home Assistant                          |
|                                                           |
|   +---------------------------------------------------+   |
|   |        Beatify Integration — Backend (Python)      |   |
|   |                                                    |   |
|   |   +--------------+       +--------------------+   |   |
|   |   |  Game State  |------>|  WebSocket Handler |   |   |
|   |   |  Machine     |       |  (Real-time sync)  |   |   |
|   |   +--------------+       +--------------------+   |   |
|   |         |                        |                |   |
|   |         |                        | broadcast      |   |
|   |   +--------------+       +--------------------+   |   |
|   |   |  Playlist    |       |   HTTP Views       |   |   |
|   |   |  Manager     |       |   (REST API)       |   |   |
|   |   +--------------+       +--------------------+   |   |
|   |         |                        |                |   |
|   |    load |                        | serve          |   |
|   |         v                        |                |   |
|   |   +--------------+       +--------------------+   |   |
|   |   | Media Player |       | Analytics/Stats    |   |   |
|   |   | Service      |       | Storage            |   |   |
|   |   +--------------+       +--------------------+   |   |
|   +---------------------------------------------------+   |
|                          |                                 |
+--------------------------|--------------------------------+
                           | WebSocket + HTTP
                           v
# Frontend (JavaScript)
          +--- Frontend (JavaScript) ---+
          |                             |
    +------------+               +------------+
    |  Admin UI  |               | Player UI  |
    | admin.html |               | player.html|
    +------------+               +------------+
          |
    +------------+     +------------+
    | Dashboard  |     | Analytics  |
    |  (TV view) |     |  Page      |
    +------------+     +------------+
```

## Backend Components

### Game State Machine (`game/state.py`)

Core business logic. Manages the game lifecycle through phases:

- **LOBBY** — Players join via QR code. Admin configures settings.
- **PLAYING** — Song plays, timer counts down, players submit year guesses.
- **REVEAL** — Correct answer shown, scores calculated, fun facts displayed.
- **END** — Final leaderboard, superlative awards, rematch option.
- **PAUSED** — Game frozen when admin disconnects (auto-resumes on reconnect).

Key responsibilities:
- Player session management with reconnection support
- Round lifecycle (song selection, timer, scoring)
- Scoring engine with difficulty presets (Easy/Normal/Hard)
- Streak tracking and power-up unlocking (steal)
- Artist challenge and movie quiz bonus modes
- Superlative award calculation

### WebSocket Handler (`server/websocket.py`)

Real-time bidirectional communication with all connected clients.

- Handles player joins, guess submissions, admin actions, reconnections
- Broadcasts game state changes to all connected clients in parallel with debouncing (see [Key Design Decisions](#key-design-decisions))
- Manages admin disconnect/reconnect with grace period
- Automatic ping/pong heartbeat (30s interval) to prevent proxy timeouts

See [WEBSOCKET.md](WEBSOCKET.md) for the full protocol specification.

### HTTP Views (`server/views.py`)

REST API endpoints for game management and page serving:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/beatify/admin` | GET | Serve admin HTML page |
| `/beatify/play` | GET | Serve player HTML page |
| `/beatify/dashboard` | GET | Serve TV spectator dashboard |
| `/beatify/analytics` | GET | Serve analytics page |
| `/beatify/launcher` | GET | HA sidebar launcher (opens admin in new tab) |
| `/beatify/api/status` | GET | Current game status, media players, playlists |
| `/beatify/api/start-game` | POST | Create a new game with settings |
| `/beatify/api/start-gameplay` | POST | Transition LOBBY to PLAYING |
| `/beatify/api/end-game` | POST | End the current game |
| `/beatify/api/rematch-game` | POST | Start rematch with current players |
| `/beatify/api/game-status` | GET | Check if a game exists (for player join page) |
| `/beatify/api/stats` | GET | Game statistics summary and history |
| `/beatify/api/analytics` | GET | Analytics metrics with caching |
| `/beatify/api/analytics/songs` | GET | Per-song statistics |
| `/beatify/api/playlist-requests` | GET/POST | Manage playlist requests |

### Media Player Service (`services/media_player.py`)

Platform-aware media playback routing:

| Platform | Detection | Playback Method |
|----------|-----------|-----------------|
| Music Assistant | Config entry check | `music_assistant.play_media` service |
| Sonos | Entity registry | Native Sonos media playback |
| Alexa Media Player | Entity registry | `media_content_type: "spotify"` |

Handles volume control, playback start/stop, and provider routing (Spotify, Apple Music, YouTube Music, Tidal).

### Playlist Manager (`game/playlist.py`)

Discovers and loads playlist JSON files from `config/beatify/playlists/`. Each playlist contains songs with metadata: year, URIs (multi-provider), artist, fun facts (multi-language), chart data, and certifications.

### Analytics (`analytics.py`) and Stats (`services/stats.py`)

- **Analytics** — Aggregate metrics: games played, avg players, error rates, trends over time periods
- **Stats** — Per-game and per-song statistics, historical performance tracking

Both store data locally in JSON format with no cloud dependency.

## Frontend

Vanilla JavaScript with IIFE (Immediately Invoked Function Expression) pattern. No frameworks.

### Build System

- **esbuild** for JavaScript bundling and minification
- **lightningcss** for CSS minification
- Source files in `www/js/` and `www/css/`
- Build output: `.min.js` and `.min.css` files
- `npm run build` for production, `npm run build:watch` for development

### Pages

| Page | File | Purpose |
|------|------|---------|
| Admin | `www/admin.html` | Game setup, lobby management, in-game controls |
| Player | `www/player.html` | Join screen, guessing UI, results view |
| Dashboard | `www/dashboard.html` | TV spectator view, leaderboard |
| Analytics | `www/analytics.html` | Game statistics and charts |

### Internationalization

Translation files in `www/i18n/` — JSON key-value files for `en`, `de`, `es`, and `fr`. Language is set per-game by the admin; all players see the same language.

### Real-time Updates

All pages maintain a WebSocket connection. The server broadcasts `state` messages on every change, and clients re-render based on the current phase and game data.

## Data Flow

### Starting a Game

1. Admin loads `/beatify/admin` and selects playlist + speaker
2. Admin POST to `/beatify/api/start-game` with settings
3. Backend creates `GameState`, loads songs, generates join URL + QR code
4. Admin opens WebSocket, sends `join` with `is_admin: true`
5. Players scan QR, open `/beatify/play`, connect via WebSocket
6. Admin POST to `/beatify/api/start-gameplay` to begin

### Playing a Round

1. `GameState.start_round()` selects a random song, starts media playback
2. Server broadcasts `state` with phase=PLAYING and timer deadline
3. Players send `submit` messages with their year guesses
4. When timer expires (or all players submit), `end_round()` fires
5. Server broadcasts `state` with phase=REVEAL, showing scores and correct answer
6. Admin sends `admin.next_round` to continue

### Reconnection

1. Client stores `session_id` from `join_ack`
2. On disconnect, server marks player as disconnected (preserves score/session)
3. Client reconnects WebSocket, sends `reconnect` with stored `session_id`
4. Server restores connection, sends current `state`
5. Admin disconnect triggers 5s grace period, then PAUSED phase

## Key Design Decisions

- **No auth required** — Frictionless party access. Scan QR, play immediately. Designed for trusted local networks only — anyone with network access can join or become admin. Do not expose to untrusted networks without additional security layers (reverse proxy with TLS, access controls).
- **Local-only processing** — No cloud, no subscriptions. All data stays on the local network.
- **Platform detection** — Auto-detect speaker type and show only compatible music services.
- **Vanilla JS** — No framework dependency. Simple, fast, zero build complexity for the end user.
- **Session persistence** — Players can reconnect mid-game without losing score or position.
- **Debounced broadcasts** — Concurrent WebSocket events (e.g., multiple players joining at once) are batched and broadcast together to prevent network congestion and ensure consistent state delivery.
