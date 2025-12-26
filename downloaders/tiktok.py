import logging
import os
import yt_dlp

logger = logging.getLogger(__name__)

def download_tiktok_video(url, output_path="downloads", progress_callback=None):
    """
    Downloads a TikTok video using yt-dlp.
    Returns the path to the downloaded file.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    logger.info(f"Attempting TikTok download: {url}")

    def ytdlp_progress(d):
        if d['status'] == 'downloading':
            if progress_callback:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    progress_callback(downloaded, total)

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [ytdlp_progress],
        # Add user agent to avoid bot detection
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            logger.info(f"TikTok download success: {filename}")
            return filename
            
    except Exception as e:
        logger.error(f"TikTok download failed: {e}")
        raise Exception(f"Failed to download TikTok video: {str(e)}")

def is_tiktok_url(url):
    """
    Checks if a URL is a TikTok URL.
    """
    return "tiktok.com" in url
