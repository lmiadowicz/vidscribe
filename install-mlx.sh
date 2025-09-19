#!/bin/bash

# MLX Installation Script for Apple Silicon Macs
# This script installs MLX support for faster Whisper transcription

echo "==================================="
echo "Vidscribe MLX Installer"
echo "==================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is only for macOS systems."
    echo "MLX is specifically designed for Apple Silicon."
    exit 1
fi

# Check if running on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "⚠️  Warning: You appear to be running on Intel Mac."
    echo "MLX is optimized for Apple Silicon (M1/M2/M3) chips."
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Installing MLX support for Whisper..."

# Install mlx-whisper
pip install mlx-whisper

if [ $? -eq 0 ]; then
    echo "✅ MLX Whisper installed successfully!"
    echo ""
    echo "Usage:"
    echo "  vidscribe transcribe VIDEO_URL           # Auto-detect MLX"
    echo "  vidscribe transcribe VIDEO_URL --use-mlx # Force MLX"
    echo "  vidscribe transcribe VIDEO_URL --no-mlx  # Disable MLX"
    echo ""
    echo "MLX will provide ~50% speed improvement for transcription."
else
    echo "❌ Failed to install MLX Whisper."
    echo "Please try: pip install mlx-whisper"
    exit 1
fi