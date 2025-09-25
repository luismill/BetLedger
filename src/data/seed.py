"""Populate the database with demo data."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .db import get_connection, initialise_database, now_ts


def run() -> None:
    initialise_database()
    with get_connection() as conn:
        conn.execute("DELETE FROM transactions")
        conn.execute("DELETE FROM operations")
        conn.execute("DELETE FROM incentives")
        conn.execute("DELETE FROM accounts")

        accounts = [
            ("Cuenta Origen A", "origen", "EUR", 0.0, 100.0, None, now_ts(), now_ts()),
            ("Cuenta Origen B", "origen", "EUR", 0.0, 50.0, None, now_ts(), now_ts()),
            ("Exchange X", "contraposicion", "EUR", 5.0, 200.0, None, now_ts(), now_ts()),
        ]
        conn.executemany(
            "INSERT INTO accounts (name, type, currency, commission, balance, notes, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
            accounts,
        )

        origin_id = conn.execute("SELECT id FROM accounts WHERE name=?", ("Cuenta Origen A",)).fetchone()[0]
        origin2_id = conn.execute("SELECT id FROM accounts WHERE name=?", ("Cuenta Origen B",)).fetchone()[0]
        hedge_id = conn.execute("SELECT id FROM accounts WHERE name=?", ("Exchange X",)).fetchone()[0]

        operations = [
            (
                now_ts(),
                origin_id,
                hedge_id,
                "Evento Calificacion 1",
                "calificacion",
                "efectivo",
                25.0,
                2.0,
                24.39,
                2.1,
                26.83,
                5.0,
                -1.83,
                -0.61,
                1.83,
                None,
                None,
                96.5,
                "PENDIENTE",
                None,
                None,
                "",
            ),
            (
                now_ts(),
                origin_id,
                hedge_id,
                "Evento CNR",
                "credito_no_retorno",
                "credito",
                20.0,
                5.0,
                18.95,
                5.2,
                79.59,
                5.0,
                60.0,
                18.00,
                None,
                18.0,
                0.9,
                99.1,
                "GANA_B",
                now_ts(),
                "Ganó B",
                "",
            ),
        ]
        conn.executemany(
            """
            INSERT INTO operations (
                ts, origin_account_id, hedge_account_id, event, mode, stake_source,
                stake_a, odds_a, hedge_stake_b, odds_b, exposure_b, commission_b,
                profit_a_wins, profit_b_wins, perdida_calificacion, beneficio_cnr,
                rendimiento_cnr, rating, status, settled_at, settlement_note, notes
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            operations,
        )

        incentives = [
            (
                origin_id,
                "Bono Bienvenida",
                "deposit",
                50.0,
                1.5,
                (datetime.now(UTC) + timedelta(days=7)).date().isoformat(),
                "QUAL_DONE",
                "",
            ),
            (
                origin2_id,
                "Bono Fidelidad",
                "cashback",
                30.0,
                1.8,
                (datetime.now(UTC) + timedelta(days=14)).date().isoformat(),
                "COMPLETED",
                "",
            ),
        ]
        conn.executemany(
            "INSERT INTO incentives (account_id, title, type, req_stake, min_odds, expiry_date, status, notes) VALUES (?,?,?,?,?,?,?,?)",
            incentives,
        )

        conn.commit()


if __name__ == "__main__":
    run()
    print("Database seeded with demo data")
