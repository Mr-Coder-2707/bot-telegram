import logging
import os
from pytube import YouTube
from pytube.exceptions import PytubeError
import yt_dlp

logger = logging.getLogger(__name__)

def download_youtube_video(url, output_path="downloads", progress_callback=None):
    """
    Downloads a YouTube video using pytube, with a fallback to yt-dlp.
    Returns the path to the downloaded file.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Try pytube first
    try:
        logger.info(f"Attempting download with pytube: {url}")
        
        def pytube_progress(stream, chunk, bytes_remaining):
            if progress_callback:
                total_size = stream.filesize
                bytes_downloaded = total_size - bytes_remaining
                progress_callback(bytes_downloaded, total_size)

        yt = YouTube(url, on_progress_callback=pytube_progress)
        # Get highest resolution progressive stream (video+audio)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not stream:
            # Fallback if no progressive stream found
            stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
            
        if stream:
            filename = stream.download(output_path)
            logger.info(f"Pytube download success: {filename}")
            return filename
    except Exception as e:
        logger.warning(f"Pytube failed: {e}. Switching to yt-dlp.")

    # Fallback to yt-dlp
    try:
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
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            logger.info(f"yt-dlp download success: {filename}")
            return filename
    except Exception as e:
        logger.error(f"yt-dlp failed: {e}")
        raise Exception("Failed to download video using both pytube and yt-dlp.")
