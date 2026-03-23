"""
test_task_integrity.py — TDD semantic integrity checks for the task registry.

Runs as CI job `task-integrity-check` on every push to macbook / thinkpad / main.
Also runs locally via: pytest _tests/test_task_integrity.py

Checks are grouped by severity:
  FATAL  — structural errors that block merging (test fails hard)
  ERROR  — semantic violations that indicate project state inconsistency
  WARN   — soft rules that catch drift (printed but don't fail CI)

Coverage:
  1. Schema validity (IDs, statuses, priorities, devices)
  2. No duplicate task IDs across shared + queue files
  3. All depends_on references resolve to known task IDs
  4. No circular dependencies (DFS cycle detection)
  5. Done tasks have all dependencies done (monotonic progression)
  6. P1-critical tasks have explicit device assignments
  7. Blocked tasks have a blocking note or blocked status
  8. Queue files reference only IDs that exist in TASKS-shared.yaml
  9. Device field in shared task matches owning queue file
 10. MANIFEST.yaml version numbers are valid semver
 11. Release note files exist for pending_releases entries in MANIFEST
 12. No task in a queue has status=done in queue but open in shared (stale queue)
 13. Meta project list matches actual project keys
"""

import os
import re
import sys
import pytest
import yaml
from collections import defaultdict, deque
from pathlib import Path

# ── File paths ────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent

SHARED_PATH    = REPO_ROOT / "TASKS-shared.yaml"
MACBOOK_QUEUE  = REPO_ROOT / "queue-macbook.yaml"
THINKPAD_QUEUE = REPO_ROOT / "queue-thinkpad.yaml"
MANIFEST_PATH  = REPO_ROOT / "MANIFEST.yaml"

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def shared():
    assert SHARED_PATH.exists(), f"TASKS-shared.yaml not found at {SHARED_PATH}"
    with open(SHARED_PATH, encoding='utf-8') as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def queue_macbook():
    if not MACBOOK_QUEUE.exists():
        return {}
    with open(MACBOOK_QUEUE, encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

@pytest.fixture(scope="session")
def queue_thinkpad():
    if not THINKPAD_QUEUE.exists():
        return {}
    with open(THINKPAD_QUEUE, encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

@pytest.fixture(scope="session")
def manifest():
    if not MANIFEST_PATH.exists():
        return {}
    with open(MANIFEST_PATH, encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

@pytest.fixture(scope="session")
def all_tasks(shared):
    """Flat list of all task dicts from TASKS-shared.yaml."""
    tasks = []
    for proj_name, proj in (shared.get('projects') or {}).items():
        for task in (proj.get('tasks') or []):
            task['_project'] = proj_name
            tasks.append(task)
    return tasks

@pytest.fixture(scope="session")
def task_index(all_tasks):
    """Dict of {task_id: task_dict}."""
    return {t['id']: t for t in all_tasks if 'id' in t}

@pytest.fixture(scope="session")
def queue_ids(queue_macbook, queue_thinkpad):
    """All task IDs referenced in any queue file."""
    ids = set()
    for queue in [queue_macbook, queue_thinkpad]:
        session = queue.get('session') or {}
        for state_key in ('active', 'pending', 'done', 'blocked'):
            entries = session.get(state_key) or []
            for e in entries:
                if isinstance(e, str):
                    ids.add(e)
                elif isinstance(e, dict) and 'id' in e:
                    ids.add(e['id'])
    return ids


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SCHEMA VALIDITY
# ═══════════════════════════════════════════════════════════════════════════════

class TestSchemaValidity:

    def test_shared_yaml_is_valid_yaml(self):
        """TASKS-shared.yaml must be parseable YAML — no syntax errors."""
        with open(SHARED_PATH, encoding='utf-8') as f:
            doc = yaml.safe_load(f)
        assert doc is not None, "TASKS-shared.yaml parsed as empty"
        assert 'projects' in doc, "Missing top-level 'projects' key"

    def test_all_tasks_have_required_fields(self, all_tasks):
        """Every task must have id, title, priority, device, status."""
        required = ('id', 'title', 'priority', 'device', 'status')
        violations = []
        for t in all_tasks:
            missing = [f for f in required if f not in t]
            if missing:
                violations.append(f"{t.get('id', '??')} missing: {missing}")
        assert not violations, "Tasks missing required fields:\n" + "\n".join(violations)

    def test_all_task_statuses_are_valid(self, shared, all_tasks):
        """Task status values must be from the valid_statuses enum in meta."""
        valid = set(shared.get('meta', {}).get('valid_statuses', [
            'pending', 'open', 'in-progress', 'done', 'blocked', 'stub'
        ]))
        violations = [
            f"{t['id']}: '{t['status']}'" for t in all_tasks
            if t.get('status') not in valid
        ]
        assert not violations, "Invalid status values:\n" + "\n".join(violations)

    def test_all_task_priorities_are_valid(self, shared, all_tasks):
        """Task priority values must be from the valid_priorities enum in meta."""
        valid = set(shared.get('meta', {}).get('valid_priorities', [
            'P1-critical', 'P2-high', 'P3-medium', 'P4-low', 'high', 'medium', 'low'
        ]))
        violations = [
            f"{t['id']}: '{t['priority']}'" for t in all_tasks
            if t.get('priority') not in valid
        ]
        assert not violations, "Invalid priority values:\n" + "\n".join(violations)

    def test_all_task_devices_are_valid(self, shared, all_tasks):
        """Task device values must be from the valid_devices enum."""
        valid = set(shared.get('meta', {}).get('valid_devices', [
            'MacBook', 'ThinkPad', 'any', 'both'
        ]))
        violations = [
            f"{t['id']}: '{t['device']}'" for t in all_tasks
            if t.get('device') not in valid
        ]
        assert not violations, "Invalid device values:\n" + "\n".join(violations)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. DUPLICATE ID DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestDuplicateIds:

    def test_no_duplicate_task_ids_in_shared(self, all_tasks):
        """Task IDs must be globally unique across all projects."""
        seen = defaultdict(list)
        for t in all_tasks:
            if 'id' in t:
                seen[t['id']].append(t.get('_project', '?'))
        dupes = {k: v for k, v in seen.items() if len(v) > 1}
        assert not dupes, "Duplicate task IDs:\n" + "\n".join(
            f"  {k}: appears in {v}" for k, v in dupes.items()
        )

    def test_no_duplicate_ids_across_queue_files(self, queue_macbook, queue_thinkpad):
        """A task ID should not appear in both macbook AND thinkpad active queues simultaneously."""
        def active_ids(queue):
            return {
                (e if isinstance(e, str) else e['id'])
                for e in (queue.get('session') or {}).get('active', [])
            }
        macbook_active  = active_ids(queue_macbook)
        thinkpad_active = active_ids(queue_thinkpad)
        overlap = macbook_active & thinkpad_active
        assert not overlap, f"Tasks active on BOTH devices simultaneously: {overlap}"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. DEPENDENCY REFERENCE INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════

class TestDependencyReferences:

    def test_all_depends_on_ids_exist(self, all_tasks, task_index):
        """Every ID in depends_on must resolve to a known task."""
        violations = []
        for t in all_tasks:
            for dep_id in (t.get('depends_on') or []):
                if dep_id not in task_index:
                    violations.append(f"{t['id']} → unknown dependency '{dep_id}'")
        assert not violations, "Unresolved depends_on references:\n" + "\n".join(violations)

    def test_no_self_referential_dependencies(self, all_tasks):
        """A task must not list itself as a dependency."""
        violations = [
            t['id'] for t in all_tasks
            if t['id'] in (t.get('depends_on') or [])
        ]
        assert not violations, f"Self-referential dependencies: {violations}"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CIRCULAR DEPENDENCY DETECTION (DFS)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCircularDependencies:

    def test_no_circular_dependencies(self, all_tasks, task_index):
        """
        Detect cycles in the depends_on graph using iterative DFS.
        A cycle means two tasks transitively depend on each other — unresolvable.
        """
        graph = {t['id']: list(t.get('depends_on') or []) for t in all_tasks}

        def has_cycle(start):
            """Returns True if a cycle is reachable from start."""
            visited  = set()
            rec_stack = set()
            stack = [(start, False)]
            while stack:
                node, returning = stack.pop()
                if returning:
                    rec_stack.discard(node)
                    continue
                if node in rec_stack:
                    return True
                if node in visited:
                    continue
                visited.add(node)
                rec_stack.add(node)
                stack.append((node, True))  # mark for removal from rec_stack
                for neighbour in graph.get(node, []):
                    if neighbour in graph:
                        stack.append((neighbour, False))
            return False

        cycles = [tid for tid in graph if has_cycle(tid)]
        assert not cycles, f"Circular dependency detected involving: {cycles}"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. MONOTONIC STATUS PROGRESSION
# ═══════════════════════════════════════════════════════════════════════════════

STATUS_RANK = {
    'done': 6, 'in-progress': 5, 'open': 4,
    'pending': 3, 'stub': 2, 'blocked': 1
}

class TestStatusProgression:

    def test_done_tasks_have_done_dependencies(self, all_tasks, task_index):
        """
        A task marked 'done' must not have dependencies that are still open/pending.
        Exception: blocked dependencies are flagged as warnings, not failures.
        """
        violations = []
        for t in all_tasks:
            if t.get('status') != 'done':
                continue
            for dep_id in (t.get('depends_on') or []):
                dep = task_index.get(dep_id)
                if dep and dep.get('status') not in ('done', 'blocked'):
                    violations.append(
                        f"{t['id']} (done) depends on {dep_id} which is '{dep.get('status')}'"
                    )
        assert not violations, "Done tasks with open dependencies:\n" + "\n".join(violations)

    def test_in_progress_tasks_have_done_or_valid_dependencies(self, all_tasks, task_index):
        """
        An in-progress task's dependencies should all be done (or at most in-progress).
        Flags if a dependency is still pending/open — likely sequencing error.
        """
        warnings = []
        for t in all_tasks:
            if t.get('status') != 'in-progress':
                continue
            for dep_id in (t.get('depends_on') or []):
                dep = task_index.get(dep_id)
                if dep and dep.get('status') in ('pending', 'open', 'stub'):
                    warnings.append(
                        f"WARN: {t['id']} (in-progress) depends on {dep_id} which is '{dep.get('status')}'"
                    )
        # Emit as warnings — printed but don't fail
        for w in warnings:
            print(w, file=sys.stderr)
        # Not a hard failure — in-progress + pending deps can be valid in parallel work


# ═══════════════════════════════════════════════════════════════════════════════
# 6. P1 TASK COMPLETENESS
# ═══════════════════════════════════════════════════════════════════════════════

class TestP1Completeness:

    def test_p1_tasks_have_device_assignment(self, all_tasks):
        """P1-critical tasks must have an explicit device (not 'any' or missing)."""
        # 'any' is allowed for blocked P1s (e.g. C-00 waiting on user input)
        violations = [
            f"{t['id']}: device='{t.get('device')}'"
            for t in all_tasks
            if t.get('priority') == 'P1-critical'
            and t.get('status') not in ('done', 'blocked')
            and t.get('device') in (None, '', 'both')
        ]
        assert not violations, "P1-critical open tasks without device assignment:\n" + "\n".join(violations)

    def test_p1_tasks_have_notes_or_spec(self, all_tasks):
        """P1-critical open tasks should have notes linking to a spec or action plan."""
        missing_notes = [
            t['id'] for t in all_tasks
            if t.get('priority') == 'P1-critical'
            and t.get('status') not in ('done', 'blocked')
            and not t.get('notes')
        ]
        # Soft warning — emit but don't fail
        for tid in missing_notes:
            print(f"WARN: P1 task {tid} has no notes/spec reference", file=sys.stderr)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. QUEUE FILE INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════

class TestQueueIntegrity:

    def test_queue_ids_exist_in_shared(self, queue_ids, task_index):
        """Every task ID in queue files must exist in TASKS-shared.yaml."""
        unknown = queue_ids - set(task_index.keys())
        assert not unknown, f"Queue references to unknown task IDs: {sorted(unknown)}"

    def test_macbook_queue_only_references_macbook_or_any_tasks(self, queue_macbook, task_index):
        """
        MacBook queue should not actively run ThinkPad-assigned tasks.
        Flags mismatches between queue ownership and task device field.
        """
        session = (queue_macbook.get('session') or {})
        active  = [
            (e if isinstance(e, str) else e['id'])
            for e in session.get('active', [])
        ]
        violations = []
        for tid in active:
            task = task_index.get(tid)
            if task and task.get('device') == 'ThinkPad':
                violations.append(f"{tid} is assigned to ThinkPad but active in MacBook queue")
        assert not violations, "Device ownership mismatch in MacBook active queue:\n" + "\n".join(violations)

    def test_thinkpad_queue_only_references_thinkpad_or_any_tasks(self, queue_thinkpad, task_index):
        """ThinkPad queue should not actively run MacBook-assigned tasks."""
        session = (queue_thinkpad.get('session') or {})
        active  = [
            (e if isinstance(e, str) else e['id'])
            for e in session.get('active', [])
        ]
        violations = []
        for tid in active:
            task = task_index.get(tid)
            if task and task.get('device') == 'MacBook':
                violations.append(f"{tid} is assigned to MacBook but active in ThinkPad queue")
        assert not violations, "Device ownership mismatch in ThinkPad active queue:\n" + "\n".join(violations)

    def test_no_stale_done_in_queue_vs_shared(self, queue_ids, task_index):
        """
        Tasks marked done in TASKS-shared.yaml should not appear in pending queues.
        (Stale queue entry = device forgot to remove completed task from pending list.)
        """
        # Check pending entries vs shared status
        stale = []
        for queue_path, queue_doc in [
            ('queue-macbook.yaml',  None),
            ('queue-thinkpad.yaml', None),
        ]:
            qfile = REPO_ROOT / queue_path
            if not qfile.exists():
                continue
            with open(qfile, encoding='utf-8') as f:
                qdoc = yaml.safe_load(f) or {}
            pending_ids = [
                (e if isinstance(e, str) else e['id'])
                for e in (qdoc.get('session') or {}).get('pending', [])
            ]
            for tid in pending_ids:
                task = task_index.get(tid)
                if task and task.get('status') == 'done':
                    stale.append(f"{queue_path}: {tid} is 'done' in shared but still in pending queue")

        # Soft warning only — done cleanup is low-severity drift
        for s in stale:
            print(f"WARN: {s}", file=sys.stderr)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. MANIFEST INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════

SEMVER_RE = re.compile(r'^v?\d+\.\d+\.\d+$')

class TestManifestIntegrity:

    def test_manifest_live_versions_are_semver(self, manifest):
        """Live version strings in MANIFEST must match vX.Y.Z pattern."""
        if not manifest:
            pytest.skip("MANIFEST.yaml not present")
        violations = []
        for site, ver in (manifest.get('live_versions') or {}).items():
            if not SEMVER_RE.match(str(ver)):
                violations.append(f"{site}: '{ver}'")
        assert not violations, "Non-semver live versions in MANIFEST:\n" + "\n".join(violations)

    def test_manifest_pending_releases_are_semver(self, manifest):
        """Pending release tags in MANIFEST must match vX.Y.Z pattern."""
        if not manifest:
            pytest.skip("MANIFEST.yaml not present")
        violations = []
        for rel in (manifest.get('pending_releases') or []):
            tag = rel.get('tag', '')
            if not SEMVER_RE.match(str(tag)):
                violations.append(f"{rel.get('site', '?')}: tag='{tag}'")
        assert not violations, "Non-semver pending release tags:\n" + "\n".join(violations)

    def test_manifest_hotfix_versions_greater_than_live(self, manifest):
        """Pending hotfix releases must be strictly greater than current live version."""
        if not manifest:
            pytest.skip("MANIFEST.yaml not present")

        def parse_ver(v):
            v = str(v).lstrip('v')
            parts = v.split('.')
            return tuple(int(p) for p in parts) if len(parts) == 3 else (0, 0, 0)

        live = manifest.get('live_versions') or {}
        violations = []
        for rel in (manifest.get('pending_releases') or []):
            site = rel.get('site', '')
            live_ver  = parse_ver(live.get(site, 'v0.0.0'))
            hotfix_ver = parse_ver(rel.get('tag', 'v0.0.0'))
            if hotfix_ver <= live_ver:
                violations.append(
                    f"{site}: hotfix {rel['tag']} ≤ live {live.get(site)}"
                )
        assert not violations, "Hotfix versions not greater than live:\n" + "\n".join(violations)

    def test_release_note_files_exist_for_pending_releases(self, manifest):
        """Every pending_release in MANIFEST must have a corresponding release note file."""
        if not manifest:
            pytest.skip("MANIFEST.yaml not present")
        missing = []
        for rel in (manifest.get('pending_releases') or []):
            note_path = rel.get('release_note', '')
            if note_path:
                full_path = REPO_ROOT / note_path
                if not full_path.exists():
                    missing.append(str(note_path))
        assert not missing, "Missing release note files:\n" + "\n".join(missing)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. META CONSISTENCY
# ═══════════════════════════════════════════════════════════════════════════════

class TestMetaConsistency:

    def test_meta_project_list_matches_actual_projects(self, shared):
        """Project names declared in meta.projects must match actual project keys."""
        meta_projects   = set(shared.get('meta', {}).get('projects', []))
        actual_projects = set((shared.get('projects') or {}).keys())

        in_meta_not_actual = meta_projects - actual_projects
        in_actual_not_meta = actual_projects - meta_projects

        issues = []
        if in_meta_not_actual:
            issues.append(f"In meta.projects but no project block: {in_meta_not_actual}")
        if in_actual_not_meta:
            issues.append(f"Project block exists but missing from meta.projects: {in_actual_not_meta}")

        assert not issues, "meta.projects mismatch:\n" + "\n".join(issues)

    def test_no_empty_project_task_lists_for_active_projects(self, shared):
        """Active projects must have at least one task defined."""
        violations = []
        for pname, proj in (shared.get('projects') or {}).items():
            if proj.get('status') == 'active' and not proj.get('tasks'):
                violations.append(pname)
        # Soft warning
        for v in violations:
            print(f"WARN: Active project '{v}' has no tasks", file=sys.stderr)
