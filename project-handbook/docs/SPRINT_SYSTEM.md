# Sprint & Release Management System

## Overview
This project handbook now includes a complete sprint and release management system with automated daily status, weekly sprints, and multi-sprint releases.

## Key Features Implemented

### ✅ Task Management Enhancements
- **Story Points**: Every task now has `story_points` field (Fibonacci: 1,2,3,5,8,13,21)
- **Dependencies**: Tasks can depend on other tasks with `depends_on: [TASK-ID]`
- **Validation**: Automatic checking for missing fields, invalid dependencies, and story point values

### ✅ Daily Status Automation
- **Weekend-Aware**: Automatically skips Saturday/Sunday
- **24-Hour Check**: Alerts if daily status is overdue
- **Smart Templates**: Monday includes weekend summary, Friday includes week wrap-up
- **Location**: `status/daily/YYYY-MM-DD.md`

### ✅ Sprint Management
- **1-Week Sprints**: Monday to Friday (5 working days)
- **Sprint IDs**: Format `SPRINT-YYYY-W##` based on ISO week number
- **Velocity Tracking**: Automatic calculation of completed vs planned points
- **Health Indicators**:
  - 🟢 Green: On track
  - 🟡 Yellow: Some blockers or slightly behind
  - 🔴 Red: >30% blocked or <50% progress by mid-week

### ✅ Burndown Visualization
```
Sprint Burndown: SPRINT-2025-W38
Points |
  34   |████████████████████ (planned)
  28   |████████████████░░░░
  20   |████████████░░░░░░░░ (actual)
   0   |____________________
       M T W T F
```

### ✅ Automation Scripts
- `process/automation/daily_status_check.py` - Daily status generation
- `process/automation/sprint_manager.py` - Sprint lifecycle management
- `status/generate_project_status.py` - Enhanced with dependency-aware ordering

### ✅ Makefile Commands
```bash
# Daily Operations
make daily           # Generate daily status
make daily-force     # Force generation (even on weekends)

# Sprint Management
make sprint-plan     # Create new sprint (Monday)
make sprint-status   # Check sprint health
make sprint-tasks    # List all sprint tasks
make burndown        # Generate ASCII burndown
make sprint-close    # Create retrospective (Friday)

# Task Management
make task-create title="Setup OAuth" feature=auth decision=ADR-001 points=8
make task-list       # List sprint tasks with status emojis
make task-show id=TASK-001    # Show complete task details
make task-status id=TASK-001 status=doing  # Update status

# Validation & Status
make validate        # Run validation checks
make status          # Generate project status
make dashboard       # Show full dashboard
```

## Workflow

### Weekly Sprint Cycle

**Monday (Sprint Start)**
1. Run `make sprint-close` to finish previous sprint
2. Run `make sprint-plan` to create new sprint
3. Review and commit to sprint goals
4. Run `make daily` to start tracking

**Tuesday-Thursday (Execution)**
1. Update task status via `make task-status id=TASK-XXX status=doing`
2. Read task implementation details in `sprints/current/tasks/TASK-XXX-name/`
3. Run `make daily` at end of day
4. Check `make sprint-status` for health
5. Review `make burndown` for progress

**Friday (Sprint End)**
1. Final `make daily` with week summary
2. Run `make sprint-close` for retrospective
3. Review velocity and metrics
4. Plan for Monday

### Release Cycle (2-3 Sprints)
- **Minor Release**: 2 sprints (2 weeks)
- **Standard Release**: 3 sprints (3 weeks)
- **Major Release**: 4 sprints (4 weeks)

## Epic Features
Features can be marked as epics in their front matter:
```yaml
---
title: Major Platform Overhaul
type: feature
epic: true
epic_id: EPIC-001
planned_sprints: [SPRINT-2025-W38, SPRINT-2025-W39, SPRINT-2025-W40]
---
```

## Directory Structure
```
project-handbook/
├── status/
│   └── daily/              # Daily status files
│       └── YYYY-MM-DD.md
├── sprints/
│   ├── current -> active   # Symlink to active sprint
│   └── YYYY/
│       └── SPRINT-YYYY-W##/
│           ├── plan.md
│           ├── burndown.md
│           └── retrospective.md
├── process/
│   ├── automation/         # Automation scripts
│   └── playbooks/          # Process documentation
└── Makefile                # Convenience commands
```

## Configuration
The system uses sensible defaults:
- 5-day work week (Monday-Friday)
- Story points using Fibonacci sequence
- 20% sprint buffer for unknowns
- 24-hour daily status requirement

## Next Steps
1. Start using `make daily` for daily updates
2. Use `make sprint-plan` on Mondays
3. Track velocity over 3 sprints for accurate planning
4. Add team-specific customizations as patterns emerge