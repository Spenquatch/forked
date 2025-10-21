"""Feature and patch selection resolver for build workflows."""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from fnmatch import fnmatch

from config import Config, Feature


class ResolutionError(Exception):
    """Raised when feature or overlay resolution fails."""


@dataclass
class ResolvedSelection:
    """Resolver output describing selected patches/features and provenance."""

    patches: list[str]
    active_features: list[str] = field(default_factory=list)
    overlay_profile: str | None = None
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    unmatched_include: list[str] = field(default_factory=list)
    unmatched_exclude: list[str] = field(default_factory=list)
    source: str = "default"
    patch_feature_map: dict[str, list[str]] = field(default_factory=dict)


def _unique(seq: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in seq:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _feature_membership(cfg: Config) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for feature_name, feature_cfg in cfg.features.items():
        for patch in feature_cfg.patches:
            mapping.setdefault(patch, []).append(feature_name)
    return mapping


def _match_patterns(
    patterns: Sequence[str], candidates: Sequence[str]
) -> tuple[set[str], list[str]]:
    matches: set[str] = set()
    unmatched: list[str] = []
    for pattern in patterns:
        hit = [value for value in candidates if fnmatch(value, pattern)]
        if hit:
            matches.update(hit)
        else:
            unmatched.append(pattern)
    return matches, unmatched


def resolve_selection(
    cfg: Config,
    *,
    overlay: str | None = None,
    features: Sequence[str] | None = None,
    include: Sequence[str] | None = None,
    exclude: Sequence[str] | None = None,
) -> ResolvedSelection:
    """Resolve the ordered patch list for a build.

    Overlay profiles and direct feature selection are mutually exclusive.
    Include/exclude patterns refine the resulting patch set while preserving
    global patch order from ``cfg.patches.order``.
    """

    if overlay and features:
        raise ResolutionError("Cannot combine --overlay with --features. Choose one.")

    membership = _feature_membership(cfg)
    include = list(include or [])
    exclude = list(exclude or [])

    overlay_profile = None
    feature_names: list[str] = []
    source = "all"

    if overlay:
        profile = cfg.overlays.get(overlay)
        if profile is None:
            raise ResolutionError(f"Unknown overlay profile '{overlay}'.")
        overlay_profile = overlay
        feature_names = _unique(profile.features or [])
        source = f"overlay:{overlay}"
    elif features:
        feature_names = _unique(list(features))
        source = "features"

    selected: set[str] = set()
    patch_feature_map: dict[str, list[str]] = {}

    if feature_names:
        for feature_name in feature_names:
            if feature_name not in cfg.features:
                raise ResolutionError(f"Unknown feature '{feature_name}'. Define it in forked.yml.")
            feature_cfg = cfg.features[feature_name]
            for patch in feature_cfg.patches:
                if patch not in cfg.patches.order:
                    raise ResolutionError(
                        f"Feature '{feature_name}' references patch '{patch}' "
                        "which is missing from patches.order."
                    )
                selected.add(patch)
                owners = patch_feature_map.setdefault(patch, [])
                if feature_name not in owners:
                    owners.append(feature_name)
    else:
        # default: include all patches in global order
        for patch in cfg.patches.order:
            selected.add(patch)
            if patch in membership:
                patch_feature_map[patch] = list(membership[patch])

    include_matches, unmatched_include = _match_patterns(include, cfg.patches.order)
    selected.update(include_matches)

    exclude_matches, unmatched_exclude = _match_patterns(exclude, cfg.patches.order)
    selected.difference_update(exclude_matches)

    ordered_patches = [patch for patch in cfg.patches.order if patch in selected]

    if not ordered_patches:
        raise ResolutionError("Resolver produced an empty patch selection.")

    if not feature_names:
        active_features: list[str] = []
        seen_features: set[str] = set()
        for patch in ordered_patches:
            for feature_name in membership.get(patch, []):
                if feature_name in seen_features:
                    continue
                seen_features.add(feature_name)
                active_features.append(feature_name)
    else:
        active_features = []
        for feature_name in feature_names:
            candidate_cfg: Feature | None = cfg.features.get(feature_name)
            if candidate_cfg is None:
                continue
            if any(patch in ordered_patches for patch in candidate_cfg.patches):
                active_features.append(feature_name)

    for patch in ordered_patches:
        if patch not in patch_feature_map:
            patch_feature_map[patch] = list(membership.get(patch, []))

    return ResolvedSelection(
        patches=ordered_patches,
        active_features=active_features,
        overlay_profile=overlay_profile,
        include=include,
        exclude=exclude,
        unmatched_include=unmatched_include,
        unmatched_exclude=unmatched_exclude,
        source=source,
        patch_feature_map=patch_feature_map,
    )
