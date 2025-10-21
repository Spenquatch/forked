"""Overlay build workflows."""

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import typer
from pathspec import PathSpec

from . import gitutil as g
from .config import Config
from .conflicts import ConflictContext, apply_recommendations, create_conflict_writer
from .resolver import ResolvedSelection


def _conflict_paths(cwd: str | None = None) -> list[str]:
    out = g.run(["status", "--porcelain"], cwd=cwd).stdout.splitlines()
    return [line.split()[-1] for line in out if line.startswith(("U", "AA", "DD", "DU", "UD"))]


def _apply_path_bias(cfg: Config, cwd: str | None = None) -> bool:
    ours = PathSpec.from_lines("gitwildmatch", cfg.path_bias.ours or [])
    theirs = PathSpec.from_lines("gitwildmatch", cfg.path_bias.theirs or [])
    conflicted = _conflict_paths(cwd)
    applied = False
    for path in conflicted:
        if ours.match_file(path):
            g.run(["checkout", "--ours", "--", path], cwd=cwd)
            g.run(["add", path], cwd=cwd)
            applied = True
        elif theirs.match_file(path):
            g.run(["checkout", "--theirs", "--", path], cwd=cwd)
            g.run(["add", path], cwd=cwd)
            applied = True
    return applied


WINDOWS_ABS_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")


def _looks_like_windows_absolute(raw: str) -> bool:
    return bool(WINDOWS_ABS_PATTERN.match(raw))


def _resolve_worktree_dir(cfg: Config, overlay_id: str) -> Path:
    root_override = os.environ.get("FORKED_WORKTREES_DIR")
    raw_root = root_override or cfg.worktree.root

    if _looks_like_windows_absolute(raw_root):
        if os.name != "nt":
            typer.echo(
                "[build] Provided worktree root looks like a Windows path but the current platform "
                "is POSIX. Set $FORKED_WORKTREES_DIR to an absolute POSIX path instead."
            )
            raise typer.Exit(code=4)

    repo = g.repo_root()
    base_root = Path(raw_root)
    if not base_root.is_absolute():
        base_root = (repo / base_root).resolve()
    else:
        base_root = base_root.resolve()
    candidate = base_root / overlay_id

    target = candidate
    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        typer.echo(
            f"[build] Worktree directory '{target}' already exists; suffixing. "
            "Run 'git worktree prune' to clean up stale entries."
        )
        suffix = 1
        while True:
            alt = parent / f"{target.name}-{suffix}"
            if not alt.exists():
                target = alt
                break
            suffix += 1
        target.parent.mkdir(parents=True, exist_ok=True)

    return target


def _rev_list_range(base: str, tip: str) -> list[str]:
    revs = g.run(["rev-list", "--reverse", f"{base}..{tip}"]).stdout.splitlines()
    return [rev for rev in revs if rev]


def _upstream_equivalent_commits(trunk: str, branch: str) -> set[str]:
    """Return commit SHAs already contained in the trunk branch."""
    cp = g.run(["cherry", trunk, branch], check=False)
    if cp.returncode != 0:
        typer.echo(
            f"[build] Failed to compute upstream-equivalent commits for {branch}: {cp.stderr.strip()}",
            err=True,
        )
        return set()
    skip: set[str] = set()
    for line in cp.stdout.splitlines():
        if not line.startswith("- "):
            continue
        parts = line.split()
        if len(parts) >= 2:
            skip.add(parts[1])
    return skip


def build_overlay(
    cfg: Config,
    overlay_id: str,
    selection: ResolvedSelection | None = None,
    *,
    use_worktree: bool = True,
    auto_continue: bool = False,
    skip_upstream_equivalents: bool = False,
    write_git_note: bool = True,
    emit_conflicts: str | None = None,
    conflict_blobs_dir: str | None = None,
    on_conflict: str = "stop",
    on_conflict_exec: str | None = None,
) -> tuple[str, Path, dict[str, Any]]:
    conflict_mode = (on_conflict or "stop").lower()
    if conflict_mode not in {"stop", "bias", "exec"}:
        raise typer.BadParameter(f"Unsupported --on-conflict mode '{on_conflict}'.")
    if auto_continue and conflict_mode == "stop":
        conflict_mode = "bias"
    if conflict_mode == "exec" and not on_conflict_exec:
        raise typer.BadParameter("--on-conflict exec requires --on-conflict-exec command.")

    emit_option = emit_conflicts
    if conflict_mode in {"bias", "exec"} and emit_option is None:
        emit_option = "__AUTO__"

    blob_option = conflict_blobs_dir
    if blob_option == "__AUTO__":
        blob_option = "__AUTO__"

    conflict_writer = None
    repo = g.repo_root()

    g.run(["fetch", cfg.upstream.remote])
    prev_ref = g.current_ref()
    g.run(["checkout", "-B", cfg.branches.trunk, f"{cfg.upstream.remote}/{cfg.upstream.branch}"])

    if selection is None:
        selection = ResolvedSelection(
            patches=list(cfg.patches.order),
            active_features=[],
            overlay_profile=None,
            include=[],
            exclude=[],
            unmatched_include=[],
            unmatched_exclude=[],
            source="all",
            patch_feature_map={patch: [] for patch in cfg.patches.order},
        )

    overlay = f"{cfg.branches.overlay_prefix}{overlay_id}"
    wt_existing: Path | None = None
    if use_worktree and cfg.worktree.enabled:
        wt_existing = g.worktree_for_branch(overlay)
        if wt_existing and not wt_existing.exists():
            g.run(["worktree", "prune"])
            wt_existing = g.worktree_for_branch(overlay)

        if wt_existing:
            wt_path = wt_existing
            cwd = str(wt_path)
            g.run(["checkout", overlay], cwd=cwd)
            g.run(["reset", "--hard", cfg.branches.trunk], cwd=cwd)
        else:
            wt_path = _resolve_worktree_dir(cfg, overlay_id)
            g.run(["worktree", "add", "-B", overlay, str(wt_path), cfg.branches.trunk])
            cwd = str(wt_path)
    else:
        g.ensure_clean()
        g.run(["checkout", "-B", overlay, cfg.branches.trunk])
        wt_path = Path.cwd() / f".overlay-{overlay_id}"
        cwd = None

    selection_data = {
        "source": selection.source,
        "overlay_profile": selection.overlay_profile,
        "features": selection.active_features,
        "patches": selection.patches,
        "include": selection.include,
        "exclude": selection.exclude,
        "unmatched_include": selection.unmatched_include,
        "unmatched_exclude": selection.unmatched_exclude,
        "patch_feature_map": selection.patch_feature_map,
        "skip_upstream_equivalents": skip_upstream_equivalents,
    }

    def _quote_cli(value: str) -> str:
        if not value:
            return "''"
        if any(ch in value for ch in (" ", "'", '"')):
            return "'" + value.replace("'", "'\"'\"'") + "'"
        return value

    rebuild_tokens: list[str] = ["forked", "build", "--id", overlay_id]
    if selection.overlay_profile:
        rebuild_tokens.extend(["--overlay", selection.overlay_profile])
    elif selection.active_features:
        rebuild_tokens.extend(["--features", ",".join(selection.active_features)])
    for pattern in selection.include:
        rebuild_tokens.extend(["--include", pattern])
    for pattern in selection.exclude:
        rebuild_tokens.extend(["--exclude", pattern])
    if skip_upstream_equivalents:
        rebuild_tokens.append("--skip-upstream-equivalents")
    rebuild_tokens.extend(["--on-conflict", conflict_mode])
    rebuild_command = " ".join(_quote_cli(token) for token in rebuild_tokens)

    logs_dir = repo / ".forked" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    patch_summaries: list[dict] = []
    conflict_records: list[dict[str, Any]] = []
    bias_logs: list[dict[str, Any]] = []

    def log_build(status: str) -> dict[str, Any]:
        telemetry = {
            "event": "forked.build",
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overlay": overlay,
            "worktree": str(wt_path),
            "reused_worktree": bool(wt_existing),
            "patches": patch_summaries,
            "trunk": cfg.branches.trunk,
            "upstream": f"{cfg.upstream.remote}/{cfg.upstream.branch}",
            "selection": selection_data,
            "conflicts": conflict_records,
            "on_conflict": conflict_mode,
        }
        if bias_logs:
            telemetry["bias_actions"] = bias_logs
        log_path = logs_dir / "forked-build.log"
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(telemetry) + "\n")
        return telemetry

    for branch in selection.patches:
        base = g.merge_base(cfg.branches.trunk, branch)
        commits = _rev_list_range(base, branch)
        summary_entry = {
            "branch": branch,
            "commit_count": 0,
            "commits": [],
            "skipped_commits": [],
            "skipped_count": 0,
            "total_commits": len(commits),
        }
        summary_appended = False

        if not commits:
            typer.echo(f"[build] {branch} already contained in {cfg.branches.trunk}; skipping")
            summary_entry["status"] = "skipped"
            patch_summaries.append(summary_entry)
            continue

        skip_shas: set[str] = set()
        if skip_upstream_equivalents:
            skip_shas = _upstream_equivalent_commits(cfg.branches.trunk, branch)

        for sha in commits:
            summary = g.run(["show", "-s", "--format=%s", sha]).stdout.strip()
            if skip_shas and sha in skip_shas:
                summary_entry["skipped_commits"].append({"sha": sha, "summary": summary})
                summary_entry["skipped_count"] += 1
                continue

            cp = g.run(["cherry-pick", "-x", sha], cwd=cwd, check=False)
            if cp.returncode != 0:
                unmerged = g.run(["ls-files", "-u"], cwd=cwd).stdout.strip()
                has_conflicts = bool(unmerged)
                if not has_conflicts:
                    typer.echo(cp.stderr.strip())
                    summary_entry["status"] = "error"
                    if not summary_appended:
                        patch_summaries.append(summary_entry)
                        summary_appended = True
                    log_build("failed")
                    raise typer.Exit(code=cp.returncode or 1)
                if emit_option is None:
                    typer.echo(cp.stderr)
                    summary_entry["status"] = "conflict"
                    if not summary_appended:
                        patch_summaries.append(summary_entry)
                        summary_appended = True
                    log_build("conflict")
                    raise typer.Exit(code=1)

                if conflict_writer is None:
                    conflict_writer = create_conflict_writer(
                        cfg,
                        repo,
                        emit_conflicts=emit_option,
                        conflict_blobs_dir=blob_option,
                        overlay_id=overlay_id,
                        cwd=cwd,
                    )

                feature_names = selection.patch_feature_map.get(branch, [])
                feature_name = feature_names[0] if feature_names else None
                resume_cmds = {
                    "continue": "git cherry-pick --continue",
                    "abort": "git cherry-pick --abort",
                    "rebuild": rebuild_command,
                }
                context = ConflictContext(
                    mode="build",
                    overlay=overlay,
                    overlay_id=overlay_id,
                    trunk=cfg.branches.trunk,
                    upstream=f"{cfg.upstream.remote}/{cfg.upstream.branch}",
                    patch_branch=branch,
                    patch_commit=sha,
                    merge_base=base,
                    feature=feature_name,
                    resume=resume_cmds,
                )
                bundle_path, bundle = conflict_writer.next_bundle(context, feature_names)
                record = {
                    "bundle": str(bundle_path),
                    "wave": conflict_writer.wave,
                    "mode": "build",
                    "patch_branch": branch,
                    "patch_commit": sha,
                    "handler": conflict_mode,
                }
                conflict_records.append(record)
                typer.echo(f"[build] Conflicts detected. Bundle written to {bundle_path}")

                if conflict_mode == "bias":
                    actions = apply_recommendations(bundle, cwd)
                    if actions:
                        action_records = [
                            {"path": path, "resolution": choice} for path, choice in actions
                        ]
                        record["auto_actions"] = action_records
                        bias_logs.append({"bundle": str(bundle_path), "actions": action_records})
                    cont = g.run(["cherry-pick", "--continue"], cwd=cwd, check=False)
                    if cont.returncode == 0:
                        record["result"] = "auto-continued"
                        continue

                    record["result"] = "auto-continue-failed"
                    head_cp = g.run(["rev-parse", "CHERRY_PICK_HEAD"], check=False)
                    current_sha = head_cp.stdout.strip() if head_cp.returncode == 0 else sha
                    context = ConflictContext(
                        mode="build",
                        overlay=overlay,
                        overlay_id=overlay_id,
                        trunk=cfg.branches.trunk,
                        upstream=f"{cfg.upstream.remote}/{cfg.upstream.branch}",
                        patch_branch=branch,
                        patch_commit=current_sha,
                        merge_base=base,
                        feature=feature_name,
                        resume=resume_cmds,
                    )
                    bundle_path, bundle = conflict_writer.next_bundle(context, feature_names)
                    conflict_records.append(
                        {
                            "bundle": str(bundle_path),
                            "wave": conflict_writer.wave,
                            "mode": "build",
                            "patch_branch": branch,
                            "patch_commit": current_sha,
                            "handler": "stop",
                            "result": "unresolved",
                        }
                    )
                    typer.echo(f"[build] Remaining conflicts captured in {bundle_path}")
                    summary_entry["status"] = "conflict"
                    if not summary_appended:
                        patch_summaries.append(summary_entry)
                        summary_appended = True
                    log_build("conflict")
                    raise typer.Exit(code=10)

                if conflict_mode == "exec":
                    record["result"] = "exec"
                    command = on_conflict_exec.replace("{json}", str(bundle_path))
                    typer.echo(f"[build] Running conflict exec: {command}")
                    result = subprocess.run(command, shell=True, cwd=str(repo))
                    record["exec_exit_code"] = result.returncode
                    summary_entry["status"] = "conflict"
                    if not summary_appended:
                        patch_summaries.append(summary_entry)
                        summary_appended = True
                    log_build("conflict")
                    raise typer.Exit(code=result.returncode)

                record["result"] = "stopped"
                summary_entry["status"] = "conflict"
                if not summary_appended:
                    patch_summaries.append(summary_entry)
                    summary_appended = True
                log_build("conflict")
                raise typer.Exit(code=10)

            summary_entry["commits"].append({"sha": sha, "summary": summary})
            summary_entry["commit_count"] += 1

        if not summary_appended:
            summary_entry["status"] = "applied"
            patch_summaries.append(summary_entry)

    if use_worktree and cfg.worktree.enabled and prev_ref:
        g.run(["checkout", prev_ref])

    if patch_summaries:
        typer.echo("[build] Patch results:")
        for entry in patch_summaries:
            applied = entry["commit_count"]
            skipped = entry["skipped_count"]
            total = entry["total_commits"]
            plural = "s" if applied != 1 else ""
            descriptor = f"+{applied} commit{plural}"
            if total and applied != total:
                descriptor += f" / {total}"
            if skipped:
                descriptor += f" (skipped {skipped})"
            preview_source = entry["commits"] if entry["commits"] else entry["skipped_commits"]
            if preview_source:
                preview_text = ", ".join(
                    f"{c['sha'][:7]} {c['summary']}" for c in preview_source[:3]
                )
                remaining = len(preview_source) - min(len(preview_source), 3)
                if remaining > 0:
                    preview_text += f", … +{remaining}"
                typer.echo(f"  • {entry['branch']} ({descriptor}): {preview_text}")
            else:
                typer.echo(f"  • {entry['branch']} ({descriptor})")
    else:
        typer.echo("[build] No patches selected; overlay matches trunk.")

    telemetry = log_build("success")

    if write_git_note:
        note_lines = [
            f"forked.build {telemetry['timestamp']}",
            f"overlay={overlay}",
            f"source={selection.source}",
        ]
        if selection.overlay_profile:
            note_lines.append(f"overlay_profile={selection.overlay_profile}")
        if selection.active_features:
            note_lines.append("features=" + ", ".join(selection.active_features))
        note_lines.append("patches=" + ", ".join(selection.patches))
        if skip_upstream_equivalents:
            note_lines.append("skip_upstream_equivalents=true")
        note = "\n".join(note_lines)
        cp = g.run(
            ["notes", "--ref", "refs/notes/forked-meta", "add", "-f", "-m", note, overlay],
            check=False,
        )
        if cp.returncode != 0:
            typer.echo(
                f"[build] Warning: failed to write git note for {overlay}: {cp.stderr.strip()}",
                err=True,
            )

    return overlay, wt_path, telemetry
