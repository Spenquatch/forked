"""Forked CLI Typer entrypoint."""

from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import typer
from rich import print as rprint
from .config import Config, Feature, load_config, write_config, write_skeleton
from . import gitutil as g
from .build import build_overlay
from .guards import both_touched, sentinels, size_caps
from .sync import run_sync
from .resolver import ResolutionError, resolve_selection


app = typer.Typer(add_completion=False)
feature_app = typer.Typer(help="Feature slice management")
app.add_typer(feature_app, name="feature")


def _parse_csv_option(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    items = []
    for chunk in raw.split(","):
        value = chunk.strip()
        if value:
            items.append(value)
    return items


def _ahead_behind(trunk: str, branch: str) -> Optional[Tuple[int, int]]:
    cp = g.run(["rev-list", "--left-right", "--count", f"{trunk}...{branch}"], check=False)
    if cp.returncode != 0:
        return None
    parts = cp.stdout.strip().split()
    if len(parts) != 2:
        return None
    try:
        behind = int(parts[0])
        ahead = int(parts[1])
    except ValueError:
        return None
    return behind, ahead


def _overlays_by_date(prefix: str) -> List[Tuple[str, int]]:
    fmt = "%(refname:short)|%(committerdate:unix)"
    cp = g.run(["for-each-ref", f"--format={fmt}", f"refs/heads/{prefix}"])
    items: List[Tuple[str, int]] = []
    for line in cp.stdout.splitlines():
        if "|" not in line:
            continue
        name, ts_value = line.split("|", 1)
        try:
            items.append((name, int(ts_value)))
        except ValueError:
            continue
    return sorted(items, key=lambda item: item[1], reverse=True)


def _parse_iso_timestamp(raw: str) -> Optional[datetime]:
    if not raw:
        return None
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _format_timestamp_utc(ts: Optional[datetime]) -> Optional[str]:
    if ts is None:
        return None
    return ts.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_latest_build_entries() -> Dict[str, Tuple[Optional[datetime], Dict[str, Any]]]:
    repo = g.repo_root()
    log_path = repo / ".forked" / "logs" / "forked-build.log"
    if not log_path.exists():
        return {}
    latest: Dict[str, Tuple[Optional[datetime], Dict[str, Any]]] = {}
    for raw_line in log_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            typer.secho(
                "[status] Warning: unable to parse build log entry; skipping.",
                fg=typer.colors.YELLOW,
                err=True,
            )
            continue
        overlay_name = entry.get("overlay")
        if not overlay_name:
            continue
        ts = _parse_iso_timestamp(entry.get("timestamp", ""))
        existing = latest.get(overlay_name)
        if existing is None:
            latest[overlay_name] = (ts, entry)
            continue
        prev_ts, _ = existing
        if prev_ts is None and ts is not None:
            latest[overlay_name] = (ts, entry)
        elif ts is not None and prev_ts is not None and ts > prev_ts:
            latest[overlay_name] = (ts, entry)
        elif ts is None and prev_ts is None:
            latest[overlay_name] = (ts, entry)
    return latest


def _read_overlay_note(overlay: str) -> Optional[Dict[str, Any]]:
    cp = g.run(["notes", "--ref", "refs/notes/forked-meta", "show", overlay], check=False)
    if cp.returncode != 0 or not cp.stdout.strip():
        return None
    features: List[str] = []
    patches: List[str] = []
    overlay_profile: Optional[str] = None
    skip_equivalents = False
    for raw_line in cp.stdout.splitlines():
        line = raw_line.strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lower()
        value = value.strip()
        if key == "features":
            features = [chunk.strip() for chunk in value.split(",") if chunk.strip()]
        elif key == "patches":
            patches = [chunk.strip() for chunk in value.split(",") if chunk.strip()]
        elif key == "overlay_profile":
            overlay_profile = value or None
        elif key == "skip_upstream_equivalents":
            skip_equivalents = value.lower() in {"1", "true", "yes"}
    return {
        "source": "git-note",
        "features": features,
        "patches": patches,
        "overlay_profile": overlay_profile,
        "skip_upstream_equivalents": skip_equivalents,
    }


def _load_guard_report() -> Optional[Dict[str, Any]]:
    repo = g.repo_root()
    path = repo / ".forked" / "report.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        typer.secho(
            "[status] Warning: unable to parse .forked/report.json; ignoring guard metrics.",
            fg=typer.colors.YELLOW,
            err=True,
        )
        return None


def _selection_from_log(entry: Dict[str, Any]) -> Dict[str, Any]:
    raw = entry.get("selection") or {}
    selection: Dict[str, Any] = {
        "source": "provenance-log",
        "features": raw.get("features", []),
        "patches": raw.get("patches", []),
    }
    if "overlay_profile" in raw:
        selection["overlay_profile"] = raw.get("overlay_profile")
    if "include" in raw:
        selection["include"] = raw.get("include")
    if "exclude" in raw:
        selection["exclude"] = raw.get("exclude")
    if "unmatched_include" in raw:
        selection["unmatched_include"] = raw.get("unmatched_include")
    if "unmatched_exclude" in raw:
        selection["unmatched_exclude"] = raw.get("unmatched_exclude")
    if "patch_feature_map" in raw:
        selection["patch_feature_map"] = raw.get("patch_feature_map")
    if "skip_upstream_equivalents" in raw:
        selection["skip_upstream_equivalents"] = raw.get("skip_upstream_equivalents")
    resolver_source = raw.get("source")
    if resolver_source:
        selection["resolver_source"] = resolver_source
    return selection


def _derived_selection(cfg: Config, overlay_branch: str) -> Dict[str, Any]:
    prefix = cfg.branches.overlay_prefix
    overlay_id = overlay_branch[len(prefix) :] if overlay_branch.startswith(prefix) else overlay_branch
    typer.secho(
        f"[status] Provenance missing for {overlay_branch}; deriving selection from configuration.",
        fg=typer.colors.YELLOW,
        err=True,
    )
    try:
        if overlay_id in cfg.overlays:
            resolved = resolve_selection(cfg, overlay=overlay_id)
        else:
            resolved = resolve_selection(cfg)
    except ResolutionError as exc:
        typer.secho(
            f"[status] Warning: resolver fallback failed for {overlay_branch}: {exc}",
            fg=typer.colors.YELLOW,
            err=True,
        )
        return {"source": "derived", "features": [], "patches": []}

    return {
        "source": "derived",
        "resolver_source": resolved.source,
        "overlay_profile": resolved.overlay_profile,
        "features": resolved.active_features,
        "patches": resolved.patches,
        "include": resolved.include,
        "exclude": resolved.exclude,
        "skip_upstream_equivalents": False,
    }


def _collect_status_summary(cfg: Config, latest: int) -> Dict[str, Any]:
    upstream_ref = g.run(
        ["rev-parse", f"{cfg.upstream.remote}/{cfg.upstream.branch}"], check=False
    )
    if upstream_ref.returncode != 0:
        typer.secho(
            f"[status] Warning: unable to resolve upstream {cfg.upstream.remote}/{cfg.upstream.branch}",
            fg=typer.colors.YELLOW,
            err=True,
        )
        upstream_sha = None
    else:
        upstream_sha = upstream_ref.stdout.strip()

    trunk_ref = g.run(["rev-parse", cfg.branches.trunk], check=False)
    if trunk_ref.returncode != 0:
        typer.secho(
            f"[status] Warning: unable to resolve trunk branch '{cfg.branches.trunk}'",
            fg=typer.colors.YELLOW,
            err=True,
        )
        trunk_sha = None
    else:
        trunk_sha = trunk_ref.stdout.strip()

    summary: Dict[str, Any] = {
        "status_version": 1,
        "upstream": {
            "remote": cfg.upstream.remote,
            "branch": cfg.upstream.branch,
            "sha": upstream_sha,
        },
        "trunk": {"name": cfg.branches.trunk, "sha": trunk_sha},
        "patches": [],
        "overlays": [],
    }

    for branch in cfg.patches.order:
        rev = g.run(["rev-parse", branch], check=False)
        if rev.returncode != 0:
            typer.secho(
                f"[status] Warning: patch branch '{branch}' not found.",
                fg=typer.colors.YELLOW,
                err=True,
            )
            branch_sha = None
            ahead = None
            behind = None
        else:
            branch_sha = rev.stdout.strip()
            ahead_behind = _ahead_behind(cfg.branches.trunk, branch)
            if ahead_behind is None:
                typer.secho(
                    f"[status] Unable to compute ahead/behind for '{branch}'.",
                    fg=typer.colors.YELLOW,
                    err=True,
                )
                behind = None
                ahead = None
            else:
                behind, ahead = ahead_behind
        summary["patches"].append(
            {"name": branch, "sha": branch_sha, "ahead": ahead, "behind": behind}
        )

    guard_report = _load_guard_report()
    guard_counts: Dict[str, int] = {}
    if guard_report:
        overlay_name = guard_report.get("overlay")
        both = guard_report.get("both_touched")
        if isinstance(overlay_name, str) and isinstance(both, list):
            guard_counts[overlay_name] = len(both)

    build_entries = _load_latest_build_entries()
    overlays = _overlays_by_date(cfg.branches.overlay_prefix)
    if not overlays:
        typer.secho("[status] No overlay branches found.", fg=typer.colors.BLUE, err=True)

    for name, commit_ts in overlays[:latest]:
        rev = g.run(["rev-parse", name], check=False)
        if rev.returncode != 0:
            typer.secho(
                f"[status] Warning: overlay branch '{name}' not found.",
                fg=typer.colors.YELLOW,
                err=True,
            )
            overlay_sha: Optional[str] = None
        else:
            overlay_sha = rev.stdout.strip()

        log_entry = build_entries.get(name)
        selection: Dict[str, Any]
        built_ts: Optional[datetime] = None
        status_value: Optional[str] = None

        if log_entry:
            built_ts, entry_payload = log_entry
            selection = _selection_from_log(entry_payload)
            status_value = entry_payload.get("status")
        else:
            selection = {}

        if not selection:
            note_selection = _read_overlay_note(name)
            if note_selection:
                selection = note_selection

        if not selection:
            selection = _derived_selection(cfg, name)

        if built_ts is None:
            built_ts = datetime.utcfromtimestamp(commit_ts).replace(tzinfo=timezone.utc)

        overlay_payload: Dict[str, Any] = {
            "name": name,
            "sha": overlay_sha,
            "built_at": _format_timestamp_utc(built_ts),
            "selection": selection,
            "both_touched_count": guard_counts.get(name),
        }
        if status_value:
            overlay_payload["build_status"] = status_value

        summary["overlays"].append(overlay_payload)

    return summary

def _ensure_gitignore(entry: str):
    repo = g.repo_root()
    gitignore_path = repo / ".gitignore"
    if gitignore_path.exists():
        lines = gitignore_path.read_text().splitlines()
        if entry in lines:
            return
        lines.append(entry)
        gitignore_path.write_text("\n".join(lines) + "\n")
    else:
        gitignore_path.write_text(f"{entry}\n")


@app.command()
def init(upstream_remote: str = "upstream", upstream_branch: str = "main"):
    g.ensure_clean()
    if not g.has_remote(upstream_remote):
        typer.echo(
            f"[init] Missing remote '{upstream_remote}'. Add it first: git remote add {upstream_remote} <url>"
        )
        raise typer.Exit(code=4)
    write_skeleton()
    _ensure_gitignore(".forked/")
    cfg = load_config()
    g.run(["fetch", upstream_remote])
    g.run(["checkout", "-B", cfg.branches.trunk, f"{upstream_remote}/{upstream_branch}"])
    g.run(["config", "rerere.enabled", "true"])
    ver_cp = g.run(["--version"])
    version_parts = ver_cp.stdout.strip().split()
    git_version = version_parts[-1] if version_parts else ""
    supports_zdiff3 = False
    try:
        major, minor, *rest = git_version.split(".")
        minor_val = int(minor)
        major_val = int(major)
        patch_val = int(rest[0]) if rest else 0
        supports_zdiff3 = (major_val, minor_val, patch_val) >= (2, 38, 0)
    except ValueError:
        supports_zdiff3 = False

    if supports_zdiff3:
        g.run(["config", "merge.conflictStyle", "zdiff3"])
    else:
        typer.echo("[init] Using diff3 merge conflict style (zdiff3 requires Git 2.38+)")
        g.run(["config", "merge.conflictStyle", "diff3"])
    rprint("[green]Initialized Forked. trunk mirrors upstream.[/green]")


@app.command()
def status(
    latest: int = typer.Option(5, "--latest", min=1, help="Show N newest overlays"),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit machine-readable status JSON",
        is_flag=True,
    ),
):
    cfg = load_config()
    summary = _collect_status_summary(cfg, latest)

    if json_output:
        typer.echo(json.dumps(summary, indent=2))
        return

    upstream = summary["upstream"]
    trunk = summary["trunk"]
    upstream_sha = upstream.get("sha") or ""
    trunk_sha = trunk.get("sha") or ""
    rprint(
        f"[bold]Upstream[/bold]: {upstream['remote']}/{upstream['branch']} @ {upstream_sha[:12]}"
    )
    rprint(f"[bold]Trunk[/bold]:    {trunk['name']} @ {trunk_sha[:12]}")

    rprint("[bold]Patches:[/bold]")
    for patch in summary["patches"]:
        sha = patch.get("sha") or ""
        rprint(f"  {patch['name']} @ {sha[:12]}")

    overlays = summary["overlays"]
    if overlays:
        rprint("[bold]Overlays (newest first):[/bold]")
        for entry in overlays:
            name = entry["name"]
            sha = entry.get("sha")
            built_at = entry.get("built_at") or "unknown"
            if sha is None:
                rprint(f"  {name}  [{built_at}]  missing")
                continue
            base = g.merge_base(cfg.branches.trunk, name)
            bt = both_touched(cfg, base, cfg.branches.trunk, name)
            rprint(f"  {name}  [{built_at}]  both-touched={len(bt)}")


@app.command()
def sync(
    emit_conflicts: Optional[str] = typer.Option(
        None,
        "--emit-conflicts",
        help="Write conflict bundle JSON to PATH (default auto under .forked/conflicts)",
        metavar="[PATH]",
        show_default=False,
        flag_value="__AUTO__",
    ),
    conflict_blobs_dir: Optional[str] = typer.Option(
        None,
        "--conflict-blobs-dir",
        help="Directory for base/ours/theirs blob exports",
        metavar="[DIR]",
        show_default=False,
        flag_value="__AUTO__",
    ),
    on_conflict: str = typer.Option(
        "stop",
        "--on-conflict",
        help="Conflict handling mode: stop, bias, or exec",
        metavar="MODE",
        show_default=True,
    ),
    on_conflict_exec: Optional[str] = typer.Option(
        None,
        "--on-conflict-exec",
        help="Shell command to run when --on-conflict exec (use {json} placeholder)",
        metavar="COMMAND",
    ),
    auto_continue: bool = typer.Option(
        False,
        "--auto-continue",
        help="Alias for --on-conflict bias",
    ),
):
    cfg = load_config()
    conflict_mode = on_conflict.lower()
    if conflict_mode in {"bias-continue", "bias_continue"}:
        conflict_mode = "bias"
    if conflict_mode not in {"stop", "bias", "exec"}:
        raise typer.BadParameter("--on-conflict must be one of: stop, bias, exec")
    if on_conflict_exec and conflict_mode != "exec":
        conflict_mode = "exec"

    telemetry = run_sync(
        cfg,
        emit_conflicts=emit_conflicts,
        conflict_blobs_dir=conflict_blobs_dir,
        on_conflict=conflict_mode,
        on_conflict_exec=on_conflict_exec,
        auto_continue=auto_continue,
    )

    branches = telemetry.get("branches", [])
    if branches:
        for entry in branches:
            status = entry.get("status", "")
            typer.echo(f"[sync] {entry['branch']}: {status}")

    conflict_entries = telemetry.get("conflicts", []) or []
    if conflict_entries:
        bundles = ", ".join(entry.get("bundle", "") for entry in conflict_entries)
        typer.echo(f"[sync] Conflict bundle(s) recorded: {bundles}")

    rprint("[green]Sync complete: trunk fast-forwarded, patches rebased.[/green]")


@app.command()
def build(
    overlay: Optional[str] = typer.Option(
        None, "--overlay", help="Overlay profile defined in forked.yml"
    ),
    features_arg: Optional[str] = typer.Option(
        None,
        "--features",
        "-f",
        help="Comma-separated list of features to include (mutually exclusive with --overlay)",
    ),
    include: List[str] = typer.Option(
        None,
        "--include",
        help="Patch glob to force-include (can be provided multiple times)",
        show_default=False,
        metavar="PATTERN",
    ),
    exclude: List[str] = typer.Option(
        None,
        "--exclude",
        help="Patch glob to exclude (can be provided multiple times)",
        show_default=False,
        metavar="PATTERN",
    ),
    id: Optional[str] = typer.Option(
        None,
        "--id",
        help="Overlay identifier; defaults to profile name when using --overlay, otherwise today's date",
    ),
    no_worktree: bool = typer.Option(False, "--no-worktree"),
    auto_continue: bool = typer.Option(False, "--auto-continue"),
    skip_upstream_equivalents: bool = typer.Option(
        False,
        "--skip-upstream-equivalents",
        help="Skip commits already present in trunk (uses git cherry)",
    ),
    git_note: bool = typer.Option(
        True,
        "--git-note/--no-git-note",
        help="Write provenance note to refs/notes/forked-meta",
    ),
    emit_conflicts: Optional[str] = typer.Option(
        None,
        "--emit-conflicts",
        help="Write conflict bundle JSON to PATH (default: .forked/conflicts/<id>-<wave>.json)",
        metavar="[PATH]",
        show_default=False,
        flag_value="__AUTO__",
    ),
    conflict_blobs_dir: Optional[str] = typer.Option(
        None,
        "--conflict-blobs-dir",
        help="Directory for base/ours/theirs blob exports (default auto when flag used)",
        metavar="[DIR]",
        show_default=False,
        flag_value="__AUTO__",
    ),
    on_conflict: str = typer.Option(
        "stop",
        "--on-conflict",
        help="Conflict handling mode: stop, bias, or exec",
        metavar="MODE",
        show_default=True,
    ),
    on_conflict_exec: Optional[str] = typer.Option(
        None,
        "--on-conflict-exec",
        help="Shell command to run when --on-conflict exec (use {json} placeholder)",
        metavar="COMMAND",
    ),
):
    cfg = load_config()
    feature_list = _parse_csv_option(features_arg)
    try:
        selection = resolve_selection(
            cfg,
            overlay=overlay,
            features=feature_list or None,
            include=include or [],
            exclude=exclude or [],
        )
    except ResolutionError as exc:
        typer.secho(f"[build] {exc}", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    overlay_id = id or (overlay or date.today().isoformat())

    conflict_mode = on_conflict.lower()
    if conflict_mode in {"bias-continue", "bias_continue"}:
        conflict_mode = "bias"
    if conflict_mode not in {"stop", "bias", "exec"}:
        raise typer.BadParameter("--on-conflict must be one of: stop, bias, exec")
    if on_conflict_exec and conflict_mode != "exec":
        conflict_mode = "exec"

    if selection.unmatched_include:
        typer.secho(
            "[build] Warning: include patterns matched no patches: "
            + ", ".join(selection.unmatched_include),
            fg=typer.colors.YELLOW,
        )
    if selection.unmatched_exclude:
        typer.secho(
            "[build] Warning: exclude patterns matched no patches: "
            + ", ".join(selection.unmatched_exclude),
            fg=typer.colors.YELLOW,
        )

    if selection.active_features:
        typer.echo("[build] Active features: " + ", ".join(selection.active_features))
    else:
        typer.echo("[build] Active features: (none)")
    typer.echo(f"[build] Applying {len(selection.patches)} patch branch(es)")

    overlay_branch, worktree, telemetry = build_overlay(
        cfg,
        overlay_id,
        selection,
        use_worktree=(not no_worktree),
        auto_continue=auto_continue,
        skip_upstream_equivalents=skip_upstream_equivalents,
        write_git_note=git_note,
        emit_conflicts=emit_conflicts,
        conflict_blobs_dir=conflict_blobs_dir,
        on_conflict=conflict_mode,
        on_conflict_exec=on_conflict_exec,
    )

    if selection.overlay_profile:
        rprint(f"[bold]Overlay profile:[/bold] {selection.overlay_profile}")
    if selection.include or selection.exclude:
        filters: List[str] = []
        if selection.include:
            filters.append("include=" + ",".join(selection.include))
        if selection.exclude:
            filters.append("exclude=" + ",".join(selection.exclude))
        rprint("[bold]Selection filters:[/bold] " + "; ".join(filters))

    rprint(f"[green]Built overlay[/green] [bold]{overlay_branch}[/bold]")
    if not no_worktree and cfg.worktree.enabled:
        rprint(f"Worktree: {worktree}")

    conflict_entries = telemetry.get("conflicts", []) or []
    if conflict_entries:
        bundles = ", ".join(entry.get("bundle", "") for entry in conflict_entries)
        typer.echo(f"[build] Conflict bundle(s) recorded: {bundles}")

    skipped_total = sum(entry.get("skipped_count", 0) for entry in telemetry["patches"])
    if skip_upstream_equivalents:
        typer.echo(f"[build] Skipped {skipped_total} upstream-equivalent commit(s)")


@app.command()
def guard(
    overlay: str = typer.Option(..., "--overlay", help="Overlay branch/ref to inspect"),
    output: Path = typer.Option(Path(".forked/report.json"), "--output"),
    mode: str = typer.Option(None, "--mode"),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Display sentinel matches and write additional debug details",
    ),
):
    cfg = load_config()
    if mode:
        cfg.guards.mode = mode
    trunk = cfg.branches.trunk
    base = g.merge_base(trunk, overlay)

    report: Dict[str, Any] = {
        "report_version": 1,
        "overlay": overlay,
        "trunk": trunk,
        "base": base,
        "violations": {},
    }
    debug_info: Dict[str, Any] = {}

    if cfg.guards.both_touched:
        bt = both_touched(cfg, base, trunk, overlay)
        report["both_touched"] = bt
        if bt:
            report["violations"]["both_touched"] = bt
        if verbose:
            debug_info["both_touched"] = bt

    sentinel_report, sentinel_debug = sentinels(cfg, trunk, overlay, return_debug=verbose)
    report["sentinels"] = sentinel_report
    if sentinel_report["must_match_upstream"] or sentinel_report["must_diverge_from_upstream"]:
        report["violations"]["sentinels"] = sentinel_report
    if verbose:
        debug_info["sentinels"] = sentinel_debug

    size_report = size_caps(cfg, overlay, trunk)
    report["size_caps"] = size_report
    if size_report.get("violations"):
        report["violations"]["size_caps"] = {
            "files": size_report["files_changed"],
            "loc": size_report["loc"],
        }
    if verbose:
        debug_info["size_caps"] = {
            "files_changed": size_report["files_changed"],
            "loc": size_report["loc"],
        }

    if verbose:
        report["debug"] = debug_info
        if debug_info.get("both_touched"):
            typer.echo("[guard] Both-touched files:")
            for path in debug_info["both_touched"]:
                typer.echo(f"  {path}")
        sent_dbg = debug_info.get("sentinels", {})
        if sent_dbg:
            mm = sent_dbg.get("matched_must_match", [])
            md = sent_dbg.get("matched_must_diverge", [])
            typer.echo("[guard] Sentinel matches:")
            typer.echo(f"  must_match_upstream ({len(mm)}):")
            for path in mm[:10]:
                typer.echo(f"    {path}")
            if len(mm) > 10:
                typer.echo(f"    … +{len(mm) - 10}")
            typer.echo(f"  must_diverge_from_upstream ({len(md)}):")
            for path in md[:10]:
                typer.echo(f"    {path}")
            if len(md) > 10:
                typer.echo(f"    … +{len(md) - 10}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
    rprint(f"[bold]Report written:[/bold] {output}")

    repo = g.repo_root()
    logs_dir = repo / ".forked" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    guard_log_entry = {
        "timestamp": datetime.now().isoformat(),
        "overlay": overlay,
        "mode": cfg.guards.mode,
        "violations": report["violations"],
        "verbose": verbose,
    }
    if verbose:
        guard_log_entry["debug"] = debug_info
    with (logs_dir / "forked-guard.log").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(guard_log_entry) + "\n")

    has_violations = bool(report["violations"])
    if cfg.guards.mode == "block" and has_violations:
        raise typer.Exit(code=2)
    if cfg.guards.mode == "require-override" and has_violations:
        raise typer.Exit(code=2)


@app.command()
def publish(
    overlay: str,
    tag: str = typer.Option(None, "--tag"),
    push: bool = typer.Option(False, "--push"),
    remote: str = typer.Option("origin", "--remote"),
):
    if tag:
        g.run(["tag", "-f", tag, overlay])
    if push:
        if tag:
            g.run(["push", "--force", remote, tag])
        g.run(["push", "--force", remote, overlay])
    rprint("[green]Publish complete.[/green]")


def main():
    app()


if __name__ == "__main__":
    main()
@feature_app.command("create")
def feature_create(
    name: str = typer.Argument(..., help="Feature name (kebab-case recommended)"),
    slices: int = typer.Option(1, "--slices", min=1, help="Number of patch slices to scaffold"),
    slug: Optional[str] = typer.Option(
        None,
        "--slug",
        help="Optional suffix for slice branches (e.g. 'initial'); defaults to numeric only",
    ),
):
    cfg = load_config()
    g.ensure_clean()

    if name in cfg.features:
        typer.secho(f"[feature] Feature '{name}' already exists in forked.yml.", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    slug_fragment = slug.replace(" ", "-") if slug else ""
    new_patches: List[str] = []

    # Ensure trunk exists before creating branches.
    trunk_cp = g.run(["rev-parse", cfg.branches.trunk], check=False)
    if trunk_cp.returncode != 0:
        typer.secho(
            f"[feature] Trunk branch '{cfg.branches.trunk}' not found. Run `forked sync` first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=2)

    for index in range(1, slices + 1):
        suffix = f"{index:02d}"
        if slug_fragment:
            suffix = f"{suffix}-{slug_fragment}"
        branch_name = f"patch/{name}/{suffix}"
        if branch_name in cfg.patches.order:
            typer.secho(
                f"[feature] Patch '{branch_name}' already listed in forked.yml.patches.order.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=2)
        existing = g.run(["show-ref", "--verify", f"refs/heads/{branch_name}"], check=False)
        if existing.returncode == 0:
            typer.secho(
                f"[feature] Branch '{branch_name}' already exists; choose a different feature name.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=2)
        g.run(["branch", branch_name, cfg.branches.trunk])
        new_patches.append(branch_name)

    cfg.patches.order.extend(new_patches)
    cfg.features[name] = Feature(patches=new_patches)
    write_config(cfg)

    rprint(f"[green]Created feature[/green] [bold]{name}[/bold]")
    for branch_name in new_patches:
        rprint(f"  • {branch_name}")


@feature_app.command("status")
def feature_status():
    cfg = load_config()
    if not cfg.features:
        typer.echo("[feature] No features defined in forked.yml.")
        return

    trunk = cfg.branches.trunk
    typer.echo(f"[feature] Trunk reference: {trunk}")

    first = True
    for feature_name, feature_cfg in cfg.features.items():
        if not first:
            typer.echo("")
        first = False
        typer.echo(f"{feature_name}:")
        patches = feature_cfg.patches or []
        if not patches:
            typer.echo("  (no slices defined)")
            continue
        for patch_branch in patches:
            cp = g.run(["rev-parse", patch_branch], check=False)
            if cp.returncode != 0:
                typer.secho(f"  - {patch_branch}: branch missing", fg=typer.colors.RED)
                continue
            sha = cp.stdout.strip()
            ahead_behind = _ahead_behind(trunk, patch_branch)
            if ahead_behind is None:
                typer.echo(f"  - {patch_branch}: {sha[:12]} (unable to compute ahead/behind)")
                continue
            behind, ahead = ahead_behind
            if ahead == 0 and behind == 0:
                status = "merged"
            else:
                status = f"{ahead} ahead / {behind} behind"
            typer.echo(f"  - {patch_branch}: {sha[:12]} ({status})")
