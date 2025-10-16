#!/usr/bin/env python3
"""
Release management system.
- Plan releases with feature assignments and sprint timeline
- Track release progress across multiple sprints
- Generate release notes and changelogs
- Coordinate between roadmap planning and sprint execution
"""

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[3] / "project-handbook"
RELEASES_DIR = ROOT / "releases"
SPRINTS_DIR = ROOT / "sprints"
FEATURES_DIR = ROOT / "features"

def get_current_sprint_id() -> str:
    """Get current sprint ID."""
    today = dt.date.today()
    week_num = today.isocalendar()[1]
    year = today.year
    return f"SPRINT-{year}-W{week_num:02d}"

def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse semantic version string."""
    if not version.startswith('v'):
        version = 'v' + version

    version_clean = version[1:]  # Remove 'v'
    parts = version_clean.split('.')

    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return major, minor, patch
    except:
        return 1, 0, 0

def calculate_sprint_range(start_sprint: str, sprint_count: int) -> List[str]:
    """Calculate sprint IDs for release timeline."""
    # Parse start sprint
    parts = start_sprint.split('-')
    year = int(parts[1])
    week = int(parts[2][1:])  # Remove 'W'

    sprint_ids = []
    for i in range(sprint_count):
        current_week = week + i
        sprint_id = f"SPRINT-{year}-W{current_week:02d}"
        sprint_ids.append(sprint_id)

    return sprint_ids

def create_release_structure(version: str, sprint_count: int, start_sprint: str = None) -> Path:
    """Create release directory structure."""
    if not version.startswith('v'):
        version = 'v' + version

    if start_sprint is None:
        start_sprint = get_current_sprint_id()

    # Create directory structure
    release_dir = RELEASES_DIR / version
    release_dir.mkdir(parents=True, exist_ok=True)

    # Calculate sprint timeline
    sprint_ids = calculate_sprint_range(start_sprint, sprint_count)
    end_sprint = sprint_ids[-1]

    # Create plan.md
    plan_content = f"""---
title: Release {version} Plan
type: release-plan
version: {version}
start_sprint: {start_sprint}
end_sprint: {end_sprint}
planned_sprints: {sprint_count}
status: planned
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [release, planning]
links: []
---

# Release {version}

## Release Summary
Brief description of what this release delivers.

## Release Goals
1. **Primary Goal**: Main feature or capability
2. **Secondary Goal**: Supporting features
3. **Stretch Goal**: Nice-to-have if time permits

## Sprint Timeline
"""

    for i, sprint_id in enumerate(sprint_ids, 1):
        plan_content += f"- **{sprint_id}** (Sprint {i} of {sprint_count}): Sprint theme/focus\n"

    plan_content += f"""

## Feature Assignments
*Use `make release-add-feature` to assign features to this release*

## Success Criteria
- [ ] All assigned features complete
- [ ] Performance benchmarks met
- [ ] Quality gates passed
- [ ] Documentation updated

## Risk Management
- Critical path: (Identify critical features)
- Dependencies: (External dependencies)
- Capacity: (Team availability considerations)

## Release Notes Draft
*Auto-generated from completed tasks and features*
"""

    (release_dir / "plan.md").write_text(plan_content, encoding='utf-8')

    # Create features.yaml
    features_content = f"""# Feature assignments for {version}
# Auto-managed by release commands

version: {version}
start_sprint: {start_sprint}
end_sprint: {end_sprint}
planned_sprints: {sprint_count}

features:
  # Features will be added with: make release-add-feature
  # Example:
  # auth-system:
  #   type: epic
  #   priority: P0
  #   sprints: [SPRINT-2025-W38, SPRINT-2025-W39, SPRINT-2025-W40]
  #   status: in_progress
  #   critical_path: true
"""

    (release_dir / "features.yaml").write_text(features_content, encoding='utf-8')

    # Create progress tracking file
    progress_content = f"""---
title: Release {version} Progress
type: release-progress
version: {version}
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [release, progress]
links: []
---

# Release {version} Progress

*This file is auto-generated. Do not edit manually.*

## Sprint Progress
"""

    for i, sprint_id in enumerate(sprint_ids, 1):
        status = "✅ Complete" if i == 1 else ("🔄 In Progress" if sprint_id == get_current_sprint_id() else "⭕ Planned")
        progress_content += f"- **{sprint_id}**: {status}\n"

    progress_content += """

## Feature Progress
*Updated automatically from feature status files*

## Task Completion
*Updated automatically from sprint tasks*

## Release Health
*Calculated from sprint velocity and feature completion*
"""

    (release_dir / "progress.md").write_text(progress_content, encoding='utf-8')

    return release_dir

def load_release_features(version: str) -> Dict:
    """Load feature assignments for a release."""
    if not version.startswith('v'):
        version = 'v' + version

    features_file = RELEASES_DIR / version / "features.yaml"

    if not features_file.exists():
        return {}

    try:
        content = features_file.read_text(encoding='utf-8')
        # Simple YAML parsing for features section
        features = {}
        in_features = False
        current_feature = None

        for line in content.splitlines():
            line = line.rstrip()

            if line.startswith('features:'):
                in_features = True
                continue

            # Skip comments and empty lines
            if not line.strip() or line.strip().startswith('#'):
                continue

            if in_features:
                if line.startswith('  ') and ':' in line and not line.startswith('    '):
                    # New feature (2-space indent)
                    current_feature = line.strip().split(':')[0]
                    if current_feature:  # Make sure it's not empty
                        features[current_feature] = {}
                elif current_feature and line.startswith('    ') and ':' in line:
                    # Feature property (4-space indent)
                    key, value = line.strip().split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if not key or not current_feature:
                        continue

                    if value.startswith('[') and value.endswith(']'):
                        # Parse list
                        items = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
                        features[current_feature][key] = items
                    elif value.lower() in ['true', 'false']:
                        features[current_feature][key] = value.lower() == 'true'
                    elif value.isdigit():
                        features[current_feature][key] = int(value)
                    else:
                        features[current_feature][key] = value

        return features
    except Exception as e:
        print(f"Error parsing {features_file}: {e}")
        return {}

def add_feature_to_release(version: str, feature: str, feature_type: str = "regular",
                          priority: str = "P1", critical_path: bool = False):
    """Add feature to release."""
    if not version.startswith('v'):
        version = 'v' + version

    features_file = RELEASES_DIR / version / "features.yaml"

    if not features_file.exists():
        print(f"❌ Release {version} not found. Create with: make release-plan")
        return False

    # Load current features
    features = load_release_features(version)

    # Add new feature
    features[feature] = {
        'type': feature_type,
        'priority': priority,
        'status': 'planned',
        'completion': 0,
        'critical_path': critical_path
    }

    # Write back (simple format)
    try:
        content = features_file.read_text(encoding='utf-8')
        lines = content.splitlines()

        # Find features section and replace
        new_lines = []
        in_features = False

        for line in lines:
            if line.strip().startswith('features:'):
                new_lines.append(line)
                in_features = True

                # Add all features
                for feat_name, feat_data in features.items():
                    new_lines.append(f"  {feat_name}:")
                    for key, value in feat_data.items():
                        if isinstance(value, list):
                            value_str = '[' + ', '.join(value) + ']'
                        else:
                            value_str = str(value)
                        new_lines.append(f"    {key}: {value_str}")
                    new_lines.append("")

            elif in_features and (not line.strip() or line.startswith('features:') or
                                not line.startswith(' ')):
                in_features = False
                if line.strip():
                    new_lines.append(line)
            elif not in_features:
                new_lines.append(line)

        features_file.write_text('\n'.join(new_lines), encoding='utf-8')
        print(f"✅ Added {feature} to release {version}")
        return True

    except Exception as e:
        print(f"❌ Error updating release: {e}")
        return False

def get_current_release() -> Optional[str]:
    """Get current active release."""
    current_link = RELEASES_DIR / "current"

    if current_link.exists() and current_link.is_symlink():
        target = current_link.readlink()
        return target.name

    return None

def calculate_release_progress(version: str) -> Dict:
    """Calculate release progress from features and sprints."""
    if not version.startswith('v'):
        version = 'v' + version

    # Load release features
    features = load_release_features(version)

    if not features:
        return {}

    # Get feature completion from sprint task system
    feature_completions = {}

    # Import task collection function
    try:
        import sys
        sys.path.append(str(ROOT / 'process' / 'automation'))
        from feature_status_updater import collect_all_sprint_tasks, calculate_feature_metrics

        tasks_by_feature = collect_all_sprint_tasks()

        for feature_name in features.keys():
            if feature_name in tasks_by_feature:
                tasks = tasks_by_feature[feature_name]
                metrics = calculate_feature_metrics(tasks)
                feature_completions[feature_name] = metrics.get('completion_percentage', 0)
            else:
                feature_completions[feature_name] = 0

    except Exception as e:
        print(f"Warning: Could not calculate feature completion: {e}")
        feature_completions = {fname: 0 for fname in features.keys()}

    # Calculate overall release progress
    total_features = len(features)
    completed_features = 0
    total_completion = 0
    critical_path_complete = True

    for feature_name, feature_data in features.items():
        completion = feature_completions.get(feature_name, 0)
        total_completion += completion

        if completion >= 90:  # Consider 90%+ as complete
            completed_features += 1

        if feature_data.get('critical_path') and completion < 90:
            critical_path_complete = False

    avg_completion = total_completion // total_features if total_features > 0 else 0

    # Determine release health
    if avg_completion >= 90 and critical_path_complete:
        health = "🟢 GREEN - Ready for release"
    elif avg_completion >= 70 and critical_path_complete:
        health = "🟡 YELLOW - On track"
    elif critical_path_complete:
        health = "🟡 YELLOW - Some features behind"
    else:
        health = "🔴 RED - Critical path at risk"

    return {
        'total_features': total_features,
        'completed_features': completed_features,
        'avg_completion': avg_completion,
        'critical_path_complete': critical_path_complete,
        'health': health,
        'feature_completions': feature_completions
    }

def show_release_status(version: str = None):
    """Show detailed release status."""
    if version is None:
        version = get_current_release()

    if not version:
        print("❌ No current release found")
        print("💡 Create one with: make release-plan version=v1.2.0 sprints=3")
        return

    if not version.startswith('v'):
        version = 'v' + version

    release_dir = RELEASES_DIR / version
    if not release_dir.exists():
        print(f"❌ Release {version} not found")
        return

    # Load release data
    features = load_release_features(version)
    progress = calculate_release_progress(version)

    # Load plan metadata
    plan_file = release_dir / "plan.md"
    sprint_count = 3  # Default
    start_sprint = get_current_sprint_id()

    if plan_file.exists():
        content = plan_file.read_text(encoding='utf-8')
        for line in content.splitlines():
            if line.startswith('planned_sprints:'):
                sprint_count = int(line.split(':')[1].strip())
            elif line.startswith('start_sprint:'):
                start_sprint = line.split(':')[1].strip()

    # Calculate current sprint position
    current_sprint = get_current_sprint_id()
    sprint_timeline = calculate_sprint_range(start_sprint, sprint_count)

    try:
        current_sprint_index = sprint_timeline.index(current_sprint) + 1
    except ValueError:
        current_sprint_index = 1

    print(f"📦 RELEASE STATUS: {version}")
    print("=" * 60)
    print(f"Sprint: {current_sprint_index} of {sprint_count} ({current_sprint})")
    print(f"Overall Progress: {progress.get('avg_completion', 0)}% complete")
    print(f"Target: {sprint_timeline[-1] if sprint_timeline else 'TBD'}")
    print(f"Release Health: {progress.get('health', 'Unknown')}")
    print()

    # Feature progress
    if features:
        print("🎯 Feature Progress:")
        for feature_name, feature_data in features.items():
            completion = progress.get('feature_completions', {}).get(feature_name, 0)
            status_emoji = "✅" if completion >= 90 else ("🔄" if completion > 0 else "⭕")
            critical_indicator = " (Critical Path)" if feature_data.get('critical_path') else ""

            print(f"{status_emoji} {feature_name:<20} {completion:3d}% complete{critical_indicator}")
        print()

    # Sprint breakdown
    print("📅 Sprint Breakdown:")
    for i, sprint_id in enumerate(sprint_timeline, 1):
        if sprint_id == current_sprint:
            status = "🔄 In progress"
        elif i < current_sprint_index:
            status = "✅ Complete"
        else:
            status = "⭕ Planned"

        print(f"{status} {sprint_id} (Sprint {i} of {sprint_count})")

def create_release_plan(version: str, sprint_count: int, start_sprint: str = None):
    """Create new release plan."""
    if not version.startswith('v'):
        version = 'v' + version

    release_dir = create_release_structure(version, sprint_count, start_sprint)

    # Update current symlink
    current_link = RELEASES_DIR / "current"
    if current_link.exists() or current_link.is_symlink():
        current_link.unlink()

    current_link.symlink_to(version)

    print(f"✅ Created release plan: {version}")
    print(f"📁 Location: {release_dir}")
    print(f"📅 Timeline: {sprint_count} sprints starting {start_sprint or get_current_sprint_id()}")
    print(f"📝 Next steps:")
    print(f"   1. Edit {release_dir}/plan.md to define release goals")
    print(f"   2. Add features: make release-add-feature release={version} feature=feature-name")
    print(f"   3. Review timeline and adjust if needed")

def suggest_release_features(version: str):
    """Suggest features for release based on current status."""
    print(f"💡 SUGGESTED FEATURES FOR {version}")
    print("=" * 50)

    # Get features that are ready or in progress
    if FEATURES_DIR.exists():
        for feature_dir in FEATURES_DIR.iterdir():
            if not feature_dir.is_dir():
                continue

            status_file = feature_dir / "status.md"
            if status_file.exists():
                try:
                    content = status_file.read_text(encoding='utf-8')
                    stage = "unknown"

                    for line in content.splitlines():
                        if line.startswith("Stage:"):
                            stage = line.split(":", 1)[1].strip()
                            break

                    # Suggest based on stage
                    if stage in ['approved', 'developing', 'in_progress']:
                        print(f"📦 {feature_dir.name:<20} Stage: {stage} - Good candidate")
                    elif stage in ['proposed', 'planned']:
                        print(f"🤔 {feature_dir.name:<20} Stage: {stage} - Needs approval")

                except:
                    pass

def close_release(version: str):
    """Close release and generate final artifacts."""
    if not version.startswith('v'):
        version = 'v' + version

    release_dir = RELEASES_DIR / version
    if not release_dir.exists():
        print(f"❌ Release {version} not found")
        return False

    # Generate changelog from completed tasks
    changelog_content = f"""---
title: Release {version} Changelog
type: changelog
version: {version}
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [changelog, release]
links: []
---

# Changelog: {version}

## Release Summary
Released on {dt.date.today().strftime('%B %d, %Y')}

## Features Delivered
"""

    # Get features for this release
    features = load_release_features(version)
    for feature_name in features.keys():
        changelog_content += f"- **{feature_name}**: Feature description\n"

    changelog_content += """

## Tasks Completed
*Auto-generated from sprint tasks*

## Breaking Changes
- None

## Migration Guide
- No migration required

## Known Issues
- None

## Contributors
- Team members who contributed
"""

    (release_dir / "changelog.md").write_text(changelog_content, encoding='utf-8')

    # Move to delivered
    delivered_dir = RELEASES_DIR / "delivered"
    delivered_dir.mkdir(exist_ok=True)

    print(f"✅ Release {version} closed")
    print(f"📋 Generated changelog: {release_dir}/changelog.md")
    print(f"📈 Ready for deployment")

    return True

def main():
    parser = argparse.ArgumentParser(description="Release management")

    # Release lifecycle
    parser.add_argument('--plan', help='Create release plan (version)')
    parser.add_argument('--sprints', type=int, help='Number of sprints for release', default=3)
    parser.add_argument('--start-sprint', help='Starting sprint ID')

    # Feature management
    parser.add_argument('--add-feature', nargs=2, metavar=('RELEASE', 'FEATURE'),
                       help='Add feature to release')
    parser.add_argument('--epic', action='store_true', help='Mark feature as epic')
    parser.add_argument('--critical', action='store_true', help='Mark as critical path')

    # Status and tracking
    parser.add_argument('--status', help='Show release status (version, or current)')
    parser.add_argument('--progress', help='Show detailed progress (version)')
    parser.add_argument('--suggest', help='Suggest features for release (version)')

    # Release completion
    parser.add_argument('--close', help='Close and deliver release (version)')

    # Utilities
    parser.add_argument('--list', action='store_true', help='List all releases')
    parser.add_argument('--current', action='store_true', help='Show current release')

    args = parser.parse_args()

    if args.plan:
        create_release_plan(args.plan, args.sprints, args.start_sprint)

    elif args.add_feature:
        release_version, feature = args.add_feature
        feature_type = "epic" if args.epic else "regular"
        add_feature_to_release(release_version, feature, feature_type,
                             critical_path=args.critical)

    elif args.status:
        if args.status == "current":
            show_release_status()
        else:
            show_release_status(args.status)

    elif args.suggest:
        suggest_release_features(args.suggest)

    elif args.close:
        close_release(args.close)

    elif args.current:
        current = get_current_release()
        if current:
            print(f"Current release: {current}")
            show_release_status(current)
        else:
            print("No current release set")

    elif args.list:
        if RELEASES_DIR.exists():
            releases = [d.name for d in RELEASES_DIR.iterdir()
                       if d.is_dir() and d.name.startswith('v')]
            if releases:
                print("📦 RELEASES")
                for release in sorted(releases):
                    current_indicator = " (current)" if release == get_current_release() else ""
                    print(f"  {release}{current_indicator}")
            else:
                print("📦 No releases found")
        else:
            print("📦 No releases directory")

    else:
        # Default: show current release status
        show_release_status()

    return 0

if __name__ == "__main__":
    exit(main())