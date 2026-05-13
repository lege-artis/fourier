#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
probe_b1_muon.py -- one-time structural probe of the Rodriguez muon
oscilloscope data set, to inform B1 chapter authoring.

Downloads:
    https://amor.cms.hu-berlin.de/~rodrigus/Resources/MuonLifetimeData.zip

Copyright on the data set (per amor.cms.hu-berlin.de/~rodrigus/copyright.html):
    (c) 2018-2022 Santiago Rodriguez.
    Personal use and reproduction unrestricted; public reproduction needs
    written permission. Public use must credit + link to his site.
Per those terms, lege-artis/fourier does NOT redistribute the data: the
reader fetches it themselves via this script. The chapter embeds only
first-N-rows snippets under fair-use educational citation with full
attribution, and links back to the source.

Run:
    python probe_b1_muon.py

Outputs to ./data/muon/:
    The unzipped contents of MuonLifetimeData.zip.

Prints to stdout:
    - File listing with sizes
    - For each ASCII-text file: encoding, line count, first 30 lines
    - For each binary file: first 64 bytes hex dump + magic detection
    - Summary heuristic: which file looks like the oscilloscope-export

Paste the stdout back to chat -- the B1 chapter then gets authored
against the actual data layout (not speculatively).
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data" / "muon"
DATA.mkdir(parents=True, exist_ok=True)

ZIP_URL  = "https://amor.cms.hu-berlin.de/~rodrigus/Resources/MuonLifetimeData.zip"
ZIP_PATH = DATA / "MuonLifetimeData.zip"


def fetch():
    if ZIP_PATH.exists():
        print(f"[cached]  {ZIP_PATH.name}  ({ZIP_PATH.stat().st_size:,} bytes)")
        return
    print(f"[fetch]   {ZIP_URL}")
    subprocess.run(
        ["curl", "-fSL", "--max-time", "60", "-o", str(ZIP_PATH), ZIP_URL],
        check=True,
    )
    print(f"          -> {ZIP_PATH.name}  ({ZIP_PATH.stat().st_size:,} bytes)")


def unzip():
    extract_root = DATA / "extracted"
    if extract_root.exists() and any(extract_root.iterdir()):
        print(f"[cached]  extracted/  ({sum(1 for _ in extract_root.rglob('*'))} entries)")
        return extract_root
    extract_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extractall(extract_root)
    print(f"[unzip]   {ZIP_PATH.name}  ->  extracted/")
    return extract_root


def probe_file(path: pathlib.Path, max_lines: int = 30) -> None:
    rel = path.relative_to(DATA)
    size = path.stat().st_size
    print(f"\n--- {rel}  ({size:,} bytes) ---")
    # try text
    try:
        with open(path, encoding="utf-8") as fh:
            head = []
            for i, line in enumerate(fh):
                if i >= max_lines:
                    break
                head.append(line.rstrip("\n"))
            # count remaining lines cheaply
            extra = sum(1 for _ in fh)
        total_lines = len(head) + extra
        if head and all(ord(c) < 128 for c in (head[0] if head else "")):
            print(f"  [text, {total_lines} lines]")
            for ln, line in enumerate(head):
                print(f"  {ln+1:>4}|  {line}")
            if extra > 0:
                print(f"  ...  ({extra} more lines)")
            return
    except UnicodeDecodeError:
        pass
    # fallback: binary hex dump
    with open(path, "rb") as fh:
        head = fh.read(64)
    hexstr = " ".join(f"{b:02x}" for b in head)
    asciistr = "".join(chr(b) if 32 <= b < 127 else "." for b in head)
    magic_hint = ""
    if head[:2] == b"PK":
        magic_hint = "  (ZIP archive)"
    elif head[:4] == b"\x89PNG":
        magic_hint = "  (PNG image)"
    elif head[:3] == b"\xff\xd8\xff":
        magic_hint = "  (JPEG image)"
    elif head[:4] == b"%PDF":
        magic_hint = "  (PDF document)"
    print(f"  [binary, first 64 bytes hex]{magic_hint}")
    print(f"  hex:    {hexstr}")
    print(f"  ascii:  {asciistr}")


def main() -> int:
    print("=" * 60)
    print(" Rodriguez muon-scope data probe (one-time, for B1 authoring)")
    print(" Source: " + ZIP_URL)
    print(" Licence: personal-use OK per amor.cms.hu-berlin.de/~rodrigus/copyright.html")
    print("=" * 60)
    fetch()
    extract_root = unzip()

    print()
    print("--- file listing ---")
    files = sorted(p for p in extract_root.rglob("*") if p.is_file())
    for p in files:
        size = p.stat().st_size
        print(f"  {size:>10,d}  {p.relative_to(DATA)}")
    print(f"  total files: {len(files)}")

    print()
    print("--- per-file probe ---")
    for p in files:
        probe_file(p)

    print()
    print("=" * 60)
    print(" Probe complete. Paste this output back to chat.")
    print(" The B1 chapter author will use this to map the real")
    print(" scope-CSV layout (header + columns) into the five-step")
    print(" pipeline, the same way S2 / S3 / S4 in B0 were authored.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
