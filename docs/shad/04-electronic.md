# B4 — Electronic systems

## The premise

The word "filter" is borrowed from coffee, from water treatment, from air
conditioning — and in each context it means approximately the same thing: a
structure that lets some things through and stops the rest. The filter has no
editorial preferences. It has a physical structure, and that structure
determines what passes.

Electronic versions of the same idea work on exactly this principle, except
that the things being sorted are not particles or molecules but frequency
components — sinusoidal elements that coexist inside a complicated waveform
and can, rather surprisingly, be extracted from it individually. That this
extraction is possible at all was not obvious to anyone before approximately
1807, when a French administrator and mathematical physicist named Joseph
Fourier argued that any periodic function could be decomposed into sines and
cosines. He was told his proof had a gap in it¹. He had to wait fifteen years
before mathematics officially agreed with him.

(¹ The 1807 paper was submitted to the Institut de France and reviewed by
Lagrange, Laplace, and Monge, who found the convergence argument incomplete.
Fourier continued doing it anyway. The 1822 *Théorie analytique de la chaleur*
was the version that properly established the result; Dirichlet filled in the
last piece in 1829. The man responsible for "any signal can be decomposed into
frequencies" had to wait twenty-two years for full mathematical vindication —
which is, in retrospect, not how you'd choose to run things.)

B3 showed you a spectrum you could only *observe*. The machine was already
spinning; the fault was already there. Fourier handed you a picture.

**B4 is different.** In electronics, you actively *design* for frequency-domain
behaviour. A filter is literally defined by which frequencies it passes and
which it kills. A radio receiver is deliberately moving frequencies around. The
spectrum view is not a diagnostic aid here — it is the primary engineering
language.

Three sub-topics, each adding one layer to the same idea: active circuits change
the spectrum, and you can predict exactly how.

---

## 1. AC mains harmonics — what is actually in that socket?

### The setup

You probably learned that mains is a "50 Hz sine wave." It is not. Everything
you plug in that contains a rectifier (phone charger, computer power supply,
LED dimmer) draws current in narrow pulses rather than sinusoidally. That
non-linear current draw distorts the mains voltage, injecting energy at odd
harmonics of the 50 Hz fundamental.

The distortion is not dramatic in the time domain — the waveform still looks
like a sine wave if you glance at it quickly — but it accumulates across an
entire building's load mix, and a spectrum analyser makes the harmonics
unmistakeable.

`examples/shad/b4-electronic/main.py` synthesises a realistic mains waveform:

| Harmonic | Frequency | Relative amplitude | Source |
|----------|-----------|-------------------|--------|
| **1st (fundamental)** | 50 Hz | 1.000 | The line itself |
| **3rd** | 150 Hz | 0.040 | Single-phase rectifiers |
| **5th** | 250 Hz | 0.025 | Switching power supplies |
| **7th** | 350 Hz | 0.015 | Accumulated load mix |
| **9th** | 450 Hz | 0.008 | Distributed building load |

Total Harmonic Distortion: **THD = 5.0%** — typical residential grid.

### The input

![B4 input: mains time-domain waveform](figures/fig-b4-input.png)

Three cycles of 50 Hz mains. The distortion from harmonics is visible as a
slight flattening near each peak — not dramatic, but measurable. This is the
signal arriving at your equipment's input terminals every day.

### The spectrum

![B4 spectrum: mains harmonics, filter response, mixer output](figures/fig-b4-spectrum.png)

Top panel: mains spectrum, 0–600 Hz. Five peaks. The fundamental at 50 Hz
dominates; the odd harmonics fall off to the right. The 9th harmonic (450 Hz)
is barely visible at 0.8% amplitude — but it is there, and it matters in
sensitive measurement equipment.

### The takeaway

![B4 takeaway: annotated mains harmonics, filter, mixer](figures/fig-b4-takeaway.png)

**Panel 1 — reading the mains spectrum like a power quality engineer:**

The standard metric is **THD** (Total Harmonic Distortion):

```
THD = sqrt(V_3^2 + V_5^2 + V_7^2 + V_9^2 + ...) / V_1
```

IEEE 519-2022 sets acceptable THD limits for industrial and utility
interconnections: typically < 5% THD-V at the point of common coupling for
most industrial systems, < 8% for some distribution-level buses.

A THD above these thresholds has measurable consequences:
- **Motor heating**: motors see voltages that produce torque at all harmonic
  frequencies; the harmonics mostly produce heat, not useful torque.
- **Transformer derating**: the additional copper and core losses from
  harmonics require a de-rating factor K, typically K = 0.85–0.95 for a
  moderately distorted supply.
- **EMC pre-compliance**: every product sold in the EU must pass IEC 61000-3-2
  (limits on harmonic current drawn from the mains). The measurement is just
  an FFT of the input current waveform, checked against a published table.
  That compliance test *is* what we just computed.

---

## 2. Active filter — filtering IS multiplication in frequency

### The setup

The goal: suppress the 5th, 7th, and 9th mains harmonics from a sensitive
analogue measurement circuit. You install a 2nd-order Sallen-Key low-pass
filter with a cutoff at 300 Hz.

The Sallen-Key transfer function (normalised LP)²:

(² R.P. Sallen and E.L. Key published this active-filter topology in a 1955
paper while working at MIT Lincoln Laboratory — a few years after commercial
op-amps had made active filters economically viable. The topology is sometimes
described as "two RC stages and an op-amp", which is accurate the same way
that a lever is "a plank and a fulcrum". Its practical virtue was that it
achieved a 2nd-order response with no inductors, which in the 1950s was a
meaningful advantage — audio-frequency inductors are large, expensive, and
have a tendency to pick up interference from nearby transformers.)

```
H(f) = 1 / (1 + j*(f/fc)/Q - (f/fc)^2)
```

**Do not panic about the** `j` **in that expression.** The `j` is the imaginary
unit (√−1), and it is doing one specific job here: encoding the phase shift the
filter introduces at each frequency — a real physical effect, not a
mathematical inconvenience. The modulus |H(f)| — the amplitude response, which
is what the figures show — comes out to a real positive number after the
arithmetic, and that is the only number you need to read a plot.

For a Butterworth (maximally flat) response: Q = 1/sqrt(2) = 0.707.
Above the cutoff the response rolls off at −40 dB/decade (factor of 100 in
power per decade of frequency).

The script applies this filter entirely in the frequency domain: compute the
FFT of the input, multiply by H(f), inverse-FFT back to time. This is not a
trick — it is exactly what the physical capacitors and op-amp are doing, just
described in different notation.

### The spectrum (panel 2 of the figure)

The middle panel of both figures shows the test signal (broadband: tones at
80, 200, 600, and 1200 Hz plus noise) before and after the filter.

**Before:** four peaks of roughly similar amplitude, spread across 0–1800 Hz.

**After:** the 80 Hz and 200 Hz tones survive nearly intact (they are inside
the passband); the 600 Hz and 1200 Hz tones are strongly attenuated. The noise
floor above ~500 Hz has collapsed.

### The takeaway (panel 2 annotated)

The annotation marks the 300 Hz cutoff with a dashed line and labels the
attenuation region. The key engineering intuition:

> **A filter is a multiplier in the frequency domain.** Each frequency bin
> of the input spectrum is multiplied by |H(f)| — near 1.0 inside the passband,
> near 0 far above cutoff. There is no mystery about "where the energy went."
> It was multiplied by a very small number.

The −40 dB/decade slope of a 2nd-order Butterworth filter means that a tone
at 10× the cutoff frequency (3000 Hz in our case) is attenuated by a factor of
100 in voltage (40 dB). At 100× the cutoff it is attenuated by 10,000× (80 dB).
Each additional filter order adds another −20 dB/decade to the rolloff — hence
the preference for higher-order filters in demanding EMC applications.

---

## 3. Heterodyne mixer — shifting the spectrum

### The setup

A superheterodyne receiver (every AM radio, FM radio, and most SDR dongles
uses this principle) wants to shift an incoming RF signal at an arbitrary
frequency down to a fixed intermediate frequency (IF) where it can be filtered
and amplified efficiently.

The mechanism is elegant enough to deserve a moment of appreciation before the
algebra. In 1918, Edwin Howard Armstrong — an American electrical engineer with
a remarkable gift for invention and an equally remarkable gift for acquiring
enemies — demonstrated that you could shift *any* incoming signal to a single
fixed intermediate frequency by multiplying it against a tunable local
oscillator³. The receiver's filters and amplifiers could then be designed once,
for that fixed IF, and every station in the broadcast band would arrive through
the same processing chain. This is the superheterodyne principle.

(³ Armstrong's superheterodyne patent was contested by Lee de Forest and later
by RCA for years. Armstrong won the legal arguments but spent most of his
fortune doing so, and did not live to see the principle become the architectural
basis of every radio receiver manufactured for the rest of the twentieth
century. He died in 1954. The basic trigonometric product predates him —
Reginald Fessenden described it in 1901 — but Armstrong turned it into a
practical receiver architecture, which is the part the industry kept.)

The mechanism: **multiply the RF signal by a local oscillator (LO) in the time
domain.** Trigonometric identity:

```
sin(2*pi*f_RF*t) * sin(2*pi*f_LO*t)
    = 0.5 * [cos(2*pi*(f_RF - f_LO)*t) - cos(2*pi*(f_RF + f_LO)*t)]
```

The product produces two new frequencies: the **difference** (RF − LO) and the
**sum** (RF + LO). In a receiver, you choose LO so that the difference falls
at a convenient IF; you then filter out the sum.

The script uses:
- RF = 1000 Hz (simulated carrier)
- LO =  900 Hz (local oscillator)
- IF− = RF − LO = **100 Hz** (this is the desired output channel)
- IF+ = RF + LO = **1900 Hz** (this is the image, filtered out)

### The spectrum (panel 3)

Bottom panel: the mixer output spectrum, 0–2200 Hz. The RF input and LO input
are present (they leak through in a real mixer; here they appear because we
synthesise the product of two real sinusoids). The two new peaks at 100 Hz and
1900 Hz are clearly visible, with equal amplitude — as the trigonometric
identity predicts.

### The takeaway (panel 3 annotated)

**Reading the mixer output spectrum:**

1. **100 Hz (IF−)**: this is the signal you want. A bandpass filter centred at
   100 Hz would isolate it cleanly. In a real radio, this is the audio or
   baseband channel.
2. **900 Hz (LO)**: the local oscillator leaks through. In a well-designed
   mixer IC the LO-to-output isolation is 30–50 dB; visible here because our
   ideal multiplication has no isolation at all.
3. **1000 Hz (RF)**: the RF input also leaks. Same comment.
4. **1900 Hz (IF+)**: the unwanted image. Filtered by the IF filter (a BP
   centred on 100 Hz would kill it; it's 1800 Hz away).

Why does this matter beyond radios? The same heterodyne principle appears in:
- **Lock-in amplifiers**: detect a weak signal buried in noise by multiplying
  with a reference oscillator at the exact signal frequency, shifting it to
  DC where a low-pass filter removes all other noise.
- **Optical coherence tomography (OCT)**: the depth information is encoded in
  the beat frequency between a sample arm and a reference arm — a heterodyne
  in the optical domain.
- **Software-defined radio (SDR)**: the RTL-SDR dongle you can buy for €20
  does exactly this in silicon at GHz frequencies.
- **Gravitational wave detectors**: LIGO uses optical heterodyne
  interferometry to detect mirror displacements smaller than one-thousandth of
  a proton diameter — which is, by some margin, the most demanding application
  of the trigonometric identity four paragraphs above.

---

## What we just did

Three sub-topics, one unifying claim: **the spectrum is the primary design
language for active circuits.**

An oscilloscope shows you what happened. A spectrum analyser shows you what
will happen if you add a filter, swap a component, or mix in an oscillator. The
difference between B3 (observation) and B4 (design) is the difference between
diagnosis and engineering. The spectrum doesn't care which one you're doing.
It reports the frequencies. It has always reported the frequencies.

B5 takes this one step further: Doppler radar uses the heterodyne principle to
measure velocity, not just frequency. The spectrum of the returned pulse tells
you not just what frequency was transmitted, but how fast the target is moving.

---

## References

- A. Sedra and K. Smith, *Microelectronic Circuits*, 8th ed., Oxford University
  Press, 2014. §12.2 (Sallen-Key topology + active filter design).
  ISBN 978-0-19-933918-8.

- B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall, 2011. §2.3 (mixers
  and heterodyne receivers). ISBN 978-0-13-272914-9.

- IEEE Standard 519-2022, *IEEE Standard for Harmonic Control in Electric Power
  Systems*, IEEE, 2022. doi: 10.1109/IEEESTD.2022.9848440. (THD limits and
  measurement methodology.)
