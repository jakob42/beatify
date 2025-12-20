---
project_name: 'Beatify'
user_name: 'Markusholzhaeuser'
date: '2025-12-18'
---

# Project Context for AI Agents

_Critical rules and patterns for implementing Beatify - a Home Assistant party game integration._

---

## Technology Stack

| Technology | Version | Notes |
|------------|---------|-------|
| Python | 3.11+ | HA requirement |
| Home Assistant | 2025.11+ | Target platform |
| aiohttp | (HA bundled) | WebSocket & HTTP |

---

## Constants (const.py)

```python
DOMAIN = "beatify"
MAX_PLAYERS = 20
MIN_PLAYERS = 2
RECONNECT_TIMEOUT = 60  # seconds
DEFAULT_ROUND_DURATION = 30  # seconds
MAX_NAME_LENGTH = 20
MIN_NAME_LENGTH = 1
LOBBY_DISCONNECT_GRACE_PERIOD = 5  # seconds before removing disconnected player

# Year range for guesses
YEAR_MIN = 1950
YEAR_MAX = 2025

# Volume control step (10%)
VOLUME_STEP = 0.1

# Streak milestone bonuses (awarded at exact streak counts)
STREAK_MILESTONES: dict[int, int] = {3: 20, 5: 50, 10: 100}

# Error codes
ERR_NAME_TAKEN = "NAME_TAKEN"
ERR_NAME_INVALID = "NAME_INVALID"
ERR_GAME_NOT_STARTED = "GAME_NOT_STARTED"
ERR_GAME_ALREADY_STARTED = "GAME_ALREADY_STARTED"
ERR_GAME_ENDED = "GAME_ENDED"
ERR_NOT_ADMIN = "NOT_ADMIN"
ERR_ADMIN_EXISTS = "ADMIN_EXISTS"
ERR_ROUND_EXPIRED = "ROUND_EXPIRED"
ERR_ALREADY_SUBMITTED = "ALREADY_SUBMITTED"
ERR_NOT_IN_GAME = "NOT_IN_GAME"
ERR_MEDIA_PLAYER_UNAVAILABLE = "MEDIA_PLAYER_UNAVAILABLE"
ERR_INVALID_ACTION = "INVALID_ACTION"
ERR_GAME_FULL = "GAME_FULL"
ERR_NO_SONGS_REMAINING = "NO_SONGS_REMAINING"
```

---

## Critical Implementation Rules

### Home Assistant Integration

- Use `async_setup_entry` / `async_unload_entry` pattern
- Store integration data in `hass.data[DOMAIN]`
- Use `_LOGGER = logging.getLogger(__name__)` for all logging
- Validate at least one media_player entity exists in config flow

### WebSocket (Custom, NOT HA's websocket_api)

- Endpoint: `/beatify/ws` via custom aiohttp handler
- NO authentication (frictionless player access)
- All message fields: `snake_case`
- Message types: `join`, `submit`, `admin`, `state`, `error`, `submit_ack`, `song_stopped`, `volume_changed`

```python
# Server → Client state broadcast
{
    "type": "state",
    "phase": "LOBBY|PLAYING|REVEAL|END",
    "round": int,
    "total_rounds": int,
    "deadline": int,  # Unix timestamp ms (PLAYING only)
    "players": [{"name": str, "score": int, "submitted": bool, "streak": int, "connected": bool}],
    "song": {"artist": str, "title": str, "album_art": str}  # year/fun_fact hidden until REVEAL
}
```

### State Machine (game/state.py)

Valid transitions ONLY:
```
LOBBY → PLAYING (admin starts)
PLAYING → REVEAL (timer expires OR all submitted)
REVEAL → PLAYING (next round)
REVEAL → END (final round)
Any → PAUSED (admin disconnects)
PAUSED → previous (admin reconnects)
```

Reject invalid transitions with error, do not silently ignore.

### Player Session Management

- Identify players by `name` (unique per game)
- Name length: 1-20 characters
- 60-second grace period on disconnect
- Reconnect by same name within window → restore score
- After timeout → session discarded, name available

### Media Player Service Calls

```python
# Play a track
await hass.services.async_call(
    "media_player",
    "play_media",
    {
        "entity_id": media_player_entity,
        "media_content_id": song_uri,  # e.g., "spotify:track:xxx"
        "media_content_type": "music"
    }
)

# Get track metadata after playback starts
state = hass.states.get(media_player_entity)
artist = state.attributes.get("media_artist", "Unknown Artist")
title = state.attributes.get("media_title", "Unknown Title")
artwork = state.attributes.get("entity_picture", "/beatify/static/img/no-artwork.svg")
```

### Playlist Format

Location: `{HA_CONFIG}/beatify/playlists/*.json`

```json
{
  "name": "80s Hits",
  "songs": [
    {"year": 1984, "uri": "spotify:track:xxx", "fun_fact": "Written in 10 minutes"}
  ]
}
```

- `year` and `fun_fact` are authoritative (manually curated)
- `artist`, `title`, `album_art` fetched from media_player entity attributes at runtime
- Validate all URIs at game start, warn host of failures

---

## Scoring Algorithm (game/scoring.py)

Scoring order: Base → Speed multiplier → Bet multiplier → Streak bonus (added after, not multiplied)

```python
# 1. Base score from accuracy
def calculate_base_score(diff: int) -> int:
    if diff == 0: return 10
    elif diff == 1: return 7
    elif diff <= 3: return 5
    elif diff <= 5: return 3
    else: return 1

# 2. Speed multiplier (1.5x instant → 1.0x at deadline)
speed_multiplier = 1.5 - (0.5 * submission_time_ratio)
speed_adjusted = int(base_score * speed_multiplier)

# 3. Bet multiplier (applied to speed-adjusted score)
if bet:
    round_score = speed_adjusted * 2 if diff <= 3 else 0
    bet_outcome = "won" if diff <= 3 else "lost"
else:
    round_score = speed_adjusted

# 4. Streak bonus (milestone-based, added AFTER bet, not multiplied)
# Awarded at exact milestones: 3-streak=+20, 5-streak=+50, 10-streak=+100
STREAK_MILESTONES = {3: 20, 5: 50, 10: 100}
streak_bonus = STREAK_MILESTONES.get(streak, 0)

# Total = round_score + streak_bonus
total_score = round_score + streak_bonus
```

**No submission = 0 points, streak resets, previous_streak stored for "lost X-streak" display.**

---

## Naming Conventions

| Context | Convention | Example |
|---------|------------|---------|
| Python files | snake_case | `game_state.py` |
| Python classes | PascalCase | `GameState` |
| Python functions | snake_case | `get_current_round()` |
| Python constants | UPPER_SNAKE | `MAX_PLAYERS = 20` |
| JS files | kebab-case | `player-client.js` |
| JS variables | camelCase | `playerName` |
| CSS classes | kebab-case | `.player-card` |
| CSS states | is- prefix | `.is-active` |
| WS message fields | snake_case | `player_name` |
| Error codes | UPPER_SNAKE | `NAME_TAKEN` |

---

## Frontend Rules (www/)

### JavaScript
- Vanilla JS only (no jQuery, no frameworks)
- All WS field conversion: `snake_case` → `camelCase` on receive
- Reconnect with exponential backoff (1s, 2s, 4s, max 30s)

### CSS
- Mobile-first: use `min-width` breakpoints, not `max-width`
- Touch targets: minimum 44x44px
- Year slider: `<input type="range">` with custom styling

### Assets
- Album art fallback: `www/img/no-artwork.svg`
- Never leave `<img src="">` empty

---

## Testing Rules

### Structure
- Tests in `tests/` directory (not co-located)
- File naming: `test_*.py`

### Time Injection
```python
def test_round_expiry():
    state = GameState(time_fn=lambda: 1000.0)
    # Control time in tests
```

### WebSocket Testing
```python
@pytest.fixture
async def ws_client(aiohttp_client):
    """Test client for WebSocket handlers."""
    from custom_components.beatify.server.websocket import create_app
    app = create_app(mock_game_state)
    client = await aiohttp_client(app)
    async with client.ws_connect('/beatify/ws') as ws:
        yield ws

async def test_player_join(ws_client):
    await ws_client.send_json({"type": "join", "name": "Tom"})
    msg = await ws_client.receive_json()
    assert msg["type"] == "state"
```

### Mocking
- Mock HA: `MagicMock()`
- Mock media_player service: `AsyncMock()`
- Test each state transition as a separate test case

---

## Anti-Patterns (DO NOT)

- ❌ Use HA's `websocket_api` (requires auth, breaks frictionless UX)
- ❌ Store player data persistently (in-memory only)
- ❌ Send `year` or `fun_fact` during PLAYING phase
- ❌ Allow invalid state transitions silently
- ❌ Use camelCase in Python code
- ❌ Use snake_case in JavaScript code
- ❌ Hardcode IP addresses (use HA's network detection)
- ❌ Block the event loop (always use async)
- ❌ Leave empty image src (use `no-artwork.svg` placeholder)
- ❌ Guess scoring formula (use exact algorithm above)

---

## File Structure Reference

```
custom_components/beatify/
├── __init__.py          # async_setup_entry, async_unload_entry
├── const.py             # DOMAIN, MAX_PLAYERS, error codes
├── config_flow.py       # UI setup, media player validation
├── game/
│   ├── state.py         # GameState class, state machine
│   ├── scoring.py       # Points calculation (exact formula)
│   ├── player.py        # Session management
│   └── playlist.py      # JSON loading, validation
├── server/
│   ├── views.py         # HomeAssistantView classes
│   ├── websocket.py     # Custom aiohttp WS handler
│   └── messages.py      # Serialize/deserialize
├── services/
│   └── media_player.py
└── www/
    ├── admin.html
    ├── player.html
    ├── css/styles.css
    ├── js/
    │   ├── admin.js
    │   ├── player.js
    │   └── ws-client.js
    └── img/
        └── no-artwork.svg
```

---

## Import Order (Python)

```python
# 1. Standard library
import logging
from typing import Any

# 2. Third-party
import aiohttp

# 3. Home Assistant
from homeassistant.core import HomeAssistant

# 4. Local
from .const import DOMAIN
from .game.state import GameState
```

---

_Last updated: 2025-12-20_
_Source: architecture.md, Epic 5 & Epic 6 implementations_
