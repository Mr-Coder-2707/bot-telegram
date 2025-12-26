import logging
import os
import instaloader
import glob

logger = logging.getLogger(__name__)

def download_instagram_content(url, output_path="downloads"):
    """
    Downloads Instagram post (image or video) using Instaloader.
    Returns a list of paths to downloaded files (media).
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    L = instaloader.Instaloader(
        download_pictures=True,
        download_videos=True, 
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )

    try:
        # Extract shortcode from URL
        # URL format: https://www.instagram.com/p/SHORTCODE/
        if "/p/" in url:
            shortcode = url.split("/p/")[1].split("/")[0]
        elif "/reel/" in url:
            shortcode = url.split("/reel/")[1].split("/")[0]
        else:
            raise ValueError("Invalid Instagram URL format")

        logger.info(f"Downloading Instagram post: {shortcode}")
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Download to a specific target directory (named after shortcode to avoid collisions)
        # We change directory to output_path to avoid issues with nested paths in target argument
        cwd = os.getcwd()
        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            os.chdir(output_path)
            
            L.download_post(post, target=shortcode)
        finally:
            os.chdir(cwd)

        # Find the media files
        target_dir = os.path.join(output_path, shortcode)
        media_files = []
        extensions = ['*.jpg', '*.mp4', '*.png']
        for ext in extensions:
            media_files.extend(glob.glob(os.path.join(target_dir, ext)))
            
        if not media_files:
            raise Exception("No media files found after download.")
            
        return media_files

    except Exception as e:
        logger.error(f"Instagram download failed: {e}")
        raise e
