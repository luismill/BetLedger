"""Database backup utilities."""
from __future__ import annotations

import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .db import get_db_path

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)
RETENTION_DAYS = 7


def create_backup() -> Path:
    src = get_db_path()
    if not src.exists():
        raise FileNotFoundError("Database file does not exist")
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    dst = BACKUP_DIR / f"betledger-{timestamp}.sqlite"
    shutil.copy2(src, dst)
    _purge_old_backups()
    return dst


def _purge_old_backups() -> None:
    cutoff = datetime.now(UTC) - timedelta(days=RETENTION_DAYS)
    for file in BACKUP_DIR.glob("betledger-*.sqlite"):
        mtime = datetime.fromtimestamp(file.stat().st_mtime, UTC)
        if mtime < cutoff:
            file.unlink(missing_ok=True)
