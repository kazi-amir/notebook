# Sonos Speaker Guide

Reference for understanding Sonos speaker systems, models, and concepts.

## Speaker Models

| Model | Type | Key Features | Model # |
|-------|------|-------------|---------|
| Sonos Arc | Premium soundbar | Dolby Atmos, 11 drivers, TV + music | S23 |
| Sonos Beam | Compact soundbar | Dolby Atmos, HDMI eARC, TV + music | S22 |
| Sonos Five | Premium speaker | Stereo, line-in, room-filling sound | S27 |
| Era 100 | Compact speaker | Bluetooth, Wi-Fi, voice assistant | S36 |
| Era 300 | Spatial audio speaker | Dolby Atmos music, 6 drivers | S37 |
| Move 2 | Portable speaker | Battery (24 hrs), Bluetooth + Wi-Fi, IP56 | S39 |
| Sub | Subwoofer | Pairs with Arc/Beam/Five for bass | S21 |

## Playback States

| State | Meaning |
|-------|---------|
| PLAYING | Audio is currently playing |
| PAUSED | Audio is paused at current position |
| STOPPED | Audio is stopped, position reset to start |
| IDLE | No audio loaded, speaker is available |

## Grouping Concepts

### How Groups Work

- A **group** consists of a **coordinator** and one or more **members**
- The coordinator controls playback — what plays, queue position, play/pause state
- All members play the same audio in sync
- Each speaker keeps its own volume (volume is not synced)

### Group Operations

| Operation | What Happens |
|-----------|-------------|
| **Join** | Speaker joins a group, syncs to coordinator's playback |
| **Unjoin** | Speaker leaves group, pauses with last playing track |
| **Party** | All speakers join one mega-group |
| **Solo** | Speaker leaves its group, pauses independently |

### Coordinator Behavior

- If the coordinator leaves a group, the next member is promoted to coordinator
- If a group shrinks to 1 member, the group dissolves
- Playback commands (play/pause/next) on any group member affect the coordinator

## Volume

- Volume is per-speaker (0-100)
- Each speaker in a group maintains its own volume level
- Setting volume to 0 is equivalent to muting
- Volume changes are instant and persist between sessions

## Favorites

Favorites are saved shortcuts to playlists, radio stations, albums, or artists.

| Type | Behavior When Played |
|------|---------------------|
| **playlist** | Loads tracks into queue, starts playing first track |
| **album** | Same as playlist — loads album tracks |
| **artist** | Loads artist's top tracks |
| **radio** | Starts streaming (no queue, continuous playback) |

Radio streams have `duration_seconds: null` since they play indefinitely.

## Audio Sources

| Source | Type | Notes |
|--------|------|-------|
| Spotify | Streaming | Most common, playlists and tracks |
| Apple Music | Streaming | Alternative streaming service |
| TuneIn | Radio | Live radio stations, news, sports |
| Amazon Music | Streaming | Available on newer models |

## Common Scenarios

### Background Music While Cooking

1. `discover` to find kitchen speaker
2. `favorites list` to see available playlists
3. `favorites open --index N --name "Kitchen"` to start music
4. `volume set 30 --name "Kitchen"` for comfortable level

### Whole-Home Party Mode

1. `group party --to "Living Room"` to group all speakers
2. `favorites open --index N --name "Living Room"` to start party playlist
3. Adjust individual room volumes with `volume set`
4. `group status` to verify all speakers are grouped

### Movie Night (Soundbar)

1. Stop music on the soundbar: `stop --name "Living Room"`
2. If needed, `group solo --name "Living Room"` to ungroup from other speakers
3. Set appropriate volume: `volume set 45 --name "Living Room"`

### Bedtime Routine

1. `stop --name "Kids Room"` to stop kids' music
2. `favorites open --index N --name "Kids Room"` to play lullabies
3. `volume set 15 --name "Kids Room"` for quiet level
4. Later: `stop --name "Kids Room"` to silence
