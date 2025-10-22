# Overlay Development Workflow

Build and iterate on a feature stack while keeping your fork aligned with upstream.

## Prerequisites
- Repository initialised with [`forked init`](../commands/init.md)
- `forked.yml` patched with feature definitions and overlays

## Steps
1. **Check status** – `forked status --latest 3` to verify trunk/upstream and recent overlays.
2. **Create slices (optional)** – `forked feature create checkout --slices 2`.
3. **Develop on patch branches** – commit changes on `patch/<feature>/<slice>`.
4. **Rebuild overlay** – `forked build --overlay dev --emit-conflicts-path .forked/conflicts/dev`.
5. **Guard** – `forked guard --overlay overlay/dev --mode block`.
6. **Inspect status JSON** – `forked status --json --latest 3 | jq`.

Repeat steps 3–6 until the feature is ready. Clean up stale overlays with [`forked clean`](../commands/clean.md) when finished.
