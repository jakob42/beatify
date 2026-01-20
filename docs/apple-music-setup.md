# Apple Music Setup Guide for Beatify

This guide explains how to configure Apple Music as a music provider for Beatify using Music Assistant.

## Prerequisites

Before you begin, ensure you have:

- **Home Assistant** installed and running (version 2024.1 or later recommended)
- **HACS** (Home Assistant Community Store) installed
- An **Apple Music subscription** (Individual, Family, or Student)
- A **Music Assistant-compatible media player** (e.g., Sonos, Chromecast, or any HA media player)

## Step 1: Install Music Assistant

Music Assistant is the bridge between Home Assistant and Apple Music. It must be installed as a Home Assistant add-on.

1. Open Home Assistant
2. Go to **Settings** > **Add-ons** > **Add-on Store**
3. Search for "Music Assistant"
4. Click **Install**
5. After installation, click **Start**
6. Enable "Start on boot" and "Watchdog" for reliability

For detailed instructions, see the [official Music Assistant documentation](https://music-assistant.io/).

## Step 2: Add Apple Music Provider

Once Music Assistant is running:

1. Open the **Music Assistant** panel from the Home Assistant sidebar
2. Go to **Settings** (gear icon) > **Providers**
3. Click **Add Provider**
4. Select **Apple Music** from the list
5. You'll see a field requesting a "Music User Token"

The next step explains how to obtain this token.

## Step 3: Get Your Music User Token

Apple Music requires a "Music User Token" for authentication. This token is extracted from your browser cookies after signing into Apple Music.

### Browser Instructions (Chrome/Edge/Firefox)

1. Open your browser and go to [music.apple.com](https://music.apple.com)
2. **Sign in** with your Apple ID (the one with your Apple Music subscription)
3. Make sure you can see your library and play music (this confirms you're authenticated)
4. Open **Developer Tools**:
   - **Windows/Linux**: Press `F12` or `Ctrl + Shift + I`
   - **Mac**: Press `Cmd + Option + I`
5. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox)
6. In the left sidebar, expand **Cookies** > **https://music.apple.com**
7. Find the cookie named `media-user-token`
8. Click on it to select it
9. **Copy the entire value** (it's a very long string of characters)
10. Paste this value into the Music Assistant Apple Music provider configuration
11. Click **Save**

### Safari Instructions (Mac)

1. Enable Developer menu: **Safari** > **Settings** > **Advanced** > Check "Show Develop menu"
2. Go to [music.apple.com](https://music.apple.com) and sign in
3. Open **Develop** > **Show Web Inspector** (or `Cmd + Option + I`)
4. Go to **Storage** > **Cookies**
5. Find and copy the `media-user-token` value

## Step 4: Token Expiration & Renewal

### Important: Tokens Expire

The Music User Token expires after approximately **6 months**. When it expires, Apple Music playback will stop working.

### Symptoms of an Expired Token

- Playback fails silently or shows errors
- Music Assistant logs show `401 Unauthorized` errors
- Apple Music tracks won't play, but other providers (like Spotify) still work

### How to Renew Your Token

1. Sign out of Apple Music web player
2. Sign back in at [music.apple.com](https://music.apple.com)
3. Extract the new `media-user-token` using the same steps as above
4. Update the token in Music Assistant:
   - Go to **Music Assistant** > **Settings** > **Providers**
   - Find **Apple Music** and click **Configure**
   - Paste the new token
   - Click **Save**

Consider setting a calendar reminder for ~5 months to renew your token before it expires.

## Step 5: Verify Setup in Beatify

After configuring Music Assistant with Apple Music:

1. **Test in Music Assistant first**:
   - Open Music Assistant
   - Search for a song
   - Try to play it on your media player
   - Confirm playback works

2. **Test in Beatify**:
   - Open the Beatify admin page
   - Select a media player that shows `music_assistant` in its name
   - Choose **Apple Music** as the music provider
   - Select a playlist with Apple Music URIs
   - Start a game and verify songs play correctly

## Troubleshooting

### "Apple Music option is disabled"

The Apple Music option in Beatify requires a Music Assistant media player. If you don't see any `music_assistant_*` players:

1. Verify Music Assistant is running
2. Check that you've added a media player in Music Assistant
3. Refresh the Beatify admin page

### "Playback fails with 401 error"

Your token has likely expired. Follow the renewal steps above.

### "Songs don't play but no error shown"

1. Check Music Assistant logs for errors
2. Verify the media player is powered on and available
3. Try playing directly through Music Assistant first
4. Ensure the song has an Apple Music URI in the playlist

### "Some songs don't have Apple Music URIs"

Beatify playlists can contain songs for multiple providers. If a song shows "0/N" coverage for Apple Music, it means those songs don't have Apple Music URIs yet. You can:

1. Use playlists with full Apple Music coverage
2. Add Apple Music URIs to your playlist JSON files

## Additional Resources

- [Music Assistant Documentation](https://music-assistant.io/)
- [Music Assistant Apple Music Provider](https://music-assistant.io/music-providers/apple-music/)
- [Beatify GitHub Repository](https://github.com/beatify/beatify)
- [Home Assistant Community Forums](https://community.home-assistant.io/)
