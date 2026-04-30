"""Command-line interface for vidscribe."""

import logging
import sys
from datetime import datetime
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
    \b
    🎬 Vidscribe - Professional Video Transcription CLI Tool
    
    Powered by OpenAI Whisper with MLX acceleration for Apple Silicon.
    Transcribe YouTube videos, playlists, channels, and local video files.
    
    \b
    🚀 CORE CAPABILITIES:
    • YouTube Videos: Single video transcription with metadata
    • YouTube Playlists: Batch process entire playlists
    • YouTube Channels: Process channel videos with limits
    • Local Videos: MP4, AVI, MOV, MKV, WebM support
    • Local Audio: Direct audio file transcription
    • Multiple Models: tiny, base, small, medium, large
    • Output Formats: text, JSON, CSV, SRT subtitles, WebVTT
    • MLX Acceleration: 50% faster on Apple Silicon (auto-detected)
    • Batch Processing: Efficient playlist/channel processing
    • Multi-language: 99+ languages supported
    • Translation: Translate any language to English
    
    \b
    📖 QUICK EXAMPLES:
    
    # Transcribe YouTube video
    vidscribe transcribe "https://youtu.be/VIDEO_ID"
    
    # Process playlist with better model
    vidscribe playlist "https://youtube.com/playlist?list=ID" -m large
    
    # Local video with subtitles
    vidscribe transcribe video.mp4 -o subtitles.srt -f srt
    
    # Get video info
    vidscribe info "https://youtu.be/VIDEO_ID"
    
    # List available models
    vidscribe models
    
    \b
    ⚡ PERFORMANCE FEATURES:
    • Auto-detects MLX acceleration on Apple Silicon
    • Configurable model sizes (tiny=32x faster, large=highest accuracy)
    • Progress tracking with rich terminal output
    • Automatic audio extraction from videos
    • Optimized batch processing for playlists
    
    \b
    📁 OUTPUT FORMATS:
    • text: Plain text transcription
    • json: Full metadata + transcription
    • csv: Spreadsheet-compatible format
    • srt: Standard subtitle format
    • vtt: WebVTT subtitle format
    
    Use 'vidscribe COMMAND --help' for detailed command options.
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
    "--use-mlx/--no-mlx",
    default=False,
    help="Use MLX acceleration on Apple Silicon (disabled by default)"
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
@click.option(
    "--cookies-from-browser",
    type=str,
    default=None,
    help="Browser to pull cookies from to bypass bot detection (e.g. chrome, firefox, safari)"
)
@click.option(
    "--cookies-file",
    type=click.Path(exists=True),
    default=None,
    help="Path to a Netscape-format cookies file"
)
@click.pass_context
def transcribe(
    ctx: click.Context,
    input: str,
    output: Optional[str],
    model: str,
    use_mlx: Optional[bool],
    format: str,
    language: Optional[str],
    task: str,
    keep_audio: bool,
    cookies_from_browser: Optional[str],
    cookies_file: Optional[str],
) -> None:
    """
    \b
    🎥 Transcribe a single video or audio file.
    
    INPUT can be a YouTube URL, local video file, or audio file.
    
    \b
    📋 EXAMPLES:
    
    # Basic YouTube video transcription
    vidscribe transcribe "https://youtu.be/dQw4w9WgXcQ"
    
    # Save to file with specific format
    vidscribe transcribe "VIDEO_URL" -o transcript.txt -f text
    
    # Generate SRT subtitles
    vidscribe transcribe "VIDEO_URL" -o subs.srt -f srt
    
    # Use larger model for better accuracy
    vidscribe transcribe "VIDEO_URL" -m large
    
    # Force MLX acceleration (Apple Silicon)
    vidscribe transcribe "VIDEO_URL" --use-mlx
    
    # Transcribe Spanish video in Spanish
    vidscribe transcribe "VIDEO_URL" --language es
    
    # Translate any language to English
    vidscribe transcribe "VIDEO_URL" --task translate
    
    # Local video file with audio preservation
    vidscribe transcribe "/path/video.mp4" --keep-audio
    
    # JSON output with full metadata
    vidscribe transcribe "VIDEO_URL" -o data.json -f json
    
    \b
    🔧 MODEL SIZES:
    • tiny: 32x faster, good for quick drafts
    • base: 16x faster, good balance (default)
    • small: 6x faster, better accuracy
    • medium: 2x faster, high accuracy
    • large: Best accuracy, slower
    
    \b
    🌍 SUPPORTED LANGUAGES:
    Supports 99+ languages including: English (en), Spanish (es), 
    French (fr), German (de), Italian (it), Portuguese (pt), 
    Russian (ru), Japanese (ja), Chinese (zh), Korean (ko), etc.
    """
    logger = logging.getLogger(__name__)

    with console.status("[bold green]Initializing...") as status:
        # Initialize transcription engine
        engine = TranscriptionEngine(model_size=model, use_mlx=use_mlx)

        # Check if input is a YouTube URL
        if is_youtube_url(input):
            status.update("[bold yellow]Downloading from YouTube...")
            downloader = YouTubeDownloader(
                keep_files=keep_audio,
                cookies_from_browser=cookies_from_browser,
                cookies_file=cookies_file,
            )

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
    "--use-mlx/--no-mlx",
    default=False,
    help="Use MLX acceleration on Apple Silicon (disabled by default)"
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
@click.option(
    "--since",
    type=str,
    default=None,
    help="Only process videos uploaded on or after this date (YYYY-MM-DD)"
)
@click.option(
    "--cookies-from-browser",
    type=str,
    default=None,
    help="Browser to pull cookies from to bypass bot detection (e.g. chrome, firefox, safari)"
)
@click.option(
    "--cookies-file",
    type=click.Path(exists=True),
    default=None,
    help="Path to a Netscape-format cookies file"
)
@click.pass_context
def playlist(
    ctx: click.Context,
    url: str,
    output: str,
    model: str,
    use_mlx: Optional[bool],
    limit: Optional[int],
    keep_audio: bool,
    since: Optional[str],
    cookies_from_browser: Optional[str],
    cookies_file: Optional[str],
) -> None:
    """
    \b
    📃 Transcribe all videos from a YouTube playlist or channel.
    
    Efficiently processes multiple videos with progress tracking and
    automatic resumption. Results saved to CSV format by default.
    
    \b
    📋 EXAMPLES:
    
    # Process entire playlist
    vidscribe playlist "https://youtube.com/playlist?list=PLxxxxxx"
    
    # Custom output file and model
    vidscribe playlist "PLAYLIST_URL" -o results.csv -m medium
    
    # Process channel with video limit
    vidscribe playlist "https://youtube.com/@channel" --limit 10
    
    # Keep all downloaded audio files
    vidscribe playlist "PLAYLIST_URL" --keep-audio
    
    # Use MLX acceleration for faster processing
    vidscribe playlist "PLAYLIST_URL" --use-mlx -m small
    
    \b
    🎯 SUPPORTED URL TYPES:
    • Playlist URLs: /playlist?list=PLxxxxxx
    • Channel URLs: /@channelname or /channel/UCxxxxxx
    • User URLs: /user/username
    
    \b
    📊 OUTPUT FORMAT:
    CSV file with columns: Title, URL, Duration, Transcription, Error
    Each row contains one video's complete transcription data.
    
    \b
    ⚡ PERFORMANCE TIPS:
    • Use 'tiny' or 'base' models for faster batch processing
    • Enable MLX acceleration on Apple Silicon (--use-mlx)
    • Use --limit for testing on large channels
    """
    logger = logging.getLogger(__name__)

    try:
        validate_youtube_url(url)
    except ValueError as e:
        console.print(f"[red]Invalid URL: {e}[/red]")
        sys.exit(1)

    since_date = None
    if since:
        try:
            since_date = datetime.strptime(since, "%Y-%m-%d").strftime("%Y%m%d")
        except ValueError:
            console.print("[red]Invalid --since date format. Use YYYY-MM-DD (e.g. 2024-01-01)[/red]")
            sys.exit(1)

    # Initialize processor
    processor = PlaylistProcessor(
        model_size=model,
        keep_audio=keep_audio,
        use_mlx=use_mlx,
        cookies_from_browser=cookies_from_browser,
        cookies_file=cookies_file,
    )

    # Determine if it's a playlist or channel
    if "playlist" in url or "list=" in url:
        console.print(f"[cyan]Processing playlist...[/cyan]")
        processor.process_playlist(url, output)
    else:
        console.print(f"[cyan]Processing channel...[/cyan]")
        if since_date:
            console.print(f"[cyan]Filtering videos since {since}...[/cyan]")
        processor.process_channel(url, output, limit=limit, since_date=since_date)

    console.print(f"[green]✓[/green] Transcriptions saved to: {output}")


@cli.command()
@click.argument("url", type=str)
def info(url: str) -> None:
    """
    \b
    ℹ️ Get detailed information about a YouTube video.
    
    Retrieves metadata without downloading or transcribing.
    Useful for checking video details before processing.
    
    \b
    📋 EXAMPLES:
    
    # Get video information
    vidscribe info "https://youtu.be/dQw4w9WgXcQ"
    
    # Check video details before transcription
    vidscribe info "https://youtube.com/watch?v=VIDEO_ID"
    
    \b
    📊 DISPLAYED INFORMATION:
    • Title: Video title
    • Author: Channel name
    • Duration: Video length in seconds
    • Views: View count
    • Video ID: YouTube video identifier
    • URL: Full YouTube URL
    
    \b
    💡 USE CASES:
    • Verify video accessibility before transcription
    • Check video duration for processing time estimates
    • Confirm correct video before batch processing
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
    """
    \b
    🤖 List all available Whisper models with detailed specifications.
    
    Shows model sizes, performance characteristics, and memory requirements
    to help choose the best model for your needs.
    
    \b
    📋 EXAMPLES:
    
    # Show all available models
    vidscribe models
    
    \b
    🎯 MODEL SELECTION GUIDE:
    • tiny: Quick drafts, testing, low-resource environments
    • base: General use, good balance of speed/accuracy (recommended)
    • small: Better accuracy when you have more time/resources
    • medium: High accuracy for important transcriptions
    • large: Maximum accuracy for critical/professional use
    
    \b
    ⚡ PERFORMANCE NOTES:
    • Speed is relative to 'large' model baseline
    • VRAM requirements are approximate
    • MLX acceleration (Apple Silicon) reduces memory usage
    • First run downloads models (one-time ~140MB-1.5GB per model)
    """
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