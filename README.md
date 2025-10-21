# Forked CLI

Forked CLI lets you treat your fork like a product: keep `trunk` fast‑forwarded to upstream, stack patch branches in a reproducible overlay, and guard releases with deterministic policy checks. This repository contains the editable CLI implementation, automation scripts, and the project handbook that tracks sprint and release work.

---

## Table of Contents

1. [Concepts](#concepts)
2. [Repository Layout](#repository-layout)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Configuration (`forked.yml`)](#configuration-forkedyml)
6. [CLI Commands](#cli-commands)
7. [Guard Reports](#guard-reports)
8. [Logs & Generated Artifacts](#logs--generated-artifacts)
9. [Demo Repository](#demo-repository)
10. [Development Workflow](#development-workflow)
11. [Troubleshooting](#troubleshooting)

---

## Concepts

- **Upstream** – the canonical repository you track. `forked init` keeps a local branch named `trunk` fast‑forwarded to `upstream/<branch>`.
- **Patch branches** – lightweight topic branches (`patch/*`) stacked in `forked.yml.patches.order`. They are replayed during every build.
- **Overlay** – a disposable branch (`overlay/<id>`) that results from applying the ordered patch list on top of `trunk`. Optionally materialised via a Git worktree.
- **Guard** – policy checks (sentinels, both‑touched files, size caps) that validate the overlay and emit JSON reports for CI or local review.

Forked CLI coordinates those pieces so you can rebuild or guard your patch stack deterministically without mutating your day‑to‑day working tree.

---

## Repository Layout

```
.
├── forked/                    # CLI source code (typer-based)
├── pyproject.toml             # packaging metadata for editable install
├── scripts/setup-demo-repo.sh # helper to create a sandbox repo with patch branches
├── project-handbook/          # sprint/release handbook (Makefile-driven)
└── README.md                  # this document
```

Run-time artefacts are intentionally kept out of Git:

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
pipx install forked-cli
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

# 1. Initialise Forked CLI in the repo
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

4. **Optimise repeat builds** with `--skip-upstream-equivalents` (filters commits that already exist on trunk via `git cherry`).

5. **Automate overlays safely** using the new selection metadata in git notes and build logs—these record the active feature set so guard/status tooling and downstream bots can reason about provenance.

The key artefacts after a build/guard cycle:

- `.forked/worktrees/<id>/` – the reuseable overlay worktree.
- `.forked/logs/forked-build.log` – append-only JSON telemetry describing each build.
- `.forked/report.json` – deterministic guard report used by CI and local review.

---

## Configuration (`forked.yml`)

`forked.yml` is committed to your repository and controls upstream, patch ordering, guards, and worktree behaviour.

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

Key behaviours:

- Relative `worktree.root` paths are relocated outside the Git repo to avoid nested worktrees.
- Setting `$FORKED_WORKTREES_DIR` overrides the root path. On POSIX platforms the CLI rejects Windows-style roots (`C:\…`) to prevent confusion.
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
             [--emit-conflicts [PATH]] [--conflict-blobs-dir [DIR]]
             [--on-conflict MODE] [--on-conflict-exec COMMAND]
             [--no-worktree] [--auto-continue] [--git-note/--no-git-note]
```

- `--overlay PROFILE` – select features defined in `forked.yml.overlays.<profile>.features`. When omitted, all patches in `patches.order` are applied. If `--id` is not provided, the profile name becomes the overlay id.
- `--features NAME[,NAME...]` – comma-separated list of feature keys to include. Mutually exclusive with `--overlay`.
- `--include` / `--exclude` – add or remove patch branches via exact names or glob patterns (applied after feature/overlay resolution).
- `--skip-upstream-equivalents` – skip cherry-picking commits already present on trunk (based on `git cherry -v`) and log the skipped counts per patch.
- `--id` – overlay identifier (default: overlay profile name or current date `YYYY-MM-DD`).
- `--no-worktree` – build directly in the current working tree instead of creating/reusing a worktree.
- `--emit-conflicts [PATH]` – write a conflict bundle (`schema_version: 2`) when a cherry-pick halts. Defaults to `.forked/conflicts/<id>-<wave>.json` when no path is provided.
- `--conflict-blobs-dir [DIR]` – export base/ours/theirs blobs for each conflicted path (always used for binary/large files). Defaults to `.forked/conflicts/<id>/wave-<n>/` when the flag is present without a directory.
- `--on-conflict MODE` – conflict policy: `stop` (default, exit code 10), `bias` (apply recommended ours/theirs resolutions and continue), or `exec` (run an external command).
- `--on-conflict-exec COMMAND` – shell command invoked when `--on-conflict exec` is selected (use `{json}` as a placeholder for the bundle path).
- `--auto-continue` – legacy alias for `--on-conflict bias`.
- `--git-note/--no-git-note` – opt in/out of writing provenance notes to `refs/notes/forked-meta`.

Behaviour highlights:

- Worktree directories are reused between builds. If a stale directory blocks reuse, the CLI suffixes the path (e.g., `test-1`) and prints a reminder to run `git worktree prune`.
- Build summaries now display applied versus skipped commits (`--skip-upstream-equivalents`) and record the active feature set in `.forked/logs/forked-build.log` alongside resolver inputs.
- Conflict bundles capture multi-wave context, recommended resolutions, and blob locations. They are logged to `.forked/logs/forked-build.log` alongside exit metadata (status `conflict` for stop/exec, `success` when bias resolves conflicts).
- Optional git notes capture the selected features/patches to make overlay provenance discoverable with `git notes show`.

### `forked sync`

```bash
forked sync [--emit-conflicts [PATH]] [--conflict-blobs-dir [DIR]]
            [--on-conflict MODE] [--on-conflict-exec COMMAND]
            [--auto-continue]
```

- `--emit-conflicts [PATH]` – emit a rebase conflict bundle when a patch fails to rebase. Defaults to `.forked/conflicts/sync-<branch>-<wave>.json` when omitted.
- `--conflict-blobs-dir [DIR]` – export base/ours/theirs blobs for each conflicted file (automatically enabled for binary/large entries when the flag is present).
- `--on-conflict MODE` – `stop` (default, exit code `10`), `bias` (apply recommended resolutions and continue the rebase), or `exec` (delegate to an external command).
- `--on-conflict-exec COMMAND` – command executed when `--on-conflict exec` is selected; `{json}` is replaced with the bundle path.
- `--auto-continue` – alias for `--on-conflict bias`.

Successful syncs return to the previously checked-out ref and log the run to `.forked/logs/forked-build.log` (`event: "forked.sync"`). When conflicts remain unresolved, the command exits with code `10` (or the external command’s status for `exec`).

### `forked guard`

```bash
forked guard --overlay OVERLAY [--output PATH] [--mode MODE] [--verbose]
```

- `--overlay` *(required)* – overlay branch/ref to analyse (e.g., `overlay/test`).
- `--output` – report destination (default `.forked/report.json`).
- `--mode` – overrides `guards.mode` (`warn`, `block`, or `require-override`).
- `--verbose` / `-v` – print sentinel matches and include extra debug data in the report/logs.

The report contains:

- `both_touched` – files changed in both trunk and overlay since the merge base.
- `sentinels.must_match_upstream` / `.must_diverge_from_upstream` – validation results for sentinel globs.
- `size_caps` – diff size metrics via `git diff --numstat`.
- `violations` – subset of the above that failed policy.

Exit codes:

- `0` – pass (or violations in `warn` mode).
- `2` – policy violations in `block`/`require-override` mode.
- `3` – configuration missing/invalid.
- `4` – Git failure (dirty tree, missing remote, etc.).

### `forked status`

```bash
forked status [--latest N] [--json]
```

- Default output mirrors previous behaviour: upstream/trunk SHAs, patch branches in configured order, and the newest overlays with their build timestamps and both-touched counts. The overlay window defaults to the latest **5** entries; adjust with `--latest N`.
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
  "report_version": 1,
  "overlay": "overlay/test",
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
  }
}
```

Downstream tooling (CI, bots) can parse `violations` to fail builds or surface guidance. The `report_version` field allows the format to evolve while preserving backwards compatibility.

---

## Conflict Bundles

When `--emit-conflicts` is supplied, `forked build` and `forked sync` record conflict bundles (`schema_version: 2`) under `.forked/conflicts/<id>-<wave>.json`:

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
      --emit-conflicts .forked/conflicts/ci \
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
# install dependencies and editable CLI
python -m pip install -e .

# run project handbook automation (e.g., sprint dashboards)
cd project-handbook
make help
```

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

Forked CLI is still evolving. If you have questions or ideas for the next iteration (better guard reporting, new commands, CI integrations), open an issue or capture it in the project handbook backlog. Happy overlaying! 🚀
