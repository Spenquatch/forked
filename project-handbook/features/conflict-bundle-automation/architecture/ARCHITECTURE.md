---
title: Conflict Bundle Automation Architecture
type: architecture
feature: conflict-bundle-automation
date: 2025-10-20
tags: [architecture, automation]
---

# Conflict Bundle Automation Architecture

## Conflict Detection Pipeline
1. Capture conflicts via `git status --porcelain=v2` and `git ls-files -u` once cherry-pick/rebase halts.
2. For each staged path:
   - Read index stages (base/ours/theirs) using `git show :1:path` etc.
   - Record blob OIDs and optionally dump file contents to blobs directory.
   - Generate diffs using `git diff --base path`, `--ours`, `--theirs`.
3. Gather contextual metadata from the active operation (build overlay id / sync patch branch).

## Bundle Schema
- `schema_version`: integer for compatibility checks.
- `context`: mode, overlay, trunk, upstream, patch branch, commit, merge base, feature.
- `files[]`: entries containing path, slice, precedence, blob refs, diff snippets, optional blob dir.
- `resume`: command hints for continue/abort/rebuild.
- Stored at `.forked/conflicts/<overlay-id>.json` by default.

## Precedence Calculation
- Reuse guard rules to compute recommended resolution:
  - Evaluate sentinel matches (global + feature-level) → highest priority.
  - Evaluate path bias fallback.
  - Default to `"none"` if no rule applies.
- Provide textual rationale for transparency.

## Exit & Hook Strategy
- Default `--on-conflict stop` writes bundle then exits `10`.
- `--on-conflict bias` (future) applies recommendation (ours/theirs) automatically.
- `--on-conflict exec <cmd>` runs user script with JSON path exported via env var.
- Build and sync share the same configuration/argument parser to avoid drift.

## Observability
- Log bundle path and blob dir when emitted.
- Optional `--emit-conflicts -` may pipe JSON to stdout in later iteration (tracked separately).
- README + CI snippets illustrate artifact upload and exit code handling.
