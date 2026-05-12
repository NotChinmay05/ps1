#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Download FFmpeg static binary
echo "Downloading FFmpeg..."
mkdir -p bin
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ --strip-components=1 -C bin

# Ensure the bin directory is executable
chmod +x bin/ffmpeg bin/ffprobe
