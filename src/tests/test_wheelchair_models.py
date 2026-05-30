"""Tests for the canonical wheelchair-models package + legacy parity."""

from __future__ import annotations

import warnings

import pytest

from wheelchair.wheelchairs import (
    InvacareTDXSP2,
    PermobilM3Corpus,
    PrideJazzyEliteHD,
    QuantumQ6Edge,
    REGISTRY,
    Wheelchair,
)


CANONICAL = [PermobilM3Corpus, QuantumQ6Edge, InvacareTDXSP2, PrideJazzyEliteHD]


@pytest.mark.parametrize("cls", CANONICAL, ids=lambda c: c.__name__)
def test_each_chair_has_a_spec(cls) -> None:
    chair = cls()
    assert isinstance(chair, Wheelchair)
    assert chair.name
    assert chair.max_speed > 0
    assert chair.wheel_base > 0
    assert chair.wheel_diameter > 0


@pytest.mark.parametrize("cls", CANONICAL, ids=lambda c: c.__name__)
def test_motor_config_has_required_fields(cls) -> None:
    cfg = cls().get_motor_config()
    for k in ("type", "motor_count", "motor_type", "max_voltage", "max_current"):
        assert k in cfg


@pytest.mark.parametrize("cls", CANONICAL, ids=lambda c: c.__name__)
def test_peak_current_is_at_least_continuous(cls) -> None:
    cfg = cls().get_motor_config()
    assert cfg["max_peak_current"] >= cfg["max_current"]


def test_registry_resolves_by_full_name_and_alias() -> None:
    assert REGISTRY["Permobil M3 Corpus"] is PermobilM3Corpus
    assert REGISTRY["permobil_m3"] is PermobilM3Corpus
    assert REGISTRY["jazzy_elite"] is PrideJazzyEliteHD


def test_velocity_clamps_to_unit_range() -> None:
    chair = PermobilM3Corpus()
    chair.set_velocity(2.0, -2.0)
    assert chair.get_velocity() == (1.0, -1.0)


def test_stop_zeroes_velocity() -> None:
    chair = PermobilM3Corpus()
    chair.set_velocity(0.5, 0.5)
    chair.stop()
    assert chair.get_velocity() == (0.0, 0.0)


# -------- Legacy parity: importing the legacy module still works --------


def test_legacy_import_warns_and_returns_canonical_class() -> None:
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Force a fresh import so the module-level warn fires.
        import importlib
        import wheelchair_bot.wheelchairs as legacy

        importlib.reload(legacy)
        # The legacy class object IS the canonical one.
        assert legacy.PermobilM3Corpus is PermobilM3Corpus
        assert legacy.InvacareTPG is InvacareTDXSP2  # legacy alias preserved
        assert legacy.PrideJazzy is PrideJazzyEliteHD
        assert any(issubclass(x.category, DeprecationWarning) for x in w)


def test_legacy_models_module_still_resolves() -> None:
    import wheelchair_bot.wheelchairs.models as legacy_models

    chair = legacy_models.PermobilM3Corpus()
    assert chair.name == "Permobil M3 Corpus"
