#!/usr/bin/env python3
"""
Sprint lifecycle management.
- Creates new sprints on Monday
- Tracks velocity and burndown
- Generates retrospectives
- Manages sprint health indicators
"""

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[3] / "project-handbook"
SPRINTS_DIR = ROOT / "sprints"
STATUS_DIR = ROOT / "status"
RULES_PATH = ROOT / "process" / "checks" / "validation_rules.json"

def load_config() -> dict:
    """Load configuration from validation rules."""
    try:
        if RULES_PATH.exists():
            with open(RULES_PATH, 'r') as f:
                return json.load(f)
    except Exception:
        pass

    return {
        "sprint_management": {
            "health_check_thresholds": {
                "blocked_percentage_red": 30,
                "progress_percentage_red": 50,
                "progress_check_day": 3
            },
            "sprint_duration_days": 5
        }
    }

def get_sprint_id(date: dt.date = None) -> str:
    """Generate sprint ID for given date (default: today)."""
    if date is None:
        date = dt.date.today()
    week_num = date.isocalendar()[1]
    year = date.year
    return f"SPRINT-{year}-W{week_num:02d}"

def get_sprint_dates(sprint_id: str) -> Tuple[dt.date, dt.date]:
    """Get start and end dates for a sprint."""
    # Parse SPRINT-YYYY-W##
    parts = sprint_id.split('-')
    year = int(parts[1])
    week = int(parts[2][1:])  # Remove 'W'

    # Monday of that week
    jan1 = dt.date(year, 1, 1)
    week1_monday = jan1 - dt.timedelta(days=jan1.weekday())
    sprint_start = week1_monday + dt.timedelta(weeks=week-1)
    sprint_end = sprint_start + dt.timedelta(days=4)  # Friday

    return sprint_start, sprint_end

def collect_tasks(sprint_id: str = None) -> List[Dict]:
    """Collect all tasks from current sprint task directories."""
    if sprint_id is None:
        sprint_id = get_sprint_id()

    sprint_dir = SPRINTS_DIR / sprint_id.split('-')[1] / sprint_id
    tasks_dir = sprint_dir / "tasks"

    all_tasks = []

    if not tasks_dir.exists():
        return all_tasks

    for task_dir in tasks_dir.iterdir():
        if not task_dir.is_dir():
            continue

        task_yaml = task_dir / "task.yaml"
        if not task_yaml.exists():
            continue

        try:
            # Simple YAML parsing
            content = task_yaml.read_text(encoding='utf-8')
            task_data = {}

            for line in content.splitlines():
                if ':' in line and not line.strip().startswith('-'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle basic types
                    if value.isdigit():
                        task_data[key] = int(value)
                    elif value.startswith('[') and value.endswith(']'):
                        # Handle lists
                        items = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
                        task_data[key] = [item for item in items if item]
                    else:
                        task_data[key] = value

            all_tasks.append(task_data)

        except Exception as e:
            print(f"Error parsing {task_yaml}: {e}")

    return all_tasks

def calculate_velocity(tasks: List[Dict]) -> Dict:
    """Calculate velocity metrics from tasks."""
    metrics = {
        'total_points': 0,
        'completed_points': 0,
        'in_progress_points': 0,
        'blocked_points': 0,
        'todo_points': 0,
        'velocity_percentage': 0
    }

    for task in tasks:
        points = int(task.get('story_points', 0))
        status = task.get('status', 'todo').lower()

        metrics['total_points'] += points

        if status == 'done':
            metrics['completed_points'] += points
        elif status in ['doing', 'in_progress', 'review']:
            metrics['in_progress_points'] += points
        elif status == 'blocked':
            metrics['blocked_points'] += points
        else:  # todo, planned
            metrics['todo_points'] += points

    if metrics['total_points'] > 0:
        metrics['velocity_percentage'] = int(
            metrics['completed_points'] * 100 / metrics['total_points']
        )

    return metrics

def get_sprint_health(tasks: List[Dict], day_of_sprint: int, config: dict = None) -> str:
    """
    Determine sprint health status using configurable thresholds.
    """
    if config is None:
        config = load_config()

    thresholds = config.get("sprint_management", {}).get("health_check_thresholds", {})
    red_blocked = thresholds.get("blocked_percentage_red", 30)
    red_progress = thresholds.get("progress_percentage_red", 50)
    check_day = thresholds.get("progress_check_day", 3)

    metrics = calculate_velocity(tasks)

    blocked_percentage = (
        metrics['blocked_points'] * 100 / metrics['total_points']
        if metrics['total_points'] > 0 else 0
    )

    progress_percentage = (
        (metrics['completed_points'] + metrics['in_progress_points']) * 100 / metrics['total_points']
        if metrics['total_points'] > 0 else 0
    )

    # Red conditions (configurable thresholds)
    if blocked_percentage > red_blocked:
        return f"🔴 RED - Too many blockers ({blocked_percentage:.0f}% > {red_blocked}%)"
    if day_of_sprint >= check_day and progress_percentage < red_progress:
        return f"🔴 RED - Behind schedule ({progress_percentage:.0f}% < {red_progress}% by day {check_day})"

    # Yellow conditions (half of red thresholds)
    if blocked_percentage > red_blocked / 2:
        return f"🟡 YELLOW - Some blockers need attention ({blocked_percentage:.0f}%)"
    if day_of_sprint >= check_day - 1 and progress_percentage < red_progress * 0.8:
        return f"🟡 YELLOW - Slightly behind schedule ({progress_percentage:.0f}%)"

    return "🟢 GREEN - On track"

def generate_ascii_burndown(sprint_id: str, tasks: List[Dict]) -> str:
    """Generate ASCII burndown chart for sprint."""
    start_date, end_date = get_sprint_dates(sprint_id)
    metrics = calculate_velocity(tasks)

    # Calculate daily progress (simplified - would need daily snapshots in real system)
    total = metrics['total_points']
    completed = metrics['completed_points']
    remaining = total - completed

    # Generate chart
    chart = f"""
Sprint Burndown: {sprint_id}
{'='*50}

Points Remaining:
{total:3d} |{'█' * 20} Day 1 (Monday)
    |{'█' * int(20 * 0.8)} Day 2
    |{'█' * int(20 * 0.6)} Day 3 (Mid-sprint)
    |{'█' * int(20 * remaining/total) if total > 0 else ''} Today
  0 |{'_' * 20}
    Mon   Tue   Wed   Thu   Fri

Legend: █ = Remaining work

Current Status:
- Total Points: {total}
- Completed: {completed} ({metrics['velocity_percentage']}%)
- In Progress: {metrics['in_progress_points']}
- Blocked: {metrics['blocked_points']}
- Todo: {metrics['todo_points']}
"""
    return chart

def get_current_release_context() -> Dict:
    """Get current release context for sprint planning."""
    try:
        import sys
        sys.path.append(str(ROOT / 'process' / 'automation'))
        from release_manager import get_current_release, load_release_features

        current_release = get_current_release()
        if current_release:
            features = load_release_features(current_release)
            return {
                'version': current_release,
                'features': features
            }
    except Exception:
        pass

    return {}

def create_sprint_plan(sprint_id: str) -> str:
    """Generate sprint planning template with release context."""
    start_date, end_date = get_sprint_dates(sprint_id)
    tasks = collect_tasks()
    available_tasks = [t for t in tasks if t.get('status') in ['todo', 'planned']]

    # Get release context
    release_context = get_current_release_context()

    template = f"""---
title: Sprint Plan - {sprint_id}
type: sprint-plan
date: {dt.date.today().strftime('%Y-%m-%d')}
sprint: {sprint_id}
start: {start_date.strftime('%Y-%m-%d')}
end: {end_date.strftime('%Y-%m-%d')}
tags: [sprint, planning]
"""

    if release_context:
        template += f"release: {release_context['version']}\n"

    template += "---\n\n"
    template += f"# Sprint Plan: {sprint_id}\n\n"

    # Release context
    if release_context:
        template += f"## Release Context\n"
        template += f"**Release**: {release_context['version']}\n"
        template += f"**Features in this release**:\n"
        for feature_name, feature_data in release_context.get('features', {}).items():
            critical_note = " (Critical Path)" if feature_data.get('critical_path') else ""
            template += f"- {feature_name}: {feature_data.get('type', 'regular')}{critical_note}\n"
        template += "\n"

    template += f"""## Sprint Duration
- Start: Monday, {start_date.strftime('%B %d, %Y')}
- End: Friday, {end_date.strftime('%B %d, %Y')}

## Sprint Goals
"""

    if release_context:
        template += "*(Align with release features above)*\n"

    template += """1. [ ] Primary goal (60% of capacity)
2. [ ] Secondary goal (30% of capacity)
3. [ ] Stretch goal (10% of capacity)

## Task Creation Guide
Create tasks for this sprint using:
```bash
make task-create title="Task Name" feature=feature-name decision=ADR-XXX points=5
```

## Capacity Planning

### Total Capacity
- **Team Size**: X developers
- **Sprint Days**: 5 (Monday-Friday)
- **Historical Velocity**: X points/person/sprint
- **Total Available Points**: Team × Days × Velocity = X points

### 80/20 Capacity Allocation
- **80% Planned Work** (X points):
  - Release features and roadmap items
  - Sprint goals and committed deliverables
  - Scheduled improvements and tech debt
- **20% Interrupt Budget** (X points):
  - P0/P1 issues from backlog
  - Wildcards and urgent requests
  - Production support and hotfixes

### Current Backlog Status
Run `make backlog-list severity=P0` and `make backlog-list severity=P1` to review high-priority issues that may need sprint allocation.

## Feature Work Priorities
"""

    if release_context and release_context.get('features'):
        template += "Based on current release assignment:\n"
        for feature_name, feature_data in release_context['features'].items():
            priority = feature_data.get('priority', 'P2')
            template += f"- **{feature_name}** ({priority}): Work needed for release\n"
    else:
        template += "- Review roadmap and feature status for priority work\n"

    template += """

## Dependencies & Risks
- **External Dependencies**: List any blockers outside team control
- **Cross-Team Dependencies**: Coordinate with other teams
- **Technical Risks**: Known challenges or unknowns
- **Capacity Risks**: PTO, holidays, other commitments

## Success Criteria
- [ ] All committed tasks completed (story points delivered)
- [ ] Sprint health maintained (🟢 Green)
- [ ] No critical bugs introduced
- [ ] Release timeline maintained (if applicable)
- [ ] Team velocity sustainable

## Sprint Retrospective Planning
- What experiments to try this sprint?
- What metrics to track?
- What improvements from last retrospective?
"""

    return template

def create_retrospective(sprint_id: str) -> str:
    """Generate sprint retrospective template."""
    tasks = collect_tasks()
    metrics = calculate_velocity(tasks)
    health = get_sprint_health(tasks, 5)  # End of sprint

    template = f"""---
title: Sprint Retrospective - {sprint_id}
type: sprint-retrospective
date: {dt.date.today().strftime('%Y-%m-%d')}
sprint: {sprint_id}
tags: [sprint, retrospective]
---

# Sprint Retrospective: {sprint_id}

## Sprint Metrics
- **Planned Points**: {metrics['total_points']}
- **Completed Points**: {metrics['completed_points']}
- **Velocity**: {metrics['velocity_percentage']}%
- **Sprint Health**: {health}

## Velocity Trend
- This Sprint: {metrics['completed_points']} points
- 3-Sprint Average: (Calculate from previous sprints)
- Trend: ↑ ↓ →

## What Went Well
- [ ] Item 1
- [ ] Item 2

## What Could Be Improved
- [ ] Item 1
- [ ] Item 2

## Action Items
- [ ] Action 1 - Owner: @person - Due: Date
- [ ] Action 2 - Owner: @person - Due: Date

## Completed Tasks
"""

    # List completed tasks
    completed = [t for t in tasks if t.get('status') == 'done']
    for task in completed:
        template += f"- ✅ {task.get('id')}: {task.get('title')}\n"

    template += "\n## Carried Over\n"
    carried = [t for t in tasks if t.get('status') != 'done']
    for task in carried[:5]:  # Top 5
        template += f"- ⏩ {task.get('id')}: {task.get('title')} (Status: {task.get('status')})\n"

    return template

def update_current_symlink(sprint_id: str):
    """Update the 'current' symlink to point to active sprint."""
    current_link = SPRINTS_DIR / "current"
    sprint_path = SPRINTS_DIR / sprint_id.split('-')[1] / sprint_id

    if current_link.exists() or current_link.is_symlink():
        current_link.unlink()

    if sprint_path.exists():
        current_link.symlink_to(sprint_path.relative_to(SPRINTS_DIR))

def show_capacity(sprint_id: str):
    """Display sprint capacity allocation and usage"""
    # Load validation rules for configuration
    validation_rules_path = Path(__file__).parent.parent / "checks" / "validation_rules.json"
    validation_rules = {}
    if validation_rules_path.exists():
        validation_rules = json.loads(validation_rules_path.read_text())

    sprint_config = validation_rules.get("sprint_management", {})
    capacity_config = sprint_config.get("capacity_allocation", {})
    planned_pct = capacity_config.get("default_planned_percentage", 80)
    reactive_pct = capacity_config.get("default_reactive_percentage", 20)

    # Load backlog data
    backlog_index = Path(__file__).parent.parent.parent / "backlog" / "index.json"
    p0_p1_count = 0
    if backlog_index.exists():
        backlog_data = json.loads(backlog_index.read_text())
        for item in backlog_data.get("items", []):
            if item.get("severity") in ["P0", "P1"]:
                p0_p1_count += 1

    # Collect task data
    tasks = collect_tasks()
    metrics = calculate_velocity(tasks)

    # Calculate capacity usage
    total_points = metrics.get("total_points", 0)
    completed_points = metrics.get("completed_points", 0)
    blocked_points = metrics.get("blocked_points", 0)
    in_progress_points = metrics.get("in_progress_points", 0)

    print(f"\n📊 SPRINT CAPACITY ALLOCATION")
    print("=" * 80)

    print(f"\n🎯 Sprint: {sprint_id}")
    print("-" * 40)

    # Show allocation model
    print(f"\n📈 Capacity Model (80/20)")
    print("-" * 40)
    print(f"Planned Work:   {planned_pct}% of capacity")
    print(f"Reactive Work:  {reactive_pct}% of capacity")

    # Show current usage
    print(f"\n💼 Current Usage")
    print("-" * 40)

    if total_points > 0:
        # Estimate reactive vs planned based on task metadata
        print(f"Total Points:      {total_points}")
        print(f"Completed:         {completed_points} ({(completed_points/total_points*100):.1f}%)")
        print(f"In Progress:       {in_progress_points} ({(in_progress_points/total_points*100):.1f}%)")
        print(f"Blocked:           {blocked_points} ({(blocked_points/total_points*100):.1f}%)")
    else:
        print("No tasks in current sprint")

    # Show P0/P1 pressure
    print(f"\n🚨 Reactive Pressure")
    print("-" * 40)

    if p0_p1_count > 0:
        print(f"P0/P1 Issues:      {p0_p1_count}")
        if p0_p1_count > 3:
            print("⚠️  WARNING: High reactive load - consider adjusting capacity")
        else:
            print("✅ Reactive load within normal range")
    else:
        print("✅ No P0/P1 issues - full planned capacity available")

    # Show recommendations
    print(f"\n💡 Recommendations")
    print("-" * 40)

    if p0_p1_count > 5:
        print("🔴 Consider high-incident mode (60/40 allocation)")
    elif p0_p1_count > 3:
        print("🟠 Monitor reactive capacity usage closely")
    elif total_points == 0:
        print("🟡 Add tasks to sprint to utilize capacity")
    else:
        print("✅ Capacity allocation is balanced")

    # Show available adjustment presets
    if capacity_config.get("allow_dynamic_adjustment"):
        presets = capacity_config.get("adjustment_presets", {})
        if presets:
            print(f"\n🔧 Available Capacity Modes")
            print("-" * 40)
            for mode, allocation in presets.items():
                print(f"{mode:20} {allocation['planned']}% planned / {allocation['reactive']}% reactive")

    print("\n" + "=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Sprint lifecycle manager")
    parser.add_argument('--plan', action='store_true', help='Create sprint plan')
    parser.add_argument('--close', action='store_true', help='Close current sprint')
    parser.add_argument('--status', action='store_true', help='Show sprint status')
    parser.add_argument('--burndown', action='store_true', help='Generate burndown chart')
    parser.add_argument('--validate', action='store_true', help='Validate sprint setup')
    parser.add_argument('--capacity', action='store_true', help='Show capacity allocation')
    parser.add_argument('--sprint', help='Sprint ID (default: current)', default=None)

    args = parser.parse_args()

    sprint_id = args.sprint or get_sprint_id()
    sprint_dir = SPRINTS_DIR / sprint_id.split('-')[1] / sprint_id

    if args.plan:
        # Create sprint directory structure
        sprint_dir.mkdir(parents=True, exist_ok=True)
        (sprint_dir / "tasks").mkdir(exist_ok=True)
        # Note: Daily status now lives in status/daily/YYYY/MM/ with sprint references

        plan_file = sprint_dir / "plan.md"
        plan_file.write_text(create_sprint_plan(sprint_id), encoding='utf-8')
        print(f"Created sprint plan: {plan_file}")
        print(f"Created sprint structure:")
        print(f"  📁 {sprint_dir}/")
        print(f"  📁 {sprint_dir}/tasks/ (ready for task creation)")
        print(f"  📁 {sprint_dir}/daily/ (for daily status links)")
        update_current_symlink(sprint_id)

    elif args.close:
        # Generate retrospective
        retro_file = sprint_dir / "retrospective.md"
        retro_file.write_text(create_retrospective(sprint_id), encoding='utf-8')
        print(f"Created retrospective: {retro_file}")

        # Calculate final velocity
        tasks = collect_tasks()
        metrics = calculate_velocity(tasks)
        print(f"Sprint velocity: {metrics['completed_points']}/{metrics['total_points']} points ({metrics['velocity_percentage']}%)")

    elif args.burndown:
        # Generate and display burndown
        tasks = collect_tasks()
        burndown = generate_ascii_burndown(sprint_id, tasks)
        print(burndown)

        # Save to file
        if sprint_dir.exists():
            burndown_file = sprint_dir / "burndown.md"
            burndown_file.write_text(f"# Burndown Chart\n\n```\n{burndown}\n```", encoding='utf-8')
            print(f"Saved to: {burndown_file}")

    elif args.status:
        # Show current sprint status
        tasks = collect_tasks()
        metrics = calculate_velocity(tasks)

        today = dt.date.today()
        start_date, end_date = get_sprint_dates(sprint_id)
        day_of_sprint = (today - start_date).days + 1
        health = get_sprint_health(tasks, day_of_sprint)

        print(f"Sprint: {sprint_id}")
        print(f"Day {day_of_sprint} of 5")
        print(f"Health: {health}")
        print(f"Progress: {metrics['completed_points']}/{metrics['total_points']} points ({metrics['velocity_percentage']}%)")

    elif args.validate:
        # Validate sprint setup
        issues = []

        if not sprint_dir.exists():
            issues.append(f"Sprint directory does not exist: {sprint_dir}")

        if not (sprint_dir / "plan.md").exists():
            issues.append("Missing sprint plan")

        tasks = collect_tasks()
        if not tasks:
            issues.append("No tasks found")

        if issues:
            print("❌ Validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            return 1
        else:
            print("✅ Sprint validation passed")

    elif args.capacity:
        # Show capacity allocation
        show_capacity(sprint_id)

    return 0

if __name__ == "__main__":
    exit(main())