"""Incentive management service."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import List

from ..data.db import get_connection, initialise_database, now_ts
from ..domain.models import Incentive


class IncentiveService:
    def __init__(self) -> None:
        initialise_database()

    def list_incentives(self) -> List[Incentive]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM incentives ORDER BY expiry_date").fetchall()
            return [self._row_to_incentive(row) for row in rows]

    def create_incentive(self, incentive: Incentive) -> Incentive:
        payload = asdict(incentive)
        payload.pop("id")
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO incentives (account_id, title, type, req_stake, min_odds, expiry_date, status, notes)
                VALUES (:account_id,:title,:type,:req_stake,:min_odds,:expiry_date,:status,:notes)
                """,
                payload,
            )
            incentive.id = cursor.lastrowid
        return incentive

    def _row_to_incentive(self, row) -> Incentive:
        return Incentive(
            id=row["id"],
            account_id=row["account_id"],
            title=row["title"],
            type=row["type"],
            req_stake=row["req_stake"],
            min_odds=row["min_odds"],
            expiry_date=row["expiry_date"],
            status=row["status"],
            notes=row["notes"],
        )
