YDL_OPTS = {
    'quiet': True,
    'skip_download': True,
    'default_search': 'ytsearch5',
    'noplaylist': False,
}

YDL_OPTS_PLAY = {
    **YDL_OPTS,
    'default_search': 'ytsearch1',
    'extract_flat': False,
    'format': 'bestaudio/best',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}