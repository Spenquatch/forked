"""Forked CLI Typer entrypoint."""

import json
import shutil
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from fnmatch import fnmatch
from pathlib import Path
from typing import Annotated, Any

import typer
from rich import print as rprint

import gitutil as g
from build import build_overlay
from config import Config, Feature, load_config, write_config, write_skeleton
from guards import both_touched, sentinels, size_caps
from resolver import ResolutionError, resolve_selection
from sync import run_sync

app = typer.Typer(add_completion=False)
feature_app = typer.Typer(help="Feature slice management")
app.add_typer(feature_app, name="feature")


def _parse_csv_option(raw: str | None) -> list[str]:
    if not raw:
        return []
    items = []
    for chunk in raw.split(","):
        value = chunk.strip()
        if value:
            items.append(value)
    return items


def _ahead_behind(trunk: str, branch: str) -> tuple[int, int] | None:
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


def _overlays_by_date(prefix: str) -> list[tuple[str, int]]:
    fmt = "%(refname:short)|%(committerdate:unix)"
    cp = g.run(["for-each-ref", f"--format={fmt}", f"refs/heads/{prefix}"])
    items: list[tuple[str, int]] = []
    for line in cp.stdout.splitlines():
        if "|" not in line:
            continue
        name, ts_value = line.split("|", 1)
        try:
            items.append((name, int(ts_value)))
        except ValueError:
            continue
    return sorted(items, key=lambda item: item[1], reverse=True)


def _parse_iso_timestamp(raw: str) -> datetime | None:
    if not raw:
        return None
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _format_timestamp_utc(ts: datetime | None) -> str | None:
    if ts is None:
        return None
    return ts.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_latest_build_entries() -> dict[str, tuple[datetime | None, dict[str, Any]]]:
    repo = g.repo_root()
    log_path = repo / ".forked" / "logs" / "forked-build.log"
    if not log_path.exists():
        return {}
    latest: dict[str, tuple[datetime | None, dict[str, Any]]] = {}
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


def _read_overlay_note(overlay: str) -> dict[str, Any] | None:
    cp = g.run(["notes", "--ref", "refs/notes/forked-meta", "show", overlay], check=False)
    if cp.returncode != 0 or not cp.stdout.strip():
        return None
    features: list[str] = []
    patches: list[str] = []
    overlay_profile: str | None = None
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


def _load_guard_report() -> dict[str, Any] | None:
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


def _selection_from_log(entry: dict[str, Any]) -> dict[str, Any]:
    raw = entry.get("selection") or {}
    selection: dict[str, Any] = {
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


def _derived_selection(cfg: Config, overlay_branch: str) -> dict[str, Any]:
    prefix = cfg.branches.overlay_prefix
    overlay_id = (
        overlay_branch[len(prefix) :] if overlay_branch.startswith(prefix) else overlay_branch
    )
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


def _selection_for_overlay(
    cfg: Config,
    overlay_branch: str,
    build_entries: dict[str, tuple[datetime | None, dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Return selection metadata for overlay from provenance log, git note, or resolver fallback."""
    entries = build_entries if build_entries is not None else _load_latest_build_entries()
    selection: dict[str, Any] = {}
    entry = entries.get(overlay_branch)
    if entry:
        _, payload = entry
        selection = _selection_from_log(payload)
    if not selection:
        note_selection = _read_overlay_note(overlay_branch)
        if note_selection:
            selection = note_selection
    if not selection:
        selection = _derived_selection(cfg, overlay_branch)
    return selection


def _split_override_values(raw: str) -> list[str]:
    tokens = raw.replace(",", " ").split()
    seen: set[str] = set()
    values: list[str] = []
    for token in tokens:
        value = token.strip().lower()
        if not value or value in seen:
            continue
        seen.add(value)
        values.append(value)
    return values


def _collect_trailer_values(raw: str, trailer_key: str) -> list[str]:
    key_lower = trailer_key.lower()
    values: list[str] = []
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        if key.strip().lower() != key_lower:
            continue
        values.extend(_split_override_values(rest))
    return values


def _commit_override(trailer_key: str, commit: str) -> list[str]:
    cp = g.run(
        ["show", "-s", f"--format=%(trailers:key={trailer_key},valueonly)", commit],
        check=False,
    )
    if cp.returncode != 0 or not cp.stdout.strip():
        return []
    values: list[str] = []
    for line in cp.stdout.splitlines():
        values.extend(_split_override_values(line))
    return values


def _tag_override(trailer_key: str, commit: str) -> tuple[list[str], str | None]:
    tag_list = g.run(["tag", "--points-at", commit], check=False)
    if tag_list.returncode != 0:
        return [], None
    candidates: list[tuple[int, str]] = []
    for tag in tag_list.stdout.splitlines():
        if not tag:
            continue
        ref = f"refs/tags/{tag}"
        meta = g.run(
            ["for-each-ref", ref, "--format=%(objecttype)|%(creatordate:unix)"],
            check=False,
        )
        if meta.returncode != 0:
            continue
        parts = meta.stdout.strip().split("|", 1)
        if len(parts) != 2 or parts[0] != "tag":
            continue
        try:
            ts = int(parts[1])
        except ValueError:
            ts = 0
        candidates.append((ts, tag))

    for _, tag in sorted(candidates, reverse=True):
        contents = g.run(["tag", "-l", tag, "--format=%(contents)"], check=False)
        if contents.returncode != 0 or not contents.stdout:
            continue
        values = _collect_trailer_values(contents.stdout, trailer_key)
        if values:
            return values, tag
    return [], None


def _note_override(trailer_key: str, commit: str) -> list[str]:
    cp = g.run(
        ["notes", "--ref", "refs/notes/forked/override", "show", commit],
        check=False,
    )
    if cp.returncode != 0 or not cp.stdout.strip():
        return []
    return _collect_trailer_values(cp.stdout, trailer_key)


def _resolve_override(cfg: Config, overlay: str, commit: str) -> dict[str, Any]:
    trailer_key = cfg.policy_overrides.trailer_key or "Forked-Override"
    commit_values = _commit_override(trailer_key, commit)
    if commit_values:
        return {"source": "commit", "values": commit_values}

    tag_values, tag_name = _tag_override(trailer_key, commit)
    if tag_values:
        return {"source": "tag", "values": tag_values, "ref": tag_name}

    note_values = _note_override(trailer_key, commit)
    if note_values:
        return {"source": "note", "values": note_values}

    return {"source": "none", "values": []}


def _violation_scopes(violations: dict[str, Any]) -> set[str]:
    scopes: set[str] = set()
    if not violations:
        return scopes
    if "sentinels" in violations:
        scopes.add("sentinel")
    if "both_touched" in violations:
        scopes.add("both_touched")
    if "size_caps" in violations:
        scopes.add("size")
    # Include any additional violation keys for forward compatibility.
    for key in violations:
        if key in {"sentinels", "both_touched", "size_caps"}:
            continue
        scopes.add(key.lower())
    return scopes


@dataclass
class _CleanAction:
    category: str
    description: str
    command: list[str] | None = None
    path: Path | None = None


@dataclass
class _SkippedItem:
    category: str
    description: str


@dataclass
class _WorktreeInfo:
    path: Path
    branch: str | None


@dataclass
class _OverlayInfo:
    name: str
    commit: str
    commit_time: datetime
    build_time: datetime | None
    tags: list[str]
    has_worktree: bool
    is_current: bool

    @property
    def reference_time(self) -> datetime:
        return self.build_time or self.commit_time

    def age(self, now: datetime) -> timedelta:
        return now - self.reference_time


def _latest_build_times() -> dict[str, datetime]:
    entries = _load_latest_build_entries()
    times: dict[str, datetime] = {}
    for overlay_name, (timestamp, _) in entries.items():
        if timestamp:
            times[overlay_name] = timestamp
    return times


def _collect_worktrees() -> list[_WorktreeInfo]:
    cp = g.run(["worktree", "list", "--porcelain"])
    infos: list[_WorktreeInfo] = []
    current: dict[str, str] = {}
    for line in cp.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                infos.append(
                    _WorktreeInfo(
                        path=Path(current["worktree"]),
                        branch=current.get("branch"),
                    )
                )
                current = {}
            current["worktree"] = line.split(" ", 1)[1]
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1]
        elif not line and current:
            infos.append(
                _WorktreeInfo(
                    path=Path(current["worktree"]),
                    branch=current.get("branch"),
                )
            )
            current = {}
    if current:
        infos.append(
            _WorktreeInfo(
                path=Path(current["worktree"]),
                branch=current.get("branch"),
            )
        )
    return infos


def _short_branch(ref: str | None) -> str | None:
    if ref and ref.startswith("refs/heads/"):
        return ref[len("refs/heads/") :]
    return ref


def _list_overlay_infos(
    cfg: Config,
    worktrees: Sequence[_WorktreeInfo],
    build_times: dict[str, datetime],
    current_branch: str,
) -> list[_OverlayInfo]:
    g.repo_root()
    overlays_ref = g.run(
        [
            "for-each-ref",
            "--format=%(refname:short)|%(committerdate:unix)|%(objectname)",
            "refs/heads/overlay/",
        ],
        check=False,
    )
    if overlays_ref.returncode != 0:
        return []

    worktree_branch_set = {_short_branch(info.branch) for info in worktrees if info.branch}

    infos: list[_OverlayInfo] = []
    for line in overlays_ref.stdout.splitlines():
        if not line or "|" not in line:
            continue
        name_part, ts_part, sha = line.split("|", 2)
        if not name_part:
            continue
        try:
            commit_ts = datetime.fromtimestamp(int(ts_part), tz=timezone.utc)
        except ValueError:
            commit_ts = datetime.now(timezone.utc)
        tags_cp = g.run(["tag", "--points-at", name_part], check=False)
        tags = (
            [tag for tag in tags_cp.stdout.splitlines() if tag] if tags_cp.returncode == 0 else []
        )
        infos.append(
            _OverlayInfo(
                name=name_part,
                commit=sha,
                commit_time=commit_ts,
                build_time=build_times.get(name_part),
                tags=tags,
                has_worktree=name_part in worktree_branch_set,
                is_current=(current_branch == name_part),
            )
        )
    return infos


def _parse_age_spec(spec: str) -> timedelta | None:
    raw = spec.strip().lower()
    if raw.endswith("d") and raw[:-1].isdigit():
        return timedelta(days=int(raw[:-1]))
    if raw.endswith("h") and raw[:-1].isdigit():
        return timedelta(hours=int(raw[:-1]))
    return None


def _compute_keep_set(infos: Sequence[_OverlayInfo], keep: int) -> set[str]:
    if keep <= 0:
        return set()
    ordered = sorted(infos, key=lambda info: info.reference_time, reverse=True)
    return {info.name for info in ordered[:keep]}


def _plan_overlay_actions(
    cfg: Config,
    overlays_filters: Sequence[str],
    keep: int,
    now: datetime,
    worktrees: Sequence[_WorktreeInfo],
    build_times: dict[str, datetime],
    current_branch: str,
) -> tuple[list[_CleanAction], list[_SkippedItem]]:
    if not overlays_filters:
        return [], []

    age_threshold: timedelta | None = None
    patterns: list[str] = []
    for raw in overlays_filters:
        raw = raw.strip()
        if not raw:
            continue
        age = _parse_age_spec(raw)
        if age:
            age_threshold = age
        else:
            patterns.append(raw)

    if age_threshold is None and not patterns:
        typer.secho(
            "[clean] No overlay filter provided. Use an age spec (e.g. 30d) or glob pattern.",
            fg=typer.colors.YELLOW,
        )
        return [], []

    infos = _list_overlay_infos(cfg, worktrees, build_times, current_branch)
    if not infos:
        return [], []

    candidates = infos
    if age_threshold is not None:
        cutoff = now - age_threshold
        candidates = [info for info in candidates if info.reference_time <= cutoff]

    if patterns:
        candidates = [
            info for info in candidates if any(fnmatch(info.name, pattern) for pattern in patterns)
        ]

    keep_set = _compute_keep_set(infos, keep)
    default_overlay = next(iter(cfg.overlays.keys()), None)
    default_overlay_branch: str | None = None
    if default_overlay:
        default_overlay_branch = f"{cfg.branches.overlay_prefix}{default_overlay}"

    actions: list[_CleanAction] = []
    skipped: list[_SkippedItem] = []

    for info in candidates:
        if info.name in keep_set:
            skipped.append(
                _SkippedItem(
                    category="overlays",
                    description=f"skip {info.name} (within keep window)",
                )
            )
            continue
        if default_overlay_branch and info.name == default_overlay_branch:
            skipped.append(
                _SkippedItem(
                    category="overlays",
                    description=f"skip {info.name} (default overlay)",
                )
            )
            continue
        if info.tags:
            skipped.append(
                _SkippedItem(
                    category="overlays",
                    description=f"skip {info.name} (tagged: {', '.join(info.tags)})",
                )
            )
            continue
        if info.has_worktree:
            skipped.append(
                _SkippedItem(
                    category="overlays",
                    description=f"skip {info.name} (active worktree present)",
                )
            )
            continue
        if info.is_current:
            skipped.append(
                _SkippedItem(
                    category="overlays",
                    description=f"skip {info.name} (currently checked out)",
                )
            )
            continue

        age_days = int(info.age(now).total_seconds() // 86400)
        desc = f"delete {info.name} (age {age_days}d)"
        actions.append(
            _CleanAction(
                category="overlays",
                description=desc,
                command=["branch", "-D", info.name],
            )
        )

    if not actions and age_threshold is not None and not patterns:
        skipped.append(
            _SkippedItem(
                category="overlays",
                description="no overlays matched the age threshold",
            )
        )

    return actions, skipped


def _plan_worktree_actions(
    worktrees: Sequence[_WorktreeInfo],
) -> tuple[list[_CleanAction], list[_SkippedItem]]:
    repo = g.repo_root()
    worktrees_dir = repo / ".forked" / "worktrees"
    actions: list[_CleanAction] = []
    skipped: list[_SkippedItem] = []

    actions.append(
        _CleanAction(
            category="worktrees",
            description="git worktree prune",
            command=["worktree", "prune"],
        )
    )

    active_paths = {info.path.resolve() for info in worktrees}
    if worktrees_dir.exists():
        for child in worktrees_dir.iterdir():
            if not child.is_dir():
                continue
            if child.resolve() in active_paths:
                skipped.append(
                    _SkippedItem(
                        category="worktrees",
                        description=f"skip {child.relative_to(repo)} (active)",
                    )
                )
                continue
            actions.append(
                _CleanAction(
                    category="worktrees",
                    description=f"remove {child.relative_to(repo)}",
                    path=child,
                )
            )
    else:
        skipped.append(
            _SkippedItem(
                category="worktrees",
                description="no .forked/worktrees directory present",
            )
        )

    return actions, skipped


def _overlay_id_from_base(base: str) -> str:
    head, sep, tail = base.rpartition("-")
    if sep and tail.isdigit():
        return head
    return base


def _plan_conflict_actions(
    age: timedelta,
) -> tuple[list[_CleanAction], list[_SkippedItem]]:
    repo = g.repo_root()
    conflicts_dir = repo / ".forked" / "conflicts"
    if not conflicts_dir.exists():
        return [], [
            _SkippedItem(
                category="conflicts",
                description="no conflict bundles found",
            )
        ]

    entries: dict[str, list[tuple[Path, datetime]]] = {}
    for child in conflicts_dir.iterdir():
        base = None
        if child.is_file() and child.suffix == ".json":
            base = child.stem
        elif child.is_dir():
            base = child.name
        if base is None:
            continue
        mtime = datetime.fromtimestamp(child.stat().st_mtime, tz=timezone.utc)
        entries.setdefault(base, []).append((child, mtime))

    actions: list[_CleanAction] = []
    skipped: list[_SkippedItem] = []
    now = datetime.now(timezone.utc)

    overlay_groups: dict[str, list[tuple[str, list[tuple[Path, datetime]], datetime]]] = (
        defaultdict(list)
    )
    for base, paths in entries.items():
        latest_time = max(mtime for _, mtime in paths)
        overlay_id = _overlay_id_from_base(base)
        overlay_groups[overlay_id].append((base, paths, latest_time))

    for overlay_id, items in overlay_groups.items():
        items_sorted = sorted(items, key=lambda item: item[2], reverse=True)
        items_sorted[0][0]
        keep_time = items_sorted[0][2]

        if now - keep_time > age:
            for child_path, _ in items_sorted[0][1]:
                skipped.append(
                    _SkippedItem(
                        category="conflicts",
                        description=f"retained {child_path.relative_to(repo)} (latest bundle for {overlay_id})",
                    )
                )

        for _base, paths, latest_time in items_sorted[1:]:
            if now - latest_time <= age:
                for child_path, _ in paths:
                    skipped.append(
                        _SkippedItem(
                            category="conflicts",
                            description=f"retained {child_path.relative_to(repo)} (newer than threshold)",
                        )
                    )
                continue
            for child_path, _ in paths:
                rel = child_path.relative_to(repo)
                actions.append(
                    _CleanAction(
                        category="conflicts",
                        description=f"remove {rel}",
                        path=child_path,
                    )
                )

    return actions, skipped


def _build_clean_plan(
    cfg: Config,
    *,
    overlays_filters: Sequence[str],
    keep: int,
    include_worktrees: bool,
    include_conflicts: bool,
    conflicts_age_days: int,
) -> tuple[list[_CleanAction], list[_SkippedItem]]:
    now = datetime.now(timezone.utc)
    worktrees = _collect_worktrees()
    build_times = _latest_build_times()
    current_branch = g.current_ref()

    actions: list[_CleanAction] = []
    skipped: list[_SkippedItem] = []

    overlay_actions, overlay_skipped = _plan_overlay_actions(
        cfg=cfg,
        overlays_filters=overlays_filters,
        keep=keep,
        now=now,
        worktrees=worktrees,
        build_times=build_times,
        current_branch=current_branch,
    )
    actions.extend(overlay_actions)
    skipped.extend(overlay_skipped)

    if include_worktrees:
        worktree_actions, worktree_skips = _plan_worktree_actions(worktrees)
        actions.extend(worktree_actions)
        skipped.extend(worktree_skips)

    if include_conflicts:
        conflicts_actions, conflicts_skips = _plan_conflict_actions(
            timedelta(days=conflicts_age_days)
        )
        actions.extend(conflicts_actions)
        skipped.extend(conflicts_skips)

    return actions, skipped


def _append_clean_log(entries: Iterable[str]) -> None:
    repo = g.repo_root()
    logs_dir = repo / ".forked" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "clean.log"
    timestamp = datetime.now(timezone.utc).isoformat()
    with log_path.open("a", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(f"{timestamp} {entry}\n")


def _execute_clean_actions(actions: Sequence[_CleanAction]) -> None:
    repo = g.repo_root()
    log_entries: list[str] = []
    for action in actions:
        if action.command:
            g.run(action.command)
            log_entries.append(f"{action.category}: git {' '.join(action.command)}")
        elif action.path:
            if action.path.is_dir():
                shutil.rmtree(action.path, ignore_errors=True)
            elif action.path.exists():
                action.path.unlink(missing_ok=True)
            rel = action.path.relative_to(repo)
            log_entries.append(f"{action.category}: remove {rel}")
    if log_entries:
        _append_clean_log(log_entries)


def _print_clean_summary(
    actions: Sequence[_CleanAction], skipped_items: Sequence[_SkippedItem]
) -> None:
    categories = ["overlays", "worktrees", "conflicts"]
    actions_by_cat: dict[str, list[_CleanAction]] = {
        cat: [action for action in actions if action.category == cat] for cat in categories
    }
    skipped_by_cat: dict[str, list[_SkippedItem]] = {
        cat: [item for item in skipped_items if item.category == cat] for cat in categories
    }

    if not any(actions_by_cat.values()) and not any(skipped_by_cat.values()):
        typer.echo("[forked clean] Nothing matched the provided selectors.")
        return

    typer.echo("[forked clean] Plan summary:")
    for cat in categories:
        cat_actions = actions_by_cat.get(cat, [])
        cat_skips = skipped_by_cat.get(cat, [])
        if not cat_actions and not cat_skips:
            continue
        typer.echo(f"  {cat.capitalize()}:")
        for action in cat_actions:
            if action.command:
                typer.echo(f"    - {action.description} (git {' '.join(action.command)})")
            elif action.path:
                typer.echo(f"    - {action.description}")
            else:
                typer.echo(f"    - {action.description}")
        for skip_item in cat_skips:
            typer.echo(f"    - {skip_item.description}")


def _collect_status_summary(cfg: Config, latest: int) -> dict[str, Any]:
    upstream_ref = g.run(["rev-parse", f"{cfg.upstream.remote}/{cfg.upstream.branch}"], check=False)
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

    summary: dict[str, Any] = {
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
    guard_counts: dict[str, int] = {}
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
            overlay_sha: str | None = None
        else:
            overlay_sha = rev.stdout.strip()

        log_entry = build_entries.get(name)
        selection = _selection_for_overlay(cfg, name, build_entries)
        built_ts: datetime | None = None
        status_value: str | None = None

        if log_entry:
            built_ts, entry_payload = log_entry
            status_value = entry_payload.get("status")

        if built_ts is None:
            built_ts = datetime.utcfromtimestamp(commit_ts).replace(tzinfo=timezone.utc)

        overlay_payload: dict[str, Any] = {
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
def clean(
    overlays: Annotated[
        list[str] | None,
        typer.Option(
            "--overlays",
            help="Age spec (e.g. 30d) or glob pattern; repeat to combine filters",
            metavar="FILTER",
        ),
    ] = None,
    keep: Annotated[
        int,
        typer.Option(
            "--keep",
            min=0,
            help="Preserve N most-recent overlays regardless of filters",
        ),
    ] = 0,
    worktrees: Annotated[
        bool,
        typer.Option(
            "--worktrees",
            help="Include stale worktree pruning",
        ),
    ] = False,
    conflicts: Annotated[
        bool,
        typer.Option(
            "--conflicts",
            help="Include conflict bundle cleanup",
        ),
    ] = False,
    conflicts_age: Annotated[
        int,
        typer.Option(
            "--conflicts-age",
            min=1,
            help="Age threshold in days for conflict bundles",
        ),
    ] = 14,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run/--no-dry-run",
            help="Preview actions without executing (default)",
        ),
    ] = True,
    confirm: Annotated[
        bool,
        typer.Option(
            "--confirm",
            help="Required to perform destructive actions",
        ),
    ] = False,
):
    overlay_filters = overlays or []
    if not overlay_filters and not worktrees and not conflicts:
        typer.secho(
            "[clean] Specify at least one target via --overlays, --worktrees, or --conflicts.",
            fg=typer.colors.YELLOW,
        )
        return

    cfg = load_config()
    actions, skipped = _build_clean_plan(
        cfg,
        overlays_filters=overlay_filters,
        keep=keep,
        include_worktrees=worktrees,
        include_conflicts=conflicts,
        conflicts_age_days=conflicts_age,
    )
    _print_clean_summary(actions, skipped)

    if not actions:
        typer.echo("[forked clean] No actions scheduled.")
        return

    if dry_run:
        typer.echo(
            "[forked clean] Dry-run mode; no changes made. Re-run with --no-dry-run --confirm to apply."
        )
        return

    if not confirm:
        typer.secho(
            "[forked clean] Refusing to execute without --confirm.",
            fg=typer.colors.RED,
        )
        return

    _execute_clean_actions(actions)
    typer.echo("[forked clean] Cleanup complete.")


@app.command()
def sync(
    emit_conflicts: bool = typer.Option(
        False,
        "--emit-conflicts",
        help="Write conflict bundle JSON to the default sync location (.forked/conflicts/<branch>-<wave>.json)",
    ),
    emit_conflicts_path: str | None = typer.Option(
        None,
        "--emit-conflicts-path",
        help="Write conflict bundle JSON to PATH",
        metavar="PATH",
        show_default=False,
    ),
    emit_conflict_blobs: bool = typer.Option(
        False,
        "--emit-conflict-blobs",
        help="Export base/ours/theirs blobs to the default directory alongside the bundle",
    ),
    conflict_blobs_dir: str | None = typer.Option(
        None,
        "--conflict-blobs-dir",
        help="Directory for base/ours/theirs blob exports",
        metavar="DIR",
        show_default=False,
    ),
    on_conflict: str = typer.Option(
        "stop",
        "--on-conflict",
        help="Conflict handling mode: stop, bias, or exec",
        metavar="MODE",
        show_default=True,
    ),
    on_conflict_exec: str | None = typer.Option(
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
    emit_conflicts_value: str | None
    if emit_conflicts_path:
        emit_conflicts_value = emit_conflicts_path
    elif emit_conflicts:
        emit_conflicts_value = "__AUTO__"
    else:
        emit_conflicts_value = None

    conflict_blobs_dir_value: str | None
    if conflict_blobs_dir:
        conflict_blobs_dir_value = conflict_blobs_dir
    elif emit_conflict_blobs:
        conflict_blobs_dir_value = "__AUTO__"
    else:
        conflict_blobs_dir_value = None

    if conflict_blobs_dir_value and emit_conflicts_value is None:
        typer.secho(
            "[sync] --emit-conflict-blobs/--conflict-blobs-dir requires --emit-conflicts.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=2)

    conflict_mode = on_conflict.lower()
    if conflict_mode in {"bias-continue", "bias_continue"}:
        conflict_mode = "bias"
    if conflict_mode not in {"stop", "bias", "exec"}:
        raise typer.BadParameter("--on-conflict must be one of: stop, bias, exec")
    if on_conflict_exec and conflict_mode != "exec":
        conflict_mode = "exec"

    telemetry = run_sync(
        cfg,
        emit_conflicts=emit_conflicts_value,
        conflict_blobs_dir=conflict_blobs_dir_value,
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
    overlay: Annotated[
        str | None,
        typer.Option(
            "--overlay",
            help="Overlay profile defined in forked.yml",
        ),
    ] = None,
    features_arg: Annotated[
        str | None,
        typer.Option(
            "--features",
            "-f",
            help="Comma-separated list of features to include (mutually exclusive with --overlay)",
        ),
    ] = None,
    include: Annotated[
        list[str] | None,
        typer.Option(
            "--include",
            help="Patch glob to force-include (can be provided multiple times)",
            show_default=False,
            metavar="PATTERN",
        ),
    ] = None,
    exclude: Annotated[
        list[str] | None,
        typer.Option(
            "--exclude",
            help="Patch glob to exclude (can be provided multiple times)",
            show_default=False,
            metavar="PATTERN",
        ),
    ] = None,
    id: Annotated[
        str | None,
        typer.Option(
            "--id",
            help="Overlay identifier; defaults to profile name when using --overlay, otherwise today's date",
        ),
    ] = None,
    no_worktree: Annotated[
        bool,
        typer.Option("--no-worktree"),
    ] = False,
    auto_continue: Annotated[
        bool,
        typer.Option("--auto-continue"),
    ] = False,
    skip_upstream_equivalents: Annotated[
        bool,
        typer.Option(
            "--skip-upstream-equivalents",
            help="Skip commits already present in trunk (uses git cherry)",
        ),
    ] = False,
    git_note: Annotated[
        bool,
        typer.Option(
            "--git-note/--no-git-note",
            help="Write provenance note to refs/notes/forked-meta",
        ),
    ] = True,
    emit_conflicts: Annotated[
        bool,
        typer.Option(
            "--emit-conflicts",
            help="Write conflict bundle JSON to the default location (.forked/conflicts/<id>-<wave>.json)",
        ),
    ] = False,
    emit_conflicts_path: Annotated[
        str | None,
        typer.Option(
            "--emit-conflicts-path",
            help="Write conflict bundle JSON to PATH",
            metavar="PATH",
            show_default=False,
        ),
    ] = None,
    emit_conflict_blobs: Annotated[
        bool,
        typer.Option(
            "--emit-conflict-blobs",
            help="Export base/ours/theirs blobs to the default directory alongside the bundle",
        ),
    ] = False,
    conflict_blobs_dir: Annotated[
        str | None,
        typer.Option(
            "--conflict-blobs-dir",
            help="Directory for base/ours/theirs blob exports",
            metavar="DIR",
            show_default=False,
        ),
    ] = None,
    on_conflict: Annotated[
        str,
        typer.Option(
            "--on-conflict",
            help="Conflict handling mode: stop, bias, or exec",
            metavar="MODE",
            show_default=True,
        ),
    ] = "stop",
    on_conflict_exec: Annotated[
        str | None,
        typer.Option(
            "--on-conflict-exec",
            help="Shell command to run when --on-conflict exec (use {json} placeholder)",
            metavar="COMMAND",
        ),
    ] = None,
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
        raise typer.Exit(code=2) from exc

    overlay_id = id or (overlay or date.today().isoformat())

    emit_conflicts_value: str | None
    if emit_conflicts_path:
        emit_conflicts_value = emit_conflicts_path
    elif emit_conflicts:
        emit_conflicts_value = "__AUTO__"
    else:
        emit_conflicts_value = None

    conflict_blobs_dir_value: str | None
    if conflict_blobs_dir:
        conflict_blobs_dir_value = conflict_blobs_dir
    elif emit_conflict_blobs:
        conflict_blobs_dir_value = "__AUTO__"
    else:
        conflict_blobs_dir_value = None

    if conflict_blobs_dir_value and emit_conflicts_value is None:
        typer.secho(
            "[build] --emit-conflict-blobs/--conflict-blobs-dir requires --emit-conflicts.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=2)

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
        emit_conflicts=emit_conflicts_value,
        conflict_blobs_dir=conflict_blobs_dir_value,
        on_conflict=conflict_mode,
        on_conflict_exec=on_conflict_exec,
    )

    if selection.overlay_profile:
        rprint(f"[bold]Overlay profile:[/bold] {selection.overlay_profile}")
    if selection.include or selection.exclude:
        filters: list[str] = []
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
    overlay: Annotated[str, typer.Option("--overlay", help="Overlay branch/ref to inspect")],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            help="Path to write the guard report",
        ),
    ] = Path(".forked/report.json"),
    mode: Annotated[
        str | None,
        typer.Option("--mode"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Display sentinel matches and write additional debug details",
        ),
    ] = False,
):
    cfg = load_config()
    if mode:
        cfg.guards.mode = mode
    trunk = cfg.branches.trunk
    overlay_rev = g.run(["rev-parse", overlay], check=False)
    if overlay_rev.returncode != 0 or not overlay_rev.stdout.strip():
        typer.secho(
            f"[guard] Overlay '{overlay}' not found.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=4)
    overlay_sha = overlay_rev.stdout.strip()
    base = g.merge_base(trunk, overlay)

    report: dict[str, Any] = {
        "report_version": 2,
        "overlay": overlay,
        "trunk": trunk,
        "base": base,
        "violations": {},
    }
    debug_info: dict[str, Any] = {}

    build_entries = _load_latest_build_entries()
    selection = _selection_for_overlay(cfg, overlay, build_entries)
    features_block: dict[str, Any] = {
        "source": selection.get("source"),
        "values": selection.get("features", []),
    }
    if selection.get("resolver_source"):
        features_block["resolver_source"] = selection.get("resolver_source")
    if selection.get("overlay_profile"):
        features_block["overlay_profile"] = selection.get("overlay_profile")
    if selection.get("patches"):
        features_block["patches"] = selection.get("patches")
    report["features"] = features_block

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

    override_details = _resolve_override(cfg, overlay, overlay_sha)
    allowed_values_cfg = [value.lower() for value in cfg.policy_overrides.allowed_values or []]
    override_block: dict[str, Any] = {
        "enabled": cfg.policy_overrides.require_trailer or cfg.guards.mode == "require-override",
        "source": override_details.get("source", "none"),
        "values": override_details.get("values", []),
        "applied": False,
    }
    if allowed_values_cfg:
        override_block["allowed_values"] = allowed_values_cfg
    if "ref" in override_details:
        override_block["ref"] = override_details["ref"]
    report["override"] = override_block

    has_violations = bool(report["violations"])
    violation_scopes = _violation_scopes(report["violations"])
    override_values = override_block["values"]
    allowed_set = set(allowed_values_cfg)
    invalid_values = set()
    if allowed_set:
        invalid_values = {value for value in override_values if value not in allowed_set}
    override_covers = False
    if violation_scopes:
        values_set = set(override_values)
        if "all" in values_set:
            override_covers = True
        elif violation_scopes.issubset(values_set):
            override_covers = True
    if not violation_scopes:
        override_covers = True

    override_required = override_block["enabled"] and bool(violation_scopes)
    override_present = bool(override_values)
    override_error: str | None = None

    if violation_scopes and override_present and invalid_values:
        override_error = f"Override values {sorted(invalid_values)} are not permitted." + (
            f" Allowed: {', '.join(sorted(allowed_set))}." if allowed_set else ""
        )
    elif override_required and violation_scopes:
        if not override_present:
            override_error = (
                f"Override required for violation scopes: {', '.join(sorted(violation_scopes))}."
            )
        elif not override_covers:
            missing = violation_scopes - set(override_values)
            override_error = "Override does not cover all violation scopes; missing: " + ", ".join(
                sorted(missing if missing else violation_scopes)
            )

    override_applied = (
        override_present and override_covers and not invalid_values and bool(violation_scopes)
    )
    if override_applied and override_required:
        override_block["applied"] = True
    if override_error:
        typer.secho(f"[guard] {override_error}", fg=typer.colors.RED, err=True)

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
    guard_log_entry_override = {k: v for k, v in override_block.items() if k != "allowed_values"}
    guard_log_entry = {
        "timestamp": datetime.now().isoformat(),
        "overlay": overlay,
        "mode": cfg.guards.mode,
        "violations": report["violations"],
        "verbose": verbose,
        "override": guard_log_entry_override,
        "features": report["features"],
    }
    if verbose:
        guard_log_entry["debug"] = debug_info
    with (logs_dir / "forked-guard.log").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(guard_log_entry) + "\n")

    if cfg.guards.mode == "block" and has_violations:
        raise typer.Exit(code=2)
    if cfg.guards.mode == "require-override" and has_violations:
        if override_block.get("applied"):
            return
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
    slug: str | None = typer.Option(
        None,
        "--slug",
        help="Optional suffix for slice branches (e.g. 'initial'); defaults to numeric only",
    ),
):
    cfg = load_config()
    g.ensure_clean()

    if name in cfg.features:
        typer.secho(
            f"[feature] Feature '{name}' already exists in forked.yml.", fg=typer.colors.RED
        )
        raise typer.Exit(code=2)

    slug_fragment = slug.replace(" ", "-") if slug else ""
    new_patches: list[str] = []

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
