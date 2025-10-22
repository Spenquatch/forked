"""Configuration loading for Forked CLI."""

from dataclasses import asdict, dataclass, field
from pathlib import Path

import typer
import yaml  # type: ignore[import-untyped]

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
    order: list[str] = field(default_factory=list)


@dataclass
class SizeCaps:
    max_loc: int = 0
    max_files: int = 0


@dataclass
class Sentinels:
    must_match_upstream: list[str] = field(default_factory=list)
    must_diverge_from_upstream: list[str] = field(default_factory=list)


@dataclass
class Guards:
    mode: str = "warn"
    both_touched: bool = True
    sentinels: Sentinels = field(default_factory=Sentinels)
    size_caps: SizeCaps = field(default_factory=SizeCaps)


@dataclass
class PathBias:
    ours: list[str] = field(default_factory=list)
    theirs: list[str] = field(default_factory=list)


@dataclass
class WorktreeCfg:
    enabled: bool = True
    root: str = ".forked/worktrees"


@dataclass
class PolicyOverrides:
    require_trailer: bool = False
    trailer_key: str = "Forked-Override"
    allowed_values: list[str] = field(default_factory=list)


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
    features: dict[str, "Feature"] = field(default_factory=dict)
    overlays: dict[str, "OverlayProfile"] = field(default_factory=dict)


@dataclass
class Feature:
    patches: list[str] = field(default_factory=list)
    sentinels: Sentinels = field(default_factory=Sentinels)


@dataclass
class OverlayProfile:
    features: list[str] = field(default_factory=list)


def load_config(path: Path = DEFAULT_CFG_PATH) -> Config:
    """Load configuration from ``forked.yml``."""
    if not path.exists():
        typer.secho(
            "fatal: not a forked repository. Run `forked init` to configure this repo.",
            fg=typer.colors.RED,
        )
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

    features_raw = data.get("features", {}) or {}
    features: dict[str, Feature] = {}
    for name, payload in features_raw.items():
        if not isinstance(payload, dict):
            continue
        sent_cfg = payload.get("sentinels", {}) or {}
        features[name] = Feature(
            patches=list(payload.get("patches", []) or []),
            sentinels=Sentinels(**sent_cfg),
        )

    overlays_raw = data.get("overlays", {}) or {}
    overlays: dict[str, OverlayProfile] = {}
    for name, payload in overlays_raw.items():
        if not isinstance(payload, dict):
            continue
        overlays[name] = OverlayProfile(features=list(payload.get("features", []) or []))

    return Config(
        upstream=upstream,
        branches=branches,
        patches=patches,
        guards=guards,
        path_bias=path_bias,
        worktree=worktree,
        policy_overrides=policy_overrides,
        features=features,
        overlays=overlays,
    )


def write_skeleton(path: Path = DEFAULT_CFG_PATH):
    """Write a default ``forked.yml`` if one does not already exist."""
    if path.exists():
        return

    cfg = Config()
    path.write_text(dump_config(cfg))


def dump_config(cfg: Config) -> str:
    """Serialise a ``Config`` dataclass to YAML."""
    return yaml.safe_dump(asdict(cfg), sort_keys=False)


def write_config(cfg: Config, path: Path = DEFAULT_CFG_PATH):
    """Persist the provided configuration back to disk."""
    path.write_text(dump_config(cfg))
