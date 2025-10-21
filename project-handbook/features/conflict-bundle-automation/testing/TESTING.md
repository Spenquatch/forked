---
title: Conflict Bundle Automation Testing Guide
type: testing
feature: conflict-bundle-automation
date: 2025-10-20
tags: [testing, automation]
---

# Testing Guide

## Build Conflict Scenario
1. Create divergence between `trunk` and `patch/example/01-slice`.
2. Run:
   ```bash
   forked build --features example --emit-conflicts-path .forked/conflicts/example-1.json --emit-conflict-blobs --conflict-blobs-dir .forked/conflicts/example/blobs --on-conflict stop
   echo $?
   ```
3. Confirm exit code `10`.
4. Inspect JSON:
   ```bash
   jq '.schema_version, .wave, .files[0].binary, .resume' .forked/conflicts/example-1.json
   ```
5. Validate blob directory contains `base.txt`, `ours.txt`, `theirs.txt` when `--conflict-blobs-dir` is provided and for binary/large files.

## Sync Conflict Scenario
1. Introduce upstream change that conflicts with `patch/example/02-slice`.
2. Run:
   ```bash
   forked sync --emit-conflicts-path .forked/conflicts/sync-1.json --on-conflict stop
   ```
3. Ensure rebase halts with exit `10` and JSON references the offending patch commit.
4. Re-run with auto-continue:
   ```bash
   forked sync --emit-conflicts-path .forked/conflicts/sync-continue.json --auto-continue --on-conflict bias
   ```
   Confirm bias actions logged and additional wave bundle created if a second conflict occurs.
5. Follow `resume.continue` to verify the instructions succeed post-resolution.

## Exec Hook
1. Provide a simple script:
   ```bash
   forked build --features example --emit-conflicts-path .forked/conflicts/auto.json \
     --on-conflict exec './scripts/auto-resolve.sh'
   ```
2. Ensure CLI propagates script exit status and logs the handoff.

## Schema Regression
- Add unit tests that diff emitted JSON against stored fixture using `jsonschema` or custom validator (schema v2).
- Validate recommended resolution matches sentinel/path bias inputs and that binary entries set `diffs.* = null` while writing blobs.

## CI Fit Check
- Run sample GitHub Action from docs; ensure step fails on exit 10 and uploads bundle artifact.
