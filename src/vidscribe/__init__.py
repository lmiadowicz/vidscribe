"""Vidscribe - Video Transcription CLI Tool."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from vidscribe.core.engine import TranscriptionEngine
from vidscribe.downloaders.youtube import YouTubeDownloader
from vidscribe.processors.playlist import PlaylistProcessor

__all__ = ["TranscriptionEngine", "YouTubeDownloader", "PlaylistProcessor"]