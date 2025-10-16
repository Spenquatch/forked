#!/usr/bin/env python3
"""
Minimal validator stub for the project-handbook template.
Checks:
- Front matter exists on Markdown files under project-handbook/
- execution/<phase>/phase.yaml and README.md core fields match
- execution/<phase>/tasks.yaml entries have required fields and exactly one decision
Outputs a small JSON report at status/validation.json
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "project-handbook"
ROADMAP_PATH = ROOT / "roadmap" / "now-next-later.md"
RULES_PATH = ROOT / "process" / "checks" / "validation_rules.json"

def load_validation_rules() -> dict:
    """Load validation rules from JSON config."""
    default_rules = {
        "validation": {"require_front_matter": True, "skip_docs_directory": True},
        "sprint_tasks": {
            "require_task_yaml": True,
            "require_story_points": True,
            "required_task_fields": ["id", "title", "feature", "decision", "owner", "status", "story_points", "prio", "due", "acceptance"],
            "required_task_files": ["README.md", "steps.md", "commands.md", "checklist.md", "validation.md"],
            "enforce_sprint_scoped_dependencies": True
        },
        "story_points": {
            "validate_fibonacci_sequence": True,
            "allowed_story_points": [1, 2, 3, 5, 8, 13, 21]
        },
        "roadmap": {"normalize_links": True}
    }

    try:
        if RULES_PATH.exists():
            with open(RULES_PATH, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load validation rules: {e}")

    return default_rules

# --- Minimal YAML helpers (no external deps) ---
def _strip(val: str) -> str:
    return val.strip().strip('"').strip("'")

def parse_simple_yaml_mapping(text: str) -> dict:
    """Parse a small subset of YAML: top-level k:v, lists with '- ' items, and one-level nested mapping (files:)."""
    data: dict = {}
    lines = text.splitlines()
    i = 0
    n = len(lines)
    def is_kv(line: str) -> bool:
        return ":" in line and not line.lstrip().startswith("-")
    while i < n:
        raw = lines[i]
        line = raw.rstrip("\n")
        if not line.strip():
            i += 1; continue
        if not line.startswith(" ") and is_kv(line):
            key, val = line.split(":", 1)
            k = key.strip()
            v = val.strip()
            # list starting next lines
            if v == "":
                # could be list or nested mapping
                # peek next line
                if i + 1 < n and lines[i+1].lstrip().startswith("- "):
                    i += 1
                    arr = []
                    while i < n and lines[i].startswith("  - "):
                        arr.append(_strip(lines[i].split("- ",1)[1]))
                        i += 1
                    data[k] = arr
                    continue
                elif i + 1 < n and lines[i+1].startswith("  "):
                    # nested mapping one level
                    i += 1
                    sub = {}
                    while i < n and lines[i].startswith("  ") and is_kv(lines[i].strip()):
                        sk, sv = lines[i].strip().split(":", 1)
                        sub[_strip(sk)] = _strip(sv)
                        i += 1
                    data[k] = sub
                    continue
                else:
                    data[k] = ""
            else:
                data[k] = _strip(v)
            i += 1
            continue
        else:
            i += 1
    return data

def parse_simple_yaml_task_list(text: str) -> list:
    """Parse a list of tasks with top-level '- ' and indented k:v, supporting list fields acceptance, links."""
    items = []
    current = None
    mode_list_key = None  # currently collecting list for this key
    for raw in text.splitlines():
        if raw.startswith("- "):
            # flush previous
            if current is not None:
                items.append(current)
            current = {}
            mode_list_key = None
            # allow single-line '- key: value' (rare), otherwise ignore content here
            remainder = raw[2:].strip()
            if remainder and ":" in remainder:
                k, v = remainder.split(":", 1)
                current[_strip(k)] = _strip(v)
            continue
        if current is None:
            continue
        if raw.startswith("  ") and ":" in raw and not raw.strip().startswith("- "):
            k, v = raw.strip().split(":", 1)
            k = _strip(k)
            v = v.strip()
            # Handle inline lists like [TASK-001, TASK-002]
            if v.startswith("[") and v.endswith("]"):
                # Parse inline list
                list_content = v[1:-1].strip()
                if list_content:
                    current[k] = [_strip(item) for item in list_content.split(",")]
                else:
                    current[k] = []
                mode_list_key = None
            elif v == "":
                # start list or nested (we only support list here)
                mode_list_key = k
                current[k] = []
            else:
                current[k] = _strip(v)
                mode_list_key = None
            continue
        if raw.startswith("    - ") and mode_list_key:
            current[mode_list_key].append(_strip(raw.split("- ",1)[1]))
            continue
        # end of nested list
        mode_list_key = None
    if current is not None:
        items.append(current)
    return items

def read(p: Path) -> str:
    try: return p.read_text(encoding="utf-8")
    except Exception: return ""

def parse_front_matter(text: str):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---": return {}, -1, -1
    try: end = lines[1:].index("---") + 1
    except ValueError: return {}, -1, -1
    fm = {}
    for line in lines[1:end]:
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, 0, end

def validate_front_matter(issues, rules):
    if not rules.get("validation", {}).get("require_front_matter", True):
        return

    for md in ROOT.rglob("*.md"):
        # Skip docs directory if configured
        if rules.get("validation", {}).get("skip_docs_directory", True):
            if "docs/" in str(md.relative_to(ROOT)):
                continue

        # Skip triage.md files in backlog (they're analysis templates, not docs)
        if "backlog/" in str(md.relative_to(ROOT)) and md.name == "triage.md":
            continue

        fm, _, _ = parse_front_matter(read(md))
        if not fm:
            issues.append({"path": str(md), "code": "front_matter_missing", "severity": "error"})

def validate_sprints(issues, rules):
    """Validate sprint task directories and dependencies."""
    sprint_rules = rules.get("sprint_tasks", {})
    story_rules = rules.get("story_points", {})

    sprints_dir = ROOT / "sprints"
    if not sprints_dir.exists():
        return

    # Find all sprint directories
    for year_dir in sprints_dir.iterdir():
        if not year_dir.is_dir() or year_dir.name == "current":
            continue

        for sprint_dir in year_dir.iterdir():
            if not sprint_dir.is_dir() or not sprint_dir.name.startswith("SPRINT-"):
                continue

            tasks_dir = sprint_dir / "tasks"
            if not tasks_dir.exists():
                continue

            # Collect all task IDs in this sprint
            sprint_task_ids = set()
            sprint_tasks = []

            for task_dir in tasks_dir.iterdir():
                if not task_dir.is_dir():
                    continue

                task_yaml = task_dir / "task.yaml"
                if not task_yaml.exists():
                    issues.append({"path": str(task_dir), "code": "task_yaml_missing", "severity": "error"})
                    continue

                try:
                    content = task_yaml.read_text(encoding="utf-8")
                    task_data = {}

                    # Parse task.yaml
                    for line in content.splitlines():
                        if ':' in line and not line.strip().startswith('-'):
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()

                            if value.startswith('[') and value.endswith(']'):
                                # Parse list
                                items = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
                                task_data[key] = [item for item in items if item]
                            else:
                                task_data[key] = value

                    sprint_tasks.append((task_dir, task_data))

                    # Track task ID
                    task_id = task_data.get("id")
                    if task_id:
                        sprint_task_ids.add(task_id)

                except Exception as e:
                    issues.append({"path": str(task_yaml), "code": "task_yaml_parse_error", "severity": "error", "message": str(e)})

            # Validate each task
            for task_dir, task_data in sprint_tasks:
                task_yaml = task_dir / "task.yaml"

                # Check required fields
                required_fields = sprint_rules.get("required_task_fields", ["id", "title", "feature", "decision", "owner", "status", "story_points", "prio", "due", "acceptance"])
                missing = [k for k in required_fields if k not in task_data]
                if missing and sprint_rules.get("require_task_yaml", True):
                    issues.append({"path": str(task_yaml), "code": "task_missing_fields", "severity": "error", "missing": missing})

                # Validate decision format
                decision = task_data.get("decision")
                if decision and sprint_rules.get("require_single_decision_per_task", True):
                    if not (decision.startswith("ADR-") or decision.startswith("FDR-")):
                        issues.append({"path": str(task_yaml), "code": "task_decision_invalid", "severity": "error"})

                # Validate story points
                story_points = task_data.get("story_points")
                if story_points and story_rules.get("validate_fibonacci_sequence", True):
                    try:
                        sp_int = int(story_points)
                        allowed_points = story_rules.get("allowed_story_points", [1, 2, 3, 5, 8, 13, 21])
                        if sp_int not in allowed_points:
                            issues.append({
                                "path": str(task_yaml),
                                "code": "task_story_points_invalid",
                                "severity": "warning",
                                "message": f"Story points should use configured sequence: {allowed_points}"
                            })
                    except:
                        issues.append({"path": str(task_yaml), "code": "task_story_points_not_integer", "severity": "error"})

                # Validate dependencies are sprint-scoped only
                if sprint_rules.get("enforce_sprint_scoped_dependencies", True):
                    depends_on = task_data.get("depends_on", [])
                    if isinstance(depends_on, str):
                        depends_on = [depends_on]

                    for dep in depends_on:
                        if dep and dep not in sprint_task_ids:
                            issues.append({
                                "path": str(task_yaml),
                                "code": "task_dependency_out_of_sprint",
                                "severity": "error",
                                "message": f"Task depends on {dep} which is not in current sprint. Dependencies must be sprint-scoped only."
                            })

                # Check required files exist
                if sprint_rules.get("require_task_directory_files", True):
                    required_files = sprint_rules.get("required_task_files", ["README.md", "steps.md", "commands.md", "checklist.md", "validation.md"])
                    for req_file in required_files:
                        if not (task_dir / req_file).exists():
                            issues.append({"path": str(task_dir), "code": f"task_missing_{req_file.replace('.', '_')}", "severity": "warning"})

def validate_phase(issues):
    """Validate legacy execution phases (for backwards compatibility)."""
    exec_dir = ROOT / "execution"
    if not exec_dir.exists():
        return

    # Only validate if execution phases still exist
    for pdir in [p for p in exec_dir.iterdir() if p.is_dir()]:
        readme = pdir / "README.md"
        phase_yaml = pdir / "phase.yaml"
        if readme.exists() and phase_yaml.exists():
            rfm, _, _ = parse_front_matter(read(readme))
            data = parse_simple_yaml_mapping(phase_yaml.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for k in ["phase", "title"]:
                    if str(data.get(k, "")) != str(rfm.get(k, "")):
                        issues.append({"path": str(pdir), "code": f"phase_mismatch_{k}", "severity": "error"})
                # features/decisions presence
                if not data.get("features"): issues.append({"path": str(pdir), "code": "phase_features_missing", "severity": "error"})
                if not data.get("decisions"): issues.append({"path": str(pdir), "code": "phase_decisions_missing", "severity": "error"})

def normalize_roadmap_links(rules):
    """Convert bare paths in roadmap to proper markdown links."""
    if not rules.get("roadmap", {}).get("normalize_links", True):
        return

    if not ROADMAP_PATH.exists():
        return

    try:
        text = ROADMAP_PATH.read_text(encoding="utf-8")
    except:
        return

    if not text:
        return

    # Parse front matter
    fm, start, end = parse_front_matter(text)
    if start == -1 or end == -1:
        body_start = 0
    else:
        body_start = end + 1

    lines = text.splitlines()
    head = lines[:body_start]
    body_lines = lines[body_start:]
    body_text = "\n".join(body_lines)

    # Pattern to match [../path] not followed by (url)
    pattern = re.compile(r'\[(\.\./[^\]\s]+)\](?!\()')

    def repl(match: re.Match) -> str:
        target = match.group(1)
        return f"[{target}]({target})"

    new_body, count = pattern.subn(repl, body_text)

    if count:
        # Reconstruct the file
        prefix = "\n".join(head)
        if prefix:
            prefix += "\n"
        new_text = prefix + new_body
        if text.endswith("\n") and not new_text.endswith("\n"):
            new_text += "\n"
        ROADMAP_PATH.write_text(new_text, encoding="utf-8")
        print(f"Normalized {count} roadmap link(s)")

def main():
    # Load validation rules
    rules = load_validation_rules()

    # Normalize roadmap links first
    normalize_roadmap_links(rules)

    issues = []
    validate_front_matter(issues, rules)

    # Validate sprint task directories (new primary system)
    try:
        validate_sprints(issues, rules)
    except Exception as e:
        print(f"Warning: Sprint validation error: {e}")

    # Validate legacy execution phases (backwards compatibility)
    try:
        validate_phase(issues)
    except Exception:
        # YAML may be missing; keep template lightweight
        pass

    out = ROOT / "status" / "validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"issues": issues}, indent=2) + "\n", encoding="utf-8")
    errs = sum(1 for i in issues if i.get("severity") == "error")
    warns = sum(1 for i in issues if i.get("severity") == "warning")
    print(f"validation: {errs} error(s), {warns} warning(s), report: {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
