# Forked Documentation

This directory complements the README with focused references and workflow guides. If you are new to Forked, skim the quick primer below and then dive into the command or workflow that matches your task.

## Primer
1. `forked init` scaffolds `forked.yml` and syncs `trunk` with your upstream remote.
2. `forked build` replays the patch stack as overlays, logging provenance under `.forked/`.
3. `forked guard`, `forked status`, `forked sync`, and `forked clean` keep the overlay healthy and auditable.

## Layout
- `commands/` – one-pagers for each CLI command (flags, exit codes, examples).
- `workflows/` – step-by-step guides for common scenarios (feature development, conflict response, release hygiene).

When in doubt, run `forked --help` or open the matching file in `commands/`. Each workflow guide links back to the command pages for deeper detail.
