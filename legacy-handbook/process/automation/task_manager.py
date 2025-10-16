#!/usr/bin/env python3
"""
Task directory management for sprints.
- Create task directories with complete implementation details
- Update task status with validation
- Manage task dependencies within sprint scope only
"""

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3] / "project-handbook"
SPRINTS_DIR = ROOT / "sprints"
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
        "story_points": {"default_story_points": 5, "allowed_story_points": [1, 2, 3, 5, 8, 13, 21]},
        "task_status": {"allowed_statuses": ["todo", "doing", "review", "done", "blocked"]}
    }

def get_current_sprint_id() -> str:
    """Get current sprint ID."""
    today = dt.date.today()
    week_num = today.isocalendar()[1]
    year = today.year
    return f"SPRINT-{year}-W{week_num:02d}"

def get_current_sprint_dir() -> Path:
    """Get current sprint directory."""
    sprint_id = get_current_sprint_id()
    year = sprint_id.split('-')[1]
    return SPRINTS_DIR / year / sprint_id

def get_next_task_id(sprint_dir: Path) -> str:
    """Generate next task ID for sprint."""
    tasks_dir = sprint_dir / "tasks"
    if not tasks_dir.exists():
        return "TASK-001"

    # Find highest existing task number
    max_num = 0
    for task_dir in tasks_dir.iterdir():
        if task_dir.is_dir() and task_dir.name.startswith("TASK-"):
            try:
                num_part = task_dir.name.split("-")[1]
                max_num = max(max_num, int(num_part))
            except:
                continue

    return f"TASK-{max_num + 1:03d}"

def create_task_directory(
    title: str,
    feature: str,
    decision: str,
    story_points: int,
    owner: str = "@owner",
    prio: str = "P2",
    due_days: int = 7
) -> Path:
    """Create complete task directory structure."""

    sprint_dir = get_current_sprint_dir()
    if not sprint_dir.exists():
        print(f"❌ No current sprint found. Run 'make sprint-plan' first.")
        return None

    # Generate task ID and directory
    task_id = get_next_task_id(sprint_dir)
    task_slug = title.lower().replace(" ", "-").replace("_", "-")
    task_dir_name = f"{task_id}-{task_slug}"
    task_dir = sprint_dir / "tasks" / task_dir_name

    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "source").mkdir(exist_ok=True)

    # Calculate due date
    due_date = dt.date.today() + dt.timedelta(days=due_days)

    # Create task.yaml (metadata)
    task_yaml = f"""id: {task_id}
title: {title}
feature: {feature}
decision: {decision}
owner: {owner}
status: todo
story_points: {story_points}
depends_on: []
prio: {prio}
due: {due_date.strftime('%Y-%m-%d')}
acceptance:
  - Implementation complete and tested
  - Code review passed
  - Documentation updated
links: []
"""

    (task_dir / "task.yaml").write_text(task_yaml, encoding='utf-8')

    # Create README.md (Agent Navigation)
    readme_content = f"""---
title: Task {task_id} - {title}
type: task
date: {dt.date.today().strftime('%Y-%m-%d')}
task_id: {task_id}
feature: {feature}
tags: [task, {feature}]
links: [../../../features/{feature}/overview.md]
---

# Task {task_id}: {title}

## Overview
**Feature**: [{feature}](../../../features/{feature}/overview.md)
**Decision**: [{decision}](../../../adr/{decision.lower()}.md)
**Story Points**: {story_points}
**Owner**: {owner}

## Agent Navigation Rules
1. **Start work**: Update `task.yaml` status to "doing"
2. **Read first**: `steps.md` for implementation sequence
3. **Use commands**: Copy-paste from `commands.md`
4. **Validate progress**: Follow `validation.md` guidelines
5. **Check completion**: Use `checklist.md` before marking done
6. **Update status**: Set to "review" when ready for review

## Context & Background
This task implements the [{decision}] decision for the [{feature}] feature.

## Quick Start
```bash
# Update status when starting
cd sprints/current/tasks/{task_dir_name}/
# Edit task.yaml: status: doing

# Follow implementation
cat steps.md              # Read implementation steps
cat commands.md           # Copy-paste commands
cat validation.md         # Validation approach
```

## Dependencies
Review `task.yaml` for any `depends_on` tasks that must be completed first.

## Acceptance Criteria
See `task.yaml` acceptance section and `checklist.md` for completion requirements.
"""

    (task_dir / "README.md").write_text(readme_content, encoding='utf-8')

    # Create steps.md (Implementation Steps)
    steps_content = f"""---
title: {title} - Implementation Steps
type: implementation
date: {dt.date.today().strftime('%Y-%m-%d')}
task_id: {task_id}
tags: [implementation]
links: []
---

# Implementation Steps: {title}

## Overview
Detailed step-by-step implementation guide for this task.

## Prerequisites
- [ ] All dependent tasks completed (check task.yaml depends_on)
- [ ] Development environment ready
- [ ] Required permissions/access available

## Step 1: Analysis & Planning
**Estimated Time**: 1-2 hours

### Actions
- [ ] Review feature requirements in features/{feature}/
- [ ] Read decision rationale in adr/{decision.lower()}.md
- [ ] Identify implementation approach
- [ ] Plan testing strategy

### Expected Outcome
- Clear understanding of requirements
- Implementation approach decided
- Test plan outlined

## Step 2: Core Implementation
**Estimated Time**: 4-6 hours

### Actions
- [ ] Implement core functionality
- [ ] Add error handling
- [ ] Write unit tests
- [ ] Update documentation

### Expected Outcome
- Core functionality working
- Tests passing
- Basic documentation updated

## Step 3: Integration & Validation
**Estimated Time**: 1-2 hours

### Actions
- [ ] Integration testing
- [ ] Performance validation
- [ ] Security review (if applicable)
- [ ] Final documentation pass

### Expected Outcome
- All tests passing
- Performance acceptable
- Documentation complete
- Ready for review

## Notes
- Update task.yaml status as you progress through steps
- Document any blockers or decisions in daily status
- Link any PRs/commits back to this task
"""

    (task_dir / "steps.md").write_text(steps_content, encoding='utf-8')

    # Create commands.md (Copy-Paste Commands)
    commands_content = f"""---
title: {title} - Commands
type: commands
date: {dt.date.today().strftime('%Y-%m-%d')}
task_id: {task_id}
tags: [commands]
links: []
---

# Commands: {title}

## Task Status Updates
```bash
# When starting work
cd sprints/current/tasks/{task_dir_name}/
# Edit task.yaml: change status from "todo" to "doing"

# When ready for review
# Edit task.yaml: change status to "review"

# When complete
# Edit task.yaml: change status to "done"
```

## Validation Commands
```bash
# Run validation
make validate

# Check sprint status
make sprint-status

# Update daily status
make daily
```

## Implementation Commands
```bash
# Add specific commands for this task here
# Example:
# npm install package-name
# python3 -m pytest tests/
# docker build -t app .
```

## Git Integration
```bash
# Commit with task reference
git commit -m "feat: {title.lower()}

Implements {task_id} for {feature} feature.
Part of sprint: {get_current_sprint_id()}

Refs: #{task_id}"

# Link PR to task (in PR description)
# Closes #{task_id}
# Implements {decision}
```

## Quick Copy-Paste
```bash
# Most common commands for this task type
echo "Add task-specific commands here"
```
"""

    (task_dir / "commands.md").write_text(commands_content, encoding='utf-8')

    # Create checklist.md (Completion Checklist)
    checklist_content = f"""---
title: {title} - Completion Checklist
type: checklist
date: {dt.date.today().strftime('%Y-%m-%d')}
task_id: {task_id}
tags: [checklist]
links: []
---

# Completion Checklist: {title}

## Code Quality
- [ ] Code follows project conventions
- [ ] No obvious bugs or security issues
- [ ] Error handling implemented
- [ ] Performance is acceptable

## Testing
- [ ] Unit tests written and passing
- [ ] Integration tests passing (if applicable)
- [ ] Manual testing completed
- [ ] Edge cases considered

## Documentation
- [ ] Code comments added where needed
- [ ] API documentation updated (if applicable)
- [ ] Feature documentation updated
- [ ] README updated (if applicable)

## Integration
- [ ] No merge conflicts
- [ ] CI/CD pipeline passing
- [ ] Dependencies properly declared
- [ ] No breaking changes (or properly communicated)

## Sprint Integration
- [ ] Task status updated in task.yaml
- [ ] Daily status includes this task progress
- [ ] Any blockers documented and escalated
- [ ] Sprint burndown reflects progress

## Feature Integration
- [ ] Feature status.md updated if needed
- [ ] Feature stage advanced if this completes feature
- [ ] Cross-feature dependencies considered
- [ ] Changelog entry added (if significant)

## Review Readiness
- [ ] All acceptance criteria met (see task.yaml)
- [ ] Self-review completed
- [ ] Ready for peer review
- [ ] Task marked as "review" status

## Completion
- [ ] Peer review approved
- [ ] All checklist items verified
- [ ] Task status set to "done"
- [ ] Sprint metrics updated
"""

    (task_dir / "checklist.md").write_text(checklist_content, encoding='utf-8')

    # Create validation.md (Validation Guide)
    validation_content = f"""---
title: {title} - Validation Guide
type: validation
date: {dt.date.today().strftime('%Y-%m-%d')}
task_id: {task_id}
tags: [validation]
links: []
---

# Validation Guide: {title}

## Automated Validation
```bash
# Run project validation
make validate

# Check sprint health
make sprint-status

# Verify task dependencies
# (Validation will check depends_on within current sprint)
```

## Manual Validation Steps

### Functional Testing
1. **Happy Path Testing**
   - [ ] Primary use case works as expected
   - [ ] User interface responds correctly
   - [ ] Data flows properly

2. **Edge Case Testing**
   - [ ] Invalid inputs handled gracefully
   - [ ] Boundary conditions tested
   - [ ] Error scenarios covered

3. **Integration Testing**
   - [ ] Works with existing features
   - [ ] API contracts maintained
   - [ ] No regressions introduced

### Quality Checks

1. **Code Quality**
   - [ ] Code is readable and maintainable
   - [ ] Follows project coding standards
   - [ ] No code smells or anti-patterns

2. **Performance**
   - [ ] Performance meets requirements
   - [ ] No memory leaks introduced
   - [ ] Database queries optimized (if applicable)

3. **Security**
   - [ ] Input validation implemented
   - [ ] Authentication/authorization correct
   - [ ] No sensitive data exposed

### Documentation Validation
- [ ] Implementation matches feature specification
- [ ] Decision rationale reflected in code
- [ ] Comments explain complex logic
- [ ] API documentation accurate

## Validation Evidence
Document validation results here:

### Test Results
- Unit tests: X/Y passing
- Integration tests: X/Y passing
- Manual testing: Complete/Incomplete

### Review Results
- Code review: Approved/Needs changes
- Security review: Approved/Not required
- Performance review: Approved/Needs optimization

## Sign-off
- [ ] All validation steps completed
- [ ] Evidence documented above
- [ ] Ready to mark task as "done"
"""

    (task_dir / "validation.md").write_text(validation_content, encoding='utf-8')

    # Create references.md (Links and Resources)
    references_content = f"""---
title: {title} - References
type: references
date: {dt.date.today().strftime('%Y-%m-%d')}
task_id: {task_id}
tags: [references]
links: []
---

# References: {title}

## Internal References

### Decision Context
- **Decision**: [ADR/FDR link](../../../adr/{decision.lower()}.md)
- **Feature**: [Feature overview](../../../features/{feature}/overview.md)
- **Architecture**: [Feature architecture](../../../features/{feature}/architecture/ARCHITECTURE.md)

### Sprint Context
- **Sprint Plan**: [Current sprint](../../plan.md)
- **Sprint Tasks**: [All sprint tasks](../)
- **Daily Progress**: [Daily status](../../daily/)

## External References

### Documentation
- [ ] API documentation: [Add relevant API docs]
- [ ] Library docs: [Add library/framework docs]
- [ ] Tutorials: [Add helpful tutorials]

### Code Examples
- [ ] Similar implementations: [Add internal code examples]
- [ ] Open source examples: [Add relevant open source projects]
- [ ] Best practices: [Add best practice guides]

### Tools & Resources
- [ ] Development tools: [Add specific tools needed]
- [ ] Testing resources: [Add testing frameworks/tools]
- [ ] Deployment guides: [Add deployment documentation]

## Learning Resources
- [ ] Background reading: [Add conceptual resources]
- [ ] Technical specifications: [Add relevant specs]
- [ ] Industry standards: [Add relevant standards]

## Related Work
- [ ] Similar tasks in other sprints: [Add references if helpful]
- [ ] Feature dependencies: [List related features]
- [ ] Follow-up tasks: [Note future tasks this enables]

## Notes
Keep this file updated as you discover useful resources during implementation.
Link back to this task from any PRs or external discussions.
"""

    (task_dir / "references.md").write_text(references_content, encoding='utf-8')

    return task_dir

def list_sprint_tasks(sprint_dir: Path = None) -> List[Dict]:
    """List all tasks in a sprint."""
    if sprint_dir is None:
        sprint_dir = get_current_sprint_dir()

    tasks = []
    tasks_dir = sprint_dir / "tasks"

    if not tasks_dir.exists():
        return tasks

    for task_dir in sorted(tasks_dir.iterdir()):
        if not task_dir.is_dir():
            continue

        task_yaml = task_dir / "task.yaml"
        if not task_yaml.exists():
            continue

        try:
            # Simple YAML parsing for task metadata
            content = task_yaml.read_text(encoding='utf-8')
            task_data = {}

            for line in content.splitlines():
                if ':' in line and not line.strip().startswith('-'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle lists like depends_on: [TASK-001, TASK-002]
                    if value.startswith('[') and value.endswith(']'):
                        items = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
                        task_data[key] = [item for item in items if item]
                    else:
                        task_data[key] = value

            task_data['directory'] = task_dir.name
            tasks.append(task_data)

        except Exception as e:
            print(f"Error parsing {task_yaml}: {e}")

    return tasks

def update_task_status(task_id: str, new_status: str, sprint_dir: Path = None) -> bool:
    """Update task status with validation."""
    config = load_config()
    task_config = config.get("task_status", {})

    if sprint_dir is None:
        sprint_dir = get_current_sprint_dir()

    tasks_dir = sprint_dir / "tasks"
    if not tasks_dir.exists():
        print(f"❌ No tasks directory found in {sprint_dir}")
        return False

    # Find task directory
    task_dir = None
    for td in tasks_dir.iterdir():
        if td.is_dir() and td.name.startswith(f"{task_id}-"):
            task_dir = td
            break

    if not task_dir:
        print(f"❌ Task {task_id} not found in current sprint")
        return False

    task_yaml = task_dir / "task.yaml"
    if not task_yaml.exists():
        print(f"❌ Task metadata not found: {task_yaml}")
        return False

    # Validate status transition (configurable)
    valid_statuses = task_config.get("allowed_statuses", ['todo', 'doing', 'review', 'done', 'blocked'])
    if new_status not in valid_statuses:
        print(f"❌ Invalid status '{new_status}'. Must be one of: {valid_statuses}")
        return False

    try:
        content = task_yaml.read_text(encoding='utf-8')
        lines = content.splitlines()

        # Update status line
        for i, line in enumerate(lines):
            if line.startswith('status:'):
                lines[i] = f"status: {new_status}"
                break

        updated_content = '\n'.join(lines) + '\n'
        task_yaml.write_text(updated_content, encoding='utf-8')

        print(f"✅ Updated {task_id} status: {new_status}")

        # Show helpful next steps
        if new_status == 'doing':
            print(f"📋 Next: Read {task_dir}/steps.md for implementation details")
        elif new_status == 'review':
            print(f"📋 Next: Ensure {task_dir}/checklist.md is complete")
        elif new_status == 'done':
            print(f"🎉 Task complete! Run 'make sprint-status' to see updated progress")

        return True

    except Exception as e:
        print(f"❌ Error updating task: {e}")
        return False

def validate_sprint_dependencies(sprint_dir: Path = None) -> List[str]:
    """Validate that all task dependencies are within current sprint."""
    if sprint_dir is None:
        sprint_dir = get_current_sprint_dir()

    tasks = list_sprint_tasks(sprint_dir)
    task_ids = {task['id'] for task in tasks}
    issues = []

    for task in tasks:
        depends_on = task.get('depends_on', [])
        if isinstance(depends_on, str):
            depends_on = [depends_on]

        for dep in depends_on:
            if dep and dep not in task_ids:
                issues.append(f"Task {task['id']} depends on {dep} which is not in current sprint")

    return issues

def show_task_details(task_id: str, sprint_dir: Path = None):
    """Show detailed task information."""
    if sprint_dir is None:
        sprint_dir = get_current_sprint_dir()

    tasks = list_sprint_tasks(sprint_dir)
    task = next((t for t in tasks if t['id'] == task_id), None)

    if not task:
        print(f"❌ Task {task_id} not found")
        return

    print(f"📋 TASK DETAILS: {task_id}")
    print("=" * 50)
    print(f"Title: {task.get('title')}")
    print(f"Feature: {task.get('feature')}")
    print(f"Owner: {task.get('owner')}")
    print(f"Status: {task.get('status')}")
    print(f"Story Points: {task.get('story_points')}")
    print(f"Priority: {task.get('prio')}")
    print(f"Due: {task.get('due')}")

    depends_on = task.get('depends_on', [])
    if depends_on:
        print(f"Dependencies: {', '.join(depends_on)}")
    else:
        print("Dependencies: None")

    print(f"\nLocation: {sprint_dir}/tasks/{task['directory']}")
    print(f"Files: README.md, steps.md, commands.md, checklist.md, validation.md")

def main():
    parser = argparse.ArgumentParser(description="Task directory management")

    # Task creation
    parser.add_argument('--create', action='store_true', help='Create new task')
    parser.add_argument('--title', help='Task title')
    parser.add_argument('--feature', help='Feature name')
    parser.add_argument('--decision', help='Decision ID (ADR-XXX or FDR-feature-XXX)')
    config = load_config()
    default_points = config.get("story_points", {}).get("default_story_points", 5)
    parser.add_argument('--points', type=int, help='Story points', default=default_points)
    parser.add_argument('--owner', help='Task owner', default='@owner')
    parser.add_argument('--prio', help='Priority', default='P2')

    # Task management
    parser.add_argument('--list', action='store_true', help='List all sprint tasks')
    parser.add_argument('--show', help='Show task details')
    parser.add_argument('--update-status', nargs=2, metavar=('TASK_ID', 'STATUS'),
                       help='Update task status')
    parser.add_argument('--validate-deps', action='store_true',
                       help='Validate sprint-scoped dependencies')

    args = parser.parse_args()

    if args.create:
        if not all([args.title, args.feature, args.decision]):
            print("❌ Required: --title, --feature, --decision")
            return 1

        task_dir = create_task_directory(
            args.title, args.feature, args.decision,
            args.points, args.owner, args.prio
        )

        if task_dir:
            print(f"✅ Created task directory: {task_dir.name}")
            print(f"📁 Location: {task_dir}")
            print(f"📝 Next steps:")
            print(f"   1. Edit {task_dir}/steps.md with implementation details")
            print(f"   2. Update {task_dir}/commands.md with specific commands")
            print(f"   3. Set status to 'doing' when starting work")

    elif args.list:
        tasks = list_sprint_tasks()
        if not tasks:
            print("📋 No tasks in current sprint")
            print("💡 Create one with: make task-create")
            return

        print(f"📋 SPRINT TASKS: {get_current_sprint_id()}")
        print("=" * 60)

        for task in tasks:
            status_emoji = {
                'todo': '⭕',
                'doing': '🔄',
                'review': '👀',
                'done': '✅',
                'blocked': '🚫'
            }.get(task.get('status'), '❓')

            deps = task.get('depends_on', [])
            dep_info = f" (depends: {', '.join(deps)})" if deps else ""

            print(f"{status_emoji} {task.get('id')}: {task.get('title')} "
                  f"[{task.get('story_points')}pts]{dep_info}")

    elif args.show:
        show_task_details(args.show)

    elif args.update_status:
        task_id, status = args.update_status
        update_task_status(task_id, status)

    elif args.validate_deps:
        issues = validate_sprint_dependencies()
        if issues:
            print("❌ Sprint dependency validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            return 1
        else:
            print("✅ Sprint dependencies valid (all within current sprint)")

    else:
        # Default: list tasks
        tasks = list_sprint_tasks()
        if tasks:
            args.list = True
            main()
        else:
            print("📋 No tasks in current sprint")
            print("💡 Create one with: make task-create title='Task Name' feature=feature-name decision=ADR-001")

    return 0

if __name__ == "__main__":
    exit(main())