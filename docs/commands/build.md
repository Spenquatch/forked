# `forked build`

## Summary
Cherry-picks the configured patch stack onto `trunk`, producing an overlay branch (`overlay/<id>`) and optional worktree. Logs provenance, selection filters, and per-patch commit summaries to `.forked/logs/forked-build.log`.

## Key Flags
- `--overlay <name>` – name of the overlay profile defined in `forked.yml.overlays`.
- `--features <list>` – comma-separated feature names (bypasses overlay profiles).
- `--include / --exclude <pattern>` – add or remove specific patch branches via glob.
- `--id <overlay-id>` – override the generated overlay branch name.
- `--skip-upstream-equivalents` – skip commits already present on `trunk`.
- `--emit-conflicts / --emit-conflicts-path` – write conflict bundles (schema v2) when cherry-picks stop.
- `--emit-conflict-blobs / --conflict-blobs-dir` – export base/ours/theirs blobs alongside bundles.
- `--on-conflict <stop|bias|exec>` – choose conflict handling mode (`--auto-continue` maps to `bias`).

## Usage Examples
```bash
# Build the dev overlay from forked.yml
forked build --overlay dev

# Build with explicit features and include an extra patch
forked build --features payments,branding --include patch/logging --id dev-plus

# Capture conflict bundles and blobs when cherry-picks fail
forked build --overlay dev \
             --emit-conflicts-path .forked/conflicts/dev \
             --emit-conflict-blobs \
             --on-conflict stop

# Auto-resolve using path bias rules
forked build --overlay dev --auto-continue --on-conflict bias
```

Overlays are safe to discard and rebuild: rerun the command after updating patch branches or `forked.yml`.

## Related Commands
- [forked guard](guard.md) – validates the resulting overlay against sentinels and override policy.
- [forked clean](clean.md) – removes old overlays, worktrees, and conflict bundles.
