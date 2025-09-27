"""SQLite database helpers and schema management."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator

SCHEMA = """
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    owner TEXT NOT NULL,
    type TEXT CHECK(type IN ('origen','contraposicion')) NOT NULL,
    currency TEXT DEFAULT 'EUR',
    commission REAL DEFAULT 5.0,
    balance REAL NOT NULL DEFAULT 0.0,
    bonus_balance REAL NOT NULL DEFAULT 0.0,
    notes TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    ts DATETIME NOT NULL,
    kind TEXT CHECK(kind IN (
        'deposit','withdrawal','incentive','adjustment',
        'op_lock','op_release','op_settlement','transfer_out','transfer_in'
    )) NOT NULL,
    amount REAL NOT NULL,
    balance_after REAL NOT NULL,
    ref_operation_id INTEGER REFERENCES operations(id),
    ref_incentive_id INTEGER REFERENCES incentives(id),
    note TEXT
);

CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts DATETIME NOT NULL,
    origin_account_id INTEGER NOT NULL REFERENCES accounts(id),
    hedge_account_id INTEGER NOT NULL REFERENCES accounts(id),
    event TEXT NOT NULL,
    mode TEXT CHECK(mode IN ('calificacion','credito_no_retorno')) NOT NULL,
    stake_source TEXT CHECK(stake_source IN ('efectivo','credito')) DEFAULT 'efectivo',
    stake_a REAL NOT NULL,
    odds_a REAL NOT NULL,
    hedge_stake_b REAL NOT NULL,
    odds_b REAL NOT NULL,
    exposure_b REAL NOT NULL,
    commission_b REAL NOT NULL,
    profit_a_wins REAL NOT NULL,
    profit_b_wins REAL NOT NULL,
    perdida_calificacion REAL,
    beneficio_cnr REAL,
    rendimiento_cnr REAL,
    rating REAL,
    status TEXT CHECK(status IN ('PENDIENTE','GANA_A','GANA_B','ANULADA','CANCELADA')) NOT NULL,
    settled_at DATETIME,
    settlement_note TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS incentives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER REFERENCES accounts(id),
    title TEXT NOT NULL,
    type TEXT,
    req_stake REAL,
    min_odds REAL,
    expiry_date DATE,
    status TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_ops_status_ts ON operations(status, ts);
CREATE INDEX IF NOT EXISTS idx_ops_account_ts ON operations(origin_account_id, ts);
CREATE INDEX IF NOT EXISTS idx_tx_account_ts ON transactions(account_id, ts);
"""


def get_db_path() -> Path:
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir / "betledger.sqlite"


def initialise_database() -> None:
    path = get_db_path()
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def get_connection(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    db_path = path or get_db_path()
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def now_ts() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")
