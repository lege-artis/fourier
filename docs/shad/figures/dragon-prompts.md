# Dragon mascot — AI image-gen prompt brief

**Target file:** `docs/shad/figures/dragon-icon.png` (square, ≥1024 × 1024 px, transparent or cream background, no embedded text/watermark).

**Aesthetic register:** **drawing, not painting.** Line art, ink, pencil — no watercolour wash, no acrylic, no oil, no rendered glossy surfaces. The mark should read as a clean monochrome (or near-monochrome) ink-drawing first, with restrained colour accents second.

**Scalability requirement (load-bearing):** the output is also used as a thumbnail / favicon-adjacent icon. That means:
- Bold silhouette: the dragon's coil must be readable at 64 × 64 px.
- High contrast: dark ink lines against cream paper, no low-contrast grey-on-grey detail.
- Minimal background: the circular ink-wash seal is optional; if present, keep it faint enough that scaling down doesn't turn it into mud.
- Negative space deliberate: the empty cream paper around the figure is part of the composition. Don't let the model fill it with extraneous brushwork.

**Trademark hygiene:** No prompt contains `Studio Ghibli`, `Miyazaki`, `Haku`, `Spirited Away`. Both for IP cleanliness (the guide is CC-BY-SA-4.0 and ships publicly) and because most major gen-models now reject or degrade those terms. The visual register is reached through descriptive language only.

**Model notes:** Phrasing trades off by model. FLUX.1 / Imagen / SDXL respond well to long descriptive prompts (use the second prompt below). DALL·E 3 prefers tighter, scene-first phrasing (use the first prompt). Mid/late SD3 / SDXL with anime LoRA usually benefit from sketch / lineart / monochrome reinforcement in the negative prompt of any colour terms that would push it toward "painted".

---

## Recommended prompt (long, girl + dragon composition, smoking-gag gag, drawing register)

> Hand-drawn black-ink line art over cream paper, Japanese animation lineart style, no painting and no watercolour. A small girl in the lower-left of the frame: pinafore-style dress with shoulder straps, short dark hair tied back in a small ponytail, hands clasped at her chest, looking up with a small wry smile (not afraid, mildly amused). Upper-right and curving across the frame: a serene serpentine eastern river-dragon. The dragon has white scales, a flowing jade-green mane drawn as restrained line accents, two amber-coloured swept-back horns, half-closed amber eyes, one long curling whisker reaching toward the girl. The dragon holds a thin hand-rolled cigarette between its teeth at a casual diagonal, a single soft curl of grey smoke rising over the horns. Calm, mildly amused expression on both figures. Clean confident ink linework with consistent stroke weight, no shading gradients, no painted surfaces, optional faint circular ink-wash behind the dragon for compositional grounding. Cream paper backdrop. Square 1:1 composition. No text, no border, no watermark, no signature. The drawing must read clearly at thumbnail size: bold silhouette, strong negative space, high line contrast. Two figures meeting at a quiet moment; nothing menacing.

**Negative prompt (all models that accept one):**
`text, watermark, signature, logo, frame, border, blood, weapon, photorealistic, 3d render, painting, watercolour, watercolor, oil paint, acrylic, painted surfaces, soft shading gradient, low contrast, low quality, deformed hands, extra limbs, dark background, neon, glow`

---

## Tighter alternative (DALL·E 3 / shorter context windows)

> Black-ink line drawing on cream paper, Japanese animation lineart style. A small girl with short dark hair and a pinafore dress, lower-left, looking up with a wry smile. A serene serpentine white river-dragon with jade mane and amber horns curves across the frame from upper-right, head descending toward the girl, a thin hand-rolled cigarette held between its teeth, a single curl of grey smoke rising. Clean confident outlines, no painted shading, bold silhouette, strong negative space — must read at thumbnail size. Square 1:1, no text.

---

## Dragon-only fallback (if the girl figure breaks consistently)

> Black-ink line drawing on cream paper, Japanese animation lineart style. A serene serpentine eastern river-dragon coiled in mid-air, white scales, jade-green flowing mane, two amber swept-back horns, half-closed amber eyes, single long curling whisker, calm expression. Confident outlines, no painted shading, bold silhouette for thumbnail legibility. Square 1:1, no text, no border.

---

## Library layout

The `figures/` directory holds dragons under a three-role naming scheme:

| File | Role | How it lands |
|---|---|---|
| `dragon-firstshot.png` | preserved AI original #1 (library) | you save the PNG here |
| `dragon-secondshot.png` | preserved AI original #2 (library) | you save the PNG here |
| `dragon-cover.png` | active title-page cover (large) | `build-pdf.sh` refreshes from `dragon-firstshot.png` every run |
| `dragon-icon.png` | embedded picture inside TeX body (Preamble) | `build-pdf.sh` refreshes from `dragon-secondshot.png` every run |
| `dragon-thumbnail.png` | top-right corner-mark on every chapter opener (128 px) | `build-pdf.sh` regenerates via `sips` from `dragon-icon.png` every run |

Originals are canonical. Working copies (cover / icon / thumbnail) are **always** refreshed from originals at build time — drop a new AI generation onto the original name and the next build picks it up cleanly. To swap roles (e.g. promote secondshot to cover), edit the corresponding `cp -f` line at the top of `build-pdf.sh`.

## Once you have a new AI PNG

1. Save it to `docs/shad/figures/dragon-firstshot.png` or `dragon-secondshot.png` (whichever role you want it to take).
2. Re-run `docs/shad/build-pdf.sh` — the refresh + thumbnail steps fire automatically; pdflatex picks up the new images.
3. If the AI output is the wrong aspect ratio, crop/pad to square in any image editor before saving.
4. Spot-check at thumbnail size (64 × 64 or 128 × 128) before committing. If the dragon turns to mud at that scale, the model gave you a painting and not a drawing — re-run with stronger lineart emphasis in the prompt.
