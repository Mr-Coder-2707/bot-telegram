# Bot Tasks

This document outlines the various tasks and functionalities performed by the bot.

## Core Bot Functions (`bot.py`)

*   `start`: Initializes the bot and handles the `/start` command.
*   `help_command`: Provides help information to users via the `/help` command.
*   `about_command`: Displays information about the bot using the `/about` command.
*   `button_callback`: Manages interactions with inline keyboard buttons.
*   `handle_message`: Processes all incoming user messages, determining the appropriate action or download type.
*   `progress_callback`: A utility function used to report download progress to the user.
*   `post_init`: Performs setup tasks after the bot application has initialized.
*   `main`: The primary entry point for starting and running the bot application.

## Downloader Modules (`downloaders/`)

### YouTube Downloader (`downloaders/youtube.py`)

*   `download_youtube_video`: Handles the downloading of videos from YouTube.
*   `pytube_progress`: A specific progress callback for `pytube` based downloads.
*   `ytdlp_progress`: A specific progress callback for `yt-dlp` based downloads.

### Utility Functions (`downloaders/utils.py`)

*   `check_file_size`: Checks and returns the size of a specified file.
*   `cleanup_file`: Deletes or cleans up a specified file.

### Twitter Downloader (`downloaders/twitter.py`)

*   `download_twitter_video`: Facilitates the downloading of videos from Twitter.
*   `ytdlp_progress`: A specific progress callback for `yt-dlp` used in Twitter downloads.

### TikTok Downloader (`downloaders/tiktok.py`)

*   `download_tiktok_video`: Manages the downloading of videos from TikTok.
*   `ytdlp_progress`: A specific progress callback for `yt-dlp` used in TikTok downloads.
*   `is_tiktok_url`: Verifies if a given URL is a valid TikTok URL.

### Music Downloader (`downloaders/music.py`)

*   `download_music`: Downloads audio content from various music platforms.
*   `progress_hook`: A progress callback specifically for music downloads.
*   `extract_metadata`: Extracts metadata (e.g., title, artist, duration) from downloaded music files.
*   `format_duration`: Formats time in seconds into a human-readable duration string.
*   `format_date`: Formats date strings into a consistent, readable format.
*   `format_number`: Formats numerical values for better readability.
*   `get_file_size`: Retrieves and formats the size of a given file.
*   `create_metadata_file`: Generates a file containing extracted metadata for a downloaded track.
*   `format_metadata_message`: Formats extracted music metadata into a user-friendly message.

### Instagram Downloader (`downloaders/instagram.py`)

*   `download_instagram_content`: Downloads various types of content from Instagram.

### Facebook Downloader (`downloaders/facebook.py`)

*   `download_facebook_video`: Handles the downloading of videos from Facebook.