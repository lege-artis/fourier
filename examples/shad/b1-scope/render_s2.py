#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Render Chapter B0 Slot S2 figures + head-data fixtures from the three
audio captures fetched by fetch_audio_s2.sh.

Each audio file is treated as a real "voltage vs time" trace (the
microphone is the probe; the ADC is the scope sampler). The same
five-step pipeline that fed S1 is applied to each:

  1. Aggregate  load the OGG, lift fs and N
  2. Parse       show first 10 samples as text
  3. Transform   np.fft.fft + slice to one-sided
  4. Read        show first 10 spectrum bins as text
  5. Plot        save time + spectrum + takeaway figures

Outputs (docs/shad/figures/):
  fig-s2a-input.png    fig-s2a-spectrum.png    fig-s2a-takeaway.png
  fig-s2b-input.png    fig-s2b-spectrum.png    fig-s2b-takeaway.png
  fig-s2c-input.png    fig-s2c-spectrum.png    fig-s2c-takeaway.png

Outputs (examples/shad/b1-scope/data/):
  s2a_head.txt   s2b_head.txt   s2c_head.txt
    one literal listing per slot, ready to paste into the TeX listing.

Requires:
  pip install scipy numpy matplotlib soundfile pooch
  (soundfile is the OGG/Vorbis decoder; libsndfile must be on the system)

If soundfile is missing, the script falls back to ffmpeg subprocess
decoding into a temporary WAV file. Either path works.

Run:
    ./fetch_audio_s2.sh        # one-time
    python render_s2.py
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

import matplotlib.pyplot as plt
import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
DATA = HERE / "data"
FIGDIR = REPO / "docs" / "shad" / "figures"

SLOTS = [
    ("s2a", "s2a_sine440.ogg",
     "S2a -- Wikimedia Commons Sine_wave_440.ogg",
     "pure 440 Hz tone (reference, single-peak sanity check)"),
    ("s2b", "s2b_tone440.ogg",
     "S2b -- Wikimedia Commons Tone_440Hz.ogg",
     "alternative 440 Hz tone (different encoder / upload path)"),
    ("s2c", "s2c_example.ogg",
     "S2c -- Wikimedia Commons Example.ogg",
     "example speech sample (broadband content)"),
    ("s4", "s4_guitar_e2.ogg",
     "S4 -- Wikimedia Commons Guitar_string_E2.ogg",
     "single guitar string pluck E2, fundamental ~82 Hz + harmonic stack"),
]


def load_audio(path: pathlib.Path):
    """Return (samples, fs) for an audio file. samples is mono float64."""
    try:
        import soundfile as sf
        samples, fs = sf.read(str(path), dtype="float64")
    except ImportError:
        # ffmpeg fallback
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-i", str(path), "-ac", "1", "-acodec", "pcm_s16le", wav_path],
            check=True)
        from scipy.io import wavfile
        fs, samples = wavfile.read(wav_path)
        samples = samples.astype("float64") / 32768.0
    # mono
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    return samples, float(fs)


def render_slot(slot_id, filename, title, blurb):
    audio_path = DATA / filename
    if not audio_path.exists():
        print(f"[skip] {slot_id}: {audio_path} missing. "
              f"Run ./fetch_audio_s2.sh first.")
        return None

    samples, fs = load_audio(audio_path)
    N = samples.size

    # spectrum
    spec = np.fft.fft(samples) / N
    freq = np.fft.fftfreq(N, d=1.0 / fs)
    half = N // 2
    f_pos = freq[:half]
    mag = np.abs(spec[:half])

    # head text fixture
    head_lines = []
    head_lines.append(f"# {title}")
    head_lines.append(f"# {blurb}")
    head_lines.append(f"# fs = {fs:.1f} Hz, N = {N} samples, duration = {N/fs:.3f} s")
    head_lines.append("")
    head_lines.append("--- first 10 raw samples ---")
    for i in range(10):
        head_lines.append(f"[{i:>3}] t = {i/fs:.6f} s   v = {samples[i]:+.6f} (normalised)")
    head_lines.append("")
    head_lines.append("--- first 10 spectrum bins ---")
    for k in range(10):
        head_lines.append(f"[{k:>3}] f = {freq[k]:>10.4f} Hz   |X|/N = {abs(spec[k]):.6e}")
    head_lines.append("")
    # find dominant peak
    peak_idx = int(np.argmax(mag))
    head_lines.append(f"dominant peak: f = {f_pos[peak_idx]:.2f} Hz, |X|/N = {mag[peak_idx]:.4e}")
    (DATA / f"{slot_id}_head.txt").write_text("\n".join(head_lines))

    # input figure: first 50 ms or all if shorter
    show_n = min(int(0.05 * fs), N)
    t = np.arange(show_n) / fs
    fig, ax = plt.subplots(figsize=(8, 3.0))
    ax.plot(t * 1000.0, samples[:show_n], linewidth=0.7, color="#1f4e79")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("amplitude (normalised)")
    ax.set_title(f"{title} -- first {show_n} samples @ {fs:.0f} Hz")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGDIR / f"fig-{slot_id}-input.png", dpi=120)
    plt.close(fig)

    # spectrum 0..2 kHz zoom
    fig, ax = plt.subplots(figsize=(8, 3.0))
    mask = f_pos <= 2000.0
    ax.plot(f_pos[mask], mag[mask], linewidth=0.8, color="#702020")
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("|X[k]| / N")
    ax.set_title(f"{title} -- spectrum 0..2 kHz")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGDIR / f"fig-{slot_id}-spectrum.png", dpi=120)
    plt.close(fig)

    # takeaway: full spectrum, log scale, dominant peak annotated
    fig, ax = plt.subplots(figsize=(8, 3.0))
    ax.semilogy(f_pos, mag + 1e-15, linewidth=0.7, color="#1f4e79")
    ax.axvline(f_pos[peak_idx], color="#a02020", linestyle="--", linewidth=0.7, alpha=0.7)
    ax.annotate(f"peak {f_pos[peak_idx]:.1f} Hz\n|X|/N = {mag[peak_idx]:.2e}",
                xy=(f_pos[peak_idx], mag[peak_idx]),
                xytext=(f_pos[peak_idx] * 1.5 + 100, mag[peak_idx] * 0.3),
                fontsize=9, color="#a02020",
                arrowprops=dict(arrowstyle="->", color="#a02020", linewidth=0.7))
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("|X[k]| / N (log)")
    ax.set_title(f"{title} -- full spectrum, dominant peak labelled")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(FIGDIR / f"fig-{slot_id}-takeaway.png", dpi=120)
    plt.close(fig)

    print(f"[{slot_id}] rendered. fs={fs:.0f} Hz, N={N}, "
          f"peak {f_pos[peak_idx]:.1f} Hz, head -> {DATA/(slot_id+'_head.txt')}")
    return f_pos[peak_idx]


def main() -> int:
    FIGDIR.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    rendered = []
    for slot_id, filename, title, blurb in SLOTS:
        peak = render_slot(slot_id, filename, title, blurb)
        if peak is not None:
            rendered.append((slot_id, peak))
    if not rendered:
        print("\nNo audio files found. Run ./fetch_audio_s2.sh first.",
              file=sys.stderr)
        return 1
    print(f"\nRendered {len(rendered)} slot(s).")
    print(f"  figure dir: {FIGDIR}")
    print(f"  data dir:   {DATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
