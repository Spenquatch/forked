# Project Handbook

**Deterministic project management with daily status, weekly sprints, and automated workflows.**

## 🎯 Overview

This project handbook provides a complete sprint and release management system built on text files, git, and automation. It separates durable feature documentation from sprint-based task execution while enforcing a deterministic, validator-checked workflow.

## 🚀 Quick Start

```bash
# Get started with your first sprint
make sprint-plan          # Create weekly sprint
make daily               # Generate daily status
make feature-create name=my-feature  # Create new feature
make dashboard           # See everything at once
```

## 📋 System Architecture

### Core Concepts

- **Daily Status** → **Weekly Sprints** → **Multi-Sprint Releases** → **Quarterly Roadmap**
- **80/20 Capacity Model**: 80% planned work, 20% reactive (P0/P1 issues)
- **Parking Lot**: Future ideas awaiting quarterly promotion to roadmap
- **Issue Backlog**: P0-P4 severity system with AI triage for critical issues
- **Story Points** with Fibonacci sequence (1,2,3,5,8,13,21)
- **Task Dependencies** within sprints
- **Epic Features** that span multiple sprints
- **Weekend-Aware** automation (Monday-Friday work weeks)

### Directory Structure

```
project-handbook/
├── sprints/             # Sprint directories with detailed task subdirectories
├── features/            # Feature documentation with epic support
├── roadmap/             # Now/Next/Later planning
├── parking-lot/         # Future ideas and research items
├── backlog/             # Bug tracking and urgent issues
├── status/              # Generated dashboards and daily status files
├── process/             # Automation scripts and validation
├── docs/                # System documentation
└── releases/            # Release notes and changelogs
```

## 📈 Complete Command Reference

### Daily Operations
```bash
make daily               # Generate daily status (auto-skips weekends)
make daily-force         # Force generation (even on weekends)
make daily-check         # Check if daily status is current
```

### Sprint Management (1-Week Sprints)
```bash
# Monday: Start Sprint
make sprint-plan         # Create new sprint plan
make sprint-status       # Check sprint health (🟢🟡🔴)
make burndown           # ASCII burndown chart

# Friday: Close Sprint
make sprint-close        # Generate retrospective with metrics
```

### Feature Management
```bash
# Create Features
make feature-create name=my-feature     # Regular feature 📦
make feature-create name=big-project epic=true  # Epic feature 🎯

# Manage Features
make feature-list        # List all features with status
make feature-status name=my-feature stage=development  # Update stage
```

### Roadmap & Planning
```bash
make roadmap            # Show Now/Next/Later roadmap
make roadmap-create     # Create roadmap template
make roadmap-validate   # Validate roadmap links
```

### Parking Lot Management (Future Ideas)
```bash
make parking-add type=features title="Idea" desc="Description"  # Add future idea
make parking-list       # List all parking lot items by category
make parking-review     # Quarterly review interface
make parking-promote item=FEAT-001 target=later  # Promote to roadmap
```

### Issue Backlog (Bugs & Wildcards)
```bash
make backlog-add type=bug title="Bug" severity=P1 desc="Issue"  # Add bug/issue
make backlog-list       # List all backlog issues with severity
make backlog-triage issue=BUG-001  # Generate AI analysis for P0
make backlog-assign issue=BUG-001 sprint=current  # Assign to sprint
make backlog-rubric     # Show P0-P4 severity classification
```

### Validation & Status
```bash
make validate           # Run all validation checks
make status             # Generate project status with feature updates
make check-all          # Validate + status together
```

### Utilities
```bash
make dashboard          # Complete project overview
make test-system        # Test all automation
make install-hooks      # Set up git hooks
make clean             # Clean generated files
make help              # Show all commands
```

## 🔄 Deterministic Lifecycle

### 1. **DECIDE** - Create Decisions
- **ADR** (Architecture Decision Record) - Global decisions
- **FDR** (Feature Decision Record) - Feature-specific decisions
- **Status**: draft → accepted → implemented

### 2. **PLAN** - Sprint Planning
```bash
make sprint-plan  # Monday morning
# - Review backlog
# - Calculate capacity (team × 5 days × velocity)
# - Select work with dependencies
# - Set sprint goals
```

### 3. **EXECUTE** - Daily Work
```bash
make daily  # End of each day
# - Update task status (todo → doing → review → done)
# - Track blockers and decisions
# - Monitor sprint health
```

### 4. **REPORT** - Sprint Progress
```bash
make sprint-status  # Check health indicators
make burndown       # View progress visualization
```

### 5. **VALIDATE** - Quality Gates
```bash
make validate  # Before closing sprint
# - All story points assigned
# - Dependencies satisfied
# - No missing task fields
```

### 6. **CLOSE** - Sprint Completion
```bash
make sprint-close  # Friday evening
# - Generate retrospective
# - Calculate velocity
# - Update feature status
```

## 📊 Sprint Health Indicators

| Status | Indicator | Meaning |
|--------|-----------|---------|
| 🟢 Green | On track | Normal progress, minimal blockers |
| 🟡 Yellow | At risk | Some blockers or slightly behind |
| 🔴 Red | Blocked | >30% blocked or <50% progress by Wednesday |

## 🎯 Task Management

### Task Schema (in `sprints/current/tasks/TASK-XXX-name/task.yaml`)
```yaml
- id: TASK-XXX
  title: Task description
  feature: feature-name
  decision: ADR-001 or FDR-feature-001
  owner: @username
  status: todo|doing|review|done|blocked
  story_points: 5                    # Fibonacci: 1,2,3,5,8,13,21
  depends_on: [TASK-YYY]            # Task dependencies
  prio: P1                          # P0 (urgent) to P3 (low)
  due: 2025-09-25
  acceptance:
    - Acceptance criteria 1
    - Acceptance criteria 2
  links: []
```

### Status Transitions
```
todo → doing → review → done
 ↓       ↓
blocked → (back to todo or doing when unblocked)
```

## 🏗️ Feature Management

### Feature Types
- **📦 Regular Features**: Fit within 1 sprint
- **🎯 Epic Features**: Span 2-4 sprints

### Feature Stages
```
proposed → approved → developing → complete → live → deprecated
```

### Creating Features
```bash
# Creates complete directory structure:
make feature-create name=user-auth

features/user-auth/
├── overview.md           # Feature definition
├── architecture/         # Technical design
├── implementation/       # Implementation notes
├── testing/             # Test strategy
├── fdr/                 # Feature Decision Records
├── status.md            # Current status
├── changelog.md         # Change history
└── risks.md             # Risk register
```

## 📅 Release Cycles

- **Minor Release**: 2 sprints (2 weeks)
- **Standard Release**: 3 sprints (3 weeks)
- **Major Release**: 4 sprints (4 weeks)

## 🎯 80/20 Sprint Capacity Allocation

### Capacity Management Philosophy
The system implements an 80/20 capacity allocation to balance predictability with flexibility:

### Planned Work (80% of capacity)
- Features and tasks from current release
- Committed sprint goals and objectives
- Planned technical improvements
- Scheduled refactoring and tech debt

### Reactive Work (20% of capacity)
- P0/P1 issues from backlog system
- Urgent wildcards and escalations
- Critical bug fixes and hotfixes
- Customer-reported urgent issues

### Workflow Integration
```bash
# During sprint planning
make sprint-plan         # Allocates 80% to planned work
make backlog-list        # Review P0-P1 issues for 20% allocation

# During sprint execution
make backlog-assign issue=BUG-001 sprint=current  # Uses reactive capacity

# Check capacity usage
make sprint-status       # Shows planned vs reactive work
```

### Issue Severity Guidelines
| Severity | Impact | Action |
|----------|--------|--------|
| P0 - Critical | >50% users affected, data loss, security | Interrupt immediately |
| P1 - High | 10-50% users affected, major feature broken | Current sprint (20% capacity) |
| P2 - Medium | <10% users affected, minor issues | Next sprint planning |
| P3 - Low | Cosmetic, developer experience | Backlog queue |
| P4 - Wishlist | Future enhancements | Consider parking lot |

## 🤖 Automation Features

### Daily Status
- **Auto-generates** on weekdays at 5 PM (configurable)
- **Special templates** for Monday (weekend summary) and Friday (week wrap-up)
- **Sprint metrics** included automatically
- **Git hooks** remind you if overdue

### Sprint Tracking
- **Velocity calculation** from story points
- **Burndown charts** in ASCII art
- **Health monitoring** with early warnings
- **Dependency validation** prevents blocked work

### Validation System
- **Front matter** validation on all markdown files
- **Task schema** validation (story points, dependencies)
- **Link checking** in roadmaps
- **Circular dependency** detection

## 🔍 Example Workflows

### Starting a New Sprint (Monday)
```bash
# 1. Close previous sprint
make sprint-close

# 2. Check critical backlog items
make backlog-list severity=P0,P1  # Review urgent issues
make backlog-rubric               # Understand severity levels

# 3. Plan new sprint (80% planned, 20% reactive)
make sprint-plan

# 4. Assign P0/P1 items to sprint
make backlog-assign issue=BUG-P0-001 sprint=current

# 5. Review plan and commit to goals
# Edit sprints/YYYY/SPRINT-YYYY-W##/plan.md

# 6. Start daily tracking
make daily
```

### Daily Development Flow
```bash
# Morning: Check critical issues
make backlog-list severity=P0     # Any production issues?
make sprint-status                # Check sprint health

# During day: Update task status in sprint task directories
# If P0 issue arises:
make backlog-add type=bug title="Critical bug" severity=P0 desc="Details"
make backlog-triage issue=BUG-P0-001  # Get AI analysis
make backlog-assign issue=BUG-P0-001 sprint=current

# End of day: Generate daily status
make daily

# If blockers: Update blocked_reason field
# If dependencies: Check depends_on field
```

### Feature Development
```bash
# Check if feature originated from parking lot
make parking-list           # Review future ideas

# Create feature (possibly promoted from parking lot)
make feature-create name=new-feature
# If from parking lot, update feature overview.md:
# parking_lot_origin: FEAT-001

# Link any related backlog items in feature overview
# backlog_items: [BUG-P1-123, WILD-P2-456]

# Update feature as it progresses
make feature-status name=new-feature stage=development
make feature-status name=new-feature stage=complete

# Check all features
make feature-list
```

### Quarterly Planning Workflow
```bash
# 1. Review parking lot for promotion
make parking-review          # Interactive quarterly review
make parking-list           # See all categorized items

# 2. Promote valuable ideas to roadmap
make parking-promote item=FEAT-001 target=next
make parking-promote item=RESEARCH-002 target=later

# 3. Archive outdated ideas
make parking-archive item=OLD-001

# 4. Update roadmap with promoted items
make roadmap                # View current roadmap
# Edit roadmap/now-next-later.md to include promoted items
```

### Sprint Health Monitoring
```bash
# Quick status check
make sprint-status
# Output: Sprint: SPRINT-2025-W38
#         Day 3 of 5
#         Health: 🟡 YELLOW - Some blockers need attention
#         Progress: 15/30 points (50%)

# Detailed burndown
make burndown
# Output: ASCII chart showing remaining work
```

## 🛠️ Configuration

The system uses sensible defaults but key settings can be customized:

- **Work Week**: Monday-Friday (5 days)
- **Story Points**: Fibonacci sequence
- **Sprint Buffer**: 20% for unknowns
- **Daily Reminder**: Check if status overdue
- **Health Thresholds**: Configurable in scripts

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | This overview |
| `CLAUDE.md` | Claude Code integration guide |
| `CONVENTIONS.md` | Validation rules and schemas |
| `SPRINT_SYSTEM.md` | Sprint system details |
| `MAKEFILE_COMMANDS.md` | Complete command reference |
| `workflow-diagram.md` | Visual workflow diagrams |

## 🔗 Integration

### Git Hooks (Optional)
```bash
make install-hooks
# Sets up:
# - post-commit: Check daily status
# - pre-push: Run validation
```

### Status Dashboard
```bash
make dashboard
# Complete project overview:
# - Current sprint status
# - Recent daily status files
# - Validation results
# - Feature progress
```

## 🆘 Troubleshooting

### Common Issues

**Daily status missing**
```bash
make daily-check  # Check status
make daily        # Generate if needed
```

**Sprint health issues**
```bash
make sprint-status  # Check health indicators
make burndown       # See progress visualization
# If red: Review blockers and dependencies
```

**Validation errors**
```bash
make validate  # See specific issues
# Common fixes:
# - Add missing front matter
# - Fix story point values (use Fibonacci)
# - Resolve dependency issues
```

**Feature management**
```bash
make feature-list  # See all features
# Update stages as work progresses
make feature-status name=my-feature stage=development
```

## 🎯 Best Practices

1. **Daily Discipline**: Run `make daily` every working day
2. **Sprint Planning**: Use actual velocity for capacity planning
3. **Dependencies**: Define task dependencies upfront
4. **Story Points**: Use team estimation sessions for consistency
5. **Blockers**: Escalate after 24 hours
6. **Validation**: Run `make check-all` before pushing
7. **Features**: Keep epic features to 2-4 sprints max

---

**Quick Reference**: Run `make help` for all available commands, or `make dashboard` for current project status.

The system is designed to be simple, deterministic, and automation-friendly while providing rich project insights and maintaining high quality standards.