from YDL_OPTS import YDL_OPTS
import yt_dlp

async def search(query: str) -> list[dict] | None:
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
        entries = info.get('entries', [])
        if not entries:
            return None
        
        results = []
        for entry in entries[:5]:
            results.append({
                'title': entry.get('title'),
                'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                'channel': entry.get('uploader') or entry.get('channel'),
                'description': (entry.get('description') or '')[:100],
                'thumbnail': entry.get('thumbnail'),
                'duration': entry.get('duration'),
            })
        return results