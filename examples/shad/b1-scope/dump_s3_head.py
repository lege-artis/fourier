#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Print the literal first-10 samples and first-10 spectrum bins of the
MIT-BIH ECG record 100, for embedding into Chapter B0 Slot S3 listings.

Run on a machine with network access (scipy fetches ecg.dat on first
call). Output is plain text, paste into the .tex listing as-is.

Run:
    python dump_s3_head.py
"""
from __future__ import annotations

import numpy as np


def main() -> int:
    try:
        from scipy.datasets import electrocardiogram
    except ImportError as e:
        raise SystemExit(
            "scipy not installed. Install with:\n"
            "    pip install scipy pooch"
        ) from e

    ecg = electrocardiogram()
    fs = 360.0
    N = ecg.size
    print(f"--- first 10 raw samples ---")
    for i in range(10):
        t = i / fs
        print(f"[{i:>3}] t = {t:.4f} s   v = {ecg[i]:+.4f} mV")

    spec = np.fft.fft(ecg) / N
    freq = np.fft.fftfreq(N, d=1.0 / fs)
    half = N // 2
    print(f"\n--- first 10 spectrum bins ---")
    for k in range(10):
        f = freq[k]
        mag = abs(spec[k])
        print(f"[{k:>3}] f = {f:>7.4f} Hz   |X|/N = {mag:.6f} mV")

    print(f"\n--- summary ---")
    print(f"N = {N}, fs = {fs} Hz, duration = {N/fs:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
