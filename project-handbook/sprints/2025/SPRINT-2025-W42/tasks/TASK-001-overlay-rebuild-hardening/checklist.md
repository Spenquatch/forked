---
title: Overlay Rebuild Hardening - Completion Checklist
type: checklist
date: 2025-09-22
task_id: TASK-001
tags: [checklist, overlay-infrastructure]
links: []
---

# Completion Checklist: Overlay Rebuild Hardening

## Code Quality
- [ ] `_resolve_worktree_dir` relocates/suffixes directories deterministically
- [ ] `worktree_for_branch` handles prune + reuse paths safely
- [ ] Cherry-pick loop handles empty ranges and errors gracefully
- [ ] No regressions to `--no-worktree` mode

## Testing
- [ ] `forked build --id smoke --auto-continue` succeeds twice without manual cleanup
- [ ] Resulting worktree path sits under `.forked/worktrees/smoke`
- [ ] Guard run after rebuild exits with documented codes
- [ ] Edge cases: missing `$FORKED_WORKTREES_DIR`, existing directory suffixing

## Documentation
- [ ] README retains accurate description of worktree behaviour
- [ ] Feature status/changelog updated
- [ ] Release plan updated with milestone completion

## Integration
- [ ] `git worktree list` shows reused entry after second build
- [ ] CI workflow smoke commands updated if necessary
- [ ] No breaking change to CLI flags

## Sprint Integration
- [ ] Task status updated in task.yaml
- [ ] Daily status includes this task progress
- [ ] Any blockers documented and escalated
- [ ] Sprint burndown reflects progress

## Feature Integration
- [ ] Feature status.md updated if needed
- [ ] Feature stage advanced if this completes feature
- [ ] Cross-feature dependencies considered
- [ ] Changelog entry added (if significant)

## Review Readiness
- [ ] All acceptance criteria met (see task.yaml)
- [ ] Self-review completed
- [ ] Ready for peer review
- [ ] Task marked as "review" status

## Completion
- [ ] Peer review approved
- [ ] All checklist items verified
- [ ] Task status set to "done"
- [ ] Sprint metrics updated
