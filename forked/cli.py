"""Forked CLI Typer entrypoint."""

from datetime import date, datetime
import json
from pathlib import Path
from typing import List, Tuple
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


@app.command()
def init(upstream_remote: str = "upstream", upstream_branch: str = "main"):
    g.ensure_clean()
    if not g.has_remote(upstream_remote):
        typer.echo(
            f"[init] Missing remote '{upstream_remote}'. Add it first: git remote add {upstream_remote} <url>"
        )
        raise typer.Exit(code=4)
    write_skeleton()
    cfg = load_config()
    g.run(["fetch", upstream_remote])
    g.run(["checkout", "-B", cfg.branches.trunk, f"{upstream_remote}/{upstream_branch}"])
    g.run(["config", "rerere.enabled", "true"])
    conflict_probe = g.run(["-c", "merge.conflictStyle=zdiff3", "status"], check=False)
    if conflict_probe.returncode == 0:
        g.run(["config", "merge.conflictStyle", "zdiff3"])
    else:
        typer.echo("[init] merge.conflictStyle=zdiff3 unsupported; falling back to diff3")
        g.run(["config", "merge.conflictStyle", "diff3"])
    rprint("[green]Initialized Forked. trunk mirrors upstream, forked.yml created.[/green]")


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
):
    cfg = load_config()
    if mode:
        cfg.guards.mode = mode
    trunk = cfg.branches.trunk
    base = g.merge_base(trunk, overlay)

    report = {"report_version": 1, "overlay": overlay, "trunk": trunk, "base": base, "violations": {}}

    if cfg.guards.both_touched:
        bt = both_touched(cfg, base, trunk, overlay)
        report["both_touched"] = bt
        if bt:
            report["violations"]["both_touched"] = bt

    sentinel_report = sentinels(cfg, trunk, overlay)
    report["sentinels"] = sentinel_report
    if sentinel_report["must_match_upstream"] or sentinel_report["must_diverge_from_upstream"]:
        report["violations"]["sentinels"] = sentinel_report

    size_report = size_caps(cfg, overlay, trunk)
    report["size_caps"] = size_report
    if size_report.get("violations"):
        report["violations"]["size_caps"] = {
            "files": size_report["files_changed"],
            "loc": size_report["loc"],
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
    rprint(f"[bold]Report written:[/bold] {output}")

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
