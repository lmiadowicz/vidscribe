"""Unit tests for validators module."""

import pytest
from pathlib import Path

from vidscribe.utils.validators import (
    validate_file_path,
    is_youtube_url,
    validate_youtube_url,
    validate_model_size,
    validate_output_format,
)


class TestValidateFilePath:
    """Test file path validation."""

    def test_valid_file(self, temp_dir):
        """Test with a valid file path."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        # Should not raise
        validate_file_path(str(test_file))

    def test_nonexistent_file(self):
        """Test with a nonexistent file."""
        with pytest.raises(FileNotFoundError):
            validate_file_path("/nonexistent/file.txt")

    def test_directory_instead_of_file(self, temp_dir):
        """Test with a directory path instead of file."""
        with pytest.raises(ValueError):
            validate_file_path(str(temp_dir))


class TestYouTubeURLValidation:
    """Test YouTube URL validation."""

    def test_is_youtube_url_valid(self):
        """Test valid YouTube URLs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=test123",
            "https://youtube.com/watch?v=test123",
            "https://youtu.be/test123",
            "https://m.youtube.com/watch?v=test123",
        ]
        
        for url in valid_urls:
            assert is_youtube_url(url) is True

    def test_is_youtube_url_invalid(self):
        """Test invalid YouTube URLs."""
        invalid_urls = [
            "https://vimeo.com/123456",
            "https://example.com",
            "not a url",
            "/local/path",
        ]
        
        for url in invalid_urls:
            assert is_youtube_url(url) is False

    def test_validate_youtube_url_video(self):
        """Test YouTube video URL validation."""
        url = "https://www.youtube.com/watch?v=test123"
        is_valid, url_type = validate_youtube_url(url)
        assert is_valid is True
        assert url_type == "video"

    def test_validate_youtube_url_playlist(self):
        """Test YouTube playlist URL validation."""
        url = "https://www.youtube.com/playlist?list=PLtest123"
        is_valid, url_type = validate_youtube_url(url)
        assert is_valid is True
        assert url_type == "playlist"

    def test_validate_youtube_url_channel(self):
        """Test YouTube channel URL validation."""
        urls = [
            "https://www.youtube.com/@testchannel",
            "https://www.youtube.com/c/testchannel",
            "https://www.youtube.com/channel/UCtest123",
        ]
        
        for url in urls:
            is_valid, url_type = validate_youtube_url(url)
            assert is_valid is True
            assert url_type == "channel"

    def test_validate_youtube_url_invalid(self):
        """Test invalid YouTube URL validation."""
        with pytest.raises(ValueError):
            validate_youtube_url("https://example.com")


class TestModelValidation:
    """Test model size validation."""

    def test_valid_model_sizes(self):
        """Test valid model sizes."""
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        
        for size in valid_sizes:
            # Should not raise
            validate_model_size(size)

    def test_invalid_model_size(self):
        """Test invalid model size."""
        with pytest.raises(ValueError):
            validate_model_size("invalid")


class TestFormatValidation:
    """Test output format validation."""

    def test_valid_formats(self):
        """Test valid output formats."""
        valid_formats = ["text", "json", "csv", "srt", "vtt"]
        
        for format in valid_formats:
            # Should not raise
            validate_output_format(format)

    def test_invalid_format(self):
        """Test invalid output format."""
        with pytest.raises(ValueError):
            validate_output_format("invalid")