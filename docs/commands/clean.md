# `forked clean`

## Summary
Prunes overlays, worktrees, and conflict artefacts created by other commands. Dry-run mode previews actions; confirmed runs log an audit trail to `.forked/logs/clean.log`.

## Key Flags
- `--overlays <filter>` – age spec (`30d`) or glob (`overlay/tmp-*`); repeatable.
- `--worktrees` – include stale worktree pruning (`git worktree prune` + filesystem checks).
- `--conflicts` – include conflict bundles under `.forked/conflicts/`.
- `--conflicts-age <days>` – retention window for conflict artefacts (default 14).
- `--keep <n>` – preserve the N most recent overlays regardless of filters.
- `--dry-run / --no-dry-run` – preview vs. execute actions (default dry-run).
- `--confirm` – required when executing destructive actions.

## Usage Examples
```bash
# Preview what would be deleted
forked clean --dry-run --overlays 'overlay/tmp-*' --worktrees --conflicts

# Delete old overlays and conflict bundles
forked clean --no-dry-run --confirm --overlays 'overlay/tmp-*' --conflicts --conflicts-age 7

# Remove stale worktrees only
forked clean --no-dry-run --confirm --worktrees --keep 3
```

Executed actions are recorded in `.forked/logs/clean.log` for auditing.

## Related Commands
- [forked build](build.md) – creates overlays and worktrees that may later be pruned.
- [forked sync](sync.md) – produces conflict bundles that `clean` can archive.
