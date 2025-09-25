"""Calculator service implementing hedge computations."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ..utils.rounding import as_float, round_half_up, round_up, to_decimal
from ..utils.validators import ensure_commission_range, ensure_odds_valid, ensure_positive


@dataclass
class CalculatorResult:
    hedge_stake_b: float
    exposure_b: float
    profit_a_wins: float
    profit_b_wins: float
    perdida_calificacion: float | None = None
    beneficio_cnr: float | None = None
    rendimiento_cnr: float | None = None
    rating: float | None = None


class CalculatorService:
    def compute(
        self,
        *,
        stake_a: float,
        odds_a: float,
        odds_b: float,
        commission_b: float = 5.0,
        mode: str = "calificacion",
        stake_source: str = "efectivo",
    ) -> CalculatorResult:
        ensure_positive(stake_a, "stake_a")
        ensure_odds_valid(odds_a)
        ensure_odds_valid(odds_b)
        ensure_commission_range(commission_b)

        c = to_decimal(commission_b) / Decimal(100)
        stake_dec = to_decimal(stake_a)
        odds_a_dec = to_decimal(odds_a)
        odds_b_dec = to_decimal(odds_b)

        if mode == "calificacion":
            hedge_stake = (stake_dec * odds_a_dec) / (odds_b_dec - c)
        elif mode == "credito_no_retorno":
            hedge_stake = (stake_dec * (odds_a_dec - 1)) / (odds_b_dec - c)
        else:
            raise ValueError("Unknown mode")

        exposure = hedge_stake * (odds_b_dec - 1)
        hedge_stake = round_up(hedge_stake)
        exposure = round_up(exposure)

        profit_a_wins = stake_dec * (odds_a_dec - 1) - exposure
        if mode == "credito_no_retorno" and stake_source == "credito":
            profit_a_wins = stake_dec * (odds_a_dec - 1) - exposure
        elif stake_source == "efectivo":
            profit_a_wins = stake_dec * (odds_a_dec - 1) - exposure
        profit_b_wins = hedge_stake * (1 - c)
        if mode == "calificacion":
            profit_b_wins -= stake_dec
        perdida = None
        beneficio = None
        rendimiento = None
        if mode == "calificacion":
            perdida = -min(profit_a_wins, profit_b_wins)
        else:
            beneficio = min(profit_a_wins, profit_b_wins)
            rendimiento = beneficio / stake_dec

        rating = (odds_a_dec * (1 - (odds_b_dec - 1) / (odds_b_dec * (1 - c)))) * 100

        return CalculatorResult(
            hedge_stake_b=as_float(hedge_stake, rounding="up"),
            exposure_b=as_float(exposure, rounding="up"),
            profit_a_wins=as_float(profit_a_wins),
            profit_b_wins=as_float(profit_b_wins),
            perdida_calificacion=as_float(perdida) if perdida is not None else None,
            beneficio_cnr=as_float(beneficio) if beneficio is not None else None,
            rendimiento_cnr=as_float(rendimiento) if rendimiento is not None else None,
            rating=as_float(rating),
        )
