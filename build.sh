#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

echo "Force-reinstalling Redis 7.4.0..."
pip install --upgrade --force-reinstall redis==7.4.0

echo "Downloading FFmpeg..."
mkdir -p ffmpeg_bin
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ --strip-components=1 -C ffmpeg_bin

chmod +x ffmpeg_bin/ffmpeg ffmpeg_bin/ffprobe
