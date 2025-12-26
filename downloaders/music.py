import logging
import os
import json
from datetime import datetime
from typing import Dict, Tuple, Optional
import yt_dlp
from pathlib import Path

logger = logging.getLogger(__name__)

def download_music(url: str, output_path: str = "downloads", progress_callback=None) -> Tuple[str, Dict]:
    """
    Downloads audio from YouTube and extracts metadata.
    Returns tuple of (file_path, metadata_dict)
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    try:
        logger.info(f"Downloading music from: {url}")
        
        def progress_hook(d):
            if d['status'] == 'downloading':
                if progress_callback:
                    total = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded = d.get('downloaded_bytes', 0)
                    if total:
                        progress_callback(downloaded, total)
            elif d['status'] == 'finished':
                if progress_callback:
                    progress_callback(100, 100)

        # Extract metadata and download audio
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [progress_hook],
            'extract_flat': False,
            'no_color': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("Extracting metadata...")
            info = ydl.extract_info(url, download=True)
            
            # Get the downloaded file path
            file_path = ydl.prepare_filename(info)
            
            # Try to find the actual mp3 file
            mp3_path = os.path.splitext(file_path)[0] + '.mp3'
            if os.path.exists(mp3_path):
                file_path = mp3_path
            
            # Extract and organize metadata
            metadata = extract_metadata(info, file_path)
            
            logger.info(f"Music download successful: {file_path}")
            return file_path, metadata

    except Exception as e:
        logger.error(f"Error downloading music: {e}")
        raise Exception(f"Failed to download music: {str(e)}")


def extract_metadata(info: Dict, file_path: str) -> Dict:
    """
    Extracts comprehensive metadata from YouTube info dict.
    Returns a dictionary with formatted metadata.
    """
    try:
        metadata = {
            'title': info.get('title', 'Unknown'),
            'artist': info.get('uploader', 'Unknown Artist'),
            'duration': format_duration(info.get('duration', 0)),
            'duration_seconds': info.get('duration', 0),
            'upload_date': format_date(info.get('upload_date', '')),
            'view_count': format_number(info.get('view_count', 0)),
            'like_count': format_number(info.get('like_count', 0)),
            'description': info.get('description', '')[:200] + '...' if info.get('description') else 'No description',
            'file_size': get_file_size(file_path),
            'file_path': file_path,
            'thumbnail': info.get('thumbnail', ''),
            'uploader_url': info.get('uploader_url', ''),
            'video_id': info.get('id', ''),
            'url': info.get('url', ''),
        }
        
        # Clean description if too long
        if metadata['description'].endswith('...'):
            metadata['description'] = metadata['description'][:-3]
        
        return metadata
    
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}")
        return {
            'title': 'Unknown',
            'artist': 'Unknown Artist',
            'duration': 'Unknown',
            'file_path': file_path,
        }


def format_duration(seconds: int) -> str:
    """Converts seconds to MM:SS format."""
    if not seconds:
        return '00:00'
    
    minutes = seconds // 60
    secs = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_date(date_str: str) -> str:
    """Converts YYYYMMDD format to readable date."""
    try:
        if date_str and len(date_str) == 8:
            dt = datetime.strptime(date_str, '%Y%m%d')
            return dt.strftime('%d %b %Y')
    except:
        pass
    return 'Unknown Date'


def format_number(num: int) -> str:
    """Formats numbers with K, M abbreviations."""
    if num is None or num == 0:
        return '0'
    
    num = int(num)
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)


def get_file_size(file_path: str) -> str:
    """Gets file size in human-readable format."""
    try:
        size_bytes = os.path.getsize(file_path)
        
        if size_bytes >= 1_000_000:
            return f"{size_bytes / 1_000_000:.2f} MB"
        elif size_bytes >= 1_000:
            return f"{size_bytes / 1_000:.2f} KB"
        return f"{size_bytes} B"
    except:
        return "Unknown"


def create_metadata_file(metadata: Dict, output_dir: str = "downloads") -> str:
    """
    Creates a JSON file with metadata information.
    Returns path to metadata file.
    """
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        metadata_file = os.path.splitext(metadata['file_path'])[0] + '.json'
        
        # Create clean metadata for JSON
        clean_metadata = {
            'title': metadata['title'],
            'artist': metadata['artist'],
            'duration': metadata['duration'],
            'upload_date': metadata['upload_date'],
            'view_count': metadata['view_count'],
            'like_count': metadata['like_count'],
            'file_size': metadata['file_size'],
            'video_id': metadata['video_id'],
            'uploader_url': metadata['uploader_url'],
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(clean_metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Metadata file created: {metadata_file}")
        return metadata_file
    
    except Exception as e:
        logger.error(f"Error creating metadata file: {e}")
        return None


def format_metadata_message(metadata: Dict) -> str:
    """
    Formats metadata into a readable Telegram message.
    """
    message = (
        "🎵 **الأغنية تم تحميلها بنجاح!**\n"
        "🎵 **Music Downloaded Successfully!**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 **العنوان | Title:**\n`{metadata['title']}`\n\n"
        f"🎤 **الفنان | Artist:**\n`{metadata['artist']}`\n\n"
        f"⏱️ **المدة | Duration:**\n`{metadata['duration']}`\n\n"
        f"📅 **تاريخ التحميل | Upload Date:**\n`{metadata['upload_date']}`\n\n"
        f"👁️ **المشاهدات | Views:**\n`{metadata['view_count']}`\n\n"
        f"❤️ **الإعجابات | Likes:**\n`{metadata['like_count']}`\n\n"
        f"💾 **حجم الملف | File Size:**\n`{metadata['file_size']}`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    return message
