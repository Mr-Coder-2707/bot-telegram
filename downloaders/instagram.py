import logging
import os
import instaloader
import glob
import yt_dlp
import time

from .utils import get_ytdlp_opts

logger = logging.getLogger(__name__)

def download_instagram_content(url, output_path="downloads"):
    """
    Downloads Instagram post (image or video) using Instaloader with yt-dlp as fallback.
    Returns a list of paths to downloaded files (media).
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cookies_path = os.path.join(base_dir, "cookies.txt")

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
            quiet=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # Load cookies if available
        if os.path.exists(cookies_path):
            try:
                L.context.load_cookies_from_file(cookies_path)
                logger.info("Instaloader: Loaded cookies from cookies.txt")
            except Exception as ce:
                logger.warning(f"Instaloader: Failed to load cookies: {ce}")

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

        # Use 'best' instead of 'bestvideo+bestaudio' to handle images/carousels 
        # that might not have a "video format" in the traditional sense
        ydl_opts = get_ytdlp_opts({
            'format': 'best', 
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'allow_playlist': True,
        })
        
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
                # One last attempt to find ANY file in the temp_dir if filenames don't match exactly
                for ext in ['*.jpg', '*.mp4', '*.png', '*.jpeg']:
                    media_files.extend(glob.glob(os.path.join(temp_dir, ext)))
                
                if media_files:
                    return list(set(media_files)) # deduplicate
                
                raise Exception("yt-dlp finished but no files were found.")

    except Exception as e:
        logger.error(f"Both Instaloader and yt-dlp failed for Instagram: {e}")
        err_msg = str(e).lower()
        if "no video formats found" in err_msg:
             raise Exception("هذا المنشور لا يحتوي على فيديو (ربما صور فقط). جاري العمل على تحسين دعم الصور.")
        if "wait a few minutes" in err_msg or "401" in err_msg or "429" in err_msg:
            raise Exception("Instagram has temporarily blocked requests. Please try again in 5-10 minutes or check your cookies.txt")
        raise Exception(f"Failed to download Instagram content: {str(e)}")
