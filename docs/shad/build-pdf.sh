#!/usr/bin/env bash
# Build the Shad-tier PDF from shad-guide.tex
#
# Usage:  ./build-pdf.sh        (assumes you are in docs/shad/)
#
# Behaviour:
#  1. Regenerates figures/dragon-icon.pdf from dragon-icon.svg via cairosvg.
#  2. Runs pdflatex twice to resolve TOC + cross-refs.
#  3. Cleans intermediate artefacts.
#  4. Final PDF lands at docs/shad/shad-guide.pdf
#
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

echo "[1/3] resolve dragon assets"
# Library layout (everything lives in figures/):
#
#   dragon-firstshot.png    <- AI gen attempt #1, preserved verbatim (library)
#   dragon-secondshot.png   <- AI gen attempt #2, preserved verbatim (library)
#   dragon-cover.png        <- active title-page cover (large display)
#   dragon-icon.png         <- active icon (thumbnail / favicon / smaller use)
#   dragon-thumbnail.png    <- derived 128x128 thumbnail of dragon-icon
#   dragon-cover.svg        <- hand-drawn fallback (used only if no PNG)
#   dragon-icon.svg         <- hand-drawn fallback (used only if no PNG)
#
# Role assignment per Pete: first shot = cover, second shot = icon.
# Both originals are kept untouched so future rounds can re-promote.
# If you want to swap roles later, just `cp` the other original onto the
# working name -- nothing in the TeX changes.

# Originals are the canonical source of truth. ALWAYS refresh working
# copies from them so stale derivatives (e.g. left over from a prior
# placeholder SVG) cannot survive across rebuilds.
if [[ -f figures/dragon-firstshot.png ]]; then
    cp -f figures/dragon-firstshot.png  figures/dragon-cover.png
    echo "      refreshed dragon-cover.png from dragon-firstshot.png"
fi
if [[ -f figures/dragon-secondshot.png ]]; then
    cp -f figures/dragon-secondshot.png figures/dragon-icon.png
    echo "      refreshed dragon-icon.png from dragon-secondshot.png"
fi

# Generate a 128x128 thumbnail from dragon-icon.png if possible.
if [[ -f figures/dragon-icon.png ]]; then
  if command -v sips >/dev/null 2>&1; then
    sips -Z 128 figures/dragon-icon.png --out figures/dragon-thumbnail.png >/dev/null 2>&1 \
      && echo "      generated dragon-thumbnail.png (128 px, via sips)"
  else
    python3 - <<'PY' 2>/dev/null && echo "      generated dragon-thumbnail.png (128 px, via Pillow)"
from PIL import Image
img = Image.open('figures/dragon-icon.png')
img.thumbnail((128, 128))
img.save('figures/dragon-thumbnail.png')
PY
  fi
fi

# Priority chain for each working asset: prefer .png (delete stale .pdf so
# pdflatex picks up the PNG); otherwise regenerate .pdf from .svg via cairosvg.
resolve_asset () {
  local base="$1"
  if [[ -f "figures/${base}.png" ]]; then
    echo "      ${base}: using PNG"
    rm -f "figures/${base}.pdf"
  elif [[ -f "figures/${base}.svg" ]]; then
    echo "      ${base}: rendering ${base}.pdf from ${base}.svg via cairosvg"
    python3 -c "import cairosvg; cairosvg.svg2pdf(url='figures/${base}.svg', write_to='figures/${base}.pdf')"
  else
    echo "      ${base}: no source found (expected .png or .svg)"
  fi
}
resolve_asset dragon-cover
resolve_asset dragon-icon

echo "[2/3] pdflatex pass 1"
pdflatex -interaction=nonstopmode -halt-on-error shad-guide.tex > /tmp/shad-guide-pass1.log 2>&1 || {
  tail -40 /tmp/shad-guide-pass1.log
  echo "pdflatex pass 1 failed --- see /tmp/shad-guide-pass1.log" >&2
  exit 1
}

echo "[3/3] pdflatex pass 2 (TOC + cross-refs)"
pdflatex -interaction=nonstopmode -halt-on-error shad-guide.tex > /tmp/shad-guide-pass2.log 2>&1 || {
  tail -40 /tmp/shad-guide-pass2.log
  echo "pdflatex pass 2 failed --- see /tmp/shad-guide-pass2.log" >&2
  exit 1
}

# clean
rm -f shad-guide.aux shad-guide.log shad-guide.out shad-guide.toc

echo
echo "  built  ->  $HERE/shad-guide.pdf"
ls -la shad-guide.pdf
