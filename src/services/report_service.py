"""Reporting helpers for dashboards."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from ..data.db import get_connection, initialise_database


class ReportService:
    def __init__(self) -> None:
        initialise_database()

    def kpis(self) -> Dict[str, float]:
        with get_connection() as conn:
            total_profit = conn.execute(
                "SELECT COALESCE(SUM(CASE WHEN kind='op_settlement' THEN amount ELSE 0 END),0) FROM transactions"
            ).fetchone()[0]
            operations_count = conn.execute("SELECT COUNT(*) FROM operations").fetchone()[0]
            total_balance = conn.execute("SELECT COALESCE(SUM(balance),0) FROM accounts").fetchone()[0]
        roi = total_profit / total_balance if total_balance else 0.0
        return {
            "beneficio_total": float(total_profit),
            "roi": float(roi),
            "operaciones": float(operations_count),
            "saldo_total": float(total_balance),
        }

    def profit_over_time(self, period: str = "day") -> List[tuple[str, float]]:
        if period not in {"day", "week", "month"}:
            raise ValueError("Invalid period")
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT ts, amount FROM transactions WHERE kind='op_settlement' ORDER BY ts"
            ).fetchall()
        buckets: Dict[str, float] = defaultdict(float)
        for row in rows:
            ts = datetime.fromisoformat(row["ts"])
            if period == "day":
                key = ts.strftime("%Y-%m-%d")
            elif period == "week":
                key = f"{ts.isocalendar().year}-W{ts.isocalendar().week:02d}"
            else:
                key = ts.strftime("%Y-%m")
            buckets[key] += row["amount"]
        return sorted(buckets.items())
