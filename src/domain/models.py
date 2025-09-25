"""Domain dataclasses representing core entities."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Account:
    id: Optional[int]
    name: str
    type: str  # 'origen' or 'contraposicion'
    currency: str = "EUR"
    commission: float = 5.0
    balance: float = 0.0
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Transaction:
    id: Optional[int]
    account_id: int
    ts: datetime
    kind: str
    amount: float
    balance_after: float
    ref_operation_id: Optional[int] = None
    ref_incentive_id: Optional[int] = None
    note: Optional[str] = None


@dataclass
class Operation:
    id: Optional[int]
    ts: datetime
    origin_account_id: int
    hedge_account_id: int
    event: str
    mode: str
    stake_source: str
    stake_a: float
    odds_a: float
    hedge_stake_b: float
    odds_b: float
    exposure_b: float
    commission_b: float
    profit_a_wins: float
    profit_b_wins: float
    perdida_calificacion: Optional[float] = None
    beneficio_cnr: Optional[float] = None
    rendimiento_cnr: Optional[float] = None
    rating: Optional[float] = None
    status: str = "PENDIENTE"
    settled_at: Optional[datetime] = None
    settlement_note: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Incentive:
    id: Optional[int]
    account_id: int
    title: str
    type: Optional[str] = None
    req_stake: Optional[float] = None
    min_odds: Optional[float] = None
    expiry_date: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Opportunity:
    provider_a: str
    provider_b: str
    mercado: str
    seleccion: str
    odds_a: float
    odds_b: float
    commission_b: float
    rating: float
    perdida_calificacion: Optional[float] = None
    rendimiento_cnr: Optional[float] = None
    beneficio_cnr: Optional[float] = None
    ts: datetime = field(default_factory=datetime.utcnow)
