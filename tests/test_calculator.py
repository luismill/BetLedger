from decimal import Decimal

import pytest

from src.services.calculator_service import CalculatorService


@pytest.fixture
def service():
    return CalculatorService()


def test_calificacion_rounding_up(service):
    result = service.compute(stake_a=25.0, odds_a=2.0, odds_b=2.1, commission_b=5.0, mode="calificacion")
    assert result.hedge_stake_b >= 24.39
    assert result.exposure_b >= 26.83
    assert result.perdida_calificacion is not None
    assert round(result.rating, 2) == pytest.approx(89.72, abs=0.1)


def test_credito_expected_profit(service):
    result = service.compute(
        stake_a=20.0,
        odds_a=5.0,
        odds_b=5.2,
        commission_b=5.0,
        mode="credito_no_retorno",
        stake_source="credito",
    )
    assert result.beneficio_cnr > 0
    assert result.rendimiento_cnr == pytest.approx(result.beneficio_cnr / 20.0, abs=0.01)


def test_invalid_inputs(service):
    with pytest.raises(ValueError):
        service.compute(stake_a=0, odds_a=2.0, odds_b=2.0)
    with pytest.raises(ValueError):
        service.compute(stake_a=10, odds_a=1.0, odds_b=2.0)
