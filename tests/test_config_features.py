import pytest

from forked.config import Config, Feature, OverlayProfile
from forked.resolver import ResolutionError, resolve_selection


def make_config() -> Config:
    cfg = Config()
    cfg.patches.order = [
        "patch/payments/01",
        "patch/payments/02",
        "patch/branding/01",
    ]
    cfg.features = {
        "payments": Feature(
            patches=["patch/payments/01", "patch/payments/02"],
        ),
        "branding": Feature(
            patches=["patch/branding/01"],
        ),
    }
    cfg.overlays = {
        "dev": OverlayProfile(features=["payments", "branding"]),
        "payments": OverlayProfile(features=["payments"]),
    }
    return cfg


def test_overlay_profile_resolves_in_global_order():
    cfg = make_config()
    selection = resolve_selection(cfg, overlay="dev")
    assert selection.patches == cfg.patches.order
    assert selection.active_features == ["payments", "branding"]
    assert selection.source == "overlay:dev"


def test_feature_list_deduplicates_and_respects_order():
    cfg = make_config()
    selection = resolve_selection(cfg, features=["branding", "payments", "branding"])
    assert selection.patches == cfg.patches.order
    assert selection.active_features == ["branding", "payments"]


def test_include_exclude_adjust_selection():
    cfg = make_config()
    selection = resolve_selection(
        cfg,
        overlay="dev",
        include=["patch/branding/01"],
        exclude=["patch/payments/*"],
    )
    assert selection.patches == ["patch/branding/01"]
    assert selection.active_features == ["branding"]


def test_unknown_feature_raises_resolution_error():
    cfg = make_config()
    with pytest.raises(ResolutionError):
        resolve_selection(cfg, features=["nonexistent"])
