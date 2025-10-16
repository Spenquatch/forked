---
title: Guard CLI Contract - Completion Checklist
type: checklist
date: 2025-09-22
task_id: TASK-002
tags: [checklist, guard-automation]
links: []
---

# Completion Checklist: Guard CLI Contract

## Code Quality
- [ ] `typer.Exit` used consistently for non-zero exits
- [ ] Guard report includes `"report_version": 1`
- [ ] Sentinel logic handles missing overlay + trunk cases correctly
- [ ] Size metrics sourced from `--numstat`

## Testing
- [ ] Guard run in `--mode block` exits with code 2 on violation
- [ ] Guard run in `--mode warn` emits warnings but exit code 0
- [ ] Removing trunk-owned file triggers sentinel violation
- [ ] Overlay-only files do **not** trigger divergence violation

## Documentation
- [ ] README guard section references exit codes + report version
- [ ] Feature status + changelog updated
- [ ] Release plan success criteria updated if completed

## Integration
- [ ] CI workflow leverages editable install and guard command
- [ ] Quick release checklist includes guard step (already documented)
- [ ] No regressions to existing CLI flags

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
