# Just Shad's Guide to Fourier's Galaxy

> *placeholder for the Miyazaki dragon — smoking weed, drinking tea, looking mildly amused*

## What this is

Most books about the Fourier transform start by writing the Fourier transform on the page. They write it in its full integral form, with the limits going to infinity and the integrand involving a complex exponential, and they apologise for none of it. The reader, having opened the book hoping to understand something interesting about the world, closes it again and goes looking for a different book.

This guide does not do that. This guide starts somewhere else entirely. It starts with the assumption that you, the reader, have a piece of data¹ that you would like to understand better, and that you suspect — correctly, as it happens — that the way to understand it better involves a thing called a Discrete Fourier Transform. The data might be a CSV file with timestamps and voltages. It might be an audio recording of an instrument you cannot identify. It might be a vibration log from a machine in your basement that has, over the last fortnight, begun to make a noise it did not previously make.

(¹ "Data" is, in the most pedantic sense possible, the plural of "datum", and a single number is, technically, "a datum". This guide will use "data" as a mass noun throughout, because that is what it is in English in 2026 regardless of what Latin teachers say.)

The DFT can tell you something useful about any of those. **Don't panic** if you're new to the algorithm: by the end of this guide you will have run it against four or five different signals, in seven different domains, with code you can copy and modify, and you will have a working intuition for what it does and what it doesn't.

What you need to bring:

- a curiosity about your data, or somebody else's data
- the willingness to read a plot
- a Python interpreter, if you want to run the code (optional, but recommended)
- about 25 minutes per chapter, give or take
- nothing else — no calculus, no remembered complex-number rules, no theorem-proving discipline

Complex numbers will show up briefly, and we will deal with them when they do.

## What this is *not*

This is not the canonical reference. Anywhere this guide says "the DFT does X", there is a more rigorous statement of the same fact in [`../canonical/en/`](../canonical/en/) with the proof attached. The cross-tier hand-off is the point. If you read a chapter here and find yourself wanting to know *why* the result is what it is — not just *that* it is — follow the link at the chapter's end.

This is not exhaustive either. The seven-band progression — oscilloscope, audio, vibration, electronic systems, radar, radio astronomy, nuclear reactor noise — jumps deliberately from familiar to advanced, and skips a great many domains in between. There is no chapter on seismology, no chapter on medical imaging, no chapter on financial time series, no chapter on weather radar (which is a different chapter from regular radar, and is fascinating in its own right, and may eventually become a chapter here when somebody has the time to write it). The seven bands are the ones that, in the author's opinion, give you the broadest cross-section of "what the DFT does, applied to real signals" with the smallest number of words.

If you want a specific domain in greater depth than this guide provides, the books in [`../../shared/reference-bibliography/refs.bib`](../../shared/reference-bibliography/refs.bib) are the ones to read next. This guide gets you to the doorstep; the books take you the rest of the way through.

## How to use this guide

Each chapter is self-contained but they are written to be read in order. The complexity escalates one axis at a time:

| Chapter | New thing the chapter teaches |
|---------|------------------------------|
| [B1 — Oscilloscope](01-oscilloscope.md) | DFT turns a time-domain trace into a frequency spectrum. Peaks correspond to real signals. |
| [B2 — Audio](02-audio.md) | Multiple tones stack additively. Windowing matters when frequencies don't land on integer bins. |
| [B3 — Vibration](03-vibration.md) | Real industrial signals carry harmonics + fault signatures. Spectra are diagnostic. |
| [B4 — Electronic systems](04-electronic.md) | Modulation, demodulation, and the DFT as the universal demodulator. |
| [B5 — Radar](05-radar.md) | Same algorithm; now it extracts distance and velocity from echoes. |
| B6 — Radio astronomy *(queued v0.2.x)* | Pulsar timing, coherent dedispersion, the DFT in observational physics. |
| B7 — Nuclear reactor noise *(queued v0.2.x)* | Where the bare DFT stops being enough, and the toolkit you reach for next. |

Each chapter has three plots — input, spectrum, annotated takeaway — and a runnable script you can copy, paste, and modify. The figures in this guide were rendered by those scripts. Run a script, you get the same figures back, modulo your matplotlib's font choices and the colour palette your terminal feels like producing today.

## Tone

Dry. Technical. Slightly amused. Occasionally wandering off on a related observation for a paragraph before returning to the main point. The relevant comparison, for readers who care about literary comparisons, is to a particular tradition of British technical writing where the narrator is allowed to find things interesting on the reader's behalf². This is partly because the DFT genuinely is interesting once you can see what it's doing, and partly because the narrator is the only person available to keep the reader company while the reader figures it out.

(² The full voice-guide for this tier lives at [`../../_specs/SHAD-VOICE-GUIDE-v0.2.md`](../../_specs/SHAD-VOICE-GUIDE-v0.2.md) — read it only if you are an author writing new chapters in this guide. Readers can ignore it; the voice does its job whether or not you know there's a spec for it.)

If a sentence in here makes you think *"the author is being clever for the sake of being clever"*, please file a bug. The point is to make Fourier feel obvious to readers who don't yet feel that way about it, not to perform cleverness at them.

## License

This guide is CC-BY-SA-4.0. The example scripts are Apache 2.0. The DFT algorithm itself has been around since 1822 (Joseph Fourier, in a treatise mostly about heat) and 1965 (Cooley and Tukey, who made the fast version, in a paper of about four pages); we make no claim there, and would have to disgrace a great many tombs to try.

---

**Next:** [B1 — Oscilloscope trace](01-oscilloscope.md)
