---
title: Guard CLI Contract - Commands
type: commands
date: 2025-09-22
task_id: TASK-002
tags: [commands]
links: []
---

# Commands: Guard CLI Contract

## Task Status Updates
```bash
# When starting work
cd legacy-handbook/sprints/current/tasks/TASK-002-guard-cli-contract/
# Edit task.yaml: change status from "todo" to "doing"

# When ready for review
# Edit task.yaml: change status to "review"

# When complete
# Edit task.yaml: change status to "done"
```

## Validation Commands
```bash
# Generate guard report (expect exit 2 on violations)
forked guard --overlay overlay/test --mode block || true

# Inspect report metadata
cat .forked/report.json | jq '.report_version'

# Update daily status
make daily
```

## Implementation Commands
```bash
# Run guard with warn mode while iterating
forked guard --overlay overlay/test --mode warn

# Verify sentinel behaviour when deleting trunk-owned file
repo_name=$(basename "$(git rev-parse --show-toplevel)")
git -C ../.forked-worktrees/$repo_name/test rm README.md
forked guard --overlay overlay/test --mode warn || true
```

## Git Integration
```bash
# Commit with task reference
git commit -m "feat: finalize guard cli contract

Implements TASK-002 for guard-automation feature.
Part of sprint: SPRINT-2025-W42

Refs: #TASK-002"

# Link PR to task (in PR description)
# Closes #TASK-002
# Implements ADR-0002
```

## Quick Copy-Paste
```bash
forked guard --overlay overlay/test --mode block || echo "violations detected"
```
