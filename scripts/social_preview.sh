#!/usr/bin/env sh
# Make a 1280x640 social preview image (GitHub's recommended size) from a
# GIF, video or screenshot. The source is scaled to fit and padded, never
# cropped, so nothing important gets cut off.
#
# Usage: sh scripts/social_preview.sh SOURCE [OUTPUT.png] [SECONDS] [PAD_COLOR]
#   SECONDS    for GIFs and videos, which moment to grab (default 0.6 of the length)
#   PAD_COLOR  background for the padding (default 1e1e2e, a dark terminal colour)
set -eu

src=${1:?usage: social_preview.sh SOURCE [OUTPUT.png] [SECONDS] [PAD_COLOR]}
out=${2:-docs/social-preview.png}
at=${3:-}
pad=${4:-1e1e2e}

command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg is required (brew install ffmpeg / apt install ffmpeg)" >&2; exit 1; }
[ -f "$src" ] || { echo "No such file: $src" >&2; exit 1; }

if [ -z "$at" ]; then
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$src" 2>/dev/null || true)
  case "$dur" in
    ''|N/A) at=0 ;;
    *) at=$(awk "BEGIN { printf \"%.2f\", $dur * 0.6 }") ;;
  esac
fi

mkdir -p "$(dirname "$out")"
ffmpeg -v error -y -ss "$at" -i "$src" -frames:v 1 \
  -vf "scale=1200:560:force_original_aspect_ratio=decrease,pad=1280:640:(ow-iw)/2:(oh-ih)/2:color=0x$pad" \
  "$out"

size=$(ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x "$out")
echo "Wrote $out ($size) from $src at ${at}s"
echo "Upload it in the repo's Settings > General > Social preview."
