#!/usr/bin/env python3
"""
Feature management utilities.
- Create new feature scaffolding
- Update feature status
- List feature progress
"""

import argparse
import datetime as dt
from pathlib import Path
from typing import List, Dict

ROOT = Path(__file__).resolve().parents[3] / "project-handbook"
FEATURES_DIR = ROOT / "features"

def create_feature(name: str, epic: bool = False, owner: str = "@owner", stage: str = "proposed"):
    """Create new feature with standard directory structure."""
    feature_dir = FEATURES_DIR / name

    if feature_dir.exists():
        print(f"❌ Feature '{name}' already exists")
        return 1

    # Create directory structure
    feature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / "architecture").mkdir(exist_ok=True)
    (feature_dir / "implementation").mkdir(exist_ok=True)
    (feature_dir / "testing").mkdir(exist_ok=True)
    (feature_dir / "fdr").mkdir(exist_ok=True)

    # Create overview.md
    overview_content = f"""---
title: {name.replace('-', ' ').title()}
type: overview
feature: {name}
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [feature]
links: [./architecture/ARCHITECTURE.md, ./implementation/IMPLEMENTATION.md, ./testing/TESTING.md]
dependencies: []
backlog_items: []  # Related P0-P4 issues from backlog
parking_lot_origin: null  # Original parking lot ID if promoted
capacity_impact: planned  # planned (80%) or reactive (20%)
epic: {str(epic).lower()}
---

# {name.replace('-', ' ').title()}

## Purpose
Brief description of this feature's value and scope.

## Outcomes
- Key outcome 1
- Key outcome 2

## State
- Stage: {stage}
- Owner: {owner}

## Backlog Integration
- Related Issues: []  # List any P0-P4 items this addresses
- Capacity Type: planned  # Uses 80% allocation
- Parking Lot Origin: null  # Set if promoted from parking lot

## Key Links
- [Architecture](./architecture/ARCHITECTURE.md)
- [Implementation](./implementation/IMPLEMENTATION.md)
- [Testing](./testing/TESTING.md)
- [Status](./status.md)
- [Changelog](./changelog.md)
"""

    (feature_dir / "overview.md").write_text(overview_content, encoding='utf-8')

    # Create other required files
    files_to_create = {
        "architecture/ARCHITECTURE.md": f"""---
title: {name.replace('-', ' ').title()} Architecture
type: architecture
feature: {name}
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [architecture]
links: []
---

# Architecture: {name.replace('-', ' ').title()}

## Overview
High-level architecture description.

## Components
- Component 1: Description
- Component 2: Description

## Data Flow
Describe how data flows through the system.

## Dependencies
- External dependency 1
- External dependency 2
""",
        "implementation/IMPLEMENTATION.md": f"""---
title: {name.replace('-', ' ').title()} Implementation
type: implementation
feature: {name}
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [implementation]
links: []
---

# Implementation: {name.replace('-', ' ').title()}

## Development Plan
1. Phase 1: Core functionality
2. Phase 2: Extended features
3. Phase 3: Polish and optimization

## Technical Decisions
- Decision 1: Rationale
- Decision 2: Rationale

## Implementation Notes
Detailed implementation guidance.
""",
        "testing/TESTING.md": f"""---
title: {name.replace('-', ' ').title()} Testing
type: testing
feature: {name}
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [testing]
links: []
---

# Testing: {name.replace('-', ' ').title()}

## Test Strategy
- Unit tests: Coverage expectations
- Integration tests: Key scenarios
- E2E tests: User journeys

## Test Cases
1. Test case 1: Description
2. Test case 2: Description

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
""",
        "status.md": f"""---
title: {name.replace('-', ' ').title()} Status
type: status
feature: {name}
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [status]
links: []
---

# Status: {name.replace('-', ' ').title()}

Stage: {stage}

## Now
- Planning and initial design

## Next
- Architecture definition
- Implementation start

## Risks
- Risk 1: Description and mitigation
- Risk 2: Description and mitigation

## Recent
- Feature created
""",
        "changelog.md": f"""---
title: {name.replace('-', ' ').title()} Changelog
type: changelog
feature: {name}
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [changelog]
links: []
---

# Changelog: {name.replace('-', ' ').title()}

## Unreleased
- Initial feature creation

## [Future Versions]
- To be determined based on implementation progress
""",
        "risks.md": f"""---
title: {name.replace('-', ' ').title()} Risks
type: risks
feature: {name}
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [risks]
links: []
---

# Risk Register: {name.replace('-', ' ').title()}

## High Priority Risks
- **Risk 1**: Description
  - Impact: High/Medium/Low
  - Probability: High/Medium/Low
  - Mitigation: Action plan

## Medium Priority Risks
- **Risk 2**: Description
  - Impact: Medium
  - Probability: Medium
  - Mitigation: Action plan

## Risk Mitigation Strategies
- Strategy 1: Description
- Strategy 2: Description
"""
    }

    for file_path, content in files_to_create.items():
        (feature_dir / file_path).write_text(content, encoding='utf-8')

    epic_note = " (Epic)" if epic else ""
    print(f"✅ Created feature '{name}'{epic_note} with complete directory structure")
    print(f"📁 Location: {feature_dir}")
    print(f"📝 Next steps:")
    print(f"   1. Edit {feature_dir}/overview.md to define the feature")
    print(f"   2. Update {feature_dir}/status.md with current status")
    print(f"   3. Run 'make validate' to check structure")

    return 0

def list_features():
    """List all features with their current status."""
    if not FEATURES_DIR.exists():
        print("❌ No features directory found")
        return

    feature_dirs = [d for d in FEATURES_DIR.iterdir() if d.is_dir()]

    if not feature_dirs:
        print("📁 No features found")
        print("💡 Create one with: make feature-create name=my-feature")
        return

    print("📋 FEATURES OVERVIEW")
    print("=" * 60)

    for feature_dir in sorted(feature_dirs):
        name = feature_dir.name
        status_file = feature_dir / "status.md"
        overview_file = feature_dir / "overview.md"

        # Try to extract stage from status.md
        stage = "unknown"
        epic = False

        if status_file.exists():
            try:
                content = status_file.read_text(encoding='utf-8')
                for line in content.splitlines():
                    if line.startswith("Stage:"):
                        stage = line.split(":", 1)[1].strip()
                        break
            except:
                pass

        if overview_file.exists():
            try:
                content = overview_file.read_text(encoding='utf-8')
                if "epic: true" in content.lower():
                    epic = True
            except:
                pass

        epic_indicator = "🎯" if epic else "📦"
        print(f"{epic_indicator} {name:<25} Stage: {stage}")

def update_feature_status(name: str, stage: str):
    """Update feature status stage."""
    feature_dir = FEATURES_DIR / name
    status_file = feature_dir / "status.md"

    if not status_file.exists():
        print(f"❌ Feature '{name}' not found")
        return 1

    try:
        content = status_file.read_text(encoding='utf-8')
        lines = content.splitlines()

        # Update stage line
        for i, line in enumerate(lines):
            if line.startswith("Stage:"):
                lines[i] = f"Stage: {stage}"
                break

        # Update date in front matter
        for i, line in enumerate(lines):
            if line.startswith("date:"):
                lines[i] = f"date: {dt.date.today().strftime('%Y-%m-%d')}"
                break

        updated_content = "\n".join(lines)
        status_file.write_text(updated_content, encoding='utf-8')
        print(f"✅ Updated '{name}' stage to '{stage}'")

    except Exception as e:
        print(f"❌ Error updating feature: {e}")
        return 1

    return 0

def main():
    parser = argparse.ArgumentParser(description="Feature management")
    parser.add_argument('--create', help='Create new feature with given name')
    parser.add_argument('--epic', action='store_true', help='Mark feature as epic')
    parser.add_argument('--owner', help='Feature owner', default='@owner')
    parser.add_argument('--stage', help='Initial feature stage', default='proposed')
    parser.add_argument('--list', action='store_true', help='List all features')
    parser.add_argument('--update-status', nargs=2, metavar=('NAME', 'STAGE'),
                       help='Update feature status (name stage)')

    args = parser.parse_args()

    if args.create:
        return create_feature(args.create, args.epic, args.owner, args.stage)
    elif args.list:
        list_features()
    elif args.update_status:
        name, stage = args.update_status
        return update_feature_status(name, stage)
    else:
        list_features()

    return 0

if __name__ == "__main__":
    exit(main())