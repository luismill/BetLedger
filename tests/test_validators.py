import pytest

from src.utils.validators import ensure_commission_range, ensure_odds_valid, validate_and_round_to_tick


def test_tick_rounding():
    rounded = validate_and_round_to_tick(2.03)
    assert float(rounded) == pytest.approx(2.04, abs=1e-9)


def test_commission_range():
    ensure_commission_range(5.0)
    with pytest.raises(ValueError):
        ensure_commission_range(11.0)


def test_odds_validation():
    ensure_odds_valid(1.5)
    with pytest.raises(ValueError):
        ensure_odds_valid(1.0)
