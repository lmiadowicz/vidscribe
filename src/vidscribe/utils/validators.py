"""Validation utilities."""

import os
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse


def validate_file_path(file_path: str) -> None:
    """
    Validate that a file path exists and is readable.

    Args:
        file_path: Path to validate

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file isn't readable
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    if not os.access(path, os.R_OK):
        raise PermissionError(f"File is not readable: {file_path}")


def is_youtube_url(url: str) -> bool:
    """
    Check if a string is a YouTube URL.

    Args:
        url: String to check

    Returns:
        True if it's a YouTube URL, False otherwise
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        return hostname.lower() in [
            "www.youtube.com",
            "youtube.com",
            "youtu.be",
            "m.youtube.com",
        ]
    except Exception:
        return False


def validate_youtube_url(url: str) -> Tuple[bool, str]:
    """
    Validate if URL is a valid YouTube URL and determine its type.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, url_type)

    Raises:
        ValueError: If URL is not a valid YouTube URL
    """
    if not is_youtube_url(url):
        raise ValueError(f"Not a valid YouTube URL: {url}")

    parsed = urlparse(url)

    # Determine URL type
    if "playlist" in url or "list=" in url:
        return True, "playlist"
    elif "watch" in url or "youtu.be" in parsed.hostname:
        return True, "video"
    elif "@" in url or "/c/" in url or "/channel/" in url or "/user/" in url:
        return True, "channel"
    else:
        raise ValueError(f"Unsupported YouTube URL format: {url}")


def validate_model_size(model_size: str) -> None:
    """
    Validate Whisper model size.

    Args:
        model_size: Model size to validate

    Raises:
        ValueError: If model size is invalid
    """
    valid_models = ["tiny", "base", "small", "medium", "large"]
    if model_size not in valid_models:
        raise ValueError(f"Invalid model size. Must be one of {valid_models}")


def validate_output_format(format: str) -> None:
    """
    Validate output format.

    Args:
        format: Format to validate

    Raises:
        ValueError: If format is invalid
    """
    valid_formats = ["text", "json", "csv", "srt", "vtt"]
    if format not in valid_formats:
        raise ValueError(f"Invalid format. Must be one of {valid_formats}")