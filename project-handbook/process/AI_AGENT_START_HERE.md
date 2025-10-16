---
title: AI Agent Start Here
type: process
date: 2025-09-21
tags: [process, ai, agents]
links: [../docs/SYSTEM_GUIDE.md, ../docs/CLAUDE.md]
---

# AI Agent Start Here

## Quick Orientation (30 seconds)

This is a **sprint-based project handbook** with complete automation. Everything is organized around:

1. **Features** (what we're building) → **Releases** (delivery milestones) → **Sprints** (weekly work) → **Tasks** (implementation details)
2. **Make commands** for everything - no need to remember Python script paths
3. **Rich task directories** with complete implementation guidance
4. **Weekend-aware automation** (Monday-Friday work weeks)

## Essential Commands

```bash
# Get your bearings
make help               # See all available commands
make dashboard          # Complete project overview
make sprint-status      # Current sprint health

# Check critical issues
make backlog-list severity=P0,P1    # Review urgent issues
make backlog-triage issue=BUG-P0-001  # AI analysis for P0 issues

# Daily workflow
make daily              # Generate daily status (auto-skips weekends)
make task-list          # See current sprint tasks
make feature-summary    # See feature progress across sprints

# Working on tasks
make task-status id=TASK-XXX status=doing    # Start work
make task-show id=TASK-XXX                   # See task details
make task-status id=TASK-XXX status=review   # Submit for review
make task-status id=TASK-XXX status=done     # Mark complete
```

## Agent Workflow

### 1. **Understand Current Context**
```bash
make dashboard          # See sprint, features, release status
make release-status     # Understand current release goals
make task-list          # See available work
```

### 2. **Pick Up Task**
```bash
# Choose a task from the list
make task-show id=TASK-001              # See task details
make task-status id=TASK-001 status=doing    # Claim the task
```

### 3. **Get Implementation Guidance**
```bash
# Navigate to task directory
cd sprints/current/tasks/TASK-001-*/

# Read implementation guidance
cat README.md           # Agent navigation & task overview
cat steps.md            # Step-by-step implementation guide
cat commands.md         # Copy-paste terminal commands
cat checklist.md        # Completion criteria
cat validation.md       # How to validate your work
cat references.md       # Links, docs, examples
```

### 4. **Work and Update Progress**
```bash
# Update daily status with progress
make daily              # At end of each work day

# Check sprint health
make sprint-status      # See overall progress
```

### 5. **Submit for Review**
```bash
# Validate your work
cat sprints/current/tasks/TASK-001-*/checklist.md    # Check completion criteria

# Submit for review
make task-status id=TASK-001 status=review

# After approval
make task-status id=TASK-001 status=done
```

## Key Rules for Agents

### Task Management
- **One task at a time**: Update status to "doing" when starting
- **Sprint-scoped dependencies**: Tasks can only depend on other tasks in same sprint
- **Rich guidance**: Every task has complete implementation directory
- **Story points**: Use Fibonacci sequence (1,2,3,5,8,13,21)
- **Capacity awareness**: Sprint allocates 80% planned, 20% reactive work

### Daily Updates
- **End of day**: Run `make daily` to log progress
- **Blockers**: Document in daily status if stuck
- **Weekend awareness**: System auto-skips Saturday/Sunday

### Feature Context
- **Feature connection**: Every task belongs to a feature
- **Decision reference**: Every task implements exactly one ADR/FDR decision
- **Cross-feature work**: Coordinate via feature dependencies, not task dependencies

### Sprint Context
- **Weekly cycles**: Monday (plan) → Tuesday-Thursday (execute) → Friday (close)
- **Health monitoring**: Check `make sprint-status` for 🟢🟡🔴 indicators
- **Burndown tracking**: `make burndown` shows visual progress
- **P0/P1 priority**: Critical issues interrupt planned work (20% capacity reserved)

### Release Context
- **Release goals**: Check `make release-status` for context of current work
- **Feature priorities**: Release assignments guide sprint planning
- **Timeline awareness**: Understand how your work fits into release schedule

## Critical File Locations

### Task Implementation
- **Current tasks**: `sprints/current/tasks/TASK-XXX-name/`
- **Task metadata**: `task.yaml` (status, story points, dependencies)
- **Implementation guide**: `README.md`, `steps.md`, `commands.md`

### Status and Planning
- **Daily status**: `status/daily/YYYY-MM-DD.md`
- **Sprint plan**: `sprints/current/plan.md`
- **Feature status**: `features/feature-name/status.md` (auto-updated)
- **Release plan**: `releases/current/plan.md`

### Documentation
- **System guide**: `docs/SYSTEM_GUIDE.md` - Complete workflows
- **Commands reference**: `docs/MAKEFILE_COMMANDS.md` - All commands
- **Conventions**: `docs/CONVENTIONS.md` - Validation rules

## Troubleshooting

### Common Issues

**Can't find current work**
```bash
make task-list          # See all current sprint tasks
make sprint-status      # See sprint health
make dashboard          # Complete overview
```

**Task directory missing files**
```bash
make validate           # Check for missing files
# Task directories should have: README.md, steps.md, commands.md, checklist.md, validation.md
```

**Validation errors**
```bash
make validate           # See specific issues
# Common: missing story points, invalid dependencies, missing front matter
```

**Sprint/release context unclear**
```bash
make release-status     # See current release goals
make sprint-status      # See current sprint health
make feature-summary    # See feature progress
```

## AI Triage for P0 Issues

### When to Use AI Triage
- **P0 issues only**: Production down, data loss, security breaches
- **Root cause analysis**: Quickly identify probable causes
- **Investigation guidance**: Get structured troubleshooting steps

### Using AI Triage
```bash
# Add P0 issue to backlog
make backlog-add type=bug title="API failing" severity=P0 desc="Details here"

# Run AI triage analysis
make backlog-triage issue=BUG-P0-001

# Review generated triage report
cat backlog/bugs/BUG-P0-*/triage.md
```

### AI Triage Output
The AI analysis provides:
- **Root cause hypotheses**: Ranked by probability
- **Investigation steps**: Specific commands and checks
- **Similar incidents**: Historical pattern matching
- **Team recommendations**: Who to involve based on expertise
- **Mitigation strategies**: Immediate actions to reduce impact

### Acting on AI Triage
1. **Review hypotheses**: Start with highest probability causes
2. **Follow investigation steps**: Execute recommended diagnostics
3. **Document findings**: Update issue with discoveries
4. **Assign to sprint**: Use reactive capacity (20% allocation)

## Success Patterns

### High-Quality Task Completion
1. **Read everything**: README.md → steps.md → commands.md
2. **Follow checklist**: Use checklist.md for completion criteria
3. **Validate thoroughly**: Follow validation.md guidelines
4. **Update status**: Keep task.yaml status current
5. **Daily logging**: Use `make daily` to track progress

### Effective Communication
1. **Daily status**: Log blockers, decisions, progress
2. **Task updates**: Keep status current for team visibility
3. **Sprint health**: Monitor and escalate issues early
4. **Feature progress**: Understand how tasks contribute to feature goals
5. **P0 escalation**: Use AI triage for critical issues immediately

The system is designed to provide **complete context** and **rich guidance** for every piece of work while maintaining **automated coordination** across all levels.