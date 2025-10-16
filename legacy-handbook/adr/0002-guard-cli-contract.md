---
id: ADR-0002
title: Guard CLI Contract
type: adr
status: accepted
date: 2025-09-22
supersedes: null
superseded_by: null
tags: [guards, cli]
links: [../features/guard-automation/overview.md]
---

## Context
`forked guard` evaluates overlay risk policies. The initial implementation returned plain `SystemExit` errors, parsed `--shortstat`, and treated overlay-only files as violations. Release v0.1.0 requires deterministic exit codes for CI, locale-safe metrics, and clear sentinel behaviour.

## Decision
- Use `typer.Exit(code)` for all guard termination paths: `0` (pass), `2` (policy violation), `4` (config/dirty tree errors).
- Include `"report_version": 1` in emitted JSON artifacts for forward compatibility.
- Evaluate sentinels against the union of trunk + overlay trees and treat overlay-only paths as valid divergence.
- Compute size metrics via `git diff --numstat` and treat `-` (binary) entries as changes.

## Consequences
**Positive**
- CI pipelines can rely on documented exit codes.
- Sentinel logic catches missing overlay files while allowing overlay-only additions.
- Size metrics are locale-independent and ready for future automation.

**Negative**
- Slightly more diff parsing work in Python (`--numstat`).
- Requires future maintenance if JSON schema evolves (tracked by report_version).

## Rollout & Reversibility
- Shipped in Forked CLI v0.1.0 along with README updates.
- Quick smoke checklist exercises guard steps before every release tag.
- To revert, restore prior sentinel logic and update README/feature docs accordingly.
