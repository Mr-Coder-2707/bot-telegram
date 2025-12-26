import os
import logging

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB = 2000  # 2 GB - حد Telegram الأقصى

def check_file_size(file_path):
    """Checks if the file size is within the limit."""
    try:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            return False, size_mb
        return True, size_mb
    except OSError as e:
        logger.error(f"Error checking file size: {e}")
        return False, 0

def cleanup_file(file_path):
    """Removes the file after sending and cleans up empty parent directories."""
    try:
        if os.path.exists(file_path):
            parent_dir = os.path.dirname(file_path)
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
            
            # If the parent directory is empty and not the root 'downloads' folder, remove it
            if parent_dir and os.path.basename(parent_dir) != "downloads":
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
                    logger.info(f"Deleted empty directory: {parent_dir}")
    except OSError as e:
        logger.error(f"Error deleting file or directory {file_path}: {e}")
