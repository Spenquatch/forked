# Forked

Forked keeps long-lived forks healthy. It lets you:

- Track upstream with a clean `trunk`
- Rebuild feature stacks as disposable overlays
- Capture guard reports and conflict bundles for automation
- Clean up worktrees, conflict artefacts, and stale overlays safely

This document focuses on getting you productive quickly with the published PyPI package.

---

## Installation

```bash
pip install forked
# or, in an isolated environment
pipx install forked
```

Requirements:
- Git ≥ 2.31 (2.38 enables `zdiff3` conflict style)
- Python ≥ 3.10

You can still work on the CLI locally via:
```bash
python -m pip install -e .
```

---

## First-Time Setup

1. **Clone your fork** and add the upstream remote.
2. **Run `forked init`:**
   ```bash
   forked init --upstream-remote upstream --upstream-branch main
   ```
   This creates `trunk`, scaffolds `forked.yml`, and sets up `.forked/` for logs, overlays, and guard artefacts.
3. **Describe your stack** in `forked.yml`:
   - `patches.order` lists the topic branches in the sequence you want them cherry-picked.
   - `features` group related patches so you can turn whole slices on/off with a flag.
   - `overlays` map a friendly name (e.g., `dev`) to the feature set that should be built.

   ```yaml
   patches:
     order:
       - patch/payments/01
       - patch/payments/02
   features:
     payments:
       patches:
         - patch/payments/01
         - patch/payments/02
   overlays:
     dev:
       features: [payments]
   ```
   With this config, `forked build --overlay dev` applies the two payment patches, and you can layer in more feature blocks or custom overlays as your fork grows.

---

## Core Workflow

| Step | Command | What it does |
|------|---------|--------------|
| Build overlay | `forked build --overlay dev` | Applies ordered patches on `trunk`, logs selections, optionally emits conflict bundles (`--emit-conflicts-path`). |
| Guard overlay | `forked guard --overlay overlay/dev --mode block` | Runs sentinel checks, produces `.forked/report.json`, returns non-zero if policy fails. |
| Status summary | `forked status --json --latest 5` | Prints upstream/trunk SHAs, per-patch ahead/behind, overlay provenance (with fallback warnings). |
| Sync patches | `forked sync --emit-conflicts-path .forked/conflicts/sync --on-conflict stop` | Rebases patch branches onto latest upstream, capturing conflicts with resume instructions. |
| Clean artefacts | `forked clean --dry-run --overlays 'overlay/tmp-*' --worktrees --conflicts` | Plans or executes cleanup of old overlays/worktrees/conflict bundles. |

Additional helpers:
- `forked feature create checkout --slices 2` – scaffold feature slices
- `forked feature status` – show ahead/behind per feature slice
- `forked build --auto-continue --on-conflict bias` – auto-resolve with path bias rules

---

## Example Session

```bash
# 1. Initialise and configure
forked init
editor forked.yml   # add patch order, features, sentinels

# 2. Build overlay with provenance logs
forked build --overlay dev --emit-conflicts-path .forked/conflicts/dev

# 3. Guard the overlay (fails if sentinels trigger)
forked guard --overlay overlay/dev --mode block

# 4. Resolve override requirements if needed
git -C .forked/worktrees/dev commit --allow-empty -m $'override\n\nForked-Override: sentinel'
forked guard --overlay overlay/dev --mode require-override

# 5. Inspect status JSON for dashboards
forked status --json --latest 3 | jq

# 6. Sync patch stack against upstream
forked sync --emit-conflicts-path .forked/conflicts/sync --on-conflict stop

# 7. Tidy stale overlays/worktrees
forked clean --no-dry-run --confirm --overlays 'overlay/tmp-*' --worktrees
```

All JSON logs live under `.forked/logs/`. Conflict bundles (schema v2) include wave numbering, blob references, and resume commands for automation.

---

## Learning More

- `sanity_check.md` – guided walkthrough covering all commands
- `docs/` – command reference and workflow guides
- `tests/` – Pytest scenarios demonstrating guard overrides, conflict bundles, status provenance, etc.

Need help? File an issue, browse the docs in [`docs/`](docs/), or start with the demo script:
```bash
./scripts/setup-demo-repo.sh demo-forked
```

## Repository Layout

```
.
├── src/                       # CLI source modules (typer-based)
├── docs/                      # command reference and workflow guides
├── pyproject.toml             # packaging metadata for editable install
├── scripts/setup-demo-repo.sh # helper to create a sandbox repo with patch branches
└── README.md                  # this document
```

Run-time artifacts are intentionally kept out of Git:

```
.forked/                       # logs, guard reports, and overlay worktrees
```

The directory is gitignored by default.

---

## Installation

You can install the CLI in editable mode while iterating locally:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Once published, the recommended user path will be:

```bash
pipx install forked
```

The CLI requires:

- Git ≥ 2.31 (Git ≥ 2.38 unlocks the `zdiff3` conflict style automatically)
- Python ≥ 3.10

---

## Quick Start

```bash
# optional: create a sandbox fork with patch branches
./scripts/setup-demo-repo.sh demo-forked
cd demo-forked

# 1. Initialize Forked CLI in the repo
forked init

# 2. Configure patch order and optional sentinels in forked.yml
sed -i 's/order: \[\]/order:\n  - patch\/contract-update\n  - patch\/service-logging/' forked.yml

# 3. Build an overlay (creates overlay/<id> + optional worktree)
forked build --id smoke --auto-continue

# 4. Guard the overlay (generates .forked/report.json)
forked guard --overlay overlay/smoke --mode block

# 5. Sync trunk & rebase patch branches against upstream
forked sync
```

## Feature-Sliced Overlays

1. **Define features and overlays** in `forked.yml` using the new `features` and `overlays` sections. Each feature lists the patch branches (slices) that compose it, and overlays map profile names to feature sets. Example:

   ```yaml
   features:
     payments_v2:
       patches:
         - patch/payments_v2/01-schema
         - patch/payments_v2/02-api
   overlays:
     dev:
       features: [payments_v2, branding]
   ```

2. **Scaffold feature slices** with the CLI:

   ```bash
   forked feature create payments_v2 --slices 3
   forked feature status         # shows ahead/behind vs trunk
   ```

3. **Build overlays by profile or feature lists**:

   ```bash
   # Profile-driven build (overlay/dev)
   forked build --overlay dev --skip-upstream-equivalents

   # Ad-hoc feature combination with include/exclude globs
   forked build --features payments_v2,branding \
     --include patch/branding/experimental \
     --exclude patch/branding/old
   ```

   The resolver preserves global patch order, surfaces unmatched patterns, and logs provenance (features, patches, and filters) to `.forked/logs/forked-build.log` and optional git notes on the overlay tip.

4. **Optimize repeat builds** with `--skip-upstream-equivalents` (filters commits that already exist on trunk via `git cherry`).

5. **Automate overlays safely** using the new selection metadata in git notes and build logs—these record the active feature set so guard/status tooling and downstream bots can reason about provenance.

The key artifacts after a build/guard cycle:

- `.forked/worktrees/<id>/` – the reuseable overlay worktree.
- `.forked/logs/forked-build.log` – append-only JSON telemetry describing each build.
- `.forked/report.json` – deterministic guard report used by CI and local review.

---

## Configuration (`forked.yml`)

`forked.yml` is committed to your repository and controls upstream, patch ordering, guards, and worktree behavior.

```yaml
version: 1
upstream:
  remote: upstream
  branch: main
branches:
  trunk: trunk
  overlay_prefix: overlay/
patches:
  order:
    - patch/contract-update
    - patch/service-logging
features:
  contract_update:
    patches:
      - patch/contract-update
    sentinels:
      must_match_upstream:
        - api/contracts/**
  service_logging:
    patches:
      - patch/service-logging
overlays:
  dev:
    features: [contract_update, service_logging]
guards:
  mode: warn                # warn | block | require-override
  both_touched: true
  sentinels:
    must_match_upstream:
      - api/contracts/**
    must_diverge_from_upstream:
      - branding/**
  size_caps:
    max_loc: 0               # 0 disables the cap
    max_files: 0
path_bias:
  ours:
    - config/forked/**
  theirs:
    - vendor/**
worktree:
  enabled: true
  root: ".forked/worktrees"  # relative paths live under <repo>/.forked/worktrees/<id>
policy_overrides:
  require_trailer: false
  trailer_key: "Forked-Override"
```

Key behaviors:

- Relative `worktree.root` paths are relocated outside the Git repo to avoid nested worktrees.
- Setting `$FORKED_WORKTREES_DIR` overrides the root path. On POSIX platforms, the CLI rejects Windows-style roots (`C:\…`) to prevent confusion.
- Sentinel sections determine whether specific paths must match or must diverge from upstream in the final overlay.

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| [`forked init`](#forked-init) | Verify upstream remote, fast-forward `trunk`, scaffold config. |
| [`forked sync`](#forked-sync) | Fast-forward `trunk` to upstream and rebase every patch branch. |
| [`forked build`](#forked-build) | Rebuild an overlay branch (and optional worktree) from trunk + patches. |
| [`forked guard`](#forked-guard) | Evaluate policies against an overlay and write a JSON report. |
| [`forked status`](#forked-status) | Show trunk, patches, and the most recent overlays. |
| [`forked feature create`](#forked-feature-create) | Scaffold numbered patch slices for a feature. |
| [`forked feature status`](#forked-feature-status) | Display ahead/behind state for feature slices. |
| [`forked publish`](#forked-publish) | Tag and/or push an overlay branch. |

### `forked init`

```bash
forked init [--upstream-remote REMOTE] [--upstream-branch BRANCH]
```

Performs safety checks (clean working tree, remote exists), fetches from upstream, creates/updates the `trunk` branch, enables helpful Git settings (`rerere`, conflict style), and writes `forked.yml` if missing. On Git < 2.38 the CLI automatically falls back to `diff3` conflict style with a short notice.

### `forked sync`

```bash
forked sync
```

Fetches upstream, resets `trunk` to `upstream/<branch>`, then iterates through each patch listed in `forked.yml.patches.order` and rebases it onto trunk. If a rebase stops on conflicts, the command exits with code `4` and prints the branch to fix.

### `forked build`

```bash
forked build [--overlay PROFILE | --features NAME[,NAME...]] [--include PATTERN]...
             [--exclude PATTERN]... [--id ID] [--skip-upstream-equivalents]
             [--emit-conflicts] [--emit-conflicts-path PATH]
             [--emit-conflict-blobs] [--conflict-blobs-dir DIR]
             [--on-conflict MODE] [--on-conflict-exec COMMAND]
             [--no-worktree] [--auto-continue] [--git-note/--no-git-note]
```

- `--overlay PROFILE` – select features defined in `forked.yml.overlays.<profile>.features`. When omitted, all patches in `patches.order` are applied. If `--id` is not provided, the profile name becomes the overlay id.
- `--features NAME[,NAME...]` – comma-separated list of feature keys to include. Mutually exclusive with `--overlay`.
- `--include` / `--exclude` – add or remove patch branches via exact names or glob patterns (applied after feature/overlay resolution).
- `--skip-upstream-equivalents` – skip cherry-picking commits already present on trunk (based on `git cherry -v`) and log the skipped counts per patch.
- `--id` – overlay identifier (default: overlay profile name or current date `YYYY-MM-DD`).
- `--no-worktree` – build directly in the current working tree instead of creating/reusing a worktree.
- `--emit-conflicts` – write a conflict bundle (`schema_version: 2`) when a cherry-pick halts, storing it at the default path `.forked/conflicts/<id>-<wave>.json`.
- `--emit-conflicts-path PATH` – write the conflict bundle to a custom location instead of the default path.
- `--emit-conflict-blobs` – export base/ours/theirs blobs for each conflicted path alongside the bundle (binary/large files always trigger blob export).
- `--conflict-blobs-dir DIR` – store exported blobs under a custom directory when `--emit-conflict-blobs` is used.
- `--on-conflict MODE` – conflict policy: `stop` (default, exit code 10), `bias` (apply recommended ours/theirs resolutions and continue), or `exec` (run an external command).
- `--on-conflict-exec COMMAND` – shell command invoked when `--on-conflict exec` is selected (use `{json}` as a placeholder for the bundle path).
- `--auto-continue` – legacy alias for `--on-conflict bias`.
- `--git-note/--no-git-note` – opt in/out of writing provenance notes to `refs/notes/forked-meta`.

Behavior highlights:

- Worktree directories are reused between builds. If a stale directory blocks reuse, the CLI suffixes the path (e.g., `test-1`) and prints a reminder to run `git worktree prune`.
- Build summaries now display applied versus skipped commits (`--skip-upstream-equivalents`) and record the active feature set in `.forked/logs/forked-build.log` alongside resolver inputs.
- Conflict bundles capture multi-wave context, recommended resolutions, and blob locations. They are logged to `.forked/logs/forked-build.log` alongside exit metadata (status `conflict` for stop/exec, `success` when bias resolves conflicts).
- Optional git notes capture the selected features/patches to make overlay provenance discoverable with `git notes show`.

### `forked sync`

```bash
forked sync [--emit-conflicts] [--emit-conflicts-path PATH]
            [--emit-conflict-blobs] [--conflict-blobs-dir DIR]
            [--on-conflict MODE] [--on-conflict-exec COMMAND]
            [--auto-continue]
```

- `--emit-conflicts` – emit a rebase conflict bundle when a patch fails to rebase, storing it at the default path `.forked/conflicts/sync-<branch>-<wave>.json`.
- `--emit-conflicts-path PATH` – place the sync conflict bundle at a custom location.
- `--emit-conflict-blobs` – export base/ours/theirs blobs for each conflicted file alongside the bundle.
- `--conflict-blobs-dir DIR` – store exported blobs under a custom directory when `--emit-conflict-blobs` is used.
- `--on-conflict MODE` – `stop` (default, exit code `10`), `bias` (apply recommended resolutions and continue the rebase), or `exec` (delegate to an external command).
- `--on-conflict-exec COMMAND` – command executed when `--on-conflict exec` is selected; `{json}` is replaced with the bundle path.
- `--auto-continue` – alias for `--on-conflict bias`.

Successful syncs return to the previously checked-out ref and log the run to `.forked/logs/forked-build.log` (`event: "forked.sync"`). When conflicts remain unresolved, the command exits with code `10` (or the external command’s status for `exec`).

### `forked guard`

```bash
forked guard --overlay OVERLAY [--output PATH] [--mode MODE] [--verbose]
```

- `--overlay` *(required)* – overlay branch/ref to analyze (e.g., `overlay/test`).
- `--output` – report destination (default `.forked/report.json`).
- `--mode` – overrides `guards.mode` (`warn`, `block`, or `require-override`).
- `--verbose` / `-v` – print sentinel matches and include extra debug data in the report/logs.

Policy overrides are configured in `forked.yml`:

```yaml
policy_overrides:
  require_trailer: true
  trailer_key: "Forked-Override"
  allowed_values: ["sentinel","size","both_touched","all"]
```

When `guards.mode=require-override` (or `policy_overrides.require_trailer` is set), guard looks
for override trailers in this order: overlay tip commit → annotated tag message → git note
(`refs/notes/forked/override`). The first match wins; values can be comma- or space-delimited and
are normalized to lowercase (`sentinel`, `size`, `both_touched`, or `all`). Overrides must cover
every violation scope (or specify `all`) and respect `allowed_values`.

The v2 report schema contains:

- `both_touched` – files changed in both trunk and overlay since the merge base.
- `sentinels.must_match_upstream` / `.must_diverge_from_upstream` – validation results for sentinel globs.
- `size_caps` – diff size metrics via `git diff --numstat`.
- `violations` – subset of the above that failed policy.
- `override` – `{enabled, source, values, applied}` describing the override that was honored (source `commit|tag|note|none`).
- `features` – provenance-sourced feature list for the overlay (`source` reflects provenance log, git note, or resolver fallback).

Example extract:

```json
{
  "report_version": 2,
  "violations": {"sentinels": {...}},
  "override": {
    "enabled": true,
    "source": "commit",
    "values": ["sentinel"],
    "applied": true
  },
  "features": {
    "source": "provenance-log",
    "values": ["contract_update"],
    "patches": ["patch/contract-update"]
  }
}
```

Exit codes:

- `0` – pass (or violations in `warn` mode, or `require-override` when a valid override is applied).
- `2` – policy violations in `block`/`require-override` mode without a valid override.
- `3` – configuration missing/invalid.
- `4` – Git failure (dirty tree, missing remote, etc.).

### `forked status`

```bash
forked status [--latest N] [--json]
```

- Default output mirrors previous behavior: upstream/trunk SHAs, patch branches in configured order, and the newest overlays with their build timestamps and both-touched counts. The overlay window defaults to the latest **5** entries; adjust with `--latest N`.
- `--json` emits a machine-readable payload (`status_version: 1`) suitable for dashboards or guard automation. Provenance is sourced from `.forked/logs/forked-build.log` / `refs/notes/forked-meta`, with automatic fallbacks when those entries are missing.

Example:

```json
{
  "status_version": 1,
  "upstream": {"remote": "upstream", "branch": "main", "sha": "c0ffee..."},
  "trunk": {"name": "trunk", "sha": "b4d00d..."},
  "patches": [
    {"name": "patch/payments/01", "sha": "1234abcd...", "ahead": 2, "behind": 0}
  ],
  "overlays": [
    {
      "name": "overlay/dev",
      "sha": "feedf00d...",
      "built_at": "2025-10-20T18:45:02Z",
      "selection": {
        "source": "provenance-log",
        "features": ["payments"],
        "patches": ["patch/payments/01"]
      },
      "both_touched_count": 1
    }
  ]
}
```

Common `jq` flows:

```bash
forked status --json | jq '.overlays[].selection.features'
forked status --json --latest 1 | jq '.patches[] | {name, ahead, behind}'
```

When no overlays exist, the command returns an empty array and prints an informational message; consumers should treat `both_touched_count: null` as “guard data not yet collected”.

### `forked clean`

```bash
forked clean [--overlays FILTER] [--keep N] [--worktrees] [--conflicts]
             [--conflicts-age DAYS] [--dry-run/--no-dry-run] [--confirm]
```

- Dry-run is the default: the command prints a grouped summary (overlays, worktrees, conflicts) with the exact Git/File operations that would occur. No changes are made until you pass both `--no-dry-run` **and** `--confirm`.
- `--overlays FILTER` – target overlay branches by age (`30d`) or glob (`overlay/tmp-*`). Repeat the flag to combine filters. Use `--keep N` to preserve the N newest overlays regardless of filters. Tagged overlays, active worktrees, and the current branch are always skipped.
- `--worktrees` – prune stale worktrees via `git worktree prune` and remove leftover directories under `.forked/worktrees/*` that no longer map to live overlays.
- `--conflicts` – delete conflict bundles under `.forked/conflicts` older than the retention window (default 14 days). The newest bundle per overlay id is retained; override the threshold with `--conflicts-age`.
- Every destructive run appends an entry to `.forked/logs/clean.log` so operators have an audit trail.

Examples:

```bash
# Preview overlays older than 30 days, keeping the 2 most recent
forked clean --dry-run --overlays 30d --keep 2

# Remove temporary overlays once reviewed
forked clean --overlays 'overlay/tmp-*' --no-dry-run --confirm

# Clear stale worktrees and conflict bundles in a single sweep
forked clean --worktrees --conflicts --no-dry-run --confirm
```

### `forked feature create`

```bash
forked feature create NAME [--slices N] [--slug TEXT]
```

- `NAME` – feature identifier (kebab/snake case recommended).
- `--slices` – number of patch slices to create (default `1`).
- `--slug` – optional suffix for each slice (e.g., `--slug initial` produces `patch/<name>/01-initial`).

The command enforces a clean working tree, creates patch branches based on the current `trunk` tip, appends them to `forked.yml.patches.order`, and writes a new `features.<name>` entry. Branch creation fails fast if the feature already exists or if any target branch name is present.

### `forked feature status`

```bash
forked feature status
```

Prints each feature from `forked.yml.features` with the SHA (first 12 characters) of every slice and its ahead/behind counts relative to `trunk`. Fully merged slices are marked accordingly, providing a quick glance at feature progress before building or publishing overlays.

### `forked publish`

```bash
forked publish --overlay OVERLAY [--tag TAG] [--push] [--remote REMOTE]
```

Creates (or force-updates) a tag pointing at the overlay and optionally pushes the tag and overlay branch to a remote (default `origin`). Useful once a guarded overlay is ready to share.

---

## Guard Reports

Default location: `.forked/report.json`

Example (trimmed):

```json
{
  "report_version": 2,
  "overlay": "overlay/dev",
  "trunk": "trunk",
  "base": "6c535ebe766748006eea7f5fc21d0eaa2bcf01a2",
  "violations": {
    "sentinels": {
      "must_match_upstream": ["api/contracts/v1.yaml"],
      "must_diverge_from_upstream": []
    }
  },
  "both_touched": ["src/service.py"],
  "size_caps": {
    "files_changed": 3,
    "loc": 42,
    "violations": true
  },
  "override": {
    "enabled": true,
    "source": "commit",
    "values": ["sentinel"],
    "applied": true,
    "allowed_values": ["sentinel", "size", "both_touched", "all"]
  },
  "features": {
    "source": "provenance-log",
    "values": ["contract_update"],
    "patches": ["patch/contract-update"]
  }
}
```

Guard checks in `mode=require-override` look for the configured trailer key (default `Forked-Override`) on the overlay tip commit, then annotated tags, then `refs/notes/forked/override`. The `override` block records which source supplied the escalation marker and whether it satisfied the active violations (or the special value `all`). The `features` block carries the provenance list harvested from build logs/notes, so downstream tooling knows which slices were active.

Downstream tooling (CI, bots) can parse `violations` and `override` to fail builds or surface escalation guidance. The `report_version` field allows the format to evolve while preserving backward compatibility.

---

## Conflict Bundles

When conflict bundling is enabled (`--emit-conflicts` or `--emit-conflicts-path`), `forked build` and `forked sync` record conflict bundles (`schema_version: 2`) under `.forked/conflicts/<id>-<wave>.json`:

```json
{
  "schema_version": 2,
  "wave": 1,
  "context": {
    "mode": "build",
    "overlay": "overlay/dev",
    "patch_branch": "patch/conflict",
    "patch_commit": "44b1b20...",
    "merge_base": "6d913cc...",
    "feature": "conflict_feature"
  },
  "files": [
    {
      "path": "app.py",
      "binary": false,
      "size_bytes": 29,
      "precedence": {
        "sentinel": "must_match_upstream",
        "path_bias": "none",
        "recommended": "ours",
        "rationale": "matched sentinel must_match_upstream"
      },
      "commands": {
        "accept_ours": "git checkout --ours -- 'app.py' && git add 'app.py'",
        "accept_theirs": "git checkout --theirs -- 'app.py' && git add 'app.py'",
        "open_mergetool": "git mergetool -- 'app.py'"
      }
    }
  ],
  "resume": {
    "continue": "git cherry-pick --continue",
    "abort": "git cherry-pick --abort",
    "rebuild": "forked build --id dev --on-conflict stop"
  },
  "note": "Commands assume a POSIX-compatible shell (e.g. bash, git bash, WSL)."
}
```

- **Wave numbering** – repeated conflicts in a single invocation append `-2.json`, `-3.json`, etc., and every wave is logged to `.forked/logs/forked-build.log` (`event: "forked.build"` or `"forked.sync"`).
- **Binary & large files** – `binary: true` entries omit diffs, record `size_bytes`, and always write `base.txt`/`ours.txt`/`theirs.txt` into the configured blob directory.
- **Automation hooks** – `--on-conflict bias` records auto-applied actions; `--on-conflict exec` retains the conflicted worktree and exits with the delegated command’s status.

Exit codes: `10` for unresolved conflicts, external command status for exec mode, and raw Git exit codes for non-conflict failures.

---

## Logs & Generated Artifacts

| Path | Purpose |
|------|---------|
| `.forked/logs/forked-build.log` | Append-only JSON telemetry for each build (overlay id, resolver input/features, per-branch commit & skip summaries, reused path). |
| `.forked/logs/forked-guard.log` | Append-only JSON telemetry for guard runs (overlay, mode, violations, optional debug). |
| `.forked/report.json` | Latest guard report. |
| `.forked/worktrees/<overlay-id>/` | Reused worktree for the overlay (removed by `git worktree prune`). |

All of these paths are ignored via `.gitignore` so your repo stays clean.

---

## CI Example

Capture bundles in CI and highlight a deterministic failure when exit code `10` occurs:

```yaml
- name: Build overlay with conflict bundle
  run: |
    set -e
    forked build --overlay dev \
      --emit-conflicts-path .forked/conflicts/ci \
      --on-conflict stop || status=$?
    if [ "${status:-0}" = "10" ]; then
      bundle=$(ls .forked/conflicts/ci-*.json)
      echo "::error::Conflict bundle generated at ${bundle}"
      exit 1
    fi
```

Upload `.forked/conflicts/` as an artifact so reviewers (or downstream automation) can inspect the JSON and Blob exports when a rebase/build fails.

---

## Demo Repository

Need a sandbox with realistic branches? Use the helper script:

```bash
./scripts/setup-demo-repo.sh demo-forked
cd demo-forked
forked init
# forked.yml now lists upstream, trunk, and patch branches created by the script
```

The script provisions:

- `patch/contract-update` and `patch/service-logging`
- sentinel-friendly directories (`config/forked/**`, `branding/**`)
- both upstream and origin bare remotes for push/pull simulation

---

## Development Workflow

```bash
# install runtime + dev dependencies inside a Poetry virtualenv
poetry install --with dev

# runtime modules live directly under src/

# lint & format with Ruff
poetry run ruff check .
poetry run ruff format --check .
# apply formatting automatically when needed
poetry run ruff format .

# run mypy (configured via pyproject.toml)
poetry run mypy

# run project handbook automation (e.g., sprint dashboards)
poetry run make -C project-handbook help
```

> Tip: `poetry shell` drops you into the virtualenv; otherwise prefix commands
> with `poetry run` (for example `poetry run forked status --json`).

### Publishing to PyPI

```bash
# 1. Update version in pyproject.toml (PEP 440 format)
# 2. Verify packaging artifacts locally
poetry build
# 3. Publish using an API token (set POETRY_PYPI_TOKEN_PYPI beforehand)
poetry publish --build
```

The build step produces `dist/forked-<version>.whl` and `.tar.gz`. Inspect the wheel (`unzip -l dist/*.whl`) if you need to confirm module contents before publishing.

#### GitHub Actions Release

- Push a tag matching `v*` (e.g., `v0.2.0`) to trigger `.github/workflows/publish.yml`.
- Store your PyPI token as `PYPI_API_TOKEN` in the repository secrets.
- The workflow runs Ruff, mypy, pytest, builds the artefacts via Poetry, and publishes with `pypa/gh-action-pypi-publish`.

Key handbook commands:

- `make task-list` – show current sprint tasks (`project-handbook/Makefile`).
- `make sprint-status` – current sprint health indicators.
- `make release-status` – release v1.0.0 progress overview.

When making CLI changes, regenerate the demo repo (script above), rerun `forked build` and `forked guard`, and inspect `.forked/logs/forked-build.log` to confirm logging.

---

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| `forked init` prints “Using diff3 merge conflict style…” | You are running Git < 2.38; the CLI falls back to a supported conflict style automatically. Upgrade Git if you want `zdiff3`. |
| Build warns about suffixing worktree directories | Run `git worktree prune` to remove stale entries, or delete the directory manually. |
| Guard exits with code `2` unexpectedly | Inspect `.forked/report.json` – look under `violations`. Run in `--mode warn` to explore without failing. |
| `forked build` applies no commits | Ensure `forked.yml.patches.order` lists your patch branches and that they diverge from trunk. |
| Guard report missing sentinel hits | Confirm the globs in `forked.yml.guards.sentinels` match actual file paths. |

---

Forked is still evolving. If you have questions or ideas for the next iteration (better guard reporting, new commands, CI integrations), open an issue or capture it in the project handbook backlog. Happy overlaying! 🚀
