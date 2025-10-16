---
title: Release Operations Validation
type: testing
feature: release-operations
date: 2025-09-22
tags: [testing, release]
---

# Validation Checklist

## Pre-Tag Smoke Checklist
1. `make validate` (legacy-handbook) – confirm docs and front matter pass.
2. `forked build --id release-check --auto-continue` – ensure overlay builds without manual cleanup.
3. `forked guard --overlay overlay/release-check --mode block` – verify policy enforcement.
4. `make release-status` – regenerate progress file; confirm updated timestamps.
5. Compare `.forked/report.json` against `tests/fixtures/guard-report-example.json` for schema sanity (`diff -u`).

## Release Readiness Review
- Ensure `releases/v1.0.0/plan.md` success criteria are ticked or updated with rationale.
- Update `releases/v1.0.0.md` highlights and link new ADRs/feature changelog entries.
- Confirm backlog follow-ups (`forked clean`, `status --json`) are captured under `backlog/feature/`.

## Tag & Publish Dry Run
```bash
forked publish --overlay overlay/release-check --tag overlay/release-check --remote origin --push
```
- Expect `tag` and `push` commands to succeed (use dry-run remote or `--push` only on validation branch).
- Verify `git tag -l overlay/release-check` points to overlay branch head.

## Post-Tag Actions
- Append release summary to `releases/CHANGELOG.md`.
- Commit guard artefact checksums or sample JSON to `tests/fixtures/` (future automation).
- Notify stakeholders via project dashboard (`make dashboard`).
