#!/usr/bin/env python3
# =============================================================================
# _config/migrate-testcases-v1-to-v2.py — testcases.yaml v1 → v2 migration
# tags:    [PoC-01][MI-M-T-D08]
# date:    2026-05-03
# citation: MI-M-T-D08-TDD-SPEC.md §3.3, §8 (mapping table + extension)
#
# Usage:
#   python migrate-testcases-v1-to-v2.py                      (dry-run, prints diff)
#   python migrate-testcases-v1-to-v2.py --inplace            (writes to source file)
#   python migrate-testcases-v1-to-v2.py --out path/to/out.yaml
#   python migrate-testcases-v1-to-v2.py --check              (validate only; exit 1 if orphans)
#
# Schema delta applied:
#   schema_version: "0.1.0" → "2.0.0"
#   + test_target_ref: TT-NNN  (per §8 mapping table + PoC-01 extensions)
#   + requirement_ref: REQ-NNN (per §8 mapping table + PoC-01 extensions)
#
# Mapping table (D08-TDD-SPEC §8 + PoC-01 extensions for actual IDs):
#
#   TC-001  TT-006  REQ-008   Podcast single page — cover art render
#   TC-002  TT-005  REQ-005   Podcast player — audio element + controls
#   TC-003  TT-016  REQ-018   zemla blog — category display (NEW TT/REQ)
#   TC-004  TT-016  REQ-019   zemla blog — structured editor (NEW REQ)
#   TC-005  TT-016  REQ-020   zemla blog — edit-save round trip (NEW REQ)
#   TC-006  TT-017  REQ-021   Podcast archive — CS heading (NEW TT/REQ)
#   TC-007  TT-017  REQ-021   Podcast archive — CS CTA button
#   TC-008  TT-004  REQ-016   translation.php completeness (CC-005)
#   TC-009  TT-006  REQ-008   Podcast single page — cover art absent
#   TC-010  TT-005  REQ-006   Podcast player — speed hold across seek
#   TC-011  TT-005  REQ-007   Podcast player — skip does not reset speed
#   TC-101  TT-007  REQ-009   CEO blog YouTube embeds all locales
#   TC-102  TT-007  REQ-009   CEO blog — no duplicate References
#   TC-103  TT-007  REQ-009   CEO blog — header layout consistent
#   TC-104  TT-007  REQ-009   CEO blog — JA translation quality
#   TC-201  TT-018  REQ-022   bodyterapie blog — section exists (NEW TT/REQ)
#   TC-202  TT-018  REQ-023   bodyterapie blog — no duplicate blocks (NEW REQ)
#   TC-901  TT-019  REQ-024   Cross-site blog consistency (NEW TT/REQ)
# =============================================================================
from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.exit("ERROR: PyYAML not installed. Run: pip install pyyaml --break-system-packages")

# ── Path resolution ────────────────────────────────────────────────────────────
# Script lives at _config/; testcases.yaml is at 3-fold-path/evidence/testcases.yaml
_SCRIPT_DIR  = Path(__file__).resolve().parent
_REPO_ROOT   = _SCRIPT_DIR.parent
_DEFAULT_IN  = _REPO_ROOT / "3-fold-path" / "evidence" / "testcases.yaml"

# ── v2 mapping table ──────────────────────────────────────────────────────────
# Keys are TC IDs exactly as they appear in testcases.yaml
MAPPING: dict[str, dict[str, str]] = {
    # zemla — podcast episode single (BUG-003, BUG-004, BUG-018)
    "TC-001": {"test_target_ref": "TT-006", "requirement_ref": "REQ-008"},
    "TC-002": {"test_target_ref": "TT-005", "requirement_ref": "REQ-005"},
    "TC-009": {"test_target_ref": "TT-006", "requirement_ref": "REQ-008"},
    "TC-010": {"test_target_ref": "TT-005", "requirement_ref": "REQ-006"},
    "TC-011": {"test_target_ref": "TT-005", "requirement_ref": "REQ-007"},
    # zemla — blog (BUG-005, BUG-006, BUG-007) — TT-016 / REQ-018..020 [new]
    "TC-003": {"test_target_ref": "TT-016", "requirement_ref": "REQ-018"},
    "TC-004": {"test_target_ref": "TT-016", "requirement_ref": "REQ-019"},
    "TC-005": {"test_target_ref": "TT-016", "requirement_ref": "REQ-020"},
    # zemla — podcast archive (BUG-001, BUG-002) — TT-017 / REQ-021 [new]
    "TC-006": {"test_target_ref": "TT-017", "requirement_ref": "REQ-021"},
    "TC-007": {"test_target_ref": "TT-017", "requirement_ref": "REQ-021"},
    # zemla — translation accuracy (BUG-008 / CC-005)
    "TC-008": {"test_target_ref": "TT-004", "requirement_ref": "REQ-016"},
    # mim2000 — CEO blog (BUG-009..014)
    "TC-101": {"test_target_ref": "TT-007", "requirement_ref": "REQ-009"},
    "TC-102": {"test_target_ref": "TT-007", "requirement_ref": "REQ-009"},
    "TC-103": {"test_target_ref": "TT-007", "requirement_ref": "REQ-009"},
    "TC-104": {"test_target_ref": "TT-007", "requirement_ref": "REQ-009"},
    # bodyterapie (BUG-015, BUG-016) — TT-018 / REQ-022..023 [new]
    "TC-201": {"test_target_ref": "TT-018", "requirement_ref": "REQ-022"},
    "TC-202": {"test_target_ref": "TT-018", "requirement_ref": "REQ-023"},
    # cross-site (BUG-017) — TT-019 / REQ-024 [new]
    "TC-901": {"test_target_ref": "TT-019", "requirement_ref": "REQ-024"},
}

TARGET_SCHEMA = "2.0.0"


def _load(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _dump(data: dict[str, Any]) -> str:
    return yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)


def migrate(data: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    """
    Apply v2 migration to loaded YAML data.

    Returns:
        (migrated_data, warnings, errors)
    """
    warnings: list[str] = []
    errors:   list[str] = []

    current_version = str(data.get("schema_version", "0.1.0"))
    if current_version == TARGET_SCHEMA:
        warnings.append(f"schema_version already {TARGET_SCHEMA} — re-applying mapping (idempotent)")

    data = dict(data)  # shallow copy
    data["schema_version"] = TARGET_SCHEMA

    cases: list[dict] = data.get("testcases", [])
    patched = 0
    orphans: list[str] = []

    for case in cases:
        tc_id = case.get("id", "UNKNOWN")
        refs = MAPPING.get(tc_id)
        if refs is None:
            orphans.append(tc_id)
            errors.append(f"ORPHAN: {tc_id} has no mapping entry — add to MAPPING dict")
            continue
        # Insert refs immediately after 'id' key for readability
        # (YAML dump will preserve insertion order for dicts in Python 3.7+)
        for key, val in refs.items():
            case[key] = val
        patched += 1

    if orphans:
        errors.append(f"Total orphan TCs: {len(orphans)} — {', '.join(orphans)}")
    else:
        warnings.append(f"All {patched} testcases patched — 0 orphans")

    return data, warnings, errors


def check_orphans(data: dict[str, Any]) -> list[str]:
    """Return list of TC IDs missing test_target_ref or requirement_ref."""
    orphans = []
    for case in data.get("testcases", []):
        tc_id = case.get("id", "UNKNOWN")
        if not case.get("test_target_ref") or not case.get("requirement_ref"):
            orphans.append(tc_id)
    return orphans


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate testcases.yaml from schema v1 to v2 (adds test_target_ref + requirement_ref)"
    )
    parser.add_argument(
        "--input", "-i",
        default=str(_DEFAULT_IN),
        help=f"Input testcases.yaml (default: {_DEFAULT_IN})",
    )
    parser.add_argument(
        "--out", "-o",
        default=None,
        help="Output path (default: dry-run to stdout)",
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Write back to input file (overrides --out)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate only — exit 1 if any TC missing refs; no write",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: input file not found: {in_path}", file=sys.stderr)
        return 1

    data = _load(in_path)

    # ── Check mode ────────────────────────────────────────────────────────────
    if args.check:
        orphans = check_orphans(data)
        if orphans:
            print(f"FAIL — {len(orphans)} orphan testcase(s): {', '.join(orphans)}", file=sys.stderr)
            return 1
        schema = data.get("schema_version", "?")
        print(f"OK — schema_version={schema}, 0 orphans ({len(data.get('testcases', []))} TCs)")
        return 0

    # ── Migration ────────────────────────────────────────────────────────────
    migrated, warnings, errors = migrate(data)

    for w in warnings:
        print(f"  WARN  {w}", file=sys.stderr)
    for e in errors:
        print(f"  ERROR {e}", file=sys.stderr)

    if errors:
        print("\nMigration aborted — fix errors above before writing.", file=sys.stderr)
        return 1

    out_yaml = _dump(migrated)

    if args.inplace:
        out_path = in_path
    elif args.out:
        out_path = Path(args.out)
    else:
        # Dry-run: print to stdout
        print(out_yaml)
        print(f"\n# Dry-run complete — schema_version bumped to {TARGET_SCHEMA}", file=sys.stderr)
        print(f"# Run with --inplace to write back to {in_path}", file=sys.stderr)
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(out_yaml)

    print(f"Written: {out_path}  (schema_version: {TARGET_SCHEMA})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
