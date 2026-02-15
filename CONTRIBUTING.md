# Contributing to Beatify

Thanks for your interest in making Beatify better!

Whether you're fixing a bug, adding a playlist, improving translations, or building a new feature — you're welcome here.

## Quick Links

- [Issues](https://github.com/mholzi/beatify/issues) — Bug reports & feature requests
- [Discussions](https://github.com/mholzi/beatify/discussions) — Questions & ideas
- [Good First Issues](https://github.com/mholzi/beatify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) — Great starting points

---

## Development Setup

### Prerequisites

- [Home Assistant](https://www.home-assistant.io/) 2024.1+
- [Music Assistant](https://music-assistant.io/) with a connected music provider (Spotify, Apple Music, YouTube Music, or Tidal)
- Python 3.12+
- Node.js 18+ (for frontend build)

### Clone & Install

```bash
# Clone the repo
git clone https://github.com/mholzi/beatify.git
cd beatify

# Python dependencies (for running tests)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_test.txt

# Node dependencies (for frontend build)
npm install
```

### Run Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

The test suite includes unit, integration, and end-to-end tests. See `tests/README.md` for the full testing guide.

### Build Frontend

```bash
# Build minified JS/CSS
npm run build

# Development build (unminified)
npm run build:dev

# Watch mode (auto-rebuild on changes)
npm run build:watch
```

### Local Testing with Home Assistant

1. Copy (or symlink) `custom_components/beatify/` into your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Add the Beatify integration via Settings > Integrations

---

## Project Structure

```
custom_components/beatify/
  __init__.py           # Integration setup, lifecycle
  const.py              # Constants: scoring, limits, error codes
  config_flow.py        # HA config flow
  analytics.py          # Aggregate game analytics
  manifest.json         # Integration metadata
  game/
    state.py            # Core game state machine (phases, scoring, rounds)
    player.py           # Player session management
    playlist.py         # Playlist discovery and loading
    scoring.py          # Scoring logic
  server/
    websocket.py        # WebSocket handler (real-time sync)
    views.py            # HTTP endpoints (REST API + page serving)
  services/
    media_player.py     # Platform-aware media playback routing
    stats.py            # Per-game/per-song statistics
  playlists/            # JSON playlist files (18 playlists, 2,008 songs)
  www/                  # Frontend assets
    admin.html          # Admin interface
    player.html         # Player interface
    dashboard.html      # TV spectator view
    analytics.html      # Analytics dashboard
    js/                 # Vanilla JS source + minified bundles
    css/                # Stylesheets
    i18n/               # Translation files (EN, DE, ES, FR)
  translations/         # HA config flow translations
```

For architecture details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). For the WebSocket protocol, see [docs/WEBSOCKET.md](docs/WEBSOCKET.md).

---

## How to Contribute

### Add a Playlist (Easiest!)

Playlists are JSON files in `custom_components/beatify/playlists/`. No Python knowledge required.

**Requirements for playlists:**
- Minimum **100 songs** per playlist
- Every song needs: `year`, `uri` (Spotify), `artist`, `alt_artists` (3 wrong choices), `title`
- Fun facts in English required; German, Spanish, and French appreciated
- Cross-platform URIs (`uri_youtube_music`, `uri_tidal`) optional but welcome
- Use `scripts/enrich_playlists.py` to auto-populate cross-platform URIs

**Playlist JSON structure:**

```json
{
  "name": "Your Playlist Name",
  "version": 1,
  "tags": ["genre", "decade"],
  "songs": [
    {
      "year": 1985,
      "uri": "spotify:track:...",
      "artist": "Artist Name",
      "alt_artists": ["Wrong Choice 1", "Wrong Choice 2", "Wrong Choice 3"],
      "title": "Song Title",
      "chart_info": {
        "billboard_peak": 1,
        "uk_peak": 5,
        "weeks_on_chart": 20
      },
      "certifications": ["Gold (US)"],
      "awards": [],
      "awards_de": [],
      "awards_es": [],
      "fun_fact": "English fun fact about the song.",
      "fun_fact_de": "Deutscher Fun Fact.",
      "fun_fact_es": "Fun fact en espanol.",
      "fun_fact_fr": "Anecdote en francais.",
      "uri_youtube_music": "https://music.youtube.com/watch?v=...",
      "uri_tidal": "tidal://track/..."
    }
  ]
}
```

**Steps:**
1. Create an issue using the Playlist Request template
2. Fork the repo, create a branch (`playlist/your-playlist-name`)
3. Add your JSON file to `custom_components/beatify/playlists/`
4. Submit a PR

See [docs/PLAYLIST_ENRICHMENT_RUNBOOK.md](docs/PLAYLIST_ENRICHMENT_RUNBOOK.md) for the full playlist creation guide.

### Fix a Bug

1. Check [open issues](https://github.com/mholzi/beatify/issues) or report a new one
2. Fork the repo, create a branch (`fix/issue-number-short-description`)
3. Write your fix
4. Add/update tests if applicable
5. Run `pytest tests/ -v` to make sure nothing breaks
6. Submit a PR

### Add a Feature

1. Open an issue first to discuss the feature
2. Wait for approval before starting work (to avoid wasted effort)
3. Fork the repo, create a branch (`feature/issue-number-short-description`)
4. Implement the feature
5. Add tests
6. Submit a PR

### Improve Translations

Beatify supports English, German, Spanish, and French. Translation files:

- **Frontend (player UI):** `custom_components/beatify/www/i18n/{en,de,es,fr}.json`
- **HA config flow:** `custom_components/beatify/translations/en.json`

Want to add a new language? Create the JSON file following the English structure and submit a PR.

---

## Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<issue>-<description>` | `feature/28-movie-quiz-bonus` |
| Bug fix | `fix/<issue>-<description>` | `fix/124-song-metadata-desync` |
| Playlist | `playlist/<name>` | `playlist/classic-rock-essentials` |
| Docs | `docs/<description>` | `docs/92-screenshots-gallery` |

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add movie quiz bonus round (#28)
fix: Use playlist metadata as source of truth (#124)
docs: Add CONTRIBUTING.md (#126)
feat(playlists): Classic Rock Essentials — 100 tracks (#85)
```

## Code Style

- **Python:** Follow existing patterns. Use `ruff` for linting.
- **JavaScript:** Vanilla JS, `var` declarations, IIFE pattern. Use `CSS.escape()` for selectors.
- **CSS:** Mobile-first, no frameworks.
- **Do NOT** edit `.min.js` or `.min.css` files directly — use `npm run build`.

## Pull Requests

- One feature/fix per PR
- Reference the issue number (e.g., "Fixes #124")
- Squash merge is preferred
- Keep PRs focused and reviewable

---

## Release Schedule

- **Mondays:** Patches and playlists (vX.Y.Z)
- **Thursdays:** Features (vX.Y.0)

---

## Questions?

Open a [Discussion](https://github.com/mholzi/beatify/discussions) or check existing issues. We're happy to help!
