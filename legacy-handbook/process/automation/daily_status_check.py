#!/usr/bin/env python3
"""
Daily status generator and checker.
- Skips weekends (Saturday/Sunday)
- Auto-generates daily status if missing
- Tracks sprint progress and blockers
"""

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
STATUS_DIR = ROOT / "status"
SPRINTS_DIR = ROOT / "sprints"
RULES_PATH = ROOT / "process" / "checks" / "validation_rules.json"

def load_config() -> dict:
    """Load configuration from validation rules."""
    default_config = {
        "daily_status": {
            "skip_weekends": True,
            "weekend_days": [5, 6],
            "max_hours_without_update": 24,
            "monday_weekend_summary": True,
            "friday_week_wrapup": True
        }
    }

    try:
        if RULES_PATH.exists():
            with open(RULES_PATH, 'r') as f:
                return json.load(f)
    except Exception:
        pass

    return default_config

def get_current_sprint() -> Optional[str]:
    """Get current sprint ID based on week number."""
    today = dt.date.today()
    week_num = today.isocalendar()[1]
    year = today.year
    return f"SPRINT-{year}-W{week_num:02d}"

def should_generate_daily(config: dict = None) -> bool:
    """Check if daily status should be generated (configurable weekend skipping)."""
    if config is None:
        config = load_config()

    daily_config = config.get("daily_status", {})

    if not daily_config.get("skip_weekends", True):
        return True

    today = dt.date.today()
    weekend_days = daily_config.get("weekend_days", [5, 6])  # Default: Saturday, Sunday
    return today.weekday() not in weekend_days

def get_last_daily_status() -> Optional[Path]:
    """Find the most recent daily status file."""
    daily_dir = STATUS_DIR / "daily"
    if not daily_dir.exists():
        return None

    # Look for YYYY/MM/DD.md structure
    status_files = []
    for year_dir in daily_dir.iterdir():
        if year_dir.is_dir() and year_dir.name.isdigit():
            for month_dir in year_dir.iterdir():
                if month_dir.is_dir() and month_dir.name.isdigit():
                    for day_file in month_dir.glob("*.md"):
                        status_files.append(day_file)

    return sorted(status_files, reverse=True)[0] if status_files else None

def hours_since_last_daily() -> float:
    """Calculate hours since last daily status."""
    last_status = get_last_daily_status()
    if not last_status:
        return float('inf')

    # Extract date from filename (YYYY-MM-DD.md)
    try:
        date_str = last_status.stem
        last_date = dt.datetime.strptime(date_str, "%Y-%m-%d")
        now = dt.datetime.now()
        delta = now - last_date
        return delta.total_seconds() / 3600
    except:
        return float('inf')

def collect_sprint_tasks() -> Dict[str, List[Dict]]:
    """Collect all tasks from current sprint."""
    tasks_by_status = {
        'todo': [],
        'doing': [],
        'review': [],
        'done': [],
        'blocked': []
    }

    # Get current sprint directory
    current_sprint = get_current_sprint()
    if not current_sprint:
        return tasks_by_status

    sprint_dir = SPRINTS_DIR / current_sprint.split('-')[1] / current_sprint
    tasks_dir = sprint_dir / "tasks"

    if not tasks_dir.exists():
        return tasks_by_status

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
                    else:
                        task_data[key] = value

            status = task_data.get('status', 'todo')
            if status in tasks_by_status:
                tasks_by_status[status].append({
                    'id': task_data.get('id'),
                    'title': task_data.get('title'),
                    'story_points': task_data.get('story_points', 0),
                    'owner': task_data.get('owner'),
                    'blocked_reason': task_data.get('blocked_reason', '')
                })

        except Exception as e:
            print(f"Error parsing {task_yaml}: {e}")

    return tasks_by_status

def generate_daily_template(date: dt.date) -> str:
    """Generate daily status template."""
    sprint_id = get_current_sprint()
    tasks = collect_sprint_tasks()

    # Special templates for Monday and Friday
    weekday = date.weekday()
    is_monday = weekday == 0
    is_friday = weekday == 4

    template = f"""---
title: Daily Status - {date.strftime('%Y-%m-%d')}
type: status-daily
date: {date.strftime('%Y-%m-%d')}
sprint: {sprint_id}
tags: [status, daily]
links: [../../../sprints/current.md]
---

# Daily Status - {date.strftime('%A, %B %d, %Y')}

## Sprint: {sprint_id}
**Sprint Timeline**: {date.strftime('%A')} of work week (Day {date.weekday() + 1 if date.weekday() < 5 else 'Weekend'})
"""

    if is_monday:
        template += "\n## Weekend Summary\n"
        template += "- [ ] Review any weekend commits/PRs\n"
        template += "- [ ] Check monitoring/alerts from weekend\n\n"

    # Progress section
    template += "\n## Progress\n"
    if tasks['doing']:
        for task in tasks['doing']:
            template += f"- [ ] {task['id']}: {task['title']} - UPDATE PROGRESS\n"
    if tasks['review']:
        for task in tasks['review']:
            template += f"- [ ] {task['id']}: {task['title']} - IN REVIEW\n"
    if not tasks['doing'] and not tasks['review']:
        template += "- [ ] No tasks currently in progress\n"

    # Completed section
    template += "\n## Completed Today\n"
    template += "- [ ] (Update with completed tasks)\n"

    # Blockers section
    template += "\n## Blockers\n"
    if tasks['blocked']:
        for task in tasks['blocked']:
            reason = task.get('blocked_reason', 'Reason not specified')
            template += f"- {task['id']}: {reason}\n"
    else:
        template += "- None\n"

    # Backlog Impact section
    template += "\n## Backlog Impact\n"

    # Load backlog data
    backlog_index = Path(__file__).parent.parent.parent / "backlog" / "index.json"
    if backlog_index.exists():
        backlog_data = json.loads(backlog_index.read_text())
        p0_count = len([i for i in backlog_data.get("items", []) if i.get("severity") == "P0"])
        p1_count = len([i for i in backlog_data.get("items", []) if i.get("severity") == "P1"])

        if p0_count > 0:
            template += f"- ⚠️  **P0 Issues**: {p0_count} critical issues require immediate attention\n"
        if p1_count > 0:
            template += f"- P1 Issues: {p1_count} high priority for next sprint\n"
        if p0_count == 0 and p1_count == 0:
            template += "- No P0/P1 issues\n"
    else:
        template += "- No backlog items tracked\n"

    template += "- New issues discovered: (Update if any)\n"

    # Decisions section
    template += "\n## Decisions\n"
    template += "- (Document any technical decisions made today)\n"

    # Tomorrow section (or Monday for Friday)
    if is_friday:
        template += "\n## Monday Focus\n"
    else:
        template += "\n## Tomorrow\n"

    if tasks['todo']:
        # Pick top 2-3 todos
        for task in tasks['todo'][:3]:
            template += f"- {task['id']}: {task['title']}\n"
    else:
        template += "- Continue current work\n"

    # Sprint metrics
    total_points = sum(t.get('story_points', 0) for tasks_list in tasks.values() for t in tasks_list)
    done_points = sum(t.get('story_points', 0) for t in tasks['done'])
    in_progress_points = sum(t.get('story_points', 0) for t in tasks['doing'])

    template += f"""
## Sprint Metrics
- Total Points: {total_points}
- Completed: {done_points}
- In Progress: {in_progress_points}
- Velocity: {done_points}/{total_points} ({int(done_points*100/total_points) if total_points else 0}%)
"""

    if is_friday:
        template += "\n## Week Summary\n"
        template += "- Sprint progress: ON TRACK / AT RISK / BEHIND\n"
        template += "- Key achievements: \n"
        template += "- Carry-over items: \n"

    return template

def create_daily_status(force: bool = False) -> bool:
    """Create daily status if needed."""
    today = dt.date.today()

    # Check if we should generate (not weekend unless forced)
    if not force and not should_generate_daily():
        print(f"Skipping daily status for {today.strftime('%A')} (weekend)")
        return False

    # Create proper directory structure: status/daily/YYYY/MM/DD.md
    daily_base = STATUS_DIR / "daily"
    year_dir = daily_base / today.strftime('%Y')
    month_dir = year_dir / today.strftime('%m')
    status_file = month_dir / f"{today.strftime('%d')}.md"

    month_dir.mkdir(parents=True, exist_ok=True)

    if status_file.exists() and not force:
        print(f"Daily status already exists: {status_file}")
        return False

    # Generate and write template
    template = generate_daily_template(today)
    status_file.write_text(template, encoding='utf-8')
    print(f"Created daily status: {status_file}")
    return True

def check_status(verbose: bool = False) -> int:
    """Check if daily status is current."""
    if not should_generate_daily():
        if verbose:
            print("Weekend - no daily status required")
        return 0

    hours = hours_since_last_daily()

    if hours > 24:
        if hours == float('inf'):
            print("⚠️  No daily status found!")
        else:
            print(f"⚠️  Daily status is {int(hours)} hours old!")
        print(f"Run: python3 {__file__} --generate")
        return 1

    if verbose:
        print(f"✅ Daily status is current ({int(hours)} hours old)")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Daily status generator and checker")
    parser.add_argument('--generate', action='store_true', help='Generate daily status')
    parser.add_argument('--check-only', action='store_true', help='Only check, don\'t generate')
    parser.add_argument('--force', action='store_true', help='Force generation even on weekends')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.check_only:
        return check_status(args.verbose)

    if args.generate or hours_since_last_daily() > 24:
        created = create_daily_status(args.force)
        return 0 if created else 1

    return check_status(args.verbose)

if __name__ == "__main__":
    exit(main())