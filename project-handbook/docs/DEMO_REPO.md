---
title: Demo Repository Guide
type: docs
date: 2025-09-22
tags: [demo, handbook]
---

# Demo Repository Guide

Use `./scripts/setup-demo-repo.sh` to create a lightweight fork that exercises worktree reuse, sentinel policies, and guard reporting without heavy history.

```bash
./scripts/setup-demo-repo.sh demo-forked
cd demo-forked
```

The script provisions:
- Bare upstream (`demo-forked-upstream.git`) and origin (`demo-forked-origin.git`)
- `trunk` containing `api/contracts/v1.yaml` and `src/service.py`
- Patch branches `patch/contract-update` (contract delta) and `patch/service-logging` (two-commit stack)
- Sentinel ownership patterns (`config/forked/**` as ours, `branding/**` as theirs)

This repo has fewer than a dozen files, keeping smoke checklists fast while triggering the key workflows.

## Guard Report Fixture
After running the smoke checklist, regenerate the fixture if behaviour changes:
```bash
forked guard --overlay overlay/smoke --mode block --output .forked/report.json || true
cp .forked/report.json project-handbook/tests/fixtures/guard-report-example.json
```

Commit the updated fixture alongside any guard logic changes so future contributors can diff against a known baseline.
