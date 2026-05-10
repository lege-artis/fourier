# Shad-tier example scripts

These three scripts render the figures used in [`docs/shad/`](../../docs/shad/).
Each runs standalone, without internet, and produces three PNGs in
`docs/shad/figures/`.

## Quick run

```bash
# Prerequisites (one-time)
pip install --user numpy matplotlib

# From the repo root:
python examples/shad/b1-scope/main.py
python examples/shad/b2-audio/main.py
python examples/shad/b3-vibration/main.py
```

The PNGs in `docs/shad/figures/` will be regenerated.

## What each script does

| Script | Synthesised signal | Demonstrates |
|--------|--------------------|--------------|
| [`b1-scope/main.py`](b1-scope/main.py) | 240 Hz sine + 10% white noise, 10 kHz x 50 ms | DFT as time -> frequency machine; clean integer-bin peak |
| [`b2-audio/main.py`](b2-audio/main.py) | C-major triad (C4+E4+G4), 44.1 kHz x 500 ms | Multiple peaks; rectangular vs Hann window |
| [`b3-vibration/main.py`](b3-vibration/main.py) | 30 Hz shaft + 2x imbalance + 3x alignment + BPFO bearing fault + noise, 5 kHz x 2 s | Real-machine spectrum reading; fault diagnostics |

## Customising

Each script has a `synth_*()` function at the top with named parameters
(sample rate, duration, frequencies, noise levels). Modify those to play
with the workflow. The plot helpers underneath are generic and don't
need to change.

## Real-data extension

Each script has an `---- Real-data extension (sketch) ----` block at the
bottom showing how to replace the synthesiser with a CSV / WAV / data
loader of your choice. The DFT and plot pipeline is identical; only the
data source changes.

## License

Apache 2.0 (consistent with `backends/` and the rest of `examples/`).
