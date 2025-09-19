"""Unit tests for CLI module."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from vidscribe.cli import cli, transcribe, playlist, info, models
from vidscribe import __version__


class TestCLIHelp:
    """Test CLI help functionality."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_main_help_output(self):
        """Test main CLI help contains all expected sections."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check for enhanced help sections
        assert "🎬 Vidscribe - Professional Video Transcription CLI Tool" in output
        assert "🚀 CORE CAPABILITIES:" in output
        assert "📖 QUICK EXAMPLES:" in output
        assert "⚡ PERFORMANCE FEATURES:" in output
        assert "📁 OUTPUT FORMATS:" in output
        
        # Check for specific capabilities
        assert "YouTube Videos: Single video transcription" in output
        assert "YouTube Playlists: Batch process entire playlists" in output
        assert "Local Videos: MP4, AVI, MOV, MKV, WebM support" in output
        assert "MLX Acceleration: 50% faster on Apple Silicon" in output
        assert "Multi-language: 99+ languages supported" in output
        
        # Check for example commands
        assert "vidscribe transcribe" in output
        assert "vidscribe playlist" in output
        assert "vidscribe info" in output
        assert "vidscribe models" in output

    def test_transcribe_help_output(self):
        """Test transcribe command help contains detailed examples."""
        result = self.runner.invoke(transcribe, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check for enhanced help sections
        assert "🎥 Transcribe a single video or audio file" in output
        assert "📋 EXAMPLES:" in output
        assert "🔧 MODEL SIZES:" in output
        assert "🌍 SUPPORTED LANGUAGES:" in output
        
        # Check for specific examples
        assert "Basic YouTube video transcription" in output
        assert "Generate SRT subtitles" in output
        assert "Force MLX acceleration" in output
        assert "Translate any language to English" in output
        assert "JSON output with full metadata" in output
        
        # Check model guidance
        assert "tiny: 32x faster, good for quick drafts" in output
        assert "base: 16x faster, good balance (default)" in output
        assert "large: Best accuracy, slower" in output
        
        # Check language support
        assert "English (en), Spanish (es)" in output
        assert "99+ languages" in output

    def test_playlist_help_output(self):
        """Test playlist command help contains batch processing info."""
        result = self.runner.invoke(playlist, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check for enhanced help sections
        assert "📃 Transcribe all videos from a YouTube playlist or channel" in output
        assert "📋 EXAMPLES:" in output
        assert "🎯 SUPPORTED URL TYPES:" in output
        assert "📊 OUTPUT FORMAT:" in output
        assert "⚡ PERFORMANCE TIPS:" in output
        
        # Check for specific examples
        assert "Process entire playlist" in output
        assert "Process channel with video limit" in output
        assert "Use MLX acceleration for faster processing" in output
        
        # Check URL types
        assert "Playlist URLs: /playlist?list=PLxxxxxx" in output
        assert "Channel URLs: /@channelname" in output
        assert "User URLs: /user/username" in output
        
        # Check performance tips
        assert "Use 'tiny' or 'base' models for faster batch processing" in output
        assert "Enable MLX acceleration on Apple Silicon" in output

    def test_info_help_output(self):
        """Test info command help contains metadata information."""
        result = self.runner.invoke(info, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check for enhanced help sections
        assert "ℹ️ Get detailed information about a YouTube video" in output
        assert "📋 EXAMPLES:" in output
        assert "📊 DISPLAYED INFORMATION:" in output
        assert "💡 USE CASES:" in output
        
        # Check displayed information
        assert "Title: Video title" in output
        assert "Author: Channel name" in output
        assert "Duration: Video length in seconds" in output
        assert "Views: View count" in output
        
        # Check use cases
        assert "Verify video accessibility before transcription" in output
        assert "Check video duration for processing time estimates" in output

    def test_models_help_output(self):
        """Test models command help contains model selection guidance."""
        result = self.runner.invoke(models, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check for enhanced help sections
        assert "🤖 List all available Whisper models" in output
        assert "📋 EXAMPLES:" in output
        assert "🎯 MODEL SELECTION GUIDE:" in output
        assert "⚡ PERFORMANCE NOTES:" in output
        
        # Check model guidance
        assert "tiny: Quick drafts, testing, low-resource environments" in output
        assert "base: General use, good balance of speed/accuracy (recommended)" in output
        assert "large: Maximum accuracy for critical/professional use" in output
        
        # Check performance notes
        assert "Speed is relative to 'large' model baseline" in output
        assert "MLX acceleration (Apple Silicon) reduces memory usage" in output
        assert "First run downloads models" in output

    def test_version_output(self):
        """Test version flag output."""
        result = self.runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert f"vidscribe version {__version__}" in result.output

    def test_no_command_shows_help(self):
        """Test that running CLI without command shows help."""
        result = self.runner.invoke(cli, [])
        
        assert result.exit_code == 0
        assert "🎬 Vidscribe - Professional Video Transcription CLI Tool" in result.output


class TestCLIIntegration:
    """Test CLI command integration."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    @patch('vidscribe.cli.TranscriptionEngine')
    @patch('vidscribe.cli.YouTubeDownloader')
    def test_transcribe_command_basic(self, mock_downloader, mock_engine):
        """Test basic transcribe command functionality."""
        # Mock the dependencies
        mock_engine_instance = MagicMock()
        mock_engine.return_value = mock_engine_instance
        mock_engine_instance.transcribe_audio.return_value = {
            "text": "Test transcription",
            "transcription_time": 5.0,
        }
        
        mock_downloader_instance = MagicMock()
        mock_downloader.return_value = mock_downloader_instance
        mock_downloader_instance.get_video_info.return_value = {
            "title": "Test Video",
            "duration": 120,
        }
        mock_downloader_instance.download_video.return_value = "/tmp/test.mp3"
        
        # Test transcribe command with YouTube URL
        result = self.runner.invoke(transcribe, [
            "https://youtube.com/watch?v=test123"
        ])
        
        # Should not crash and should show transcription output
        assert result.exit_code == 0
        assert "Transcription:" in result.output

    @patch('vidscribe.cli.validate_youtube_url')
    @patch('vidscribe.cli.PlaylistProcessor')
    def test_playlist_command_basic(self, mock_processor, mock_validator):
        """Test basic playlist command functionality."""
        # Mock validation
        mock_validator.return_value = None
        
        # Mock processor
        mock_processor_instance = MagicMock()
        mock_processor.return_value = mock_processor_instance
        
        # Test playlist command
        result = self.runner.invoke(playlist, [
            "https://youtube.com/playlist?list=test123",
            "-o", "output.csv"
        ])
        
        # Should not crash
        assert result.exit_code == 0

    @patch('vidscribe.cli.validate_youtube_url')
    @patch('vidscribe.cli.YouTubeDownloader')
    def test_info_command_basic(self, mock_downloader, mock_validator):
        """Test basic info command functionality."""
        # Mock validation
        mock_validator.return_value = None
        
        # Mock downloader
        mock_downloader_instance = MagicMock()
        mock_downloader.return_value = mock_downloader_instance
        mock_downloader_instance.get_video_info.return_value = {
            "title": "Test Video",
            "author": "Test Author",
            "duration": 120,
            "views": 1000,
            "video_id": "test123",
            "url": "https://youtube.com/watch?v=test123",
        }
        
        # Test info command
        result = self.runner.invoke(info, [
            "https://youtube.com/watch?v=test123"
        ])
        
        # Should not crash and should show video info
        assert result.exit_code == 0

    def test_models_command_basic(self):
        """Test basic models command functionality."""
        result = self.runner.invoke(models, [])
        
        # Should not crash and should show model table
        assert result.exit_code == 0
        assert "Available Whisper Models" in result.output
        assert "tiny" in result.output
        assert "base" in result.output
        assert "large" in result.output


class TestCLIValidation:
    """Test CLI input validation."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_transcribe_invalid_input(self):
        """Test transcribe with invalid input."""
        result = self.runner.invoke(transcribe, ["/nonexistent/file.mp4"])
        
        # Should exit with error for nonexistent file
        assert result.exit_code == 1

    @patch('vidscribe.cli.validate_youtube_url')
    def test_playlist_invalid_url(self, mock_validator):
        """Test playlist with invalid URL."""
        # Mock validation to raise error
        mock_validator.side_effect = ValueError("Invalid URL")
        
        result = self.runner.invoke(playlist, ["https://invalid-url.com"])
        
        # Should exit with error
        assert result.exit_code == 1
        assert "Invalid URL" in result.output

    @patch('vidscribe.cli.validate_youtube_url')
    def test_info_invalid_url(self, mock_validator):
        """Test info with invalid URL."""
        # Mock validation to raise error
        mock_validator.side_effect = ValueError("Invalid URL")
        
        result = self.runner.invoke(info, ["https://invalid-url.com"])
        
        # Should exit with error
        assert result.exit_code == 1
        assert "Invalid URL" in result.output


class TestCLIOptions:
    """Test CLI command options."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_transcribe_model_option(self):
        """Test transcribe command with model option."""
        result = self.runner.invoke(transcribe, [
            "--help"  # Just test help to avoid complex mocking
        ])
        
        assert result.exit_code == 0
        assert "--model" in result.output
        assert "[tiny|base|small|medium|large]" in result.output

    def test_transcribe_format_option(self):
        """Test transcribe command with format option."""
        result = self.runner.invoke(transcribe, ["--help"])
        
        assert result.exit_code == 0
        assert "--format" in result.output
        assert "[text|json|csv|srt|vtt]" in result.output

    def test_transcribe_mlx_option(self):
        """Test transcribe command with MLX option."""
        result = self.runner.invoke(transcribe, ["--help"])
        
        assert result.exit_code == 0
        assert "--use-mlx / --no-mlx" in result.output
        assert "MLX acceleration on Apple Silicon" in result.output

    def test_playlist_limit_option(self):
        """Test playlist command with limit option."""
        result = self.runner.invoke(playlist, ["--help"])
        
        assert result.exit_code == 0
        assert "--limit" in result.output
        assert "Maximum number of videos to process" in result.output