#!/usr/bin/env python3
"""
merge-tasks.py — Semantic YAML merge driver for TASKS-shared.yaml
Registered via .gitattributes: TASKS-shared.yaml merge=tasks-merge

Git calls: merge-tasks.py %O %A %B %L
  %O = base (common ancestor)
  %A = ours  (current branch — file to be written back)
  %B = theirs (incoming branch)
  %L = conflict marker size (ignored — we resolve all conflicts)

Resolution rules (field-level, per task ID):
  - Task IDs present in only one side → keep that task (union)
  - Same task ID in both sides:
      status       → monotonic winner (done > in-progress > open > pending > blocked)
                     if equal, ours wins
      priority     → theirs wins (shared authority / most recent sprint decision)
      title        → theirs wins
      notes        → theirs wins (last writer has latest spec)
      tags         → union of both tag lists (deduplicated)
      depends_on   → union (never remove a dependency silently)
      device       → ours wins (device assignment not changed by remote)
      last_modified_by / last_modified_at → theirs wins

Returns: exit 0 on clean merge, exit 1 on unresolvable structural error.
"""

import sys
import os
import yaml
import copy
from datetime import datetime

# ── Status monotonic ordering ─────────────────────────────────────────────────
STATUS_ORDER = {
    'done':        6,
    'in-progress': 5,
    'open':        4,
    'pending':     3,
    'stub':        2,
    'blocked':     1,
}

def status_rank(s):
    return STATUS_ORDER.get(s, 0)


# ── Deep task merge ───────────────────────────────────────────────────────────

def merge_task(base_task, ours_task, theirs_task):
    """
    Merge two versions of a task (ours + theirs) with base as reference.
    Returns merged task dict.
    """
    merged = copy.deepcopy(ours_task)

    # status: monotonic — highest rank wins; ours breaks tie
    our_rank    = status_rank(ours_task.get('status', 'pending'))
    their_rank  = status_rank(theirs_task.get('status', 'pending'))
    if their_rank > our_rank:
        merged['status'] = theirs_task['status']

    # priority / title / notes: theirs wins (shared authority)
    for field in ('priority', 'title', 'notes'):
        if field in theirs_task:
            merged[field] = theirs_task[field]

    # tags: union, deduplicated, sorted
    our_tags    = set(ours_task.get('tags', []))
    their_tags  = set(theirs_task.get('tags', []))
    merged['tags'] = sorted(our_tags | their_tags)

    # depends_on: union (never silently drop a dependency)
    our_deps    = set(ours_task.get('depends_on', []))
    their_deps  = set(theirs_task.get('depends_on', []))
    union_deps  = sorted(our_deps | their_deps)
    if union_deps:
        merged['depends_on'] = union_deps
    elif 'depends_on' in merged:
        del merged['depends_on']

    # device: ours wins (local assignment authority)
    # (already set from copy.deepcopy(ours_task))

    # metadata fields: theirs wins
    for field in ('last_modified_by', 'last_modified_at'):
        if field in theirs_task:
            merged[field] = theirs_task[field]

    return merged


# ── Project-level merge ───────────────────────────────────────────────────────

def index_tasks(task_list):
    """Build {id: task} index from a list of task dicts."""
    return {t['id']: t for t in task_list if 'id' in t}


def merge_project_tasks(base_tasks, ours_tasks, theirs_tasks):
    """
    Merge three task lists by ID.
    Union of IDs; per-task merge when same ID appears in both ours and theirs.
    """
    base   = index_tasks(base_tasks   or [])
    ours   = index_tasks(ours_tasks   or [])
    theirs = index_tasks(theirs_tasks or [])

    all_ids = set(ours.keys()) | set(theirs.keys())
    merged_tasks = []

    # Preserve ours ordering first, then append theirs-only additions
    seen = set()
    for tid in list(ours.keys()) + [k for k in theirs.keys() if k not in ours]:
        if tid in seen:
            continue
        seen.add(tid)

        if tid in ours and tid not in theirs:
            merged_tasks.append(ours[tid])          # ours only → keep
        elif tid in theirs and tid not in ours:
            merged_tasks.append(theirs[tid])         # theirs only → keep
        else:
            base_t = base.get(tid, {})
            merged_tasks.append(merge_task(base_t, ours[tid], theirs[tid]))

    return merged_tasks


def merge_project(base_proj, ours_proj, theirs_proj):
    """Merge a single project block."""
    merged = copy.deepcopy(ours_proj)

    # description / status: theirs wins
    for field in ('description', 'status', 'reference_docs', 'sprint_iteration'):
        if field in theirs_proj:
            merged[field] = theirs_proj[field]

    # current_versions: theirs wins (shared source of truth for live deploys)
    if 'current_versions' in theirs_proj:
        merged['current_versions'] = theirs_proj['current_versions']

    # tasks: semantic merge
    merged['tasks'] = merge_project_tasks(
        base_proj.get('tasks', []),
        ours_proj.get('tasks', []),
        theirs_proj.get('tasks', [])
    )

    return merged


# ── Top-level document merge ──────────────────────────────────────────────────

def merge_documents(base_doc, ours_doc, theirs_doc):
    """Merge full TASKS-shared.yaml documents."""
    merged = copy.deepcopy(ours_doc)

    # meta: theirs wins for schema_version + valid_* enums; ours for last_updated/updated_by
    if 'meta' in theirs_doc:
        merged.setdefault('meta', {})
        for field in ('schema_version', 'valid_statuses', 'valid_priorities', 'valid_devices'):
            if field in theirs_doc['meta']:
                merged['meta'][field] = theirs_doc['meta'][field]
        # projects list: union
        ours_projects   = set(ours_doc.get('meta', {}).get('projects', []))
        theirs_projects = set(theirs_doc.get('meta', {}).get('projects', []))
        merged['meta']['projects'] = sorted(ours_projects | theirs_projects)
        merged['meta']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        merged['meta']['updated_by']   = 'merge-tasks.py (semantic merge)'

    # projects: merge per-project by key
    ours_projects   = ours_doc.get('projects',   {})
    theirs_projects = theirs_doc.get('projects',  {})
    base_projects   = base_doc.get('projects',    {})

    all_project_names = set(ours_projects.keys()) | set(theirs_projects.keys())
    merged_projects = {}

    for pname in all_project_names:
        if pname in ours_projects and pname not in theirs_projects:
            merged_projects[pname] = ours_projects[pname]
        elif pname in theirs_projects and pname not in ours_projects:
            merged_projects[pname] = theirs_projects[pname]
        else:
            merged_projects[pname] = merge_project(
                base_projects.get(pname, {}),
                ours_projects[pname],
                theirs_projects[pname]
            )

    merged['projects'] = merged_projects
    return merged


# ── YAML I/O ─────────────────────────────────────────────────────────────────

def load_yaml(path):
    if not path or not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def dump_yaml(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f,
                  default_flow_style=False,
                  allow_unicode=True,
                  sort_keys=False,
                  width=120)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 4:
        print("Usage: merge-tasks.py <base> <ours> <theirs> [marker_size]", file=sys.stderr)
        sys.exit(1)

    base_path  = sys.argv[1]  # %O
    ours_path  = sys.argv[2]  # %A — git writes merged result back here
    theirs_path = sys.argv[3] # %B

    try:
        base_doc   = load_yaml(base_path)
        ours_doc   = load_yaml(ours_path)
        theirs_doc = load_yaml(theirs_path)
    except yaml.YAMLError as e:
        print(f"merge-tasks: YAML parse error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        merged = merge_documents(base_doc, ours_doc, theirs_doc)
    except Exception as e:
        print(f"merge-tasks: merge error: {e}", file=sys.stderr)
        sys.exit(1)

    # Write merged result back to %A (ours path — git reads this)
    dump_yaml(merged, ours_path)
    print(f"merge-tasks: clean merge → {ours_path}", file=sys.stderr)
    sys.exit(0)


if __name__ == '__main__':
    main()
