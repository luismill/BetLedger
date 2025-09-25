from src.services.calculator_service import CalculatorService


def test_rounding_up_prevents_underhedge():
    service = CalculatorService()
    result = service.compute(stake_a=10.0, odds_a=1.5, odds_b=1.51, commission_b=0.0, mode="calificacion")
    assert result.hedge_stake_b * (result.exposure_b / result.hedge_stake_b) >= result.exposure_b
