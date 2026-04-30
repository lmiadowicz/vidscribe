"""YouTube video downloader module."""

import logging
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import parse_qs, urlparse

import ffmpeg
import yt_dlp

from vidscribe.utils.validators import validate_youtube_url

logger = logging.getLogger(__name__)


class YouTubeDownloader:
    """Handles YouTube video downloading and conversion."""

    def __init__(self, output_dir: Optional[str] = None, keep_files: bool = False):
        """
        Initialize the downloader.

        Args:
            output_dir: Directory to save downloaded files (uses temp dir if None)
            keep_files: Whether to keep downloaded files after processing
        """
        self.output_dir = output_dir or tempfile.gettempdir()
        self.keep_files = keep_files
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloader initialized with output_dir: {self.output_dir}")

    def download_video(self, url: str, output_filename: Optional[str] = None) -> Optional[str]:
        """
        Download a YouTube video and convert to MP3.

        Args:
            url: YouTube video URL
            output_filename: Optional output filename (without extension)

        Returns:
            Path to the downloaded MP3 file, or None if failed
        """
        try:
            validate_youtube_url(url)
            logger.info(f"Downloading video: {url}")

            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'extractaudio': True,
                'audioformat': 'mp3',
                'audioquality': '192',
                'quiet': True,
                'no_warnings': True,
            }

            # Use custom filename if provided
            if output_filename:
                ydl_opts['outtmpl'] = os.path.join(self.output_dir, f'{output_filename}.%(ext)s')

            # Extract info first to get the title
            ydl_opts_info = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Sanitize filename if not provided
                if not output_filename:
                    output_filename = self._sanitize_filename(info.get('title', 'unknown'))

            # Update download options with correct filename
            ydl_opts['outtmpl'] = os.path.join(self.output_dir, f'{output_filename}.%(ext)s')

            # Download the audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
                # Find the downloaded file
                mp3_path = os.path.join(self.output_dir, f"{output_filename}.mp3")
                
                # yt-dlp might use different extensions, find the actual file
                for ext in ['.mp3', '.m4a', '.webm', '.opus']:
                    potential_path = os.path.join(self.output_dir, f"{output_filename}{ext}")
                    if os.path.exists(potential_path):
                        if ext != '.mp3':
                            # Convert to MP3
                            self._convert_to_mp3(potential_path, mp3_path)
                            os.remove(potential_path)
                        else:
                            mp3_path = potential_path
                        break
                else:
                    logger.error(f"Downloaded file not found for {url}")
                    return None

                logger.info(f"Downloaded successfully: {mp3_path}")
                return mp3_path

        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}")
            return None

    def _convert_to_mp3(self, input_path: str, output_path: str) -> None:
        """Convert audio file to MP3 format."""
        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path, acodec="mp3", audio_bitrate="192k")
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg conversion error: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to convert to MP3: {e.stderr.decode()}")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "")
        # Limit length and strip whitespace
        return filename[:100].strip()

    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a YouTube video.

        Args:
            url: YouTube video URL

        Returns:
            Video information dictionary or None if failed
        """
        try:
            validate_youtube_url(url)
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    "title": info.get('title'),
                    "duration": info.get('duration'),
                    "author": info.get('uploader'),
                    "video_id": info.get('id'),
                    "description": info.get('description'),
                    "views": info.get('view_count'),
                    "publish_date": info.get('upload_date'),
                    "thumbnail_url": info.get('thumbnail'),
                    "url": url,
                }
        except Exception as e:
            logger.error(f"Error getting video info for {url}: {e}")
            return None

    def get_playlist_videos(self, playlist_url: str) -> List[str]:
        """
        Get all video URLs from a YouTube playlist.

        Args:
            playlist_url: YouTube playlist URL

        Returns:
            List of video URLs
        """
        try:
            logger.info(f"Fetching playlist: {playlist_url}")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                
                if 'entries' in info:
                    video_urls = [f"https://www.youtube.com/watch?v={entry['id']}" 
                                 for entry in info['entries'] if entry]
                    logger.info(f"Found {len(video_urls)} videos in playlist")
                    return video_urls
                else:
                    logger.error("No entries found in playlist")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching playlist: {e}")
            return []

    def get_channel_videos(
        self,
        channel_url: str,
        limit: Optional[int] = None,
        since_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get video metadata from a YouTube channel.

        Args:
            channel_url: YouTube channel URL
            limit: Maximum number of videos to return after date filtering (None for all)
            since_date: Only include videos uploaded on or after this date (YYYYMMDD)

        Returns:
            List of dicts with keys: url, upload_date, title
        """
        logger.info(f"Fetching channel: {channel_url}")

        url = channel_url.rstrip('/')
        if not url.endswith('/videos'):
            url = f"{url}/videos"

        try:
            # Flat extraction to get the full list of video IDs quickly.
            flat_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'lazy_playlist': False,
            }
            with yt_dlp.YoutubeDL(flat_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' not in info:
                    logger.error("No entries found in channel")
                    return []
                flat_entries = [e for e in info['entries'] if e]
                logger.info(f"Fetched {len(flat_entries)} total videos from channel")

            if not since_date:
                videos = [
                    {
                        'url': f"https://www.youtube.com/watch?v={e['id']}",
                        'upload_date': e.get('upload_date', ''),
                        'title': e.get('title', ''),
                    }
                    for e in flat_entries
                ]
                if limit:
                    videos = videos[:limit]
                logger.info(f"Returning {len(videos)} videos")
                return videos

            # Check if flat entries already include upload_date (modern yt-dlp versions
            # sometimes include it). If so, filter without extra network requests.
            if flat_entries and flat_entries[0].get('upload_date'):
                logger.info("Flat entries include upload_date, filtering without extra fetches")
                videos = [
                    {
                        'url': f"https://www.youtube.com/watch?v={e['id']}",
                        'upload_date': e['upload_date'],
                        'title': e.get('title', ''),
                    }
                    for e in flat_entries
                    if e.get('upload_date', '') >= since_date
                ]
                if limit:
                    videos = videos[:limit]
                logger.info(f"Returning {len(videos)} videos since {since_date}")
                return videos

            # Flat entries lack dates — fetch per-video metadata concurrently.
            # Channel listing is newest-first so we can stop once we've seen enough old videos.
            logger.info(
                f"Fetching video dates concurrently (stopping at {since_date}), "
                f"{len(flat_entries)} videos to check..."
            )

            meta_opts = {
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
            }

            def _fetch_meta(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
                video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                try:
                    with yt_dlp.YoutubeDL(meta_opts) as ydl:
                        info = ydl.extract_info(video_url, download=False)
                    if not info:
                        return None
                    upload_date = info.get('upload_date')
                    if not upload_date:
                        return None
                    return {
                        'url': video_url,
                        'upload_date': upload_date,
                        'title': info.get('title', entry.get('title', '')),
                    }
                except Exception:
                    return None

            # Process in batches so we can short-circuit once we've passed the cutoff.
            # Channels are newest-first, so once a batch contains only old videos we stop.
            BATCH_SIZE = 20
            MAX_WORKERS = 8
            videos: List[Dict[str, Any]] = []
            done = False

            for batch_start in range(0, len(flat_entries), BATCH_SIZE):
                if done:
                    break
                batch = flat_entries[batch_start: batch_start + BATCH_SIZE]
                batch_results: List[Optional[Dict[str, Any]]] = [None] * len(batch)

                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
                    future_to_idx = {
                        pool.submit(_fetch_meta, entry): idx
                        for idx, entry in enumerate(batch)
                    }
                    for future in as_completed(future_to_idx):
                        idx = future_to_idx[future]
                        batch_results[idx] = future.result()

                # Walk results in channel order (newest first) so cutoff logic is correct.
                for result in batch_results:
                    if result is None:
                        continue
                    if result['upload_date'] < since_date:
                        logger.info(
                            f"Reached video from {result['upload_date']} "
                            f"(before cutoff {since_date}), stopping"
                        )
                        done = True
                        break
                    videos.append(result)
                    if limit and len(videos) >= limit:
                        done = True
                        break

            logger.info(f"Returning {len(videos)} videos since {since_date}")
            return videos
        except Exception as e:
            logger.error(f"Error fetching channel: {e}")
            return []

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.

        Args:
            url: YouTube video URL

        Returns:
            Video ID or None
        """
        try:
            parsed = urlparse(url)

            if "youtu.be" in parsed.hostname:
                return parsed.path[1:]
            elif "youtube.com" in parsed.hostname:
                if parsed.path == "/watch":
                    return parse_qs(parsed.query)["v"][0]
                elif parsed.path.startswith("/embed/"):
                    return parsed.path.split("/")[2]
                elif parsed.path.startswith("/v/"):
                    return parsed.path.split("/")[2]

            return None
        except Exception:
            return None

    @staticmethod
    def extract_playlist_id(url: str) -> Optional[str]:
        """
        Extract playlist ID from YouTube URL.

        Args:
            url: YouTube playlist URL

        Returns:
            Playlist ID or None
        """
        try:
            parsed = urlparse(url)
            if "list" in parse_qs(parsed.query):
                return parse_qs(parsed.query)["list"][0]
            return None
        except Exception:
            return None