# Story 8.2: Fix Media Player Discovery Refresh

Status: done

## Story

As a **host**,
I want **the admin page to show all current media players**,
so that **I can select any available speaker for the game**.

## Acceptance Criteria

1. **Given** the admin page loads **When** the status API is called **Then** `async_get_media_players(hass)` is called fresh (not cached)
2. **Given** a new media player is added to Home Assistant **When** the admin page is refreshed **Then** the new media player appears in the list immediately
3. **Given** a media player is removed from Home Assistant **When** the admin page is refreshed **Then** the removed media player no longer appears

## Root Cause Analysis

Media players were cached once at integration setup in `hass.data[DOMAIN]["media_players"]` and never refreshed. The `StatusView.get()` method reads from this cached data instead of fetching fresh from Home Assistant.

**Current code (views.py line 76):**
```python
status = {
    "media_players": data.get("media_players", []),  # Cached data!
    ...
}
```

## Tasks / Subtasks

- [x] Task 1: Fix StatusView to fetch fresh media players (AC: 1, 2, 3)
  - [x] Import `async_get_media_players` from `services.media_player`
  - [x] Call `async_get_media_players(hass)` in `StatusView.get()` instead of reading cached data
  - [x] Return fresh media player list in API response

## Dev Notes

### Implementation

**views.py - StatusView.get() fix:**

```python
# Add import at top of file
from custom_components.beatify.services.media_player import async_get_media_players

# In StatusView.get():
async def get(self, request: web.Request) -> web.Response:
    """Return current status as JSON."""
    data = self.hass.data.get(DOMAIN, {})

    # Check for active game
    game_state = data.get("game")
    active_game = None
    if game_state and game_state.game_id:
        active_game = game_state.get_state()

    # FIXED: Fetch media players fresh instead of using cached data
    media_players = await async_get_media_players(self.hass)

    status = {
        "media_players": media_players,  # Fresh data!
        "playlists": data.get("playlists", []),
        "playlist_dir": data.get("playlist_dir", ""),
        "playlist_docs_url": PLAYLIST_DOCS_URL,
        "media_player_docs_url": MEDIA_PLAYER_DOCS_URL,
        "active_game": active_game,
    }

    return web.json_response(status)
```

### Verify media_player.py service exists

Check that `async_get_media_players` function exists in `custom_components/beatify/services/media_player.py` and returns the expected format:

```python
async def async_get_media_players(hass: HomeAssistant) -> list[dict]:
    """Get all media player entities with their state."""
    media_players = []
    for entity_id in hass.states.async_entity_ids("media_player"):
        state = hass.states.get(entity_id)
        if state:
            media_players.append({
                "entity_id": entity_id,
                "friendly_name": state.attributes.get("friendly_name", entity_id),
                "state": state.state,
            })
    return media_players
```

### File Locations

| File | Path | Lines to Modify |
|------|------|-----------------|
| views.py | `custom_components/beatify/server/views.py` | 65-84 (StatusView.get) |

### Testing

1. Add a new media player to HA while Beatify is running
2. Refresh admin page
3. Verify new media player appears
4. Remove a media player from HA
5. Refresh admin page
6. Verify removed media player is gone

### References

- [Source: epics.md#Story 8.2]
- [Source: project-context.md#Media Player Service Calls]
- [Source: architecture.md#Integration Patterns]

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5

### Debug Log References
N/A

### Completion Notes List
- Added import for async_get_media_players from services.media_player in views.py
- Modified StatusView.get() to call async_get_media_players(self.hass) instead of reading from cached data
- Media players are now fetched fresh on each /beatify/api/status request

### File List
- custom_components/beatify/server/views.py
