"""Core transcription engine using OpenAI Whisper."""

import json
import logging
import os
import platform
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Any

import ffmpeg

from vidscribe.utils.formatters import SubtitleFormatter
from vidscribe.utils.validators import validate_file_path

# Platform detection for MLX support
is_mac_silicon = platform.system() == "Darwin" and platform.machine() == "arm64"
mlx_available = False

if is_mac_silicon:
    try:
        import mlx_whisper
        mlx_available = True
    except ImportError:
        pass

# Always try to import standard whisper as fallback
try:
    import whisper
    whisper_available = True
except ImportError:
    whisper_available = False

logger = logging.getLogger(__name__)


class TranscriptionEngine:
    """Handles audio/video transcription using Whisper."""

    SUPPORTED_MODELS = ["tiny", "base", "small", "medium", "large"]
    SUPPORTED_FORMATS = ["text", "json", "csv", "srt", "vtt"]
    MLX_MODEL_MAP = {
        "tiny": "mlx-community/whisper-tiny",
        "base": "mlx-community/whisper-base",
        "small": "mlx-community/whisper-small",
        "medium": "mlx-community/whisper-medium",
        "large": "mlx-community/whisper-large-v3",
    }

    def __init__(self, model_size: str = "base", device: Optional[str] = None, use_mlx: Optional[bool] = None):
        """
        Initialize the transcription engine.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to use for inference (cpu, cuda, or None for auto)
            use_mlx: Force MLX usage (True), disable MLX (False), or auto-detect (None)
        """
        if model_size not in self.SUPPORTED_MODELS:
            raise ValueError(f"Invalid model size. Must be one of {self.SUPPORTED_MODELS}")

        self.model_size = model_size
        self.device = device
        self.model = None
        
        # Determine which backend to use
        if use_mlx is None:
            # Auto-detect: use MLX if available on Apple Silicon
            self.use_mlx = mlx_available and is_mac_silicon
        else:
            self.use_mlx = use_mlx and mlx_available
        
        # Fallback to standard whisper if MLX not available but requested
        if use_mlx and not mlx_available:
            logger.warning("MLX requested but not available. Install with: pip install mlx-whisper")
            self.use_mlx = False
        
        # Ensure we have at least one backend available
        if not self.use_mlx and not whisper_available:
            raise RuntimeError("No transcription backend available. Install whisper or mlx-whisper.")
        
        self._load_model()

    def _load_model(self) -> None:
        """Load the Whisper model."""
        backend = "MLX" if self.use_mlx else "Whisper"
        logger.info(f"Loading {backend} model: {self.model_size}")
        
        try:
            if self.use_mlx:
                # MLX doesn't preload models, they're loaded on first transcribe
                # Store the model path for MLX
                self.mlx_model_path = self.MLX_MODEL_MAP.get(self.model_size)
                logger.info(f"MLX model configured: {self.mlx_model_path}")
            else:
                self.model = whisper.load_model(self.model_size, device=self.device)
                logger.info("Standard Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Failed to load {backend} model: {e}")

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
        backend = "MLX" if self.use_mlx else "Whisper"
        logger.info(f"Transcribing audio with {backend}: {audio_path}")

        start_time = time.time()

        try:
            if self.use_mlx:
                # MLX transcription
                mlx_kwargs = {}
                if language:
                    mlx_kwargs['language'] = language
                    
                # Check for Hugging Face token for private model access
                hf_token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
                if hf_token:
                    mlx_kwargs['hf_token'] = hf_token
                
                # MLX doesn't support 'task' parameter directly
                # Translation is done via different model or post-processing
                
                result = mlx_whisper.transcribe(
                    audio_path,
                    path_or_hf_repo=self.mlx_model_path,
                    **mlx_kwargs
                )
                
                # Normalize MLX output to match whisper format
                if task == "translate" and language != "en":
                    logger.warning("MLX translation to English requested - using transcription")
            else:
                # Standard Whisper transcription
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
                "backend": backend,
            })

            logger.info(f"Transcription completed in {transcription_time:.2f} seconds using {backend}")
            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Transcription failed: {e}")
            
            # Provide specific guidance for authentication errors
            if "401" in error_msg or "Authorization" in error_msg or "credentials" in error_msg:
                auth_msg = (
                    f"Authentication failed for Hugging Face model. "
                    f"Please set your Hugging Face token as an environment variable:\n"
                    f"export HF_TOKEN=your_token_here\n"
                    f"or\n"
                    f"export HUGGINGFACE_TOKEN=your_token_here\n"
                    f"You can get a token from https://huggingface.co/settings/tokens"
                )
                logger.error(auth_msg)
                raise RuntimeError(f"Failed to transcribe audio: {auth_msg}")
            elif "Repository Not Found" in error_msg:
                repo_msg = (
                    f"Model repository not found. This may be due to:\n"
                    f"1. Missing authentication (set HF_TOKEN environment variable)\n"
                    f"2. Model repository doesn't exist or is private\n"
                    f"3. Network connectivity issues"
                )
                logger.error(repo_msg)
                raise RuntimeError(f"Failed to transcribe audio: {repo_msg}")
            else:
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