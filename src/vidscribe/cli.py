"""Command-line interface for vidscribe."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from vidscribe import __version__
from vidscribe.core.engine import TranscriptionEngine
from vidscribe.downloaders.youtube import YouTubeDownloader
from vidscribe.processors.playlist import PlaylistProcessor
from vidscribe.utils.config import load_config
from vidscribe.utils.validators import validate_youtube_url, is_youtube_url

console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with rich handler."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--version", is_flag=True, help="Show version and exit.")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output.")
@click.option("--config", type=click.Path(exists=True), help="Path to config file.")
def cli(ctx: click.Context, version: bool, verbose: bool, config: Optional[str]) -> None:
    """
    Vidscribe - Video Transcription CLI Tool.

    Transcribe YouTube videos and local video files using OpenAI Whisper.
    """
    if version:
        console.print(f"vidscribe version {__version__}")
        sys.exit(0)

    setup_logging(verbose)

    # Load configuration
    if config:
        ctx.obj = load_config(config)
    else:
        ctx.obj = {}

    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("input", type=str)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file path"
)
@click.option(
    "-m", "--model",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    default="base",
    help="Whisper model size"
)
@click.option(
    "-f", "--format",
    type=click.Choice(["text", "json", "csv", "srt", "vtt"]),
    default="text",
    help="Output format"
)
@click.option(
    "--language",
    type=str,
    help="Language code (e.g., 'en', 'es', 'fr')"
)
@click.option(
    "--task",
    type=click.Choice(["transcribe", "translate"]),
    default="transcribe",
    help="Task to perform"
)
@click.option(
    "--keep-audio",
    is_flag=True,
    help="Keep downloaded audio files"
)
@click.pass_context
def transcribe(
    ctx: click.Context,
    input: str,
    output: Optional[str],
    model: str,
    format: str,
    language: Optional[str],
    task: str,
    keep_audio: bool
) -> None:
    """
    Transcribe a video or audio file.

    INPUT can be a YouTube URL or a local file path.
    """
    logger = logging.getLogger(__name__)

    with console.status("[bold green]Initializing...") as status:
        # Initialize transcription engine
        engine = TranscriptionEngine(model_size=model)

        # Check if input is a YouTube URL
        if is_youtube_url(input):
            status.update("[bold yellow]Downloading from YouTube...")
            downloader = YouTubeDownloader(keep_files=keep_audio)

            # Get video info
            video_info = downloader.get_video_info(input)
            if video_info:
                console.print(f"[cyan]Title:[/cyan] {video_info['title']}")
                console.print(f"[cyan]Duration:[/cyan] {video_info['duration']} seconds")

            # Download video
            audio_path = downloader.download_video(input)
            if not audio_path:
                console.print("[red]Failed to download video[/red]")
                sys.exit(1)

            status.update("[bold blue]Transcribing audio...")
            result = engine.transcribe_audio(audio_path, language=language, task=task)

            # Add metadata
            if video_info:
                result.update({
                    "title": video_info["title"],
                    "url": input,
                })

            if not keep_audio:
                Path(audio_path).unlink(missing_ok=True)

        else:
            # Local file
            input_path = Path(input)
            if not input_path.exists():
                console.print(f"[red]File not found: {input}[/red]")
                sys.exit(1)

            status.update("[bold blue]Transcribing file...")

            # Check if it's a video or audio file
            video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
            if input_path.suffix.lower() in video_extensions:
                result = engine.transcribe_video(
                    str(input_path),
                    language=language,
                    task=task,
                    keep_audio=keep_audio
                )
            else:
                result = engine.transcribe_audio(
                    str(input_path),
                    language=language,
                    task=task
                )

    # Output results
    if output:
        engine.save_transcription(result, output, format=format)
        console.print(f"[green]✓[/green] Transcription saved to: {output}")
    else:
        # Print to console
        console.print("\n[bold]Transcription:[/bold]")
        console.print(result["text"])


@cli.command()
@click.argument("url", type=str)
@click.option(
    "-o", "--output",
    type=click.Path(),
    default="playlist_transcriptions.csv",
    help="Output CSV file path"
)
@click.option(
    "-m", "--model",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    default="base",
    help="Whisper model size"
)
@click.option(
    "--limit",
    type=int,
    help="Maximum number of videos to process"
)
@click.option(
    "--keep-audio",
    is_flag=True,
    help="Keep downloaded audio files"
)
@click.pass_context
def playlist(
    ctx: click.Context,
    url: str,
    output: str,
    model: str,
    limit: Optional[int],
    keep_audio: bool
) -> None:
    """
    Transcribe all videos from a YouTube playlist or channel.

    URL should be a YouTube playlist or channel URL.
    """
    logger = logging.getLogger(__name__)

    try:
        validate_youtube_url(url)
    except ValueError as e:
        console.print(f"[red]Invalid URL: {e}[/red]")
        sys.exit(1)

    # Initialize processor
    processor = PlaylistProcessor(model_size=model, keep_audio=keep_audio)

    # Determine if it's a playlist or channel
    if "playlist" in url or "list=" in url:
        console.print(f"[cyan]Processing playlist...[/cyan]")
        processor.process_playlist(url, output)
    else:
        console.print(f"[cyan]Processing channel...[/cyan]")
        processor.process_channel(url, output, limit=limit)

    console.print(f"[green]✓[/green] Transcriptions saved to: {output}")


@cli.command()
@click.argument("url", type=str)
def info(url: str) -> None:
    """
    Get information about a YouTube video.

    URL should be a YouTube video URL.
    """
    try:
        validate_youtube_url(url)
    except ValueError as e:
        console.print(f"[red]Invalid URL: {e}[/red]")
        sys.exit(1)

    downloader = YouTubeDownloader()
    video_info = downloader.get_video_info(url)

    if not video_info:
        console.print("[red]Failed to get video information[/red]")
        sys.exit(1)

    # Create a table for displaying info
    table = Table(title="Video Information", show_header=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    table.add_row("Title", video_info["title"])
    table.add_row("Author", video_info["author"])
    table.add_row("Duration", f"{video_info['duration']} seconds")
    table.add_row("Views", f"{video_info['views']:,}")
    table.add_row("Video ID", video_info["video_id"])
    table.add_row("URL", video_info["url"])

    console.print(table)


@cli.command()
def models() -> None:
    """List available Whisper models."""
    table = Table(title="Available Whisper Models")
    table.add_column("Model", style="cyan")
    table.add_column("Parameters")
    table.add_column("English-only")
    table.add_column("Multilingual")
    table.add_column("Required VRAM")
    table.add_column("Relative Speed")

    models_info = [
        ("tiny", "39M", "✓", "✓", "~1 GB", "~32x"),
        ("base", "74M", "✓", "✓", "~1 GB", "~16x"),
        ("small", "244M", "✓", "✓", "~2 GB", "~6x"),
        ("medium", "769M", "✓", "✓", "~5 GB", "~2x"),
        ("large", "1550M", "-", "✓", "~10 GB", "1x"),
    ]

    for model_info in models_info:
        table.add_row(*model_info)

    console.print(table)


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()