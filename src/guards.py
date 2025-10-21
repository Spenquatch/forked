"""Guard checks for Forked CLI overlays."""

from typing import Any

from pathspec import PathSpec

import gitutil as g
from config import Config


def _make_spec(globs: list[str]) -> PathSpec:
    return PathSpec.from_lines("gitwildmatch", globs or [])


def both_touched(cfg: Config, base: str, trunk: str, overlay: str) -> list[str]:
    """Return files changed by both upstream and overlay since merge base."""
    upstream_changes = set(g.changed_paths(base, trunk))
    overlay_changes = set(g.changed_paths(base, overlay))
    return sorted(upstream_changes & overlay_changes)


def sentinels(
    cfg: Config,
    trunk: str,
    overlay: str,
    return_debug: bool = False,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Evaluate sentinel rules across trunk and overlay."""
    must_match_spec = _make_spec(cfg.guards.sentinels.must_match_upstream)
    must_diverge_spec = _make_spec(cfg.guards.sentinels.must_diverge_from_upstream)
    must_match: list[str] = []
    must_diverge: list[str] = []
    matched_must_match: list[str] = []
    matched_must_diverge: list[str] = []

    overlay_ls = set(g.run(["ls-tree", "-r", "--name-only", overlay]).stdout.splitlines())
    trunk_ls = set(g.run(["ls-tree", "-r", "--name-only", trunk]).stdout.splitlines())
    candidates = sorted(overlay_ls | trunk_ls)

    for path in candidates:
        if must_match_spec.match_file(path):
            matched_must_match.append(path)
            trunk_blob = g.blob_hash(trunk, path)
            overlay_blob = g.blob_hash(overlay, path)
            if trunk_blob is None or overlay_blob is None or trunk_blob != overlay_blob:
                must_match.append(path)
        if must_diverge_spec.match_file(path):
            matched_must_diverge.append(path)
            trunk_blob = g.blob_hash(trunk, path)
            overlay_blob = g.blob_hash(overlay, path)
            if overlay_blob is None or (trunk_blob is not None and trunk_blob == overlay_blob):
                must_diverge.append(path)

    result = {"must_match_upstream": must_match, "must_diverge_from_upstream": must_diverge}
    debug = (
        {
            "matched_must_match": matched_must_match,
            "matched_must_diverge": matched_must_diverge,
        }
        if return_debug
        else {}
    )
    return result, debug


def size_caps(cfg: Config, overlay: str, trunk: str) -> dict[str, Any]:
    """Compute diff size metrics and indicate violations."""
    caps = cfg.guards.size_caps
    if not (caps.max_loc or caps.max_files):
        return {"files_changed": 0, "loc": 0, "violations": False}

    files = 0
    loc = 0
    lines = g.run(["diff", "--numstat", f"{trunk}...{overlay}"]).stdout.splitlines()
    for line in lines:
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add, dele = parts[0], parts[1]
        files += 1
        if add.isdigit():
            loc += int(add)
        if dele.isdigit():
            loc += int(dele)

    violated = bool(
        (caps.max_files and files > caps.max_files) or (caps.max_loc and loc > caps.max_loc)
    )
    return {"files_changed": files, "loc": loc, "violations": violated}
