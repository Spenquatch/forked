---
title: Guard Automation Status
type: status
feature: guard-automation
date: 2025-09-22
tags: [status]
---

# Status: Guard Automation

## Summary
Guard CLI changes are merged (exit codes, report versioning, sentinel fixes). Remaining work is capturing a golden report and validating CI wiring.

## Milestones
- [ ] Replace `SystemExit` with `typer.Exit` return codes
- [ ] Add `"report_version": 1` to guard output
- [ ] Fix `must_diverge_from_upstream` missing-file logic
- [ ] Switch diff sizing to `--numstat`
- [ ] Capture reference JSON output committing to repo

## Metrics
- Policy coverage: 100% of documented guard checks
- CI readiness: pending pipeline dry run

## Next Steps
1. Produce golden guard report for sample repo (`.forked/report.json`).
2. Dry-run GitHub Action guard step with editable install.
3. File follow-up backlog item for guard JSON fixture testing.
