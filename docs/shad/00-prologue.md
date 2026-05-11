# Just Shad's Guide to Fourier's Galaxy

> *placeholder for the Miyazaki dragon — smoking weed, drinking tea, looking mildly amused*

## What this is

Most Fourier tutorials start with the math. This one starts with **your data**. If you have a CSV with time and voltage, an audio file, a vibration log from a machine that's making a worrying noise, or really any one-dimensional signal that varies over time, this guide shows you how to put it through a Discrete Fourier Transform and read the result.

You don't need to remember calculus. You don't need to understand complex numbers (though you'll meet them briefly). You need to be comfortable reading a plot.

## What this is *not*

This is not the canonical reference. The math-rigorous derivation lives in [`../canonical/en/`](../canonical/en/). If you finish a chapter here and want to know *why* the algorithm works, follow the cross-links — every chapter ends with pointers into the canonical tier.

This is not exhaustive. The five-band progression (oscilloscope → audio → vibration → geophysical → radio interferometry) jumps deliberately from familiar to advanced. If you want a specific domain in depth, this guide gets you to the doorstep; the books in [`../../shared/reference-bibliography/refs.bib`](../../shared/reference-bibliography/refs.bib) take you the rest of the way.

## How to use this guide

Each chapter is self-contained but they're written to be read in order. The complexity escalates one axis at a time:

| Chapter | New thing the chapter teaches |
|---------|------------------------------|
| [B1 — Oscilloscope](01-oscilloscope.md) | DFT turns a time-domain trace into a frequency spectrum. Peaks = real signals. |
| [B2 — Audio](02-audio.md) | Multiple tones stack additively. Windowing matters when frequencies don't land on integer bins. |
| [B3 — Vibration](03-vibration.md) | Real industrial signals carry harmonics + fault signatures. Spectra are diagnostic. |
| B4 — Geophysical *(queued v0.2.x)* | Long records + noise floors + periodogram smoothing. |
| B5 — Radio interferometry / LIGO *(queued v0.2.x)* | FFT is the workhorse of modern observational physics. Same algorithm, bigger problems. |

Each chapter has three plots — input, spectrum, annotated takeaway — and a runnable script you can copy, paste, and modify. The figures in this guide were rendered by those scripts. Run a script, you get the same figures back, modulo your matplotlib's font choices.

## Tone

Dry. Technical. Slightly amused. If a sentence in here makes you think *"the author is being clever for the sake of being clever"*, file a bug. The point is to make Fourier feel obvious to readers who don't yet feel that way about it.

## License

This guide is CC-BY-SA-4.0. The example scripts are Apache 2.0. The DFT algorithm itself has been around since 1822 (Joseph Fourier) and 1965 (Cooley and Tukey for the fast version); we make no claim there.

---

**Next:** [B1 — Oscilloscope trace](01-oscilloscope.md)
