"""Service layer for account and transaction management."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Iterable, List

from ..domain.models import Account, Transaction
from ..data.db import get_connection, initialise_database, now_ts


class AccountService:
    def __init__(self) -> None:
        initialise_database()

    def list_accounts(self) -> List[Account]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM accounts ORDER BY id").fetchall()
            return [self._row_to_account(row) for row in rows]

    def create_account(self, account: Account) -> Account:
        payload = asdict(account)
        payload.pop("id")
        payload.setdefault("created_at", now_ts())
        payload.setdefault("updated_at", now_ts())
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO accounts (name, type, currency, commission, balance, notes, created_at, updated_at)
                VALUES (:name,:type,:currency,:commission,:balance,:notes,:created_at,:updated_at)
                """,
                payload,
            )
            account.id = cursor.lastrowid
        return account

    def apply_transaction(
        self,
        *,
        account_id: int,
        kind: str,
        amount: float,
        note: str | None = None,
        ref_operation_id: int | None = None,
        ref_incentive_id: int | None = None,
        ts: datetime | None = None,
    ) -> Transaction:
        ts_value = ts.isoformat(timespec="seconds") if ts else now_ts()
        with get_connection() as conn:
            current_balance = self._current_balance(conn, account_id)
            new_balance = current_balance + amount
            cursor = conn.execute(
                """
                INSERT INTO transactions (account_id, ts, kind, amount, balance_after, ref_operation_id, ref_incentive_id, note)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (account_id, ts_value, kind, amount, new_balance, ref_operation_id, ref_incentive_id, note),
            )
            conn.execute("UPDATE accounts SET balance=?, updated_at=? WHERE id=?", (new_balance, now_ts(), account_id))
            return Transaction(
                id=cursor.lastrowid,
                account_id=account_id,
                ts=datetime.fromisoformat(ts_value),
                kind=kind,
                amount=amount,
                balance_after=new_balance,
                ref_operation_id=ref_operation_id,
                ref_incentive_id=ref_incentive_id,
                note=note,
            )

    def _current_balance(self, conn, account_id: int) -> float:
        row = conn.execute("SELECT balance FROM accounts WHERE id=?", (account_id,)).fetchone()
        if row is None:
            raise ValueError("Account not found")
        return float(row[0])

    def ensure_funds(self, account_id: int, required: float) -> float:
        with get_connection() as conn:
            balance = self._current_balance(conn, account_id)
        deficit = required - balance
        return max(deficit, 0.0)

    def reconcile_account(self, account_id: int) -> bool:
        with get_connection() as conn:
            tx_sum = conn.execute(
                "SELECT COALESCE(SUM(amount),0) FROM transactions WHERE account_id=?", (account_id,)
            ).fetchone()[0]
            initial_balance = conn.execute("SELECT balance FROM accounts WHERE id=?", (account_id,)).fetchone()[0]
            # Recalculate from zero: assume zero + tx = final, compare to stored
            stored_balance = float(initial_balance)
            recalculated = float(tx_sum)
        return abs(stored_balance - recalculated) < 1e-6

    def reconcile_all(self) -> bool:
        return all(self.reconcile_account(acc.id) for acc in self.list_accounts())

    def _row_to_account(self, row) -> Account:
        return Account(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            currency=row["currency"],
            commission=row["commission"],
            balance=row["balance"],
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )
