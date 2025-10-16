#!/usr/bin/env python3
"""
Feature status auto-updater.
- Collects tasks from all sprints for each feature
- Calculates feature-level metrics
- Updates "Active Work" sections in feature status.md files
- Maintains manual sections while auto-generating data sections
"""

import argparse
import datetime as dt
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[3] / "project-handbook"
FEATURES_DIR = ROOT / "features"
SPRINTS_DIR = ROOT / "sprints"

def collect_all_sprint_tasks() -> Dict[str, List[Dict]]:
    """Collect all tasks from all sprints, grouped by feature."""
    tasks_by_feature = {}

    if not SPRINTS_DIR.exists():
        return tasks_by_feature

    for year_dir in SPRINTS_DIR.iterdir():
        if not year_dir.is_dir() or year_dir.name == "current":
            continue

        for sprint_dir in year_dir.iterdir():
            if not sprint_dir.is_dir() or not sprint_dir.name.startswith("SPRINT-"):
                continue

            tasks_dir = sprint_dir / "tasks"
            if not tasks_dir.exists():
                continue

            sprint_id = sprint_dir.name

            for task_dir in tasks_dir.iterdir():
                if not task_dir.is_dir():
                    continue

                task_yaml = task_dir / "task.yaml"
                if not task_yaml.exists():
                    continue

                try:
                    # Parse task.yaml
                    content = task_yaml.read_text(encoding='utf-8')
                    task_data = {"sprint": sprint_id}

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

                    feature = task_data.get('feature', 'unknown')
                    tasks_by_feature.setdefault(feature, []).append(task_data)

                except Exception as e:
                    print(f"Error parsing {task_yaml}: {e}")

    return tasks_by_feature

def calculate_feature_metrics(tasks: List[Dict]) -> Dict:
    """Calculate feature-level metrics from tasks."""
    if not tasks:
        return {}

    # Organize by status
    by_status = {
        'done': [],
        'doing': [],
        'review': [],
        'todo': [],
        'blocked': []
    }

    total_points = 0
    completed_points = 0

    for task in tasks:
        status = task.get('status', 'todo')
        points = task.get('story_points', 0)
        total_points += points

        # Normalize status
        if status in ['done', 'completed']:
            by_status['done'].append(task)
            completed_points += points
        elif status in ['doing', 'in_progress', 'in-progress']:
            by_status['doing'].append(task)
        elif status == 'review':
            by_status['review'].append(task)
        elif status == 'blocked':
            by_status['blocked'].append(task)
        else:
            by_status['todo'].append(task)

    # Calculate velocity and estimates
    completion_percentage = int(completed_points * 100 / total_points) if total_points > 0 else 0

    # Estimate completion (simplified - would need historical velocity)
    remaining_points = total_points - completed_points
    avg_velocity = 21  # Default velocity, could be calculated from sprint history
    estimated_sprints = max(1, remaining_points // avg_velocity)

    today = dt.date.today()
    week_num = today.isocalendar()[1]
    estimated_completion_week = week_num + estimated_sprints
    year = today.year
    estimated_sprint = f"SPRINT-{year}-W{estimated_completion_week:02d}"

    return {
        'total_points': total_points,
        'completed_points': completed_points,
        'completion_percentage': completion_percentage,
        'remaining_points': remaining_points,
        'estimated_completion': estimated_sprint,
        'avg_velocity': avg_velocity,
        'by_status': by_status
    }

def get_current_sprint() -> str:
    """Get current sprint ID."""
    today = dt.date.today()
    week_num = today.isocalendar()[1]
    year = today.year
    return f"SPRINT-{year}-W{week_num:02d}"

def format_active_work_section(feature: str, tasks: List[Dict], metrics: Dict) -> str:
    """Generate the Active Work section for a feature."""
    current_sprint = get_current_sprint()

    # Group tasks by sprint and status
    current_tasks = [t for t in tasks if t.get('sprint') == current_sprint]
    recent_completed = [t for t in tasks if t.get('status') == 'done'][-5:]  # Last 5 completed
    blocked_tasks = [t for t in tasks if t.get('status') == 'blocked']

    section = "## Active Work (auto-generated)\n"
    section += f"*Last updated: {dt.date.today().strftime('%Y-%m-%d')}*\n\n"

    # Current sprint tasks
    if current_tasks:
        section += f"### Current Sprint ({current_sprint})\n"
        for task in current_tasks:
            status_emoji = {
                'todo': '⭕',
                'doing': '🔄',
                'review': '👀',
                'done': '✅',
                'blocked': '🚫'
            }.get(task.get('status'), '❓')

            points = task.get('story_points', 0)
            owner = task.get('owner', '@unassigned')
            title = task.get('title', 'Untitled')
            task_id = task.get('id', 'UNKNOWN')

            section += f"- {status_emoji} {task_id}: {title} ({points}pts, {owner})\n"
        section += "\n"
    else:
        section += f"### Current Sprint ({current_sprint})\n"
        section += "- No active tasks in current sprint\n\n"

    # Recent completed work
    if recent_completed:
        section += "### Recent Completed (last 5 tasks)\n"
        for task in recent_completed:
            points = task.get('story_points', 0)
            sprint = task.get('sprint', 'UNKNOWN')
            title = task.get('title', 'Untitled')
            task_id = task.get('id', 'UNKNOWN')
            section += f"- ✅ {task_id}: {title} ({points}pts) - {sprint}\n"
        section += "\n"

    # Blocked items
    if blocked_tasks:
        section += "### Blocked Items\n"
        for task in blocked_tasks:
            points = task.get('story_points', 0)
            title = task.get('title', 'Untitled')
            task_id = task.get('id', 'UNKNOWN')
            section += f"- 🚫 {task_id}: {title} ({points}pts)\n"
        section += "\n"

    # Feature metrics
    section += "### Metrics\n"
    section += f"- **Total Story Points**: {metrics['total_points']} (planned)\n"
    section += f"- **Completed Points**: {metrics['completed_points']} ({metrics['completion_percentage']}%)\n"
    section += f"- **Remaining Points**: {metrics['remaining_points']}\n"
    section += f"- **Estimated Completion**: {metrics['estimated_completion']}\n"
    section += f"- **Average Velocity**: {metrics['avg_velocity']} points/sprint\n\n"

    return section

def update_feature_status_file(feature: str, tasks: List[Dict]):
    """Update a feature's status.md file with auto-generated sections."""
    feature_dir = FEATURES_DIR / feature
    status_file = feature_dir / "status.md"

    if not status_file.exists():
        print(f"⚠️  Feature status file not found: {status_file}")
        return False

    try:
        content = status_file.read_text(encoding='utf-8')
        metrics = calculate_feature_metrics(tasks)

        # Split content into manual and auto-generated sections
        lines = content.splitlines()
        manual_lines = []
        in_auto_section = False

        for line in lines:
            if line.startswith("## Active Work (auto-generated)"):
                in_auto_section = True
                break
            elif line.startswith("Active Work (generated)"):
                # Legacy format
                in_auto_section = True
                break
            else:
                manual_lines.append(line)

        # Keep manual content
        manual_content = "\n".join(manual_lines).rstrip()

        # Generate new auto section
        auto_section = format_active_work_section(feature, tasks, metrics)

        # Combine
        updated_content = manual_content + "\n\n" + auto_section

        # Update the file
        status_file.write_text(updated_content, encoding='utf-8')
        print(f"✅ Updated {feature} status with {len(tasks)} tasks, {metrics['completion_percentage']}% complete")

        return True

    except Exception as e:
        print(f"❌ Error updating {feature} status: {e}")
        return False

def update_all_feature_status():
    """Update all feature status files with current sprint data."""
    tasks_by_feature = collect_all_sprint_tasks()

    if not tasks_by_feature:
        print("📋 No sprint tasks found")
        return

    updated_count = 0
    for feature, tasks in tasks_by_feature.items():
        if feature == 'unknown':
            continue

        if update_feature_status_file(feature, tasks):
            updated_count += 1

    print(f"\n🎯 Updated {updated_count} feature status files")
    print(f"📊 Features with active work: {len([f for f, t in tasks_by_feature.items() if f != 'unknown' and t])}")

def show_feature_summary():
    """Show summary of all features with sprint task data."""
    tasks_by_feature = collect_all_sprint_tasks()

    print("🎯 FEATURE SUMMARY WITH SPRINT DATA")
    print("=" * 60)

    for feature, tasks in sorted(tasks_by_feature.items()):
        if feature == 'unknown':
            continue

        metrics = calculate_feature_metrics(tasks)

        # Count current sprint tasks
        current_sprint = get_current_sprint()
        current_tasks = len([t for t in tasks if t.get('sprint') == current_sprint])

        # Status indicators
        if metrics['completion_percentage'] >= 90:
            status_emoji = "🎉"  # Nearly done
        elif metrics['completion_percentage'] >= 50:
            status_emoji = "🔄"  # In progress
        elif current_tasks > 0:
            status_emoji = "⚡"  # Active
        else:
            status_emoji = "💤"  # Dormant

        print(f"{status_emoji} {feature:<25} "
              f"{metrics['completed_points']:3d}/{metrics['total_points']:3d} pts "
              f"({metrics['completion_percentage']:3d}%) "
              f"Current: {current_tasks} tasks")

def main():
    parser = argparse.ArgumentParser(description="Feature status auto-updater")
    parser.add_argument('--update-all', action='store_true',
                       help='Update all feature status files')
    parser.add_argument('--update-feature',
                       help='Update specific feature status')
    parser.add_argument('--summary', action='store_true',
                       help='Show feature summary with sprint data')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be updated without making changes')

    args = parser.parse_args()

    if args.summary:
        show_feature_summary()
    elif args.update_feature:
        tasks_by_feature = collect_all_sprint_tasks()
        tasks = tasks_by_feature.get(args.update_feature, [])
        if tasks:
            update_feature_status_file(args.update_feature, tasks)
        else:
            print(f"❌ No tasks found for feature: {args.update_feature}")
    elif args.update_all:
        if args.dry_run:
            tasks_by_feature = collect_all_sprint_tasks()
            print("🔍 DRY RUN - Would update:")
            for feature, tasks in tasks_by_feature.items():
                if feature != 'unknown' and tasks:
                    metrics = calculate_feature_metrics(tasks)
                    print(f"  - {feature}: {len(tasks)} tasks, {metrics['completion_percentage']}% complete")
        else:
            update_all_feature_status()
    else:
        show_feature_summary()

    return 0

if __name__ == "__main__":
    exit(main())