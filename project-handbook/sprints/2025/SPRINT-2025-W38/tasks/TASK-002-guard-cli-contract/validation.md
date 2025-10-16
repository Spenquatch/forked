---
title: Guard CLI Contract - Validation Guide
type: validation
date: 2025-09-22
task_id: TASK-002
tags: [validation]
links: []
---

# Validation Guide: Guard CLI Contract

## Automated Validation
```bash
# Run guard in block mode (should exit 2 with violations)
forked guard --overlay overlay/test --mode block || true

# Run guard in warn mode (should exit 0 but surface warnings)
forked guard --overlay overlay/test --mode warn

# Optional: run make validate to ensure no doc/schema drift
make validate

# Check sprint health (optional)
make sprint-status
```

## Manual Validation Steps

### Behavioural Checks
1. **Exit Codes**
   - [ ] `--mode block` returns exit 2 when violations present
   - [ ] `--mode warn` returns exit 0 while listing violations
2. **Sentinels**
   - [ ] Overlay-only file passes `must_diverge_from_upstream`
   - [ ] Missing overlay file triggers `must_diverge_from_upstream` violation
   - [ ] Deleted trunk file triggers `must_match_upstream` violation
3. **Size Caps**
   - [ ] `--numstat`-based metrics produce correct file/loc totals

### Documentation Validation
- [ ] README guard section matches actual behaviour
- [ ] Feature status + changelog updated
- [ ] Release plan success criteria ticked if applicable

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
