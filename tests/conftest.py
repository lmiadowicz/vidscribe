"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_video_info():
    """Sample video information for testing."""
    return {
        "title": "Test Video",
        "duration": 120,
        "author": "Test Author",
        "video_id": "test123",
        "description": "Test description",
        "views": 1000,
        "url": "https://www.youtube.com/watch?v=test123",
    }


@pytest.fixture
def sample_transcription_result():
    """Sample transcription result for testing."""
    return {
        "text": "This is a test transcription.",
        "segments": [
            {"start": 0.0, "end": 2.0, "text": "This is"},
            {"start": 2.0, "end": 4.0, "text": " a test"},
            {"start": 4.0, "end": 6.0, "text": " transcription."},
        ],
        "language": "en",
        "transcription_time": 5.0,
        "model_size": "base",
    }


@pytest.fixture
def mock_whisper_model():
    """Mock Whisper model for testing."""
    model = MagicMock()
    model.transcribe.return_value = {
        "text": "Test transcription",
        "segments": [],
        "language": "en",
    }
    return model


@pytest.fixture
def mock_youtube_object():
    """Mock YouTube object for testing."""
    yt = MagicMock()
    yt.title = "Test Video"
    yt.length = 120
    yt.author = "Test Author"
    yt.video_id = "test123"
    yt.description = "Test description"
    yt.views = 1000
    
    # Mock audio stream
    audio_stream = MagicMock()
    audio_stream.download.return_value = "/tmp/test_video.mp4"
    yt.streams.filter.return_value.first.return_value = audio_stream
    
    return yt


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "model": {
            "size": "base",
            "device": None,
        },
        "download": {
            "output_dir": None,
            "keep_files": False,
        },
        "output": {
            "format": "text",
            "language": None,
        },
        "logging": {
            "level": "INFO",
        },
    }