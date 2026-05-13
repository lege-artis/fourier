#!/usr/bin/env bash
# Fetch the three S2 audio captures into the local data cache.
#
# This runs on the reader's machine (the project sandbox proxy blocks
# direct curl). One-time per checkout; the OGG files are then loaded
# by the render_s2*.py scripts and never re-downloaded.
#
# Sources are CC-BY-SA / CC0 / public-domain Wikimedia Commons files.
# See docs/shad/figures/data-attribution.md (and Appendix A of the PDF)
# for the full licence trail.
#
# Usage:
#   ./fetch_audio_s2.sh
#
# Outputs:
#   examples/shad/b1-scope/data/s2a_sine440.ogg
#   examples/shad/b1-scope/data/s2b_tone440.ogg
#   examples/shad/b1-scope/data/s2c_example.ogg
#   examples/shad/b1-scope/data/s4_guitar_e2.ogg   (added v0.2.x-opus-iter)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="$HERE/data"
mkdir -p "$DATA"

fetch() {
  local url="$1"
  local dest="$2"
  if [[ -f "$dest" ]]; then
    echo "[cached]    $(basename "$dest")"
    return
  fi
  echo "[fetching]  $url"
  curl -fSL --max-time 30 -o "$dest" "$url"
}

# S2a: pure 440 Hz sine, sanity-check single-peak spectrum
fetch "https://upload.wikimedia.org/wikipedia/commons/5/50/Sine_wave_440.ogg" \
      "$DATA/s2a_sine440.ogg"

# S2b: alternative 440 Hz tone, different upload / encoder
fetch "https://upload.wikimedia.org/wikipedia/commons/c/ce/Tone_440Hz.ogg" \
      "$DATA/s2b_tone440.ogg"

# S2c: example speech / broadband content, demonstrates DFT is content-agnostic
fetch "https://upload.wikimedia.org/wikipedia/commons/c/c8/Example.ogg" \
      "$DATA/s2c_example.ogg"

# S4: single-string guitar pluck (low E2). Fills the harmonic-stack pedagogy gap.
# Fundamental ~82 Hz + clean integer harmonics at 164, 246, 328, ... Hz.
fetch "https://upload.wikimedia.org/wikipedia/commons/0/0a/Guitar_string_E2.ogg" \
      "$DATA/s4_guitar_e2.ogg"

echo
echo "All audio captures present in:"
echo "  $DATA"
echo
ls -la "$DATA"/s2*.ogg "$DATA"/s4*.ogg 2>/dev/null
