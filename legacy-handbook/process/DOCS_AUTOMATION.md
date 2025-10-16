---
title: Docs Automation
type: process
date: 2025-09-21
tags: [automation]
links: []
---

# Docs Automation

## Current Automation (Implemented)

### Validators
- **`process/checks/validate_docs.py`** - Comprehensive validation system
  - Front matter validation on all markdown files
  - Sprint task directory validation with story points and dependencies
  - Sprint-scoped dependency enforcement (no cross-sprint dependencies)
  - Legacy execution phase support (backwards compatibility)

### Generators (Implemented)
- **`status/generate_project_status.py`** - Enhanced status generation
  - Dependency-aware feature ordering
  - Sprint task aggregation
  - Feature status auto-updates
  - Roadmap integration

- **`process/automation/feature_status_updater.py`** - Feature status automation
  - Auto-injects "Active Work" sections into feature `status.md` files
  - Calculates feature metrics from sprint tasks
  - Shows current sprint tasks and completion percentages

- **`process/automation/daily_status_check.py`** - Daily status automation
  - Weekend-aware daily status generation
  - Sprint metrics integration
  - Blocker tracking

- **`process/automation/sprint_manager.py`** - Sprint lifecycle automation
  - Sprint planning with release context
  - Burndown chart generation
  - Retrospective templates
  - Velocity tracking

- **`process/automation/release_manager.py`** - Release management
  - Release planning and feature assignment
  - Release progress tracking
  - Release health indicators
  - Sprint-release coordination

- **`process/automation/task_manager.py`** - Task directory management
  - Complete task directory creation (README, steps, commands, etc.)
  - Task status updates with validation
  - Sprint-scoped dependency management

- **`process/automation/roadmap_manager.py`** - Roadmap management
  - Roadmap link normalization
  - Roadmap display formatting
  - Roadmap validation

- **`process/automation/parking_lot_manager.py`** - Parking lot management
  - Add future ideas by category (features, technical-debt, research, external-requests)
  - Quarterly review and promotion workflows
  - JSON index rollup automation
  - Integration with roadmap planning

- **`process/automation/backlog_manager.py`** - Issue backlog management
  - Bug and wildcard tracking with P0-P4 severity
  - AI-powered triage analysis and recommendations for P0 issues
  - Sprint assignment with 80/20 capacity allocation
  - Severity rubric and escalation workflows
  - JSON index rollup automation

### File Generators

The system now automatically generates/updates:

1. **`status/current.json|yml`** - Project status rollup
2. **`features/*/status.md`** - Active Work sections with sprint task data
3. **`sprints/*/burndown.md`** - ASCII burndown charts
4. **`sprints/*/retrospective.md`** - Sprint retrospective templates
5. **`releases/*/progress.md`** - Release progress tracking
6. **`status/daily/*.md`** - Daily status templates
7. **`roadmap/now-next-later.md`** - Link normalization
8. **`parking-lot/index.json`** - Parking lot item rollup
9. **`backlog/index.json`** - Issue backlog rollup with severity tracking
10. **`backlog/*/triage.md`** - AI triage analysis templates for P0 issues

## Current Commands

### Validation
```bash
make validate           # Run all validation checks
```

### Status Generation
```bash
make status             # Generate project status with feature updates and dependency ordering
```

### Feature Status Updates
```bash
make feature-update-status    # Update all feature status files from sprints
make feature-summary          # Show feature progress with sprint data
```

### Daily Automation
```bash
make daily              # Generate daily status (weekend-aware)
make daily-check        # Check if daily status is current
```

### Sprint Automation
```bash
make sprint-plan        # Create sprint with release context
make sprint-status      # Show health indicators and progress
make burndown          # Generate ASCII burndown chart
make sprint-close      # Generate retrospective with metrics
```

### Release Automation
```bash
make release-plan version=v1.2.0 sprints=3   # Create release plan
make release-status                           # Show release progress
make release-add-feature release=v1.2.0 feature=auth-system
```

### Task Automation
```bash
make task-create title="Task Name" feature=feature-name decision=ADR-001 points=5 owner=@alice prio=P1
make task-status id=TASK-001 status=doing     # Update task status
```

### Parking Lot Management
```bash
make parking-add type=features title="Title" desc="Description"
make parking-list           # List all parking lot items
make parking-review         # Quarterly review interface
make parking-promote item=FEAT-001 target=later
```

### Issue Backlog Management
```bash
make backlog-add type=bug title="Title" severity=P1 desc="Description"
make backlog-list           # List all backlog issues
make backlog-triage issue=BUG-001  # Generate AI analysis for P0 issues
make backlog-assign issue=BUG-001 sprint=current
make backlog-rubric         # Show P0-P4 severity rubric
```

## Automation Architecture

### Hierarchy Integration
```
Roadmap (manual)
    ↓ (informs)
Releases (planned) → Auto-tracks progress from features
    ↓ (coordinates)
Features (strategic) → Auto-updates from sprint tasks
    ↓ (implemented via)
Sprints (tactical) → Auto-generates burndown and retrospectives
    ↓ (breaks into)
Tasks (implementation) → Auto-generates complete directory structure
```

### Auto-Update Chain
1. **Task status changes** → Sprint metrics update → Feature progress updates → Release progress updates
2. **Daily status** → Sprint health calculation → Release timeline tracking
3. **Sprint completion** → Feature status advancement → Release milestone tracking

### Validation Chain
1. **Front matter** validation on all markdown files (except docs/)
2. **Sprint task** validation (story points, dependencies, required files)
3. **Dependency validation** (sprint-scoped only, no cross-sprint deps)
4. **Feature validation** (proper structure and metadata)
5. **Release validation** (feature assignments and timelines)

## Future Enhancements (Planned)

### Advanced Generators
- **Changelog automation** from completed tasks and features
- **Release notes** generation from sprint retrospectives
- **Velocity trend** analysis across multiple sprints
- **Capacity planning** automation based on historical data

### Notification Integration
- **Slack/Discord** webhooks for blockers and sprint health
- **Email digest** for weekly sprint summaries
- **Git hook** automation for status reminders

### Advanced Validation
- **Circular dependency** detection across features
- **Capacity validation** (story points vs team velocity)
- **Timeline validation** (release feasibility checking)
- **Quality gates** for release readiness

## System Status

- ✅ **Validation System**: Complete and functional
- ✅ **Status Generation**: Enhanced with dependency ordering
- ✅ **Feature Updates**: Auto-generated from sprint tasks
- ✅ **Sprint Management**: Full lifecycle automation
- ✅ **Release Tracking**: Integrated with features and sprints
- ✅ **Task Management**: Complete directory automation
- ✅ **Daily Workflow**: Weekend-aware automation

**All automation is production-ready and integrated through Make commands.**