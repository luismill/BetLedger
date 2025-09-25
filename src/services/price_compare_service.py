"""Load opportunities from allowed sources."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from ..domain.models import Opportunity


class PriceCompareService:
    def from_csv(self, path: Path) -> List[Opportunity]:
        df = pd.read_csv(path)
        return [self._row_to_opportunity(row) for _, row in df.iterrows()]

    def from_http_json(self, data: str) -> List[Opportunity]:
        parsed = json.loads(data)
        return [self._dict_to_opportunity(item) for item in parsed]

    def _row_to_opportunity(self, row) -> Opportunity:
        return Opportunity(
            provider_a=row["provider_a"],
            provider_b=row["provider_b"],
            mercado=row["mercado"],
            seleccion=row["seleccion"],
            odds_a=float(row["odds_a"]),
            odds_b=float(row["odds_b"]),
            commission_b=float(row.get("commission_b", 5.0)),
            rating=float(row.get("rating", 0.0)),
            perdida_calificacion=float(row.get("perdida_calificacion", 0.0)),
            rendimiento_cnr=float(row.get("rendimiento_cnr", 0.0)),
            beneficio_cnr=float(row.get("beneficio_cnr", 0.0)),
        )

    def _dict_to_opportunity(self, data: dict) -> Opportunity:
        return Opportunity(
            provider_a=data["provider_a"],
            provider_b=data["provider_b"],
            mercado=data["mercado"],
            seleccion=data["seleccion"],
            odds_a=float(data["odds_a"]),
            odds_b=float(data["odds_b"]),
            commission_b=float(data.get("commission_b", 5.0)),
            rating=float(data.get("rating", 0.0)),
            perdida_calificacion=float(data.get("perdida_calificacion", 0.0)),
            rendimiento_cnr=float(data.get("rendimiento_cnr", 0.0)),
            beneficio_cnr=float(data.get("beneficio_cnr", 0.0)),
        )


class ScraperSource:
    """Placeholder class disabled by default. Refer to provider TOS before scraping."""

    def fetch(self) -> List[Opportunity]:  # pragma: no cover - intentionally not implemented
        raise NotImplementedError("Scraping is disabled in this build")
