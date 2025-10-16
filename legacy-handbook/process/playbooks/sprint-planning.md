---
title: Playbook - Sprint Planning
type: process
date: 2025-09-21
tags: [process, playbook, sprint, planning]
links: [./daily-status.md, ../automation/sprint_manager.py, ../automation/release_manager.py]
---

# Playbook - Sprint Planning

## Purpose
Plan and launch a new weekly sprint with clear goals, committed work, and success criteria using the automated sprint system.

## When
Every Monday morning (or first working day of week)

## Duration
1 week (5 working days, Monday-Friday)

## Pre-Planning Checklist
- [ ] Previous sprint retrospective completed (`make sprint-close`)
- [ ] Release context understood (`make release-status`)
- [ ] Feature priorities reviewed (`make feature-summary`)
- [ ] Team availability confirmed (PTO, meetings, other commitments)

## Automated Sprint Setup

### 1. Create Sprint Structure
```bash
make sprint-plan
```

This **automatically generates**:
- Sprint directory: `sprints/YYYY/SPRINT-YYYY-W##/`
- Sprint ID based on current week
- Sprint date range (Monday-Friday)
- Release context (if current release exists)
- Planning template with capacity framework
- Task and daily status directories

### 2. Review Release Context
The generated plan shows:
- **Current release** goals and timeline
- **Features assigned** to this release
- **Critical path** features requiring attention
- **Sprint position** within release (e.g., "Sprint 2 of 3")

## Human Planning Process

### 3. Define Sprint Goals
Edit the generated `sprints/current/plan.md`:

**Framework**:
- **Primary Goal** (60% of capacity): Must achieve
- **Secondary Goal** (30% of capacity): Should achieve
- **Stretch Goal** (10% of capacity): Bonus if time permits

**Examples**:
- Primary: "Complete OAuth integration for auth-system feature"
- Secondary: "Begin API v2 endpoint implementation"
- Stretch: "Polish admin dashboard if auth ahead of schedule"

### 4. Calculate Team Capacity with 80/20 Allocation

**Formula**:
```
Total Capacity = Team Members × 5 days × Individual Velocity

Planned Work (80%) = Total Capacity × 0.80
  - Release features and committed sprint goals
  - Scheduled improvements and tech debt

Reactive Work (20%) = Total Capacity × 0.20
  - P0/P1 issues from backlog
  - Urgent wildcards and escalations
```

**Review Backlog for 20% Allocation**:
```bash
make backlog-list severity=P0  # Check for critical issues
make backlog-list severity=P1  # Check for high priority issues
make backlog-rubric            # Review severity guidelines
```

**Considerations**:
- **Historical velocity**: Check previous sprint retrospectives
- **Team availability**: Account for PTO, meetings, training
- **Sprint overlap**: Account for reviews, deployment, support
- **Learning curve**: New technology or team members
- **Current P0/P1 count**: May need to adjust 80/20 ratio if high severity backlog

### 5. Select and Create Tasks

#### Priority Order for Task Selection:

**For Planned Work (80% capacity)**:
1. **Release critical path** features (check `make release-status`)
2. **Carried-over tasks** from previous sprint
3. **Unblocked tasks** that were previously blocked
4. **High-priority features** from current release
5. **Technical debt** and scheduled improvements
6. **Nice-to-have** work if capacity remains

**For Reactive Work (20% capacity)**:
1. **P0 issues** - Assign immediately if any exist
2. **P1 issues** - Assign to current sprint
3. **Urgent wildcards** - Executive/stakeholder requests
4. **Reserve remaining** - Keep buffer for mid-sprint interrupts

#### Task Creation Workflow:
```bash
# Basic task creation (uses configured defaults):
make task-create title="Setup OAuth Integration" feature=auth-system decision=ADR-005

# With optional parameters for customization:
make task-create title="Setup OAuth Integration" feature=auth-system decision=ADR-005 points=8 owner=@alice prio=P0

# Review created task directory:
# sprints/current/tasks/TASK-XXX-setup-oauth-integration/
# Edit: steps.md, commands.md, checklist.md as needed
```

#### Task Sizing Guidelines:
- **1 point**: Trivial (fix typo, config change)
- **2 points**: Very small (simple validation, minor update)
- **3 points**: Small (basic feature, straightforward task)
- **5 points**: Medium (typical development task)
- **8 points**: Large (complex feature, multiple components)
- **13+ points**: Too large - must break down further

### 6. Set Task Dependencies
```bash
# Edit task.yaml files to add dependencies within sprint
depends_on: [TASK-001, TASK-002]  # Only tasks from current sprint
```

**Rule**: Dependencies can **only** be within current sprint. Cross-sprint coordination happens at the feature level.

### 7. Assign Ownership
```bash
# Edit task.yaml files to assign owners
owner: @alice
owner: @bob
```

### 8. Validate Sprint Setup
```bash
make validate           # Check all task directories are complete
make sprint-status      # Verify sprint health
make task-list          # Review all committed tasks
```

## Sprint Execution Guidelines

### Daily Routine (Tuesday-Friday)
```bash
# Team members update task status as work progresses
make task-status id=TASK-001 status=doing      # When starting
make task-status id=TASK-001 status=review     # When ready for review
make task-status id=TASK-001 status=done       # When complete

# End of each day
make daily              # Generate daily status (auto-skips weekends)
```

### Mid-Sprint Health Check (Wednesday)
```bash
make sprint-status      # Check health indicators
make burndown          # Visual progress check
make release-status    # Release timeline impact
```

**Health Indicators**:
- 🟢 **Green**: On track, minimal blockers
- 🟡 **Yellow**: Some blockers or slightly behind
- 🔴 **Red**: >30% blocked OR <50% progress by Wednesday

**Actions for Yellow/Red**:
- Review blocked tasks and escalate
- Consider scope reduction
- Request help or pair programming
- Update release timeline if needed

### Sprint Close (Friday)
```bash
make sprint-close       # Generate retrospective with velocity metrics
```

## Advanced Planning Techniques

### 80/20 Capacity Management

**Handling P0 Interrupts Mid-Sprint**:
```bash
# When P0 issue appears
make backlog-add type=bug title="Production down" severity=P0 desc="Critical failure"
make backlog-triage issue=BUG-P0-001  # Get AI analysis

# Review triage recommendations
# Decide: Hotfix vs Proper fix
# Assess impact on sprint commitments

# Assign to sprint (interrupts immediately)
make backlog-assign issue=BUG-P0-001 sprint=current
```

**Adjusting Capacity Ratios**:
- **Normal sprints**: 80% planned, 20% reactive
- **High-incident periods**: 60% planned, 40% reactive
- **Feature-focused sprints**: 90% planned, 10% reactive
- **Support rotation**: 50% planned, 50% reactive

### Release-Driven Planning
```bash
# Check release context first
make release-status

# Plan sprint tasks to advance release features
# Focus on critical path features
# Ensure release timeline is realistic
```

### Feature-Driven Planning
```bash
# Review feature progress
make feature-summary

# Select tasks that advance key features
# Balance epic features (multi-sprint) with regular features (single sprint)
# Ensure feature dependencies are satisfied
```

### Capacity-Driven Planning
- **Conservative**: 80% of calculated capacity (safer)
- **Aggressive**: 100% of calculated capacity (risky)
- **Learning sprints**: 60% capacity (team building/training)

## Common Anti-Patterns to Avoid

- ❌ **Overcommitting**: Planning more than historical velocity
- ❌ **Ignoring dependencies**: Creating impossible task sequences
- ❌ **Scope creep**: Adding work mid-sprint
- ❌ **Skipping task creation**: Working without proper task directories
- ❌ **No buffer**: Planning 100% capacity with no unknowns
- ❌ **Release blindness**: Planning without release context

## Success Metrics

### Sprint Planning Success
- **Velocity predictability**: Actual ± 10% of planned story points
- **Goal achievement**: Primary goal always achieved
- **Team satisfaction**: Sustainable pace maintained
- **Release progress**: Contributing to release timeline

### Tools and Integration
- **Sprint automation**: `process/automation/sprint_manager.py`
- **Task management**: `process/automation/task_manager.py`
- **Release context**: `process/automation/release_manager.py`
- **Validation**: `process/checks/validate_docs.py`

## Troubleshooting

### Sprint Planning Issues

**Team velocity unknown**
- Use conservative estimate (5 points/person/sprint)
- Track actual velocity for future planning
- Adjust based on team experience and complexity

**Too many high-priority items**
- Use release context to prioritize
- Push lower priority to next sprint
- Discuss scope with stakeholders

**External dependencies blocking**
- Identify early in planning
- Create contingency tasks
- Escalate dependency resolution

**Task estimation disagreement**
- Use planning poker or similar technique
- Discuss assumptions and complexity
- When in doubt, round up

The sprint planning playbook provides the **human process** that works with the **automated infrastructure** to create effective, sustainable sprints.