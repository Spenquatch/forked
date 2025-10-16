#!/usr/bin/env python3
"""
Generate project-wide status rollup with dependency-aware feature ordering.
- Reads feature dependencies from overview.md files
- Parses roadmap priorities from roadmap/now-next-later.md
- Performs topological sort respecting dependencies and priorities
- Outputs status/current.json
"""
from __future__ import annotations
import json
import datetime as dt
import heapq
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]  # project-handbook/
SPRINTS = ROOT / 'sprints'
FEATURES = ROOT / 'features'
ROADMAP = ROOT / 'roadmap'
STATUS_DIR = ROOT / 'status'

# Stage priority mapping (lower = higher priority)
STAGE_PRIORITY = {
    "in-progress": 0,
    "in progress": 0,
    "active": 0,
    "doing": 0,
    "blocked": 1,
    "review": 2,
    "planning": 3,
    "planned": 3,
    "proposed": 4,
    "concept": 4,
    "backlog": 5,
    "todo": 5,
    "hold": 6,
    "on-hold": 6,
    "done": 7,
    "completed": 7,
    "complete": 7,
    "live": 8,
    "released": 8,
    "deprecated": 9,
    "unknown": 10,
}

CYCLE_PRIORITY = {"now": 0, "next": 1, "later": 2}

def _strip(val: str) -> str:
    return val.strip().strip('"').strip("'")

def parse_map(text: str) -> dict:
    """Parse simple YAML-like key:value mappings."""
    data: dict = {}
    lines = text.splitlines()
    i, n = 0, len(lines)
    def is_kv(s: str) -> bool:
        return ':' in s and not s.lstrip().startswith('-')
    while i < n:
        line = lines[i].rstrip('\n')
        if not line.strip():
            i += 1; continue
        if not line.startswith(' ') and is_kv(line):
            k, v = line.split(':', 1)
            k = k.strip(); v = v.strip()
            if v == '':
                if i+1 < n and lines[i+1].lstrip().startswith('- '):
                    i += 1
                    arr = []
                    while i < n and lines[i].startswith('  - '):
                        arr.append(_strip(lines[i].split('- ',1)[1]))
                        i += 1
                    data[k] = arr; continue
                elif i+1 < n and lines[i+1].startswith('  '):
                    i += 1
                    sub = {}
                    while i < n and lines[i].startswith('  ') and is_kv(lines[i].strip()):
                        sk, sv = lines[i].strip().split(':',1)
                        sub[_strip(sk)] = _strip(sv)
                        i += 1
                    data[k] = sub; continue
                else:
                    data[k] = ''
            else:
                data[k] = _strip(v)
            i += 1; continue
        i += 1
    return data

def parse_task_list(text: str) -> list[dict]:
    """Parse YAML-like task list format."""
    items = []
    cur = None
    listkey = None
    for raw in text.splitlines():
        if raw.startswith('- '):
            if cur is not None: items.append(cur)
            cur = {}; listkey = None
            rem = raw[2:].strip()
            if rem and ':' in rem:
                k,v = rem.split(':',1)
                cur[_strip(k)] = _strip(v)
            continue
        if cur is None: continue
        if raw.startswith('  ') and ':' in raw and not raw.strip().startswith('- '):
            k, v = raw.strip().split(':',1)
            k = _strip(k); v = v.strip()
            if v == '':
                listkey = k; cur[k] = []
            else:
                cur[k] = _strip(v); listkey = None
            continue
        if raw.startswith('    - ') and listkey:
            cur[listkey].append(_strip(raw.split('- ',1)[1]))
            continue
        listkey = None
    if cur is not None: items.append(cur)
    return items

def parse_front_matter(text: str) -> dict:
    """Extract front matter from markdown file."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return {}
    try:
        end = lines[1:].index('---') + 1
    except ValueError:
        return {}
    fm = {}
    for line in lines[1:end]:
        if ':' in line:
            k, v = line.split(':', 1)
            k = k.strip()
            v = v.strip()
            # Handle lists in front matter
            if v.startswith('[') and v.endswith(']'):
                try:
                    fm[k] = json.loads(v)
                except json.JSONDecodeError:
                    # Fallback to string splitting
                    parts = [p.strip().strip('"\'') for p in v[1:-1].split(',')]
                    fm[k] = [p for p in parts if p]
            else:
                fm[k] = v
    return fm

def parse_dependency_features(raw: Any) -> List[str]:
    """Extract feature dependencies from front matter."""
    if raw is None:
        return []
    if isinstance(raw, list):
        candidates = raw
    else:
        text = str(raw).strip()
        if not text:
            return []
        if text.startswith('[') and text.endswith(']'):
            try:
                candidates = json.loads(text)
            except json.JSONDecodeError:
                parts = [seg.strip() for seg in text[1:-1].split(',')]
                candidates = [p.strip('"\'') for p in parts if p]
        else:
            candidates = [text]

    features = []
    for entry in candidates:
        if isinstance(entry, str):
            cleaned = entry.strip()
            # Extract feature name from "feature:name" format
            if cleaned.lower().startswith('feature:'):
                features.append(cleaned.split(':', 1)[1].strip())
    return features

def load_roadmap_priorities() -> Dict[str, Tuple[int, int]]:
    """Load feature priorities from roadmap/now-next-later.md."""
    path = ROADMAP / 'now-next-later.md'
    priorities = {}
    if not path.exists():
        return priorities

    try:
        text = path.read_text(encoding='utf-8')
    except:
        return priorities

    section = None
    order_in_section = 0

    for line in text.splitlines():
        line = line.strip()
        lowered = line.lower()

        # Check for section headers
        if lowered in CYCLE_PRIORITY:
            section = lowered
            order_in_section = 0
            continue

        # Parse feature entries
        if section and line.startswith('-'):
            content = line[1:].strip()
            # Extract feature name before colon
            feature_text, _, _ = content.partition(':')
            feature_key = feature_text.strip()
            if feature_key:
                priorities[feature_key] = (CYCLE_PRIORITY[section], order_in_section)
                order_in_section += 1

    return priorities

def compute_feature_priority(
    feature: str,
    status_info: Dict[str, Any],
    index: int,
    roadmap_priorities: Dict[str, Tuple[int, int]],
    dependent_count: int,
) -> Tuple[int, int, int, int, int, str]:
    """Compute multi-level priority tuple for feature sorting."""

    # Check if feature has now/next items in its status
    now_items = status_info.get('now', []) if isinstance(status_info, dict) else []
    next_items = status_info.get('next', []) if isinstance(status_info, dict) else []

    # Get stage and normalize it
    stage = (status_info.get('stage') or 'unknown') if isinstance(status_info, dict) else 'unknown'
    stage_key = stage.lower().strip().replace('-', ' ')

    # Determine cycle rank from roadmap or status
    if feature in roadmap_priorities:
        cycle_rank, cycle_position = roadmap_priorities[feature]
    else:
        # Fallback to status-based priority
        if now_items:
            cycle_rank = CYCLE_PRIORITY['now']
        elif next_items:
            cycle_rank = CYCLE_PRIORITY['next']
        else:
            cycle_rank = CYCLE_PRIORITY['later']
        cycle_position = index

    # Negative dependent count (more dependents = higher priority)
    dependent_rank = -dependent_count

    # Stage rank
    stage_rank = STAGE_PRIORITY.get(stage_key, 10)

    return (cycle_rank, cycle_position, dependent_rank, stage_rank, index, feature)

def topologically_sort_features(
    features: List[str],
    dependencies: Dict[str, List[str]],
    priority_hints: Dict[str, Tuple[int, int, int, int, int, str]],
) -> List[str]:
    """Perform topological sort with priority-based tie breaking."""

    # Build adjacency list and indegree map
    adjacency = {feature: set() for feature in features}
    indegree = {feature: 0 for feature in features}
    feature_set = set(features)

    for feature in features:
        for dep in dependencies.get(feature, []):
            if dep in feature_set:
                # dep -> feature edge (dep must come before feature)
                if feature not in adjacency[dep]:
                    adjacency[dep].add(feature)
                    indegree[feature] += 1

    # Priority queue for Kahn's algorithm
    heap = []
    default_priority = lambda f: (99, 99, 0, 99, 99, f)

    # Start with nodes with no dependencies
    for feature in features:
        if indegree[feature] == 0:
            heapq.heappush(heap, (priority_hints.get(feature, default_priority(feature)), feature))

    ordered = []
    while heap:
        _, current = heapq.heappop(heap)
        ordered.append(current)

        # Process neighbors
        for neighbor in sorted(adjacency.get(current, [])):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(heap, (priority_hints.get(neighbor, default_priority(neighbor)), neighbor))

    # Handle cycles (shouldn't happen but be safe)
    if len(ordered) != len(features):
        remaining = [f for f in features if f not in ordered]
        remaining.sort(key=lambda f: priority_hints.get(f, default_priority(f)))
        ordered.extend(remaining)

    return ordered

def parse_status_content(text: str) -> dict:
    """Parse feature status.md content."""
    info = {
        'stage': None,
        'now': [],
        'next': [],
        'risks': [],
    }

    if not text:
        return info

    lines = text.splitlines()
    section = None
    in_auto_generated = False

    for line in lines:
        stripped = line.strip()
        lowered = stripped.lower()

        # Skip auto-generated sections
        if "## Active Work (auto-generated)" in line or "Active Work (generated)" in line:
            in_auto_generated = True
            continue

        # End of auto-generated section (next ## heading)
        if in_auto_generated and line.startswith("## ") and "auto-generated" not in line:
            in_auto_generated = False

        # Skip lines in auto-generated sections
        if in_auto_generated:
            continue

        # Check for stage
        if lowered.startswith('stage:'):
            info['stage'] = stripped.split(':', 1)[1].strip()
            continue

        # Check for section headers (only manual sections)
        if lowered in ['now:', 'next:', 'risks:']:
            section = lowered[:-1]  # Remove colon
            continue

        # Reset section on new header
        if line.startswith('##'):
            section = None
            continue

        # Parse list items (only in manual sections)
        if section and stripped.startswith('-') and not in_auto_generated:
            content = stripped[1:].strip()
            if content:
                info[section].append(content)

    return info

def bucket(status: str) -> str:
    """Map task status to bucket."""
    s = (status or '').lower()
    if s in {'done','completed'}: return 'done'
    if s in {'review'}: return 'review'
    if s in {'doing','in_progress','in-progress','wip'}: return 'in_progress'
    if s in {'blocked'}: return 'blocked'
    if s in {'todo','planned'}: return 'planned'
    return 'backlog'

def main():
    """Generate project status with dependency-aware feature ordering."""

    # Initialize collections
    phases = []
    totals = {k:0 for k in ['backlog','planned','in_progress','review','blocked','done']}
    features_data = {}
    features_summary = []

    # Load roadmap priorities
    roadmap_priorities = load_roadmap_priorities()

    # Collect feature information
    feature_dependencies = {}
    feature_status_map = {}
    feature_index_map = {}

    if FEATURES.exists():
        feature_dirs = sorted([p for p in FEATURES.iterdir() if p.is_dir()])

        for idx, feat_dir in enumerate(feature_dirs):
            feature_key = feat_dir.name

            # Parse overview.md for dependencies
            overview_path = feat_dir / 'overview.md'
            if overview_path.exists():
                try:
                    text = overview_path.read_text(encoding='utf-8')
                    fm = parse_front_matter(text)
                    dependencies = parse_dependency_features(fm.get('dependencies'))
                    feature_dependencies[feature_key] = dependencies
                except:
                    feature_dependencies[feature_key] = []

            # Parse status.md
            status_path = feat_dir / 'status.md'
            if status_path.exists():
                try:
                    text = status_path.read_text(encoding='utf-8')
                    status_info = parse_status_content(text)
                    feature_status_map[feature_key] = status_info
                    feature_index_map[feature_key] = idx

                    # Add to summary
                    features_summary.append({
                        'key': feature_key,
                        'stage': status_info.get('stage'),
                        'now': status_info.get('now', []),
                        'next': status_info.get('next', []),
                        'risks': status_info.get('risks', []),
                    })
                except:
                    pass

    # Process sprint task directories
    if SPRINTS.exists():
        for year_dir in SPRINTS.iterdir():
            if not year_dir.is_dir() or year_dir.name == "current":
                continue

            for sprint_dir in year_dir.iterdir():
                if not sprint_dir.is_dir() or not sprint_dir.name.startswith("SPRINT-"):
                    continue

                tasks_dir = sprint_dir / "tasks"
                if not tasks_dir.exists():
                    continue

                sprint_tasks = []
                for task_dir in tasks_dir.iterdir():
                    if not task_dir.is_dir():
                        continue

                    task_yaml = task_dir / "task.yaml"
                    if not task_yaml.exists():
                        continue

                    try:
                        # Parse task.yaml
                        content = task_yaml.read_text(encoding='utf-8')
                        task_data = {}

                        for line in content.splitlines():
                            if ':' in line and not line.strip().startswith('-'):
                                key, value = line.split(':', 1)
                                key = key.strip()
                                value = value.strip()

                                if value.isdigit():
                                    task_data[key] = int(value)
                                elif value.startswith('[') and value.endswith(']'):
                                    items = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
                                    task_data[key] = [item for item in items if item]
                                else:
                                    task_data[key] = value

                        sprint_tasks.append(task_data)
                    except Exception as e:
                        print(f"Error parsing {task_yaml}: {e}")

                if sprint_tasks:
                    phases.append({
                        'name': sprint_dir.name,
                        'phase': sprint_dir.name,
                        'title': f"Sprint {sprint_dir.name}",
                        'features': list(set(t.get('feature', 'unknown') for t in sprint_tasks)),
                        'decisions': list(set(t.get('decision', '') for t in sprint_tasks if t.get('decision'))),
                        'tasks': [t.get('id') for t in sprint_tasks]
                    })

                    for t in sprint_tasks:
                        b = bucket(t.get('status',''))
                        totals[b] = totals.get(b,0)+1
                        feat = t.get('feature','unknown')
                        features_data.setdefault(feat, {'open':[], 'done':[]})
                        entry = {
                            'id': t.get('id'),
                            'title': t.get('title'),
                            'sprint': sprint_dir.name,
                            'status': t.get('status'),
                            'story_points': t.get('story_points'),
                            'prio': t.get('prio'),
                            'decision': t.get('decision')
                        }
                        if b == 'done':
                            features_data[feat]['done'].append(entry)
                        else:
                            features_data[feat]['open'].append(entry)

    # Calculate dependent counts
    feature_keys = [s['key'] for s in features_summary]
    dependent_counts = {feature: 0 for feature in feature_keys}
    for feature, deps in feature_dependencies.items():
        for dep in deps:
            if dep in dependent_counts:
                dependent_counts[dep] += 1

    # Compute priority hints
    feature_priority_hints = {}
    for feature in feature_keys:
        feature_priority_hints[feature] = compute_feature_priority(
            feature,
            feature_status_map.get(feature, {}),
            feature_index_map.get(feature, 0),
            roadmap_priorities,
            dependent_counts.get(feature, 0),
        )

    # Topologically sort features
    feature_order = topologically_sort_features(
        feature_keys,
        feature_dependencies,
        feature_priority_hints
    )

    # Reorder features_summary based on computed order
    summary_by_key = {s['key']: s for s in features_summary}
    features_summary = [summary_by_key[key] for key in feature_order if key in summary_by_key]

    # Build project-level now/next lists
    project_now = []
    project_next = []
    project_risks = []

    for feature in features_summary:
        for item in feature.get('now', []):
            project_now.append(f"{feature['key']}: {item}")
        for item in feature.get('next', []):
            project_next.append(f"{feature['key']}: {item}")
        for item in feature.get('risks', []):
            project_risks.append({'feature': feature['key'], 'risk': item})

    # Create final payload
    payload = {
        'generated_at': dt.datetime.utcnow().replace(microsecond=0).isoformat()+'Z',
        'phases': phases,
        'totals': totals,
        'features': features_data,
        'features_summary': features_summary,
        'project': {
            'now': project_now,
            'next': project_next,
            'risks': project_risks,
        }
    }

    # Write outputs (JSON only)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    (STATUS_DIR/'current.json').write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')
    print('Generated:', STATUS_DIR/'current.json')

    # Auto-update feature status files
    try:
        import subprocess
        result = subprocess.run([
            'python3',
            str(ROOT / 'process' / 'automation' / 'feature_status_updater.py'),
            '--update-all'
        ], capture_output=True, text=True, cwd=ROOT)

        if result.returncode == 0:
            print('Updated feature status files')
        else:
            print(f'Warning: Feature status update failed: {result.stderr}')
    except Exception as e:
        print(f'Warning: Could not update feature status: {e}')

if __name__ == '__main__':
    raise SystemExit(main())