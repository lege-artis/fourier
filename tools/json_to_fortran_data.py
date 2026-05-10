#!/usr/bin/env python3
"""
json_to_fortran_data.py -- convert golden-vector JSON files to Fortran .dat

Reads:  shared/golden-vectors/dft_n={2,4,8,16,64}.json
Emits:  backends/fortran/tests/golden_data/dft_n={2,4,8,16,64}.dat

.dat format (Fortran list-directed and explicit-format readable):
  Line 1:  N  num_cases                (integers, list-directed)
  Per case (repeated num_cases times):
    Line:    case_name                  (64-char fixed field, a-format, space-padded)
    N lines: re_in  im_in              (IEEE 754 double, .17e, list-directed)
    N lines: re_out im_out             (IEEE 754 double, .17e, list-directed)

Usage (from repo root):
    python tools/json_to_fortran_data.py

Called automatically by:
    make golden-data   (from backends/fortran/)

Per WORKING-SPEC-v0.3-EN.md section 4.2 (oracle-as-testbed rule).
License: Apache 2.0
"""
from __future__ import annotations

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
GV_DIR    = REPO_ROOT / "shared" / "golden-vectors"
# Output inside backends/fortran/build/golden/ -- this dir is gitignored
# (backends/fortran/build/ is in .gitignore); generated at test time.
OUT_DIR   = REPO_ROOT / "backends" / "fortran" / "build" / "golden"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SIZES = [2, 4, 8, 16, 64]


def convert(n: int) -> None:
    json_path = GV_DIR / f"dft_n={n}.json"
    with open(json_path, encoding="utf-8") as fh:
        bundle = json.load(fh)

    cases = bundle["test_cases"]      # OrderedDict preserved (Python 3.7+)
    num_cases = len(cases)

    # Underscore filename convention: dft_n_<N>.dat
    out_path = OUT_DIR / f"dft_n_{n}.dat"
    with open(out_path, "w", encoding="ascii") as fh:
        # Header: N  num_cases
        fh.write(f"{n:8d} {num_cases:8d}\n")
        for case_name, case_data in cases.items():
            # 64-char fixed field -- Fortran reads with read(unit, '(a64)')
            fh.write(f"{case_name:<64}\n")
            # N input complex values
            for re, im in case_data["input"]:
                fh.write(f"  {re:.17e}  {im:.17e}\n")
            # N oracle output complex values
            for re, im in case_data["output"]:
                fh.write(f"  {re:.17e}  {im:.17e}\n")

    print(f"[OK] backends/fortran/build/golden/dft_n_{n}.dat "
          f"-- N={n}, {num_cases} cases")


if __name__ == "__main__":
    print("== json_to_fortran_data.py ==")
    for n in SIZES:
        convert(n)
    print("Done.")
