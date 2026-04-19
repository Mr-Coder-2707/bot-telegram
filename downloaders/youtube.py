import logging
import os
from pytube import YouTube
from pytube.exceptions import PytubeError
import yt_dlp

from .utils import get_ytdlp_opts

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

        requested_format = os.getenv('YTDLP_FORMAT', 'best/bestvideo+bestaudio/best')
        merge_format = os.getenv('YTDLP_MERGE_FORMAT', 'mp4')

        def _run_download(fmt: str, ignoreerrors: bool = True):
            ydl_opts = get_ytdlp_opts({
                'format': fmt,
                'merge_output_format': merge_format,
                'ignoreerrors': ignoreerrors,
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [ytdlp_progress],
            })
            logger.info(
                f"yt-dlp format selected: {ydl_opts.get('format')} | merge_output_format: {ydl_opts.get('merge_output_format')} | ignoreerrors: {ignoreerrors}"
            )
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    return None
                filename = ydl.prepare_filename(info)
                if not filename or not os.path.exists(filename):
                    return None
                logger.info(f"yt-dlp download success: {filename}")
                return filename

        # Try a sequence of fallback formats
        fallback_formats = [
            requested_format,
            'bv*+ba/b',
            'bestvideo+bestaudio',
            'best',
            'best[ext=mp4]',
            'best[ext=webm]'
        ]
        tried = set()
        for fmt in fallback_formats:
            if fmt in tried:
                continue
            tried.add(fmt)
            filename = _run_download(fmt, ignoreerrors=True)
            if filename:
                return filename
            # Try strict mode as last resort for this format
            filename = _run_download(fmt, ignoreerrors=False)
            if filename:
                return filename

        raise Exception(
            "yt-dlp could not download the video with any known format.\n"
            "جرب رابط آخر أو استخدم yt-dlp -F لرؤية الصيغ المتاحة بنفسك.\n"
            "If the problem persists, the video may be private, deleted, or region-locked."
        )

        try:
            return _run_download(requested_format)
        except Exception as e:
            err_msg = str(e).lower()
            # If a strict format was requested (via env or default) and is unavailable, fallback to best.
            if "requested format is not available" in err_msg:
                logger.warning(
                    f"Requested format not available ({requested_format}). Falling back to format=best"
                )
                return _run_download('best')
            raise
    except Exception as e:
        logger.error(f"yt-dlp failed: {e}")
        err_msg = str(e).lower()
        if "sign in to confirm" in err_msg or "bot" in err_msg:
            raise Exception("YouTube is asking for verification. Please add your cookies.txt file to bypass this.")
        raise Exception(f"Failed to download YouTube video: {str(e)}")
