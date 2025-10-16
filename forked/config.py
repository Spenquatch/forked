"""Configuration loading for Forked CLI."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import typer
import yaml


DEFAULT_CFG_PATH = Path("forked.yml")


@dataclass
class Upstream:
    remote: str = "upstream"
    branch: str = "main"


@dataclass
class Branches:
    trunk: str = "trunk"
    overlay_prefix: str = "overlay/"


@dataclass
class Patches:
    order: List[str] = field(default_factory=list)


@dataclass
class SizeCaps:
    max_loc: int = 0
    max_files: int = 0


@dataclass
class Sentinels:
    must_match_upstream: List[str] = field(default_factory=list)
    must_diverge_from_upstream: List[str] = field(default_factory=list)


@dataclass
class Guards:
    mode: str = "warn"
    both_touched: bool = True
    sentinels: Sentinels = field(default_factory=Sentinels)
    size_caps: SizeCaps = field(default_factory=SizeCaps)


@dataclass
class PathBias:
    ours: List[str] = field(default_factory=list)
    theirs: List[str] = field(default_factory=list)


@dataclass
class WorktreeCfg:
    enabled: bool = True
    root: str = ".forked/worktrees"


@dataclass
class PolicyOverrides:
    require_trailer: bool = False
    trailer_key: str = "Forked-Override"


@dataclass
class Config:
    version: int = 1
    upstream: Upstream = field(default_factory=Upstream)
    branches: Branches = field(default_factory=Branches)
    patches: Patches = field(default_factory=Patches)
    guards: Guards = field(default_factory=Guards)
    path_bias: PathBias = field(default_factory=PathBias)
    worktree: WorktreeCfg = field(default_factory=WorktreeCfg)
    policy_overrides: PolicyOverrides = field(default_factory=PolicyOverrides)


def load_config(path: Path = DEFAULT_CFG_PATH) -> Config:
    """Load configuration from ``forked.yml``."""
    if not path.exists():
        raise typer.Exit(code=3)

    data = yaml.safe_load(path.read_text()) or {}
    upstream = Upstream(**data.get("upstream", {}))
    branches = Branches(**data.get("branches", {}))
    patches = Patches(**data.get("patches", {}))

    guards_raw = data.get("guards", {})
    sent = Sentinels(**guards_raw.get("sentinels", {}))
    size_caps = SizeCaps(**guards_raw.get("size_caps", {}))
    guards = Guards(
        mode=guards_raw.get("mode", "warn"),
        both_touched=guards_raw.get("both_touched", True),
        sentinels=sent,
        size_caps=size_caps,
    )

    path_bias = PathBias(**data.get("path_bias", {}))
    worktree = WorktreeCfg(**data.get("worktree", {}))
    policy_overrides = PolicyOverrides(**data.get("policy_overrides", {}))

    return Config(
        upstream=upstream,
        branches=branches,
        patches=patches,
        guards=guards,
        path_bias=path_bias,
        worktree=worktree,
        policy_overrides=policy_overrides,
    )


def write_skeleton(path: Path = DEFAULT_CFG_PATH):
    """Write a default ``forked.yml`` if one does not already exist."""
    if path.exists():
        return

    cfg = Config()
    path.write_text(
        yaml.safe_dump(
            {
                "version": cfg.version,
                "upstream": vars(cfg.upstream),
                "branches": vars(cfg.branches),
                "patches": {"order": []},
                "guards": {
                    "mode": cfg.guards.mode,
                    "both_touched": cfg.guards.both_touched,
                    "sentinels": {
                        "must_match_upstream": [],
                        "must_diverge_from_upstream": [],
                    },
                    "size_caps": {"max_loc": 0, "max_files": 0},
                },
                "path_bias": {"ours": [], "theirs": []},
                "worktree": {"enabled": True, "root": ".forked/worktrees"},
                "policy_overrides": {
                    "require_trailer": False,
                    "trailer_key": "Forked-Override",
                },
            },
            sort_keys=False,
        )
    )
