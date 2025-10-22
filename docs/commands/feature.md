# `forked feature`

## Summary
Manages feature slices—groupings of patch branches that map to logical workstreams. The subcommands help you scaffold new patches, inspect ahead/behind status, and remove unused slices.

## Subcommands
- `forked feature status` – shows each feature with per-slice ahead/behind counts relative to `trunk`.
- `forked feature create <name> --slices N` – creates N numbered patch branches (`patch/<name>/01`, etc.) and updates `forked.yml`.
- `forked feature remove <name>` – removes feature metadata (patch branches are left intact).

## Usage Examples
```bash
# Inspect all feature slices
forked feature status

# Create a two-slice feature skeleton
forked feature create onboarding --slices 2

# Remove feature metadata after merging upstream
forked feature remove onboarding
```

Feature definitions in `forked.yml` feed directly into [forked build](build.md) via overlays or the `--features` flag.

## Related Commands
- [forked build](build.md) – consumes feature definitions when constructing overlays.
- [forked status](status.md) – displays active feature provenance in JSON output.
