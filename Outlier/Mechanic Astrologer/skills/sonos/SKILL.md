---
name: sonos
description: Control Sonos speakers — discover rooms, play/pause music, adjust volume, manage speaker groups, browse favorites, and view playback status. Use when the user asks about music, speakers, playing songs, changing volume, grouping rooms, or home audio.
---

# Sonos

Control Sonos speakers — discover rooms, play/pause, volume, groups, favorites, and queues.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/sonos_cli.py login --email your@email.com
```

## Speaker Control

Use `sonos_cli.py` to control speakers. All output is JSON.

### Discover speakers

```bash
python3 {baseDir}/sonos_cli.py discover
```

### Playback status

```bash
python3 {baseDir}/sonos_cli.py status --name "Living Room"
python3 {baseDir}/sonos_cli.py now --name "Kitchen"
```

### Play / Pause / Stop

```bash
python3 {baseDir}/sonos_cli.py play --name "Living Room"
python3 {baseDir}/sonos_cli.py pause --name "Kitchen"
python3 {baseDir}/sonos_cli.py stop --name "Bedroom"
```

### Skip tracks

```bash
python3 {baseDir}/sonos_cli.py next --name "Living Room"
python3 {baseDir}/sonos_cli.py prev --name "Living Room"
```

### Volume

```bash
python3 {baseDir}/sonos_cli.py volume get --name "Living Room"
python3 {baseDir}/sonos_cli.py volume set 40 --name "Living Room"
```

### Speaker groups

```bash
# See current groups
python3 {baseDir}/sonos_cli.py group status

# Add speaker to a group
python3 {baseDir}/sonos_cli.py group join --name "Kitchen" --to "Living Room"

# Remove speaker from group
python3 {baseDir}/sonos_cli.py group unjoin --name "Kitchen"

# Group all speakers to one room
python3 {baseDir}/sonos_cli.py group party --to "Living Room"

# Make a speaker play on its own
python3 {baseDir}/sonos_cli.py group solo --name "Kitchen"
```

### Favorites

```bash
# List saved favorites
python3 {baseDir}/sonos_cli.py favorites list

# Play a favorite on a speaker (by index number)
python3 {baseDir}/sonos_cli.py favorites open --index 1 --name "Living Room"
```

### Queue

```bash
python3 {baseDir}/sonos_cli.py queue list --name "Living Room"
python3 {baseDir}/sonos_cli.py queue clear --name "Living Room"
```

### Reset to defaults

```bash
python3 {baseDir}/sonos_cli.py reset
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What speakers do I have?" | `sonos_cli.py discover` |
| "What's playing?" | `sonos_cli.py status --name "<room>"` or discover first to find rooms |
| "Play music in the kitchen" | `sonos_cli.py favorites list` then `sonos_cli.py favorites open --index N --name "Kitchen"` |
| "Pause the music" | `sonos_cli.py pause --name "<room>"` |
| "Turn it up" | `sonos_cli.py volume set <higher> --name "<room>"` |
| "Play the same music everywhere" | `sonos_cli.py group party --to "<room>"` |
| "Skip this song" | `sonos_cli.py next --name "<room>"` |
| "What can I listen to?" | `sonos_cli.py favorites list` |
| "Group the kitchen and living room" | `sonos_cli.py group join --name "Kitchen" --to "Living Room"` |
| "Stop the kids' music" | `sonos_cli.py stop --name "Kids Room"` |
| "What's in the queue?" | `sonos_cli.py queue list --name "<room>"` |

## Tips

- **Room names** are case-insensitive and support partial matching ("kitchen" matches "Kitchen", "living" matches "Living Room")
- **Favorites** are the primary way to start music — browse with `favorites list`, play with `favorites open`
- **Groups** sync playback across rooms. The coordinator controls what plays.
- When a speaker joins a group, it plays whatever the coordinator is playing
- Use `discover` first if unsure which rooms exist
- `reset` restores speakers to their default state

## Reference

- `{baseDir}/references/sonos_guide.md` — Sonos speaker models, grouping concepts, and audio tips
