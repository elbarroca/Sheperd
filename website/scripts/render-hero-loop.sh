#!/usr/bin/env bash
# Rebuild the 20-second atmospheric loop from the original artwork and generated fog plate.
set -euo pipefail
cd "$(dirname "$0")/.."

# Match the mobile 29% focal position while avoiding a full panorama decode.
ffmpeg -hide_banner -loglevel error -y -i public/media/recovery-terminal.png \
  -vf 'crop=820:820:318:0' -frames:v 1 public/media/recovery-terminal-mobile.png

# Periodic translation and light variation join continuously at the loop boundary.
# The terminal geometry remains fixed; only the ground atmosphere changes.
ffmpeg -hide_banner -loglevel warning -y \
  -loop 1 -framerate 24 -i public/media/recovery-terminal.png \
  -loop 1 -framerate 24 -i design-experiments/assets/recovery-ground-fog.png \
  -filter_complex "[0:v]scale=1600:684,setsar=1,format=gbrp[scene];[1:v]scale=1920:640,pad=1920:854:0:170:black,crop=1600:684:x='160+90*sin(2*PI*t/20)':y=0,setsar=1,format=gbrp[fog];[scene][fog]blend=all_expr='min(255,A+B*(0.28+0.08*sin(2*PI*T/20)))',format=yuv420p[out]" \
  -map '[out]' -t 20 -an -c:v libx264 -preset slow -crf 23 -g 480 \
  -movflags +faststart public/media/recovery-terminal-loop.mp4

ffmpeg -hide_banner -loglevel warning -y \
  -i public/media/recovery-terminal-loop.mp4 -an \
  -c:v libvpx-vp9 -b:v 0 -crf 31 -g 480 -row-mt 1 \
  public/media/recovery-terminal-loop.webm

# A portable GIF export, deliberately separate from the website's smaller video delivery.
ffmpeg -hide_banner -loglevel warning -y \
  -i public/media/recovery-terminal-loop.mp4 \
  -filter_complex '[0:v]fps=12,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=192:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle' \
  -loop 0 public/media/recovery-terminal-loop.gif
