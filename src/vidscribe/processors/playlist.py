"""YouTube playlist and channel processing module."""

import csv
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

from vidscribe.core.engine import TranscriptionEngine
from vidscribe.downloaders.youtube import YouTubeDownloader

logger = logging.getLogger(__name__)
console = Console()


class PlaylistProcessor:
    """Handles batch processing of YouTube playlists and channels."""

    def __init__(
        self,
        model_size: str = "base",
        keep_audio: bool = False,
        output_dir: Optional[str] = None,
        use_mlx: Optional[bool] = None
    ):
        """
        Initialize the playlist processor.

        Args:
            model_size: Whisper model size
            keep_audio: Keep downloaded audio files
            output_dir: Directory for temporary files
            use_mlx: Force MLX usage (True), disable MLX (False), or auto-detect (None)
        """
        self.model_size = model_size
        self.keep_audio = keep_audio
        self.output_dir = output_dir

        # Initialize components
        self.downloader = YouTubeDownloader(output_dir=output_dir, keep_files=keep_audio)
        self.engine = TranscriptionEngine(model_size=model_size, use_mlx=use_mlx)

        # Track processing stats
        self.stats = {
            "total_videos": 0,
            "processed": 0,
            "failed": 0,
            "skipped": 0,
            "total_duration": 0,
            "total_transcription_time": 0,
        }

    def process_playlist(self, playlist_url: str, output_csv: str) -> None:
        """
        Process all videos in a YouTube playlist.

        Args:
            playlist_url: YouTube playlist URL
            output_csv: Path to output CSV file
        """
        logger.info(f"Processing playlist: {playlist_url}")

        # Get all video URLs
        video_urls = self.downloader.get_playlist_videos(playlist_url)

        if not video_urls:
            console.print("[yellow]No videos found in playlist[/yellow]")
            return

        self.stats["total_videos"] = len(video_urls)
        console.print(f"[cyan]Found {len(video_urls)} videos to process[/cyan]")

        # Process videos and save to CSV
        self._process_video_list(video_urls, output_csv)

        # Print summary
        self._print_summary()

    def process_channel(
        self,
        channel_url: str,
        output_csv: str,
        limit: Optional[int] = None
    ) -> None:
        """
        Process all videos from a YouTube channel.

        Args:
            channel_url: YouTube channel URL
            output_csv: Path to output CSV file
            limit: Maximum number of videos to process
        """
        logger.info(f"Processing channel: {channel_url}")

        # Get all video URLs
        video_urls = self.downloader.get_channel_videos(channel_url, limit=limit)

        if not video_urls:
            console.print("[yellow]No videos found in channel[/yellow]")
            return

        self.stats["total_videos"] = len(video_urls)
        console.print(f"[cyan]Found {len(video_urls)} videos to process[/cyan]")

        # Process videos and save to CSV
        self._process_video_list(video_urls, output_csv)

        # Print summary
        self._print_summary()

    def _process_video_list(self, video_urls: List[str], output_csv: str) -> None:
        """
        Process a list of video URLs and save to CSV.

        Args:
            video_urls: List of YouTube video URLs
            output_csv: Path to output CSV file
        """
        # Prepare CSV file
        csv_path = Path(output_csv)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file exists to determine if we need to write headers
        file_exists = csv_path.exists()

        with open(csv_path, "a" if file_exists else "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "Index",
                "Title",
                "Video Link",
                "Video Length (seconds)",
                "Transcription Time (seconds)",
                "Transcription",
                "Processed At",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            # Process each video with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "[cyan]Processing videos...",
                    total=len(video_urls)
                )

                for i, url in enumerate(video_urls, 1):
                    progress.update(task, description=f"[cyan]Processing video {i}/{len(video_urls)}")

                    try:
                        # Process single video
                        result = self._process_single_video(url, i)

                        if result:
                            # Write to CSV
                            writer.writerow(result)
                            csvfile.flush()
                            self.stats["processed"] += 1
                        else:
                            self.stats["failed"] += 1

                    except KeyboardInterrupt:
                        console.print("\n[yellow]Processing interrupted by user[/yellow]")
                        break
                    except Exception as e:
                        logger.error(f"Error processing {url}: {e}")
                        self.stats["failed"] += 1

                    progress.advance(task)

                    # Brief pause to avoid overwhelming the API
                    if i < len(video_urls):
                        time.sleep(1)

        console.print(f"\n[green]✓[/green] Transcriptions saved to: {csv_path}")

    def _process_single_video(self, url: str, index: int) -> Optional[Dict[str, Any]]:
        """
        Process a single video.

        Args:
            url: YouTube video URL
            index: Video index number

        Returns:
            Dictionary with video data or None if failed
        """
        try:
            # Get video info
            video_info = self.downloader.get_video_info(url)
            if not video_info:
                logger.error(f"Failed to get info for: {url}")
                return None

            console.print(f"  [dim]Title: {video_info['title']}[/dim]")

            # Download video
            audio_path = self.downloader.download_video(url)
            if not audio_path:
                logger.error(f"Failed to download: {url}")
                return None

            # Transcribe
            result = self.engine.transcribe_audio(audio_path)

            # Update stats
            self.stats["total_duration"] += video_info.get("duration", 0)
            self.stats["total_transcription_time"] += result.get("transcription_time", 0)

            # Clean up audio file if not keeping
            if not self.keep_audio and os.path.exists(audio_path):
                os.remove(audio_path)

            # Return data for CSV
            return {
                "Index": index,
                "Title": video_info["title"],
                "Video Link": url,
                "Video Length (seconds)": video_info.get("duration", 0),
                "Transcription Time (seconds)": result.get("transcription_time", 0),
                "Transcription": result["text"],
                "Processed At": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing video {url}: {e}")
            return None

    def _print_summary(self) -> None:
        """Print processing summary."""
        # Create summary table
        table = Table(title="Processing Summary", show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        table.add_row("Total videos", str(self.stats["total_videos"]))
        table.add_row("Successfully processed", f"[green]{self.stats['processed']}[/green]")
        table.add_row("Failed", f"[red]{self.stats['failed']}[/red]")

        if self.stats["total_duration"] > 0:
            total_duration_min = self.stats["total_duration"] / 60
            table.add_row("Total video duration", f"{total_duration_min:.1f} minutes")

        if self.stats["total_transcription_time"] > 0:
            total_trans_min = self.stats["total_transcription_time"] / 60
            table.add_row("Total transcription time", f"{total_trans_min:.1f} minutes")

            if self.stats["total_duration"] > 0:
                speed_ratio = self.stats["total_duration"] / self.stats["total_transcription_time"]
                table.add_row("Processing speed", f"{speed_ratio:.1f}x real-time")

        console.print("\n")
        console.print(table)