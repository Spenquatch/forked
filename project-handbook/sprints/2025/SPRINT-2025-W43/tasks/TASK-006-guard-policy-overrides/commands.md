---
title: Guard Policy Overrides - Command Snippets
type: reference
date: 2025-10-20
task_id: TASK-006
tags: [commands]
links: []
---

# Command Snippets

## Create Override Commit Trailer
```bash
git checkout overlay/dev
git commit --allow-empty -m $'temporary override commit\n\nForked-Override: sentinel'
```

## Guard Runs
```bash
# Require override (should fail without trailer)
forked guard --overlay overlay/dev --mode require-override || echo "expected failure"

# After adding trailer
forked guard --overlay overlay/dev --mode require-override
jq '.override, .features' .forked/report.json
```

## Tag & Notes Overrides
```bash
# Annotated tag override
FORKED_OVERRIDE="Forked-Override: all"
git tag -a override-tag -m "$FORKED_OVERRIDE"
forked publish --tag override-tag --dry-run

# Git note override
cat <<'NOTE' | git notes --ref=refs/notes/forked/override add -F - HEAD
Forked-Override: size
NOTE
```

## Tests
```bash
pytest tests/test_guard_overrides.py -q
pytest tests/test_report_v2.py -q
```
