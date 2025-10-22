# Release Hygiene Workflow

Use Forked to produce clean overlays, guard reports, and audit logs before tagging a release.

## Prerequisites
- All feature branches merged into the overlay you intend to ship
- CI/automation expecting `.forked/report.json` and/or status JSON artefacts

## Steps
1. **Sync with upstream** – `forked sync --emit-conflicts --on-conflict stop` and resolve any conflicts.
2. **Rebuild overlay** – `forked build --overlay release --emit-conflicts-path .forked/conflicts/release`.
3. **Guard in require-override mode** (if policy demands):
   ```bash
   forked guard --overlay overlay/release --mode require-override --verbose
   ```
4. **Capture status JSON** for dashboards:
   ```bash
   forked status --json --latest 1 > reports/status-release.json
   ```
5. **Archive artefacts** – attach `reports/status-release.json` and `.forked/report.json` to your release notes or CI logs.
6. **Clean stale resources** – `forked clean --no-dry-run --confirm --overlays 'overlay/release-*' --keep 1`.
7. **Tag & publish** – bump the version, push the release tag, and let CI publish to PyPI.

Refer to the [publishing section in the README](../../README.md#publishing-to-pypi) once validation passes.
