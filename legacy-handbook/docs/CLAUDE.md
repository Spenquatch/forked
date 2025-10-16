# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Repository Overview

This is a deterministic project handbook system with sprint management, daily status tracking, and automated workflows. It enforces a validator-checked workflow with strict conventions for documentation structure and state transitions.

## Key Commands

### Primary Interface (Use Make Commands)
```bash
# Daily workflow
make daily                    # Generate daily status (skips weekends)
make sprint-status           # Check sprint health

# Sprint management
make sprint-plan             # Create new sprint (Monday)
make sprint-close            # Close sprint with retrospective (Friday)
make burndown               # View ASCII burndown chart

# Feature management
make feature-create name=X   # Create new feature with full structure
make feature-list           # List all features with status
make feature-status name=X stage=Y  # Update feature stage

# Validation and status
make validate               # Run all validation checks
make status                 # Generate enhanced project status
make check-all              # Run both validate and status
```

### Direct Script Access (if needed)
```bash
# Validation
python3 process/checks/validate_docs.py

# Status generation
python3 status/generate_project_status.py

# Daily status
python3 process/automation/daily_status_check.py --generate

# Sprint management
python3 process/automation/sprint_manager.py --status

# Feature management
python3 process/automation/feature_manager.py --list

# Roadmap
python3 process/automation/roadmap_manager.py --show
```

## Architecture & Workflow

### Directory Structure
- `docs/` - Documentation ABOUT the handbook system
- `adr/` - Global Architecture Decision Records (ADR-XXXX)
- `features/<feature>/` - Feature documentation with local Feature Decision Records (FDR-<feature>-XXXX)
- `sprints/YYYY/SPRINT-YYYY-W##/` - Sprint directories with detailed task subdirectories, plans, burndowns, retrospectives
- `status/` - Generated status files and daily status tracking
- `process/` - Automation scripts, validation, and playbooks
- `roadmap/` - Now-Next-Later planning
- `releases/` - Changelog and release notes

### Sprint-Based Lifecycle
1. **Decide** - Create ADR (global) or FDR (feature-local) with status: draft → accepted
2. **Plan** - Create weekly sprint linking features and decisions
3. **Execute** - Update `tasks.yaml` daily, track with `make daily`
4. **Monitor** - Check `make sprint-status` and `make burndown`
5. **Close** - Generate retrospective and advance feature stages

### State Transitions
- **Task**: todo → doing → review → done (or todo → blocked → todo/doing)
- **Sprint**: planned → active → completed
- **Feature**: proposed → approved → developing → complete → live
- **Decision**: draft → accepted (or rejected; accepted → superseded)

## Enhanced Task Schema

Each task in `sprints/current/tasks/TASK-XXX-name/task.yaml` now requires:
```yaml
- id: TASK-XXX
  title: Task description
  feature: feature-name
  decision: ADR-XXXX or FDR-<feature>-XXXX
  owner: @username
  status: todo|doing|review|done|blocked
  story_points: 5                    # NEW: Fibonacci sequence (1,2,3,5,8,13,21)
  depends_on: [TASK-YYY]            # NEW: Task dependencies
  prio: P1
  due: 2025-09-25
  acceptance:
    - Acceptance criteria
  links: []
```

## Capacity Allocation & Backlog Management

### 80/20 Sprint Capacity Model
Each sprint follows an 80/20 capacity allocation:
- **80% Planned Work**: Features, technical debt, planned improvements
- **20% Reactive Work**: P0/P1 bugs, urgent requests, production issues

When planning sprints:
```bash
make sprint-plan                      # Automatically calculates capacity
make backlog-list severity=P0         # Check critical issues first
make backlog-assign issue=BUG-001 sprint=current  # Uses 20% capacity
```

### Issue Severity Guidelines (P0-P4)
- **P0 (Critical)**: Production down, data loss, security breach
  - Action: Immediate response, may override sprint
  - AI triage: Automatic for root cause analysis
- **P1 (High)**: Major feature broken, significant UX impact
  - Action: Address in current sprint (20% capacity)
- **P2 (Medium)**: Feature degraded, workaround exists
  - Action: Next sprint planning consideration
- **P3 (Low)**: Minor issue, cosmetic defect
  - Action: Backlog, address when convenient
- **P4 (Trivial)**: Nice-to-have improvement
  - Action: Parking lot candidate

### AI-Powered Triage
For P0 issues, use AI analysis to accelerate resolution:
```bash
make backlog-add type=bug title="Production down" severity=P0 desc="API failing"
make backlog-triage issue=BUG-P0-001  # Generates AI root cause analysis
```

The AI triage provides:
- Potential root causes ranked by probability
- Suggested investigation steps
- Similar historical issues
- Recommended team members to involve

### Parking Lot Management
Track future ideas without cluttering the backlog:
```bash
make parking-add type=features title="OAuth Integration" desc="Social login support"
make parking-add type=research title="GraphQL Migration" desc="Evaluate benefits"
```

Quarterly review process:
```bash
make parking-review                   # Interactive review interface
make parking-promote item=FEAT-001 target=next  # Move to roadmap
make parking-archive item=OLD-001     # Archive stale ideas
```

## Critical Rules

### When Implementing
- Use Make commands for all operations: `make daily`, `make sprint-status`, etc.
- Work inside sprint task directories `sprints/current/tasks/TASK-XXX-name/`
- Update task status via `make task-status` commands
- Use `story_points` field (required) with Fibonacci values
- Define `depends_on` for task dependencies
- Each task must reference exactly one decision (ADR-XXXX or FDR-<feature>-XXXX)

### Sprint Management
- **Monday**: Run `make sprint-plan` to start new sprint
- **Daily**: Run `make daily` to track progress (auto-skips weekends)
- **Wednesday**: Check `make sprint-status` for health (🟢🟡🔴 indicators)
- **Friday**: Run `make sprint-close` to complete sprint with retrospective

### Feature Management
- **Create**: Use `make feature-create name=feature-name` for complete scaffolding
- **Epic Features**: Add `epic=true` parameter: `make feature-create name=big-project epic=true`
- **Status Updates**: Use `make feature-status name=X stage=Y`
- **Epic features** span 2-4 sprints, regular features fit in 1 sprint

### Front Matter Requirements
All Markdown files require front matter with:
- `title`, `type`, `date`, `tags`, `links`
- Feature overviews must include `feature: <name>`, optional `dependencies`, and `epic: true/false`
- Epic features should include `epic_id` and `planned_sprints`

### Validation Gates
- **Gate A**: Decision must exist and be accepted before task creation
- **Gate B**: Tasks must have valid story points and dependencies
- **Gate C**: Feature dependencies must be satisfied
- **Gate D**: Daily status required on work days (Mon-Fri)
- **Gate E**: Sprint health monitoring and burndown tracking

### Sprint Health Indicators
- **🟢 Green**: On track, minimal blockers
- **🟡 Yellow**: Some blockers or slightly behind schedule
- **🔴 Red**: >30% blocked OR <50% progress by Wednesday

## Automation Features

### Daily Status
- **Auto-generates** on weekdays, skips weekends
- **Special templates** for Monday (weekend summary) and Friday (week wrap-up)
- **Sprint metrics** included automatically
- **Blocker tracking** with duration monitoring

### Sprint Tracking
- **Velocity calculation** from story points
- **ASCII burndown charts** showing remaining work
- **Health monitoring** with early warning indicators
- **Dependency validation** to prevent blocked work

### Feature Ordering
- **Dependency-aware** ordering in all status reports
- **Roadmap integration** with now/next/later priorities
- **Epic progress** tracking across multiple sprints

## Quick Reference

```bash
# Daily workflow
make daily               # End of each work day
make sprint-status       # Check progress anytime
make dashboard          # Full project overview

# Sprint workflow (weekly)
make sprint-plan        # Monday: Plan sprint
make sprint-close       # Friday: Close with retrospective

# Feature workflow
make feature-create name=X    # Create new feature
make feature-list            # View all features
make roadmap                 # View roadmap

# Parking Lot (Future Ideas)
make parking-add type=features title="Idea" desc="Description"
make parking-list           # Review all items by category
make parking-review         # Quarterly review interface
make parking-promote item=FEAT-001 target=later  # Move to roadmap

# Issue Backlog (Bugs & Urgent Work)
make backlog-add type=bug title="Bug" severity=P1 desc="Issue"
make backlog-list           # View all issues with severity
make backlog-triage issue=BUG-001  # AI analysis for P0 issues
make backlog-assign issue=BUG-001 sprint=current  # Assign to sprint
make backlog-rubric         # View P0-P4 severity guidelines

# Validation
make validate               # Check all rules
make test-system           # Test all automation
```