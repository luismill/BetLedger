"""Operations lifecycle management."""
from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import List

from ..data.db import get_connection, initialise_database, now_ts
from ..domain.models import Operation
from .account_service import AccountService
from .calculator_service import CalculatorService


class OperationService:
    def __init__(self, account_service: AccountService | None = None) -> None:
        initialise_database()
        self.account_service = account_service or AccountService()
        self.calculator = CalculatorService()

    def list_operations(self, *, include_cancelled: bool = True) -> List[Operation]:
        query = "SELECT * FROM operations"
        params: tuple[object, ...] = ()
        if not include_cancelled:
            query += " WHERE status != 'CANCELADA'"
        query += " ORDER BY ts DESC"
        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_operation(row) for row in rows]

    def create_operation(
        self,
        *,
        origin_account_id: int,
        hedge_account_id: int,
        event: str,
        mode: str,
        stake_source: str,
        stake_a: float,
        odds_a: float,
        odds_b: float,
        commission_b: float,
    ) -> Operation:
        calc = self.calculator.compute(
            stake_a=stake_a,
            odds_a=odds_a,
            odds_b=odds_b,
            commission_b=commission_b,
            mode=mode,
            stake_source=stake_source,
        )

        deficit_origin = 0.0 if stake_source == "credito" else self.account_service.ensure_funds(origin_account_id, stake_a)
        deficit_hedge = self.account_service.ensure_funds(hedge_account_id, calc.exposure_b)
        if deficit_origin > 0 or deficit_hedge > 0:
            raise ValueError("Fondos insuficientes para crear la operación")

        operation = Operation(
            id=None,
            ts=datetime.now(UTC),
            origin_account_id=origin_account_id,
            hedge_account_id=hedge_account_id,
            event=event,
            mode=mode,
            stake_source=stake_source,
            stake_a=stake_a,
            odds_a=odds_a,
            hedge_stake_b=calc.hedge_stake_b,
            odds_b=odds_b,
            exposure_b=calc.exposure_b,
            commission_b=commission_b,
            profit_a_wins=calc.profit_a_wins,
            profit_b_wins=calc.profit_b_wins,
            perdida_calificacion=calc.perdida_calificacion,
            beneficio_cnr=calc.beneficio_cnr,
            rendimiento_cnr=calc.rendimiento_cnr,
            rating=calc.rating,
            status="PENDIENTE",
        )

        payload = asdict(operation)
        payload.pop("id")
        payload["ts"] = operation.ts.isoformat(timespec="seconds")
        payload["settled_at"] = None

        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO operations (
                    ts, origin_account_id, hedge_account_id, event, mode, stake_source,
                    stake_a, odds_a, hedge_stake_b, odds_b, exposure_b, commission_b,
                    profit_a_wins, profit_b_wins, perdida_calificacion, beneficio_cnr,
                    rendimiento_cnr, rating, status, settled_at, settlement_note, notes
                ) VALUES (:ts,:origin_account_id,:hedge_account_id,:event,:mode,:stake_source,
                    :stake_a,:odds_a,:hedge_stake_b,:odds_b,:exposure_b,:commission_b,
                    :profit_a_wins,:profit_b_wins,:perdida_calificacion,:beneficio_cnr,
                    :rendimiento_cnr,:rating,:status,:settled_at,:settlement_note,:notes)
                """,
                payload,
            )
            operation.id = cursor.lastrowid

        if stake_source == "efectivo":
            self.account_service.apply_transaction(
                account_id=origin_account_id,
                kind="op_lock",
                amount=-stake_a,
                ref_operation_id=operation.id,
            )
        self.account_service.apply_transaction(
            account_id=hedge_account_id,
            kind="op_lock",
            amount=-calc.exposure_b,
            ref_operation_id=operation.id,
        )
        return operation

    def settle_operation(self, operation_id: int, outcome: str, note: str | None = None) -> Operation:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM operations WHERE id=?", (operation_id,)).fetchone()
            if not row:
                raise ValueError("Operation not found")
            operation = self._row_to_operation(row)

        if operation.status != "PENDIENTE":
            raise ValueError("Operation already settled")

        if outcome not in {"GANA_A", "GANA_B", "ANULADA"}:
            raise ValueError("Invalid outcome")

        settlement_ts = datetime.now(UTC).isoformat(timespec="seconds")
        with get_connection() as conn:
            conn.execute(
                "UPDATE operations SET status=?, settled_at=?, settlement_note=? WHERE id=?",
                (outcome, settlement_ts, note, operation_id),
            )

        if outcome == "GANA_A":
            if operation.stake_source == "efectivo":
                self.account_service.apply_transaction(
                    account_id=operation.origin_account_id,
                    kind="op_release",
                    amount=operation.stake_a,
                    ref_operation_id=operation_id,
                )
            winnings = operation.stake_a * (operation.odds_a - 1)
            self.account_service.apply_transaction(
                account_id=operation.origin_account_id,
                kind="op_settlement",
                amount=winnings,
                ref_operation_id=operation_id,
                note="Ganó origen",
            )
            self.account_service.apply_transaction(
                account_id=operation.hedge_account_id,
                kind="op_release",
                amount=operation.exposure_b,
                ref_operation_id=operation_id,
            )
            self.account_service.apply_transaction(
                account_id=operation.hedge_account_id,
                kind="op_settlement",
                amount=-operation.exposure_b,
                ref_operation_id=operation_id,
                note="Pagada cobertura",
            )
        elif outcome == "GANA_B":
            if operation.stake_source == "efectivo":
                self.account_service.apply_transaction(
                    account_id=operation.origin_account_id,
                    kind="op_release",
                    amount=operation.stake_a,
                    ref_operation_id=operation_id,
                    note="Liberado stake",
                )
                self.account_service.apply_transaction(
                    account_id=operation.origin_account_id,
                    kind="op_settlement",
                    amount=-operation.stake_a,
                    ref_operation_id=operation_id,
                    note="Perdió origen",
                )
            else:
                self.account_service.apply_transaction(
                    account_id=operation.origin_account_id,
                    kind="op_release",
                    amount=0.0,
                    ref_operation_id=operation_id,
                )
            self.account_service.apply_transaction(
                account_id=operation.hedge_account_id,
                kind="op_release",
                amount=operation.exposure_b,
                ref_operation_id=operation_id,
            )
            net = operation.hedge_stake_b * (1 - operation.commission_b / 100)
            self.account_service.apply_transaction(
                account_id=operation.hedge_account_id,
                kind="op_settlement",
                amount=net,
                ref_operation_id=operation_id,
                note="Ganó cobertura",
            )
        else:  # ANULADA
            if operation.stake_source == "efectivo":
                self.account_service.apply_transaction(
                    account_id=operation.origin_account_id,
                    kind="op_release",
                    amount=operation.stake_a,
                    ref_operation_id=operation_id,
                    note="Anulada",
                )
            self.account_service.apply_transaction(
                account_id=operation.hedge_account_id,
                kind="op_release",
                amount=operation.exposure_b,
                ref_operation_id=operation_id,
                note="Anulada",
            )

        with get_connection() as conn:
            row = conn.execute("SELECT * FROM operations WHERE id=?", (operation_id,)).fetchone()
            return self._row_to_operation(row)

    def cancel_operation(self, operation_id: int, *, note: str | None = None) -> Operation:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM operations WHERE id=?", (operation_id,)).fetchone()
            if not row:
                raise ValueError("Operation not found")
            operation = self._row_to_operation(row)

        if operation.status != "PENDIENTE":
            raise ValueError("Solo se pueden cancelar operaciones pendientes")

        if operation.stake_source == "efectivo":
            self.account_service.apply_transaction(
                account_id=operation.origin_account_id,
                kind="op_release",
                amount=operation.stake_a,
                ref_operation_id=operation.id,
                note=note or "Operación cancelada",
            )
        self.account_service.apply_transaction(
            account_id=operation.hedge_account_id,
            kind="op_release",
            amount=operation.exposure_b,
            ref_operation_id=operation.id,
            note=note or "Operación cancelada",
        )

        settled_ts = datetime.now(UTC).isoformat(timespec="seconds")
        with get_connection() as conn:
            conn.execute(
                "UPDATE operations SET status=?, settled_at=?, settlement_note=? WHERE id=?",
                ("CANCELADA", settled_ts, note, operation_id),
            )
            row = conn.execute("SELECT * FROM operations WHERE id=?", (operation_id,)).fetchone()
        return self._row_to_operation(row)

    def _row_to_operation(self, row) -> Operation:
        return Operation(
            id=row["id"],
            ts=datetime.fromisoformat(row["ts"]),
            origin_account_id=row["origin_account_id"],
            hedge_account_id=row["hedge_account_id"],
            event=row["event"],
            mode=row["mode"],
            stake_source=row["stake_source"],
            stake_a=row["stake_a"],
            odds_a=row["odds_a"],
            hedge_stake_b=row["hedge_stake_b"],
            odds_b=row["odds_b"],
            exposure_b=row["exposure_b"],
            commission_b=row["commission_b"],
            profit_a_wins=row["profit_a_wins"],
            profit_b_wins=row["profit_b_wins"],
            perdida_calificacion=row["perdida_calificacion"],
            beneficio_cnr=row["beneficio_cnr"],
            rendimiento_cnr=row["rendimiento_cnr"],
            rating=row["rating"],
            status=row["status"],
            settled_at=datetime.fromisoformat(row["settled_at"]) if row["settled_at"] else None,
            settlement_note=row["settlement_note"],
            notes=row["notes"],
        )
