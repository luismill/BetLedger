"""Utilities for financial rounding with explicit rules."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, ROUND_UP, getcontext

getcontext().prec = 28

def to_decimal(value: float | int | str) -> Decimal:
    """Convert a numeric value to Decimal safely."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def round_half_up(value: Decimal | float | int, ndigits: int = 2) -> Decimal:
    quantize_exp = Decimal(f"1.{'0' * ndigits}")
    return to_decimal(value).quantize(quantize_exp, rounding=ROUND_HALF_UP)


def round_up(value: Decimal | float | int, ndigits: int = 2) -> Decimal:
    quantize_exp = Decimal(f"1.{'0' * ndigits}")
    return to_decimal(value).quantize(quantize_exp, rounding=ROUND_UP)


def as_float(value: Decimal | float | int, ndigits: int = 2, rounding: str = 'half_up') -> float:
    decimal_value = to_decimal(value)
    if rounding == 'up':
        decimal_value = round_up(decimal_value, ndigits)
    else:
        decimal_value = round_half_up(decimal_value, ndigits)
    return float(decimal_value)
