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
    """Removes the file after sending."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
    except OSError as e:
        logger.error(f"Error deleting file {file_path}: {e}")
