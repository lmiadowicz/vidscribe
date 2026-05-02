# Vidscribe

A CLI tool for transcribing YouTube videos, playlists, channels, and local video files using OpenAI's Whisper model, with MLX acceleration for Apple Silicon.

## Features

- **Multiple Input Sources**: YouTube URLs, local video files, playlists, and channels
- **High-Quality Transcription**: Powered by OpenAI Whisper
- **Multiple Output Formats**: Text, JSON, CSV, SRT subtitles, and WebVTT
- **Apple Silicon Acceleration**: MLX Whisper support for ~50% faster transcription on M1/M2/M3
- **Date Filtering**: `--since` flag to only process videos uploaded after a given date
- **Resume Support**: Re-running a playlist/channel skips already-processed videos
- **Cookie Auth**: Bypass bot detection via browser cookies or a Netscape cookies file
- **Batch Scripts**: Pre-built scripts for transcribing curated channel lists

## Installation

```bash
git clone https://github.com/lmiadowicz/vidscribe.git
cd vidscribe
pip install -e .
```

### Apple Silicon (optional — ~50% faster)

```bash
pip install -r requirements-mac.txt
```

MLX models require a Hugging Face token. Create `.env` from the example and add yours:

```bash
cp .env.example .env
# Edit .env: HF_TOKEN=your_token_here
```

Get a token at https://huggingface.co/settings/tokens.

### Prerequisites

- **Python 3.8+**
- **FFmpeg**:
  ```bash
  brew install ffmpeg          # macOS
  sudo apt install ffmpeg      # Ubuntu/Debian
  choco install ffmpeg         # Windows
  ```

## Usage

### Single video

```bash
# Transcribe a YouTube video
vidscribe transcribe "https://www.youtube.com/watch?v=VIDEO_ID"

# Save to file with specific format
vidscribe transcribe "VIDEO_URL" -o transcript.txt -f text

# Generate SRT subtitles
vidscribe transcribe "VIDEO_URL" -o subs.srt -f srt

# Use a larger model for better accuracy
vidscribe transcribe "VIDEO_URL" -m large

# Enable MLX acceleration (Apple Silicon)
vidscribe transcribe "VIDEO_URL" --use-mlx

# Transcribe in a specific language
vidscribe transcribe "VIDEO_URL" --language es

# Translate any language to English
vidscribe transcribe "VIDEO_URL" --task translate

# Keep downloaded audio file
vidscribe transcribe "VIDEO_URL" --keep-audio

# Bypass bot detection using browser cookies
vidscribe transcribe "VIDEO_URL" --cookies-from-browser chrome
vidscribe transcribe "VIDEO_URL" --cookies-file /path/to/cookies.txt
```

### Playlist / channel

```bash
# Process entire playlist
vidscribe playlist "https://youtube.com/playlist?list=PLxxxxxx"

# Process a channel, save to CSV
vidscribe playlist "https://youtube.com/@channel" -o results.csv

# Only process videos uploaded on or after a date
vidscribe playlist "https://youtube.com/@channel" --since 2024-01-01

# Limit number of videos processed
vidscribe playlist "https://youtube.com/@channel" --limit 10

# Use MLX acceleration and medium model
vidscribe playlist "PLAYLIST_URL" --use-mlx -m medium

# Bypass bot detection
vidscribe playlist "PLAYLIST_URL" --cookies-from-browser chrome
```

Re-running any `playlist` command automatically skips videos already present in the output CSV.

### Other commands

```bash
# Get video metadata without transcribing
vidscribe info "https://www.youtube.com/watch?v=VIDEO_ID"

# List available Whisper models
vidscribe models
```

## Batch scripts

`scripts/transcribe_growth_channels.sh` transcribes a curated list of mobile growth / app founder YouTube channels:

```bash
# Run with defaults (base model, videos since 2024-04-30)
bash scripts/transcribe_growth_channels.sh

# Override model and date
MODEL=small SINCE=2023-01-01 bash scripts/transcribe_growth_channels.sh

# Enable MLX acceleration
USE_MLX=1 bash scripts/transcribe_growth_channels.sh
```

Output CSVs are written to `scripts/channel_transcriptions/`. Already-covered channels are skipped automatically on re-runs.

## Configuration

### Environment variables (`.env`)

```bash
HF_TOKEN=your_huggingface_token_here   # required for MLX
VIDSCRIBE_MODEL_SIZE=base
VIDSCRIBE_OUTPUT_FORMAT=text
VIDSCRIBE_USE_MLX=true
```

### YAML config (`~/.vidscribe/config.yaml`)

```yaml
model:
  size: base

download:
  output_dir: ~/Downloads/vidscribe
  keep_files: false

output:
  format: text
  language: auto
```

## Project structure

```
vidscribe/
├── src/vidscribe/
│   ├── core/engine.py          # Whisper / MLX transcription engine
│   ├── downloaders/youtube.py  # yt-dlp based downloader
│   ├── processors/playlist.py  # Batch playlist / channel processor
│   ├── utils/                  # Config, formatters, validators
│   └── cli.py                  # Click CLI entry point
├── scripts/
│   ├── install.sh
│   └── transcribe_growth_channels.sh
└── tests/
```

## Models

| Model  | Parameters | Multilingual | Required VRAM | Relative Speed |
|--------|------------|--------------|---------------|----------------|
| tiny   | 39M        | ✓            | ~1 GB         | ~32x           |
| base   | 74M        | ✓            | ~1 GB         | ~16x           |
| small  | 244M       | ✓            | ~2 GB         | ~6x            |
| medium | 769M       | ✓            | ~5 GB         | ~2x            |
| large  | 1550M      | ✓            | ~10 GB        | 1x             |

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

make test        # run unit tests
make test-cov    # tests with coverage
make lint        # flake8 + mypy
make format      # black + isort
```

## Troubleshooting

**FFmpeg not found**
```bash
ffmpeg -version   # verify install
brew install ffmpeg
```

**YouTube download errors**
- Check your internet connection
- Try passing cookies: `--cookies-from-browser chrome`
- Some videos may be age-restricted or private
- Update yt-dlp: `pip install --upgrade yt-dlp`

**MLX authentication errors (Apple Silicon)**
```bash
# Error: 401 Client Error / Repository Not Found
cp .env.example .env
# Edit .env and add: HF_TOKEN=your_token_here
```

**Out of memory**
- Use a smaller model (`-m tiny` or `-m base`)
- Process videos individually instead of in batches

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) — speech recognition model
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube downloading
- [MLX Whisper](https://github.com/ml-explore/mlx-examples) — Apple Silicon acceleration
- [Click](https://click.palletsprojects.com/) — CLI framework
- [Rich](https://rich.readthedocs.io/) — terminal output
