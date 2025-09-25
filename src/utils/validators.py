"""Validation helpers for odds and stakes."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from .rounding import round_up, to_decimal


@dataclass
class TickSizeBand:
    min_value: Decimal
    max_value: Decimal
    tick: Decimal

    def contains(self, odds: Decimal) -> bool:
        return self.min_value <= odds <= self.max_value


def default_tick_bands() -> list[TickSizeBand]:
    return [
        TickSizeBand(Decimal("1.01"), Decimal("2.0"), Decimal("0.01")),
        TickSizeBand(Decimal("2.0"), Decimal("3.0"), Decimal("0.02")),
        TickSizeBand(Decimal("3.0"), Decimal("4.0"), Decimal("0.05")),
        TickSizeBand(Decimal("4.0"), Decimal("6.0"), Decimal("0.1")),
        TickSizeBand(Decimal("6.0"), Decimal("10.0"), Decimal("0.2")),
        TickSizeBand(Decimal("10.0"), Decimal("20.0"), Decimal("0.5")),
        TickSizeBand(Decimal("20.0"), Decimal("30.0"), Decimal("1.0")),
        TickSizeBand(Decimal("30.0"), Decimal("50.0"), Decimal("2.0")),
        TickSizeBand(Decimal("50.0"), Decimal("100.0"), Decimal("5.0")),
    ]


def validate_and_round_to_tick(odds: float | Decimal, bands: Iterable[TickSizeBand] | None = None) -> Decimal:
    odds_decimal = to_decimal(odds)
    if odds_decimal <= 0:
        raise ValueError("Odds must be positive")
    bands = list(bands or default_tick_bands())
    for band in bands:
        if band.contains(odds_decimal):
            ticks = ((odds_decimal - band.min_value) / band.tick).to_integral_value(rounding="ROUND_FLOOR")
            adjusted = band.min_value + band.tick * ticks
            if adjusted < odds_decimal:
                adjusted += band.tick
            return adjusted.quantize(band.tick)
    # If outside all bands just round up to nearest cent
    return round_up(odds_decimal)


def ensure_commission_range(value: float, min_value: float = 0.0, max_value: float = 10.0) -> None:
    if not (min_value <= value <= max_value):
        raise ValueError("Commission must be between 0 and 10")


def ensure_odds_valid(odds: float) -> None:
    if odds <= 1.01:
        raise ValueError("Odds must be greater than 1.01")


def ensure_positive(value: float, label: str = "value") -> None:
    if value <= 0:
        raise ValueError(f"{label} must be positive")
