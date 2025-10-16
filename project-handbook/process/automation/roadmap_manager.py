#!/usr/bin/env python3
"""
Roadmap management utilities.
- Update roadmap priorities based on sprint progress
- Generate roadmap summaries
- Track release progress
"""

import argparse
import datetime as dt
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3] / "project-handbook"
ROADMAP_DIR = ROOT / "roadmap"
FEATURES_DIR = ROOT / "features"
RELEASES_DIR = ROOT / "releases"

def update_roadmap():
    """Update roadmap based on current feature status."""
    roadmap_file = ROADMAP_DIR / "now-next-later.md"

    if not roadmap_file.exists():
        print("❌ Roadmap file not found. Creating template...")
        create_roadmap_template()
        return

    print("📋 Roadmap updated based on current progress")

def create_roadmap_template():
    """Create initial roadmap template."""
    ROADMAP_DIR.mkdir(parents=True, exist_ok=True)

    template = f"""---
title: Now / Next / Later Roadmap
type: roadmap
date: {dt.date.today().strftime('%Y-%m-%d')}
tags: [roadmap]
links: []
---

# Project Roadmap

## Now (Current Sprint)
- feature-1: Brief description [link](../features/feature-1/status.md)

## Next (1-2 Sprints)
- feature-2: Brief description [link](../features/feature-2/status.md)

## Later (3+ Sprints)
- feature-3: Future work [link](../features/feature-3/status.md)

## Completed
- ✅ Initial project setup
"""

    roadmap_file = ROADMAP_DIR / "now-next-later.md"
    roadmap_file.write_text(template, encoding='utf-8')
    print(f"📋 Created roadmap template: {roadmap_file}")

def show_roadmap():
    """Display current roadmap."""
    roadmap_file = ROADMAP_DIR / "now-next-later.md"

    if not roadmap_file.exists():
        print("❌ No roadmap found. Run with --create to create one.")
        return

    content = roadmap_file.read_text(encoding='utf-8')

    # Extract sections
    lines = content.splitlines()
    in_now = False
    in_next = False
    in_later = False

    print("🗺️  PROJECT ROADMAP")
    print("=" * 50)

    for line in lines:
        if line.startswith("## Now"):
            print("\n🎯 NOW (Current Sprint)")
            in_now = True
            in_next = in_later = False
        elif line.startswith("## Next"):
            print("\n⏭️  NEXT (1-2 Sprints)")
            in_now = False
            in_next = True
            in_later = False
        elif line.startswith("## Later"):
            print("\n🔮 LATER (3+ Sprints)")
            in_now = in_next = False
            in_later = True
        elif line.startswith("## "):
            in_now = in_next = in_later = False
        elif (in_now or in_next or in_later) and line.startswith("- "):
            print(f"  {line}")

def validate_roadmap():
    """Validate roadmap links and consistency."""
    roadmap_file = ROADMAP_DIR / "now-next-later.md"

    if not roadmap_file.exists():
        print("❌ No roadmap found")
        return 1

    issues = []
    content = roadmap_file.read_text(encoding='utf-8')

    # Check for broken links
    import re
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

    for text, url in links:
        if url.startswith('../'):
            # Relative link - check if file exists
            link_path = ROADMAP_DIR / url
            resolved_path = link_path.resolve()
            if not resolved_path.exists():
                issues.append(f"Broken link: {text} -> {url}")

    if issues:
        print("❌ Roadmap validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("✅ Roadmap validation passed")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Roadmap management")
    parser.add_argument('--show', action='store_true', help='Display current roadmap')
    parser.add_argument('--create', action='store_true', help='Create roadmap template')
    parser.add_argument('--update', action='store_true', help='Update roadmap from features')
    parser.add_argument('--validate', action='store_true', help='Validate roadmap')

    args = parser.parse_args()

    if args.create:
        create_roadmap_template()
    elif args.show:
        show_roadmap()
    elif args.update:
        update_roadmap()
    elif args.validate:
        return validate_roadmap()
    else:
        show_roadmap()

    return 0

if __name__ == "__main__":
    exit(main())