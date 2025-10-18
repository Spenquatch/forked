"""Forked CLI Typer entrypoint."""

from datetime import date, datetime
import json
from pathlib import Path
from typing import Dict, List, Tuple
import typer
from rich import print as rprint
from .config import Config, load_config, write_skeleton
from . import gitutil as g
from .build import build_overlay
from .guards import both_touched, sentinels, size_caps


app = typer.Typer(add_completion=False)


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
def status(latest: int = typer.Option(1, "--latest", min=1, help="Show N newest overlays")):
    cfg = load_config()
    upstream_ref = g.run(["rev-parse", f"{cfg.upstream.remote}/{cfg.upstream.branch}"]).stdout.strip()
    trunk_ref = g.run(["rev-parse", cfg.branches.trunk]).stdout.strip()
    rprint(f"[bold]Upstream[/bold]: {cfg.upstream.remote}/{cfg.upstream.branch} @ {upstream_ref[:12]}")
    rprint(f"[bold]Trunk[/bold]:    {cfg.branches.trunk} @ {trunk_ref[:12]}")
    rprint("[bold]Patches:[/bold]")
    for branch in cfg.patches.order:
        sha = g.run(["rev-parse", branch]).stdout.strip()
        rprint(f"  {branch} @ {sha[:12]}")
    overlays = _overlays_by_date(cfg.branches.overlay_prefix)
    if overlays:
        rprint("[bold]Overlays (newest first):[/bold]")
        for name, ts in overlays[:latest]:
            base = g.merge_base(cfg.branches.trunk, name)
            bt = both_touched(cfg, base, cfg.branches.trunk, name)
            when = datetime.fromtimestamp(ts).isoformat(sep=" ", timespec="seconds")
            rprint(f"  {name}  [{when}]  both-touched={len(bt)}")


@app.command()
def sync():
    cfg = load_config()
    prev_ref = g.current_ref()
    g.ensure_clean()
    g.run(["fetch", cfg.upstream.remote])
    g.run(["checkout", cfg.branches.trunk])
    g.run(["reset", "--hard", f"{cfg.upstream.remote}/{cfg.upstream.branch}"])
    for branch in cfg.patches.order:
        g.run(["checkout", branch])
        cp = g.run(["rebase", cfg.branches.trunk], check=False)
        if cp.returncode != 0:
            typer.echo(f"[sync] Rebase stopped on {branch}. Resolve and rerun `forked sync`.")
            raise typer.Exit(code=4)
    if prev_ref:
        g.run(["checkout", prev_ref])
    rprint("[green]Sync complete: trunk fast-forwarded, patches rebased.[/green]")


@app.command()
def build(
    id: str = typer.Option(date.today().isoformat(), "--id"),
    no_worktree: bool = typer.Option(False, "--no-worktree"),
    auto_continue: bool = typer.Option(False, "--auto-continue"),
):
    cfg = load_config()
    overlay, worktree = build_overlay(cfg, id, use_worktree=(not no_worktree), auto_continue=auto_continue)
    rprint(f"[green]Built overlay[/green] [bold]{overlay}[/bold]")
    if not no_worktree and cfg.worktree.enabled:
        rprint(f"Worktree: {worktree}")


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
