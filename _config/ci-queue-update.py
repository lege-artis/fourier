#!/usr/bin/env python3
"""
ci-queue-update.py — CI-authored task status updater (GW-009)

Reads TASKS-shared.yaml, updates specified task IDs to a target status,
and writes the file back.  Intended to be called from GitHub Actions after
a CI gate passes (e.g. all PLT jobs green → close PLT-001..005).

Usage:
    python _config/ci-queue-update.py \\
        --tasks PLT-001,PLT-002,PLT-003,PLT-004,PLT-005 \\
        --status done \\
        [--completed 2026-04-09] \\
        [--dry-run]

Arguments:
    --tasks       Comma-separated list of task IDs to update
    --status      New status value (must be a valid status from TASKS-shared.yaml meta)
    --completed   Optional: YYYY-MM-DD completion date (defaults to today)
    --dry-run     Print changes but do not write
    --file        Path to TASKS-shared.yaml (default: TASKS-shared.yaml relative to repo root)

Exit codes:
    0 = success (or --dry-run with no errors)
    1 = one or more task IDs not found
    2 = validation error

Notes:
    - Only updates tasks whose current status is NOT already done / deferred.
    - Appends a note with CI context if GITHUB_RUN_ID / GITHUB_WORKFLOW env vars are set.
    - Does NOT run the integrity gate — caller is responsible for running pytest.
    - Respects the semantic merge contract: modifies status/completed/notes only;
      never removes fields already present.
"""

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path


# ── Valid statuses (mirrors TASKS-shared.yaml meta.valid_statuses) ────────────
VALID_STATUSES = {
    "pending", "open", "in-progress", "done",
    "blocked", "stub", "deferred",
}

# Statuses that are considered terminal (skip update if already in one of these)
TERMINAL_STATUSES = {"done", "deferred"}

# ── Argument parsing ──────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Update task statuses in TASKS-shared.yaml from CI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:")[0].strip(),
    )
    ap.add_argument(
        "--tasks", required=True,
        help="Comma-separated task IDs, e.g. PLT-001,PLT-002",
    )
    ap.add_argument(
        "--status", required=True,
        choices=sorted(VALID_STATUSES),
        help="Target status to set",
    )
    ap.add_argument(
        "--completed",
        default=str(date.today()),
        help="Completion date (YYYY-MM-DD, default: today)",
    )
    ap.add_argument(
        "--note",
        default=None,
        help="Optional note to append to the task's notes field",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Print changes without writing",
    )
    ap.add_argument(
        "--file",
        default=None,
        help="Path to TASKS-shared.yaml (default: auto-locate from script dir)",
    )
    return ap.parse_args()


# ── File location ─────────────────────────────────────────────────────────────

def find_tasks_file(override: str | None) -> Path:
    if override:
        p = Path(override)
        if not p.exists():
            print(f"[ERROR] --file path not found: {p}", file=sys.stderr)
            sys.exit(2)
        return p
    # Script lives in _config/ — project root is one level up
    repo_root = Path(__file__).parent.parent
    p = repo_root / "TASKS-shared.yaml"
    if not p.exists():
        # Try cwd
        p = Path("TASKS-shared.yaml")
    if not p.exists():
        print(
            "[ERROR] Cannot locate TASKS-shared.yaml. "
            "Run from repo root or pass --file.",
            file=sys.stderr,
        )
        sys.exit(2)
    return p


# ── CI context note ───────────────────────────────────────────────────────────

def build_ci_note(extra_note: str | None) -> str:
    """Build a note string with GitHub Actions context if available."""
    parts = []
    run_id = os.environ.get("GITHUB_RUN_ID")
    workflow = os.environ.get("GITHUB_WORKFLOW")
    sha = os.environ.get("GITHUB_SHA", "")[:8]
    if workflow:
        parts.append(f"CI: {workflow}")
    if run_id:
        parts.append(f"run #{run_id}")
    if sha:
        parts.append(f"commit {sha}")
    if extra_note:
        parts.append(extra_note)
    return "Auto-closed by ci-queue-update.py. " + "; ".join(parts) if parts else (
        extra_note or "Auto-closed by ci-queue-update.py."
    )


# ── Per-task patch (line-oriented, preserves indentation) ────────────────────

def patch_task(
    lines: list[str],
    task_id: str,
    new_status: str,
    completed: str,
    note: str,
    dry_run: bool,
) -> tuple[bool, list[str]]:
    """
    Locate the task block for task_id in lines and update its status/completed/notes.
    Returns (changed: bool, updated_lines: list[str]).

    Strategy:
      - Find line matching `- id: <task_id>`
      - Scan forward to find `status:` line in the same block
        (stops when a new task marker or section boundary is reached)
      - Replace status value
      - If new_status == 'done': add/update `completed:` after status
      - Append/update `notes:` line
    """
    # Regex: matches '      - id: PLT-001' style lines
    id_pat = re.compile(r'^(\s+)-\s+id:\s+' + re.escape(task_id) + r'\s*$')
    status_pat = re.compile(r'^(\s+)status:\s+(\S+)')
    completed_pat = re.compile(r'^(\s+)completed:\s+')
    new_id_pat = re.compile(r'^\s+-\s+id:\s+\S')
    section_pat = re.compile(r'^\s{0,6}\S')  # unindented or low-indent = new section

    # Find task start
    task_start: int | None = None
    for i, line in enumerate(lines):
        if id_pat.match(line):
            task_start = i
            break

    if task_start is None:
        return False, lines

    # Detect indentation of the block (from the `- id:` line)
    task_indent = len(lines[task_start]) - len(lines[task_start].lstrip())
    field_indent = " " * (task_indent + 2)

    # Scan the block (from task_start to next peer task or section)
    block_end = len(lines)
    for i in range(task_start + 1, len(lines)):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())
        # A new task at same or lower indent level closes the block
        if indent <= task_indent and new_id_pat.match(line):
            block_end = i
            break
        # A section heading (very low indent, not a task field)
        if indent <= task_indent and not line.startswith(" " * task_indent):
            block_end = i
            break

    block = lines[task_start:block_end]

    # Find current status in block
    status_line_idx: int | None = None
    current_status: str | None = None
    for rel_i, line in enumerate(block):
        m = status_pat.match(line)
        if m:
            status_line_idx = rel_i
            current_status = m.group(2).rstrip()
            break

    if status_line_idx is None:
        print(f"  [WARN] {task_id}: no status: field found in block — skipping")
        return False, lines

    if current_status in TERMINAL_STATUSES:
        print(
            f"  [SKIP] {task_id}: already {current_status} — no change needed"
        )
        return False, lines

    if dry_run:
        print(
            f"  [DRY-RUN] {task_id}: status {current_status!r} -> {new_status!r}"
            + (f", completed: {completed}" if new_status == "done" else "")
        )
        return True, lines  # signal "would change" but don't modify

    # Perform update on block lines
    m = status_pat.match(block[status_line_idx])
    indent_str = m.group(1)
    block[status_line_idx] = f"{indent_str}status: {new_status}\n"
    print(f"  [OK] {task_id}: status {current_status!r} -> {new_status!r}")

    # Insert/replace completed: after status line
    if new_status == "done":
        completed_idx: int | None = None
        for rel_i, line in enumerate(block):
            if completed_pat.match(line):
                completed_idx = rel_i
                break
        completed_line = f"{field_indent}completed: \"{completed}\"\n"
        if completed_idx is not None:
            block[completed_idx] = completed_line
        else:
            block.insert(status_line_idx + 1, completed_line)
            print(f"  [OK] {task_id}: inserted completed: {completed}")

    # Append note to notes field (or add notes field if absent)
    notes_start_idx: int | None = None
    notes_pat = re.compile(r'^(\s+)notes:\s*')
    for rel_i, line in enumerate(block):
        if notes_pat.match(line):
            notes_start_idx = rel_i
            break

    if note:
        if notes_start_idx is not None:
            # Append to existing notes inline value (single-line only)
            existing = block[notes_start_idx]
            m_notes = re.match(r'^(\s+notes:\s+)"(.*)"', existing)
            if m_notes:
                combined = f'{m_notes.group(1)}"{m_notes.group(2)} {note}"\n'
                block[notes_start_idx] = combined
            # Multi-line notes block: append a new line at end of block
            else:
                # Find end of notes block (indented further than field_indent)
                notes_end = notes_start_idx + 1
                note_indent = len(field_indent) + 2
                while notes_end < len(block):
                    line = block[notes_end]
                    if line.strip() and len(line) - len(line.lstrip()) < note_indent:
                        break
                    notes_end += 1
                block.insert(notes_end, f'{" " * note_indent}{note}\n')
        else:
            # Add notes field before end of block
            block.append(f'{field_indent}notes: "{note}"\n')

    # Rebuild lines
    new_lines = lines[:task_start] + block + lines[block_end:]
    return True, new_lines


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    task_ids = [t.strip() for t in args.tasks.split(",") if t.strip()]
    if not task_ids:
        print("[ERROR] --tasks is empty", file=sys.stderr)
        sys.exit(2)

    tasks_file = find_tasks_file(args.file)
    print(f"[INFO] Target file: {tasks_file}")
    print(f"[INFO] Tasks      : {', '.join(task_ids)}")
    print(f"[INFO] New status : {args.status}")
    if args.status == "done":
        print(f"[INFO] Completed  : {args.completed}")
    if args.dry_run:
        print("[INFO] --dry-run active — no writes will occur")
    print()

    note = build_ci_note(args.note)
    with open(tasks_file, encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines(keepends=True)

    not_found: list[str] = []
    changed_count = 0

    for task_id in task_ids:
        changed, lines = patch_task(
            lines, task_id, args.status, args.completed, note, args.dry_run
        )
        if changed:
            changed_count += 1
        # Check presence even if unchanged (already done = not "not found")
        id_pat = re.compile(r'^\s+-\s+id:\s+' + re.escape(task_id) + r'\s*$')
        if not any(id_pat.match(ln) for ln in lines):
            not_found.append(task_id)
            print(f"  [ERROR] {task_id}: not found in {tasks_file}")

    print()
    if not_found:
        print(f"[FAIL] {len(not_found)} task(s) not found: {', '.join(not_found)}")
        sys.exit(1)

    if args.dry_run:
        print(f"[DRY-RUN] {changed_count} task(s) would be updated. No file written.")
        return

    if changed_count == 0:
        print("[INFO] No changes needed — all tasks already in target/terminal status.")
        return

    # Write back
    with open(tasks_file, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"[OK] {changed_count} task(s) updated in {tasks_file}")


if __name__ == "__main__":
    main()
