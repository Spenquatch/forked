"""Patch sync workflows with conflict bundle support."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from typing import Any

import typer

import gitutil as g
from config import Config
from conflicts import ConflictContext, apply_recommendations, create_conflict_writer


def _quote_cli(value: str) -> str:
    if not value:
        return "''"
    if any(ch in value for ch in (" ", "'", '"')):
        return "'" + value.replace("'", "'\"'\"'") + "'"
    return value


def _feature_membership(cfg: Config) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for feature_name, feature_cfg in cfg.features.items():
        for patch in feature_cfg.patches:
            mapping.setdefault(patch, []).append(feature_name)
    return mapping


def run_sync(
    cfg: Config,
    *,
    emit_conflicts: str | None,
    conflict_blobs_dir: str | None,
    on_conflict: str,
    on_conflict_exec: str | None,
    auto_continue: bool,
) -> dict[str, Any]:
    conflict_mode = (on_conflict or "stop").lower()
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
    logs_dir = repo / ".forked" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    prev_ref = g.current_ref()
    g.ensure_clean()
    g.run(["fetch", cfg.upstream.remote])
    g.run(["checkout", cfg.branches.trunk])
    g.run(["reset", "--hard", f"{cfg.upstream.remote}/{cfg.upstream.branch}"])

    branch_results: list[dict[str, Any]] = []
    conflict_records: list[dict[str, Any]] = []
    bias_logs: list[dict[str, Any]] = []

    membership = _feature_membership(cfg)

    def log_sync(status: str) -> dict[str, Any]:
        telemetry = {
            "event": "forked.sync",
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "branches": branch_results,
            "trunk": cfg.branches.trunk,
            "upstream": f"{cfg.upstream.remote}/{cfg.upstream.branch}",
            "conflicts": conflict_records,
            "on_conflict": conflict_mode,
        }
        if bias_logs:
            telemetry["bias_actions"] = bias_logs
        log_path = logs_dir / "forked-build.log"
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(telemetry) + "\n")
        return telemetry

    for branch in cfg.patches.order:
        g.run(["checkout", branch])
        base = g.merge_base(cfg.branches.trunk, branch)
        cp = g.run(["rebase", cfg.branches.trunk], check=False)
        if cp.returncode == 0:
            branch_results.append({"branch": branch, "status": "rebased"})
            continue

        if emit_option is None:
            typer.echo(cp.stderr)
            branch_results.append({"branch": branch, "status": "failed", "code": cp.returncode})
            log_sync("failed")
            raise typer.Exit(code=cp.returncode or 4)

        if conflict_writer is None:
            overlay_id = f"sync-{branch.replace('/', '_')}"
            conflict_writer = create_conflict_writer(
                cfg,
                repo,
                emit_conflicts=emit_option,
                conflict_blobs_dir=blob_option,
                overlay_id=overlay_id,
            )

        feature_names = membership.get(branch, [])
        feature_name = feature_names[0] if feature_names else None
        resume_tokens = ["forked", "sync"]
        if emit_conflicts is not None:
            resume_tokens.extend(["--emit-conflicts", emit_conflicts])
        if conflict_blobs_dir is not None:
            resume_tokens.extend(["--conflict-blobs-dir", conflict_blobs_dir])
        resume_tokens.extend(["--on-conflict", conflict_mode])
        if on_conflict_exec:
            resume_tokens.extend(["--on-conflict-exec", on_conflict_exec])
        if auto_continue:
            resume_tokens.append("--auto-continue")
        resume_cmd = " ".join(_quote_cli(token) for token in resume_tokens)

        head_cp = g.run(["rev-parse", "REBASE_HEAD"], check=False)
        current_sha = head_cp.stdout.strip() if head_cp.returncode == 0 else branch
        context = ConflictContext(
            mode="sync",
            overlay=None,
            overlay_id=branch,
            trunk=cfg.branches.trunk,
            upstream=f"{cfg.upstream.remote}/{cfg.upstream.branch}",
            patch_branch=branch,
            patch_commit=current_sha,
            merge_base=base,
            feature=feature_name,
            resume={
                "continue": "git rebase --continue",
                "abort": "git rebase --abort",
                "rebuild": resume_cmd,
            },
        )
        bundle_path, bundle = conflict_writer.next_bundle(context, feature_names)
        record = {
            "bundle": str(bundle_path),
            "wave": conflict_writer.wave,
            "mode": "sync",
            "patch_branch": branch,
            "patch_commit": current_sha,
            "handler": conflict_mode,
        }
        conflict_records.append(record)
        branch_results.append({"branch": branch, "status": "conflict"})
        typer.echo(f"[sync] Conflicts detected. Bundle written to {bundle_path}")

        if conflict_mode == "bias":
            actions = apply_recommendations(bundle, cwd=None)
            if actions:
                action_records = [{"path": path, "resolution": choice} for path, choice in actions]
                record["auto_actions"] = action_records
                bias_logs.append({"bundle": str(bundle_path), "actions": action_records})
            cont = g.run(["rebase", "--continue"], check=False)
            if cont.returncode == 0:
                record["result"] = "auto-continued"
                branch_results[-1]["status"] = "rebased"
                continue

            record["result"] = "auto-continue-failed"
            head_cp = g.run(["rev-parse", "REBASE_HEAD"], check=False)
            current_sha = head_cp.stdout.strip() if head_cp.returncode == 0 else current_sha
            context = ConflictContext(
                mode="sync",
                overlay=None,
                overlay_id=branch,
                trunk=cfg.branches.trunk,
                upstream=f"{cfg.upstream.remote}/{cfg.upstream.branch}",
                patch_branch=branch,
                patch_commit=current_sha,
                merge_base=base,
                feature=feature_name,
                resume=context.resume,
            )
            bundle_path, bundle = conflict_writer.next_bundle(context, feature_names)
            conflict_records.append(
                {
                    "bundle": str(bundle_path),
                    "wave": conflict_writer.wave,
                    "mode": "sync",
                    "patch_branch": branch,
                    "patch_commit": current_sha,
                    "handler": "stop",
                    "result": "unresolved",
                }
            )
            typer.echo(f"[sync] Remaining conflicts captured in {bundle_path}")
            log_sync("conflict")
            raise typer.Exit(code=10)

        if conflict_mode == "exec":
            if on_conflict_exec is None:
                raise typer.BadParameter("--on-conflict exec requires --on-conflict-exec command.")
            record["result"] = "exec"
            command = on_conflict_exec.replace("{json}", str(bundle_path))
            typer.echo(f"[sync] Running conflict exec: {command}")
            result = subprocess.run(command, shell=True, cwd=str(repo))
            record["exec_exit_code"] = result.returncode
            log_sync("conflict")
            raise typer.Exit(code=result.returncode)

        record["result"] = "stopped"
        log_sync("conflict")
        raise typer.Exit(code=10)

    if prev_ref:
        g.run(["checkout", prev_ref])

    telemetry = log_sync("success")
    return telemetry
