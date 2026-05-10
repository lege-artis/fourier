#!/usr/bin/env python3
"""
json_to_fortran_data.py -- convert golden-vector JSON files to .dat (cross-language)

Reads:  shared/golden-vectors/dft_n={2,4,8,16,64}.json
Emits:  backends/fortran/build/golden/dft_n={2,4,8,16,64}.dat
        backends/cpp/build/golden/dft_n={2,4,8,16,64}.dat   (v0.2.0 C++ port)

The .dat format is language-agnostic (Fortran-name retained for historical
continuity; both Fortran and C++ tests read the same format). Future ports
(Rust, Pascal) will consume the same .dat files.

.dat format (whitespace-tokenized + 64-char fixed-field for case name):
  Line 1:  N  num_cases                (integers)
  Per case (repeated num_cases times):
    Line:    case_name                  (64-char fixed field, space-padded)
    N lines: re_in  im_in              (IEEE 754 double, .17e)
    N lines: re_out im_out             (IEEE 754 double, .17e)

Usage (from repo root):
    python tools/json_to_fortran_data.py

Called automatically by:
    make golden-data   (from backends/fortran/ AND backends/cpp/)

Per WORKING-SPEC-v0.3-EN.md section 4.2 (oracle-as-testbed rule).
License: Apache 2.0
"""
from __future__ import annotations

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
GV_DIR    = REPO_ROOT / "shared" / "golden-vectors"

# Output dirs: one per backend, all gitignored (build/ is in .gitignore).
OUT_DIRS = [
    REPO_ROOT / "backends" / "fortran" / "build" / "golden",
    REPO_ROOT / "backends" / "cpp"     / "build" / "golden",
]
for d in OUT_DIRS:
    d.mkdir(parents=True, exist_ok=True)

SIZES = [2, 4, 8, 16, 64]


def emit_dat(out_path: pathlib.Path, n: int, cases: dict) -> None:
    """Write one .dat file in the canonical cross-language format."""
    num_cases = len(cases)
    with open(out_path, "w", encoding="ascii") as fh:
        fh.write(f"{n:8d} {num_cases:8d}\n")
        for case_name, case_data in cases.items():
            fh.write(f"{case_name:<64}\n")
            for re, im in case_data["input"]:
                fh.write(f"  {re:.17e}  {im:.17e}\n")
            for re, im in case_data["output"]:
                fh.write(f"  {re:.17e}  {im:.17e}\n")


def convert(n: int) -> None:
    json_path = GV_DIR / f"dft_n={n}.json"
    with open(json_path, encoding="utf-8") as fh:
        bundle = json.load(fh)

    cases = bundle["test_cases"]
    num_cases = len(cases)

    for out_dir in OUT_DIRS:
        out_path = out_dir / f"dft_n_{n}.dat"
        emit_dat(out_path, n, cases)
        rel = out_path.relative_to(REPO_ROOT).as_posix()
        print(f"[OK] {rel} -- N={n}, {num_cases} cases")


if __name__ == "__main__":
    print("== json_to_fortran_data.py ==")
    for n in SIZES:
        convert(n)
    print("Done.")
