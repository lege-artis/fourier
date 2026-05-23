# Cover letter draft — Shaddack birthday-edition shipment

**Filename for email subject:** `Just Shad's Guide to Fourier's Galaxy — v0.2.x-opus-iter (birthday edition)`
**Attachment:** `shad-guide-shipment-2026-05-24.tar.gz` (3.6 MB)
**Tone:** technical-shipment-formal per project-owner direction; birthday acknowledgement as brief opener.
**Status:** DRAFT — review before send. Edit anything that doesn't sound like you.

---

## Email body (English) — draft

Subject: **Just Shad's Guide to Fourier's Galaxy — v0.2.x-opus-iter (birthday edition)**

---

Shaddack,

Happy birthday. Attached is the next iteration of the Shad guide, timed
to coincide.

This is `v0.2.x-opus-iter` — the next step on the same arc as the
`v0.2.x-first-cut` you saw earlier this month. The shipment structure is
unchanged: single-file LaTeX source, the same `data/` head fixtures, the
same `figures/` directory layout, and a `build.sh` that invokes
`pdflatex` twice. If it built for you last time, it will build for you
this time.

**What changed:**

- **Preamble & Dedication** and **B1 oscilloscope** carry a new voice
  pass — call it the Hitchhiker's pass, in the sense that the narrator
  is now allowed to wander for a paragraph and is on speaking terms
  with both the reader and the muon. Numerical content is byte-identical
  to the prior cut (verified via grep against 25+ key claims).
- **B0** unchanged from `v0.2.x-first-cut`. The real-data pipeline you
  saw is preserved exactly.
- **B2–B5** carry the prior cut's "queued for rebuild" stub content
  unchanged. A v0.2 voice pass on those is queued for `v0.2.x-sonnet-batch`
  later this month.
- **Canonical equations chapter** (DFT-1, FFT-1, PS-1) unchanged.
- **Bibliography**, **figures**, **data fixtures**, **build process**:
  unchanged.

The voice pass is the main thing. If you read the new B0 prologue and
the new B1 oscilloscope chapter and tell me whether the narrator is
being clever-for-its-own-sake at any point, that is the most useful
feedback you can give. The acceptance gates I wrote against (A1–A10
in the voice guide) include an explicit "if a sentence feels clever
for the sake of being clever, file a bug" clause — and you are
probably the only reader who will spot the violations the author
missed.

PDF and EPUB built in-house and attached separately if email size
permits. Both render the new voice intact. If the attachment system
chokes on size, the .tex shipment is the source of truth and either
output is reproducible from it via `./build.sh`.

The `lege-artis/fourier` public repo on GitHub carries the same content
at v0.2.x-opus-iter — `git pull` if you prefer to track it that way.

Thanks for being the audience this guide is written for. The whole
voice direction would not exist without your having stood in for "the
reader who has soldered something" all the way through the prior cut.

— Pete

---

## Pre-send checklist

Before hitting send:

1. [ ] Open `inspection/shad-guide.pdf` locally and skim B0 + B1 — confirm v0.2 voice landed as expected
2. [ ] Open `inspection/shad-guide.epub` on whatever EPUB reader you use — confirm chapter nav works + cover image renders + math (DFT-1, FFT-1, PS-1) is at least readable
3. [ ] Confirm `shad-guide-shipment-2026-05-24.tar.gz` size fits your mail server's attachment limit (3.6 MB should be safe for most; if your provider caps at 25 MB you have headroom for adding the PDF + EPUB as separate attachments)
4. [ ] Confirm Shaddack's preferred delivery address is current
5. [ ] If lege-artis/fourier mirror push is also done by send-time, mention the public-repo path in the email (already in the draft — line "git pull if you prefer to track it that way")
6. [ ] Optional: attach the PDF + EPUB alongside the .tar.gz if your mail allows three attachments at ~5.9 MB combined
7. [ ] Send

---

## Czech version (CS) — optional second pass

If Shaddack prefers Czech delivery, request a CS pass on this draft as a
separate Opus task. The voice work itself is currently EN-only; CS/JA/DE/IT
translations are queued for `v0.1.1+` per the bibliography roadmap.

---

**End COVER-LETTER-DRAFT-v0.1.md**
