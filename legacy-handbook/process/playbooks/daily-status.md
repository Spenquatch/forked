---
title: Playbook - Daily Status Update
type: process
date: 2025-09-21
tags: [process, playbook, status, daily]
links: [../automation/daily_status_check.py, ./sprint-planning.md]
---

# Playbook - Daily Status Update

## Purpose
Maintain daily momentum and visibility through automated status updates that integrate with sprint and feature tracking.

## When
Every working day at end of day (Monday-Friday, auto-skips weekends)

## Automation Overview

### Automated Daily Status
```bash
make daily              # Generate daily status template
make daily-check        # Check if daily status is current
make daily-force        # Force generation (even on weekends)
```

**The system automatically**:
- Skips weekends (Saturday/Sunday)
- Generates templates with current sprint context
- Includes sprint metrics and task progress
- Provides Monday (weekend summary) and Friday (week wrap-up) templates
- Tracks if daily status is overdue (>24 hours)

### Daily Status Structure
**Location**: `status/daily/YYYY-MM-DD.md`

**Auto-generated content**:
- Current sprint ID and progress
- Active tasks with current status
- Sprint metrics (points completed/remaining)
- Special templates for Monday/Friday

**Manual input sections**:
- Progress updates on specific tasks
- Completed work today
- Blockers encountered
- Decisions made
- Tomorrow's focus

## Daily Workflow

### End-of-Day Routine (5 minutes)

1. **Check critical backlog items**:
   ```bash
   make backlog-list severity=P0    # Check for production issues
   make backlog-list severity=P1    # Review high priority bugs
   ```

2. **Update task status** (if changed during day):
   ```bash
   make task-status id=TASK-001 status=review    # If completed work
   make task-status id=TASK-002 status=blocked   # If hit blocker
   ```

3. **Generate daily status**:
   ```bash
   make daily              # Creates template with current context
   ```

4. **Edit daily status** in `status/daily/YYYY-MM-DD.md`:
   - Update progress on active tasks
   - Document completed work
   - Note any blockers or decisions
   - Record any backlog items addressed
   - Set tomorrow's priorities

5. **Check sprint health and capacity**:
   ```bash
   make sprint-status      # See health indicators
   make sprint-capacity    # View 80/20 allocation usage
   ```

### Monday Morning Routine (Weekend Summary)

The Monday template automatically includes:
- Weekend summary section
- Review of any weekend commits/PRs
- Check of monitoring/alerts
- Sprint context reset

### Friday Evening Routine (Week Wrap-up)

The Friday template automatically includes:
- Week summary section
- Sprint progress assessment
- Key achievements section
- Carry-over items identification

## Integration with Sprint System

### Sprint Metrics Integration
Daily status automatically includes:
- **Total sprint points**: All tasks in current sprint
- **Completed points**: Tasks marked as "done"
- **In progress points**: Tasks being worked on
- **Velocity percentage**: Progress toward sprint goal

### Task Status Integration
- Daily status pulls current task states
- Shows which tasks are active, blocked, or completed
- Provides context for task progress updates

### Feature Progress Integration
- Daily status can reference feature completion
- Links to auto-updated feature status files
- Shows how daily work contributes to feature goals

## Daily Status Template Structure

### Auto-Generated Sections
```markdown
## Sprint: SPRINT-YYYY-W##
- Sprint progress overview
- Active tasks list
- Sprint metrics

## Progress
- [ ] TASK-001: [Auto-filled with current status]
- [ ] TASK-002: [Auto-filled with current status]

## Sprint Metrics
- Total Points: X
- Completed: Y
- Velocity: Z%
```

### Manual Input Sections
```markdown
## Completed Today
- [Manual] List what was actually completed
- [Manual] Note any backlog items resolved

## Blockers
- [Manual] Any issues encountered
- [Manual] New P0/P1 issues discovered

## Decisions
- [Manual] Technical decisions made
- [Manual] Backlog items deferred or escalated

## Backlog Impact
- [Manual] P0 issues addressed: []
- [Manual] P1 issues in progress: []
- [Manual] New issues discovered: []

## Tomorrow/Monday Focus
- [Manual] Priorities for next work day
- [Manual] Critical backlog items to address
```

## Quality Guidelines

### Effective Daily Status
- **Specific**: "Completed OAuth integration tests" not "worked on auth"
- **Blockers**: Include what help is needed and from whom
- **Decisions**: Document rationale for future reference
- **Realistic**: Tomorrow's focus should be achievable

### Integration Points
- **Link to tasks**: Reference specific TASK-IDs when relevant
- **Sprint awareness**: Note how work contributes to sprint goals
- **Feature context**: Connect daily work to feature advancement
- **Release timeline**: Consider impact on release schedule

## Automation Benefits

### For Individuals
- **No setup overhead**: Template auto-generated with context
- **Sprint integration**: Automatically connected to current work
- **Weekend relief**: No alerts or generation on weekends
- **Progress tracking**: Visual connection to sprint/feature progress

### For Teams
- **Visibility**: Everyone's daily progress visible
- **Coordination**: Blockers and decisions shared
- **Velocity tracking**: Real progress data for planning
- **Health monitoring**: Early warning on sprint issues

### For Project Management
- **Automatic rollup**: Daily statuses inform sprint metrics
- **Feature tracking**: Daily work rolls up to feature completion
- **Release monitoring**: Sprint progress affects release timeline
- **Historical data**: Daily logs provide velocity and blocker analysis

## Troubleshooting

### Daily Status Issues

**Forgot to run daily status**
```bash
make daily-check        # See how many hours overdue
make daily              # Generate for today
```

**Weekend generation**
```bash
# System skips weekends automatically
# Use make daily-force only if actually working weekends
```

**Missing sprint context**
```bash
make sprint-plan        # Create current sprint if missing
make task-list          # See available tasks
```

**Template seems empty**
```bash
# Need active sprint tasks for rich templates
make task-create title="Sample Task" feature=feature-name decision=ADR-001 points=3 owner=@me
```

## Success Patterns

### Effective Daily Updates
1. **End-of-day habit**: Consistent timing builds routine
2. **Honest reporting**: Include struggles and unknowns
3. **Forward-looking**: Always set next day priorities
4. **Sprint-aware**: Connect work to sprint goals
5. **Blocker escalation**: Don't let blockers sit >24 hours

### Team Coordination
1. **Read others' status**: Stay aware of team progress
2. **Offer help**: Respond to blockers you can resolve
3. **Share decisions**: Technical choices that affect others
4. **Celebrate wins**: Acknowledge completed work

The daily status system provides **sustainable momentum** through **automated infrastructure** while capturing the **human insights** that drive effective team coordination.