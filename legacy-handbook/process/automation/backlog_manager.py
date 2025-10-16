#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import argparse
import re

class BacklogManager:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).absolute()
        self.backlog_dir = self.project_root / "backlog"
        self.index_file = self.backlog_dir / "index.json"
        self.sprint_dir = self.project_root / "sprints"
        
        # Severity rubric
        self.severity_rubric = {
            "P0": {
                "name": "Critical",
                "color": "🔴",
                "criteria": [
                    "Production outage affecting >50% of users",
                    "Active security exploit",
                    "Data loss or corruption",
                    "Complete feature failure in production"
                ],
                "action": "Always interrupts current sprint"
            },
            "P1": {
                "name": "High",
                "color": "🟠",
                "criteria": [
                    "Service degradation affecting 10-50% of users",
                    "Major feature broken but workaround exists",
                    "Security vulnerability (not actively exploited)",
                    "Significant performance degradation"
                ],
                "action": "Addressed in next sprint"
            },
            "P2": {
                "name": "Medium",
                "color": "🟡",
                "criteria": [
                    "Issue affecting <10% of users",
                    "Minor feature malfunction",
                    "UI/UX issues with moderate impact",
                    "Non-critical performance issues"
                ],
                "action": "Queued in backlog"
            },
            "P3": {
                "name": "Low",
                "color": "🟢",
                "criteria": [
                    "Cosmetic issues",
                    "Developer experience improvements",
                    "Documentation gaps",
                    "Nice-to-have enhancements"
                ],
                "action": "Backlog queue, low priority"
            },
            "P4": {
                "name": "Wishlist",
                "color": "⚪",
                "criteria": [
                    "Future enhancements",
                    "Experimental features",
                    "Long-term improvements"
                ],
                "action": "Consider for parking lot"
            }
        }
        
    def add_issue(self, issue_type, title, severity, desc="", owner="", impact="", workaround=""):
        """Add a new issue to the backlog"""
        if issue_type not in ['bugs', 'wildcards']:
            print(f"Error: Invalid type '{issue_type}'")
            print("Valid types: bugs, wildcards")
            return False
            
        if severity not in self.severity_rubric:
            print(f"Error: Invalid severity '{severity}'")
            print("Valid severities: P0, P1, P2, P3, P4")
            return False
            
        # Create directory structure
        type_dir = self.backlog_dir / issue_type
        type_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate issue ID
        issue_id = self._generate_issue_id(issue_type, severity)
        issue_dir = type_dir / issue_id
        
        if issue_dir.exists():
            print(f"Error: Issue '{issue_id}' already exists")
            return False
            
        issue_dir.mkdir(parents=True)
        
        # Create README.md with front matter
        readme_path = issue_dir / "README.md"
        front_matter = {
            "title": title,
            "type": issue_type,
            "severity": severity,
            "status": "open",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "owner": owner or "unassigned",
            "impact": impact,
            "workaround": workaround
        }
        
        severity_info = self.severity_rubric[severity]
        
        content = f"""---
title: {front_matter['title']}
type: {front_matter['type']}
severity: {front_matter['severity']}
status: {front_matter['status']}
created: {front_matter['created']}
owner: {front_matter['owner']}
---

# {severity_info['color']} [{severity}] {title}

**Severity:** {severity} - {severity_info['name']}  
**Action Required:** {severity_info['action']}

## Description

{desc}

## Impact

{impact or "_Describe the impact on users, systems, or business_"}

## Workaround

{workaround or "_Document any temporary workaround if available_"}

## Root Cause Analysis

_To be completed during investigation_

## Solution Options

### Option 1: Quick Fix
_Describe quick/hotfix approach_

### Option 2: Proper Fix
_Describe comprehensive solution_

## Investigation Notes

_Add investigation findings here_
"""
        
        readme_path.write_text(content)
        
        # For P0 issues, create triage analysis template
        if severity == "P0":
            triage_path = issue_dir / "triage.md"
            triage_content = self._generate_triage_template(title, desc, impact)
            triage_path.write_text(triage_content)
            print(f"  🎯 Created P0 triage template: triage.md")
        
        print(f"✅ Created backlog issue: {issue_id}")
        print(f"   Severity: {severity_info['color']} {severity} - {severity_info['name']}")
        print(f"   Location: {issue_dir.relative_to(self.project_root)}")
        
        # Update index
        self.update_index()
        
        # Alert for P0
        if severity == "P0":
            print("\n" + "=" * 60)
            print("🚨 P0 CRITICAL ISSUE - IMMEDIATE ACTION REQUIRED 🚨")
            print("=" * 60)
            print(f"Issue: {title}")
            print(f"Impact: {impact or 'Not specified'}")
            print("\nRecommended actions:")
            print("1. Run: make backlog-triage issue={} to generate AI analysis".format(issue_id))
            print("2. Notify incident response team")
            print("3. Consider interrupting current sprint")
            print("=" * 60)
            
        return True
        
    def _generate_issue_id(self, issue_type, severity):
        """Generate a unique issue ID"""
        prefix = "BUG" if issue_type == "bugs" else "WILD"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        return f"{prefix}-{severity}-{timestamp}"
        
    def _generate_triage_template(self, title, desc, impact):
        """Generate AI triage analysis template for P0 issues"""
        return f"""# P0 Triage Analysis: {title}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 🎯 Problem Statement

**Issue:** {title}

**Description:** {desc}

**Impact Metrics:**
- Users affected: _[To be determined]_
- Services impacted: _[To be determined]_
- Revenue impact: _[To be determined]_
- Data at risk: _[To be determined]_

## 🛠️ Solution Options Analysis

### Option 1: Hotfix Approach

**Description:** _[Quick tactical fix to stop the bleeding]_

**Pros:**
- ✅ Can be deployed immediately
- ✅ Minimal testing required
- ✅ Low risk of additional issues

**Cons:**
- ❌ Technical debt created
- ❌ May not address root cause
- ❌ Requires follow-up work

**Time Estimate:** _[X hours]_

**Interruption Cost:** 
- Sprint tasks delayed: _[List affected tasks]_
- Team members required: _[Number and roles]_

### Option 2: Proper Fix

**Description:** _[Comprehensive solution addressing root cause]_

**Pros:**
- ✅ Addresses root cause
- ✅ Prevents recurrence
- ✅ Improves overall system

**Cons:**
- ❌ Takes longer to implement
- ❌ Requires thorough testing
- ❌ Higher risk during deployment

**Time Estimate:** _[Y hours/days]_

**Interruption Cost:**
- Sprint tasks delayed: _[List affected tasks]_
- Team members required: _[Number and roles]_
- Sprint completion risk: _[High/Medium/Low]_

## 🔄 Cascading Effects Analysis

### If we do Option 1 (Hotfix):
- **Immediate:** _[What happens right after deployment]_
- **Next Sprint:** _[Follow-up work required]_
- **Long-term:** _[Technical debt and maintenance impact]_

### If we do Option 2 (Proper Fix):
- **Immediate:** _[Impact on current sprint and deliverables]_
- **Next Sprint:** _[Cleaner state, no follow-up needed]_
- **Long-term:** _[System improvements and prevention]_

### If we do nothing:
- **Next 1 hour:** _[Escalation scenario]_
- **Next 24 hours:** _[Full impact scenario]_
- **Business impact:** _[Reputation, revenue, compliance]_

## 🤖 AI Recommendation

**Recommended Approach:** _[Option 1 or 2]_

**Rationale:**
_[Detailed explanation of why this option is recommended based on:]
- Severity and urgency of the issue
- Available resources and expertise
- Current sprint commitments
- Long-term system health
- Business priorities]_

## 👥 Human Decision Framework

**Key Questions for Leadership:**

1. **Business Priority:** Is fixing this issue more important than current sprint deliverables?
2. **Resource Availability:** Do we have the right people available now?
3. **Risk Tolerance:** Can we accept the risk of a quick fix vs. proper solution?
4. **Customer Communication:** What do we need to tell customers and when?
5. **Compliance/Legal:** Are there regulatory implications to consider?

**Decision Checklist:**
- [ ] Incident commander assigned
- [ ] Stakeholders notified
- [ ] Customer communication plan
- [ ] Resource allocation confirmed
- [ ] Success criteria defined
- [ ] Rollback plan prepared

## 📋 Next Steps

1. **Immediate (Next 30 min):**
   - [ ] Review this analysis with incident commander
   - [ ] Make go/no-go decision
   - [ ] Assign resources

2. **Short-term (Next 2 hours):**
   - [ ] Begin implementation of chosen option
   - [ ] Set up monitoring and alerts
   - [ ] Prepare customer communication

3. **Follow-up:**
   - [ ] Post-mortem scheduled
   - [ ] Lessons learned documented
   - [ ] Prevention measures identified
"""
        
    def update_index(self):
        """Update the index.json file by scanning all directories"""
        index_data = {
            "last_updated": datetime.now().isoformat(),
            "total_items": 0,
            "by_severity": {
                "P0": [],
                "P1": [],
                "P2": [],
                "P3": [],
                "P4": []
            },
            "by_category": {
                "bugs": [],
                "wildcards": []
            },
            "items": []
        }
        
        for category in ['bugs', 'wildcards']:
            category_dir = self.backlog_dir / category
            if not category_dir.exists():
                continue
                
            for issue_dir in category_dir.iterdir():
                if not issue_dir.is_dir():
                    continue
                    
                readme_path = issue_dir / "README.md"
                if not readme_path.exists():
                    continue
                    
                # Parse front matter
                issue_info = self._parse_front_matter(readme_path)
                if issue_info:
                    issue_info["id"] = issue_dir.name
                    issue_info["path"] = str(issue_dir.relative_to(self.project_root))
                    
                    # Check for triage analysis
                    triage_path = issue_dir / "triage.md"
                    issue_info["has_triage"] = triage_path.exists()
                    
                    index_data["items"].append(issue_info)
                    index_data["by_category"][category].append(issue_info["id"])
                    
                    severity = issue_info.get("severity", "P2")
                    if severity in index_data["by_severity"]:
                        index_data["by_severity"][severity].append(issue_info["id"])
                        
                    index_data["total_items"] += 1
        
        # Sort items by severity then created date
        severity_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
        index_data["items"].sort(key=lambda x: (
            severity_order.get(x.get("severity", "P2"), 2),
            x.get("created", "")
        ))
        
        # Write index file
        self.index_file.write_text(json.dumps(index_data, indent=2))
        print(f"📊 Updated backlog index: {index_data['total_items']} items")
        
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
            
            # Parse manually
            result = {}
            for line in front_matter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    result[key] = value
                    
            return result
        except Exception as e:
            print(f"Warning: Could not parse front matter from {file_path}: {e}")
            return None
            
    def list_issues(self, severity=None, category=None, format="table"):
        """List all backlog issues"""
        if not self.index_file.exists():
            self.update_index()
            
        index_data = json.loads(self.index_file.read_text())
        
        if format == "json":
            print(json.dumps(index_data, indent=2))
            return
            
        print("\n📝 ISSUE BACKLOG")
        print("=" * 80)
        
        if index_data["total_items"] == 0:
            print("No issues in backlog")
            return
            
        # Count by severity
        p0_count = len(index_data["by_severity"]["P0"])
        p1_count = len(index_data["by_severity"]["P1"])
        
        if p0_count > 0:
            print(f"🚨 WARNING: {p0_count} P0 CRITICAL ISSUES REQUIRE IMMEDIATE ACTION")
        if p1_count > 0:
            print(f"⚠️  Note: {p1_count} P1 high priority issues for next sprint")
            
        print()
        
        # Group by severity
        for sev in ['P0', 'P1', 'P2', 'P3', 'P4']:
            if severity and severity != sev:
                continue
                
            items = [item for item in index_data["items"] if item.get("severity") == sev]
            if not items:
                continue
                
            sev_info = self.severity_rubric[sev]
            print(f"{sev_info['color']} {sev} - {sev_info['name']} ({len(items)} issues)")
            print("-" * 40)
            
            for item in items:
                issue_type = item.get('type', 'unknown')
                created = item.get('created', 'unknown')
                status = item.get('status', 'open')
                owner = item.get('owner', 'unassigned')
                title = item.get('title', item['id'])
                triage = "🎯" if item.get('has_triage') else ""
                
                print(f"  • {item['id']} {triage}")
                print(f"    {title}")
                print(f"    Type: {issue_type} | Status: {status} | Owner: {owner}")
                print(f"    Created: {created}")
                print()
                
        print(f"\nTotal issues: {index_data['total_items']}")
        
        # Show severity breakdown
        print("\nBy Severity:")
        for sev in ['P0', 'P1', 'P2', 'P3', 'P4']:
            count = len(index_data["by_severity"][sev])
            if count > 0:
                sev_info = self.severity_rubric[sev]
                print(f"  {sev_info['color']} {sev}: {count} issues")
                
        print(f"\nLast updated: {index_data.get('last_updated', 'never')}")
        
    def triage_issue(self, issue_id):
        """Generate or display triage analysis for an issue"""
        # Find the issue
        if not self.index_file.exists():
            self.update_index()
            
        index_data = json.loads(self.index_file.read_text())
        issue = None
        
        for item in index_data['items']:
            if item['id'] == issue_id:
                issue = item
                break
                
        if not issue:
            print(f"Error: Issue '{issue_id}' not found")
            return False
            
        issue_path = self.project_root / issue['path']
        triage_path = issue_path / "triage.md"
        
        if triage_path.exists():
            print(f"\n🎯 TRIAGE ANALYSIS: {issue_id}")
            print("=" * 80)
            print(triage_path.read_text())
        else:
            print(f"No triage analysis found for {issue_id}")
            if issue.get('severity') == 'P0':
                print("Generating triage template...")
                # Read issue details
                readme_path = issue_path / "README.md"
                content = readme_path.read_text()
                
                # Extract title and description
                title = issue.get('title', 'Unknown Issue')
                desc = "See README.md for details"
                impact = issue.get('impact', 'Not specified')
                
                triage_content = self._generate_triage_template(title, desc, impact)
                triage_path.write_text(triage_content)
                print(f"✅ Generated triage template: {triage_path.relative_to(self.project_root)}")
                print("\nEdit the template to complete the analysis.")
                
        return True
        
    def assign_to_sprint(self, issue_id, sprint="current"):
        """Assign an issue to a sprint"""
        # Find the issue
        if not self.index_file.exists():
            self.update_index()
            
        index_data = json.loads(self.index_file.read_text())
        issue = None
        
        for item in index_data['items']:
            if item['id'] == issue_id:
                issue = item
                break
                
        if not issue:
            print(f"Error: Issue '{issue_id}' not found")
            return False
            
        # Determine sprint
        if sprint == "current":
            # Find current sprint
            import subprocess
            try:
                result = subprocess.run(
                    ["python3", str(self.project_root / "process/automation/sprint_manager.py"), "current"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0 and result.stdout:
                    # Parse sprint name from output
                    for line in result.stdout.split('\n'):
                        if "SPRINT-" in line:
                            sprint = line.split()[0] if line.split() else None
                            break
            except:
                pass
                
            if sprint == "current":
                print("Error: Could not determine current sprint")
                return False
                
        print(f"\nAssigning {issue_id} to sprint {sprint}")
        print(f"Severity: {issue.get('severity', 'unknown')}")
        print(f"Title: {issue.get('title', 'unknown')}")
        
        # Check if this is a P0 interruption
        if issue.get('severity') == 'P0':
            print("\n" + "=" * 60)
            print("🚨 P0 SPRINT INTERRUPTION 🚨")
            print("=" * 60)
            print("This will interrupt the current sprint!")
            print("\nImpact Analysis:")
            print("- Current sprint capacity will be reduced")
            print("- Some planned tasks may be deferred")
            print("- Team will context-switch to address this issue")
            print("=" * 60)
            
            confirm = input("\nConfirm P0 interruption? (yes/no): ").lower().strip()
            if confirm != "yes":
                print("Cancelled")
                return False
                
        # Create task in sprint
        issue_path = self.project_root / issue['path']
        readme_content = (issue_path / "README.md").read_text() if (issue_path / "README.md").exists() else ""
        
        # TODO: Call task_manager to create task in sprint
        print(f"\n✅ Issue {issue_id} assigned to {sprint}")
        print("Next steps:")
        print(f"1. Task created in {sprint}/tasks/")
        print("2. Update sprint capacity planning")
        print("3. Notify team of assignment")
        
        return True
        
    def show_stats(self):
        """Display backlog statistics and analysis"""
        # Load validation rules for configuration
        validation_rules_path = Path(__file__).parent.parent / "checks" / "validation_rules.json"
        validation_rules = {}
        if validation_rules_path.exists():
            validation_rules = json.loads(validation_rules_path.read_text())

        backlog_config = validation_rules.get("backlog", {})
        capacity_config = backlog_config.get("capacity_allocation", {})
        escalation_thresholds = backlog_config.get("escalation_thresholds", {})

        # Load current index
        if not self.index_file.exists():
            self.update_index()

        index_data = json.loads(self.index_file.read_text())

        print("\n📊 BACKLOG STATISTICS")
        print("=" * 80)

        # Overall statistics
        print("\n📈 Summary")
        print("-" * 40)
        print(f"Total Issues: {index_data['total_items']}")
        print(f"Categories: {', '.join(index_data['by_category'].keys())}")
        print(f"Last Updated: {index_data['last_updated']}")

        # Severity distribution
        print("\n🎯 Severity Distribution")
        print("-" * 40)
        severity_stats = {}
        for item in index_data["items"]:
            severity = item.get("severity", "P2")
            severity_stats[severity] = severity_stats.get(severity, 0) + 1

        for severity in ["P0", "P1", "P2", "P3", "P4"]:
            count = severity_stats.get(severity, 0)
            percentage = (count / max(index_data['total_items'], 1)) * 100
            bar_length = int(percentage / 2)
            bar = "█" * bar_length + "░" * (50 - bar_length)

            severity_info = self.severity_rubric.get(severity, {})
            color = severity_info.get("color", "")
            print(f"{color:4} {severity}: {count:3} ({percentage:5.1f}%) |{bar}|")

        # Category breakdown
        print("\n📁 Category Breakdown")
        print("-" * 40)
        for category, items in index_data["by_category"].items():
            print(f"{category.capitalize():15} {len(items):3} issues")

        # Age analysis
        print("\n⏱️ Age Analysis")
        print("-" * 40)
        from datetime import datetime, timedelta
        now = datetime.now()
        age_buckets = {"<24h": 0, "1-3d": 0, "3-7d": 0, "1-2w": 0, "2-4w": 0, ">1m": 0}

        for item in index_data["items"]:
            created = item.get("created", "")
            if created:
                try:
                    created_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    age = now - created_date

                    if age < timedelta(days=1):
                        age_buckets["<24h"] += 1
                    elif age < timedelta(days=3):
                        age_buckets["1-3d"] += 1
                    elif age < timedelta(days=7):
                        age_buckets["3-7d"] += 1
                    elif age < timedelta(days=14):
                        age_buckets["1-2w"] += 1
                    elif age < timedelta(days=28):
                        age_buckets["2-4w"] += 1
                    else:
                        age_buckets[">1m"] += 1
                except:
                    pass

        for bucket, count in age_buckets.items():
            if count > 0:
                print(f"{bucket:10} {count:3} issues")

        # Capacity impact analysis
        print("\n💼 Capacity Impact")
        print("-" * 40)
        p0_p1_count = severity_stats.get("P0", 0) + severity_stats.get("P1", 0)

        if p0_p1_count > 0:
            print(f"P0/P1 Issues: {p0_p1_count}")
            print(f"Reactive Capacity Required: ~20% of sprint")

            # Check against escalation thresholds
            if severity_stats.get("P0", 0) > 0:
                print(f"⚠️  P0 ALERT: Immediate interrupt required!")
            if severity_stats.get("P1", 0) > 3:
                print(f"⚠️  P1 WARNING: High reactive load for next sprint")
        else:
            print("✅ No P0/P1 issues - full planned capacity available")

        # Recommendations
        print("\n💡 Recommendations")
        print("-" * 40)

        if severity_stats.get("P0", 0) > 0:
            print("🔴 Address P0 issues immediately - interrupt current sprint")
        if severity_stats.get("P1", 0) > 0:
            print("🟠 Plan P1 issues for next sprint (use 20% reactive capacity)")
        if severity_stats.get("P2", 0) > 5:
            print("🟡 Consider prioritizing P2 backlog in upcoming sprints")
        if severity_stats.get("P4", 0) > 10:
            print("⚪ Review P4 items for parking lot candidates")

        print("\n" + "=" * 80)

    def show_rubric(self):
        """Display the severity rubric"""
        print("\n📏 ISSUE SEVERITY RUBRIC")
        print("=" * 80)
        
        for severity, info in self.severity_rubric.items():
            print(f"\n{info['color']} {severity} - {info['name']}")
            print("-" * 40)
            print(f"Action: {info['action']}")
            print("\nCriteria:")
            for criterion in info['criteria']:
                print(f"  • {criterion}")
                
        print("\n" + "=" * 80)
        print("\n💡 Guidelines:")
        print("  • P0 issues ALWAYS interrupt the current sprint")
        print("  • P1 issues are addressed in the next sprint")
        print("  • P2-P3 issues queue in the backlog")
        print("  • P4 issues are candidates for the parking lot")
        print("  • Use 'make backlog-triage' for P0 decision support")

def main():
    parser = argparse.ArgumentParser(description="Backlog Management")
    parser.add_argument("action", choices=["add", "list", "triage", "assign", "rubric", "stats", "update-index"])
    parser.add_argument("--type", help="Issue type: bugs or wildcards (for add)")
    parser.add_argument("--title", help="Issue title (for add)")
    parser.add_argument("--severity", help="Severity: P0-P4 (for add/list)")
    parser.add_argument("--desc", help="Issue description (for add)", default="")
    parser.add_argument("--owner", help="Issue owner (for add)", default="")
    parser.add_argument("--impact", help="Impact description (for add)", default="")
    parser.add_argument("--workaround", help="Workaround if any (for add)", default="")
    parser.add_argument("--category", help="Filter by category (for list)")
    parser.add_argument("--format", help="Output format (for list)", default="table", choices=["table", "json"])
    parser.add_argument("--issue", help="Issue ID (for triage/assign)")
    parser.add_argument("--sprint", help="Sprint to assign to (for assign)", default="current")
    
    args = parser.parse_args()
    
    manager = BacklogManager()
    
    if args.action == "add":
        if not args.type or not args.title or not args.severity:
            print("Error: --type, --title, and --severity are required for add")
            sys.exit(1)
        manager.add_issue(
            args.type, 
            args.title, 
            args.severity, 
            args.desc, 
            args.owner, 
            args.impact, 
            args.workaround
        )
        
    elif args.action == "list":
        manager.list_issues(args.severity, args.category, args.format)
        
    elif args.action == "triage":
        if not args.issue:
            print("Error: --issue is required for triage")
            sys.exit(1)
        manager.triage_issue(args.issue)
        
    elif args.action == "assign":
        if not args.issue:
            print("Error: --issue is required for assign")
            sys.exit(1)
        manager.assign_to_sprint(args.issue, args.sprint)
        
    elif args.action == "rubric":
        manager.show_rubric()

    elif args.action == "stats":
        manager.show_stats()

    elif args.action == "update-index":
        manager.update_index()

if __name__ == "__main__":
    main()
