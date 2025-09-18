"""Unit tests for formatters module."""

import pytest
from pathlib import Path

from vidscribe.utils.formatters import SubtitleFormatter, TableFormatter


class TestSubtitleFormatter:
    """Test subtitle formatting."""

    def test_format_timestamp_srt(self):
        """Test SRT timestamp formatting."""
        formatter = SubtitleFormatter()
        
        # Test various time values
        assert formatter.format_timestamp_srt(0) == "00:00:00,000"
        assert formatter.format_timestamp_srt(1.5) == "00:00:01,500"
        assert formatter.format_timestamp_srt(61.25) == "00:01:01,250"
        assert formatter.format_timestamp_srt(3661.5) == "01:01:01,500"

    def test_format_timestamp_vtt(self):
        """Test VTT timestamp formatting."""
        formatter = SubtitleFormatter()
        
        # Test various time values
        assert formatter.format_timestamp_vtt(0) == "00:00:00.000"
        assert formatter.format_timestamp_vtt(1.5) == "00:00:01.500"
        assert formatter.format_timestamp_vtt(61.25) == "00:01:01.250"
        assert formatter.format_timestamp_vtt(3661.5) == "01:01:01.500"

    def test_save_as_srt(self, temp_dir, sample_transcription_result):
        """Test saving transcription as SRT."""
        formatter = SubtitleFormatter()
        output_path = temp_dir / "test.srt"
        
        formatter.save_as_srt(sample_transcription_result, output_path)
        
        content = output_path.read_text()
        assert "1\n" in content
        assert "00:00:00,000 --> 00:00:02,000" in content
        assert "This is" in content

    def test_save_as_vtt(self, temp_dir, sample_transcription_result):
        """Test saving transcription as VTT."""
        formatter = SubtitleFormatter()
        output_path = temp_dir / "test.vtt"
        
        formatter.save_as_vtt(sample_transcription_result, output_path)
        
        content = output_path.read_text()
        assert "WEBVTT" in content
        assert "00:00:00.000 --> 00:00:02.000" in content
        assert "This is" in content


class TestTableFormatter:
    """Test table formatting."""

    def test_format_duration(self):
        """Test duration formatting."""
        formatter = TableFormatter()
        
        assert formatter.format_duration(30) == "30s"
        assert formatter.format_duration(90) == "1m 30s"
        assert formatter.format_duration(3690) == "1h 1m"
        assert formatter.format_duration(7200) == "2h 0m"

    def test_format_size(self):
        """Test file size formatting."""
        formatter = TableFormatter()
        
        assert formatter.format_size(500) == "500.00 B"
        assert formatter.format_size(1536) == "1.50 KB"
        assert formatter.format_size(1048576) == "1.00 MB"
        assert formatter.format_size(1073741824) == "1.00 GB"