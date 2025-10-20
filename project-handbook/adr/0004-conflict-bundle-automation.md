---
id: ADR-0004
title: Conflict Bundle Automation
type: adr
status: accepted
date: 2025-10-20
supersedes: null
superseded_by: null
tags: [conflicts, automation, ci]
links: [../features/conflict-bundle-automation/overview.md]
---

## Context
`forked build` and `forked sync` currently halt on merge conflicts without structured guidance, forcing developers or CI to inspect Git state manually. We need deterministic artefacts and exit codes so humans and automation can resolve conflicts quickly, upload context, or trigger additional tooling.

## Decision
- Introduce a shared conflict collector that, on cherry-pick/rebase halt, records blob OIDs, unified diffs, sentinel/path-bias recommendations, and resume commands in a JSON “conflict bundle” (schema versioned).
- Add `--emit-conflicts`, `--conflict-blobs-dir`, `--on-conflict <mode>`, and `--on-conflict-exec` flags to `forked build` and `forked sync`.
- Emit exit code `10` when conflicts are captured (unless a custom exec hook overrides it) so CI can branch logic cleanly.
- Optionally export base/ours/theirs blobs per conflicted path for downstream tools.
- Document the schema, usage patterns, and CI integration in README + release notes.

## Consequences
**Positive**
- Developers and bots receive machine-readable conflict details and recommended actions.
- CI pipelines can detect conflicts reliably and attach bundles as artefacts.
- Shared collector keeps build and sync behaviour consistent.

**Negative**
- Additional JSON/blobs increase artefact storage; users must opt-in to blob export.
- Exit code changes require coordination with existing scripts (migration note provided).

## Rollout & Reversibility
- Targeted for release v1.1.0.
- Default behaviour remains “stop on conflict” unless flags supplied, minimizing disruption.
- Reversal path: disable flags and collector module (retaining legacy stdout messages) if unforeseen issues arise.
