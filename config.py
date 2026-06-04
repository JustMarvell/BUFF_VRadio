YDL_OPTS = {
    'quiet' : True,
    'skip_download' : True,
    'default_search' : 'ytsearch5',
    'runtime' : 'nodejs',
}

FFMPEG_OPTIONS = {
    'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options' : '-vn',
}