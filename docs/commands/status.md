# `forked status`

## Summary
Summarises the fork at a glance: upstream/trunk SHAs, per-patch ahead/behind counts, and recent overlays with provenance metadata. The `--json` flag produces a machine-readable payload for dashboards and automation.

## Key Flags
- `--latest <n>` – number of overlay branches to list (default 5).
- `--json` – emit structured JSON (including provenance, guard counts, build status).

## Usage Examples
```bash
# Human-friendly summary
forked status --latest 3

# JSON for dashboards / CI artifacts
forked status --json --latest 10 | jq
```

If provenance logs or notes are missing, the command recomputes selections using the resolver and emits a warning. Guard runs populate `both_touched_count` when a recent `.forked/report.json` references the overlay.

## Related Commands
- [forked build](build.md) – records provenance consumed by status.
- [forked guard](guard.md) – feeds guard metrics into the status JSON payload.
