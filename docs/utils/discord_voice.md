# Discord Voice Module Documentation

The `DiscordVoice` module is a standalone extension designed to integrate with the existing `DiscordClient`. It provides real-time, per-user audio capture from Discord voice channels and the ability to play audio files back into those channels.

---

## Prerequisites & Installation

This module requires **discord.py** (2.8.0 nightly or later) and **PyNaCl** for voice decryption.

```
pip install discord.py PyNaCl
```

> **Note:** Do not use `py-cord` or `nextcord`. This module targets the official `discord.py` library specifically.

**System requirement:** FFmpeg must be installed and available on your system PATH for audio conversion and playback.

---

## How It Works

When a user speaks in a voice channel, the module captures their audio, buffers it, and waits for silence. Once `SILENCE_THRESHOLD` seconds of silence are detected (default 1.5s), the buffered audio is converted to a **16kHz mono WAV** file in memory and yielded from `process_audio_streams()` as a completed utterance. This makes the output ready to pass directly to Whisper or any other STT API without further processing.

Transport encryption (`aead_xchacha20_poly1305_rtpsize`) and DAVE E2EE are handled automatically with no configuration required.

---

## Example Implementation

```python
import time
from agentforge.utils.discord_client import DiscordClient
from agentforge.utils.discord_voice import DiscordVoice

# 1. Initialize and run your core client
client = DiscordClient()
client.run()

# Give the client a moment to establish its connection and event loop
time.sleep(2)

# 2. Initialize the voice module, passing in the core client
voice = DiscordVoice(client)

# 3. Connect to a voice channel
VOICE_CHANNEL_ID = 123456789012345678
voice.connect_voice(VOICE_CHANNEL_ID)

# 4. Main loop
while True:
    try:
        # Process text messages
        for message in client.process_channel_messages():
            print(f"Text: {message}")

        # Process completed voice utterances
        for utterance in voice.process_audio_streams():
            name = utterance['display_name']
            wav  = utterance['wav_bytes']    # 16kHz mono WAV, ready for Whisper
            dur  = utterance['duration']     # seconds of speech captured

            print(f"{name} spoke for {dur:.1f}s")
            # transcribe(wav)

        time.sleep(0.02)

    except KeyboardInterrupt:
        voice.disconnect_voice(GUILD_ID)
        client.stop()
        break
```

---

## Return Data Structure

`process_audio_streams()` is a generator that yields one dictionary per completed utterance (i.e., after silence is detected). It does **not** yield continuous 20ms chunks.

```python
{
    "guild_id":     123456789012345678,   # int
    "user_id":      987654321098765432,   # int
    "display_name": "DataBass",           # str, Discord display name
    "wav_bytes":    b"RIFF...",           # bytes, 16kHz mono WAV
    "duration":     3.2                   # float, seconds of captured audio
}
```

**wav_bytes** is a complete, in-memory WAV file already converted to 16kHz mono PCM by ffmpeg. Pass it directly to Whisper or write it to disk -- no downsampling needed.

---

## Function Reference

### `DiscordVoice(discord_client)`

Constructor. Hooks into the provided `DiscordClient` instance, borrowing its `discord.Client` object, asyncio event loop, and logger.

- **discord_client** *(DiscordClient)*: A running instance of `DiscordClient`.

---

### `connect_voice(channel_id)`

Connects the bot to a voice channel and begins capturing audio.

- **channel_id** *(int)*: The Discord ID of the target voice channel.
- **Returns** *(bool)*: `True` if connected and capturing, `False` on failure.

If the bot is already connected to a different channel in the same server, it disconnects first and reconnects to the new channel.

---

### `process_audio_streams(guild_id=None)`

Generator that yields completed utterances as WAV audio. Poll this continuously in your main loop.

- **guild_id** *(int, optional)*: If provided, yields only utterances from that server. If `None`, yields from all connected servers.
- **Yields** *(dict)*: The utterance structure described above.

An utterance is yielded when a user has been silent for at least `SILENCE_THRESHOLD` seconds (default 1.5s) and the captured audio meets the minimum duration `MIN_SPEECH_DURATION` (default 0.25s).

---

### `play_audio(guild_id, audio_file_path)`

Plays a local audio file into the bot's current voice channel.

- **guild_id** *(int)*: The server ID where the bot is connected.
- **audio_file_path** *(str)*: Path to the audio file (WAV, MP3, etc.).
- **Returns** *(bool)*: `True` if playback started successfully.

If the bot is already playing audio, the current playback is stopped and the new file starts immediately.

---

### `disconnect_voice(guild_id)`

Stops audio capture and disconnects the bot from the voice channel.

- **guild_id** *(int)*: The server ID to disconnect from.
- **Returns** *(bool)*: `True` if disconnected successfully.

---

## Configuration

The following class-level constants on `VoiceReceiver` can be adjusted if needed:

| Constant | Default | Description |
|---|---|---|
| `SILENCE_THRESHOLD` | `1.5` | Seconds of silence before an utterance is finalized |
| `MIN_SPEECH_DURATION` | `0.25` | Minimum seconds of audio required to yield an utterance |
| `SAMPLE_RATE` | `48000` | Discord's native sample rate (do not change) |
| `CHANNELS` | `2` | Discord sends stereo (do not change) |