# Forked CLI Expansion Implementation Plan

**Plan Version:** 1.1

> Addendum v1.1 captures policy override enforcement, status/clean UX, build provenance, conflict bundle v2, and sync safety changes. Schema bumps are additive and maintain backwards compatibility.

## Addendum Overview

- **Guard Policy Overrides** — introduce `guards.mode: require-override` behavior backed by commit/tag/note trailers and expand the guard report to `report_version: 2` with an `override` block.
- **Status JSON & Housekeeping** — add `forked status --json` (`status_version: 1`) and a guarded `forked clean` command with dry-run, retention, and confirmation semantics.
- **Build Selection Provenance** — persist overlay selections to `.forked/logs/forked-build.log` and optional Git notes so guard/report workflows inherit feature context.
- **Skip Upstream Equivalents** — optional `--skip-upstream-equivalents` flag filters no-op commits via `git cherry`.
- **Conflict Bundles v2** — handle binary/large diffs, multi-wave conflicts, and platform notes with `schema_version: 2`.
- **Sync Auto-Continue Policy** — default to halting on conflicts during `forked sync`; add `--auto-continue` for opt-in bias application and ensure bundle support matches build behavior.
- **Tech Evolution Note** — document Rust sidecar plans without shifting current Python CLI contracts.

## Updated CLI Commands and Options

**Context:** The current Forked CLI (Typer-based Python app) provides core commands – init, sync, build, guard, status, and publish – to manage a fork via an upstream-tracking **trunk**, a stack of **patch** branches, and throwaway **overlay** branches for combined testing[\[1\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Status%20and%20Publish%3A%20The%20CLI,fork%E2%80%99s%20repository%20for%20others%20to). We will enhance these commands and add new ones to support **feature-slice workflows** and **conflict bundle automation**. All new options align with existing Git-native patterns and produce machine-readable outputs for CI. Below are the planned CLI updates:

### forked build – Feature Selection & Conflict Handling

We extend forked build with new flags to allow selective overlay construction and automatic conflict bundle generation:

* **\--overlay \<profile\>** – Build an overlay from a named **overlay profile** defined in forked.yml. This flag selects all features listed under that profile (see *YAML Schema* below) and cherry-picks their patches in global order[\[2\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=build%20overlays%20by%20profile%20or,exclude%20patch%3Apatch%2Fexperimental). If no \--id is given, the profile name is used as the overlay branch name (e.g. overlay/dev for profile “dev”). This enables reproducible overlays (like a persistent overlay/dev branch) for common stacks of features.

* **\--features \<name1,name2,...\>** – Build an overlay from an ad-hoc set of **features**[\[2\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=build%20overlays%20by%20profile%20or,exclude%20patch%3Apatch%2Fexperimental). The CLI will resolve the patch list for each specified feature (via config) and combine them. This allows quickly testing a subset of features (e.g. forked build \--features payments\_v2,branding to include only those slices). Multiple features are merged and de-duplicated according to the global patch order (ensuring the overall cherry-pick sequence respects the established order)[\[3\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Under%20the%20hood%2C%20).

* **\--include \<patch\_glob\> / \--exclude \<patch\_glob\>** – Further refine which patch branches are included or skipped. \--include can add specific patch branches (by name or glob pattern) to the selection, and \--exclude filters out certain patches[\[2\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=build%20overlays%20by%20profile%20or,exclude%20patch%3Apatch%2Fexperimental). These apply on top of the features/overlay selection. For example, one could build a profile but exclude an experimental patch: forked build \--overlay dev \--exclude patch/experimental/\* (or include a one-off patch on top of selected features). The internal resolver will add all included patches (if present in global order) and then remove any excluded ones before building[\[4\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,global%20order%20selected%20%3D%20set)[\[5\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=def%20add,add%28p%29%20if%20include). If no \--overlay/--features are given, the default is to include *all* patches in patches.order (full stack, as today).
* **\--skip-upstream-equivalents** – Optional opt-in to skip no-op commits by comparing patch commit `patch-id`s against trunk via `git cherry -v`. When enabled, the resolver still respects the selected patch order but filters commits marked as already upstream (lines prefixed with `-`). We log how many commits are skipped per patch for auditability. Default behaviour (flag omitted) applies every commit in the patch branch as today.

* **\--emit-conflicts \<path\>** – Enable **conflict bundle** output. If a cherry-pick halts due to merge conflicts, the CLI will write a JSON **conflict bundle** file at the given path (e.g. .forked/conflicts.json) containing all details needed to resolve the conflicts[\[6\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%2A%20%60,conflict). By convention, we will default this path to .forked/conflicts/\<overlay-id\>.json if the flag is used without an explicit path (ensuring each build’s conflicts are saved separately). The JSON schema is detailed in a later section. This flag turns a stalled build into a machine-readable artifact for inspection or automation, instead of just a Git error.

* **\--conflict-blobs-dir \<dir\>** – Optional directory to output raw blob files for each conflicted file[\[6\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%2A%20%60,conflict). If provided (default would be .forked/conflicts/\<overlay-id\>/), the CLI will save three files per conflict (base.txt, ours.txt, theirs.txt) containing the content of the common base, overlay (ours), and patch (theirs) versions respectively[\[6\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%2A%20%60,conflict). The JSON bundle will include a reference to these files’ location for tools that prefer direct file access[\[7\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,19%2Fsrc_service.py%2F%22). This is useful for external merge tools or AI agents that want to read the full context of conflicts.

* **\--on-conflict \<mode\>** – Automated conflict resolution behavior on build. Modes include:

* **stop** (default): Stop the build on the first conflict, after emitting the bundle, and exit with a **distinct code 10**[\[8\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%2A%20%60)[\[9\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=). This is the safe default that surfaces conflicts for manual or automated handling.

* **bias-continue**: On conflict, first write the conflict bundle, then attempt to auto-resolve using the configured path bias rules and continue the cherry-pick (similar to the current \--auto-continue behavior)[\[10\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,with%20the%20JSON%20path). In this mode, the CLI will apply the predefined “ours”/“theirs” preferences (forked.yml.path\_bias) to each conflicted file and then run git cherry-pick \--continue. If *all* conflicts are resolved by the bias rules, the build proceeds to completion (exit 0). If any conflict remains (no bias rule matched a file), the build will stop as in stop mode, still producing the JSON. This mode automates trivial conflict resolution using known patterns.

* **exec**: On conflict, write the JSON bundle then immediately execute a custom shell command provided via \--on-conflict-exec[\[11\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,with%20the%20JSON%20path), instead of continuing. This lets you hook in an external script or AI-based resolver. The CLI will *not* attempt any resolution itself in this mode; it simply generates the data and calls your command.

* **\--on-conflict-exec '\<cmd {json}\>'** – Command to run when \--on-conflict exec is chosen[\[11\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,with%20the%20JSON%20path). Use {json} within the command as a placeholder for the conflict JSON file path. For example: forked build \--emit-conflicts .forked/conflicts.json \--on-conflict exec \--on-conflict-exec 'my-bot \--input {json}'. The CLI will substitute the path and run the command via shell. After the command exits, Forked will exit with *the same code* as the command’s exit status[\[12\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=), allowing CI to detect success/failure of the external resolution. The Git repository remains in a conflicted state for the external agent to finalize (e.g. the agent might resolve files and then advise a git cherry-pick \--continue). This mechanism enables powerful automation: for instance, invoking an AI to fix conflicts and then halting for review.

All existing forked build flags remain supported (e.g. \--id for naming overlays, \--no-worktree to build in-place). In particular, \--id can be combined with \--overlay or \--features to assign a custom overlay branch name if needed (overriding the default naming). If neither \--overlay nor \--features is given, the build will include every patch in the global order (full stack, preserving current default behavior). The legacy \--auto-continue flag will be deprecated in favor of \--on-conflict bias-continue (with backward-compatibility: using \--auto-continue will internally map to the new option). After each build, we continue to log a summary of applied patches and their commits to the JSON build log as done currently[\[13\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L194-L201). If a conflict bundle was emitted, the build log entry can note the bundle path for traceability.

### forked feature create

We introduce a new command for easier management of patch slices within a feature:

forked feature create \<feature-name\> \--slices N

This command scaffolds **N empty patch branches** for a new feature[\[14\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,makes%20patch%2Fpayments_v2%2F%7B01%2C02%2C03). For example, forked feature create payments\_v2 \--slices 3 will create branches: patch/payments\_v2/01-..., patch/payments\_v2/02-..., and patch/payments\_v2/03-...[\[15\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=create%20scaffolded%20slices%20forked%20feature,makes%20patch%2Fpayments_v2%2F%7B01%2C02%2C03). The naming convention uses a zero-padded index and a short slug for each slice (e.g. 01-initial or 01 if no slug is provided)[\[16\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Notes%3A). By default, each new patch branch will be based on the current trunk tip (so they start in sync with upstream). After creation, these branches are added to forked.yml automatically:

* In patches.order: the new patch branches are appended (or inserted in a sensible position if an order convention is followed) so that builds will include them.

* In features: a new feature entry is created mapping \<feature-name\> to the list of its patch branch names[\[17\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=features%3A%20payments_v2%3A%20patches%3A%20,logo).

The CLI will confirm branch creation and update the config. For instance, creating payments\_v2 feature adds a features.payments\_v2 section listing the three new patch/payments\_v2/NN-\* branches, and those branches are added to the global patches.order (maintaining overall order consistency). Branch creation will fail gracefully (with an error message and non-zero exit) if the feature name already exists or if any target branch name already exists in the repo. This ensures we don’t accidentally overwrite existing work. By automating slice setup, developers can immediately begin making small, logically separated commits in each patch branch, which keeps rebases easier down the line.

### forked feature status

This new command provides a status overview of features and their patches, complementing the existing forked status (which shows trunk/patches at a high level):

forked feature status

It will list each feature and the patch branches (slices) that compose it, along with their Git commit information[\[18\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=status%20by%20feature%20forked%20feature,SHAs). The output is organized as a tree:

* **Feature name** – for each feature in forked.yml.features.

* **Patch slices** – under each feature, list each patch branch in order (e.g. 01-schema, 02-repo, etc.), showing the latest commit SHA on that branch, and its relation to trunk. We will indicate if a patch is **ahead** or **behind** trunk or diverged:

  * e.g. patch/payments\_v2/01-schema: abcdef0 (2 commits ahead of trunk) if the patch contains commits not in trunk.

  * If a patch is fully merged upstream (no diff from trunk’s base), it could be marked as “(merged upstream)” and would be skipped in builds (as currently done)[\[19\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=The%20overlay%20branch%20represents%20your,build.log%29%20for%20auditability%5B10%5D%5B11).

  * If a patch is behind trunk (should rarely happen since sync rebases them), we note that as well.

The status helps developers see the state of each slice at a glance – which slices have unmerged changes and how large they are. We will implement this by iterating over features in the config and using Git to retrieve each patch branch’s HEAD SHA and compare it with trunk. The command will likely support an option in the future (like \--json) to script this output, but initially a human-readable tree is sufficient (following the style of forked status). Exit code will be 0 unless an error occurs (no policy checking here, just reporting). This command is especially useful to ensure all feature slices are up-to-date before building or publishing.

### forked status – JSON Output and Provenance

We extend `forked status` with a `--json` flag that emits machine-readable state for upstream, trunk, patches, and recent overlays. The schema (versioned via `status_version: 1`) is:

```json
{
  "status_version": 1,
  "upstream": {"remote": "upstream", "branch": "main", "sha": "abc..."},
  "trunk": {"name": "trunk", "sha": "def..."},
  "patches": [
    {"name": "patch/feature/01-schema", "sha": "123...", "ahead": 3, "behind": 0}
  ],
  "overlays": [
    {
      "name": "overlay/dev",
      "sha": "789...",
      "built_at": "2025-10-20T18:45:02Z",
      "selection": {
        "features": ["payments_v2","branding"],
        "patches": ["patch/feature/01-schema","patch/feature/02-repo"]
      },
      "both_touched_count": 4
    }
  ]
}
```

Key details:

- Ahead/behind counts are computed versus `trunk` using `git rev-list --left-right --count`; failure to compute (e.g. patch missing) yields zeroes plus a warning in `stderr`.
- Overlay list defaults to the latest 5 entries; `--latest N` adjusts the window.
- During `forked build`, we append provenance to `.forked/logs/forked-build.log` including timestamp, trunk SHA, selected patches, features, resolver metadata, commit ranges per patch, and skip counts. We also write optional notes to `refs/notes/forked-meta` for the overlay tip (`patches:...;features:...`). Guard prefers log/notes metadata before recomputing selections so reports include `report.features`.
- `forked status --json` reads the provenance log to populate overlay `selection` and `built_at` fields, grabs `both_touched_count` from the latest guard report when available, otherwise emits `null` and issues a warning (while marking `selection.source = "derived"`).

Acceptance criteria: the JSON output feeds direct consumption by dashboards; guard and status share provenance utilities; documentation updates show combined usage with `jq`.

### forked clean – Safe Pruning Workflow

We are introducing a first-class cleanup command to prune stale worktrees, overlay branches, and conflict artefacts. Usage:

```
forked clean [--dry-run] [--keep N] [--overlays <age|pattern>] [--worktrees] [--conflicts] [--confirm] [--age 30d]
```

Design notes:

- **Dry-run first**: without `--confirm`, the command prints a summary plus exact Git operations (deleting branches, removing directories) and exits 0 with a reminder that nothing was executed; users must re-run with `--no-dry-run --confirm` to execute actions.
- **Worktrees**: `--worktrees` applies `git worktree prune` and removes directories under `.forked/worktrees/*` that no longer map to live overlays or protected entries. We never touch worktrees referenced by the current overlay or listed in `forked.yml` overrides.
- **Overlays**: `--overlays 30d` deletes overlay branches older than 30 days that are not tagged and not the configured default overlay; glob patterns (e.g. `--overlays 'overlay/tmp-*'`) remove matches. `--keep N` preserves the N most recent overlays regardless of age/pattern. Overlays referenced in provenance logs within the keep window are protected automatically.
- **Conflicts**: `--conflicts` clears `.forked/conflicts/*` directories older than 14 days (removing JSON + blob subdirectories), retaining the latest bundle per overlay id for auditability.
- **Safety**: Tagged overlays, the configured default overlay, and those referenced in provenance logs within the keep window are skipped automatically; executed actions are appended to `.forked/logs/clean.log` for audit.

Acceptance criteria: dry-run output mirrors execution, installing guardrails against accidental destructive operations, and documentation clarifies recommended cadence (post-release or weekly).

### forked guard Enhancements (Feature Awareness)

The forked guard command (policy checks) will be updated to better handle feature-scoped context and reduce noise when working with selective overlays:

* **Feature-Scoped Sentinels:** We introduce the ability to define sentinel rules per feature in forked.yml (see schema below). Guard will merge any feature-specific sentinel patterns with the global sentinel list when evaluating an overlay[\[20\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=%2A%20%2A%2AScope%20both,globs%2C%20merged%20with%20global%20ones)[\[21\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=payments_v2%3A%20sentinels%3A%20must_match_upstream%3A%20%5B,so%20you%20can%20decide%20%E2%80%9Cship). If the overlay being guarded was built with a specific set of features (e.g. via \--features or \--overlay), the guard will *only enforce the sentinel rules relevant to those features* plus all global rules. This way, feature-specific “must\_match” or “must\_diverge” expectations are checked only when that feature is present. For example, if feature payments\_v2 declares that api/contracts/\*\* must not be altered, then any overlay including payments\_v2 slices will flag deviations in api/contracts/\*\* as violations[\[22\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=features%3A%20payments_v2%3A%20sentinels%3A%20must_match_upstream%3A%20%5B,so%20you%20can%20decide%20%E2%80%9Cship). In an overlay that does *not* include payments\_v2, that rule can be ignored or reported separately (since the feature’s changes aren’t present). This scoping prevents irrelevant sentinel warnings when you’re only building other features.

* **Both-touched file focus:** The guard’s both-touched analysis (files changed both upstream and in the overlay) can now be **scoped to the selected features first**[\[23\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Guards%20that%20understand%20features%20,noise%2C%20more%20signal). Concretely, if you built an overlay with \--features X, guard will report any both-touched files that were touched by feature X’s patches as primary output. Optionally, it can still report other both-touched files (from patches not in this overlay or from excluded patches) in a separate section for awareness. This prioritization ensures that when working on a single feature, you see the most relevant merge conflict hotspots first, reducing noise from unrelated changes.

* **Per-Feature Risk Summary:** The JSON guard report (.forked/report.json) will include a breakdown of policy results by feature (when features are defined). We will add a section grouping any violations or noteworthy metrics per feature[\[24\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=must_match_upstream%3A%20%5B,%E2%80%9Cship%20branding%20now%2C%20hold%20payments_v2%E2%80%9D). For example, the report might list that feature *X* has 2 both-touched files and 1 sentinel violation, while feature *Y* has none. This helps in decisions like “ship feature A now, but hold off on feature B” based on risk. It essentially annotates the existing violations and both\_touched data with the feature that contributed those changes. Internally, we can derive this by mapping each patch branch to its feature, and for each file flagged by guard, determine which feature’s patch last modified it. This attribution will be noted in the JSON (e.g. an array of features associated with a both-touched file or a new violations\_by\_feature map for easy lookup).

Aside from these additions, forked guard retains its current behavior for exit codes and output formatting. The exit codes remain: 0 for success (or warnings only), 2 for policy failure in block mode, etc.[\[25\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=The%20guard%20outputs%20a%20JSON,16). A new exit code is not needed here, since guard’s context hasn’t changed – we are only enriching the report and filtering scope. All guard output (including any new feature-grouped info) will continue to be written to the JSON report file by default (.forked/report.json)[\[26\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L200-L208)[\[27\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L242-L250), with the \--verbose flag still available for extra debug detail if needed.

#### Guard Policy Overrides (`mode=require-override`)

To support escalation workflows, guard now honours override trailers when `guards.mode` is set to `require-override`. Configuration remains optional and backwards compatible:

```yaml
policy_overrides:
  require_trailer: true
  trailer_key: "Forked-Override"
  allowed_values: ["size","sentinel","both_touched","all"]
```

When violations occur in `require-override` mode, the CLI searches for override markers in this order: overlay tip commit trailers, annotated tag message trailers (when publishing), and `git notes --ref=refs/notes/forked/override`. The first matching source wins and later sources are ignored. Trailers may list comma- or space-separated scopes (`Forked-Override: sentinel, size`). If no override is found the run exits **2**; if scopes are present and allowed it exits **0** and records `override.applied=true`; disallowed scopes keep the failure. Guard increments `report_version` to `2`, adding an `override` block to `.forked/report.json`:

```json
{
  "override": {
    "enabled": true,
    "source": "commit|tag|note|none",
    "values": ["all","sentinel"],
    "applied": true
  }
}
```

Unit tests cover each source path plus allowed/disallowed combinations. Documentation updates call out override usage and migration guidance.

### forked sync Enhancements (Conflict Bundles)

The forked sync command (which fast-forwards trunk and rebases each patch onto it) will gain similar conflict-handling improvements to make upstream integration smoother:

* **Conflict Bundle on Rebase:** Just like forked build, if a forked sync encounter conflicts rebasing a patch branch, the CLI will generate a conflict bundle. The JSON schema is the same, with context.mode \= "sync" to distinguish it from build mode[\[28\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=Also%20do%20this%20for%20,sync). Additional context fields will indicate which patch branch and commit are being rebased when the conflict occurred. For example, context.patch\_branch and context.patch\_commit will be set for sync conflicts[\[29\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,base%28trunk%2C%20patch_commit%20or%20tip). This artifact gives maintainers a structured view of what went wrong during sync (which upstream changes collided with which patch). We will reuse the same fields and format defined for build conflicts, ensuring tools or scripts can handle both scenarios uniformly.

* **forked sync \--emit-conflicts and related flags:** We will extend sync to accept \--emit-conflicts, \--conflict-blobs-dir, \--on-conflict, and \--on-conflict-exec options analogous to forked build (though they may often be used in non-interactive contexts). In practice, a maintainer might run forked sync \--emit-conflicts .forked/conflict-sync.json \--on-conflict stop during an automated upstream update to capture any merge issues. If a conflict is detected in one of the patch rebases, the CLI will output the JSON and exit with code 10, instead of leaving the repo mid-rebase with no context. The bias-continue mode could also be applied to sync if the maintainer is comfortable auto-resolving trivial rebase conflicts using the same path bias rules. (Auto-continuing a rebase can be riskier than for overlays, so this would be opt-in and used with caution[\[30\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Automate%20Where%20Safe%3A%20Continue%20to,it%20could%20speed%20up%20updates), similar to how \--auto-continue might be extended to sync in the future.)
* **Auto-continue policy:** By default sync stops on the first conflict (safer behaviour). A new `--auto-continue` flag mirrors the build’s bias handling: after capturing the bundle, we apply path-bias recommendations, run `git rebase --continue`, and if a subsequent commit conflicts we emit the next wave bundle and repeat. Each auto-applied bias is logged in `.forked/logs/forked-build.log` under a `sync` entry so operators can review automated edits.

* **Process flow:** forked sync will iterate through each patch as usual, rebasing onto trunk. We will incorporate conflict handling in this loop. If a patch rebase hits a conflict:

* If \--on-conflict=stop (default), write the bundle (e.g. .forked/conflicts-sync-\<patch\>.json) and abort the sync operation at that patch, exit code 10\. The user can then address the patch conflict with the help of the JSON.

* If \--on-conflict=bias-continue, generate the bundle (for logging/record) then attempt git rebase \--continue after auto-resolving files per path bias rules. If successful, sync proceeds to the next patch; if not, it aborts as above.

* If \--on-conflict=exec, generate JSON then run the specified command, passing it the JSON path. We will then exit with the command’s status, leaving the repo in conflict for the external resolver to handle (the user/agent would fix the patch branch and run git rebase \--continue).

Throughout the sync process, trunk remains untouched except for the fast-forward, and any successfully rebased patches will have been applied to new commits. By adding conflict bundle support, we significantly improve guidance when upstream changes break a patch: instead of a generic “Resolve conflicts and run git rebase \--continue,” the user or an automated helper gets structured info on what to do.

**Note:** The forked init, forked status, and forked publish commands remain largely unchanged in this expansion. forked status will continue to show recent overlays and patch list, and may be updated later to incorporate feature info (for now, feature status is the main feature-specific status tool). forked publish will work as before, tagging/pushing overlay branches – it can be used after building an overlay from features or profiles to share that combined result[\[1\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Status%20and%20Publish%3A%20The%20CLI,fork%E2%80%99s%20repository%20for%20others%20to). We ensure that these commands continue to function with the extended config schema (e.g. ignoring new keys they don’t use).

## forked.yml Configuration Schema Extensions

To support features and overlay profiles, we will extend the forked.yml schema (while maintaining backward compatibility). Below are the new sections to be added, alongside the existing keys:

* **Global Patch Order (unchanged):** We retain patches.order as the single source of truth for the sequence of patch branches[\[31\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=%2A%20%2A%2ABranch%20naming%2A%2A%3A%20%60patch%2F%3Cfeature%3E%2F%3CNN%3E,subsets%20from%20that%20order). This is a list of patch branch names (strings) in the order they should be applied. The new features mechanism will reference these names. (If a patch is not listed in order, it’s considered inactive/unmanaged).

* **features map:** A mapping of **feature name** to a list of patch branches (slices) that constitute that feature. For example:

features:  
  payments\_v2:  
    patches:  
      \- patch/payments\_v2/01-schema  
      \- patch/payments\_v2/02-repo  
      \- patch/payments\_v2/03-api  
  branding:  
    patches:  
      \- patch/branding/01-logo  
      \- patch/branding/02-header

Each feature’s patch list **must** be a subsequence of the global patches.order. The CLI will enforce that these names match actual branches and appear in patches.order. The global order is still authoritative on build sequencing; features are effectively named subsets of that ordered list[\[31\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=%2A%20%2A%2ABranch%20naming%2A%2A%3A%20%60patch%2F%3Cfeature%3E%2F%3CNN%3E,subsets%20from%20that%20order). This design avoids any duplicate or contradictory ordering – features do not introduce a second ordering layer, they only group patches. By default, this features map can be empty or omitted if not using the feature-slice workflow; the CLI will treat every patch as its own feature or just use the flat order.

* **overlays map:** A mapping of **profile name** to a set of features (and/or individual patches) that define an overlay composition. For example:

overlays:  
  dev:  
    features: \[payments\_v2, branding\]  
  payments-only:  
    features: \[payments\_v2\]  
  branding-only:  
    features: \[branding\]

In this example, “dev” overlay includes both features, whereas other profiles include only one[\[32\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=overlays%3A%20dev%3A%20features%3A%20,only%3A%20features%3A%20%5Bbranding%5D). Users can define any number of profiles for common combinations of features. The forked build \--overlay \<name\> flag uses this map to resolve which patch branches to include. Under the hood, the CLI will replace the profile with the union of all patches from its listed features (again preserving the global order). If a profile name is passed that isn’t in the config, the CLI will error (exit code 3, config invalid). This map is optional; if no overlays are defined, the \--overlay flag simply won’t be used by the user.

* **Feature-level Sentinels (optional):** We extend the **guards.sentinels** concept to allow **per-feature overrides**. In addition to the global guards.sentinels.must\_match\_upstream and must\_diverge\_from\_upstream (which remain in effect globally[\[33\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Sentinels%3A%20You%20can%20configure%20path,16)), a feature can specify its own sentinel patterns. In forked.yml, inside each feature entry, an optional sentinels key can be added, for example:

features:  
  payments\_v2:  
    patches:  
      \- patch/payments\_v2/01-schema  
      \- patch/payments\_v2/02-repo  
      \- patch/payments\_v2/03-api  
    sentinels:  
      must\_match\_upstream:  
        \- "api/contracts/\*\*"  
      \# (could also have must\_diverge\_from\_upstream if needed)

This means “when feature *payments\_v2* is active in an overlay, ensure all files under api/contracts/ remain identical to upstream”[\[34\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,so%20you%20can%20decide%20%E2%80%9Cship) (perhaps this feature intentionally avoids touching API contracts). These feature-level sentinels will be **merged with** the global sentinels when running guard: effectively, the guard will consider all guards.sentinels patterns plus any from the active features’ own lists[\[20\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=%2A%20%2A%2AScope%20both,globs%2C%20merged%20with%20global%20ones). If a feature’s sentinel conflicts with a global rule (e.g. globally a path must match upstream, but feature says it must diverge), the stricter interpretation will be taken or we’ll flag the config conflict – however, we expect configuration to be set logically (features likely refine but not directly contradict global policies). Feature sentinels allow granular policy: e.g. one particular feature is expected to alter certain files (so those files are exempt from a global must-match rule only when that feature’s patches are present). We will document this clearly so users understand that feature sentinels are conditional on feature inclusion.

* **No changes to other keys:** The rest of forked.yml remains as in version 1\. We still have upstream (remote and branch), branches (trunk and overlay prefix), guards (global guard settings), path\_bias, worktree, etc., which all continue to apply[\[35\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=automatically%20skips%20patches%20that%20are,build.log%29%20for%20auditability%5B10%5D%5B11). Notably, path\_bias remains a single global setting for conflict resolution preferences (it is not made per-feature in this iteration). The version field will remain 1 for now, as these additions are backwards-compatible extensions to the schema (we’ll bump the version if needed to signal non-backwards-compatible changes). Users with older configs (without features/overlays) will see no change in behavior – the CLI simply won’t utilize the new keys until they are added.

**YAML Schema Summary:** In summary, a full forked.yml with new features might look like:

version: 1  
upstream:  
  remote: upstream  
  branch: main  
branches:  
  trunk: trunk  
  overlay\_prefix: overlay/  
patches:  
  order:  
    \- patch/payments\_v2/01-schema  
    \- patch/payments\_v2/02-repo  
    \- patch/payments\_v2/03-api  
    \- patch/branding/01-logo  
    \- patch/branding/02-header  
features:  
  payments\_v2:  
    patches:  
      \- patch/payments\_v2/01-schema  
      \- patch/payments\_v2/02-repo  
      \- patch/payments\_v2/03-api  
    sentinels:  
      must\_match\_upstream:  
        \- "api/contracts/\*\*"  
  branding:  
    patches:  
      \- patch/branding/01-logo  
      \- patch/branding/02-header  
      \# no special sentinels for this feature  
overlays:  
  dev:  
    features: \[payments\_v2, branding\]  
  payments-only:  
    features: \[payments\_v2\]  
  branding-only:  
    features: \[branding\]  
guards:  
  mode: warn  
  both\_touched: true  
  sentinels:  
    must\_match\_upstream:  
      \- "config/forked/\*\*"  
    must\_diverge\_from\_upstream:  
      \- "branding/\*\*"  
  size\_caps:  
    max\_loc: 0  
    max\_files: 0  
path\_bias:  
  ours:  
    \- "config/forked/\*\*"  
  theirs:  
    \- "vendor/\*\*"  
worktree:  
  enabled: true  
  root: ".forked/worktrees"  
\# ... (policy\_overrides etc., unchanged)

The above illustrates how the new features and overlays nest into the existing structure[\[36\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Keep%20your%20existing%20,overlay%20profiles)[\[17\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=features%3A%20payments_v2%3A%20patches%3A%20,logo). This format keeps all configuration in one file, still easily editable by hand. The CLI will provide validation (e.g. ensuring that every listed feature patch is in patches.order and every overlay profile refers to valid feature names, and that there are no duplicate patch names across features). We will update the internal config data class or schema parser to accommodate these new fields. For clarity, we’ll also update documentation and examples to show how to upgrade an existing forked.yml to use features and overlays (though they’re optional).

## Conflict Bundle JSON Schema (v1)

When a build or sync operation hits a conflict and \--emit-conflicts is used, Forked will produce a **conflict bundle** JSON file. This file encapsulates all information needed to understand and resolve the merge conflicts in an automated or manual way. The schema is as follows (**schema\_version: 1**):

{  
  "schema\_version": 1,  
  "context": {  
    "mode": "build",                  // "build" or "sync"  
    "overlay": "overlay/2025-10-19",  // Overlay branch used (if mode=build)  
    "trunk": "trunk",  
    "upstream": "upstream/main",  
    "patch\_branch": "patch/feature-x",// Patch branch being applied (or rebased, if sync)  
    "patch\_commit": "abcdef123456",   // SHA of the specific commit that caused the conflict  
    "merge\_base": "7890defabcdef",    // merge-base of trunk and patch (for reference)  
    "feature": "feature-x"            // (if applicable) Feature name of the patch, if known  
  },  
  "files": \[  
    {  
      "path": "src/service.py",  
      "status": "conflicted",  
      "slice": "patch/feature-x/02-example",   // which patch slice this file change comes from  
      "precedence": {  
        "sentinel": "must\_match\_upstream",  // if matched a sentinel rule (or "must\_diverge\_from\_upstream" or "none")  
        "path\_bias": "ours",               // if matched a path\_bias rule ("ours", "theirs", or "none")  
        "recommended": "ours",             // net recommendation for resolution ("ours", "theirs", or "none")  
        "rationale": "matched sentinel must\_match\_upstream"  // explanation for recommendation  
      },  
      "oids": {  
        "base": "blob:1:src/service.py",   // Git blob OIDs for base, ours, theirs (index stage references)  
        "ours": "blob:2:src/service.py",  
        "theirs": "blob:3:src/service.py"  
      },  
      "diffs": {  
        "base\_vs\_ours\_unified": "@@ \-10,3 \+10,5 @@ ...",   // unified diff chunks (context abbreviated)  
        "base\_vs\_theirs\_unified": "@@ \-10,3 \+10,4 @@ ...",  
        "ours\_vs\_theirs\_unified": "@@ \-12,8 \+12,9 @@ ..."  
      },  
      "commands": {  
        "accept\_ours": "git checkout \--ours \-- 'src/service.py' && git add 'src/service.py'",  
        "accept\_theirs": "git checkout \--theirs \-- 'src/service.py' && git add 'src/service.py'",  
        "open\_mergetool": "git mergetool \-- 'src/service.py'"  
      },  
      "blobs\_dir": ".forked/conflicts/2025-10-19/src\_service.py/"  // folder with base.txt/ours.txt/theirs.txt if \--conflict-blobs-dir was used  
    }  
    // ... possibly more file objects if multiple files are in conflict  
  \],  
  "resume": {  
    "continue": "git cherry-pick \--continue",   // or "git rebase \--continue" for sync  
    "abort": "git cherry-pick \--abort",  
    "rebuild": "forked build \--id 2025-10-19"    // command to retry build (or resume) after aborting, if applicable  
  }  
}

Each top-level section is described below:

* **context:** Metadata about the conflict event[\[37\]\[29\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,base%28trunk%2C%20patch_commit%20or%20tip). It includes the mode (build or sync), which overlay branch was being built (if build mode; for sync this may be omitted or could use the special overlay name “sync” since an overlay branch isn’t created), the trunk branch name and upstream remote/branch for reference, the specific patch branch involved, and the commit ID that was being applied when the conflict occurred[\[29\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,base%28trunk%2C%20patch_commit%20or%20tip)[\[38\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%22patch_branch%22%3A%20%22patch%2Ffeature,base%28trunk%2C%20patch_commit%20or%20tip). We also record the merge\_base commit of trunk vs that patch commit, which can help understand the common ancestor of the changes. Additionally, if the patch branch is associated with a feature in the config, we include a feature field to contextualize which feature’s slice was in conflict[\[39\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Add%20fields%3A)[\[40\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,). This contextual info allows tools to, for instance, group conflicts by feature or provide user messaging like “Conflict while applying Feature X (patch 02-repo)”.

* **files:** An array of objects, one for each file that has merge conflicts. For each file:

* path: The file path relative to the repo that is in conflict.

* status: The conflict status/type. Currently this will simply be "conflicted" for all entries (we include it for future expansion, e.g. differentiating add/add conflicts or rename conflicts).

* slice: The patch slice identifier (branch name) that introduced the change on the fork’s side. This is essentially the patch branch name that was being applied when the conflict happened (same as patch\_branch in context, but if one commit touches multiple files, all will have the same slice value). Including it here makes it easy to filter or script per-slice resolutions.

* **precedence:** A sub-object providing guidance on how to resolve:

  * sentinel: If the file path matches a sentinel rule, we note which one (must\_match\_upstream or must\_diverge\_from\_upstream). If not, this is "none". In our example above, src/service.py matched a must-match rule[\[41\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20)[\[42\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,THEIRS%20%28patch).

  * path\_bias: If the file matches one of the configured path\_bias globs (ours or theirs), we note that preference (ours/theirs), or "none" if no bias pattern applies[\[43\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=2.%20Else%20).

  * recommended: The net **recommended resolution** based on Forked’s rules[\[44\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,is%20index%20stage%20for%20base)[\[45\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,matched%20sentinel%20must_match_upstream). This is determined by our precedence logic: **sentinel rules dominate, then path bias, otherwise no preference**[\[46\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20)[\[47\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=3.%20Else%20). In the example, because a must\_match\_upstream sentinel matched, the recommendation is "ours" (meaning favor the trunk/upstream version over the patch)[\[41\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20). If a must\_diverge\_from\_upstream matched, recommended would be "theirs" (take the patch changes)[\[41\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20). If no sentinel but a path bias rule matched, we recommend that side[\[43\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=2.%20Else%20). If neither applies, "none" (meaning manual decision needed).

  * rationale: A human-readable explanation of how the recommendation was derived (e.g. "matched sentinel must\_match\_upstream" or "matched path\_bias.theirs"). This helps developers or AI agents understand *why* a certain resolution is suggested. It basically echoes the rule that applied. We include this to improve transparency.

* **oids:** The Git blob object IDs for the three versions of the file:

  * base – the common ancestor version (Git index stage 1 in a merge conflict).

  * ours – the version from the overlay/trunk side (index stage 2).

  * theirs – the version from the patch commit being applied (stage 3\)[\[48\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,). These are given in a stable blob:\<stage\>:\<path\> format so that an agent or script can fetch the content easily (e.g. via git show blob:3:src/service.py)[\[49\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,based%20agents). By referencing the index, we avoid creating new blob entries or needing a working tree copy, keeping it Git-native.

* **diffs:** Quick unified diffs for convenience:

  * base\_vs\_ours\_unified – diff of base vs ours (what upstream/trunk changed on that file, relative to base).

  * base\_vs\_theirs\_unified – diff of base vs theirs (what the fork patch changed).

  * ours\_vs\_theirs\_unified – diff between the two sides of the conflict directly[\[50\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%22diffs%22%3A%20%7B%20%22base_vs_ours_unified%22%3A%20%22%40%40%20,py%27%20%26%26%20git%20add)[\[51\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%22base_vs_ours_unified%22%3A%20%22%40%40%20,py).

* These diffs are in unified format (with @@ hunks) as a quick way for an agent or user to see the changes without having to fetch blobs separately. We limited context (e.g. \-U3 for 3 lines of context) to keep these diffs concise[\[52\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,ours_vs_theirs_unified). They are meant for inspection or small-scale patching; for complex merges an agent might still prefer using the actual blobs. We chose text diffs in the first iteration for simplicity and interoperability – they can be easily parsed or shown in a CLI. (In the future, we could add a machine-friendly JSON diff structure as an option if needed.) \- **commands:** Ready-to-run Git commands to accept one side or invoke a mergetool: \- accept\_ours – a command string that, if run in the repo, will accept the "ours" version of this file (essentially git checkout \--ours \-- \<path\> && git add \<path\> as shown)[\[7\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,19%2Fsrc_service.py%2F%22). \- accept\_theirs – similarly, a command to accept the "theirs" (patch) version[\[7\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,19%2Fsrc_service.py%2F%22). \- open\_mergetool – a command to open the system’s merge tool for this file[\[7\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,19%2Fsrc_service.py%2F%22).

* These are provided for convenience so that an automated tool or even a user copying from the JSON can quickly apply a resolution. For instance, an AI agent could choose based on recommended and execute the corresponding accept\_\* command. We ensure to properly escape file paths in these commands. If the file was already resolved by an auto-continue, these might not be needed, but we emit them anyway for completeness. \- **blobs\_dir:** If \--conflict-blobs-dir was used, this points to the directory containing the base.txt, ours.txt, theirs.txt files for this path[\[53\]\[49\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,based%20agents). In our design, we’ll create a subfolder per file (for example, .forked/conflicts/\<id\>/src\_service.py/ where slashes in the path are replaced or encoded) to avoid collisions. Each such folder has three text files with the contents. An agent that prefers file I/O can use this path. If \--conflict-blobs-dir was not provided, this field may be omitted or null.

* **resume:** Instructions to resume or abort the halted Git operation[\[54\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%5D%2C%20,19%22%20%7D). We include:

* continue – the Git command to continue the cherry-pick or rebase once conflicts are resolved (git cherry-pick \--continue for builds, or git rebase \--continue for sync)[\[55\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=%60%60%60json%20%7B%20,ours)[\[56\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,continue%22).

* abort – the command to abort the cherry-pick/rebase (git cherry-pick \--abort or git rebase \--abort).

* rebuild – a suggested Forked command to rebuild the overlay from scratch, if the user prefers to start over after aborting. For example, forked build \--id 2025-10-19 to retry the same overlay build. This can help if one wants to incorporate resolved changes and run the build afresh.

These commands are mostly for user guidance. An automated agent might not need them, but they’re helpful for a person reading the JSON or for a script to echo next steps. By including them, we make the bundle self-contained in telling “how do I continue from here.”

The conflict bundle is written as a single JSON file. We designed it to be complete and actionable – a user or tool should be able to take this file and know exactly what happened and how to address it[\[57\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,containing%20everything%20an%20agent%20needs)[\[58\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,%28accept%20ours%2Ftheirs%2C%20continue%2Fabort). The schema\_version at top allows us to evolve the format in the future while tools can check version compatibility.

A few additional notes on this artifact: \- It is intended to be created whenever a conflict stops the process (either on first conflict if stop, or even if bias-continue resolves some files but then stops on an unresolved one – we’d output the remaining conflicts). In bias-continue mode, the JSON will show what conflicts occurred *even though the tool attempted to resolve them*. This can be useful for auditing or if the auto-resolution wasn’t desirable. \- The JSON is meant to complement the existing .forked/report.json (guard report) and .forked/logs – it does not replace any, and it’s only generated on build/sync failure due to merge conflicts[\[59\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=This%20complements%20your%20existing%20guard,%2B%20build%20logs). In CI, a conflict bundle could be archived as an artifact or used to trigger a notification, distinct from a guard policy failure. \- The size of this JSON is bounded by the number of conflict files and diff lengths; for typical conflicts (handful of files, small diffs) it will be very manageable. If a very large conflict occurs, the diffs could make the JSON large – in those cases, using the \--conflict-blobs-dir for raw files might be better than stuffing huge diffs into JSON. We allow both approaches.

## Ergonomic Defaults, Exit Codes, and Output Paths

We will follow established CLI conventions to make these new features user-friendly and consistent:

* **Default Overlay Naming:** Currently, forked build defaults the overlay \--id to the current date (YYYY-MM-DD)[\[60\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L185-L193). We will retain this behavior for builds that include *all patches or an ad-hoc feature set*. For builds triggered via an overlay profile (\--overlay \<name\>), if the user does not specify \--id, the default branch name will be overlay/\<name\> (using the profile’s name) rather than a date. This way, profile-based overlays get a predictable branch name (and can be rebuilt in place). The overlay\_prefix from config is used as usual (default “overlay/”). If an overlay profile name might conflict with an existing branch, the CLI will warn or append a suffix to avoid collisions. For example, if overlay/dev already exists and is in use, a build of \--overlay dev may create overlay/dev-1 and prompt the user to prune old worktrees (similar to current reuse logic)[\[61\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L193-L201).

* **Conflict Bundle Paths:** By default, if \--emit-conflicts is used without specifying a path, we will choose a path under .forked/ automatically. The default file could be .forked/conflicts.json (as in our docs) or .forked/conflicts/\<overlay-id\>.json to distinguish multiple runs. We are inclined towards including the overlay or timestamp in the name for clarity. Similarly, if \--conflict-blobs-dir is used with no argument, we default to .forked/conflicts/\<overlay-id\>/ directory. These defaults will be documented. All conflict-related outputs live under .forked/ (which is already gitignored) to keep the repo root clean[\[62\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=This%20dovetails%20with%20existing%20build,namespace). The user can of course specify custom paths if integrating with other systems.

* **Exit Codes:** We introduce **exit code 10** to specifically indicate “build/sync stopped due to merge conflicts with a bundle emitted”[\[10\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,with%20the%20JSON%20path)[\[63\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=). This separates conflict stops from guard policy failures (exit 2\) or general errors. The CLI’s exit codes will be as follows:

* **0:** Success (build completed and, if guard ran, no blocking violations).

* **2:** Guard policy violations (in \--mode block or require-override)[\[64\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=The%20guard%20outputs%20a%20JSON,16).

* **3:** Usage or configuration error (invalid config, missing upstream, etc.)[\[65\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L217-L224).

* **4:** Git operation failure (e.g. couldn’t apply a patch, or trunk sync failed due to a dirty worktree).

* **10:** Merge conflicts occurred, bundle emitted (new).

Code 10 is used in both forked build and forked sync when a conflict halts the process (and we successfully wrote the conflict JSON). If \--on-conflict=exec was used, the exit code will instead be whatever the user’s exec command returns[\[12\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=) – this lets a custom script signal success (0) or failure (non-zero) of its attempt. We chose 10 because it’s distinct and doesn’t overlap with common Git exit codes; CI systems or wrappers can specifically look for 10 to handle merge conflicts differently from policy failures. These codes will be clearly documented (they extend the existing set, keeping all current codes the same)[\[9\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=).

* **CLI Usability Defaults:**

* The forked feature create command’s \--slices option will default to 1 if not provided (creating a single patch branch). We anticipate most features start with a few slices, so we allow quick scaffolding of multiple at once, but a single slice is a valid default.

* The forked feature status command might get a \--latest N option similar to forked status to limit how many features or how many recent overlays to show, but by default it will show all features in the config.

* For forked guard, no new flags are added in this phase (scoping and feature sentinel merging happen automatically based on the overlay content and config). We might introduce a flag to control “rest of repo” output for both-touched (e.g. \--full vs \--focused) if needed, but initially it can automatically show a summary of outside-of-feature both-touched files when relevant.

* The forked sync command by default will continue to stop on conflicts as it does now (just now it can produce a bundle). We won’t change default sync behavior to auto-resolve anything – \--on-conflict must be explicitly used to alter that, keeping safety by default[\[66\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Guidance%20on%20Conflicts%3A%20Ensure%20that,best%20practices%20for%20resolving%20those).

* **Output File Locations:** We continue the convention that all generated artifacts go under a dedicated directory. The .forked/ directory will still contain:

* worktrees/ – overlay worktrees (no change).

* logs/ – JSON logs for builds and guards (no change; we append to these logs on each run)[\[67\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=invoked%20with%20,build.log%29%20for%20auditability%5B10%5D%5B11).

* report.json – latest guard report (still the default guard output)[\[27\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L242-L250).

* conflicts/ – *new* directory for conflict bundles. The default JSON and any blob subdirectories will reside here.

For example, after a conflict, you might have .forked/conflicts/dev.json and a folder .forked/conflicts/dev/src\_service.py/ with blobs, if you built overlay “dev”. We ensure to create any subdirectories as needed. All these paths are already ignored by Git, so they won’t show up as untracked changes[\[68\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L280-L283). This layout makes it easy to clean up old artifacts (we may later provide a forked clean command to remove stale worktrees, logs, and conflict files).

* **Integration with Existing Logs:** We will augment the JSON logs to note new events. For instance, the .forked/logs/forked-build.log entry for a build that encountered conflicts can include a field like "conflict\_bundle": ".forked/conflicts/\<id\>.json" to trace that this build produced a conflict file. The guard log could include per-feature violation counts if we add that. These logs are mainly for audit and troubleshooting, and we will keep their format backward-compatible (adding new keys rather than changing existing ones)[\[67\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=invoked%20with%20,build.log%29%20for%20auditability%5B10%5D%5B11). Logging of normal operations (patch applied, patch skipped because merged, etc.) will remain as is.

In summary, the CLI will behave predictably, with sensible defaults that favor safety. Users can ignore new flags if they don’t need them – the workflow remains the same unless you opt into features or conflict automation. When used, the outputs and exit codes are chosen to be distinct and scriptable, enabling smooth CI integration.

## Python Implementation Strategy

We will implement these features in Python, leveraging the existing code structure (Typer commands, dataclass config loader, and Git subprocess calls). Below are key implementation notes and strategies:

### Feature & Overlay Resolution

Introduce a utility function (as sketched in design docs) to **resolve patches to apply** based on the new flags[\[69\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,global%20order%20selected%20%3D%20set)[\[70\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=for%20f%20in%20cfg.overlays%5Boverlay%5D%5B,set%28exclude). For example, resolve\_patches(config, features=None, overlay=None, include=None, exclude=None) will:

1. Start from the full ordered list config.patches.order (global sequence)[\[71\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=def%20resolve_patches,global%20order%20selected%20%3D%20set).

2. Initialize an empty set selected.

3. If overlay (profile name) is provided, loop through each feature in config.overlays\[overlay\].features and add all their patch names to selected[\[72\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=if%20p%20in%20order%3A%20selected,add%28p%29%20if%20include).

4. If features (list of feature names) is provided, do the same for each named feature[\[70\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=for%20f%20in%20cfg.overlays%5Boverlay%5D%5B,set%28exclude).

5. If include is provided, add those patch names/pattern matches to selected (provided they exist in the global order)[\[73\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=def%20add,add%28p).

6. If exclude is provided, remove any matching patch names from selected[\[74\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=for%20p%20in%20cfg.features%5Bf%5D%5B,set%28exclude).

7. Finally, produce a list of patch names in the original global order that are in selected[\[75\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=order%20%3D%20cfg.patches.order%5B%3A%5D%20%20,global%20order%20selected%20%3D%20set).

This ensures the final list of patches to cherry-pick respects the intended order and selection criteria. We will utilize Python’s fnmatch or regex to allow glob patterns in include/exclude. This resolver will be called at the start of forked build to determine which patches to apply. (If none of the new flags are given, selected will effectively become all of patches.order.) The resolver also naturally de-duplicates patches if the same patch is pulled in via multiple features or repeated include (set logic handles that). We will add unit tests for this function to cover scenarios: e.g. selecting one feature, one overlay, combining overlay+include, include+exclude overriding each other, etc., to ensure correctness.

### Applying Patches (Cherry-Pick Loop)

The core loop of forked build that cherry-picks each patch commit in order remains mostly the same – we’ll integrate the new logic as follows:

* We will modify the loop to be aware of the *current patch branch* being applied, and its feature (if any). As we cherry-pick commits from each patch branch, we know which feature we’re in by checking the config.features mapping. This context will be passed to the conflict handler (below) so that the JSON can record patch\_branch and feature[\[29\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,base%28trunk%2C%20patch_commit%20or%20tip).

* If no conflicts occur, the build finishes normally (exit 0, overlay branch contains all commits cherry-picked). If a conflict occurs during a git cherry-pick:

* Catch the git error/exception. At this point, Git will have paused with index state having conflict markers.

* Invoke the **conflict bundle generator** (see next section) to collect conflict info and write the JSON (and blob files if requested).

* Then decide next steps based on \--on-conflict:

  * For stop: we simply exit the command with code 10 after writing the bundle. (We may want to print a short message to the user, e.g. “Conflicts detected. See .forked/conflicts/\<id\>.json for details.”)

  * For bias-continue: we call an internal function to auto-resolve each conflicted file for which we have a recommendation:

  * For each file in the bundle where precedence.recommended is “ours” or “theirs”, run the corresponding git checkout \--ours/--theirs and git add (same as the commands we output) to accept that side[\[7\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,19%2Fsrc_service.py%2F%22). If any file had "recommended": "none", we will *not* attempt to resolve it (no rule to apply).

  * After processing files, run git cherry-pick \--continue. If Git reports that conflicts remain (meaning at least one file was not resolved due to no bias or complex conflict), then we stop as if in stop mode (the bundle was already written). If \--continue succeeds, the cherry-pick resumes to the next commit. We loop and continue applying patches. It’s possible another conflict arises later in the list – the process would repeat (generating another JSON bundle for the next conflict). Each conflict event is independent; we will name subsequent bundles uniquely (e.g. append an index or timestamp if the same overlay id is reused in one run, though typically one run stops at first conflict unless bias-continue is clearing them).

  * The outcome is either the build eventually finishes (exit 0\) after auto-resolving all conflicts, or it stops at a point where auto-resolve couldn’t fully handle it (exit 10 with the last bundle).

  * For exec: form the command string by replacing {json} with the path of the bundle file, then execute it via subprocess.run(shell=True). We will ensure the command runs in an environment where git is available (same repo directory). We’ll let it output to the console as it runs (so the user can see any AI tool messages, etc.). After it finishes, we exit with whatever code it returned. **Important:** we do *not* run git cherry-pick \--continue in this mode – it’s up to the external tool or user to continue the Git operation. Our CLI will remain stopped at the conflict point. This design was deliberate to allow an interactive or long-running resolution outside of our process[\[12\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=). The user could choose to abort or continue afterwards manually.

* We also need to handle cleanup: if forked build stops due to conflicts (in any mode), the overlay branch and worktree (if used) remain in a partially applied state. We’ll document that the user/agent should fix conflicts and continue/abort. If the user aborts, they can run forked build again to try again (possibly with updated patches). We won’t automatically delete the overlay in case the user wants to inspect it.

Implementing these in Python will likely involve the existing Git wrapper calls (we use subprocess Git calls currently). We can detect conflict situations by checking return codes or by using git status \--porcelain to see if any merge conflicts are present after a cherry-pick attempt. Another robust way is to run git cherry-pick \<commit\> and catch the exception or non-zero exit – Git will return a specific code for merge conflicts (often 128). We then proceed to bundle generation.

### Conflict Bundle Generation

The conflict bundle creation is a critical part. Steps to implement (mirroring the design spec):

1. **Collect conflicted files & OIDs:** We use git ls-files \-u which lists unmerged entries in the index for each conflicted file[\[76\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,OIDs). Each line of output provides stage number and blob id. We will parse this output to build a dictionary: {file\_path: {1: base\_oid, 2: ours\_oid, 3: theirs\_oid}}. This tells us the blob IDs for each version. If needed, we might also parse git status or git diff \--name-status to get the list of files, but ls-files \-u is concise and reliable for this purpose.

2. **Write quick diffs:** For each conflicted file, we will produce the unified diffs. We have two implementation options:

3. Use Python’s difflib to diff the blobs (after decoding to text). However, difflib may not produce identical output to Git and we’d have to manage file encoding, etc.

4. Easier: use git show to retrieve each blob’s content and then use git diff \--no-index on the temporary files[\[52\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,ours_vs_theirs_unified). We prefer the latter to ensure the diff format matches Git’s and respects e.g. any .gitattributes settings for diff (though likely not needed for unified text). Specifically, for a given path, we can do:

* git show \<base\_oid\> \> /tmp/base.txt  
  git show \<ours\_oid\> \> /tmp/ours.txt  
  git show \<theirs\_oid\> \> /tmp/theirs.txt  
  git diff \--no-index \-U3 /tmp/base.txt /tmp/ours.txt   \# base\_vs\_ours\_unified  
  git diff \--no-index \-U3 /tmp/base.txt /tmp/theirs.txt \# base\_vs\_theirs\_unified  
  git diff \--no-index \-U3 /tmp/ours.txt /tmp/theirs.txt \# ours\_vs\_theirs\_unified

* We can invoke these via subprocess and capture output. To avoid dealing with actual temp files, we might also try piping directly (git show :1:path | git diff \--no-index \-U3 \- \<(git show :3:path) etc.), but that complicates Windows support. Simpler is writing to a temp directory (Python tempfile can manage unique files). This is a bit heavy for many files, but the number of conflict files is usually small. We’ll also ensure to clean up temp files after diffing.

5. Alternatively, use a lib like GitPython to get blob data and use a diff library – but to ensure consistency with what a developer expects, using Git’s diff is acceptable. We do not include these diffs for binary files or extremely large files to avoid huge JSON; for binary, we might set the diff fields to an empty string or note “\<binary file\>”.

6. We will include at most these three diffs per file. (We might decide to omit base\_vs\_ours and base\_vs\_theirs if not strictly needed, since ours\_vs\_theirs often suffices, but our spec includes them all for thoroughness.)

7. **Compute precedence for each file:** Using the forked.yml config loaded in memory, we apply the **precedence rules**:

8. Check if the file path matches any sentinel in guards.sentinels.must\_match\_upstream or .must\_diverge\_from\_upstream[\[33\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Sentinels%3A%20You%20can%20configure%20path,16) (and also feature-level sentinels if applicable for the patch’s feature). We likely have glob patterns, so we use fnmatch to test. If a match is found:

   * If it’s in must\_match, we set precedence.sentinel \= "must\_match\_upstream" and that implies the fork’s changes should be dropped in favor of upstream – so recommended \= "ours" (since “ours” is the trunk/upstream side in the overlay)[\[41\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20).

   * If in must\_diverge, set sentinel \= "must\_diverge\_from\_upstream", recommended \= "theirs" (keep the fork changes)[\[41\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20).

9. Else, check config.path\_bias.ours and .theirs lists:

   * If file matches any ours path bias pattern, set path\_bias \= "ours", recommended \= "ours" (provided no sentinel already decided)[\[43\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=2.%20Else%20).

   * Else if matches any theirs pattern, set path\_bias \= "theirs", recommended \= "theirs"[\[43\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=2.%20Else%20).

10. If neither sentinel nor bias matched, set both to "none" and recommended \= "none"[\[47\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=3.%20Else%20).

11. We will also populate a rationale string: e.g. "matched sentinel must\_diverge\_from\_upstream" or "matched path\_bias.theirs" or "no rule matched". This is straightforward by keeping track of which condition triggered.

12. This logic mirrors what the CLI already does in \--auto-continue, so we can refactor the existing code (if any) for path\_bias application into a helper and use it here, to ensure consistency[\[30\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Automate%20Where%20Safe%3A%20Continue%20to,it%20could%20speed%20up%20updates). By making the recommended resolution explicit in JSON, we empower external tools to follow the same logic[\[77\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=This%20mirrors%20how%20%60,for%20agents).

13. **Prepare commands:** For each file, populate the commands.accept\_ours, commands.accept\_theirs, and commands.open\_mergetool exactly as shown above[\[7\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,19%2Fsrc_service.py%2F%22). We can hardcode these strings, inserting the file path. (On Windows, the commands would be the same if run in Git Bash or WSL; if someone uses Windows CMD, these commands might not run as-is, but we assume a POSIX shell context since Git on Windows typically provides that. We’ll note this in docs if needed.)

14. **Write the JSON file:** Gather all this data into a Python dict matching the schema and use json.dump to write to the file path. We set "schema\_version": 1. We include the context (with mode, overlay, trunk, upstream, patch\_branch, patch\_commit, merge\_base, feature as determined)[\[37\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,base%28trunk%2C%20patch_commit%20or%20tip). For resume, we know the commands (we can detect if we were in cherry-pick or rebase mode to choose the right continue/abort) and the intended overlay id to rebuild (which we have from \--id)[\[54\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%5D%2C%20,19%22%20%7D). If \--conflict-blobs-dir was used, we will have already saved the files in the specified directory; we should double-check that their paths are relative or absolute and put the appropriate reference in blobs\_dir for each file. We might make blobs\_dir either file-specific (as in our example) or one common directory for the whole operation. The design leans toward a subfolder per file for neatness. So the JSON writing function will need to know the directory pattern and fill that in.

15. **Clean up and messaging:** After writing the JSON (and blob files), if we are in stop or exec mode, we might issue a console message along the lines of “Conflict bundle written to .forked/conflicts/XYZ.json” so the user knows where to look. We’ll avoid overly verbose output since the JSON is the source of truth.

We will implement this in a separate module or function (e.g. generate\_conflict\_bundle(idx, output\_path, blobs\_dir, context) for reuse between build and sync). Given the detail, we will also add unit tests for the core parts: \- A test for the precedence logic: feed in some dummy patterns and file paths to ensure recommended outcomes match the rules (e.g. sentinel vs bias). \- Possibly a test with a simulated mini git repo: we can create a repo with a known conflict (or simulate index states by calling low-level git). As an alternative, use a pre-captured git ls-files \-u output and fake blob contents to run through the diff and JSON generation in isolation. The golden output should match expected JSON structure.

### Conflict Bundle v2 Enhancements

The addendum upgrades the bundle schema to `schema_version: 2` while remaining backwards compatible for consumers that accept v1. Enhancements include:

- **Binary/large file handling**: detect binaries (via `git diff --numstat` or null-byte probe) and large unified diffs (>256 KB). For those files we set `diffs.* = null`, add `binary: true`, include `size_bytes`, and always emit `base|ours|theirs` blobs into the configured directory.
- **Multiple conflict waves**: if `--on-conflict bias-continue` automatically resolves a set of files but later commits conflict again, we generate numbered bundles (`overlay-id-1.json`, `overlay-id-2.json`, ...), adding `"wave": 1|2|...` to the JSON. Each wave also appends a log entry to `.forked/logs/forked-build.log` summarizing the paths involved.
- **Shell metadata**: each file entry contains `"shell": "posix"` and the top-level resume block documents POSIX commands, clarifying expectations for Windows users (use Git Bash/WSL). We also add a top-level `"note": "Commands assume POSIX shell"` when applicable.
- **Shared serializer**: both build and sync consume the same writer, so `context.mode` plus fields (`feature`, `patch_branch`, `patch_commit`, `merge_base`) are consistent. Exit code handling stays the same (default `10`, overridden by `--on-conflict exec`).

Testing covers binary files, two-wave conflicts, blob directory creation, and Windows messaging.

### Feature Commands Implementation

* **forked feature create:** This will be implemented as a Typer subcommand. The logic:

* Verify that forked.yml is present and parseable (similar to how other commands ensure config exists).

* Validate the feature name (no spaces or weird chars, not "trunk"/"overlay" etc., to avoid conflicts).

* Determine the starting point commit for new patches – typically the current trunk HEAD (we will run git rev-parse trunk to get the commit). We ensure trunk is up-to-date (we might suggest running forked sync first if it’s behind upstream, but not strictly required).

* Loop from 1 to N (N \= \--slices):

  * Construct a branch name: patch/\<feature-name\>/\<NN\>-\<slug\>. We need a slug. We may default to something like the feature name or a generic "part". One approach: prompt the user for a short description for each slice (could be interactive, but that breaks automation). Instead, we might simply use the feature name as slug for all slices (but then they’d be identical, not great). Alternatively, use a fixed placeholder like “change” or “slice”. For now, we might name them 01-${feature}, 02-${feature}, etc., or just 01 if simplicity is okay. The design doc left it as an asterisk, implying perhaps they expect the user to rename the branches later or fill in. Since interactive prompts are not ideal, we could just create 01-placeholder and mention they can rename the branch if desired. We’ll document this choice. The key is the numeric prefix for ordering.

  * Use Git to create the new branch at trunk HEAD: e.g. git branch patch/feature/01-slice \<trunk\_sha\>. (No commit made on it yet; it’s just a branch pointer.)

* Append the new branch name to patches.order in the config (likely at the end, or we could insert them right after the last patch of that feature if some ordering grouping is desired – but since it’s a new feature, appending is fine).

* Add a new entry in features map for the feature (or update existing if feature already in config but maybe was empty):

  * features.\<name\>.patches \= \[list of branches created\].

* Write the updated forked.yml to disk. Possibly make a backup or warn the user that we modified it.

* Output a success message listing the new branches. We can suggest: “Edit files on these branches and commit your changes. Then run forked build \--features \<name\> to test the feature.”

We’ll also consider error cases: \- If the feature name already exists in config, we should either abort (to avoid accidentally duplicating) or allow adding more slices to an existing feature. Perhaps better to have the user run it once per feature. So likely we’ll error: “Feature X already exists. Use a different name or manually add slices.” \- If any patch/\<feature\>/\<NN\>-... branch already exists in Git (maybe leftover or name collision), abort and inform the user. \- If working directory is not clean (to avoid modifying config while unstaged changes exist), we might warn or even require a clean state (similar to init and sync which often demand no uncommitted changes[\[78\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Upstream%20Sync%20,4)).

This implementation is straightforward using subprocess Git for branch creation and PyYAML (if we use it) or manual YAML editing for config. Since we already parse forked.yml into a Python object (dataclass or dict), we can modify that object and dump it back.

* **forked feature status:** Implementation will gather data and print it. Likely steps:

* Load config and identify all features and their patches.

* For each feature, print the feature name. Then for each patch in features\[feature\].patches:

  * Get the latest commit’s short SHA and commit message (maybe just SHA for brevity). We can use git rev-parse \--short HEAD on that branch.

  * Compute its relation to trunk: one way is git merge-base patchbranch trunk, and if that equals the patch’s HEAD, then patch is fully merged. If not, count commits ahead: git rev-list \--left-right \--count trunk...patchbranch yields how many commits patch is ahead or behind trunk. If ahead count is \>0, that many commits are only in patch. If behind count is \>0, trunk has progressed that many commits beyond the patch’s base – but since sync is supposed to rebase, behind count for patch should usually be 0 (unless trunk has new commits and user hasn’t synced).

  * We’ll then format something like:

  * payments\_v2: (feature)

    * patch/payments\_v2/01-schema – abc1234 (1 commit ahead)

    * patch/payments\_v2/02-repo – def5678 (merged upstream)

    * etc.

  * We also might show if a patch is currently checked out (probably not relevant).

* If we discover any inconsistencies (like a patch listed in a feature not in patches.order), we could highlight them as warnings.

* This command mostly reads Git state; it doesn’t change anything, so it should be safe to run anytime.

We will reuse some logic from forked status (which already obtains trunk and overlay info). The output is textual, so we just ensure alignment/indentation is clear.

### Guard Command Updates

For the guard enhancements, we’ll modify the existing forked guard implementation:

* **Merging feature sentinels:** When loading the config for guard, determine which features are part of the overlay under analysis. If the user invoked guard via \--overlay overlay/X, we can infer X \= profile name if it matches one, or we may need to parse the overlay’s commit ancestry to guess included features. A simpler approach: when a build is done with features or overlay flags, we can record the feature list used (e.g. store it in the overlay branch’s ref notes or in the build log). However, to avoid over-engineering, we can allow the user to explicitly specify a context to guard (perhaps not needed if we can deduce reliably).

Likely, if overlay branch name equals overlay/\<profile\>, we assume it includes exactly those features. If it’s a custom id (like a date or custom name), we might not know directly which features were used. We could in the future embed metadata (like a local ref or file listing the features included). For now, we will implement a best-effort: \- If the overlay was built by profile, user probably used \--overlay so they know what’s in it. \- For sentinel enforcement, the safe route is to always apply global sentinels, and apply any feature-specific sentinels for *all* features by default (which is what current guard would effectively do if we naïvely merged all). But that could flag things irrelevant to this overlay.

Perhaps we add an option \--features X,Y to forked guard to tell guard “treat this overlay as containing features X,Y” – but this complicates usage. Instead, we can infer by examining the patch commits present in the overlay branch: \- List the patch branch names that were cherry-picked. We can get this from the build log or by diffing trunk vs overlay and matching commits to patch branch tips. \- The build log has each patch and how many commits applied. If we logged that, guard could read .forked/logs/forked-build.log (the last entry for that overlay) to find the feature list. This is feasible.

For simplicity in implementation, we might initially just merge *all* feature-level sentinel patterns globally (since if the overlay didn’t include that feature, those files likely didn’t change – though if they did via another feature, perhaps a false violation might appear). However, since the design specifically calls out feature-scoped sentinel to reduce noise, we should implement it properly: \- Determine active features: one quick method – for each feature in config, check if at least one patch from that feature is present in the overlay branch’s history (since last sync). We can do git log \--oneline trunk..overlay and see which patch branch names appear in commit messages (if commits maintain original branch info in message or some pattern). Alternatively, if we enforce that patch commits are always from their patch branches, maybe the branch name is not in commit messages though. \- We might simply decide that if the overlay was built with \--features or \--overlay, the user knows which features, and if built with all patches, then all features count. \- For now, assume overlay is full (features \= all) or partial (in which case user likely used features flag and thus knows they only care about those sentinel rules).

Implementation: merge feature sentinels conditionally: \- Start with global sentinel dict. \- For each feature in config.features: \* If none of that feature’s patch branches are in patches.order selection we built, skip (but since guard runs after build, we need the selection it was built with). \* If yes (meaning feature’s patches were applied), then for each sentinel pattern under that feature, add it to a copy of global sentinel patterns for checking. \* We ensure no duplicates and maintain the separation of must\_match vs must\_diverge lists. \- Then run the existing guard checks on these combined patterns.

The guard output JSON can include a new section indicating from which feature a sentinel violation came, but we might just rely on our separate feature risk summary to convey that.

* **Both-touched focusing:** The guard already calculates both\_touched by diffing trunk..overlay. To scope it, we can post-process the list of both\_touched files:

* Identify which files in both\_touched were touched by the features in question. If we had mapping of file \-\> feature from the build (like conflict bundler has patch-\>feature mapping), we could do similar: for each file in both\_touched, check which patch branch contributed changes to that file. This could be done by analyzing the overlay’s commits: find the commit(s) that last changed that file in the overlay’s history and see which patch branch that commit came from. Potentially heavy but doable using git log.

* Simpler: since in a partial build only some patches were applied, both\_touched inherently only arises from those patches. If overlay is partial, maybe treat all both\_touched as relevant. The design though implies maybe still showing if trunk changed a file that we didn’t include via a patch (so not in overlay, the file might differ if upstream changed it but since we had no patch, overlay has upstream version, then it’s not actually differing – so no conflict).

* Possibly they want to highlight if some upstream changes didn’t get fork changes because feature not included, etc. But it says “optionally show rest of repo”.

Implementation: we can simply split the both\_touched list into two: those files that are within directories of interest to the selected features (for example, feature’s patches often operate in certain folders), and the rest. But to be safe, we can list them all but maybe mark with feature tags in the JSON.

We will implement a basic grouping: using the mapping of patch-\>feature, and using git diff \--name-only trunk...overlay to get changed files, we can guess: \- If a file path matches any pattern of sentinel for a feature or lies in a path a feature touches (not easily known), we skip this for now. \- Instead, we will produce the same list but in the JSON risk summary group them by feature as described. That inherently focuses on per-feature issues, which covers the spirit.

In summary, implementation for guard changes is mostly about data grouping and using existing diff logic with extended patterns. The guard’s internal logic to compute sentinel violations and both\_touched counts remains robust, we are layering additional context on top of it.

### Logging and Error Handling

We will maintain the current approach to logging and error reporting:

* **Structured Logs:** The CLI already appends JSON logs for build and guard operations for traceability[\[79\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L276-L284). We will continue to log key events. For example:

* In the build log entry, add fields for overlay\_profile (if \--overlay was used) and features list (if \--features was used) for that build. This will record how the overlay was composed.

* If a conflict occurred, log an event with the patch that caused it and the fact that a bundle was emitted (with file path). We might also note if bias-continue was attempted and how many conflicts were auto-resolved vs remained.

* In the guard log, if we implement feature grouping, we can add a summary like violations\_by\_feature: {featureX: 1, featureY: 0, ...} for quick reference.

These logs remain in .forked/logs/ and are append-only JSON lines; we’ll preserve this format and extend it as needed.

* **User-facing Messages:** The CLI will remain relatively quiet unless an action is needed or an error occurs (following current style). On successful operations we often just print a short summary (e.g., build prints patch summary, guard prints “N violations” if any in warn mode). We will ensure:

* forked feature create prints the created branch names and reminds to update forked.yml (or mentions it auto-updated it).

* forked feature status prints the tree of features and slices.

* When a conflict bundle is generated, print a one-liner: e.g. “Merge conflicts detected. Written conflict bundle to .forked/conflicts/\<id\>.json (exit code 10).” This both informs the user and confirms the action for logs.

* If \--on-conflict-exec is used, we will likely stream the output of the external command to the console so the user can see what the tool did (and any errors from it).

* In all cases, avoid lengthy verbose text; rely on JSON for details. The user-facing text is just to guide or indicate success/failure.

* **Error Handling & Codes:** We covered exit codes above. Implementation will ensure to sys.exit(code) appropriately or throw Typer Exit(code) exceptions. Notable error conditions and handling:

* Missing or invalid config (still exit 3 with a clear message, e.g. “forked.yml not found or invalid”).

* Unknown feature or overlay name provided: treat as config error (exit 3\) with message “Feature X not defined in forked.yml” or “Overlay profile Y not defined”.

* Running forked build \--overlay or \--features with an empty selection (e.g. the feature has zero patches) – this is a no-op build; we might warn and do nothing (exit 0\) or treat as error if that indicates misconfig.

* forked feature create could encounter Git errors (e.g. branch create fails), we will catch those and surface as error messages.

* If any command is invoked in a wrong context (e.g. not in a Git repo or trunk missing), we continue to handle as in MVP (likely exit 4 or 3 with message).

* We will also guard against improper usage combinations, like \--overlay and \--features both given (though we allow combining, we should allow it as additive; if there’s any ambiguity, we’ll document how they combine rather than forbid it).

In general, the CLI will remain non-interactive and fail early with clear messaging if something is wrong, to be CI-friendly. We’ll add tests for common error cases to ensure the exit codes are correct.

* **Continuing .forked/ Directory Conventions:** The .forked dir remains the central place for all outputs. We won’t create any config or state elsewhere. The new conflict files fit into this structure neatly[\[80\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=This%20dovetails%20with%20existing%20build,namespace). If any new subdirectories are created (e.g. for blobs), we ensure they are under .forked and add them to the gitignore if necessary (though .forked/\* is likely already ignored). We will encourage users to periodically clean the .forked folder (with a planned forked clean command in future perhaps) to remove old worktrees and logs to save space.

* **Logging Library:** Currently, the CLI likely prints directly or uses simple logging. For consistency, we might continue to just print messages and use the JSON log files for structured data. We won’t introduce a complex logging framework at this time – the existing approach suffices for an MVP product.

* **Parallel Execution Considerations:** If multiple Forked commands are run concurrently (rare in CI, but possible if user manually does so), conflict could arise writing to the same log or report. However, since typically one would not run two builds at once on the same repo, we assume sequential usage. Our logging writes append with file lock (the OS should handle appends atomic enough for our use). We mention this just to note no new issues are introduced.

By adhering to these logging and error conventions, we ensure any new complexity (features or conflict handling) remains transparent and debuggable, in line with the existing tool’s philosophy of traceable automation.

## Example Workflows

To illustrate how these enhancements come together, consider a developer’s typical workflow using Forked CLI:

1. **Creating a Feature Slice Stack:** Suppose a developer wants to implement a new feature “Payments v2” composed of several small patches. They run:\<br\> bash forked feature create payments\_v2 \--slices 3\<br\> This creates branches patch/payments\_v2/01-\*, /02-\*, /03-\* and updates forked.yml accordingly[\[15\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=create%20scaffolded%20slices%20forked%20feature,makes%20patch%2Fpayments_v2%2F%7B01%2C02%2C03). The developer now has an empty 3-patch stack to work in. They proceed to code:

2. They make changes on patch/payments\_v2/01-schema, commit (maybe “Add payments schema”).

3. Then on patch/payments\_v2/02-repo, commit (“Implement repository layer for payments”).

4. Then on patch/payments\_v2/03-api, commit (“Expose payments API”). Each slice is a focused change. They periodically run forked status or forked feature status to see that their feature branches are ahead of trunk and by how many commits.

5. **Building a Feature Overlay for Testing:** Once the patches are ready, the developer builds an overlay with just this new feature to test it in isolation:\<br\> bash forked build \--features payments\_v2 \--id payments-dev\<br\> This resolves the patches for feature *payments\_v2* (the three slices)[\[3\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Under%20the%20hood%2C%20), cherry-picks them onto the latest trunk (creating branch overlay/payments-dev). If some patches had already been merged upstream, Forked would skip them, but let’s assume these are all new changes. The \--id payments-dev gives a friendly name to the overlay. The build completes, creating a worktree for overlay/payments-dev under .forked/worktrees/ (since worktrees are enabled by default)[\[81\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L100-L108). The CLI prints a summary of applied patches and notes if any were skipped or had conflicts auto-resolved. The developer can now run tests on the overlay/payments-dev code.

6. **Guarding the Overlay:** Before considering this feature ready, the developer checks it against policies:\<br\> bash forked guard \--overlay overlay/payments-dev \--mode warn\<br\> Running in warn mode ensures it won’t block, but will report any issues. The guard inspects only the changes introduced by *payments\_v2*: it knows to focus on those slices[\[23\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Guards%20that%20understand%20features%20,noise%2C%20more%20signal). Suppose the guard finds that api/contracts/payment.yaml was modified by this feature, but according to policy it should not diverge from upstream (a sentinel violation). In the JSON report, this is recorded under violations.sentinels.must\_match\_upstream and it’s also attributed to payments\_v2 in a feature breakdown section. The CLI exits 0 (warn mode doesn’t fail the build) but the developer sees the warning in output or can open .forked/report.json for details[\[82\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L244-L253)[\[83\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L254-L262). Realizing this might be intentional (perhaps the feature *needs* to update the contract), the developer can decide to adjust the policy: for example, add that path under features.payments\_v2.sentinels.must\_match\_upstream to enforce it, or if it’s allowed, move it to must\_diverge. In this case, assume it was actually a violation they need to fix – they update the code or consult with the team.

7. **Syncing with Upstream:** While working on the feature, upstream releases new changes. The developer runs:\<br\> bash forked sync\<br\> This fetches upstream and fast-forwards trunk, then attempts to rebase each patch in patches.order onto the new trunk[\[78\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Upstream%20Sync%20,4). As it rebases the payments\_v2 slices, imagine a conflict occurs (upstream changed something in src/service.py that patch 02-repo also modifies). Normally, Forked would stop and say “Resolve conflicts in patch/payments\_v2/02-repo and run git rebase \--continue.” Now, however, because we have conflict bundling, the CLI was invoked (perhaps by CI or manually) with forked sync \--emit-conflicts .forked/conflict-sync.json \--on-conflict stop. It detects the conflict, writes .forked/conflict-sync.json, and exits with code 10 instead of leaving the repo in limbo. The developer opens the JSON and sees exactly which files are conflicted and that the recommended resolution for src/service.py is “ours” (maybe upstream’s change should win, as indicated by a sentinel)[\[46\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20)[\[44\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,is%20index%20stage%20for%20base). They follow the resume instructions in the JSON: open a mergetool for deeper inspection (using the provided commands.open\_mergetool), accept the upstream version as suggested (accept\_ours command) and then run git rebase \--continue[\[7\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,19%2Fsrc_service.py%2F%22)[\[84\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%22resume%22%3A%20%7B%20%22continue%22%3A%20%22git%20cherry,19%22%20%7D). The rebase completes. They then likely re-run forked build \--features payments\_v2 to test the feature against the new trunk.

8. **Composing Multiple Features:** Now assume another feature “Branding” exists (which has its own patch branches for changing UI). That feature might be done by another team, but the developer wants to test integration of *payments\_v2* and *branding* together. The config has an overlay profile “dev” that includes both. They run:\<br\> bash forked build \--overlay dev\<br\> This uses overlays.dev.features list from config to gather patches[\[2\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=build%20overlays%20by%20profile%20or,exclude%20patch%3Apatch%2Fexperimental). Let’s say “branding” has two patches. Forked resolves the list: (payments\_v2’s three patches \+ branding’s two patches, in the global order). It then cherry-picks all five patch series onto trunk, creating (or updating) branch overlay/dev. If any conflicts occur between the two feature sets (or with upstream), the same conflict bundling applies. For instance, if branding and payments\_v2 both touched README.md, a conflict arises; the CLI outputs .forked/conflicts.json and stops. The developer could run forked build \--overlay dev \--on-conflict bias-continue to let path biases handle it if such conflicts were anticipated, but assume none or trivial ones that auto-merge. The build succeeds, overlay/dev now has combined changes.

9. **Guard and Publish:** The developer now runs a final guard on the full “dev” overlay in blocking mode to ensure it meets all policies:\<br\> bash forked guard \--overlay overlay/dev \--mode block\<br\> The guard checks both features’ changes together. If there are any policy violations, it exits 2 to indicate a failure[\[65\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L217-L224). Let’s say everything passes (exit 0). The developer then proceeds to publish this overlay as a release candidate:\<br\> bash forked publish \--overlay overlay/dev \--tag v2.0.0-rc1 \--push\<br\> This tags the overlay/dev commit as v2.0.0-rc1 and pushes the tag and branch to the origin remote[\[85\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L230-L239). Now the forked repository on the server has a branch/tag containing the integrated feature. Alternatively, if only one feature was ready, they could choose to build and publish an overlay with just that feature’s patches (that’s where the per-feature guard summary helps decide). The workflow demonstrates flexibility: features can be developed independently but tested and released in combinations with minimal friction.

Throughout this scenario, the team benefits from the **machine-readable outputs** at each step: \- Guard reports (report.json) for each overlay build, to be consumed by CI or to compare before/after upstream sync. \- Conflict bundles (conflicts.json) whenever manual intervention is needed, so even those steps can be guided or automated by tools. \- Build logs (forked-build.log) capturing the sequence of applied patches and any auto-resolutions, for auditing. \- Status commands to quickly see where patches stand relative to upstream.

## Testing Strategy

Ensuring reliability and correctness of these new features is crucial. We will implement a comprehensive testing approach, including unit tests, integration tests with sample repositories, and continuous integration (CI) pipeline setup.

**Unit Tests:** \- *Patch Resolver:* Write unit tests for the resolve\_patches function that combine flags. Test scenarios: \- Only \--features specified (returns exactly that feature’s patches in order). \- Only \--overlay specified (returns union of those features’ patches). \- Combination of \--overlay \+ \--exclude (profile minus something). \- Combination of \--features \+ \--include (specific additions). \- Overlapping includes/excludes to ensure de-duplication works. \- Edge cases like specifying a feature that has no patches or an unknown name (should error). \- *Feature Sentinel Merging:* Create dummy config objects with global and feature-level sentinel patterns. Simulate an overlay with certain features and ensure the merged list is correct. Also test that a file path that should trigger a feature sentinel does get caught and one for a non-included feature does not. \- *Precedence Logic:* Test the conflict precedence function: \- Feed it scenarios: e.g. file path that matches a must\_match pattern \-\> expect recommended “ours”[\[41\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20). \- Path that matches path\_bias.theirs and no sentinel \-\> expect recommended “theirs”[\[43\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=2.%20Else%20). \- Both sentinel and bias (should never truly conflict because if sentinel matches we ignore bias). \- No matches \-\> recommended “none”. Each with correct sentinel/path\_bias flags set. This ensures the logic follows the specified priority[\[46\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20)[\[47\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=3.%20Else%20). \- *Conflict Bundle JSON formation:* We can simulate a conflict state without an actual Git operation by stubbing the ls-files \-u output and blob contents: \- Prepare fake OIDs and contents for a known small conflict (e.g. base content “hello”, ours “hello world”, theirs “hello folks”). Run our diff generation function and ensure the diffs appear in the JSON and recommended resolution is as expected if we set up sentinel/path\_bias to prefer one side. \- Verify that commands strings are correct and JSON serializes properly (no unserializable types). \- If possible, use a temporary git repo in tests: We could create a minimal repository in a tempdir and intentionally create a conflict (e.g., create a trunk commit, a patch commit that conflicts, then simulate a cherry-pick stopping). Then run an internal function to gather the conflict bundle. This would be an end-to-end test for bundle generation, comparing the output JSON to an expected structure (we might use a “golden file” approach where we have a sample JSON we expect and diff against it, allowing minor variations like commit hashes).

* *CLI Option Combinations:* Test that Typer wiring accepts the new flags and subcommands:

* e.g. invoke forked build with incompatible options (if any) and ensure it errors or handles them gracefully.

* forked feature create with various values (especially ensuring it properly writes config – we might simulate by using a temp config file).

* Ensure forked feature status doesn’t crash on edge cases (like no features defined, or a feature with no patches, etc).

**Integration Tests:** We will set up a suite of integration tests using a real Git repository scenario (possibly leveraging the existing scripts/setup-demo-repo.sh which creates a sandbox fork environment[\[86\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L79-L88)). For example: \- Start with the demo repo (which has a couple of patch branches and some sentinel settings). Convert it to use features: \- Manually edit or have the test create a forked.yml that defines a feature grouping those patches. \- Run forked build \--overlay dev (assuming we define dev profile in the test config). Verify that it creates the expected overlay branch and worktree. Check that the commits in the overlay match the union of patches. \- Introduce a deliberate conflict in the demo repo scenario: e.g., modify upstream and a patch to conflict. Then run forked build \--emit-conflicts and verify the JSON file exists and has the correct fields (not necessarily exact content, but keys and high-level structure). Possibly parse it in the test to confirm context.mode \== "build", etc. \- Run forked guard on a partial overlay and verify the JSON report indicates only intended violations. \- Use the integration tests to simulate a full workflow: \- Create a new feature via CLI in the test repo, add a commit to each slice, run forked build \--features X, ensure it succeeds. \- Run forked sync after making an upstream change causing conflict, ensure it produces conflict JSON and exits 10\. \- Resolve the conflict (in test, maybe just accept ours via git commands), continue the sync, verify that patch was rebased. \- Then do a combined build of multiple features, guard it, and maybe test forked publish (though perhaps in a dry-run way, as pushing in a test might require a dummy remote).

We can automate these in a CI environment by using containerized Git and the repository files.

**Continuous Integration Setup:** \- We will configure a CI (e.g., GitHub Actions or GitLab CI) to run our test suite on each push. This ensures that as we develop these features, we don’t break existing functionality. \- CI will run linting (if any), all unit tests, and integration tests. We need to ensure a Git environment with Git \>= 2.31 is available for tests (to mirror user requirements). \- We will also add a job to build and install the CLI (pip install) and run a quick smoke test of the commands – basically what our current sanity\_check.md or demo does – to ensure packaging and entry points are correct.

**CI Integration Examples for Users:** We will also document how *users* can integrate Forked into their CI: \- For guarding policies: a CI pipeline (e.g., GitHub Actions) could have a step:

\- name: Run Forked Guard  
  run: forked build \--id ci-$GITHUB\_RUN\_ID && forked guard \--overlay overlay/ci-$GITHUB\_RUN\_ID \--mode block

This ensures that for each CI run, we build the full overlay and guard it. If forked guard exits 2 (policy fail), the CI job will fail, preventing promotion of that build. The JSON report can be uploaded as an artifact or parsed to give a nice comment on the PR (highlighting which files violate policy). We will provide an example in documentation. \- For syncing forks: an organization might set up a daily cron job to run forked sync on their fork. We’ll suggest using \--emit-conflicts so that if that job fails due to conflicts, it can automatically create an issue or notification attaching the conflict bundle. This way, maintainers get all the info to resolve it. For instance, a GitHub Action could catch exit code 10 and then post the contents of .forked/conflict-sync.json to a new GitHub issue for developers to address. We can include a snippet in the README or docs for how to do this, since the JSON is structured and possibly too large for direct issue text, one might link it or attach as artifact. \- For using AI assistance: We could demonstrate a local script or action that uses \--on-conflict exec. E.g., an Action that triggers an AI service on conflict. This might be more experimental, but our design allows it. We’ll provide the example from the design doc (which shows how to call a hypothetical my-ai-fixer on conflict).

**Manual Testing and Real Repos:** Beyond automated tests, we plan to test the enhanced CLI on a real fork scenario (possibly a fork of a known project) to ensure the workflow is smooth. We’ll test: \- Upgrading an existing forked.yml to include features and making sure older commands still run. \- Running forked feature create in a live repo and then doing the entire sync-\>build-\>guard cycle multiple times. \- Performance checks: The added overhead (parsing index, writing JSON) is minimal for small conflicts, but we’ll test on a scenario with, say, 100 conflict files to see that it’s still manageable. Git’s performance should handle that, but we might optimize by not diffing overly large files or by streaming output efficiently.

Our CI will guard against regressions. We’ll also incorporate the **demo repository** in tests or as a CI step: using the provided setup-demo-repo.sh to generate a sandbox and then running a script that exercises feature creation, building, guarding, syncing on that sandbox, comparing outputs to expected results. This serves as an end-to-end test.

## Continuous Integration & Release

We will integrate these testing practices into the development lifecycle. Each new feature will come with corresponding tests. We can also set up **pre-merge checks** that run forked guard on the Forked CLI’s own repository to ensure we’re not violating our own policies (for example, we might dogfood a sentinel that ensures our CLI output examples in docs remain updated).

When all tests pass and we are satisfied with the stability, we’ll update the documentation (README and help texts) to reflect these new commands and options. We will likely bump the CLI version (to, say, 1.1.0) for a feature release. A CI job can package and publish the updated package (once we decide to release to PyPI, etc.).

Finally, we will prepare a section in the README or an ADR (architecture decision record) summarizing these enhancements (especially the conflict bundle feature) so that users understand the reasoning and usage. This fulfills the plan to improve both the tool and its usability.

## CI Integration Example (Summary)

For clarity, here’s an example GitHub Actions snippet showcasing how one might use the expanded Forked CLI in a pipeline:

jobs:  
  build-and-guard:  
    runs-on: ubuntu-latest  
    steps:  
      \- uses: actions/checkout@v3  
      \- name: Install Forked CLI  
        run: pip install forked-cli  \# assuming published  
      \- name: Sync fork with upstream  
        run: |  
          forked sync \--emit-conflicts .forked/conflict-sync.json || |  
          if \[ $? \-eq 10 \]; then   
            echo "Upstream conflict detected. See conflict bundle artifact."   
            exit 1   
          fi  
      \- name: Build overlay  
        run: forked build \--overlay dev \--id ci-${{ github.run\_id }}  
      \- name: Guard overlay  
        run: forked guard \--overlay overlay/ci-${{ github.run\_id }} \--mode block  
      \- name: Upload guard report  
        if: failure()  
        uses: actions/upload-artifact@v2  
        with:  
          name: guard-report  
          path: .forked/report.json  
      \- name: Upload conflict bundle  
        if: failure() && exists('.forked/conflict-sync.json')  
        uses: actions/upload-artifact@v2  
        with:  
          name: conflict-bundle  
          path: .forked/conflict-sync.json

In the above, we attempt forked sync and handle the special exit 10 for conflicts, then build and guard an overlay for the dev profile and use the exit code of guard to pass/fail the job. Artifacts are uploaded for inspection when things go wrong (guard violations or a sync conflict). This is just one illustration; teams can adapt it to their CI system of choice. The key point is that with deterministic exit codes and machine-readable outputs, Forked CLI can be tightly integrated into CI/CD to automate fork maintenance and policy enforcement[\[87\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,code%20keeps%20CI%20logic%20clean).

---

With this implementation plan, we cover all requested enhancements – feature slicing, selective builds, conflict bundle generation, and improved ergonomics – while leveraging the existing design of Forked CLI. The plan emphasizes minimal state (everything derives from Git and YAML) and transparency (logs and JSON for every action), aligning with the project’s goals[\[88\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,is%20derivable%20from%20branches)[\[89\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=%60forked%20sync%60.%20,forked.yml). By following this plan, we will significantly improve the flexibility and safety of managing a fork as a product, making the next release of Forked CLI a robust tool ready for real-world, continuous use. [\[90\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Overall%2C%20the%20MVP%20covers%20the,of%20a%20%E2%80%9Cmanaged%20fork%E2%80%9D%20CLI)[\[91\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=functions%2C%20it%20feels%20more%20like,nets%20that%20a%20true%20minimal)

## Tech Evolution: Rust Path

While Python remains the reference implementation for v1.1, high-cost operations (guard parsing, large diff analysis, symbol inspection) are candidates for a future Rust sidecar or full re-write. The migration path:

- Maintain stable CLI contracts (flags, exit codes, JSON schemas) so Rust binaries can be drop-in replacements.
- Prototype a `forked-guard-symbol` micro-binary that emits `{file → symbols}` JSON to speed symbol-aware policies.
- Collect performance telemetry after v1.1 to prioritise which commands benefit most from Rust.

This note signals intent without committing to immediate changes; all documentation should reiterate that Python is still supported long-term.

## Work Items (Addendum v1.1)

| ID | Scope | Summary |
|----|-------|---------|
| A | Guard | Implement policy override trailers/notes, update `report_version` to 2, and add override tests. |
| B | Status | Deliver `forked status --json` with provenance integration and overlay window controls. |
| C | Clean | Ship `forked clean` with dry-run/confirm, retention, and safety rails. |
| D | Build | Persist selection metadata to logs/notes and expose features in guard/report. |
| E | Build | Add `--skip-upstream-equivalents`, logging skipped commits per patch. |
| F | Conflict | Upgrade bundle writer to schema v2 (binary/large files, waves, shell metadata). |
| G | Sync | Default stop-on-conflict; add `--auto-continue` and bias logging for sync rebases. |

Tasks in the sprint and backlog map directly to these items.

## Acceptance Gates

- Complete items A–G with documentation and tests.
- Run end-to-end smoke tests on at least two real forks covering init → sync → build (features/overlays, skip no-ops) → guard (`require-override`) → conflict bundles → clean.
- Publish updated schemas (`report_version >= 2`, `schema_version >= 2`) and README sections for overrides, status JSON, clean, skip no-ops, sync policy, and conflict bundle usage.
- Share CI samples for guard enforcement and conflict bundle artefacts.

---

[\[1\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Status%20and%20Publish%3A%20The%20CLI,fork%E2%80%99s%20repository%20for%20others%20to) [\[19\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=The%20overlay%20branch%20represents%20your,build.log%29%20for%20auditability%5B10%5D%5B11) [\[25\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=The%20guard%20outputs%20a%20JSON,16) [\[30\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Automate%20Where%20Safe%3A%20Continue%20to,it%20could%20speed%20up%20updates) [\[33\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Sentinels%3A%20You%20can%20configure%20path,16) [\[35\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=automatically%20skips%20patches%20that%20are,build.log%29%20for%20auditability%5B10%5D%5B11) [\[64\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=The%20guard%20outputs%20a%20JSON,16) [\[66\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Guidance%20on%20Conflicts%3A%20Ensure%20that,best%20practices%20for%20resolving%20those) [\[67\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=invoked%20with%20,build.log%29%20for%20auditability%5B10%5D%5B11) [\[78\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Upstream%20Sync%20,4) [\[90\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=Overall%2C%20the%20MVP%20covers%20the,of%20a%20%E2%80%9Cmanaged%20fork%E2%80%9D%20CLI) [\[91\]](file://file-SRFsfRqcrvLd9NxYoz4vgP#:~:text=functions%2C%20it%20feels%20more%20like,nets%20that%20a%20true%20minimal) Current MVP Status and Capabilities.docx

[file://file-SRFsfRqcrvLd9NxYoz4vgP](file://file-SRFsfRqcrvLd9NxYoz4vgP)

[\[2\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=build%20overlays%20by%20profile%20or,exclude%20patch%3Apatch%2Fexperimental) [\[3\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Under%20the%20hood%2C%20) [\[4\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,global%20order%20selected%20%3D%20set) [\[5\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=def%20add,add%28p%29%20if%20include) [\[14\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,makes%20patch%2Fpayments_v2%2F%7B01%2C02%2C03) [\[15\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=create%20scaffolded%20slices%20forked%20feature,makes%20patch%2Fpayments_v2%2F%7B01%2C02%2C03) [\[16\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Notes%3A) [\[17\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=features%3A%20payments_v2%3A%20patches%3A%20,logo) [\[18\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=status%20by%20feature%20forked%20feature,SHAs) [\[20\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=%2A%20%2A%2AScope%20both,globs%2C%20merged%20with%20global%20ones) [\[21\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=payments_v2%3A%20sentinels%3A%20must_match_upstream%3A%20%5B,so%20you%20can%20decide%20%E2%80%9Cship) [\[22\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=features%3A%20payments_v2%3A%20sentinels%3A%20must_match_upstream%3A%20%5B,so%20you%20can%20decide%20%E2%80%9Cship) [\[23\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Guards%20that%20understand%20features%20,noise%2C%20more%20signal) [\[24\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=must_match_upstream%3A%20%5B,%E2%80%9Cship%20branding%20now%2C%20hold%20payments_v2%E2%80%9D) [\[31\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=%2A%20%2A%2ABranch%20naming%2A%2A%3A%20%60patch%2F%3Cfeature%3E%2F%3CNN%3E,subsets%20from%20that%20order) [\[32\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=overlays%3A%20dev%3A%20features%3A%20,only%3A%20features%3A%20%5Bbranding%5D) [\[34\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,so%20you%20can%20decide%20%E2%80%9Cship) [\[36\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Keep%20your%20existing%20,overlay%20profiles) [\[39\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=Add%20fields%3A) [\[40\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,) [\[55\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=%60%60%60json%20%7B%20,ours) [\[56\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,continue%22) [\[69\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,global%20order%20selected%20%3D%20set) [\[70\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=for%20f%20in%20cfg.overlays%5Boverlay%5D%5B,set%28exclude) [\[71\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=def%20resolve_patches,global%20order%20selected%20%3D%20set) [\[72\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=if%20p%20in%20order%3A%20selected,add%28p%29%20if%20include) [\[73\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=def%20add,add%28p) [\[74\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=for%20p%20in%20cfg.features%5Bf%5D%5B,set%28exclude) [\[75\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=order%20%3D%20cfg.patches.order%5B%3A%5D%20%20,global%20order%20selected%20%3D%20set) [\[88\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=,is%20derivable%20from%20branches) [\[89\]](file://file-T6VcbsuJugGtCSiYVrjySk#:~:text=%60forked%20sync%60.%20,forked.yml) Untitled-2.md

[file://file-T6VcbsuJugGtCSiYVrjySk](file://file-T6VcbsuJugGtCSiYVrjySk)

[\[6\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%2A%20%60,conflict) [\[7\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,19%2Fsrc_service.py%2F%22) [\[8\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%2A%20%60) [\[9\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=) [\[10\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,with%20the%20JSON%20path) [\[11\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,with%20the%20JSON%20path) [\[12\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=) [\[28\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=Also%20do%20this%20for%20,sync) [\[29\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,base%28trunk%2C%20patch_commit%20or%20tip) [\[37\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,base%28trunk%2C%20patch_commit%20or%20tip) [\[38\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%22patch_branch%22%3A%20%22patch%2Ffeature,base%28trunk%2C%20patch_commit%20or%20tip) [\[41\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20) [\[42\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,THEIRS%20%28patch) [\[43\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=2.%20Else%20) [\[44\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,is%20index%20stage%20for%20base) [\[45\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,matched%20sentinel%20must_match_upstream) [\[46\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=1.%20) [\[47\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=3.%20Else%20) [\[48\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,) [\[49\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,based%20agents) [\[50\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%22diffs%22%3A%20%7B%20%22base_vs_ours_unified%22%3A%20%22%40%40%20,py%27%20%26%26%20git%20add) [\[51\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%22base_vs_ours_unified%22%3A%20%22%40%40%20,py) [\[52\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,ours_vs_theirs_unified) [\[53\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,based%20agents) [\[54\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%5D%2C%20,19%22%20%7D) [\[57\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,containing%20everything%20an%20agent%20needs) [\[58\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,%28accept%20ours%2Ftheirs%2C%20continue%2Fabort) [\[59\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=This%20complements%20your%20existing%20guard,%2B%20build%20logs) [\[62\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=This%20dovetails%20with%20existing%20build,namespace) [\[63\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=) [\[76\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,OIDs) [\[77\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=This%20mirrors%20how%20%60,for%20agents) [\[80\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=This%20dovetails%20with%20existing%20build,namespace) [\[84\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=%22resume%22%3A%20%7B%20%22continue%22%3A%20%22git%20cherry,19%22%20%7D) [\[87\]](file://file-MbZqnFviFqwCurtd5mjEL9#:~:text=,code%20keeps%20CI%20logic%20clean) Untitled-1.md

[file://file-MbZqnFviFqwCurtd5mjEL9](file://file-MbZqnFviFqwCurtd5mjEL9)

[\[13\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L194-L201) [\[26\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L200-L208) [\[27\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L242-L250) [\[60\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L185-L193) [\[61\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L193-L201) [\[65\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L217-L224) [\[68\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L280-L283) [\[79\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L276-L284) [\[81\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L100-L108) [\[82\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L244-L253) [\[83\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L254-L262) [\[85\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L230-L239) [\[86\]](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md#L79-L88) README.md

[https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md](https://github.com/Spenquatch/forked/blob/013a2380f81f381f324e7c9a603d25c1e221bd5b/README.md)
