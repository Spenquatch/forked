# `forked guard`

## Summary
Evaluates an overlay against the guard configuration in `forked.yml` (sentinel patterns, both-touched files, size caps, override policy). Produces `.forked/report.json` and exits non-zero when policy fails.

## Key Flags
- `--overlay <ref>` – overlay branch or SHA to inspect (required).
- `--mode <warn|block|require-override>` – behaviour when violations are found.
  - `warn` exits 0 but records violations.
  - `block` exits 2 when violations exist.
  - `require-override` requires a valid `Forked-Override` marker (commit trailer, tag, or note).
- `--output <path>` – alternate report location (default `.forked/report.json`).
- `--verbose` – include matched sentinel paths and additional diagnostics in the report.

## Usage Examples
```bash
# Standard policy check (fails on violations)
forked guard --overlay overlay/dev --mode block

# Require an override marker (commit trailer, tag, or note)
forked guard --overlay overlay/dev --mode require-override

# Write report to a custom location with debug details
forked guard --overlay overlay/dev --mode warn --verbose --output reports/dev-guard.json
```

Override search order:
1. Commit trailers on overlay tip (default key `Forked-Override`)
2. Annotated tags pointing at the tip
3. Git notes under `refs/notes/forked/override`

## Related Commands
- [forked status](status.md) – confirms provenance and guard-derived metrics such as `both_touched_count`.
- [forked build](build.md) – supplies the overlay to guard.
