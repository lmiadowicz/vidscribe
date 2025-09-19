# Vidscribe

[![CI](https://github.com/yourusername/vidscribe/workflows/CI/badge.svg)](https://github.com/yourusername/vidscribe/actions)
[![codecov](https://codecov.io/gh/yourusername/vidscribe/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/vidscribe)
[![PyPI version](https://badge.fury.io/py/vidscribe.svg)](https://badge.fury.io/py/vidscribe)
[![Python versions](https://img.shields.io/pypi/pyversions/vidscribe.svg)](https://pypi.org/project/vidscribe/)

A powerful, professional-grade CLI tool for transcribing YouTube videos and local video files using OpenAI's Whisper model. Built with modern Python best practices and designed for both individual use and integration into larger workflows.

## ✨ Features

- **🎬 Multiple Input Sources**: Support for YouTube URLs, local video files, playlists, and channels
- **🎯 High-Quality Transcription**: Powered by OpenAI's state-of-the-art Whisper model
- **📊 Multiple Output Formats**: Text, JSON, CSV, SRT subtitles, and WebVTT
- **⚡ Efficient Processing**: Optimized batch processing with MLX support for Apple Silicon
- **🔧 Configurable**: Flexible configuration system with environment variable support
- **🎨 Beautiful CLI**: Rich terminal interface with progress bars and colored output
- **🧪 Well-Tested**: Comprehensive test suite with high code coverage
- **📦 Professional Structure**: Modern Python packaging with proper dependency management

## 🚀 Quick Start

### Installation

```bash
# Using pip with requirements.txt
pip install -r requirements.txt

# (Optional) For Apple Silicon Mac users - 50% faster transcription
pip install -r requirements-mac.txt

# Or install as a package with all dependencies
pip install -e .

# For development (includes testing and linting tools)
pip install -r requirements-dev.txt

# From PyPI (when published)
pip install vidscribe

# From source (development)
git clone https://github.com/yourusername/vidscribe.git
cd vidscribe
pip install -e ".[dev]"
```

### Prerequisites

1. **Python 3.8+** is required

2. **FFmpeg** is required for audio/video processing:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (using chocolatey)
choco install ffmpeg
```

3. **OpenAI Whisper** will be automatically installed with dependencies. The package includes:
   - OpenAI Whisper (installed from GitHub)
   - PyTorch (for running the model)
   - All necessary audio processing libraries
   - (Optional) MLX support for Apple Silicon acceleration

**Note**: First run will download the Whisper model (~140MB for base model) which is a one-time setup.

**Apple Silicon Optimization**: MLX acceleration provides ~50% speed improvement on M1/M2/M3 Macs and is automatically detected when installed.

### MLX Setup for Apple Silicon

For optimal performance on Apple Silicon Macs, install MLX Whisper:

```bash
# Install MLX Whisper for Apple Silicon acceleration
pip install mlx-whisper

# Or use the Mac-specific requirements
pip install -r requirements-mac.txt
```

**Important**: MLX models require Hugging Face authentication. Set up your environment:

1. **Get a Hugging Face token**: Visit [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```
3. **Edit `.env` and add your token**:
   ```bash
   HF_TOKEN=your_actual_token_here
   ```

Without authentication, you'll get 401 errors when using MLX models.

### Basic Usage

```bash
# Transcribe a YouTube video
vidscribe transcribe "https://www.youtube.com/watch?v=VIDEO_ID"

# Use MLX acceleration on Apple Silicon (auto-detected)
vidscribe transcribe "VIDEO_URL" --use-mlx

# Transcribe a local video file
vidscribe transcribe "/path/to/video.mp4"

# Process a YouTube playlist
vidscribe playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Get video information
vidscribe info "https://www.youtube.com/watch?v=VIDEO_ID"

# List available models
vidscribe models
```

### Dumping Video to File

To download and save videos locally (with optional transcription), you can use the following approaches:

```bash
# Download YouTube video and keep the audio file
vidscribe transcribe "https://www.youtube.com/watch?v=VIDEO_ID" --keep-audio -o output.txt

# Process local video and extract audio
vidscribe transcribe "/path/to/video.mp4" --keep-audio -o transcript.txt

# Download playlist videos and keep all audio files
vidscribe playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID" --keep-audio

# Save transcription in different formats
vidscribe transcribe "VIDEO_URL" -o output.json -f json  # JSON format
vidscribe transcribe "VIDEO_URL" -o output.csv -f csv    # CSV format
vidscribe transcribe "VIDEO_URL" -o output.srt -f srt    # Subtitle format
vidscribe transcribe "VIDEO_URL" -o output.vtt -f vtt    # WebVTT format
```

When using `--keep-audio`, the tool will:
- For YouTube videos: Download and save the audio file in the current directory
- For local videos: Extract and save the audio as an MP3 file
- The audio files are preserved after transcription completes

## 📖 Detailed Usage

### Apple Silicon Acceleration

On Apple Silicon Macs, vidscribe automatically uses MLX for faster transcription when available:

```bash
# Auto-detect and use MLX if available (default)
vidscribe transcribe "VIDEO_URL"

# Force MLX usage
vidscribe transcribe "VIDEO_URL" --use-mlx

# Disable MLX (use standard Whisper)
vidscribe transcribe "VIDEO_URL" --no-mlx

# Check backend in verbose mode
vidscribe transcribe "VIDEO_URL" -v  # Shows "MLX" or "Whisper" backend
```

### Single Video Transcription

```bash
# Basic transcription
vidscribe transcribe "https://www.youtube.com/watch?v=VIDEO_ID"

# Save to file with specific format
vidscribe transcribe "VIDEO_URL" -o transcription.txt -f text

# Use a larger model for better accuracy
vidscribe transcribe "VIDEO_URL" -m large

# Generate subtitles
vidscribe transcribe "VIDEO_URL" -o subtitles.srt -f srt

# Transcribe in a specific language
vidscribe transcribe "VIDEO_URL" --language es

# Translate to English
vidscribe transcribe "VIDEO_URL" --task translate
```

### Batch Processing

```bash
# Process entire playlist
vidscribe playlist "PLAYLIST_URL" -o results.csv

# Process channel with video limit
vidscribe playlist "CHANNEL_URL" --limit 10

# Use different model for batch processing
vidscribe playlist "PLAYLIST_URL" -m small --keep-audio
```

### Configuration

Vidscribe supports multiple configuration methods:

#### Environment Variables (.env file)

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Required for MLX on Apple Silicon
HF_TOKEN=your_huggingface_token_here

# Optional configuration overrides
VIDSCRIBE_MODEL_SIZE=base
VIDSCRIBE_OUTPUT_FORMAT=text
VIDSCRIBE_USE_MLX=true
```

#### YAML Configuration File

Create a config file at `~/.vidscribe/config.yaml`:

```yaml
model:
  size: base
  device: cuda  # or cpu

download:
  output_dir: ~/Downloads/vidscribe
  keep_files: false

output:
  format: text
  language: auto

logging:
  level: INFO
```

#### Command Line Environment Variables

```bash
export VIDSCRIBE_MODEL_SIZE=large
export VIDSCRIBE_OUTPUT_FORMAT=json
export HF_TOKEN=your_token_here
vidscribe transcribe "VIDEO_URL"
```

## 🏗️ Architecture

### Project Structure

```
vidscribe/
├── src/vidscribe/
│   ├── core/               # Core transcription engine
│   │   └── engine.py
│   ├── downloaders/        # Video download modules
│   │   └── youtube.py
│   ├── processors/         # Batch processing modules
│   │   └── playlist.py
│   ├── utils/              # Utility modules
│   │   ├── config.py
│   │   ├── formatters.py
│   │   └── validators.py
│   └── cli.py              # Command-line interface
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test fixtures
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── config/                 # Default configurations
```

### Key Components

- **TranscriptionEngine**: Core Whisper/MLX integration with automatic backend selection
- **YouTubeDownloader**: Robust YouTube video downloading with fallbacks  
- **PlaylistProcessor**: Efficient batch processing with progress tracking
- **CLI**: Rich command-line interface built with Click
- **Config System**: Flexible configuration with multiple sources

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/vidscribe.git
cd vidscribe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
make install-dev

# Run tests
make test

# Run with coverage
make test-cov

# Format code
make format

# Lint code
make lint
```

### Available Make Commands

```bash
make help           # Show all available commands
make install        # Install package
make install-dev    # Install with development dependencies
make test           # Run unit tests
make test-cov       # Run tests with coverage
make lint           # Run linters (flake8, mypy)
make format         # Format code (black, isort)
make clean          # Remove build artifacts
make build          # Build distribution packages
make docs           # Generate documentation
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/unit/test_validators.py

# Run with coverage
pytest --cov=vidscribe --cov-report=html

# Run integration tests (requires network)
pytest tests/integration/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`make test`)
6. Format code (`make format`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📊 Model Information

| Model  | Parameters | English-only | Multilingual | Required VRAM | Relative Speed |
|--------|------------|--------------|--------------|---------------|----------------|
| tiny   | 39M        | ✓            | ✓            | ~1 GB         | ~32x           |
| base   | 74M        | ✓            | ✓            | ~1 GB         | ~16x           |
| small  | 244M       | ✓            | ✓            | ~2 GB         | ~6x            |
| medium | 769M       | ✓            | ✓            | ~5 GB         | ~2x            |
| large  | 1550M      | -            | ✓            | ~10 GB        | 1x             |

## 🐛 Troubleshooting

### Common Issues

**FFmpeg not found**
```bash
# Test FFmpeg installation
ffmpeg -version

# Install FFmpeg using package manager
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

**Out of memory errors**
- Use a smaller model (`-m tiny` or `-m base`)
- Process videos individually instead of in batches
- Ensure sufficient RAM/VRAM for chosen model

**YouTube download errors**
- Check internet connection
- Update pytube: `pip install --upgrade pytube`
- Some videos may be age-restricted or private

**MLX Authentication errors (Apple Silicon)**
```bash
# Error: 401 Client Error / Repository Not Found
# Solution: Set up Hugging Face authentication
cp .env.example .env
# Edit .env and add: HF_TOKEN=your_token_here
# Get token from: https://huggingface.co/settings/tokens
```

**Slow transcription**
- Use smaller model for faster processing
- Consider GPU acceleration (install CUDA-enabled PyTorch)
- First run downloads models (one-time delay)

### Performance Tips

1. **Model Selection**: Start with `base` for good speed/accuracy balance
2. **GPU Acceleration**: Install CUDA-enabled PyTorch for GPU processing
3. **Batch Processing**: Process multiple videos in one session to reuse loaded models
4. **Storage**: Ensure sufficient disk space for temporary audio files

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - State-of-the-art speech recognition
- [pytube](https://github.com/pytube/pytube) - YouTube video downloading
- [Click](https://click.palletsprojects.com/) - Command-line interface framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output

## 📬 Support

- **Documentation**: [Link to docs]
- **Issues**: [GitHub Issues](https://github.com/yourusername/vidscribe/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/vidscribe/discussions)

---

**Made with ❤️ by the Vidscribe team**