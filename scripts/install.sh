#!/bin/bash
# Installation script for Vidscribe

set -e

echo "🎬 Installing Vidscribe..."

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python $python_version detected"
else
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

# Check for FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg detected"
else
    echo "⚠️  FFmpeg not found. Please install FFmpeg:"
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt install ffmpeg"
    echo "   Windows: choco install ffmpeg"
    read -p "Continue without FFmpeg? (y/N): " continue_install
    if [[ ! $continue_install =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Vidscribe from source
echo "📦 Installing Vidscribe..."
pip install -e .

echo "🎉 Installation complete!"
echo ""
echo "Quick start:"
echo "  vidscribe transcribe 'https://www.youtube.com/watch?v=VIDEO_ID'"
echo "  vidscribe --help"
echo ""
echo "For more information, visit: https://github.com/lmiadowicz/vidscribe"