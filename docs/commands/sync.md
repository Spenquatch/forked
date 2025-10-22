# `forked sync`

## Summary
Fetches upstream, fast-forwards `trunk`, and rebases each patch branch in `forked.yml.patches.order` onto the updated base. Captures conflict bundles (schema v2) and resume instructions when a rebase halts.

## Key Flags
- `--emit-conflicts / --emit-conflicts-path` – write conflict bundle JSON per rebased patch.
- `--emit-conflict-blobs / --conflict-blobs-dir` – export base/ours/theirs blobs for each conflicted file.
- `--on-conflict <stop|bias|exec>` – choose how to handle conflicts; `stop` exits 10, `bias` applies path bias rules, `exec` runs a custom command.
- `--on-conflict-exec <command>` – command to execute in `exec` mode (use `{json}` placeholder for bundle path).
- `--auto-continue` – alias for `--on-conflict bias`.

## Usage Examples
```bash
# Standard rebase with conflict bundles
forked sync --emit-conflicts-path .forked/conflicts/sync --on-conflict stop

# Auto-resolve using bias rules when possible
forked sync --emit-conflicts --on-conflict bias --auto-continue

# Delegate conflicts to an external tool
forked sync --emit-conflicts-path .forked/conflicts/sync-exec \
            --on-conflict exec \
            --on-conflict-exec "./scripts/resolve-sync.sh {json}"
```

Each run logs telemetry to `.forked/logs/forked-build.log` with `event: "forked.sync"`, including per-branch results, wave numbers, and exec exit codes.

## Related Commands
- [forked build](build.md) – rebuilds overlays after patches are rebased.
- [forked clean](clean.md) – removes old conflicts/worktrees after sync completes.
