import discord
import discord.opus
import asyncio
import os
import time
import subprocess
import threading
import traceback
import struct
from collections import defaultdict
from agentforge.utils.logger import Logger


# ========================================================================
# [AGENTFORGE EXCLUSIVE HACK] - Thread Assassin Catcher
# ========================================================================
def _global_thread_crash_catcher(args):
    crash_logger = Logger(name='ThreadAssassin', default_logger='discord')
    tb_str = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
    error_msg = (
        f"[🚨 THREAD ASSASSINATION DETECTED 🚨]\n"
        f"Thread Name: {args.thread.name if args.thread else 'Unknown'}\n"
        f"Error Type: {args.exc_type.__name__ if args.exc_type else 'Unknown'}\n"
        f"Error Message: {args.exc_value}\n"
        f"Traceback:\n{tb_str}"
    )
    crash_logger.critical(error_msg)


threading.excepthook = _global_thread_crash_catcher


# ========================================================================
# NATIVE VOICE RECEIVER: Flawless Decryption & Padding Handling
# ========================================================================
class VoiceReceiver:
    """
    Captures and decodes voice audio directly from a Discord UDP socket listener.
    Handles NaCl transport decryption, RTP padding removal, DAVE E2EE decryption,
    and Opus decoding natively. (Adapted from Hermes-Agent example.py)
    """
    SILENCE_THRESHOLD = 1.5
    MIN_SPEECH_DURATION = 0.25
    SAMPLE_RATE = 48000
    CHANNELS = 2

    def __init__(self, voice_client, logger: Logger):
        self._vc = voice_client
        self.logger = logger
        self._running = False
        self._paused = False

        self._secret_key = None
        self._bot_ssrc = 0
        self._dave_session = None

        self._ssrc_to_user = {}
        self._lock = threading.Lock()

        self._buffers = defaultdict(bytearray)
        self._last_packet_time = {}
        self._decoders = {}

    def start(self):
        conn = self._vc._connection
        self._secret_key = bytes(conn.secret_key)
        self._dave_session = getattr(conn, 'dave_session', None)
        self._bot_ssrc = conn.ssrc

        self._install_speaking_hook(conn)
        conn.add_socket_listener(self._on_packet)
        self._running = True
        self.logger.info("VoiceReceiver started")

    def stop(self):
        self._running = False
        try:
            self._vc._connection.remove_socket_listener(self._on_packet)
        except Exception:
            pass
        with self._lock:
            self._buffers.clear()
            self._last_packet_time.clear()
            self._decoders.clear()
            self._ssrc_to_user.clear()
        self.logger.info("VoiceReceiver stopped")

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def map_ssrc(self, ssrc: int, user_id: int):
        with self._lock:
            self._ssrc_to_user[ssrc] = user_id

    def _install_speaking_hook(self, conn):
        """Intercepts the op 5 SPEAKING event to map SSRC identifiers to User IDs."""
        original_hook = conn.hook
        receiver_self = self

        async def wrapped_hook(ws, msg):
            if isinstance(msg, dict) and msg.get("op") == 5:
                data = msg.get("d", {})
                ssrc = data.get("ssrc")
                user_id = data.get("user_id")
                if ssrc and user_id:
                    self.logger.info(f"SPEAKING event: ssrc={ssrc} -> user={user_id}")
                    receiver_self.map_ssrc(int(ssrc), int(user_id))
            if original_hook:
                await original_hook(ws, msg)

        conn.hook = wrapped_hook
        try:
            from discord.utils import MISSING
            if hasattr(conn, 'ws') and conn.ws is not MISSING:
                conn.ws._hook = wrapped_hook
                self.logger.info("Speaking hook installed on live websocket")
        except Exception as e:
            self.logger.warning(f"Could not install hook on live ws: {e}")

    def _on_packet(self, data: bytes):
        if not self._running or self._paused:
            return

        if len(data) < 16:
            return

        first_byte = data[0]
        _, _, seq, timestamp, ssrc = struct.unpack_from(">BBHII", data, 0)

        # Skip bot's own audio
        if ssrc == self._bot_ssrc:
            return

        cc = first_byte & 0x0F
        has_extension = bool(first_byte & 0x10)
        has_padding = bool(first_byte & 0x20)
        header_size = 12 + (4 * cc) + (4 if has_extension else 0)

        if len(data) < header_size + 4:
            return

        ext_data_len = 0
        if has_extension:
            ext_preamble_offset = 12 + (4 * cc)
            ext_words = struct.unpack_from(">H", data, ext_preamble_offset + 2)[0]
            ext_data_len = ext_words * 4

        header = bytes(data[:header_size])
        payload_with_nonce = data[header_size:]

        # --- NaCl transport decrypt (aead_xchacha20_poly1305_rtpsize) ---
        if len(payload_with_nonce) < 4:
            return
        nonce = bytearray(24)
        nonce[:4] = payload_with_nonce[-4:]
        encrypted = bytes(payload_with_nonce[:-4])

        try:
            import nacl.secret
            box = nacl.secret.Aead(self._secret_key)
            decrypted = box.decrypt(encrypted, header, bytes(nonce))
        except Exception as e:
            self.logger.warning(f"NaCl decrypt failed: {e} (hdr={header_size}, enc={len(encrypted)})")
            return

        # Skip encrypted extension data
        if ext_data_len and len(decrypted) > ext_data_len:
            decrypted = decrypted[ext_data_len:]

        # --- Strip RTP padding (RFC 3550 §5.1) ---
        if has_padding:
            if not decrypted:
                return
            pad_len = decrypted[-1]
            if pad_len == 0 or pad_len > len(decrypted):
                return
            decrypted = decrypted[:-pad_len]
            if not decrypted:
                return

        # --- DAVE E2EE decrypt ---
        if self._dave_session:
            with self._lock:
                user_id = self._ssrc_to_user.get(ssrc, 0)
            if not user_id:
                user_id = self._infer_user_for_ssrc(ssrc)
            if user_id:
                try:
                    import davey
                    decrypted = self._dave_session.decrypt(
                        user_id, davey.MediaType.audio, decrypted
                    )
                except Exception as e:
                    # Unencrypted passthrough — use NaCl-decrypted data as-is
                    if "Unencrypted" not in str(e):
                        self.logger.warning(f"DAVE decrypt failed for ssrc={ssrc}: {e}")
                        return
            else:
                # Unknown user + active DAVE = can't decrypt, drop packet
                return

        # --- Opus decode -> PCM ---
        try:
            if ssrc not in self._decoders:
                self._decoders[ssrc] = discord.opus.Decoder()
            pcm = self._decoders[ssrc].decode(decrypted)
            with self._lock:
                self._buffers[ssrc].extend(pcm)
                self._last_packet_time[ssrc] = time.time()
        except Exception as e:
            self.logger.warning(f"Opus decode error for ssrc={ssrc}: {e}")
            return

    def check_silence(self) -> list:
        now = time.time()
        completed = []

        with self._lock:
            ssrc_list = list(self._buffers.keys())
            for ssrc in ssrc_list:
                last_time = self._last_packet_time.get(ssrc, now)
                silence_duration = now - last_time
                buf = self._buffers[ssrc]
                buf_duration = len(buf) / (self.SAMPLE_RATE * self.CHANNELS * 2)

                if silence_duration >= self.SILENCE_THRESHOLD and buf_duration >= self.MIN_SPEECH_DURATION:
                    user_id = self._ssrc_to_user.get(ssrc, 0)
                    if not user_id:
                        user_id = self._infer_user_for_ssrc(ssrc)

                    if user_id:
                        completed.append((user_id, bytes(buf)))

                    self._buffers[ssrc] = bytearray()
                    self._last_packet_time.pop(ssrc, None)

                elif silence_duration >= self.SILENCE_THRESHOLD * 2:
                    self._buffers.pop(ssrc, None)
                    self._last_packet_time.pop(ssrc, None)

        return completed

    def _infer_user_for_ssrc(self, ssrc: int) -> int:
        try:
            channel = self._vc.channel
            if not channel: return 0
            candidates = [m.id for m in channel.members if not m.bot]
            if len(candidates) == 1:
                uid = candidates[0]
                self._ssrc_to_user[ssrc] = uid
                self.logger.info(f"Auto-mapped ssrc={ssrc} -> user={uid} (sole allowed member)")
                return uid
        except Exception:
            pass
        return 0


class DiscordVoice:
    def __init__(self, discord_client):
        self.bot_client = discord_client.client
        self.loop = getattr(discord_client, 'discord_loop', self.bot_client.loop)
        self.logger = discord_client.logger
        self.voice_receivers = {}
        self.keepalive_tasks = {}

    @staticmethod
    def create_wav_from_pcm(pcm_data: bytes, src_rate: int = 48000, src_channels: int = 2) -> bytes:
        """Convert raw PCM to 16kHz mono WAV directly in-memory via ffmpeg."""
        try:
            result = subprocess.run(
                [
                    "ffmpeg", "-y", "-loglevel", "error",
                    "-f", "s16le",
                    "-ar", str(src_rate),
                    "-ac", str(src_channels),
                    "-i", "pipe:0",       # Read from standard input
                    "-ar", "16000",
                    "-ac", "1",
                    "-f", "wav",
                    "pipe:1",             # Write to standard output
                ],
                input=pcm_data,
                capture_output=True,
                check=True,
                timeout=10,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg conversion failed: {e.stderr.decode(errors='ignore')}")
            return b""
        except Exception as e:
            print(f"FFmpeg execution error: {e}")
            return b""

    def connect_voice(self, channel_id):
        async def connect_async():
            channel = self.bot_client.get_channel(channel_id)
            if not channel:
                self.logger.error(f"[DiscordVoice.connect_voice] Voice channel {channel_id} not found.")
                return False

            guild_id = channel.guild.id

            try:
                vc = channel.guild.voice_client
                if vc:
                    try:
                        await vc.disconnect(force=True)
                    except:
                        pass

                self.logger.info("Connecting to voice channel...")
                # Native connection, bypassing voice_recv completely
                vc = await channel.connect(timeout=20.0, reconnect=True)

                if not vc.is_connected():
                    self.logger.error("VoiceClient connected but reports not connected")
                    return False

                receiver = VoiceReceiver(vc, self.logger)
                receiver.start()
                self.voice_receivers[guild_id] = receiver

                # Keep UDP hole punched to prevent Discord from dropping the receive route
                self.keepalive_tasks[guild_id] = asyncio.ensure_future(self._udp_keepalive(vc))

                self.logger.info(f"[DiscordVoice.connect_voice] Connected to {channel.name}.")
                return True

            except Exception as e:
                self.logger.error(f"[DiscordVoice.connect_voice] Error: {e}")
                return False

        try:
            return asyncio.run_coroutine_threadsafe(connect_async(), self.loop).result()
        except Exception as e:
            self.logger.error(f"[DiscordVoice.connect_voice] Critical asyncio error: {e}")
            return False

    async def _udp_keepalive(self, vc):
        """Sends periodic empty frames to prevent Discord from pruning the UDP route"""
        try:
            while vc.is_connected():
                await asyncio.sleep(15)
                try:
                    vc._connection.send_packet(b'\xf8\xff\xfe')
                except Exception:
                    pass
        except asyncio.CancelledError:
            pass

    def process_audio_streams(self, guild_id=None):
        """Yields perfectly decrypted and decoded WAV streams per user"""
        guilds_to_check = [guild_id] if guild_id else list(self.voice_receivers.keys())

        for g_id in guilds_to_check:
            receiver = self.voice_receivers.get(g_id)
            if not receiver:
                continue

            completed_utterances = receiver.check_silence()
            for user_id, pcm_data in completed_utterances:
                # Resolve User Display Name
                guild = self.bot_client.get_guild(g_id)
                member = guild.get_member(user_id) if guild else None
                display_name = member.display_name if member else f"User_{user_id}"

                duration = len(pcm_data) / 192000.0
                wav_bytes = self.create_wav_from_pcm(pcm_data)

                yield {
                    "guild_id": g_id,
                    "user_id": user_id,
                    "display_name": display_name,
                    "wav_bytes": wav_bytes,
                    "duration": duration
                }

    def disconnect_voice(self, guild_id):
        async def disconnect_async():
            guild = self.bot_client.get_guild(guild_id)

            # Clean up the receiver
            receiver = self.voice_receivers.pop(guild_id, None)
            if receiver:
                receiver.stop()

            task = self.keepalive_tasks.pop(guild_id, None)
            if task:
                task.cancel()

            if not guild or not guild.voice_client: return False
            vc = guild.voice_client
            await vc.disconnect(force=True)
            return True

        return asyncio.run_coroutine_threadsafe(disconnect_async(), self.loop).result()

    def play_audio(self, guild_id, audio_file_path):
        async def play_async():
            guild = self.bot_client.get_guild(guild_id)
            if not guild or not guild.voice_client: return False
            vc = guild.voice_client

            if vc.is_playing():
                vc.stop()

            try:
                if not os.path.exists(audio_file_path): return False
                vc.play(discord.FFmpegPCMAudio(audio_file_path))
                return True
            except:
                return False

        return asyncio.run_coroutine_threadsafe(play_async(), self.loop).result()