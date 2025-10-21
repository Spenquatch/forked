"""Conflict bundle collection and serialization."""

from __future__ import annotations

import json
import subprocess
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import gitutil as g
from .config import Config, Feature, Sentinels

BINARY_DIFF_THRESHOLD = 256 * 1024  # 256 KiB
POSIX_SHELL_NOTE = "Commands assume a POSIX-compatible shell (e.g. bash, git bash, WSL)."


def _quote_posix(arg: str) -> str:
    """Return a POSIX-safe quoted string."""
    if not arg:
        return "''"
    return "'" + arg.replace("'", "'\"'\"'") + "'"


def _is_probably_binary(data: bytes) -> bool:
    """Detect binary content using a null-byte probe."""
    if b"\x00" in data:
        return True
    # Heuristic: consider text if it decodes cleanly as UTF-8
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def _git_show_blob(oid: str) -> bytes:
    """Return raw blob bytes for the provided object id."""
    cp = subprocess.run(
        ["git", "cat-file", "-p", oid],
        check=True,
        capture_output=True,
    )
    return cp.stdout


def _git_blob_size(oid: str) -> int:
    cp = subprocess.run(
        ["git", "cat-file", "-s", oid],
        check=True,
        capture_output=True,
        text=True,
    )
    return int(cp.stdout.strip())


def _git_unmerged_entries(cwd: str | None = None) -> dict[str, dict[int, str]]:
    """Parse `git ls-files -u` output into {path: {stage: oid}}."""
    cp = g.run(["ls-files", "-u"], cwd=cwd)
    entries: dict[str, dict[int, str]] = {}
    for line in cp.stdout.splitlines():
        # format: <mode> <oid> <stage>\t<path>
        try:
            meta, path = line.split("\t", 1)
        except ValueError:
            continue
        parts = meta.split()
        if len(parts) != 3:
            continue
        _mode, oid, stage_str = parts
        try:
            stage = int(stage_str)
        except ValueError:
            continue
        per_path = entries.setdefault(path, {})
        per_path[stage] = oid
    return entries


def _make_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_blob(path: Path, data: bytes):
    _make_parent(path)
    path.write_bytes(data)


def _diff_paths(first: Path, second: Path) -> str:
    cp = subprocess.run(
        ["git", "diff", "--no-index", "-U3", str(first), str(second)],
        capture_output=True,
        text=True,
    )
    return cp.stdout


def _feature_sentinels(feature: Feature | None) -> Sentinels:
    if feature:
        return feature.sentinels
    return Sentinels()


def _match_globs(path: str, patterns: Iterable[str]) -> bool:
    from fnmatch import fnmatch

    return any(fnmatch(path, pattern) for pattern in patterns or [])


@dataclass
class PrecedenceResult:
    sentinel: str
    path_bias: str
    recommended: str
    rationale: str


def _compute_precedence(
    cfg: Config,
    path: str,
    feature_names: list[str],
) -> PrecedenceResult:
    sentinel = "none"
    path_bias = "none"
    recommended = "none"
    rationale = "no rule matched"

    feature_sentinels: list[Sentinels] = []
    for feature_name in feature_names:
        feature_cfg = cfg.features.get(feature_name)
        if feature_cfg:
            feature_sentinels.append(feature_cfg.sentinels)

    # Sentinel precedence
    all_must_match = list(cfg.guards.sentinels.must_match_upstream)
    all_must_diverge = list(cfg.guards.sentinels.must_diverge_from_upstream)
    for sent_cfg in feature_sentinels:
        all_must_match.extend(sent_cfg.must_match_upstream)
        all_must_diverge.extend(sent_cfg.must_diverge_from_upstream)

    if _match_globs(path, all_must_match):
        sentinel = "must_match_upstream"
        recommended = "ours"
        rationale = "matched sentinel must_match_upstream"
        return PrecedenceResult(sentinel, path_bias, recommended, rationale)

    if _match_globs(path, all_must_diverge):
        sentinel = "must_diverge_from_upstream"
        recommended = "theirs"
        rationale = "matched sentinel must_diverge_from_upstream"
        return PrecedenceResult(sentinel, path_bias, recommended, rationale)

    # Path bias precedence
    if _match_globs(path, cfg.path_bias.ours):
        path_bias = "ours"
        recommended = "ours"
        rationale = "matched path_bias.ours"
    elif _match_globs(path, cfg.path_bias.theirs):
        path_bias = "theirs"
        recommended = "theirs"
        rationale = "matched path_bias.theirs"
    else:
        rationale = "no sentinel or path bias matched"

    return PrecedenceResult(sentinel, path_bias, recommended, rationale)


@dataclass
class ConflictContext:
    mode: str  # "build" or "sync"
    overlay: str | None
    overlay_id: str | None
    trunk: str
    upstream: str
    patch_branch: str
    patch_commit: str
    merge_base: str
    feature: str | None
    resume: dict[str, str]
    shell: str = "posix"
    note: str = POSIX_SHELL_NOTE


@dataclass
class ConflictWriter:
    cfg: Config
    repo_root: Path
    emit_base: Path | None
    blobs_base: Path | None
    default_prefix: str
    cwd: str | None = None
    wave: int = 0
    recorded_paths: list[Path] = field(default_factory=list)

    def _ensure_emit_prefix(self) -> Path:
        if self.emit_base is not None:
            return self.emit_base
        base_dir = self.repo_root / ".forked" / "conflicts"
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / self.default_prefix

    def _make_wave_path(self) -> Path:
        prefix = self._ensure_emit_prefix()
        if prefix.suffix == ".json":
            prefix = prefix.with_suffix("")
        filename = f"{prefix.name}-{self.wave}.json"
        return prefix.with_name(filename)

    def _resolve_blob_root(self) -> Path | None:
        if self.blobs_base is None:
            return None
        if self.wave <= 0:
            return None
        base = self.blobs_base
        if base.suffix:  # treat as file path; strip suffix
            base = base.with_suffix("")
        target = base / f"wave-{self.wave}"
        target.mkdir(parents=True, exist_ok=True)
        return target

    def next_bundle(
        self,
        context: ConflictContext,
        feature_names: list[str],
    ) -> tuple[Path, dict[str, Any]]:
        self.wave += 1
        entries = _git_unmerged_entries(self.cwd)
        if not entries:
            raise RuntimeError("Conflict collector invoked with no merge conflicts present.")

        blob_root = self._resolve_blob_root()
        files = []
        for path, stages in sorted(entries.items()):
            base_oid = stages.get(1)
            ours_oid = stages.get(2)
            theirs_oid = stages.get(3)

            base_bytes = _git_show_blob(base_oid) if base_oid else b""
            ours_bytes = _git_show_blob(ours_oid) if ours_oid else b""
            theirs_bytes = _git_show_blob(theirs_oid) if theirs_oid else b""

            binary = _is_probably_binary(ours_bytes) or _is_probably_binary(theirs_bytes)
            size_bytes = max(len(base_bytes), len(ours_bytes), len(theirs_bytes))

            diffs: dict[str, str | None] = {
                "base_vs_ours_unified": None,
                "base_vs_theirs_unified": None,
                "ours_vs_theirs_unified": None,
            }
            if not binary:
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmp_path = Path(tmpdir)
                    base_path = tmp_path / "base"
                    ours_path = tmp_path / "ours"
                    theirs_path = tmp_path / "theirs"
                    base_path.write_bytes(base_bytes)
                    ours_path.write_bytes(ours_bytes)
                    theirs_path.write_bytes(theirs_bytes)

                    diff_bo = _diff_paths(base_path, ours_path)
                    diff_bt = _diff_paths(base_path, theirs_path)
                    diff_ot = _diff_paths(ours_path, theirs_path)

                    if len(diff_bo.encode("utf-8")) <= BINARY_DIFF_THRESHOLD:
                        diffs["base_vs_ours_unified"] = diff_bo
                    if len(diff_bt.encode("utf-8")) <= BINARY_DIFF_THRESHOLD:
                        diffs["base_vs_theirs_unified"] = diff_bt
                    if len(diff_ot.encode("utf-8")) <= BINARY_DIFF_THRESHOLD:
                        diffs["ours_vs_theirs_unified"] = diff_ot

                    if any(value is None for value in diffs.values()):
                        binary = True

            precedence = _compute_precedence(self.cfg, path, feature_names)

            commands = {
                "accept_ours": f"git checkout --ours -- {_quote_posix(path)} && git add {_quote_posix(path)}",
                "accept_theirs": f"git checkout --theirs -- {_quote_posix(path)} && git add {_quote_posix(path)}",
                "open_mergetool": f"git mergetool -- {_quote_posix(path)}",
            }

            file_entry = {
                "path": path,
                "status": "conflicted",
                "slice": context.patch_branch,
                "precedence": {
                    "sentinel": precedence.sentinel,
                    "path_bias": precedence.path_bias,
                    "recommended": precedence.recommended,
                    "rationale": precedence.rationale,
                },
                "oids": {
                    "base": base_oid,
                    "ours": ours_oid,
                    "theirs": theirs_oid,
                },
                "commands": commands,
                "diffs": diffs
                if not binary
                else {
                    "base_vs_ours_unified": None,
                    "base_vs_theirs_unified": None,
                    "ours_vs_theirs_unified": None,
                },
                "shell": context.shell,
                "binary": binary,
                "size_bytes": size_bytes,
            }

            if blob_root is not None:
                safe_target = (blob_root / path).resolve()
                base_root_resolved = blob_root.resolve()
                if not str(safe_target).startswith(str(base_root_resolved)):
                    raise RuntimeError(f"Unsafe blob path escape detected for {path}")
                _write_blob(safe_target / "base.txt", base_bytes)
                _write_blob(safe_target / "ours.txt", ours_bytes)
                _write_blob(safe_target / "theirs.txt", theirs_bytes)
                file_entry["blobs_dir"] = str((safe_target).as_posix())
            elif binary:
                file_entry["blobs_dir"] = None

            files.append(file_entry)

        bundle = {
            "schema_version": 2,
            "wave": self.wave,
            "context": {
                "mode": context.mode,
                "overlay": context.overlay,
                "overlay_id": context.overlay_id,
                "trunk": context.trunk,
                "upstream": context.upstream,
                "patch_branch": context.patch_branch,
                "patch_commit": context.patch_commit,
                "merge_base": context.merge_base,
                "feature": context.feature,
            },
            "files": files,
            "resume": context.resume,
            "note": context.note,
        }

        bundle_path = self._make_wave_path()
        _make_parent(bundle_path)
        bundle_str = json.dumps(bundle, indent=2)
        bundle_path.write_text(bundle_str)
        self.recorded_paths.append(bundle_path)
        return bundle_path, bundle


def create_conflict_writer(
    cfg: Config,
    repo_root: Path,
    *,
    emit_conflicts: str | None,
    conflict_blobs_dir: str | None,
    overlay_id: str | None,
    cwd: str | None = None,
) -> ConflictWriter:
    def _normalize_path(raw: str | None) -> Path | None:
        if raw is None:
            return None
        if raw == "__AUTO__":
            return None
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = (repo_root / candidate).resolve()
        return candidate

    emit_path = _normalize_path(emit_conflicts)
    blobs_base = _normalize_path(conflict_blobs_dir)

    if blobs_base is None and conflict_blobs_dir == "__AUTO__":
        base_dir = repo_root / ".forked" / "conflicts" / (overlay_id or "sync")
        base_dir.mkdir(parents=True, exist_ok=True)
        blobs_base = base_dir

    if emit_conflicts == "__AUTO__":
        emit_path = None

    default_prefix = overlay_id or "conflict"
    return ConflictWriter(
        cfg=cfg,
        repo_root=repo_root,
        emit_base=emit_path,
        blobs_base=blobs_base,
        default_prefix=default_prefix,
        cwd=cwd,
    )


def recommended_actions(bundle: dict[str, Any]) -> list[tuple[str, str]]:
    """Return list of (path, recommendation) pairs for automation."""
    actions: list[tuple[str, str]] = []
    for entry in bundle.get("files", []):
        rec = entry.get("precedence", {}).get("recommended")
        if rec in ("ours", "theirs"):
            actions.append((entry["path"], rec))
    return actions


def apply_recommendations(bundle: dict[str, Any], cwd: str | None) -> list[tuple[str, str]]:
    """Apply recommended ours/theirs actions and return the list applied."""
    actions = recommended_actions(bundle)
    for path, choice in actions:
        if choice == "ours":
            g.run(["checkout", "--ours", "--", path], cwd=cwd)
        elif choice == "theirs":
            g.run(["checkout", "--theirs", "--", path], cwd=cwd)
        g.run(["add", path], cwd=cwd)
    return actions
