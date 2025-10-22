# `forked init`

## Summary
Initialises a repository for Forked by fast-forwarding `trunk` to upstream, scaffolding `forked.yml`, and creating the `.forked/` workspace for logs, overlays, and guard artefacts.

## Key Flags
- `--upstream-remote <name>` – remote alias that tracks the canonical project (default `upstream`).
- `--upstream-branch <branch>` – branch from the upstream remote to mirror into `trunk` (default `main`).

## Typical Flow
```bash
git clone git@github.com:you/your-fork.git
cd your-fork
git remote add upstream git@github.com:canonical/project.git

forked init --upstream-remote upstream --upstream-branch main
```

After running, review `forked.yml` and commit it to your fork so teammates inherit the same configuration.

## Related Commands
- [forked build](build.md) – replays the patch stack defined in `forked.yml`.
- [forked status](status.md) – verifies upstream vs. trunk and overlay provenance.
