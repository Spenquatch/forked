# Conflict Response Workflow

Capture, analyse, and resolve conflicts generated during builds or syncs.

## Prerequisites
- Recent run of [`forked build`](../commands/build.md) or [`forked sync`](../commands/sync.md) with `--emit-conflicts-path`
- `.forked/conflicts/` populated with JSON bundles (schema v2)

## Steps
1. **Inspect bundle**  
   ```bash
   jq '.context, .files[].precedence' .forked/conflicts/<id>.json
   ```
   Note recommended resolutions (`ours` | `theirs`) and resume commands.

2. **Optionally review blobs** (if `--emit-conflict-blobs` was used) under `.forked/conflicts/<id>/`.

3. **Resolve manually or delegate**  
   - Manual: apply edits in the worktree suggested by the bundle.  
   - Automated: rerun with `--on-conflict exec --on-conflict-exec "<tool> {json}"`.

4. **Resume the operation**  
   ```bash
   git cherry-pick --continue      # from build bundle resume block
   # or
   git rebase --continue           # from sync bundle resume block
   ```

5. **Re-run guard/status**  
   ```bash
   forked guard --overlay overlay/<id> --mode block
   forked status --json --latest 1 | jq
   ```

6. **Archive or delete bundles** with [`forked clean`](../commands/clean.md) once resolved.
