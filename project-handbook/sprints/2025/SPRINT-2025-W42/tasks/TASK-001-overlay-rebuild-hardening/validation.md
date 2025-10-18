---
title: Overlay Rebuild Hardening - Validation Guide
type: validation
date: 2025-09-22
task_id: TASK-001
tags: [validation]
links: []
---

# Validation Guide: Overlay Rebuild Hardening

## Automated Validation
```bash
# Run smoke build twice to ensure reuse
forked build --id smoke --auto-continue
forked build --id smoke --auto-continue

# Verify guard behaviour
forked guard --overlay overlay/smoke --mode warn

# Optional: run existing make validators
make validate
```

## Manual Validation Steps

### Build Behaviour
1. **Worktree Location**
- [ ] After first build, worktree lives at `.forked/worktrees/smoke`
   - [ ] After second build, same path reused (no duplicate directories)
2. **Cleanliness**
   - [ ] `git status` inside reused worktree reports clean before cherry-picks
   - [ ] No leftover conflict markers after auto-continue path bias

### Edge Cases
- [ ] Remove `.forked/worktrees/smoke` and rebuild to ensure suffixing works
- [ ] Set `FORKED_WORKTREES_DIR` to an absolute path and confirm relocation still works
- [ ] Run with `--no-worktree` to ensure fallback behaviour unchanged

### Documentation Validation
- [ ] README quick smoke checklist remains accurate
- [ ] Feature status/changelog updated with results
- [ ] Release plan success criteria updated if completed

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
