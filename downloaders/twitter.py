import logging
import os
import yt_dlp

logger = logging.getLogger(__name__)

def download_twitter_video(url, output_path="downloads", progress_callback=None):
    """
    Downloads Twitter/X video using yt-dlp.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    try:
        logger.info(f"Downloading Twitter video: {url}")
        
        def ytdlp_progress(d):
            if d['status'] == 'downloading':
                if progress_callback:
                    total = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded = d.get('downloaded_bytes', 0)
                    if total:
                        progress_callback(downloaded, total)

        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(output_path, 'twitter_%(id)s.%(ext)s'),
            'quiet': True,
            'progress_hooks': [ytdlp_progress],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        logger.error(f"Twitter download failed: {e}")
        raise e
