---
title: Feature Resolver & CLI - Command Snippets
type: reference
date: 2025-10-20
task_id: TASK-003
tags: [commands]
links: []
---

# Command Snippets

## Setup & Validation
```bash
# ensure clean state
git status --short

# run unit tests for resolver/cli modules
pytest tests/test_config_features.py tests/test_cli_feature.py -q
```

## Manual Workflow Samples
```bash
# build overlay by profile
forked build --overlay dev --emit-conflicts-path .forked/conflicts/dev.json

# build overlay for ad-hoc feature list with include/exclude
forked build --features payments_v2,branding --exclude 'patch/branding/*'

# build overlay skipping upstream-equivalent commits
forked build --features payments_v2 --skip-upstream-equivalents

# create new feature slices
forked feature create checkout --slices 2

# inspect feature status
forked feature status

# inspect provenance log
tail -n 20 .forked/logs/forked-build.log | jq .
```

## Documentation Updates
```bash
# regenerate handbook validators after editing docs
make validate
```

## Task Wrap-up
```bash
git status
make task-status id=TASK-003 status=review
```
