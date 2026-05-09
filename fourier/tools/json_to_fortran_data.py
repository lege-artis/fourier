#!/usr/bin/env python3
"""
json_to_fortran_data.py - Convert DFT golden-vector JSONs to Fortran-readable
                          list-directed-read .dat files.

Per: _specs/SONNET-HANDOFF-v0.1-FOURIER-STAGE-4-FOLLOWON.md section 4.1

For each shared/golden-vectors/dft_n=<N>.json (excluding the leakage variant
which is consumed by Job-2 PT-DFT-03B, not Job-3), emit a corresponding
build/golden/dft_n_<N>.dat file. The Fortran test program test_dft_golden.f90
opens each .dat with form='formatted' and read(*,*) consumes the
whitespace-separated tokens in the order written below.

.dat layout (whitespace-separated tokens; no embedded comments since
list-directed read does not support them):

    <N>                            integer    sequence length
    <NCASES>                       integer    number of test cases in this file
    "<case_name_1>"                quoted     case name (Fortran reads quoted string)
    <INPUT_LEN>                    integer    length of input vector (== N)
    <re_1> <im_1>                  reals      input[1] real, imag pair
    <re_2> <im_2>                                ...
    <re_INPUT_LEN> <im_INPUT_LEN>
    <EXPECTED_LEN>                 integer    length of expected vector (== N)
    <re_1> <im_1>                  reals      expected[1] real, imag pair
    <re_2> <im_2>
                                   ...
    "<case_name_2>"                next case
                                   ...

Floating-point values are emitted via Python's repr(float), which is the
shortest decimal string that round-trips exactly to the same IEEE 754
binary64 value (PEP 3101). Fortran list-directed read of real(real64)
parses the same standard scientific notation (e.g. 1.2246467991473532e-16).

Idempotency: the script writes deterministically given the same JSON input.
Running twice produces byte-identical output (modulo the dict-iteration-order
guarantee in Python 3.7+).

Usage:
    python3 tools/json_to_fortran_data.py
        # uses defaults: input=shared/golden-vectors, output=backends/fortran/build/golden

    python3 tools/json_to_fortran_data.py --input <dir> --output <dir>
        # explicit paths

License: Apache 2.0
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

# Skip patterns: JSONs not consumed by Job-3 (leakage variant is Job-2's).
SKIP_PATTERNS = ("_leakage", "_cosine_leakage")


def discover_input_jsons(input_dir: Path) -> list[Path]:
    """Return sorted list of dft_n=*.json files, excluding skip patterns."""
    if not input_dir.is_dir():
        raise FileNotFoundError(f"input directory not found: {input_dir}")
    candidates = sorted(input_dir.glob("dft_n=*.json"))
    selected = [p for p in candidates if not any(s in p.stem for s in SKIP_PATTERNS)]
    return selected


def parse_n_from_filename(json_path: Path) -> int:
    """Extract <N> from a filename like 'dft_n=64.json'."""
    stem = json_path.stem  # e.g. 'dft_n=64'
    if "=" not in stem:
        raise ValueError(f"unexpected filename pattern (no '='): {json_path}")
    return int(stem.split("=", 1)[1])


def fortran_real_token(value: float) -> str:
    """Emit a real(real64) literal as Fortran list-directed read consumes it.

    Python's repr(float) gives the shortest decimal string that round-trips
    exactly. Fortran read(unit, *) of real(real64) accepts the same notation.

    Edge cases handled:
    - integer-valued floats: repr(1.0) -> '1.0'; Fortran reads as real -> 1.0
    - scientific notation: repr(1.2e-16) -> '1.2e-16'; Fortran accepts e/E/d/D
    - special values are NOT expected in golden vectors (no NaN/Inf)
    """
    return repr(value)


def quote_case_name(name: str) -> str:
    """Quote a case name for Fortran list-directed read of character.

    Fortran read(unit, *) consumes a quoted string literal. We use double
    quotes to permit case names containing apostrophes (none in current
    test_cases keys, but defensive).
    """
    if '"' in name:
        # Fallback to single quotes if double quote present (none expected).
        return "'" + name.replace("'", "''") + "'"
    return '"' + name + '"'


def emit_dat(json_path: Path, dat_path: Path) -> tuple[int, int]:
    """Read a golden-vector JSON and write the corresponding .dat file.

    Returns: (N, num_cases) for stdout reporting.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    declared_n = int(doc.get("N", 0))
    filename_n = parse_n_from_filename(json_path)
    if declared_n != filename_n:
        raise ValueError(
            f"{json_path.name}: declared N={declared_n} disagrees with filename N={filename_n}"
        )

    test_cases = doc.get("test_cases")
    if not isinstance(test_cases, dict):
        raise ValueError(f"{json_path.name}: 'test_cases' is missing or not a dict")

    ncases = len(test_cases)
    if ncases == 0:
        raise ValueError(f"{json_path.name}: 'test_cases' is empty")

    # Build the .dat content as a list of lines for clarity, then write atomically.
    lines: list[str] = []
    lines.append(str(declared_n))
    lines.append(str(ncases))

    for case_name, case in test_cases.items():
        input_pairs = case.get("input")
        output_pairs = case.get("output")
        if not isinstance(input_pairs, list) or not isinstance(output_pairs, list):
            raise ValueError(
                f"{json_path.name}: case '{case_name}' input/output not a list"
            )
        if len(input_pairs) != declared_n:
            raise ValueError(
                f"{json_path.name}: case '{case_name}' input length {len(input_pairs)} != N {declared_n}"
            )
        if len(output_pairs) != declared_n:
            raise ValueError(
                f"{json_path.name}: case '{case_name}' output length {len(output_pairs)} != N {declared_n}"
            )

        # Case-name token (quoted for Fortran read(*,*) string consumption)
        lines.append(quote_case_name(case_name))

        # INPUT block
        lines.append(str(declared_n))
        for pair in input_pairs:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError(
                    f"{json_path.name}: case '{case_name}' input pair shape != [real, imag]"
                )
            re_, im_ = float(pair[0]), float(pair[1])
            lines.append(f"{fortran_real_token(re_)} {fortran_real_token(im_)}")

        # EXPECTED block
        lines.append(str(declared_n))
        for pair in output_pairs:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError(
                    f"{json_path.name}: case '{case_name}' output pair shape != [real, imag]"
                )
            re_, im_ = float(pair[0]), float(pair[1])
            lines.append(f"{fortran_real_token(re_)} {fortran_real_token(im_)}")

    # Atomic write: build full string first, then write in one syscall.
    content = "\n".join(lines) + "\n"
    dat_path.parent.mkdir(parents=True, exist_ok=True)
    dat_path.write_text(content, encoding="ascii")

    return declared_n, ncases


def main(argv: Iterable[str] | None = None) -> int:
    # Self-locate: tool sits at fourier/fourier/tools/json_to_fortran_data.py.
    # Project root is the parent of `tools/`.
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent  # fourier/fourier/

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root / "shared" / "golden-vectors",
        help="Directory containing dft_n=*.json files (default: shared/golden-vectors)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "backends" / "fortran" / "build" / "golden",
        help="Output directory for .dat files (default: backends/fortran/build/golden)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    input_dir: Path = args.input.resolve()
    output_dir: Path = args.output.resolve()

    print(f"[json_to_fortran_data] input:  {input_dir}")
    print(f"[json_to_fortran_data] output: {output_dir}")

    try:
        json_paths = discover_input_jsons(input_dir)
    except FileNotFoundError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    if not json_paths:
        print(
            "[error] no dft_n=*.json files found (after skip-pattern filter); aborting",
            file=sys.stderr,
        )
        return 2

    total_n = 0
    total_cases = 0
    for jp in json_paths:
        try:
            n_value = parse_n_from_filename(jp)
            dat_path = output_dir / f"dft_n_{n_value}.dat"
            declared_n, ncases = emit_dat(jp, dat_path)
            print(f"  [ok] {jp.name} -> {dat_path.name}  (N={declared_n}, cases={ncases})")
            total_n += 1
            total_cases += ncases
        except (ValueError, OSError) as exc:
            print(f"  [error] {jp.name}: {exc}", file=sys.stderr)
            return 2

    print(
        f"[json_to_fortran_data] done: {total_n} files emitted "
        f"covering {total_cases} test cases"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
