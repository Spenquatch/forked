#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import argparse
import re

class ParkingLotManager:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).absolute()
        self.parking_lot_dir = self.project_root / "parking-lot"
        self.index_file = self.parking_lot_dir / "index.json"
        self.roadmap_dir = self.project_root / "roadmap"
        
    def add_item(self, item_type, title, desc="", owner="", tags=None):
        """Add a new item to the parking lot"""
        if item_type not in ['features', 'technical-debt', 'research', 'external-requests']:
            print(f"Error: Invalid type '{item_type}'")
            print("Valid types: features, technical-debt, research, external-requests")
            return False
            
        # Create directory structure
        type_dir = self.parking_lot_dir / item_type
        type_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate item ID
        item_id = self._generate_item_id(item_type, title)
        item_dir = type_dir / item_id
        
        if item_dir.exists():
            print(f"Error: Item '{item_id}' already exists")
            return False
            
        item_dir.mkdir(parents=True)
        
        # Create README.md with front matter
        readme_path = item_dir / "README.md"
        front_matter = {
            "title": title,
            "type": item_type,
            "status": "parking-lot",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "owner": owner or "unassigned",
            "tags": tags or [],
            "description": desc
        }
        
        content = f"""---
title: {front_matter['title']}
type: {front_matter['type']}
status: {front_matter['status']}
created: {front_matter['created']}
owner: {front_matter['owner']}
tags: {json.dumps(front_matter['tags'])}
---

# {title}

{desc}

## Context

_Add context and background information here_

## Potential Value

_Describe the potential value this could bring_

## Considerations

_Note any technical, resource, or timing considerations_
"""
        
        readme_path.write_text(content)
        print(f"✅ Created parking lot item: {item_id}")
        print(f"   Location: {item_dir.relative_to(self.project_root)}")
        
        # Update index
        self.update_index()
        return True
        
    def _generate_item_id(self, item_type, title):
        """Generate a clean ID from type and title"""
        # Create prefix based on type
        prefix_map = {
            "features": "FEAT",
            "technical-debt": "DEBT",
            "research": "RES",
            "external-requests": "EXT"
        }
        prefix = prefix_map[item_type]
        
        # Clean title for ID
        clean_title = re.sub(r'[^a-zA-Z0-9-]', '-', title.lower())
        clean_title = re.sub(r'-+', '-', clean_title).strip('-')[:30]
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d")
        
        return f"{prefix}-{timestamp}-{clean_title}"
        
    def update_index(self):
        """Update the index.json file by scanning all directories"""
        index_data = {
            "last_updated": datetime.now().isoformat(),
            "total_items": 0,
            "by_category": {
                "features": [],
                "technical-debt": [],
                "research": [],
                "external-requests": []
            },
            "items": []
        }
        
        for category in index_data["by_category"].keys():
            category_dir = self.parking_lot_dir / category
            if not category_dir.exists():
                continue
                
            for item_dir in category_dir.iterdir():
                if not item_dir.is_dir():
                    continue
                    
                readme_path = item_dir / "README.md"
                if not readme_path.exists():
                    continue
                    
                # Parse front matter
                item_info = self._parse_front_matter(readme_path)
                if item_info:
                    item_info["id"] = item_dir.name
                    item_info["path"] = str(item_dir.relative_to(self.project_root))
                    
                    index_data["items"].append(item_info)
                    index_data["by_category"][category].append(item_info["id"])
                    index_data["total_items"] += 1
        
        # Sort items by created date (newest first)
        index_data["items"].sort(key=lambda x: x.get("created", ""), reverse=True)
        
        # Write index file
        self.index_file.write_text(json.dumps(index_data, indent=2))
        print(f"📊 Updated parking lot index: {index_data['total_items']} items")
        
    def _parse_front_matter(self, file_path):
        """Parse YAML front matter from a markdown file"""
        content = file_path.read_text()
        if not content.startswith("---"):
            return None
            
        try:
            # Extract front matter
            end_marker = content.find("---", 3)
            if end_marker == -1:
                return None
                
            front_matter = content[3:end_marker].strip()
            
            # Parse manually (avoiding yaml dependency)
            result = {}
            for line in front_matter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle JSON arrays
                    if value.startswith('['):
                        try:
                            value = json.loads(value)
                        except:
                            pass
                    
                    result[key] = value
                    
            # Extract description from content after front matter
            content_start = content.find("\n", end_marker + 3)
            if content_start != -1:
                lines = content[content_start:].strip().split('\n')
                for line in lines:
                    if line and not line.startswith('#'):
                        result['description'] = line.strip()
                        break
                        
            return result
        except Exception as e:
            print(f"Warning: Could not parse front matter from {file_path}: {e}")
            return None
            
    def list_items(self, category=None, format="table"):
        """List all parking lot items"""
        if not self.index_file.exists():
            self.update_index()
            
        index_data = json.loads(self.index_file.read_text())
        
        if format == "json":
            print(json.dumps(index_data, indent=2))
            return
            
        print("\n📦 PARKING LOT ITEMS")
        print("=" * 80)
        
        if index_data["total_items"] == 0:
            print("No items in parking lot")
            return
            
        # Group by category
        for cat in ['features', 'technical-debt', 'research', 'external-requests']:
            if category and category != cat:
                continue
                
            items = [item for item in index_data["items"] if item.get("type") == cat]
            if not items:
                continue
                
            print(f"\n📁 {cat.upper().replace('-', ' ')} ({len(items)} items)")
            print("-" * 40)
            
            for item in items:
                created = item.get('created', 'unknown')
                owner = item.get('owner', 'unassigned')
                title = item.get('title', item['id'])
                tags = item.get('tags', [])
                
                print(f"  • {item['id']}")
                print(f"    {title}")
                print(f"    Created: {created} | Owner: {owner}")
                if tags:
                    print(f"    Tags: {', '.join(tags)}")
                print()
                
        print(f"\nTotal items: {index_data['total_items']}")
        print(f"Last updated: {index_data.get('last_updated', 'never')}")
        
    def review_items(self):
        """Interactive review of parking lot items for quarterly planning"""
        if not self.index_file.exists():
            self.update_index()
            
        index_data = json.loads(self.index_file.read_text())
        
        if index_data["total_items"] == 0:
            print("No items to review")
            return
            
        print("\n🔍 PARKING LOT QUARTERLY REVIEW")
        print("=" * 80)
        print("Review each item and decide its fate:")
        print("  [p]romote to roadmap")
        print("  [d]elete/archive")
        print("  [s]kip (keep in parking lot)")
        print("  [q]uit review\n")
        
        decisions = []
        
        for item in index_data["items"]:
            print("-" * 40)
            print(f"ID: {item['id']}")
            print(f"Type: {item.get('type', 'unknown')}")
            print(f"Title: {item.get('title', 'Untitled')}")
            print(f"Created: {item.get('created', 'unknown')}")
            print(f"Owner: {item.get('owner', 'unassigned')}")
            
            desc = item.get('description', '')
            if desc:
                print(f"Description: {desc[:200]}..." if len(desc) > 200 else f"Description: {desc}")
                
            # Show full content if requested
            while True:
                action = input("\nAction ([p]romote/[d]elete/[s]kip/[v]iew full/[q]uit): ").lower().strip()
                
                if action == 'q':
                    break
                elif action == 'v':
                    # Show full content
                    item_path = self.project_root / item['path'] / "README.md"
                    if item_path.exists():
                        print("\n--- Full Content ---")
                        print(item_path.read_text())
                        print("--- End Content ---\n")
                    continue
                elif action in ['p', 'd', 's']:
                    decisions.append({"item": item, "action": action})
                    break
                else:
                    print("Invalid action. Please choose p/d/s/v/q")
                    
            if action == 'q':
                break
                
        # Process decisions
        print("\n" + "=" * 40)
        print("REVIEW SUMMARY")
        print("=" * 40)
        
        promoted = [d for d in decisions if d['action'] == 'p']
        deleted = [d for d in decisions if d['action'] == 'd']
        kept = [d for d in decisions if d['action'] == 's']
        
        if promoted:
            print(f"\n✅ Items to promote ({len(promoted)}):")
            for d in promoted:
                print(f"  • {d['item']['id']}: {d['item'].get('title', 'Untitled')}")
                
        if deleted:
            print(f"\n🗑️  Items to delete ({len(deleted)}):")
            for d in deleted:
                print(f"  • {d['item']['id']}: {d['item'].get('title', 'Untitled')}")
                
        if kept:
            print(f"\n⏸️  Items to keep ({len(kept)}):")
            for d in kept:
                print(f"  • {d['item']['id']}: {d['item'].get('title', 'Untitled')}")
                
        if promoted or deleted:
            confirm = input("\nProceed with these actions? (y/n): ").lower().strip()
            if confirm == 'y':
                # Execute actions
                for d in promoted:
                    self._promote_item(d['item'])
                for d in deleted:
                    self._delete_item(d['item'])
                    
                # Update index after changes
                self.update_index()
                print("✅ Review actions completed")
            else:
                print("❌ Review cancelled")
                
    def _promote_item(self, item):
        """Promote an item to the roadmap"""
        # For now, just print what would happen
        print(f"  → Would promote {item['id']} to roadmap/later/")
        # TODO: Actual promotion logic
        
    def _delete_item(self, item):
        """Delete/archive an item"""
        import shutil
        item_path = self.project_root / item['path']
        if item_path.exists():
            shutil.rmtree(item_path)
            print(f"  → Deleted {item['id']}")
            
    def promote_to_roadmap(self, item_id, target="later"):
        """Promote a specific item to the roadmap"""
        if target not in ['now', 'next', 'later']:
            print(f"Error: Invalid target '{target}'. Must be: now, next, or later")
            return False
            
        # Find the item
        if not self.index_file.exists():
            self.update_index()
            
        index_data = json.loads(self.index_file.read_text())
        item = None
        
        for i in index_data['items']:
            if i['id'] == item_id:
                item = i
                break
                
        if not item:
            print(f"Error: Item '{item_id}' not found")
            return False
            
        # Create roadmap entry
        roadmap_target_dir = self.roadmap_dir / target
        roadmap_target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy content
        source_path = self.project_root / item['path']
        dest_path = roadmap_target_dir / item['id']
        
        if source_path.exists():
            import shutil
            shutil.copytree(source_path, dest_path)
            
            # Update the status in the README
            readme_path = dest_path / "README.md"
            if readme_path.exists():
                content = readme_path.read_text()
                content = content.replace("status: parking-lot", f"status: roadmap-{target}")
                content = content.replace("status: parking-lot", f"promoted: {datetime.now().strftime('%Y-%m-%d')}")
                readme_path.write_text(content)
                
            # Remove from parking lot
            shutil.rmtree(source_path)
            
            print(f"✅ Promoted {item_id} to roadmap/{target}/")
            
            # Update index
            self.update_index()
            return True
        else:
            print(f"Error: Source path not found: {source_path}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Parking Lot Management")
    parser.add_argument("action", choices=["add", "list", "review", "promote", "update-index"])
    parser.add_argument("--type", help="Item type (for add)")
    parser.add_argument("--title", help="Item title (for add)")
    parser.add_argument("--desc", help="Item description (for add)", default="")
    parser.add_argument("--owner", help="Item owner (for add)", default="")
    parser.add_argument("--tags", help="Comma-separated tags (for add)", default="")
    parser.add_argument("--category", help="Filter by category (for list)")
    parser.add_argument("--format", help="Output format (for list)", default="table", choices=["table", "json"])
    parser.add_argument("--item", help="Item ID (for promote)")
    parser.add_argument("--target", help="Roadmap target (for promote)", default="later", choices=["now", "next", "later"])
    
    args = parser.parse_args()
    
    manager = ParkingLotManager()
    
    if args.action == "add":
        if not args.type or not args.title:
            print("Error: --type and --title are required for add")
            sys.exit(1)
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        manager.add_item(args.type, args.title, args.desc, args.owner, tags)
        
    elif args.action == "list":
        manager.list_items(args.category, args.format)
        
    elif args.action == "review":
        manager.review_items()
        
    elif args.action == "promote":
        if not args.item:
            print("Error: --item is required for promote")
            sys.exit(1)
        manager.promote_to_roadmap(args.item, args.target)
        
    elif args.action == "update-index":
        manager.update_index()

if __name__ == "__main__":
    main()
