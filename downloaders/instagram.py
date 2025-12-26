import logging
import os
import instaloader
import glob
import yt_dlp
import time

logger = logging.getLogger(__name__)

def download_instagram_content(url, output_path="downloads"):
    """
    Downloads Instagram post (image or video) using Instaloader with yt-dlp as fallback.
    Returns a list of paths to downloaded files (media).
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Try Instaloader first
    try:
        logger.info(f"Attempting Instagram download with Instaloader: {url}")
        L = instaloader.Instaloader(
            download_pictures=True,
            download_videos=True, 
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            quiet=True
        )

        # Extract shortcode from URL
        if "/p/" in url:
            shortcode = url.split("/p/")[1].split("/")[0]
        elif "/reel/" in url:
            shortcode = url.split("/reel/")[1].split("/")[0]
        elif "/reels/" in url:
            shortcode = url.split("/reels/")[1].split("/")[0]
        else:
            raise ValueError("Invalid Instagram URL format for Instaloader")

        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        target_dir = os.path.join(output_path, shortcode)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        cwd = os.getcwd()
        try:
            os.chdir(output_path)
            L.download_post(post, target=shortcode)
        finally:
            os.chdir(cwd)

        # Find the media files
        media_files = []
        extensions = ['*.jpg', '*.mp4', '*.png', '*.jpeg']
        for ext in extensions:
            media_files.extend(glob.glob(os.path.join(target_dir, ext)))
            
        if media_files:
            logger.info(f"Instaloader download success: {media_files}")
            return media_files
            
    except Exception as e:
        logger.warning(f"Instaloader failed: {e}. Switching to yt-dlp.")

    # Fallback to yt-dlp
    try:
        logger.info(f"Attempting Instagram download with yt-dlp: {url}")
        
        # Create a unique directory for this download to avoid conflicts
        timestamp = int(time.time())
        temp_dir = os.path.join(output_path, f"ig_{timestamp}")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info:
                # It's a playlist or multiple entries
                files = [ydl.prepare_filename(entry) for entry in info['entries']]
            else:
                files = [ydl.prepare_filename(info)]
            
            # Filter existing files
            media_files = [f for f in files if os.path.exists(f)]
            
            if media_files:
                logger.info(f"yt-dlp download success: {media_files}")
                return media_files
            else:
                raise Exception("yt-dlp finished but no files were found.")

    except Exception as e:
        logger.error(f"Both Instaloader and yt-dlp failed for Instagram: {e}")
        # If it's a "Wait a few minutes" error, re-raise with a friendlier message
        if "wait a few minutes" in str(e).lower() or "401" in str(e):
            raise Exception("Instagram has temporarily blocked requests. Please try again in 5-10 minutes.")
        raise Exception(f"Failed to download Instagram content: {str(e)}")
