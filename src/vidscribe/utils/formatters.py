"""Output formatting utilities."""

from pathlib import Path
from typing import Any, Dict


class SubtitleFormatter:
    """Formatter for subtitle files (SRT, VTT)."""

    @staticmethod
    def format_timestamp_srt(seconds: float) -> str:
        """
        Format timestamp for SRT format.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")

    @staticmethod
    def format_timestamp_vtt(seconds: float) -> str:
        """
        Format timestamp for WebVTT format.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    def save_as_srt(self, result: Dict[str, Any], output_path: Path) -> None:
        """
        Save transcription as SRT subtitle file.

        Args:
            result: Transcription result with segments
            output_path: Output file path
        """
        with open(output_path, "w", encoding="utf-8") as f:
            if "segments" in result:
                for i, segment in enumerate(result["segments"], 1):
                    start = self.format_timestamp_srt(segment["start"])
                    end = self.format_timestamp_srt(segment["end"])
                    f.write(f"{i}\n")
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{segment['text'].strip()}\n\n")

    def save_as_vtt(self, result: Dict[str, Any], output_path: Path) -> None:
        """
        Save transcription as WebVTT subtitle file.

        Args:
            result: Transcription result with segments
            output_path: Output file path
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            if "segments" in result:
                for segment in result["segments"]:
                    start = self.format_timestamp_vtt(segment["start"])
                    end = self.format_timestamp_vtt(segment["end"])
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{segment['text'].strip()}\n\n")


class TableFormatter:
    """Formatter for table output."""

    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        Format duration in seconds to human-readable format.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    @staticmethod
    def format_size(bytes: int) -> str:
        """
        Format file size in bytes to human-readable format.

        Args:
            bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"