from config import FFMPEG_OPTIONS, YDL_OPTS_PLAY
import asyncio
import discord
import yt_dlp
import settings

controller_logger = settings.logging.getLogger("controllers")

class GuildMusicState:
    def __init__(self):
        self.queue: list[dict] = []
        self.current: dict | None = None
        self.is_playing = False
        
_states: dict[int, GuildMusicState] = {}

def get_state(guild_id: int) -> GuildMusicState:
    if guild_id not in _states:
        _states[guild_id] = GuildMusicState()
    return _states[guild_id]

async def fetch_track(query: str) -> dict | None:
    loop = asyncio.get_event_loop()

    def _fetch():
        with yt_dlp.YoutubeDL(YDL_OPTS_PLAY) as ydl:
            info = ydl.extract_info(query, download=False)
            entries = info.get('entries')
            return entries[0] if entries else info

    entry = await loop.run_in_executor(None, _fetch)
    if not entry:
        return None

    return {
        'title': entry.get('title'),
        'webpage_url': entry.get('webpage_url'),
        'duration': entry.get('duration'),
        'thumbnail': entry.get('thumbnail'),
        'url': None,
    }
    

async def fetch_stream_url(webpage_url: str) -> str | None:
    loop = asyncio.get_event_loop()

    def _fetch():
        with yt_dlp.YoutubeDL(YDL_OPTS_PLAY) as ydl:
            info = ydl.extract_info(webpage_url, download=False)
            return info.get('url')

    return await loop.run_in_executor(None, _fetch)

def play_next(guild_id: int, voice_client: discord.VoiceClient):
    state = get_state(guild_id=guild_id)

    if not state.queue:
        state.is_playing = False
        state.current = None
        return

    track = state.queue.pop(0)
    state.current = track
    state.is_playing = True

    asyncio.run_coroutine_threadsafe(
        _play_track(guild_id, voice_client, track),
        voice_client.loop
    )
    
async def _play_track(guild_id: int, voice_client: discord.VoiceClient, track: dict):
    stream_url = await fetch_stream_url(track['webpage_url'])
    if not stream_url:
        controller_logger.error(f"Failed to fetch stream URL for {track['title']}")
        play_next(guild_id, voice_client)
        return

    source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)

    def after(error):
        if error:
            controller_logger.error(f"Playback Error: {error}")
        play_next(guild_id=guild_id, voice_client=voice_client)

    voice_client.play(source=source, after=after)

async def play(guild_id: int, voice_client: discord.VoiceClient, query: str) -> dict | None:
    track = await fetch_track(query=query)
    if not track:
        return None
    
    state = get_state(guild_id=guild_id)
    state.queue.append(track)

    if not state.is_playing:
        play_next(guild_id=guild_id, voice_client=voice_client)

    return track

def pause(voice_client: discord.VoiceClient) -> bool:
    if voice_client.is_playing():
        voice_client.pause()
        return True
    return False

def resume(voice_client: discord.VoiceClient) -> bool:
    if voice_client.is_paused():
        voice_client.resume()
        return True
    return False

def stop(guild_id: int, voice_client: discord.VoiceClient):
    state = get_state(guild_id=guild_id)
    state.queue.clear()
    state.current = None
    state.is_playing = False
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

def skip(guild_id: int, voice_client: discord.VoiceClient) -> bool:
    state = get_state(guild_id=guild_id)
    if state.is_playing or voice_client.is_playing():
        voice_client.stop()
        return True
    return False