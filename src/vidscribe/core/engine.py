"""Core transcription engine using OpenAI Whisper."""

import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Any

import ffmpeg
import whisper

from vidscribe.utils.formatters import SubtitleFormatter
from vidscribe.utils.validators import validate_file_path

logger = logging.getLogger(__name__)


class TranscriptionEngine:
    """Handles audio/video transcription using Whisper."""

    SUPPORTED_MODELS = ["tiny", "base", "small", "medium", "large"]
    SUPPORTED_FORMATS = ["text", "json", "csv", "srt", "vtt"]

    def __init__(self, model_size: str = "base", device: Optional[str] = None):
        """
        Initialize the transcription engine.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to use for inference (cpu, cuda, or None for auto)
        """
        if model_size not in self.SUPPORTED_MODELS:
            raise ValueError(f"Invalid model size. Must be one of {self.SUPPORTED_MODELS}")

        self.model_size = model_size
        self.device = device
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the Whisper model."""
        logger.info(f"Loading Whisper model: {self.model_size}")
        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}")

    def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to the audio file
            language: Language code (e.g., 'en', 'es', 'fr')
            task: Task to perform ('transcribe' or 'translate')
            **kwargs: Additional arguments for whisper.transcribe

        Returns:
            Transcription result with text and metadata
        """
        validate_file_path(audio_path)
        logger.info(f"Transcribing audio: {audio_path}")

        start_time = time.time()

        try:
            result = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                verbose=False,
                **kwargs
            )

            transcription_time = time.time() - start_time

            result.update({
                "transcription_time": transcription_time,
                "audio_file": audio_path,
                "model_size": self.model_size,
                "task": task,
            })

            logger.info(f"Transcription completed in {transcription_time:.2f} seconds")
            return result

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Failed to transcribe audio: {e}")

    def transcribe_video(
        self,
        video_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        keep_audio: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe a video file by extracting audio first.

        Args:
            video_path: Path to the video file
            language: Language code
            task: Task to perform
            keep_audio: Whether to keep the extracted audio file
            **kwargs: Additional arguments for transcription

        Returns:
            Transcription result
        """
        validate_file_path(video_path)
        logger.info(f"Processing video: {video_path}")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
            audio_path = tmp_audio.name

        try:
            # Extract audio from video
            logger.info("Extracting audio from video")
            self._extract_audio(video_path, audio_path)

            # Get video metadata
            metadata = self._get_video_metadata(video_path)

            # Transcribe the extracted audio
            result = self.transcribe_audio(audio_path, language, task, **kwargs)
            result.update({
                "video_file": video_path,
                "duration": metadata.get("duration", 0),
                "video_codec": metadata.get("codec_name"),
            })

            return result

        finally:
            # Clean up temporary audio file
            if not keep_audio and os.path.exists(audio_path):
                os.remove(audio_path)
                logger.debug(f"Removed temporary audio file: {audio_path}")

    def _extract_audio(self, video_path: str, audio_path: str) -> None:
        """Extract audio from video file."""
        try:
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream, audio_path, acodec="mp3", audio_bitrate="192k")
            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise RuntimeError(f"Failed to extract audio: {e.stderr.decode()}")

    def _get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Get video metadata using ffprobe."""
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(
                (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
                None
            )
            if video_stream:
                return {
                    "duration": float(probe["format"].get("duration", 0)),
                    "codec_name": video_stream.get("codec_name"),
                    "width": video_stream.get("width"),
                    "height": video_stream.get("height"),
                }
            return {"duration": float(probe["format"].get("duration", 0))}
        except Exception as e:
            logger.warning(f"Failed to get video metadata: {e}")
            return {}

    def save_transcription(
        self,
        result: Dict[str, Any],
        output_path: str,
        format: str = "text"
    ) -> None:
        """
        Save transcription result to file.

        Args:
            result: Transcription result dict
            output_path: Output file path
            format: Output format (text, json, csv, srt, vtt)
        """
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format. Must be one of {self.SUPPORTED_FORMATS}")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving transcription to {output_path} as {format}")

        try:
            if format == "text":
                self._save_as_text(result, output_path)
            elif format == "json":
                self._save_as_json(result, output_path)
            elif format == "csv":
                self._save_as_csv(result, output_path)
            elif format in ["srt", "vtt"]:
                formatter = SubtitleFormatter()
                if format == "srt":
                    formatter.save_as_srt(result, output_path)
                else:
                    formatter.save_as_vtt(result, output_path)

            logger.info(f"Transcription saved successfully")

        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
            raise RuntimeError(f"Failed to save transcription: {e}")

    def _save_as_text(self, result: Dict[str, Any], output_path: Path) -> None:
        """Save transcription as plain text."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

    def _save_as_json(self, result: Dict[str, Any], output_path: Path) -> None:
        """Save transcription as JSON."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    def _save_as_csv(self, result: Dict[str, Any], output_path: Path) -> None:
        """Save transcription as CSV."""
        import csv

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Duration", "Transcription Time", "Text"])
            writer.writerow([
                result.get("title", "Unknown"),
                result.get("duration", 0),
                result.get("transcription_time", 0),
                result["text"]
            ])