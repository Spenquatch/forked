---
title: Overlay Rebuild Hardening - Commands
type: commands
date: 2025-09-22
task_id: TASK-001
tags: [commands]
links: []
---

# Commands: Overlay Rebuild Hardening

## Task Status Updates
```bash
# When starting work
cd legacy-handbook/sprints/current/tasks/TASK-001-overlay-rebuild-hardening/
# Edit task.yaml: change status from "todo" to "doing"

# When ready for review
# Edit task.yaml: change status to "review"

# When complete
# Edit task.yaml: change status to "done"
```

## Validation Commands
```bash
# Quick smoke rebuild twice to ensure reuse
forked build --id test --auto-continue
forked build --id test --auto-continue

# Inspect worktrees for location & reuse
git worktree list

# Update daily status
make daily
```

## Implementation Commands
```bash
# Run guard to ensure rebuild output is clean
forked guard --overlay overlay/test --mode warn

# Clean up worktree when required
repo_name=$(basename "$(git rev-parse --show-toplevel)")
rm -rf ../.forked-worktrees/$repo_name/test || true
```

## Git Integration
```bash
# Commit with task reference
git commit -m "feat: harden overlay rebuild

Implements TASK-001 for overlay-infrastructure feature.
Part of sprint: SPRINT-2025-W42

Refs: #TASK-001"

# Link PR to task (in PR description)
# Closes #TASK-001
# Implements ADR-0001
```

## Quick Copy-Paste
```bash
forked build --id smoke --auto-continue && forked guard --overlay overlay/smoke --mode warn
```
