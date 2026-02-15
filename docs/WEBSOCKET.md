# Beatify WebSocket API

Real-time communication protocol between Beatify clients (admin UI, player UI, dashboard) and the Home Assistant backend.

## Quick Start

Minimal client connection example:

```javascript
const ws = new WebSocket("ws://homeassistant.local:8123/beatify/ws");
ws.onopen = () => ws.send(JSON.stringify({ type: "join", name: "Alice" }));
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.type === "state") console.log("Phase:", msg.phase);
};
```

> **Security Note:** This WebSocket endpoint has no authentication. It's designed for trusted local networks (home parties). Do not expose directly to the public internet. For remote access, use a reverse proxy with TLS (`wss://`) and network-level access controls.

## Connection

Connect via WebSocket to your Home Assistant instance:

```
ws://<ha-host>:8123/beatify/ws
```

All messages are JSON. The server sends automatic ping frames every 30 seconds to prevent proxy timeouts.

## Client-to-Server Messages

### `join` — Join a game

```json
{
  "type": "join",
  "name": "PlayerName",
  "is_admin": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Player display name (1-20 chars) |
| `is_admin` | boolean | No | `true` for the game host |

**Success response:** `join_ack` followed by `state`.
**Error codes:** `NAME_TAKEN`, `NAME_INVALID`, `GAME_FULL`, `GAME_ENDED`, `ADMIN_EXISTS`

---

### `submit` — Submit a year guess

```json
{
  "type": "submit",
  "year": 1985,
  "bet": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `year` | integer | Yes | Guessed release year (1950-2025) |
| `bet` | boolean | No | Double-or-nothing bet on this guess |

**Success response:** `submit_ack`, then broadcast `state`.
**Error codes:** `NOT_IN_GAME`, `INVALID_ACTION`, `ALREADY_SUBMITTED`, `ROUND_EXPIRED`

---

### `reconnect` — Reconnect with session ID

```json
{
  "type": "reconnect",
  "session_id": "abc123"
}
```

Resume a disconnected session. The `session_id` is received in the original `join_ack`.

**Success response:** `reconnect_ack` followed by `state`.
**Error codes:** `SESSION_NOT_FOUND`, `GAME_ENDED`

---

### `leave` — Leave the game

```json
{
  "type": "leave"
}
```

Removes the player and closes the WebSocket. Admins cannot leave (use `end_game` instead).

**Success response:** `left`, then server closes the connection.
**Error codes:** `ADMIN_CANNOT_LEAVE`

---

### `get_state` — Request current state

```json
{
  "type": "get_state"
}
```

Returns the full game state. Used by the dashboard/spectator view.

---

### `admin` — Admin actions

All admin actions require the sender to be the game host.

#### Start game

```json
{ "type": "admin", "action": "start_game" }
```

Transitions from LOBBY to PLAYING and starts the first round.

#### Next round

```json
{ "type": "admin", "action": "next_round" }
```

During PLAYING: ends the current round early. During REVEAL: starts next round or ends the game.

#### Stop song

```json
{ "type": "admin", "action": "stop_song" }
```

Stops media playback mid-round. Broadcasts `song_stopped` to all clients.

#### Set volume

```json
{ "type": "admin", "action": "set_volume", "direction": "up" }
```

Adjusts volume by ±10% per step (clamped to 0-100%). `direction` must be `"up"` or `"down"`. Response is sent only to the requesting admin (not broadcast).

#### End game

```json
{ "type": "admin", "action": "end_game" }
```

Transitions to END phase. Players stay connected for the rematch option.

#### Dismiss game

```json
{ "type": "admin", "action": "dismiss_game" }
```

Full teardown. Wipes all players, sends `game_ended` to all clients. Only allowed from END phase.

#### Rematch

```json
{ "type": "admin", "action": "rematch_game" }
```

Soft reset: preserves players, resets scores, returns to LOBBY. Broadcasts `rematch_started`.

#### Set language

```json
{ "type": "admin", "action": "set_language", "language": "de" }
```

Sets the game language. Only allowed in LOBBY. Valid values: `en`, `de`, `es`, `fr`.

---

### `reaction` — Emoji reaction

```json
{
  "type": "reaction",
  "emoji": "fire-emoji"
}
```

Send a live reaction during the REVEAL phase. Allowed emojis: fire, laughing, shocked, clap, thinking. One reaction per player per reveal.

---

### `artist_guess` — Artist challenge guess

```json
{
  "type": "artist_guess",
  "artist": "Queen"
}
```

Submit an artist name guess when artist challenge is active. Awards +5 bonus points to the first correct guesser.

**Error codes:** `NOT_IN_GAME`, `INVALID_ACTION`, `NO_ARTIST_CHALLENGE`

---

### `movie_guess` — Movie quiz guess

```json
{
  "type": "movie_guess",
  "movie": "The Bodyguard"
}
```

Guess which movie a song is from. Tiered bonus points based on speed rank.

**Error codes:** `NOT_IN_GAME`, `INVALID_ACTION`, `NO_MOVIE_CHALLENGE`

---

### `get_steal_targets` — List steal targets

```json
{
  "type": "get_steal_targets"
}
```

Returns available players whose guesses can be stolen. Only visible to the requesting player.

**Error codes:** `NOT_IN_GAME`, `INVALID_ACTION`

---

### `steal` — Execute steal power-up

```json
{
  "type": "steal",
  "target": "OtherPlayer"
}
```

Copy another player's submitted guess. Requires a 3-streak to unlock, max 1 per game.

**Error codes:** `NOT_IN_GAME`, `INVALID_ACTION`, `NO_STEAL_AVAILABLE`, `TARGET_NOT_SUBMITTED`, `CANNOT_STEAL_SELF`

---

## Server-to-Client Messages

### `join_ack` — Join confirmation

```json
{
  "type": "join_ack",
  "session_id": "uuid-string",
  "game_id": "game-uuid"
}
```

Sent only to the joining player. Store `session_id` for reconnection.

### `state` — Full game state

```json
{
  "type": "state",
  "phase": "PLAYING",
  "round": 3,
  "total_rounds": 10,
  "players": [...],
  "...": "..."
}
```

Broadcast to all clients on every state change (join, submit, round change, etc.).

### `submit_ack` — Guess acknowledged

```json
{
  "type": "submit_ack",
  "year": 1985
}
```

### `reconnect_ack` — Reconnection confirmed

```json
{
  "type": "reconnect_ack",
  "name": "PlayerName",
  "success": true
}
```

### `song_stopped` — Song playback stopped

```json
{
  "type": "song_stopped"
}
```

Broadcast when admin stops the current song.

### `volume_changed` — Volume adjusted

```json
{
  "type": "volume_changed",
  "level": 0.7
}
```

Sent only to the admin who adjusted volume. `level` is 0.0-1.0.

### `metadata_update` — Song metadata available

```json
{
  "type": "metadata_update",
  "song": {
    "artist": "Queen",
    "title": "Bohemian Rhapsody",
    "album_art": "https://..."
  }
}
```

Sent when metadata becomes available after round start (async fetch).

### `player_reaction` — Emoji reaction broadcast

```json
{
  "type": "player_reaction",
  "player_name": "Sarah",
  "emoji": "fire-emoji"
}
```

### `artist_guess_ack` — Artist guess result

```json
{
  "type": "artist_guess_ack",
  "correct": true,
  "first": true,
  "bonus_points": 5
}
```

If someone else guessed first: `{"correct": true, "first": false, "winner": "OtherPlayer"}`.

### `movie_guess_ack` — Movie guess result

```json
{
  "type": "movie_guess_ack",
  "correct": true,
  "already_guessed": false,
  "rank": 1,
  "bonus": 5
}
```

### `steal_targets` — Available steal targets

```json
{
  "type": "steal_targets",
  "targets": [
    {"name": "Player1", "...": "..."}
  ]
}
```

### `steal_ack` — Steal result

```json
{
  "type": "steal_ack",
  "success": true,
  "target": "Player1",
  "year": 1985
}
```

### `left` — Leave confirmed

```json
{
  "type": "left"
}
```

Server closes the connection after this message.

### `game_ended` — Game dismissed

```json
{
  "type": "game_ended"
}
```

Broadcast on full game teardown. Clients should return to the landing screen.

### `rematch_started` — Rematch initiated

```json
{
  "type": "rematch_started"
}
```

Broadcast when admin starts a rematch. Clients transition to LOBBY.

### `error` — Error response

```json
{
  "type": "error",
  "code": "NAME_TAKEN",
  "message": "Name taken, choose another"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `NAME_TAKEN` | Another player already has this name |
| `NAME_INVALID` | Name is empty or invalid |
| `GAME_NOT_STARTED` | No active game exists |
| `GAME_ENDED` | Game has finished |
| `GAME_FULL` | Maximum 20 players reached |
| `NOT_ADMIN` | Action requires admin privileges |
| `ADMIN_EXISTS` | Game already has a host |
| `ADMIN_CANNOT_LEAVE` | Host must end game, not leave |
| `ROUND_EXPIRED` | Timer ran out before submission |
| `ALREADY_SUBMITTED` | Player already guessed this round |
| `NOT_IN_GAME` | Player not found in the game |
| `INVALID_ACTION` | Action not allowed in current phase |
| `MEDIA_PLAYER_UNAVAILABLE` | Speaker not responding |
| `NO_SONGS_REMAINING` | Playlist exhausted |
| `SESSION_NOT_FOUND` | Invalid or expired session ID |
| `SESSION_TAKEOVER` | Another tab took over this session |
| `NO_ARTIST_CHALLENGE` | No artist challenge this round |
| `NO_MOVIE_CHALLENGE` | No movie quiz this round |

## Game Phases

```
LOBBY  -->  PLAYING  -->  REVEAL  -->  PLAYING  (loop)
                                           |
                                           v
                                          END  -->  LOBBY (rematch)
                                           |
                                           v
                                       (dismiss)

PLAYING can also transition to PAUSED if admin disconnects.
PAUSED resumes to PLAYING when admin reconnects.
```

## Connection Lifecycle

1. Client opens WebSocket connection
2. Server adds connection to pool
3. Client sends `join` or `reconnect`
4. Server responds with `join_ack`/`reconnect_ack` + `state`
5. Server broadcasts `state` on all game events
6. On disconnect: server marks player as disconnected, preserves session
7. Client can reconnect with stored `session_id` at any time
8. Admin disconnect triggers 5-second grace period before game pauses
