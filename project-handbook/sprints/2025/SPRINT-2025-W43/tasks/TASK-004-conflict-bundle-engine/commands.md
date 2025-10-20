---
title: Conflict Bundle Engine - Command Snippets
type: reference
date: 2025-10-20
task_id: TASK-004
tags: [commands]
links: []
---

# Command Snippets

## Force Conflict Scenario
```bash
# create conflicting changes
git checkout trunk
echo "upstream change" >> src/example.py
git commit -am "upstream change"

git checkout patch/example/01-slice
echo "feature change" >> src/example.py
git commit -am "feature change"

# run build with conflict bundle
forked build --features example \
  --emit-conflicts .forked/conflicts/example-1.json \
  --conflict-blobs-dir .forked/conflicts/example/blobs \
  --on-conflict stop || echo "expected conflict"
```

## Inspect Bundle
```bash
jq '.schema_version, .wave, .files[0].binary, .files[0].blobs_dir, .resume' .forked/conflicts/example-1.json
ls .forked/conflicts/example/blobs/
```

## Sync Conflict Test
```bash
# default stop-on-conflict
forked sync --emit-conflicts .forked/conflicts/sync-1.json --on-conflict stop || echo $?

# auto-continue bias path
forked sync --emit-conflicts .forked/conflicts/sync-continue.json --auto-continue --on-conflict bias || echo $?
```

## Exec Hook Example
```bash
forked build --emit-conflicts .forked/conflicts/auto.json \
  --on-conflict exec "./scripts/auto-resolve-conflict.sh"
```

## Cleanup
```bash
git rebase --abort || true
git cherry-pick --abort || true
rm -rf .forked/conflicts
```
